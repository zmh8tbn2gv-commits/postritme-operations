# Postritme — werkprotocol van Regie

Peildatum: 20 september 2026. Dit document is de duurzame overdracht voor de hoofdcoördinator. `office.py` is regelgestuurde Python, geen autonoom AI-kantoor. Native AI-uitvoering en planning horen bij Codex en worden afzonderlijk ingesteld.

## Feiten en blokkades

- Zeven publieke pagina's, inclusief `/campagnepakket/`. De actuele bereikbaarheid komt uit `monitor.py`; eerdere resultaten gelden niet als nieuwe meting.
- Stripe-accountactivatie is in de UI voltooid. Liveproduct `prod_VI6OJQdlN0bFkl` bestaat voor €9 eenmalig inclusief belasting. Livecheckout is nog niet gemaakt of ingeschakeld.
- De beperkte Checkout-sleutel ontbreekt: `Verification required` blijft laden. Los de verificatiestap op; omzeil deze controle niet.
- Het pakket is klaar: 36 briefings, drie branches, vier weken per branche; ZIP met vier Markdown-bestanden en een printbare `LEES-MIJ.html`.
- Siteversie 4 is op 2026-09-20 succesvol gedeployed (`appgdep_6aaf93a79c508191b0c555f48b6eed27`). De volgende audit gaf zeven routes HTTP 200 en `/api/health`: `status: ok`, `storage: ready`, `payments: disabled`, `webhooks: disabled`. De backend heeft volgens de projectoverdracht acht lokale tests doorstaan. Livebetaling en levering zijn nog niet bewezen; doe bij volgende rondes een nieuwe controle.
- Geen marketingkanaal of verkeers-/omzetmeting aangesloten. Geen echte omzet aangetoond; onbekende bedragen blijven `null`.
- GitHub weigert workflowupload wegens ontbrekende rechten. Het ongetrackte workflowbestand blijft buiten commits en pushes; gebruik geen andere credentialroute om dit te omzeilen.
- Native heartbeat `postritme-regie-techniek-seo-en-sales` is op 2026-09-20 geconfigureerd voor elke zes uur lokaal en toen native als `ACTIVE` bevestigd. Python bevestigt de actuele activiteit of uitvoering niet; de planning kan later worden gepauzeerd. Gebruik dit automation-id met `automation_update` voor inspectie of pauzeren. Computer en Codex-app moeten beschikbaar blijven; er is geen ingerichte cloud-AI-uitvoering buiten Codex of garantie op ononderbroken 24/7 werk.

## Verdeling

| Rol | Werk | Eerstvolgende taak |
| --- | --- | --- |
| Regie | Hoofdcoördinatie, credits, prioriteiten, ontdubbeling, rapportage | Controleer credits; kies één uitvoerbare taak uit de voorraad |
| Techniek | Site, healthflags, backend en levering | Controleer backenddeployment en veilige bestandslevering; herstel storingen eerst |
| SEO | Titels, beschrijvingen, canonicals, indexeerbaarheid, meting | Verwerk auditbevindingen op prioriteit; regel meettoegang vóór resultaatclaims |
| Sales | Product, checkout, kooproute en verkoopteksten | Los Stripe-verificatie op; test na werkende levering de checkout |

De vier rollen delen één taakvoorraad. Ze vereisen geen vier parallelle AI-runs of aparte modellen. Gebruik één coördinator met sequentiële rolstappen. Vaste taak-id's voorkomen dubbele taken. `ready` kan worden opgepakt; `blocked` wacht op een afhankelijkheid; `error` vraagt herstel. Rapportgeneratie voert een taak niet uit.

## Creditcontrole vóór elke AI-ronde

1. Doe als eerste handeling native `mcp__codex_app__get_usage_limits`. De start van een AI-ronde kan zelf al verbruik veroorzaken; controleer vóór verder uitvoerend werk en opnieuw vóór een dure vervolgactie.
2. Gebruik bij voorkeur `rateLimitsByLimitId.codex.credits.balance`, anders de bijbehorende `rateLimits.credits.balance`. Alleen een geldige actuele numerieke waarde telt. `usedPercent` is verbruik binnen een tijdvenster, geen aantal credits. Ontbrekende, tegenstrijdige of onleesbare waarden betekenen onbekend.
3. Oorspronkelijk opgegeven saldo: 1.250; maximaal 1.200 te besteden. Houd daarnaast 100 credits reserve. Stop bij saldo **100 of lager**; vanaf 1.250 betekent dit hoogstens 1.150 besteed. Andere accountactiviteit verbruikt hetzelfde saldo. Verhoog het budget niet automatisch bij een top-up of reset.
4. Bij onbekend saldo, bereikt budget of reserve: geen extra AI-, onderzoeks-, herstel- of marketingtaken. Lees de bestaande instellingen van `postritme-regie-techniek-seo-en-sales` met `automation_update` en pauzeer ditzelfde id; behoud overige instellingen en registreer de reden. Meld eenmaal dat invoer of budgetcontrole nodig is. Activeer niet zelf opnieuw.
5. Registreer lokaal alleen tijdstip, bruikbaar saldo, beslissing en afgeronde taak. Bewaar geen volledig accountantwoord, account-id, tokens of sleutels in deze repository. Leid geen projectspecifieke kosten af uit een accountbreed saldo.
6. Werk in korte stappen, zonder onnodige parallelle runs of extra modellen. Koop geen credits, wissel geen reset in en activeer geen automatische uitgaven.

Dit is best effort, geen harde accountcap. Saldo kan vertraagd zijn of door ander werk veranderen; lopende uitvoering kan de reserve passeren. `office.py` kan de native tool niet zelf aanroepen en rapporteert geen verzonnen actueel saldo of actieve budgethandhaving. De native coördinator moet dit protocol uitvoeren.

De officiële [Codex App Server-documentatie](https://learn.chatgpt.com/docs/app-server) onderscheidt quota per tijdvenster van optionele creditdetails. De native tool is de bron voor actuele accountmeting; documentatie is geen saldobewijs.

## Eén ronde

1. Controleer credits en lees deze overdracht plus de laatste lokale rapporten.
2. Controleer of al een ronde loopt. Eén proces per uitvoermap; start bij overlap geen tweede ronde.
3. Voer `python3 office.py --output office-output` uit. Dit leest zeven pagina's en `/api/health` en schrijft `report.json`, `report.md` en `tasks.json`. Exitcode 2 betekent een bekende blokkade; 1 betekent een controle- of rapportfout.
4. Kies één concrete taak: storing/budget, veilige levering, Stripe-verificatie en checkout, meting/SEO, dan verkoopvoorbereiding. Herhaal geen onderzoek naar dezelfde blokkade zonder nieuwe informatie.
5. Gebruik bestaande autorisatie voor die taak. Dit protocol geeft geen toestemming voor ongevraagde mail, externe berichten, advertentie-uitgaven of aankopen. Claim geen omzet, bezoekers of ranking zonder gegevens.
6. Controleer het resultaat en werk feitelijke projectstatus bij. Blijf stil zonder betekenisvolle verandering. Meld wel voltooiing, storing, gewijzigde blokkade of vereiste gebruikersactie.

## Healthstatus

De JSON bevat `status: ok`, `storage: ready|unavailable`, `payments: configured|disabled` en `webhooks: configured|disabled`. De monitor accepteert uitsluitend deze waarden en neemt geen andere velden over. Een geldig antwoord toont een bereikbare healthendpoint. `unavailable` of `disabled` is een beperking; `configured` bevestigt geen geslaagde betaling, webhook, download of uitbetaling. Controleer de keten afzonderlijk voordat de koopmogelijkheid wordt ingeschakeld.

Gebruik `--offline-demo` alleen in een aparte uitvoermap. Een fixture is nooit bewijs over site, Stripe, levering of credits.
