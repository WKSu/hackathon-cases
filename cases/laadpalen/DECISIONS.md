# Besluitenlog: Laadpalen

Dit log wordt alleen aangevuld. Een oud besluit pas je niet aan: je vervangt het met een nieuwe entry ("superseded by"). Het format staat in [`/CLAUDE.md`](../../CLAUDE.md).

## D-001: Stack: één statische kaartpagina met Leaflet en PDOK-ondergrond
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:**
  - `prototype/index.html` opent met een dubbelklik.
  - Leaflet 1.9.4 komt met een vaste versie van cdnjs.
  - De ondergrond is de PDOK BRT-achtergrondkaart (grijs), met de PDOK-luchtfoto als tweede keuze.
  - De data staat in `data.js` (`window.LAADPALEN = …`).
  - Dit is hetzelfde patroon als de VRI-case (`cases/laadlichten`, D-001).
- **Why:** voldoet aan de standaard in de repo (geen build, geen server, geen `fetch` van lokale bestanden). Met de luchtfoto kan een ambtenaar de straat herkennen, zoals bomen, stoep en geveltuinen.
- **Rejected alternative:** een marimo- of Python-dashboard. Dat heeft een draaiende kernel nodig en is lastiger op een willekeurige laptop te openen.

## D-002: Gemeentelijke lagen alleen lokaal; in git staat alleen het prep-script
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:**
  - `prototype/prep_laadpalen.py` (PEP 723, draait met `uv run`) leest de lokale gemeentelijke lagen (parkeervakken, bijzondere vakken, bomen). Het haalt de BGT op bij PDOK en leest de CBS-vierkanten.
  - Het script schrijft naar `prototype/data/private/data.js`. Dat pad wordt door `**/data/private/` in `.gitignore` buiten git gehouden.
  - Zonder data toont de pagina een melding: "draai eerst het prep-script".
- **Why:** de repo is publiek, en van de gemeentelijke lagen weten we nog niet of ze open data zijn. BGT en CBS zijn open. Met de echte vakken en bomen blijft de demo herkenbaar ("dit is mijn straat").
- **Rejected alternative:** alleen open data (BGT-parkeervlakken en OSM-laadpalen). In de BGT staan geen losse vakken en geen laadvakken, en een laadpaal staat juist op de lijn tussen twee vakken. Synthetische vakken hebben we ook niet gekozen: dan klopt de straat niet meer met de luchtfoto.

## D-003: Demogebied: de zes vooroorlogse buurten van Noord
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:** Oude Noorden, Agniesebuurt, Provenierswijk, Bergpolder, Liskwartier en Blijdorp. Samen ongeveer 16.700 parkeervakken. Een lijst bovenin het script bepaalt de buurten.
- **Why:** het formulier noemt "met name oudere wijken". Dit is één aaneengesloten gebied met smalle stoepen, veel bomen en een mix van langs- en dwarsparkeren. Het is groot genoeg om verschillen te zien, en klein genoeg voor een vlotte kaart en een korte BGT-download.
- **Rejected alternative:** de hele stad (166.598 vakken). De BGT-download en de kaart worden dan te zwaar voor 90 minuten. Losse wijken verspreid over de stad maken de overzichtskaart rommelig.

## D-004: Toets per parkeervak volgens de Beleidsregel 2025, met zichtbare aannames
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:** elk openbaar vak krijgt per criterium ✓ of ✗. De bron is de *Beleidsregel plaatsing laadpunten in de openbare ruimte gemeente Rotterdam 2025* (Gemeenteblad 2025, 307736, bijlage "Inpassingscriteria").

  | Criterium | Uit de beleidsregel | Onze uitwerking |
  |---|---|---|
  | Stoepbreedte | "minimale trottoirdoorloop van 2 meter, plaatselijk een minimale doorgang van 120 cm na plaatsing"; uitzonderlijk 90 cm | stoep ≥ 2,0 m = kandidaat; 1,7–2,0 m = maatwerk (90 cm doorgang). Schuifje |
  | Bomen | "geen grote bomen nabij laadpunten" (geen getal) | **aanname:** groot = hoogteklasse ≥ 12 m. De paal staat niet binnen de kroonprojectie (straal = kroondiameter / 2), plus een marge (schuifje, standaard 1 m) |
  | Uitstapstrook | "niet op de smalle uitstapstrook tussen parkeerplaats en fietspad" | de stoepkant grenst aan een fietspad, of de strook is < 1,5 m met een fietspad erachter |
  | Parkeerduurbeperking | "niet in zones met parkeerduurbeperking" | vak ligt in een overlay *Blauwe zone* of een type *met tijdsbeperking* / *tijdsafhankelijk* |
  | Bijzondere vakken | (impliciet) | gehandicapten, laden/lossen, deelauto, taxi enz. vallen af. *Eigen terrein* doet niet mee |
  | Groen | niet in de beleidsregel; wel in het formulier ("niet in groen plaatsen") | de stoepkant van het vak grenst aan BGT-groen in plaats van een voetpad = ongeschikt |
  | Inrit | niet in de beleidsregel; wel in het formulier | **aanname:** een BGT-inrit binnen 2 m van de paal = maatwerk |
  | Laagspanningskabel ≤ 25 m, nooddeuren | in beleidsregel resp. formulier | niet in de data. Elk vak krijgt "ter plaatse checken" |
- **Why:** de toets moet herleidbaar zijn naar de regel, anders vertrouwt een ambtenaar hem niet. Waar de regel geen getal noemt, maken we een aanname die zichtbaar is en die je kunt verschuiven.
- **Rejected alternative:** één samengestelde geschiktheidsscore. Die is niet uit te leggen, en je ziet niet welke regel een vak tegenhoudt.

## D-005: Stoepbreedte gemeten loodrecht vanaf de stoeprand van het vak, door de BGT
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:**
  - Per vak bepalen we de kortste omsluitende rechthoek. De rand waarachter BGT-voetpad ligt, is de stoeprand.
  - Vanuit het midden van die rand trekken we een lijn loodrecht de stoep op. De lengte binnen het aaneengesloten voetpad is de stoepbreedte.
  - De paal komt op de hoek met het buurvak, 50 cm uit de band ("op de scheidingslijn tussen parkeervakken, 50 cm uit de band").
  - Als er na 0,3–1,5 m nog BGT-parkeervlak ligt, slaan we dat over: de twee bronnen liggen niet precies op elkaar.
- **Why:** dit benadert hoe een inspecteur met een meetlint meet, en het werkt voor langs- en dwarsparkeren. Met paal op 0,5 m en een paal van ~0,3 m diep geldt: 2,0 m stoep laat 1,2 m doorgang over. Dat is precies de 120 cm uit de regel.
- **Rejected alternative:** de breedte van het hele voetpadvlak (oppervlak / halve omtrek). Dat middelt smalle en brede stukken en zegt niets over de plek van de paal. Een rasteranalyse hebben we ook niet gekozen, omdat die meer rekentijd kost en lastiger is uit te leggen.

## D-006: "Ruimte in het laadnetwerk" = tekort aan laadpunten binnen 200 m t.o.v. 1 op 10
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:**
  - **Dekking:** per vak tellen we binnen 200 m de bestaande laadvakken en de openbare parkeervakken.
  - **Tekort:** norm × openbare vakken − laadvakken. De norm is standaard 1 op 10 (uit de beleidsregel, strategische plaatsing) en staat als schuifje in beeld.
  - **Woningen:** CBS-woningen binnen 200 m staan erbij, als indicatie voor de vraag.
  - **Voorstel:** "beste nieuwe laadlocaties" zijn kandidaat-vakken met het grootste tekort, minstens 40 m uit elkaar. Bij gelijk tekort gaan vakken aan het eind van een rij voor ("kiezen bij voorkeur straathoeken").
  - Geen fictieve bezetting.
- **Why:** het formulier wil rekenen op bezetting en verbruik, maar die data hebben we niet. Een getal uit de beleidsregel plus echte tellingen is eerlijker dan een verzonnen bezetting die er echt uitziet.
- **Rejected alternative:** een fictieve bezetting per paal, gelabeld als `fictief`. Die maakt de demo rijker, maar stuurt de ranking op verzonnen getallen. Daarom staat bezetting in de parking lot.

## D-007: 200 m hemelsbreed als benadering van loopafstand
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:** de cirkel en de tellingen gebruiken 200 m hemelsbreed.
- **Why:** de beleidsregel noemt "binnen 200 meter loopafstand". Een echte loopafstand vraagt een voetpadennetwerk, en dat is te veel voor vandaag. Loopafstand is altijd langer dan hemelsbreed, dus de dekking valt iets te gunstig uit.
- **Rejected alternative:** een netwerkanalyse met OSM-voetpaden. Die past niet in het tijdsbudget (parking lot).

## D-008: Adres zoeken via PDOK Locatieserver, met klikken op de kaart als terugval
- **Status:** proposed
- **When / who:** 2026-11-05 13:10 · Claude
- **Decision:** het zoekvak vraagt live de PDOK Locatieserver (open, CORS toegestaan). Valt het adres buiten het demogebied, dan meldt de pagina dat. Zonder internet klik je op de kaart om de cirkel te plaatsen, of kies je een van drie voorbeeldadressen.
- **Why:** "Voert adres in" is de kern van het formulier. De Locatieserver is de standaard-geocoder van de overheid en werkt vanaf `file://`.
- **Rejected alternative:** een lokale adreslijst (BAG) in `data.js`. Dat maakt het bestand veel groter, en het is voor de demo niet nodig.

## D-009: De inrit-toets vervalt; inritten gaan naar "ter plaatse checken"
- **Status:** proposed (vervangt de rij "Inrit" in D-004)
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:** de pagina toetst niet meer op afstand tot een inrit. Inritten staan in elke popup bij "ter plaatse checken", samen met de kabel en de nooddeuren.
- **Why:** de BGT kent in het hele demogebied **één** vlak met functie `inrit`. In Rotterdam zijn in- en uitritten vrijwel altijd gekarteerd als voetpad. Een toets die nooit afgaat, wekt de indruk dat er gecontroleerd is.
- **Rejected alternative:** inritten afleiden uit verlaagde banden of BAG-garageboxen. Dat kan niet in het tijdsbudget en is ook niet te valideren.

## D-010: Overzichtslaag = dekking t.o.v. de norm, niet het absolute tekort
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:** per CBS-vierkant van 100 m: bestaande laadvakken binnen 200 m gedeeld door (openbare vakken binnen 200 m / norm). Er zijn zes klassen, van < 20% tot ≥ norm. Na het kiezen van een adres wordt de laag bijna doorzichtig, zodat de straat zichtbaar blijft.
- **Why:** de mediane dekking in Noord is 3,3% laadvakken tegenover 10% norm. Met het absolute tekort viel bijna alles in de hoogste klasse en was de kaart één kleur. De verhouding laat wél zien waar het tekort het grootst is.
- **Rejected alternative:** klassen op kwantielen. Die verschuiven bij elke andere norm en zijn lastig uit te leggen.

## D-011: Te smalle stoep = maatwerk (uitstulping), niet ongeschikt
- **Status:** proposed (vervangt de rij "Stoepbreedte" in D-004 voor stoepen < 1,7 m)
- **When / who:** 2026-11-05 14:05 · Claude
- **Decision:** een vak met een stoep smaller dan de maatwerkgrens krijgt "maatwerk: alleen met uitstulping (kost 1 vak: 3 vakken → 2 laadvakken)".
- **Why:** de beleidsregel staat uitstulping toe bij onvoldoende ruimte op het trottoir. In Noord viel 35% van de ongeschikte vakken (1.824) alleen af op stoepbreedte. Juist in oude wijken is uitstulping vaak de enige route.
- **Rejected alternative:** ongeschikt laten. Dan schrijft de tool de plekken af waar het team het meest moet zoeken.

## D-012: Greedy ranking zonder dubbeltelling, en een label voor uitbreiding van bestaande locaties
- **Status:** proposed (vervangt de rangschikking in D-006)
- **When / who:** 2026-11-05 14:05 · Claude
- **Decision:**
  - **Rangschikking:** de beste nieuwe laadlocaties worden één voor één gekozen. Na elke keuze tellen de nieuwe laadvakken (1 of 2) mee als aanbod voor de vakken binnen 200 m, en daarna wordt opnieuw gerangschikt.
  - **Uitbreiding:** een paalpunt binnen 25 m van een bestaand laadvak krijgt het label "uitbreiding bestaande locatie". De kabelregel geldt dan als waarschijnlijk vervuld.
- **Why:** in de oude ranking overlapten de 200 m-cirkels van de top 5 voor 70%. Daardoor werd hetzelfde tekort vijf keer geteld. 25% van de kandidaat-paalpunten ligt binnen 25 m van een bestaand laadvak, en de beleidsregel noemt uitbreiding van bestaande laadlocaties als optie.
- **Rejected alternative:** uitbreiding automatisch voorrang geven. Zonder bezettingsdata weten we niet of de bestaande paal vol is (parking lot).
