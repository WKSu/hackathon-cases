# Laadpalen: waar is ruimte voor een nieuwe laadpaal?

Team Laadlichten · onderwerp Wegbeheer · Themadag Mobiliteit, 5 november 2026. Dit is het tweede formulier van het team. Het eerste gaat over verkeerslichten (VRI) en staat in [`cases/laadlichten`](../laadlichten).

**De pitch in één zin:** typ een adres in, en je ziet binnen 200 meter welke parkeervakken volgens het Rotterdamse plaatsingsbeleid geschikt zijn voor een nieuwe laadpaal, en waar die het hardst nodig is.

## Status (demo vanmiddag)

- [ ] Open besluiten in [`DECISIONS.md`](DECISIONS.md) bevestigd (D-001 t/m D-008)
- [ ] Prep-script: parkeervakken, bestaande laadvakken, bomen, BGT (stoep, fietspad, groen, inrit) en CBS-woningen samenvoegen tot `data.js` (lokaal; zie D-002)
- [ ] Kaart met adres zoeken en een cirkel van 200 m, met een omgevingspaneel: vakken, laadvakken, bomen, groen, stoepbreedte en woningen
- [ ] Toets per parkeervak aan de beleidsregel: kleur geschikt / maatwerk / ongeschikt, met de reden per criterium (D-004, D-005)
- [ ] Schuifjes voor de drempels (stoepbreedte, boomafstand, norm laadpunten), met de cijfers die direct meerekenen
- [ ] Voorstel "beste nieuwe laadlocaties" binnen de cirkel, gerangschikt op tekort aan laadpunten (D-006)
- [ ] Overzichtslaag voor het hele demogebied: bestaande laadvakken en het tekort per 100 m-vak
- [ ] "Hoe te demonstreren" (3 stappen) en een screenshot

## Brief

Overgenomen uit het ontwerpformulier van het team. Persoonsgegevens zijn weggelaten; het origineel staat lokaal in `_private/`.

**Probleem.** Vooral in oudere wijken is het zoeken naar geschikte plekken voor laadpalen. De stoep is te smal, er is te weinig parkeerruimte, je plaatst niet in het groen en niet voor een inrit of nooddeur. Bewoners weten niet altijd welke laadpalen vrij zijn, en rijden rondjes op zoek naar een vrije paal.

**Voor wie.** Ambtenaren, die met een kaart sneller zien welke locaties geschikt of ongeschikt zijn. Bewoners, die minder last hebben van laadpalen in de openbare ruimte en een duidelijker overzicht krijgen.

**Wat het team wil.**
- *Doel:* overzicht van wat waar ligt in de openbare ruimte (groen, parkeerplaatsen, nooddeuren) en hoe breed stoepen en parkeervakken zijn.
- *Invoer:* een adres. Daarna direct een overzicht van de omgeving (200 m): groen, parkeerruimte, bestaande laadpalen en het aantal adressen dat elektrisch rijdt. Filteren op parkeerdruk, stoepbreedte en meer. Het Rotterdamse plaatsingskader geldt als toetskader.
- *Wat de tool doet:* berekenen waar ruimte is in het laadnetwerk, en waar bewoners binnen 200 m het best kunnen laden, op basis van bezetting en verbruik.
- *Uitkomst:* een kaart met alle bestaande laadpalen en de mogelijkheden voor nieuwe laadplekken.
- *Vandaag:* een kaart voor ambtenaren: welke locaties zijn geschikt voor nieuwe laadpalen?

## Scope vandaag (hek)

**Wel:**
- Eén demogebied: de zes vooroorlogse buurten van Noord (D-003). Het script werkt voor elke lijst buurten.
- Adres zoeken, een cirkel van 200 m en een omgevingspaneel met echte tellingen.
- Een toets per parkeervak aan de *Beleidsregel plaatsing laadpunten in de openbare ruimte gemeente Rotterdam 2025* (Gemeenteblad 2025, 307736). Per vak zie je welke criteria het haalt en welke niet.
- Een voorstel van nieuwe laadlocaties, gerangschikt op het tekort aan laadpunten binnen 200 m.

**Niet:**
- Bezetting en verbruik van bestaande laadpalen: daarvoor is laaddata van de concessiehouder nodig (parking lot).
- Een bewonersversie ("waar is nu een paal vrij?"): dat is een ander product (parking lot).
- Laagspanningskabels (eis: binnen 25 m) en nooddeuren: die staan niet in de data. De UI zegt bij elk vak "ter plaatse checken".
- Echte loopafstand over het netwerk: we rekenen hemelsbreed (D-007).
- De hele stad.

## Data (lokaal, buiten de repo)

| Bron | Inhoud | Open? |
|---|---|---|
| Parkeervakken (gemeente) | één polygoon per vak, type langs/dwars/schuin | nog na te gaan, dus lokaal |
| Bijzondere vakken (gemeente) | overlay met o.a. *Elektrische oplaadpunten* (bestaande laadvakken), gehandicapten, laden/lossen, deelauto, blauwe zone, eigen terrein | nog na te gaan, dus lokaal |
| Bomen (gemeente) | stamlocatie, hoogteklasse, kroondiameter | nog na te gaan, dus lokaal |
| BGT (PDOK) | wegdelen: voetpad, fietspad, parkeervlak, inrit, rijbaan; begroeid terrein | open (CC0) |
| CBS 100 m-vierkanten 2024 | woningen en inwoners per vierkant | open |

## Let op

- **Een kaart is geen besluit.** Elke locatie krijgt nog een verkeerskundige toets en een verkeersbesluit met 6 weken bezwaartermijn. De UI zegt "kandidaat", niet "geschikt bevonden".
- **Datakwaliteit.** De gemeentelijke parkeervakken en de BGT zijn apart ingemeten, en liggen tot tientallen centimeters naast elkaar. De stoepbreedte is daarom een schatting (D-005).
- **Aannames zijn zichtbaar.** Waar de beleidsregel geen getal noemt ("geen grote bomen nabij"), kiezen wij een drempel. Die staat als schuifje in beeld en in D-004.
- **Privacy.** Het formulier vraagt om "het aantal adressen dat elektrisch rijdt". Kentekens per adres zijn persoonsgegevens. We tonen daarom woningen per 100 m-vak (CBS) en een aanname voor het aandeel EV's.
- **Publieke repo.** De gemeentelijke lagen zijn niet bevestigd als open data. Daarom komt er geen `data.js` in git (D-002).

## Hoe te demonstreren (concept, wordt definitief vóór de feature freeze)

1. Typ een adres in Noord (bijvoorbeeld *Zwaanshals*). De kaart zoomt in en tekent een cirkel van 200 m. Links zie je wat er in de buurt ligt, zoals parkeervakken, laadvakken, bomen en stoepbreedte.
2. Elk parkeervak kleurt groen (kandidaat), oranje (maatwerk) of grijs (ongeschikt). Klik een vak aan om per regel uit de beleidsregel te zien waarom.
3. Kijk naar **Beste nieuwe laadlocaties**: de plekken met het grootste tekort aan laadpunten. Schuif de stoepbreedte van 2,0 naar 1,7 m (de uitzondering van 90 cm doorgang) en zie hoeveel plekken erbij komen.

## Parking lot

- Echte bezetting en verbruik per laadpaal via de concessiehouder of het G4-portaal (EVData), om "ruimte in het laadnetwerk" op gebruik te baseren in plaats van op aantallen.
- Een bewonersversie: welke paal is nu vrij binnen 200 m?
- Laagspanningskabels van de netbeheerder (Stedin) toevoegen voor de eis "binnen 25 m".
- Echte loopafstand over het voetpadennetwerk in plaats van hemelsbreed.
- De hele stad doorrekenen, ook de geplande herinrichtingen binnen 2 jaar.
- Parkeerdruk uit parkeerdrukmetingen in plaats van de indicatie "woningen per vak".
- Een export van de kandidaten als lijst voor de verkeerskundige toets.

## Open vragen voor het team (vanmiddag)

1. Klopt de toets? Wat ontbreekt er in de criteria, en welke drempel gebruiken jullie in de praktijk voor "grote boom nabij"?
2. Zijn de gemeentelijke lagen (parkeervakken, bijzondere vakken, bomen) open data? Dan kan het prototype online (D-002).
3. Wie heeft de bezettingsdata van de laadpalen, en mogen we die gebruiken?
4. Is "1 laadpunt op 10 openbare parkeervakken" een bruikbare norm voor bestaande wijken, of geldt die alleen voor nieuwe gebieden?
5. Moet het prototype vooral helpen bij het beoordelen van aanvragen, of bij het zelf zoeken naar nieuwe locaties (datagestuurd)?
