# Laadlichten: levende kaart van de Rotterdamse verkeerslichten

Team Laadlichten · onderwerp Wegbeheer · Themadag Mobiliteit, 5 november 2026.

**De pitch in één zin:** een kaart van alle verkeerslichten die zelf ziet waar iets mis is en die per kruispunt een eerste schets van een basisregeling geeft.

## Status (demo vanmiddag)

- [x] Open besluiten in [`DECISIONS.md`](DECISIONS.md) bevestigd (D-001 t/m D-006)
- [x] Prep-script: VRI-locaties, ITF-geometrie en intensiteit samenvoegen tot `data.js` (alleen aggregaten, lokaal; zie D-002, D-007)
- [x] Kaart met alle VRI's en een keuze van kleurlaag: signalen, detectie, OV-prioriteit, vervangjaar
- [x] Kruispuntpaneel: kenmerken, dagprofiel per signaalgroep en de ITF-geometrie (rijstroken, lussen, drukknoppen) op de kaart
- [x] Signalenlijst "Aandacht nodig": geen tellingen, mogelijke lusstoring, daling, vervanging ≤ 2027 (zie D-007, D-008)
- [x] *Stretch:* schets van een basisregeling: fasering, groentijdenplan, functionele specificatie en beleidsknoppen (zie D-009)
- [x] "Hoe te demonstreren" (3 stappen). Er komt bewust geen screenshot in de repo, omdat die niet-openbare VRI-data toont (D-002).
- [x] Uitlegpagina `prototype/uitleg.html`: wat is het, hoe is het gemaakt, wat kun je ermee (gevraagd door de eigenaar; vanuit de kaart te openen via "uitleg")

## Zo draai je het

De data is niet openbaar en zit daarom niet in de repo (D-002).

1. Zet de VRI-dataset in `data/` in de root van de repo. Git negeert die map (`/data/` in `.gitignore`).
2. Maak het databestand vanuit de root van de repo: `uv run cases/laadlichten/prototype/prep_laadlichten.py`. Dat duurt ongeveer een minuut en schrijft `prototype/data/private/data.js` (ongeveer 1,4 MB, ook genegeerd door git).
3. Dubbelklik op `cases/laadlichten/prototype/index.html`. Een kruispunt kun je direct openen met `index.html#vri=36020`.

## Brief

Overgenomen uit het ontwerpformulier van het team. Persoonsgegevens zijn weggelaten; het origineel staat lokaal in `_private/`.

**Probleem.** Het programmeren van verkeerslichten is arbeidsintensief: veel handwerk, veel manuren. De basis van een regeling is de geometrie van het kruispunt. Verkeersdata (hoeveel ov, auto's, fietsen) leveren daarbij een regelstructuur voor de doorstroming. Groen aanvragen gaat nu via detectielussen of drukknoppen, en die zijn storingsgevoelig.

**Voor wie.** Ambtenaren, en verkeerskundigen en regelaars in het bijzonder: zij willen sneller tot een regeling komen en storingen eerder zien. Uiteindelijk ook weggebruikers: zij krijgen kruispunten die sneller en logischer werken.

**Wat het team wil.**
- *Doel:* vlottere doorstroming, minder storingen, en een tool die van een functionele specificatie een regeling maakt in een programmeertaal naar keuze.
- *Invoer:* eerst de kruispuntgeometrie, dan verkeersdata, dan mobiliteitsbeleid. Voorbeelden van beleid zijn ov-prioriteit en voorrang voor voetgangers of fietsers bij regen.
- *Wat de tool doet:* snel functionele specificaties opstellen als basis voor een basisregeling.
- *Uitkomst op termijn:* een kaart met alle bestaande verkeerslichten die zelf ziet wat er nodig is om de doorstroming te verbeteren.
- *Vandaag:* een kaart voor ambtenaren die laat zien hoe zo'n levende kaart van de stad werkt. In het formulier staat hier "(Den Haag)"; zie open vraag 1.

## Scope vandaag (hek)

**Wel:**
- Een levende kaart van de echte Rotterdamse VRI's, met kleurlagen, een kruispuntpaneel en automatische signalen. Dit is de kern van het formulier.
- Als er tijd over is (stretch): een schets van een basisregeling. Die bestaat uit een vaste fasering volgens de standaardnummering, een groentijdenplan volgens Webster, knoppen voor ov-prioriteit en regen, en een functionele specificatie in tekst. Hij staat bij elke VRI met genoeg tellende auto-signaalgroepen (D-009). Dit laat de potentie zien van de stap "geometrie + data + beleid → basisregeling".

**Niet:**
- Regelcode die op straat gebruikt kan worden. Ontruimingstijden volgens de CROW-methode rekenen we ook niet.
- Een codeskelet in een programmeertaal naar keuze (gaat naar de parking lot).
- Den Haag-data, een live datakoppeling, ruwe iVRI-logdata (UDAP) of de weerkoppeling (zie de parking lot).
- Basisregelingen voor meer dan één kruispunt.

## Data (lokaal, buiten de repo)

| Bron | Inhoud | Dekking |
|---|---|---|
| VRI-kenmerken (`vri_locaties.gpkg`) | 308 installaties (292 VRI) met 44 kenmerken: vervangjaar, leverancier, iVRI, prioriteit (bus/tram/hulpdiensten), rateltikker, gekoppelde VRI's | peildatum jan 2023 |
| ITF-geometrie (`260520_ITF.gpkg`) | rijstroken (5.749), stopstrepen (3.956), sensoren (2.848 lussen, 859 drukknoppen), regelaars | 181 kruispunten |
| Intensiteit per uur (parquet) | 54,7 mln rijen, per VRI × uur × signaalgroep | 264 VRI's, sep 2024 – sep 2026 |

- Alle drie de bronnen samen dekken **124 VRI's**.
- **Eerste bevinding (sep 2025 tegenover sep 2026, D-007):** 16 VRI's leveren geen tellingen meer. Het zijn allemaal iVRI's, dus waarschijnlijk gaat het om de datalevering. Op 9 VRI's is een deel van de signaalgroepen stil: dat zijn mogelijke lusstoringen. Op 40 VRI's is er een daling van meer dan 50%. Geen van deze signalen is al bevestigd door Wegbeheer.

## Let op

- **Veiligheid.** Het einddoel, regelcode genereren, is veiligheidskritisch. De schets van een basisregeling krijgt in de UI een harde disclaimer: *"schets, geen ontruimingstijden, niet voor gebruik op straat"*. Voor productie is een aparte validatieroute nodig.
- **Datakwaliteit.**
  - De kenmerkentabel is van januari 2023. Vervangjaren 2023–2026 zijn dus misschien al uitgevoerd; we tonen ze als "te verifiëren".
  - Rijstrooknamen in ITF kennen minstens vijf notaties, bijvoorbeeld `02_1`, `03.1`, `08.1 afvoer`, `Statenweg-25` en `ZW_Hoofdweg_1`.
  - Er zit geen laag met rijstrookverbindingen in de ITF-export. De schets gebruikt daarom een vaste fasering volgens de standaardnummering, en geen conflictmatrix (D-009).
- **"Storing" is een signaal, geen diagnose.** Nul tellingen kan een kapotte lus zijn, maar ook dataverlies of een omgebouwd kruispunt. De UI zegt "mogelijke storing".
- **Privacy.** We gebruiken alleen uur-aggregaten per signaalgroep. Ruwe iVRI-logdata is deels herleidbaar tot personen, en iVRI's staan in het algoritmeregister.
- **Publieke repo.** De VRI-data is geen open data. Daarom komt er geen `data.js` in git (D-002). Het prototype draait vanmiddag op de laptop met de lokale data.

## Hoe te demonstreren

1. Open de kaart (kleurlaag **Signalen**). Rood betekent dat een deel van de detectie in sep 2026 niets meer telde, terwijl er in sep 2025 wel verkeer was. Oranje betekent dat de hele VRI geen tellingen meer levert.
2. Klik in "Aandacht nodig" op **Gordelweg - Soetendaalsebrug**. Je ziet welke signaalgroep stil is (sg 84), het dagprofiel van vorig jaar naast dat van nu, en de 54 lussen en 23 drukknoppen op het kruispunt. Laat ook **Schepenstraat - Schieweg** zien: daar waarschuwt de kaart zelf dat de signaalgroepen misschien hernummerd zijn.
3. Open **Mathenesserbrug - Mathenesserplein** (`index.html#vri=22030`) en scroll naar de **Basisregeling-schets**. Het groentijdenplan is berekend uit de rijstroken (ITF) en het drukste werkdaguur. Zet ov-prioriteit aan: F1 krijgt 10 s extra, en de cyclus gaat van 68 naar 78 s. Zet daarna regen aan: er komt een fietsfase bij. Wijs op de disclaimer: dit is een startpunt, geen regeling.

## Parking lot

- Een codeskelet van de regeling in een programmeertaal naar keuze, zoals het team vraagt (CCOL/C, Python, …), door Claude gegenereerd uit de functionele specificatie.
- Een conflictmatrix en ontruimingstijden (CROW) uit echte rijstrookverbindingen, zodra die in de ITF-export zitten. Daarmee wordt de schets een echte eerste versie van een regeling.
- Een levende kaart voor Den Haag.
- Een weerkoppeling (KNMI) voor "fiets voor bij regen".
- Ov-prioriteit: kansen vinden door GTFS-routes over kruispunten zonder prioriteit te leggen.
- Storingssignalen automatisch doorzetten naar beheerder of aannemer, met een maandelijkse trend.
- Een koppeling met de casus Contractmanagement: vervangjaar en garantie van VRI's naast de onderhoudscontracten.
- Per kruispunt een advies van Claude: "wat is hier nodig voor een betere doorstroming?"

## Open vragen voor het team (vanmiddag)

1. In stap 5 staat "(Den Haag)". Gaat het om de levende kaart van Den Haag als voorbeeld, of willen jullie Den Haag ook op de kaart?
2. Herkennen jullie de 9 kruispunten met mogelijke lusstoring en de 16 iVRI's zonder tellingen? Is dit lusuitval, dataverlies of iets anders?
3. In welke taal of welk formaat werken regelaars nu: CCOL, TLC-FI, iets anders? Dit bepaalt het codeskelet in de parking lot.
4. Wat moet een schets van een basisregeling minimaal bevatten om voor jullie een bruikbaar startpunt te zijn?
5. Wie is de eigenaar van de VRI-data, en mogen locaties en uur-aggregaten openbaar? Dit bepaalt of het prototype online kan (D-002).
