# Besluitenlog: Laadlichten

Dit log wordt alleen aangevuld. Een oud besluit pas je niet aan: je vervangt het met een nieuwe entry ("superseded by"). Het format staat in [`/CLAUDE.md`](../../CLAUDE.md).

## D-001: Stack: één statische kaartpagina met Leaflet en PDOK-ondergrond
- **Status:** accepted (PR #1, reactie eigenaar: "Ga verder met dit plan")
- **When / who:** 2026-11-05 12:55 · Claude
- **Decision:** `prototype/index.html` opent met een dubbelklik.
  - Leaflet 1.9.4 komt met een vaste versie van cdnjs.
  - De ondergrond is de PDOK BRT-achtergrondkaart (grijs).
  - De data staat in `data.js` (`window.LAADLICHTEN = …`).
  - De opmaak volgt de themadag-prototypes: KPI-tegels, panelen en een uitklapblok "Hoe wordt dit berekend?".
- **Why:** voldoet aan de standaard in de repo (geen build, geen server, geen `fetch`). Het is hetzelfde patroon als de eerdere themadag-prototypes, en PDOK is open en levert een rustige ondergrond.
- **Rejected alternative:** een marimo- of Python-dashboard. Dat heeft een draaiende kernel nodig en is lastiger op een willekeurige laptop te openen. Een eigen of vendored Leaflet-kopie hebben we ook niet gekozen, omdat de repo-standaard een vaste CDN-versie voorschrijft.

## D-002: Echte VRI-data, alleen lokaal; in git staat alleen het prep-script
- **Status:** accepted (PR #1, reactie eigenaar: "Ga verder met dit plan")
- **When / who:** 2026-11-05 12:55 · Claude
- **Decision:**
  - `prototype/prep_laadlichten.py` (PEP 723 met duckdb en geopandas, draait met `uv run`) leest de lokale VRI-bronnen.
  - Het script schrijft aggregaten per VRI × signaalgroep naar `prototype/data/private/data.js`. Dat pad wordt door `**/data/private/` in `.gitignore` buiten git gehouden.
  - Velden die we weglaten: EAN-code, aannemers, opmerkingen en bijzonderheden.
  - Zonder data toont de pagina een melding: "draai eerst het prep-script".
- **Why:** de VRI-data is geen open data en de repo is publiek. De repo-regel is alleen synthetische of open data. Met echte data blijft de demo herkenbaar ("dit is onze stad") en blijft de echte bevinding van 87 stille signaalgroepen zichtbaar. Zonder de privévelden is later publiceren makkelijk, mits de data-eigenaar akkoord geeft (open vraag 5).
- **Rejected alternative:** synthetische VRI's. Dan verdwijnt de echte storingsbevinding, en daarmee de kern van "de kaart ziet zelf wat er mis is". Aggregaten nu al committen hebben we ook niet gedaan: daarvoor is eerst toestemming van de data-eigenaar nodig.

## D-003: Definitie van de signalen "mogelijke storing" en "trendbreuk"
- **Status:** superseded by D-007
- **When / who:** 2026-11-05 12:55 · Claude
- **Decision:**
  - **Mogelijke storing:** een signaalgroep die van sep 2024 tot en met jul 2026 gemiddeld ≥5 voertuigen per uur telde, en in de laatste 30 dagen van de data 0. Eerste telling: 87 signaalgroepen op 15 VRI's.
  - **Trendbreuk:** in de laatste 30 dagen minder dan 50% van het historische gemiddelde, maar wel meer dan 0.
  - **Vervanging:** vervangjaar ≤ 2027.
  - Signaalgroepen die altijd 0 tellen (569) krijgen geen signaal.
- **Why:** elke 0 telt 709 signaalgroepen, en de meeste daarvan zijn structureel nul (bijvoorbeeld groepen zonder telling). Pas na een filter op "was eerder actief" houd je een lijst over waar Wegbeheer iets mee kan.
- **Rejected alternative:** elke signaalgroep met 0 in de laatste maand. Dat geeft te veel ruis, en de demo zou de verkeerde kant op wijzen. Een statistisch anomaliemodel (seizoen, weekdag) hebben we ook niet gekozen: in 90 minuten is dat niet uit te leggen of te valideren.

## D-004: Koppeling tussen de drie bronnen en het lezen van signaalgroepen uit rijstrooknamen
- **Status:** accepted (PR #1, reactie eigenaar: "Ga verder met dit plan")
- **When / who:** 2026-11-05 12:55 · Claude
- **Decision:**
  - **Sleutel:** `Installatienr.` (kenmerken) = `vri_id` (intensiteit) = het deel vóór `-` van ITF `intersection`. Eén VRI kan meerdere ITF-kruispunten hebben, bijvoorbeeld `11070-1` en `11070-2`. De drie bronnen overlappen samen op 124 VRI's.
  - **Signaalgroep:** de eerste twee cijfers van de rijstrooknaam (`02_1` en `03.1` worden sg 02). Namen met `afvoer` of een windrichting (`ZW_…`) zijn afvoerstroken.
  - **Dekking:** zo herkennen we 2.228 toeleidende rijstroken. 109 van de 181 kruispunten hebben er ≥4. De overige notaties (`Statenweg-25`, `2-2`, `88-1`) slaan we vandaag over.
- **Why:** dit is een join op ID's die al in de data staan, en dat is betrouwbaarder dan een ruimtelijke join. De eenvoudige parser dekt genoeg kruispunten voor de kaart en voor het kiezen van een demokruispunt.
- **Rejected alternative:** een ruimtelijke join op afstand. Die geeft fouten bij kruispunten die dicht bij elkaar liggen. Een volledige parser voor alle notaties hebben we ook niet gebouwd: dat kost tijd en levert vandaag weinig extra op.

## D-005: Stretch: schets van een basisregeling voor 1 kruispunt, conflicten via de standaardnummering
- **Status:** accepted (PR #1, reactie eigenaar: "Ga verder met dit plan")
- **When / who:** 2026-11-05 12:55 · Claude
- **Decision:** dit bouwen we alleen als de kaart klaar is.
  - We kiezen één kruispunt uit de 109 met een standaardopbouw: vier takken, signaalgroepen 01–12 auto, 2x fiets, 3x voetganger, 4x/5x ov.
  - **Conflictmatrix:** volgt uit de Nederlandse standaard-kruispuntnummering. Het nummer zegt welke tak en welke richting het is. De ITF-geometrie gebruiken we om dat te tonen en te controleren.
  - **Groentijden:** de cyclustijd en groenverdeling komen uit Webster op het maatgevende werkdagspitsuur. Daarvoor gebruiken we de logica van het eerdere themadag-prototype "Regelingsschets" (`model()`, `renderPlan()`).
  - **Beleid:** een knop zet ov-prioriteit aan of uit.
  - **Uitvoer:** een korte functionele specificatie in tekst.
  - De disclaimer staat zichtbaar in beeld.
- **Why:** het team vraagt om "geometrie + data + beleid → basisregeling". Eén kruispunt laat die potentie zien zonder dat we iets beloven wat we niet kunnen valideren. In de ITF-export zit geen laag met rijstrookverbindingen, dus de standaardnummering is de meest robuuste bron voor conflicten.
- **Rejected alternative:** conflicten puur uit kruisende rijstrookgeometrie halen. Zonder verbindingen weet je niet waar een rijstrook naartoe gaat. Alle kruispunten doen hebben we ook niet gekozen: dat is niet te valideren en schept verwachtingen die we niet waarmaken. Helemaal geen laag 2 bouwen viel af, omdat dan juist de ambitie van het team ontbreekt.

## D-006: Alleen Rotterdam
- **Status:** accepted (PR #1, reactie eigenaar: "Ga verder met dit plan")
- **When / who:** 2026-11-05 12:55 · Claude
- **Decision:** de kaart bevat alleen Rotterdamse VRI's. Den Haag staat in de parking lot.
- **Why:** voor Rotterdam hebben we kenmerken, geometrie en intensiteit. Voor Den Haag hebben we geen VRI-data. Het "(Den Haag)" in het formulier is waarschijnlijk een verwijzing naar het voorbeeld van een levende kaart (open vraag 1).
- **Rejected alternative:** Den Haag-VRI's uit open bronnen halen. Dat lukt niet binnen het tijdsbudget, en de data zou ongelijk zijn met die van Rotterdam.

## D-007: Minder data: alleen september 2025 tegenover september 2026
- **Status:** accepted (vraag eigenaar: "gebruik niet alles, het is een prototype; zo simpel mogelijk")
- **When / who:** 2026-11-05 13:15 · Claude
- **Decision:**
  - Uit de intensiteitsdata gebruiken we alleen september 2025 (basis) en september 2026 (nu).
  - **Stil:** de signaalgroep telde in de basis ≥5 vtg/uur gemiddeld en nu 0, of er zijn nu geen rijen.
  - **Daling:** nu minder dan 50% van de basis.
  - **Per VRI:** *geen tellingen ontvangen* als álle normaal actieve signaalgroepen stil zijn, *mogelijke lusstoring* als een deel stil is, en anders *daling*.
  - **Resultaat:** 16 VRI's ontvangen geen tellingen meer, 9 hebben een mogelijke lusstoring, 40 een daling, 180 zijn ok en 47 hebben geen intensiteitsdata.
  - De dataset staat lokaal in `<repo>/data/` (uitgesloten van git). Het prep-script leest hem daar.
- **Why:** de eigenaar vroeg om eenvoud. Dezelfde maand een jaar eerder vergelijken haalt seizoen en zomervakantie weg en is in één zin uit te leggen. De 16 VRI's met totale uitval zijn allemaal iVRI's. Dat wijst eerder op de datalevering dan op kapotte lussen, dus de UI zegt "geen tellingen ontvangen" en niet "storing".
- **Rejected alternative:** de basis van 25 maanden uit D-003. Die gebruikt meer data, de zomerdip vertekent de vergelijking en het is lastiger uit te leggen.

## D-008: Waarschuw bij mogelijke hernummering in plaats van stilletjes "storing" te melden
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:** de kaart toont een waarschuwing als een VRI met een signaal ook signaalgroepen heeft die vorig jaar niet telden (basis < 1) en nu wel (≥ 5 per uur). De tekst: "Misschien is de regeling aangepast of zijn de signaalgroepen hernummerd." De status zelf blijft staan. Dit speelt bij 4 VRI's, bijvoorbeeld Schepenstraat - Schieweg: daar vielen sg 01 en 12 stil en tellen sg 03, 08 en 11 nieuw.
- **Why:** het team vroeg om een tool met een kritische houding tegenover zijn eigen input. Een stille signaalgroep is niet altijd een kapotte lus. Dit vangt de meest voor de hand liggende andere verklaring af, zonder extra data.
- **Rejected alternative:** zulke VRI's uit de signalen halen. Dan verdwijnt een mogelijk echte storing. Een aparte status "hernummerd" hebben we ook niet gekozen: dat is zonder bevestiging van Wegbeheer te stellig.
