# Postritme beheer

Dit pakket controleert zeven publieke pagina's en `/api/health`. Het publiceert geen berichten, verstuurt geen mail en verwerkt geen betalingen. Een geslaagde controle bewijst geen omzet, ranking, uitbetaling of werkende bestandslevering.

## Uitvoeren

- Website en healthcontrole: `python3 monitor.py`.
- Rollen, rapporten en taken: `python3 office.py --output office-output`.
- Tests zonder liveverzoeken: `python3 -m unittest -v test_office.py`.
- Afzonderlijke fixture-demo: `python3 office.py --offline-demo --output reports/demo`.

De uitvoer bestaat uit `report.json`, `report.md` en `tasks.json`. Herhaalde uitvoeringen hergebruiken vaste taak-id's. Eén proces tegelijk per map. `current=false` betekent niet dat een taak is uitgevoerd. Exitcode `2` betekent een blokkade; `1` een controle- of rapportfout.

## Regie, Techniek, SEO en Sales

[COORDINATOR.md](COORDINATOR.md) bevat het duurzame werkprotocol. Regie bewaakt prioriteiten, afhankelijkheden, credits en de gedeelde taakvoorraad. Techniek controleert bereikbaarheid en levering, SEO werkt auditbevindingen uit en Sales bewaakt product, checkout en marketingvoorbereiding.

`office.py` voert vaste Python-regels uit, zonder gekoppeld AI-model of marketingkanaal. Een native Codex-heartbeat wordt afzonderlijk ingericht; deze versie claimt nog geen actieve planning of 24/7 beschikbaarheid. Lokale uitvoering vereist een beschikbare computer en Codex-app. Er is geen ingerichte cloud-AI-uitvoering buiten Codex.

De coördinator moet vóór elke AI-ronde native `get_usage_limits` lezen. Maximaal 1.200 van de opgegeven 1.250 credits mogen worden besteed, met 100 credits reserve: de effectieve grens is 1.150 vanaf het oorspronkelijke saldo. Bij 100 credits resterend of onbekend saldo pauzeert het werk. Dit is een best effort werkinstructie, geen harde accountcap. Python leest het native saldo niet zelf en rapporteert creditcontrole daarom als `blocked`, met onbekend actueel saldo.

## Verkoopstatus op 20 september 2026

Accountactivatie is in de Stripe-UI voltooid. Liveproduct `prod_VI6OJQdlN0bFkl` bestaat voor €9 eenmalig inclusief belasting. De livecheckout is nog niet gemaakt of ingeschakeld. Een beperkte Checkout-sleutel kon niet worden verkregen doordat `Verification required` blijft laden.

Het campagnepakket bevat 36 briefings, 12 per branche voor 3 branches, met vier weken per branche. De ZIP bevat 4 Markdown-bestanden en één printbare `LEES-MIJ.html`. `/campagnepakket/` is openbaar, maar het pakket is nog niet te koop.

De leveringsbackend heeft volgens de aangeleverde projectstatus acht lokale tests doorstaan. Productiebetaling en levering zijn nog niet van begin tot eind bewezen. De healthcontrole leest live `status`, `storage`, `payments` en `webhooks`; `configured` bewijst alleen de gerapporteerde configuratie. Een gezonde endpoint bewijst geen geslaagde betaling of download. Omzet, bestellingen en bezoekers blijven onbekend (`null`) zonder meetgegevens.

## GitHub

De dagelijkse GitHub Actions-controle is voorbereid maar niet actief. Workflowupload is geweigerd wegens ontbrekende rechten; deze blokkade wordt niet omzeild. Het lokale workflowbestand blijft buiten commits en pushes. De tijdelijke GitHub-runner bewaart zonder aanvullende opslag geen taakvoorraad tussen uitvoeringen.
