# Laadlichten: levende kaart van de Rotterdamse verkeerslichten

Team Laadlichten · onderwerp Wegbeheer · Themadag Mobiliteit, 5 november 2026.

**De pitch in één zin:** een kaart van alle verkeerslichten die zelf ziet waar iets mis is en die per kruispunt een eerste schets van een basisregeling geeft.

## Status (demo vanmiddag)

- [ ] Open besluiten in [`DECISIONS.md`](DECISIONS.md) bevestigd (D-001 t/m D-006)
- [ ] Prep-script: VRI-locaties, ITF-geometrie en intensiteit samenvoegen tot `data.js` (alleen aggregaten, lokaal; zie D-002)
- [ ] Kaart met alle VRI's en een keuze van kleurlaag: storing, detectie, OV-prioriteit, vervangjaar
- [ ] Kruispuntpaneel: kenmerken, dagprofiel per signaalgroep en de ITF-geometrie (rijstroken, stopstrepen, lussen) op de kaart
- [ ] Signalenlijst "Aandacht nodig": lusuitval, trendbreuk, vervanging ≤ 2027 (zie D-003)
- [ ] *Stretch:* schets van een basisregeling voor 1 kruispunt: conflictmatrix, groentijdenplan, functionele specificatie (zie D-005)
- [ ] "Hoe te demonstreren" (3 stappen) en een screenshot

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
- Als er tijd over is (stretch): een basisregeling voor **één** vooraf gekozen kruispunt. Die bestaat uit een conflictmatrix, een groentijdenplan volgens Webster en een functionele specificatie in tekst. Het prep-script berekent alles vooraf. Dit laat de potentie zien van de stap "geometrie + data + beleid → basisregeling".

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
- **Eerste bevinding:** 87 signaalgroepen op 15 kruispunten telden historisch gemiddeld ≥5 voertuigen per uur, maar in september 2026 nul. Dat zijn kandidaat-storingen, nog niet bevestigd door Wegbeheer. Nog eens 569 signaalgroepen tellen altijd nul; die tellen we niet als storing.

## Let op

- **Veiligheid.** Het einddoel, regelcode genereren, is veiligheidskritisch. De schets van een basisregeling krijgt in de UI een harde disclaimer: *"schets, geen ontruimingstijden, niet voor gebruik op straat"*. Voor productie is een aparte validatieroute nodig.
- **Datakwaliteit.**
  - De kenmerkentabel is van januari 2023. Vervangjaren 2023–2026 zijn dus misschien al uitgevoerd; we tonen ze als "te verifiëren".
  - Rijstrooknamen in ITF kennen minstens vijf notaties, bijvoorbeeld `02_1`, `03.1`, `08.1 afvoer`, `Statenweg-25` en `ZW_Hoofdweg_1`.
  - Er zit geen laag met rijstrookverbindingen in de ITF-export. De conflictmatrix wordt daarom afgeleid (D-004, D-005).
- **"Storing" is een signaal, geen diagnose.** Nul tellingen kan een kapotte lus zijn, maar ook dataverlies of een omgebouwd kruispunt. De UI zegt "mogelijke storing".
- **Privacy.** We gebruiken alleen uur-aggregaten per signaalgroep. Ruwe iVRI-logdata is deels herleidbaar tot personen, en iVRI's staan in het algoritmeregister.
- **Publieke repo.** De VRI-data is geen open data. Daarom komt er geen `data.js` in git (D-002). Het prototype draait vanmiddag op de laptop met de lokale data.

## Hoe te demonstreren (concept, wordt definitief vóór de feature freeze)

1. Open de kaart en kies de kleurlaag **Storing**. De rode kruispunten zijn plekken waar de detectie de afgelopen maand niets meer telde, terwijl daar normaal verkeer rijdt.
2. Klik een rood kruispunt aan. Je ziet welke signaalgroep sinds wanneer stil is, het dagprofiel, en waar de lussen op het kruispunt liggen.
3. *Stretch:* klik op **Basisregeling-schets**. Je ziet de conflictmatrix en het groentijdenplan, berekend uit geometrie en spitsintensiteit. Zet ov-prioriteit aan en kijk hoe de verdeling verschuift.

## Parking lot

- Een codeskelet van de regeling in een programmeertaal naar keuze, zoals het team vraagt (CCOL/C, Python, …), door Claude gegenereerd uit de functionele specificatie.
- Schetsen van basisregelingen voor alle 109 kruispunten met bruikbare ITF-signaalgroepen.
- Een levende kaart voor Den Haag.
- Een weerkoppeling (KNMI) voor "fiets voor bij regen".
- Ov-prioriteit: kansen vinden door GTFS-routes over kruispunten zonder prioriteit te leggen.
- Storingssignalen automatisch doorzetten naar beheerder of aannemer, met een maandelijkse trend.
- Een koppeling met de casus Contractmanagement: vervangjaar en garantie van VRI's naast de onderhoudscontracten.
- Per kruispunt een advies van Claude: "wat is hier nodig voor een betere doorstroming?"

## Open vragen voor het team (vanmiddag)

1. In stap 5 staat "(Den Haag)". Gaat het om de levende kaart van Den Haag als voorbeeld, of willen jullie Den Haag ook op de kaart?
2. Herkennen jullie de 15 kruispunten met mogelijke uitval? Is dit lusuitval, dataverlies of iets anders?
3. In welke taal of welk formaat werken regelaars nu: CCOL, TLC-FI, iets anders? Dit bepaalt het codeskelet in de parking lot.
4. Wat moet een schets van een basisregeling minimaal bevatten om voor jullie een bruikbaar startpunt te zijn?
5. Wie is de eigenaar van de VRI-data, en mogen locaties en uur-aggregaten openbaar? Dit bepaalt of het prototype online kan (D-002).
