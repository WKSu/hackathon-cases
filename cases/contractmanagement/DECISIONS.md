# Besluitenlog: Contractmanagement

Dit log wordt alleen aangevuld. Een oud besluit pas je niet aan: je vervangt het met een nieuwe entry ("superseded by"). Het format staat in [`/CLAUDE.md`](../../CLAUDE.md).

## D-001: Stack: een bouwscript dat één statische `index.html` maakt
- **Status:** proposed
- **When / who:** 2026-11-05 13:00 · Claude
- **Decision:**
  - `prototype/bouw_dashboard.py` (PEP 723, `uv run`) leest een Excel-export en schrijft één `index.html`.
  - De data staat inline in de pagina.
  - De signalen worden in de browser berekend (vanilla JavaScript, geen externe bibliotheken), zodat normen en peildatum live aan te passen zijn.
  - `dashboard_template.html` is de bron van de pagina.
- **Why:** de pagina opent met een dubbelklik, zonder server, `fetch` of CDN. Dat werkt ook op een afgeschermd gemeentenetwerk. Elke maand een nieuwe export erin, en er is een nieuw dashboard.
- **Rejected alternative:** een marimo- of Power BI-dashboard. Dat heeft een draaiende kernel of licenties nodig, en is lastiger om vanmiddag te delen.

## D-002: Synthetische data in de 15 kolommen van de export, personen op rolniveau
- **Status:** proposed
- **When / who:** 2026-11-05 13:00 · Claude
- **Decision:**
  - `prototype/genereer_dummydata.py` maakt 241 fictieve contracten (434 regels met versies) in exact de 15 kolommen van de contractexport. Het script gebruikt SEED 42.
  - Personen heten "Contractmanager A", "Contracteigenaar B" enzovoort.
  - Leveranciers dragen "(fictief)". De kolom Cluster bevat mobiliteitsthema's.
  - Er zitten bewust gaten in: ontbrekende rollen, verlopen maar actief, waardestijgingen, lange raamovereenkomsten, ontbrekende bedragen en einddatums.
  - Het Excel-bestand gaat naar `data/private/` en blijft buiten git. De `index.html` met de synthetische data staat wel in git.
- **Why:** de repo is publiek. Van de echte export zijn alleen de kolomkoppen gebruikt. De waarden lijken bewust niet op de echte verdeling. Met rolnamen zie je wel hoe werkverdeling en vertrek werken, zonder iets te zeggen over echte mensen.
- **Rejected alternative:** realistische namen verzinnen. Die kunnen per toeval op echte collega's lijken, en dan staat er "boven de norm" naast hun naam.

## D-003: Elk signaal wordt een actie met wat, wie, uiterlijk en status
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:**
  - Elke regel levert een actie op: een werkwoord ("Start de (her)aanbesteding"), de reden, een eigenaar per rol en een uiterste datum.
  - Een actie heeft de status Open, Opgepakt of Klaar, en kan aan iemand anders worden toegewezen.
  - Eigenaar per soort actie:
    - Tijd: de contractmanager.
    - Besluit over verlenging en rollen toewijzen: de contracteigenaar.
    - Status en data bijwerken: de contractbeheerder.
    - Ontbreekt de eigenaar, dan ligt de actie bij het MT.
  - De werklijst (tab Acties) groepeert op Te laat, Deze maand, Komende 3 maanden en Later.
- **Why:** het team wil zien "wat er van mij verwacht wordt of wanneer actie nodig is", en een taak aan iemand kunnen toewijzen. Een signaal zonder eigenaar en termijn leidt niet tot actie.
- **Rejected alternative:** alleen stoplichten per contract. Die zeggen niet wie wat moet doen, en blijven elke maand rood, ook als iemand er al mee bezig is.

## D-004: Afloopsignaal: uiterste start = einddatum min doorlooptijd van de procedure
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:**
  - De horizon blijft 18 maanden, de afspraak van het team.
  - De uiterste start van de (her)aanbesteding is de einddatum min de doorlooptijd: ± 18 maanden als het contractbedrag op of boven de Europese drempel ligt, en ± 6 maanden eronder.
  - De drempel staat op € 216.000 (leveringen en diensten, decentrale overheden, 2026–2027). In de UI staat "check pianoo.nl".
  - De datum is voorbij: rood. Nog binnen 3 maanden: geel. Daarna: info.
  - Alle waarden zijn instelbaar onder Normen.
- **Why:** met één termijn van 18 maanden voor alles staat een inhuurcontract van € 30k even rood als een Europese aanbesteding van miljoenen. Dat maakt de lijst te lang om op te sturen.
- **Rejected alternative:** de procedure uit Contracttype afleiden. Dat veld zegt niet of het Europees is, en ook niet of het om werken of diensten gaat.

## D-005: "Plan bij afloop" als handmatige aanvulling (vervangt de ontbrekende kolom Verlengingsoptie)
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:** per contract kies je één van zes opties:
  - Nog niets vastgelegd
  - Verlengingsoptie aanwezig (actie: besluit, uiterlijk 3 maanden voor het einde)
  - Geen optie, nog geen plan
  - Besloten: verlengen
  - (Her)aanbesteding loopt
  - Besloten: laten aflopen

  Bij een vastgelegd plan wordt het tijdsignaal "info" of een vervolgactie, zoals "leg de verlenging vast".
- **Why:** het team wil onderscheid tussen aflopen met en zonder verlengingsoptie, maar die kolom staat niet in de export. Eén veld voor feit én plan houdt het simpel, en maakt zichtbaar dat een rood signaal verdwijnt zodra er een plan is.
- **Rejected alternative:** twee aparte velden (verlengingsoptie en plan). Dat is meer invulwerk voor hetzelfde inzicht.

## D-006: Stoplichten: per contract de zwaarste open actie, per tegel een aandeel
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:**
  - Een contract kleurt naar zijn zwaarste open actie: rood, geel of anders groen.
  - Een tegel in het overzicht (tijd, geld, kwaliteit, rollen) is rood als ≥ 20% van de contracten in die categorie rood is, geel bij een signaal, en anders groen.
  - Tijd is ook rood bij één verlopen contract.
  - Kwaliteit toont "Geen data" zolang niets is beoordeeld.
- **Why:** met "de zwaarste wint" op afdelingsniveau staat alles altijd op rood. Het aandeel is instelbaar, zodat het team zelf bepaalt hoe streng het overzicht is.
- **Rejected alternative:** een gewogen score per contract (bijvoorbeeld bedrag × urgentie). Die is moeilijker uit te leggen aan de zaal.

## D-007: Wettoets als signaal, niet als oordeel
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:** drie regels, elk met een link naar wetten.overheid.nl:
  - Een raamovereenkomst langer dan 4 jaar: leg de motivering vast (Aanbestedingswet 2012, art. 2.140).
  - Een waardestijging van meer dan 10% t.o.v. versie 1: toets de wijziging (art. 2.163a–g; de-minimisgrens 10% voor leveringen/diensten, 15% voor werken).
  - Kwaliteit "onvoldoende": spreek de leverancier aan, en kijk bij aanhoudend tekortschieten naar ingebrekestelling (BW boek 6).
- **Why:** het team vroeg om een koppeling met de Aanbestedingswet en het BW. Met alleen de exportkolommen kunnen we niet meer dan dit betrouwbaar signaleren. In de UI staat: "check bij Inkoop of Juridische Zaken".
- **Rejected alternative:** een AI-samenvatting van de wet per contract. Zonder contractclausules en procedure wordt dat schijnzekerheid.

## D-008: Werkverdeling en capaciteit tegen een instelbare norm
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:**
  - De norm is 20 actieve contracten per contractmanager en 30 per contractbeheerder.
  - Nodig = actieve contracten ÷ norm, naar boven afgerond. Dit wordt vergeleken met het aantal mensen dat niet vertrekt: tekort, of genoeg mensen maar scheef verdeeld.
  - "Vertrekt" vink je per persoon aan; dat geeft een overdrachtsactie bij de eigenaar.
  - Een rolwissel tussen twee contractversies wordt gesignaleerd ("is de overdracht rond?").
- **Why:** het team noemde personeelstekorten, personele wisselingen en "ruimte voor wat je ideaal zou willen". Eén getal per rol is genoeg voor een MT-gesprek over FTE.
- **Rejected alternative:** een norm op contractwaarde of complexiteit. Daar is geen data voor, en dat is lastig uit te leggen.

## D-009: Kwaliteit voorlopig met de hand
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:** per contract vul je een oordeel in (goed, vraagt aandacht, onvoldoende) en de datum van het laatste voortgangsgesprek. Laatste gesprek langer dan 3 maanden geleden: actie "plan het voortgangsgesprek".
- **Why:** "realisatie van de afspraken" en de kwartaalgesprekken zijn een kernvraag, maar KPI-scores staan niet in de export. Zo is zichtbaar hoe het stoplicht Kwaliteit straks werkt.
- **Rejected alternative:** de tegel weglaten tot er data is. Dan verdwijnt kwaliteit uit beeld, terwijl het team dat juist wil sturen.

## D-010: Aanvullingen alleen in de browser (localStorage)
- **Status:** proposed
- **When / who:** 2026-11-05 13:30 · Claude
- **Decision:** plan bij afloop, actiestatus, toewijzingen, kwaliteitsoordelen, vertrek en normen staan in localStorage van de browser. In de header staat hoeveel aanvullingen er zijn. Onder Uitleg kun je alles wissen.
- **Why:** geen server en geen inlog binnen 90 minuten. Het laat het werkproces zien.
- **Rejected alternative:** opslag in een gedeeld bestand of in SharePoint. Dat is de echte oplossing (parking lot), maar niet vandaag te bouwen.

## D-011: Lagen: eerst eenvoudig, details op aanvraag; licht thema
- **Status:** proposed
- **When / who:** 2026-11-05 13:15 · Claude (op verzoek van de eigenaar)
- **Decision:** de lagen zijn:
  1. Eén zin, vier stoplichten en de drie urgentste acties.
  2. Klik op een stoplicht voor details. Het tijdpaneel toont een grafiek per maand en het vertrekbord; de volledige samenvatting staat ingeklapt.
  3. Tabs met lijsten en het contractdetail; ook daar zijn "meer"-delen ingeklapt.

  De pagina gebruikt altijd het lichte thema.
- **Why:** de eerste versie gaf alles in één keer en was overweldigend. Het formulier vraagt om "duidelijk en kort", met "verschillende lagen van detail".
- **Rejected alternative:** aparte pagina's per rol. Dat is meer onderhoud, en je ziet minder goed hoe de rollen samenhangen.

## D-012: Demoknop met voorbeeld-aanvullingen
- **Status:** proposed
- **When / who:** 2026-11-05 13:45 · Claude
- **Decision:** "Demo: simuleer een maand gebruik" (of `#demo`) vult een deterministische set plannen, statussen en kwaliteitsoordelen in. Dat gebeurt alleen bij dummydata. Met "Wis alle aanvullingen" ga je terug naar de rauwe export.
- **Why:** een verse export weet niets van plannen, dus staat bijna alles op rood. Met de knop ziet de zaal het verschil tussen "wat de export weet" en "wat het team aanvult".
- **Rejected alternative:** de voorbeeld-aanvullingen al in de data zetten. Dan lijkt het of de export die informatie bevat.

## D-013: Online op de themadag-site (GitHub Pages)
- **Status:** accepted (eigenaar: "I want it to be hosted on github pages")
- **When / who:** 2026-11-05 14:00 · Claude
- **Decision:**
  - Dezelfde build staat op https://wksu.github.io/hackathon/prototypes/contractmanagement/, in de site-repo `WKSu/hackathon`.
  - Op de resultatenpagina staat een kaart met een screenshot, en de Teams-pagina linkt naar het dashboard.
  - `bouw_dashboard.py --terug ../../resultaten.html` zet een link terug naar de resultaten in de kop.
  - De pagina heeft `noindex, nofollow`, net als de rest van de site.
- **Why:** alle data is synthetisch (D-002), dus het dashboard mag openbaar. De themadag-site is al de plek waar de prototypes staan. Eén bouwscript maakt de lokale en de online versie.
- **Rejected alternative:** GitHub Pages aanzetten op `hackathon-cases`. Dan staat de hele repo als site online, en komen de cases op twee plekken te staan.
- **Let op:** aanvullingen (plan, status, oordeel) bewaart de browser per site. Iedereen die de online versie gebruikt, ziet alleen zijn eigen aanvullingen (D-010).
