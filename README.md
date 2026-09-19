# Postritme beheer

Leescontroles voor de publieke Postritme-website. Dit project bevat geen bankgegevens, betaalcodes of betaalde content.

De controle bekijkt bereikbaarheid en technische SEO van zeven pagina’s, inclusief de openbare productpagina `/campagnepakket/`. Zij koopt geen advertenties, publiceert geen berichten en verwerkt geen betalingen. Een geslaagde controle zegt niets over verkeer, ranking of omzet.

Gebruik voor alleen de websitecontrole: `python3 monitor.py`.

## Voorbereid kantoor

`python3 office.py --output office-output` voert drie regelgestuurde rollen uit: techniek, SEO en verkoop. De rollen delen hun controlebevindingen en maken een lokale taakvoorraad en rapporten. Bestaande taken blijven herkenbaar wanneer dezelfde uitvoermap opnieuw wordt gebruikt. `python3 -m unittest test_office.py` controleert de foutafhandeling en voorkomt dat herhaald draaien dezelfde taken verdubbelt.

Dit zijn vaste regels en conceptteksten, geen zelfstandig denkende AI-agenten. Er is geen model gekoppeld en geen marketingkanaal aangesloten. Het livebetaalaccount is niet geactiveerd of geverifieerd. Verkoop blijft geblokkeerd; omzet blijft onbekend (`null`). De uitvoer meldt deze beperkingen. Een offline demonstratie gebruikt alleen fixtures en telt niet als een websitecontrole.

De gekozen betaalroute is Stripe/Managed Payments. De gebruiker heeft een Stripe-account aangemaakt; de publieke website en productomschrijving zijn ingevuld. De Postritme-sandbox bevat een product en een Managed Payments-testlink voor €9 eenmalig inclusief belasting; er is nog geen testtransactie uitgevoerd (`ready`). Het liveaccount blijft `blocked`: activatie en verificatie zijn niet afgerond en er is geen echte checkout, levering of productie-APIkoppeling. Deze status is aangeleverde projectinformatie; de publieke HTML-audit controleert het betaalaccount niet. Er staan geen bankgegevens of geheime sleutels in dit project.

Het campagnepakket is klaar: 36 briefings, 12 per branche voor 3 branches, met vier weken per branche. De ZIP bevat 4 Markdown-bestanden en één printbare `LEES-MIJ.html`. De productpagina is openbaar op `/campagnepakket/`, maar het pakket is nog niet te koop. €9 eenmalig is ingesteld als testprijs; de liveprijs is nog niet ingesteld. Na liveactivatie en verificatie moeten het product voor Managed Payments, de checkout en de bestandslevering nog worden ingericht en getest.

De dagelijkse GitHub Actions-controle is voorbereid, maar nog NIET actief: de huidige GitHub-koppeling mag geen workflowbestand toevoegen. Het workflowbestand is lokaal beschikbaar. Na autorisatie kan het worden toegevoegd en uitgevoerd. GitHub kan geplande uitvoeringen vertragen; openbare repositories kunnen na 60 dagen zonder activiteit hun planning verliezen. Controleer dan de Actions-pagina. Dit is technisch toezicht, geen autonome marketing- of omzetagent.

De voorbereide workflow voert tests en de drie rollen uit en bewaart het rapport als samenvatting van de uitvoering. De GitHub-runner is tijdelijk; de lokale taakvoorraad wordt daar niet tussen uitvoeringen bewaard. Niet-geactiveerde livebetaling verschijnt als `blocked` in het rapport, terwijl een mislukte sitecontrole de workflow laat falen. Het workflowbestand staat nog niet in de externe repository.
