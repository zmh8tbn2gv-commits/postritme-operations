#!/usr/bin/env python3
"""Read-only availability and HTML/SEO checks for the public Postritme site."""
import sys, urllib.request, urllib.parse, json, os
from html.parser import HTMLParser
from datetime import datetime, timezone
ORIGIN = "https://postritme.pzcqqb56gx.chatgpt.site"
PATHS = ["/", "/inspiratie/", "/contentkalender-horeca/", "/contentkalender-kappers-beauty/", "/contentplanning-zelfstandig-adviseurs/", "/privacy/", "/campagnepakket/"]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.h1 = 0; self.title = ""; self.in_title = False; self.description = ""; self.canonical = ""; self.noindex = False; self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "h1": self.h1 += 1
        if tag == "title": self.in_title = True
        if tag == "meta" and a.get("name") == "description": self.description = a.get("content", "")
        if tag == "meta" and a.get("name") == "robots" and "noindex" in a.get("content", "").lower(): self.noindex = True
        if tag == "link" and a.get("rel") == "canonical": self.canonical = a.get("href", "")
        if tag == "a": self.links.append(a.get("href", ""))
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title += data

def audit(origin=ORIGIN):
    rows=[]; titles=set()
    for path in PATHS:
        issues=[]
        try:
            req=urllib.request.Request(origin+path, headers={"User-Agent":"Postritme-availability-check/1.0"})
            with urllib.request.urlopen(req, timeout=20) as response:
                body=response.read(1_000_000).decode("utf-8"); status=response.status
                if urllib.parse.urlsplit(response.url).netloc != urllib.parse.urlsplit(origin).netloc: issues.append("Unexpected redirect")
                if "noindex" in response.headers.get("X-Robots-Tag", "").lower(): issues.append("HTTP noindex")
            parser=Page(); parser.feed(body)
            if parser.h1 != 1: issues.append("Expected one H1")
            if not parser.title.strip(): issues.append("Missing title")
            if parser.title in titles: issues.append("Duplicate title")
            titles.add(parser.title)
            if not parser.description: issues.append("Missing description")
            if parser.canonical != origin+path: issues.append("Incorrect canonical")
            if parser.noindex: issues.append("HTML noindex")
            if "Postritme" not in body: issues.append("Unexpected page content")
            rows.append({"path":path,"status":status,"title":parser.title,"issues":issues})
        except Exception as exc:
            rows.append({"path":path,"status":"error","issues":[str(exc)]})
    return rows

def audit_health(origin=ORIGIN):
    """Public configuration flags only; not proof of payment or delivery."""
    url = origin + "/api/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Postritme-availability-check/1.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            if urllib.parse.urlsplit(response.url).netloc != urllib.parse.urlsplit(origin).netloc:
                raise ValueError("Unexpected health redirect")
            data = json.loads(response.read(10_000).decode("utf-8"))
        allowed = {"status": {"ok"}, "storage": {"ready", "unavailable"},
                   "payments": {"configured", "disabled"}, "webhooks": {"configured", "disabled"}}
        if not isinstance(data, dict) or any(data.get(key) not in values for key, values in allowed.items()):
            raise ValueError("Unexpected health payload")
        return {"status": "ready", "url": url, "flags": {key: data[key] for key in allowed}, "error": None}
    except Exception as exc:
        return {"status": "error", "url": url, "flags": None, "error": str(exc)}

def main():
    rows=audit(); health=audit_health(); failed=any(row["issues"] for row in rows) or health["status"] == "error"
    report={"checked_at":datetime.now(timezone.utc).isoformat(),"ok":not failed,"checks":rows,"health":health}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:
            f.write("## Postritme: "+("controle geslaagd" if not failed else "actie nodig")+"\n\n")
            f.write("Controle op bereikbaarheid, paginatitels, H1, beschrijvingen, canonical en indexeerbaarheid. Dit meet geen bezoekers of omzet.\n\n")
            for row in rows: f.write("- "+row["path"]+": "+("OK" if not row["issues"] else "; ".join(row["issues"]))+"\n")
            f.write("- /api/health: "+json.dumps(health,ensure_ascii=False)+"\n")
    return int(failed)
if __name__ == "__main__": sys.exit(main())
