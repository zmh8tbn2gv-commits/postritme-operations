#!/usr/bin/env python3
"""Lokaal, regelgestuurd Postritme-beheer; geen LLM, publicatie of planning.

Gebruik: python3 office.py --output /pad/naar/rapporten
Demo:    python3 office.py --offline-demo --output /apart/pad/naar/demo
Exitcodes: 0 ready, 2 blocked (ook ontbrekende checkout of levering), 1 error.
"""

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import monitor


SEO_RULES = {
    "HTTP noindex": (1, "Controleer of indexering gewenst is; pas dan de HTTP-header aan."),
    "HTML noindex": (1, "Controleer of indexering gewenst is; pas dan de robots-meta aan."),
    "Unexpected redirect": (1, "Controleer de bestemming en herstel onbedoelde redirects."),
    "Unexpected page content": (1, "Controleer of de juiste Postritme-pagina wordt geleverd."),
    "Incorrect canonical": (2, "Controleer de bedoelde voorkeurs-URL en herstel de canonical."),
    "Missing title": (2, "Schrijf een unieke titel die de pagina en doelgroep beschrijft."),
    "Duplicate title": (2, "Geef de pagina een onderscheidende, inhoudelijk passende titel."),
    "Expected one H1": (2, "Controleer de kopstructuur en gebruik één duidelijke hoofdkop."),
    "Missing description": (3, "Schrijf een concrete beschrijving van inhoud en volgende stap."),
}


def demo_checks():
    """Uitsluitend verzonnen fixture; nooit als gemeten sitegegevens gebruiken."""
    return [
        {"path": path, "status": 200, "title": "DEMO Postritme " + path,
         "issues": ["Missing description"] if path == "/inspiratie/" else []}
        for path in monitor.PATHS
    ]


def technique(offline_demo):
    try:
        checks = demo_checks() if offline_demo else monitor.audit()
        health = {"status": "ready", "url": monitor.ORIGIN + "/api/health",
                  "flags": {"status": "ok", "storage": "ready", "payments": "disabled", "webhooks": "disabled"},
                  "error": None, "fixture": True} if offline_demo else monitor.audit_health()
        if not isinstance(checks, list) or len(checks) != len(monitor.PATHS):
            raise ValueError("Audit gaf geen volledige set pagina's terug.")
        if {row["path"] for row in checks} != set(monitor.PATHS):
            raise ValueError("Audit bevat onverwachte of ontbrekende paden.")
        for row in checks:
            status = row["status"]
            if not (status == "error" or type(status) is int):
                raise ValueError("Ongeldige HTTP-status in audit.")
            if not isinstance(row["issues"], list) or not all(
                isinstance(issue, str) for issue in row["issues"]
            ):
                raise ValueError("Ongeldige bevindingen in audit.")
        failed = health["status"] == "error" or any(row["status"] == "error" or not 200 <= row["status"] < 300
                     for row in checks)
        status = "error" if failed else "blocked" if any(row["issues"] for row in checks) else "ready"
        return {"status": status, "depends_on": [], "checks": checks, "health": health,
                "error": None, "scope": "Zeven publieke pagina's en /api/health; geen functionele planner-, betaal- of leveringstest."}
    except Exception as exc:
        return {"status": "error", "depends_on": [], "checks": [], "health": None,
                "error": f"{type(exc).__name__}: {exc}", "scope": "Audit kon niet worden voltooid."}


def seo(technical):
    priorities = []
    for row in technical["checks"]:
        if row["status"] == "error" or not 200 <= row["status"] < 300:
            priorities.append({"path": row["path"], "issue": "Auditpagina onbereikbaar",
                               "priority": 1, "action": "Herstel bereikbaarheid en voer de audit opnieuw uit."})
        else:
            for issue in row["issues"]:
                priority, action = SEO_RULES.get(issue, (2, "Onderzoek deze auditbevinding handmatig."))
                priorities.append({"path": row["path"], "issue": issue,
                                   "priority": priority, "action": action})
    priorities.sort(key=lambda item: (item["priority"], item["path"], item["issue"]))
    return {"status": "blocked" if technical["status"] == "error" or priorities else "ready",
            "depends_on": ["techniek"], "source": "roles.techniek.checks",
            "priorities": priorities,
            "limitation": "Geen zoekvolume-, ranking-, Search Console- of verkeersgegevens beschikbaar."}


def sales(technical, seo_result, offline_demo):
    blockers = ["livecheckout niet gemaakt of ingeschakeld", "campagnepakket nog NIET te koop",
                "Leveringsbackend heeft 8 geslaagde lokale tests; productiebetaling en levering nog niet bewezen.",
                "Stripe-sleutel voor beperkte Checkout-toegang ontbreekt: Verification required blijft laden.",
                "Betaling en levering zijn nog niet van begin tot eind getest.",
                "Geen marketingkanaal gekoppeld.",
                "GitHub-workflowrechten ontbreken; de voorbereide GitHub-planning is niet actief."]
    if technical["status"] == "error":
        blockers.append("Publieke audit onvolledig of mislukt; bereikbaarheid eerst herstellen.")
    elif technical["status"] == "blocked":
        blockers.append("Openstaande sitebevindingen eerst beoordelen.")
    if offline_demo:
        blockers.append("DEMO/FIXTURE: geen echte sitecontrole uitgevoerd.")
    return {
        "status": "blocked", "depends_on": ["techniek", "seo"],
        "technical_status": technical["status"], "seo_status": seo_result["status"],
        "blockers": blockers,
        "payment": {"status": "blocked", "provider": "Stripe / Managed Payments", "signal": "livecheckout niet gemaakt of ingeschakeld",
                    "sandbox_status": "ready", "live_status": "blocked",
                    "account_activation_ui_status": "ready", "live_product_status": "ready",
                    "live_product_id": "prod_VI6OJQdlN0bFkl", "price_eur": 9, "tax_included": True,
                    "checkout_status": "blocked", "checkout_url": None,
                    "source": "Aangeleverde projectstatus; niet vastgesteld via de publieke HTML-audit.",
                    "verification": "Peildatum 2026-09-20: accountactivatie in de Stripe-UI voltooid en liveproduct prod_VI6OJQdlN0bFkl voor €9 inclusief belasting gemaakt. Livecheckout nog niet gemaakt of ingeschakeld. Dit bewijst nog geen werkende betaal- en leveringsketen."},
        "delivery": {"status": "blocked", "local_tests_passed": 8, "end_to_end_verified": False,
                     "public_health": technical["health"],
                     "source": "Aangeleverde projectstatus op 2026-09-20; backendtests niet door office.py uitgevoerd."},
        "metrics": {"revenue_eur": None, "orders": None, "visitors": None,
                    "source": "Geen meet- of transactiedata aangesloten; onbekend is geen nul."},
        "concepts": [
            {"id": "gratis-horeca-week", "status": "ready", "offer": "Bestaande gratis contentplanner",
             "audience": "Zelfstandige horecaondernemers", "channel": "Voorstel voor horecapagina",
             "copy": "Plan deze week drie horecaposts: een gerecht, een kijkje achter de schermen en je weekendtip.",
             "cta": "Maak je gratis contentplanning", "destination": "/contentkalender-horeca/",
             "next_step": "Controleer de bestaande route naar de planner en laat de drie voorbeeldposts inhoudelijk beoordelen."},
            {"id": "gratis-beauty-week", "status": "ready", "offer": "Bestaande gratis contentplanner",
             "audience": "Kappers en beautysalons", "channel": "Voorstel voor beautysectorpagina",
             "copy": "Geef je volgende drie posts een plek: een behandeling, een verzorgingstip en een blik in je salon.",
             "cta": "Plan je salonposts gratis", "destination": "/contentkalender-kappers-beauty/",
             "next_step": "Controleer de plannerroute en werk drie voorbeelden uit zonder klantfoto's of onbewezen resultaatclaims."},
            {"id": "campagnepakket-concept", "status": "blocked", "offer": "Apart campagnepakket — nog NIET te koop",
             "price_eur": 9, "price_status": "Eenmalige prijs inclusief belasting ingesteld in Stripe-liveproduct; checkout nog niet beschikbaar.",
             "audience": "Ondernemers die meer uitgewerkte campagne-inhoud willen",
             "channel": "Openbare productpagina; nog geen checkout",
             "copy": "Het campagnepakket is klaar: 36 briefings, 12 per branche voor 3 branches, met vier weken per branche. De ZIP bevat 4 Markdown-bestanden en één printbare LEES-MIJ.html. Nog niet te koop.",
             "cta": "Nog niet te koop", "destination": "/campagnepakket/",
             "next_step": "Laat Techniek de backenddeployment en levering controleren; los de Stripe-verificatie op; maak daarna de livecheckout voor het bestaande product en test betaling en bestandslevering voordat de koopknop wordt ingeschakeld."},
        ],
        "concept_status_note": "Ready betekent lokaal uitgewerkt concept, geen gepubliceerde of goedgekeurde campagne.",
        "actions_executed": [],
    }


def coordination(roles):
    return {
        "status": "blocked", "name": "Regie — hoofdcoördinator",
        "depends_on": ["techniek", "seo", "verkoop"],
        "role_statuses": {name: role["status"] for name, role in roles.items()},
        "next_action": "Herstel de publieke audit." if roles["techniek"]["status"] == "error" else
                       "Controleer credits en de backenddeployment; rond levering af en test daarna checkout en levering.",
        "protocol": "COORDINATOR.md", "parallel_runs": 1,
        "heartbeat": {"status": "ready", "configured_at": "2026-09-20",
                      "automation_id": "postritme-regie-techniek-seo-en-sales", "interval_hours": 6,
                      "active": None, "reason": "Geconfigureerd op 2026-09-20; actuele activiteit en uitvoering niet door Python bevestigd. Computer en app moeten beschikbaar zijn."},
        "credit_guard": {
            "status": "blocked", "remaining_credits": None,
            "initial_credits_user_reported": 1250, "max_spend_credits": 1200, "reserve_credits": 100,
            "effective_spend_ceiling_from_initial": 1150,
            "required_tool": "mcp__codex_app__get_usage_limits",
            "reason": "Native actuele creditmeting vereist vóór elke AI-ronde; office.py leest deze niet zelf.",
            "stop_rule": "Pauzeer bij saldo <= 100, onbekend saldo of bereikte bestedingsgrens.",
            "enforcement": "Best effort instructie voor de coördinator; geen harde accountcap of Python-AI-integratie.",
        },
    }


def task_candidates(roles):
    tasks = [{"key": "techniek:audit", "role": "techniek", "status": "ready", "priority": 3,
              "title": "Publieke sitecontrole beoordelen", "detail": roles["techniek"]["scope"]}]
    if roles["techniek"]["status"] == "error":
        tasks[0].update(status="error", priority=1, title="Auditfout onderzoeken",
                        detail=roles["techniek"]["error"] or "Een of meer pagina's konden niet worden gecontroleerd.")
    for item in roles["seo"]["priorities"]:
        tasks.append({"key": "seo:" + item["path"] + ":" + item["issue"], "role": "seo",
                      "status": "ready", "priority": item["priority"],
                      "title": item["path"] + " — " + item["issue"], "detail": item["action"]})
    tasks.extend([
        {"key": "regie:credits", "role": "regie", "status": "blocked", "priority": 1,
         "title": "Actuele credits controleren vóór vervolgwerk", "detail": roles["regie"]["credit_guard"]["reason"] + " " + roles["regie"]["credit_guard"]["stop_rule"]},
        {"key": "regie:heartbeat", "role": "regie", "status": "ready", "priority": 2,
         "title": "Native heartbeatstatus controleren", "detail": "Geconfigureerd op 2026-09-20, elke zes uur lokaal; actuele activiteit en uitvoering niet door Python bevestigd. Gebruik COORDINATOR.md en automation-id postritme-regie-techniek-seo-en-sales."},
        {"key": "techniek:levering", "role": "techniek", "status": "ready", "priority": 1,
         "title": "Backenddeployment en levering controleren", "detail": "Backend: 8 lokale tests geslaagd. Controleer /api/health, productieconfiguratie en geautoriseerde bestandslevering vóór livecheckout; disabled flags zijn geen betaalmogelijkheid."},
        {"key": "seo:meting", "role": "seo", "status": "blocked", "priority": 3,
         "title": "Zoekprestaties meetbaar maken", "detail": "Search Console en verkeersgegevens ontbreken. Regel toegang voordat ranking, verkeer of conversie als resultaat wordt gerapporteerd."},
    ])
    tasks.append({"key": "verkoop:betaalprovider", "role": "verkoop", "status": "blocked", "priority": 1,
                  "title": "Stripe-verificatie oplossen en livecheckout testen", "detail": "Accountactivatie-UI voltooid; Stripe-liveproduct prod_VI6OJQdlN0bFkl voor €9 inclusief belasting bestaat. Beperkte Checkout-sleutel ontbreekt doordat Verification required blijft laden. Checkout nog niet gemaakt; eerst werkende levering nodig."})
    tasks.append({"key": "verkoop:marketingkanaal", "role": "verkoop", "status": "blocked", "priority": 2,
                  "title": "Geen marketingkanaal gekoppeld", "detail": "Kies een kanaal en regel toegang en toestemming voordat een concept kan worden gepubliceerd of verstuurd."})
    tasks.append({"key": "verkoop:workflowrechten", "role": "regie", "status": "blocked", "priority": 2,
                  "title": "GitHub-workflowrechten ontbreken", "detail": "De bestaande GitHub-koppeling weigert workflowrechten; de voorbereide GitHub-planning is niet actief. De native Codex-heartbeat staat hier los van. Rechten moeten via de bevoegde eigenaar worden geregeld."})
    for concept in roles["verkoop"]["concepts"]:
        tasks.append({"key": "verkoop:" + concept["id"], "role": "verkoop", "status": concept["status"],
                      "priority": 2, "title": concept["offer"] + " — " + concept["audience"],
                      "detail": concept["next_step"]})
    return tasks


def atomic_write(path, content):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def update_inventory(path, mode, candidates, checked_at):
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "schema_version": 1, "mode": mode, "tasks": []}
    if previous["schema_version"] != 1 or previous["mode"] != mode:
        raise ValueError("Gebruik aparte outputmappen voor LIVE en DEMO; taakvoorraad blijft behouden.")
    entries = {}
    for task in previous["tasks"]:
        if task["id"] in entries:
            raise ValueError("Dubbele taak-id in bestaande taakvoorraad; bestand blijft behouden.")
        entries[task["id"]] = dict(task, current=False)
    for candidate in candidates:
        task_id = hashlib.sha256((mode + ":" + candidate["key"]).encode()).hexdigest()[:20]
        old = entries.get(task_id, {})
        entries[task_id] = dict(candidate, id=task_id, current=True,
                                created_at=old.get("created_at", checked_at), last_seen=checked_at)
    inventory = {"schema_version": 1, "mode": mode, "tasks": sorted(entries.values(), key=lambda task: task["id"])}
    atomic_write(path, json_text(inventory))
    return inventory


def markdown(report):
    roles = report["roles"]
    lines = ["# Postritme beheerrapport", "", "**" + report["evidence_label"] + "**", "",
             "Status: **" + report["status"] + "** · " + report["checked_at"], "",
             "Vier regelgestuurde rollen: Regie, Techniek, SEO en Sales. Geen LLM/API-integratie of autonome AI in dit script. Geen publicatie, mail, betaling of planning uitgevoerd.", "",
             "## Regie — hoofdcoördinator", "", "Status: **" + roles["regie"]["status"] + "**. " + roles["regie"]["next_action"], "",
             "Native heartbeat geconfigureerd op 2026-09-20, elke zes uur lokaal. Actuele activiteit en uitvoering niet door Python bevestigd. Volg COORDINATOR.md; voer één ronde tegelijk uit.", "",
             "Creditcontrole: **blocked**. Actueel saldo onbekend in dit rapport. Maximaal 1.200 van opgegeven 1.250 credits, met 100 credits reserve: effectieve bestedingsgrens 1.150. Controleer native get_usage_limits vóór elke AI-ronde en pauzeer bij onbekend saldo of 100 credits resterend. Best effort; geen harde accountcap.", "",
             "## Techniek en SEO", "",
             "Techniek: **" + roles["techniek"]["status"] + "**. SEO: **" + roles["seo"]["status"] + "**.", "",
             roles["techniek"]["scope"], ""]
    if roles["techniek"]["error"]:
        lines += ["Auditfout: " + roles["techniek"]["error"], ""]
    for row in roles["techniek"]["checks"]:
        lines.append("- " + row["path"] + ": " + str(row["status"]) + " — " + ("; ".join(row["issues"]) or "geen HTML-bevindingen"))
    health = roles["techniek"]["health"]
    if health:
        lines += ["", "/api/health: **" + health["status"] + "**. " + (json.dumps(health["flags"], ensure_ascii=False) if health["flags"] else health["error"]), "",
                  "De flags tonen alleen de gerapporteerde configuratie; geen bewijs van betaling, uitbetaling of bestandslevering."]
    lines += ["", "SEO-prioriteiten (1 eerst):", ""]
    for item in roles["seo"]["priorities"]:
        lines.append(f"- P{item['priority']} {item['path']} — {item['issue']}: {item['action']}")
    if not roles["seo"]["priorities"]:
        lines.append("Geen prioriteiten vastgesteld." if roles["techniek"]["status"] != "error" else "Geen volledige SEO-beoordeling mogelijk.")
    lines += ["", roles["seo"]["limitation"], "", "## Verkoop: blocked", ""]
    lines += ["- " + blocker for blocker in roles["verkoop"]["blockers"]]
    lines += ["", "Betaalroute: " + roles["verkoop"]["payment"]["provider"] + ". Sandbox: **" + roles["verkoop"]["payment"]["sandbox_status"] + "**; live: **" + roles["verkoop"]["payment"]["live_status"] + "**.", "",
              roles["verkoop"]["payment"]["verification"], "",
              "Levering: **blocked**. Backend heeft 8 lokale tests doorstaan volgens aangeleverde projectstatus; productiebetaling en levering zijn nog niet bewezen.", "",
              roles["verkoop"]["payment"]["source"], "",
              "Omzet, bestellingen en bezoekers: **onbekend (null)**. Er is geen transactiemeting aangesloten.", "",
              roles["verkoop"]["concept_status_note"], ""]
    for concept in roles["verkoop"]["concepts"]:
        lines += ["### " + concept["offer"], "", f"Status: {concept['status']}. Doelgroep: {concept['audience']}.", "",
                  "Kanaal: " + concept["channel"], "", "Concepttekst: “" + concept["copy"] + "”", "",
                  "CTA: “" + concept["cta"] + "”", "", "Volgende stap: " + concept["next_step"], ""]
        if "price_eur" in concept:
            lines += ["Prijs: €" + str(concept["price_eur"]) + " eenmalig. " + concept["price_status"], ""]
    lines += ["## Lokale taakvoorraad", "", "Status: " + report["inventory"]["status"], "",
              "tasks.json hergebruikt vaste taak-id's. current=false betekent alleen dat een taak niet uit de huidige audit volgt; niet dat hij is uitgevoerd. Voer één proces tegelijk uit per outputmap.", ""]
    if report["inventory"]["error"]:
        lines += ["Fout: " + report["inventory"]["error"], ""]
    else:
        for task in report["inventory"]["tasks"]:
            if task["current"]:
                lines.append(f"- [{task['status']}] {task['title']}: {task['detail']}")
    return "\n".join(lines) + "\n"


def run(output, offline_demo=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    checked_at = datetime.now(timezone.utc).isoformat()
    mode = "offline_demo" if offline_demo else "live"
    roles = {"techniek": technique(offline_demo)}
    roles["seo"] = seo(roles["techniek"])
    roles["verkoop"] = sales(roles["techniek"], roles["seo"], offline_demo)
    roles["regie"] = coordination(roles)
    try:
        inventory = update_inventory(output / "tasks.json", mode, task_candidates(roles), checked_at)
        inventory.update(status="ready", error=None)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        inventory = {"status": "error", "error": f"{type(exc).__name__}: {exc}", "tasks": []}
    report = {
        "schema_version": 1, "checked_at": checked_at, "mode": mode, "origin": monitor.ORIGIN,
        "evidence_label": "DEMO / FIXTURE — verzonnen audit, geen bewijs over de echte website" if offline_demo
                          else "LIVE — publieke HTML-audit; verkoopstatus is aangeleverde projectinformatie",
        "status": "error" if roles["techniek"]["status"] == "error" or inventory["status"] == "error" else "blocked",
        "roles": roles, "inventory": inventory,
        "execution": {"type": "rule_based_python", "llm_integration": False, "external_mutations": [], "schedule_configured": True, "schedule_active": None},
    }
    atomic_write(output / "report.json", json_text(report))
    atomic_write(output / "report.md", markdown(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, required=True, help="Lokale map voor report.json, report.md en tasks.json")
    parser.add_argument("--offline-demo", action="store_true", help="Uitsluitend fixture-demonstratie; geen netwerkcontrole")
    args = parser.parse_args()
    try:
        report = run(args.output, args.offline_demo)
    except OSError as exc:
        parser.exit(1, f"Rapport kon niet worden opgeslagen: {exc}\n")
    print(f"{report['evidence_label']}\nStatus: {report['status']}\nRapport: {args.output.resolve() / 'report.md'}")
    return {"ready": 0, "blocked": 2, "error": 1}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
