"""Voer uit met: PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_office.py"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import office


class OfficeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        health = {"status": "ready", "url": office.monitor.ORIGIN + "/api/health",
                  "flags": {"status": "ok", "storage": "ready", "payments": "disabled", "webhooks": "disabled"}, "error": None}
        self.health_patch = patch.object(office.monitor, "audit_health", return_value=health)
        self.health_patch.start()
        self.addCleanup(self.health_patch.stop)

    def test_repeated_run_has_no_duplicate_tasks(self):
        first = office.run(self.output, offline_demo=True)
        second = office.run(self.output, offline_demo=True)
        before = {task["id"]: task["created_at"] for task in first["inventory"]["tasks"]}
        after = {task["id"]: task["created_at"] for task in second["inventory"]["tasks"]}
        self.assertEqual(before, after)
        self.assertEqual(len(after), len(second["inventory"]["tasks"]))
        self.assertEqual({task["role"] for task in second["inventory"]["tasks"]},
                         {"regie", "techniek", "seo", "verkoop"})
        stored = json.loads((self.output / "tasks.json").read_text())
        self.assertEqual(stored["tasks"], second["inventory"]["tasks"])

    def test_audit_exception_blocks_sales_and_is_reported(self):
        with patch.object(office.monitor, "audit", side_effect=TimeoutError("test timeout")):
            report = office.run(self.output)
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["roles"]["techniek"]["status"], "error")
        sales = report["roles"]["verkoop"]
        self.assertEqual(sales["status"], "blocked")
        self.assertTrue(any("audit" in reason.lower() for reason in sales["blockers"]))
        self.assertIn("TimeoutError", (self.output / "report.md").read_text())

    def test_page_error_blocks_sales(self):
        checks = office.demo_checks()
        checks[0] = {"path": "/", "status": "error", "issues": ["test connection error"]}
        with patch.object(office.monitor, "audit", return_value=checks):
            report = office.run(self.output)
        self.assertEqual(report["roles"]["techniek"]["status"], "error")
        self.assertEqual(report["roles"]["verkoop"]["technical_status"], "error")
        self.assertEqual(report["roles"]["verkoop"]["status"], "blocked")

    def test_normal_run_calls_real_audit_boundary_and_revenue_stays_null(self):
        checks = office.demo_checks()
        for row in checks:
            row["issues"] = []
        with patch.object(office.monitor, "audit", return_value=checks) as audit:
            report = office.run(self.output)
        audit.assert_called_once_with()
        self.assertEqual(report["mode"], "live")
        self.assertEqual(report["roles"]["techniek"]["status"], "ready")
        self.assertEqual(report["roles"]["seo"]["status"], "ready")
        saved = json.loads((self.output / "report.json").read_text())
        self.assertIsNone(saved["roles"]["verkoop"]["metrics"]["revenue_eur"])
        self.assertIsNone(saved["roles"]["verkoop"]["metrics"]["orders"])
        self.assertEqual(len(saved["roles"]["verkoop"]["concepts"]), 3)
        self.assertEqual(saved["roles"]["verkoop"]["concepts"][2]["status"], "blocked")
        self.assertIn("livecheckout niet gemaakt of ingeschakeld", saved["roles"]["verkoop"]["blockers"])
        payment = saved["roles"]["verkoop"]["payment"]
        self.assertEqual(payment["provider"], "Stripe / Managed Payments")
        self.assertEqual(payment["sandbox_status"], "ready")
        self.assertEqual(payment["live_status"], "blocked")
        self.assertEqual(payment["account_activation_ui_status"], "ready")
        self.assertEqual(payment["live_product_status"], "ready")
        self.assertIsNone(payment["checkout_url"])
        self.assertFalse(saved["roles"]["verkoop"]["delivery"]["end_to_end_verified"])
        self.assertEqual(saved["roles"]["regie"]["credit_guard"]["status"], "blocked")
        self.assertIsNone(saved["roles"]["regie"]["credit_guard"]["remaining_credits"])
        self.assertIsNone(saved["roles"]["regie"]["heartbeat"]["active"])
        self.assertEqual(saved["roles"]["regie"]["heartbeat"]["automation_id"],
                         "postritme-regie-techniek-seo-en-sales")
        self.assertIsNone(saved["execution"]["schedule_active"])

    def test_demo_never_calls_live_audit_and_is_visibly_marked(self):
        with patch.object(office.monitor, "audit", side_effect=AssertionError("demo network call")) as audit:
            report = office.run(self.output, offline_demo=True)
        audit.assert_not_called()
        self.assertIn("DEMO / FIXTURE", report["evidence_label"])
        self.assertIn("DEMO / FIXTURE", (self.output / "report.md").read_text())
        priority = report["roles"]["seo"]["priorities"][0]
        self.assertEqual((priority["priority"], priority["path"]), (3, "/inspiratie/"))

    def test_empty_audit_is_not_success(self):
        with patch.object(office.monitor, "audit", return_value=[]):
            report = office.run(self.output)
        self.assertEqual(report["roles"]["techniek"]["status"], "error")
        self.assertEqual(report["roles"]["verkoop"]["status"], "blocked")

    def test_corrupt_inventory_is_not_overwritten(self):
        stock = self.output / "tasks.json"
        stock.write_text("invalid json", encoding="utf-8")
        report = office.run(self.output, offline_demo=True)
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["inventory"]["status"], "error")
        self.assertEqual(stock.read_text(), "invalid json")

    def test_demo_and_live_inventories_cannot_mix(self):
        office.run(self.output, offline_demo=True)
        before = (self.output / "tasks.json").read_text()
        with patch.object(office.monitor, "audit", return_value=office.demo_checks()):
            report = office.run(self.output)
        self.assertEqual(report["inventory"]["status"], "error")
        self.assertEqual((self.output / "tasks.json").read_text(), before)


class HealthTests(unittest.TestCase):
    def test_public_health_only_returns_expected_flags(self):
        with patch.object(office.monitor.urllib.request, "urlopen") as request:
            response = request.return_value.__enter__.return_value
            response.url = office.monitor.ORIGIN + "/api/health"
            response.read.return_value = b'{"status":"ok","storage":"ready","payments":"disabled","webhooks":"disabled","extra":"ignored"}'
            health = office.monitor.audit_health()
        self.assertEqual(health["status"], "ready")
        self.assertEqual(set(health["flags"]), {"status", "storage", "payments", "webhooks"})
        self.assertEqual(health["flags"]["payments"], "disabled")

    def test_incomplete_health_payload_is_error(self):
        with patch.object(office.monitor.urllib.request, "urlopen") as request:
            response = request.return_value.__enter__.return_value
            response.url = office.monitor.ORIGIN + "/api/health"
            response.read.return_value = b'{"status":"ok"}'
            health = office.monitor.audit_health()
        self.assertEqual(health["status"], "error")
        self.assertIsNone(health["flags"])


if __name__ == "__main__":
    unittest.main()
