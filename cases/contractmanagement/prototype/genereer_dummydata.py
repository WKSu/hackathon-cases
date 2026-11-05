# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "numpy",
#     "pandas",
#     "openpyxl",
# ]
# ///
"""Genereer fictieve contractdata met dezelfde 15 kolommen als de contractexport.

Alle personen (op rolniveau), leveranciers, bedragen en nummers zijn verzonnen. Er zitten bewust
aandachtspunten in (ontbrekende rollen, verlopen-maar-actief, waardestijgingen,
lange raamovereenkomsten, ...) zodat het dashboard iets te signaleren heeft.

Gebruik:
    uv run genereer_dummydata.py
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
np.random.seed(SEED)
RNG = np.random.default_rng(SEED)

HIER = Path(__file__).parent
UITVOER = (
    HIER
    / "data"
    / "private"
    / f"{date.today():%y%m%d} SO-MOB dummydata contractrapport.xlsx"
)

PEILDATUM = pd.Timestamp("2026-11-05")
N_CONTRACTEN = 240

KOLOMMEN = [
    "Contractnummer",
    "Contractnaam",
    "Contractomschrijving",
    "Leverancier",
    "Bedrag",
    "Startdatum",
    "Einddatum",
    "Contractbeheerder",
    "Contractmanager",
    "Contracteigenaar",
    "Contractstatus",
    "Contracttype",
    "Versie",
    "Contractversiestatus",
    "Cluster",
]

# Fictieve personen, op rolniveau: geen namen (de repo is publiek).
EIGENAREN = [f"Contracteigenaar {c}" for c in "ABCDEFG"]
MANAGERS = [f"Contractmanager {c}" for c in "ABCDEFGHIJK"]
BEHEERDERS = [f"Contractbeheerder {c}" for c in "ABCDEFG"]

GEBIEDEN = [
    "Noord",
    "Zuid",
    "Centrum",
    "Oost",
    "West",
    "Kralingen",
    "Charlois",
    "IJsselmonde",
    "Hillegersberg",
    "Delfshaven",
]

CONTRACTTYPES = ["Overeenkomst", "Raamovereenkomst", "Nadere overeenkomst"]

# Thema (in de kolom Cluster) -> sjablonen, fictieve leveranciers, bedragrange,
# vaste contracteigenaar (index in EIGENAREN) en gewicht.
THEMAS: dict[str, dict] = {
    "Verkeersmanagement & VRI": {
        "items": [
            ("Onderhoud VRI's {g}", "Onderhoud en storingsherstel verkeerslichten {g}"),
            ("Beheer verkeerscentrale", "Beheer en doorontwikkeling verkeerscentrale"),
            (
                "Detectie en drukknoppen {g}",
                "Levering detectielussen en drukknoppen {g}",
            ),
            ("Onderhoud DRIP's", "Onderhoud dynamische route-informatiepanelen"),
        ],
        "leveranciers": [
            "Signaalhuis Verkeerstechniek (fictief)",
            "Groengolf Systems (fictief)",
            "Kruispuntkompas (fictief)",
        ],
        "bedrag": (60_000, 4_000_000),
        "eigenaar": 0,
        "gewicht": 0.16,
    },
    "Openbaar vervoer": {
        "items": [
            ("Onderhoud bushaltes {g}", "Onderhoud abri's en perrons bushaltes {g}"),
            ("Toegankelijke haltes {g}", "Toegankelijk maken tram- en bushaltes {g}"),
            ("Reisinformatiepanelen", "Levering en beheer reisinformatiepanelen"),
            ("Pendelbus evenementen", "Inzet pendelbussen bij evenementen"),
        ],
        "leveranciers": ["Haltebouw Rijnstad (fictief)", "Panelo Reisinfo (fictief)"],
        "bedrag": (40_000, 2_500_000),
        "eigenaar": 1,
        "gewicht": 0.11,
    },
    "Parkeren": {
        "items": [
            ("Beheer parkeergarage {g}", "Exploitatie en beheer parkeergarage {g}"),
            (
                "Onderhoud parkeerautomaten",
                "Onderhoud en storingsdienst parkeerautomaten",
            ),
            ("Scanauto's handhaving", "Huur en onderhoud scanauto's parkeerhandhaving"),
            ("Parkeerapp-dienstverlening", "Dienstverlening mobiel parkeren"),
        ],
        "leveranciers": [
            "Garagewacht (fictief)",
            "Meterpunt Services (fictief)",
            "ScanStraat (fictief)",
        ],
        "bedrag": (50_000, 3_000_000),
        "eigenaar": 2,
        "gewicht": 0.13,
    },
    "Fiets & voetganger": {
        "items": [
            ("Fietsenstallingen {g}", "Beheer bewaakte fietsenstallingen {g}"),
            ("Weesfietsen", "Ophalen, opslaan en afvoeren weesfietsen"),
            ("Fietstelpunten", "Levering en beheer fietstelpunten"),
            ("Fietspad {g}", "Aanleg en herinrichting fietspad {g}"),
        ],
        "leveranciers": [
            "Stallingsgilde (fictief)",
            "Trapkracht Diensten (fictief)",
            "Telwerk Mobiliteitsdata (fictief)",
        ],
        "bedrag": (25_000, 1_800_000),
        "eigenaar": 3,
        "gewicht": 0.12,
    },
    "Vervoer over water": {
        "items": [
            ("Veerdienst {g}", "Exploitatie veerdienst {g}"),
            ("Pontons en steigers", "Onderhoud pontons en aanlegsteigers"),
            ("Waterbushalte {g}", "Aanleg en onderhoud waterbushalte {g}"),
        ],
        "leveranciers": [
            "Golfslag Vervoer (fictief)",
            "Steigerwerk Maasoever (fictief)",
        ],
        "bedrag": (80_000, 6_000_000),
        "eigenaar": 4,
        "gewicht": 0.08,
    },
    "Infra & onderhoud": {
        "items": [
            ("Kademuur {g}", "Groot onderhoud kademuur {g}"),
            ("Asfaltonderhoud {g}", "Asfaltonderhoud hoofdwegen {g}"),
            ("Vervanging brug {g}", "Vervanging beweegbare brug {g}"),
            ("GWW-onderhoud {g}", "Klein onderhoud grond-, weg- en waterbouw {g}"),
        ],
        "leveranciers": [
            "Kademaker Infra (fictief)",
            "Asfaltakker Wegenbouw (fictief)",
            "Paalwerk & Co (fictief)",
            "Brugwachters Bouw (fictief)",
        ],
        "bedrag": (150_000, 25_000_000),
        "eigenaar": 5,
        "gewicht": 0.16,
    },
    "Smart mobility & data": {
        "items": [
            ("Verkeersdataplatform", "Licentie en beheer verkeersdataplatform"),
            ("Verkeersmodel licenties", "Licenties en ondersteuning verkeersmodel"),
            ("Pilot deelmobiliteit {g}", "Pilot deelmobiliteitshubs {g}"),
            ("Laadpalen {g}", "Plaatsing en beheer publieke laadpalen {g}"),
        ],
        "leveranciers": [
            "Datadijk Analytics (fictief)",
            "Laadlokaal (fictief)",
            "Modelwerf (fictief)",
        ],
        "bedrag": (30_000, 2_000_000),
        "eigenaar": 6,
        "gewicht": 0.12,
    },
    "Inhuur & advies": {
        "items": [
            ("Inhuur projectleider {g}", "Inhuur projectleider herinrichting {g}"),
            ("Inhuur verkeerskundige", "Inhuur verkeerskundige capaciteit"),
            ("Advies verkeersveiligheid", "Advies verkeersveiligheid schoolomgevingen"),
            ("Communicatieadvies {g}", "Communicatieadvies werkzaamheden {g}"),
        ],
        "leveranciers": [
            "Wegwijzer Detachering (fictief)",
            "Adviesbureau Kruisraam (fictief)",
            "Planbord Interim (fictief)",
        ],
        "bedrag": (15_000, 250_000),
        "eigenaar": 0,
        "gewicht": 0.12,
    },
}


def kies(opties: list, p: np.ndarray | list | None = None):
    return opties[RNG.choice(len(opties), p=p)]


def loguniform(lo: float, hi: float) -> float:
    return float(np.exp(RNG.uniform(np.log(lo), np.log(hi))))


def manager_gewichten() -> np.ndarray:
    # Scheve verdeling: een paar contractmanagers hebben veel meer contracten.
    w = 1 / (np.arange(len(MANAGERS)) + 1) ** 0.5
    return w / w.sum()


def basiscontract(i: int) -> dict:
    themas = list(THEMAS)
    gewichten = np.array([THEMAS[t]["gewicht"] for t in themas])
    thema = kies(themas, gewichten / gewichten.sum())
    spec = THEMAS[thema]
    naam_t, oms_t = kies(spec["items"])
    gebied = kies(GEBIEDEN)

    ctype = kies(CONTRACTTYPES, [0.55, 0.25, 0.20])
    if ctype == "Raamovereenkomst":
        looptijd = kies([24, 36, 48, 60, 72], [0.20, 0.30, 0.40, 0.07, 0.03])
    else:
        looptijd = kies([12, 24, 36, 48, 60, 96], [0.08, 0.20, 0.30, 0.22, 0.12, 0.08])

    # Start zo gekozen dat ~60% nog loopt op de peildatum.
    maanden_geleden = int(RNG.integers(1, looptijd + 24))
    start = (PEILDATUM - pd.DateOffset(months=maanden_geleden)).replace(day=1)
    eind = start + pd.DateOffset(months=looptijd) - pd.Timedelta(days=1)

    lo, hi = spec["bedrag"]
    bedrag = round(loguniform(lo, hi), -2)

    eigenaar = EIGENAREN[spec["eigenaar"]] if RNG.random() < 0.8 else kies(EIGENAREN)
    return {
        "Contractnummer": f"CM-{start.year % 100:02d}-{i + 1:04d}",
        "Contractnaam": (
            naam_t.format(g=gebied) if "{g}" in naam_t else f"{naam_t} perceel {gebied}"
        ),
        "Contractomschrijving": oms_t.format(g=gebied),
        "Leverancier": kies(spec["leveranciers"]),
        "Bedrag": bedrag,
        "Startdatum": start,
        "Einddatum": eind,
        "Contractbeheerder": kies(BEHEERDERS),
        "Contractmanager": kies(MANAGERS, manager_gewichten()),
        "Contracteigenaar": eigenaar,
        "Contracttype": ctype,
        "Cluster": thema,
    }


def maak_versies(basis: dict) -> list[dict]:
    """Maak 1-4 versies; latere versies wijzigen soms bedrag, rollen of einddatum."""
    n = kies([1, 2, 3, 4], [0.5, 0.3, 0.15, 0.05])
    versies = [dict(basis, Versie=1)]
    for v in range(2, n + 1):
        nieuw = dict(versies[-1], Versie=v)
        if RNG.random() < 0.25 and pd.notna(nieuw["Bedrag"]):
            nieuw["Bedrag"] = round(nieuw["Bedrag"] * (1 + RNG.uniform(0.02, 0.18)), -2)
        if RNG.random() < 0.25 and nieuw["Contractmanager"]:
            nieuw["Contractmanager"] = kies(MANAGERS)
        if RNG.random() < 0.12 and nieuw["Contractbeheerder"]:
            nieuw["Contractbeheerder"] = kies(BEHEERDERS)
        if RNG.random() < 0.25 and pd.notna(nieuw["Einddatum"]):
            nieuw["Einddatum"] = nieuw["Einddatum"] + pd.DateOffset(months=12)
        versies.append(nieuw)
    return versies


def zet_status(versies: list[dict]) -> list[dict]:
    laatste = versies[-1]
    eind = laatste["Einddatum"]
    actief = pd.isna(eind) or eind >= PEILDATUM
    # ~10% van de recent verlopen contracten staat nog op Actief (datakwaliteit).
    if not actief and eind >= PEILDATUM - pd.DateOffset(months=6):
        actief = RNG.random() < 0.10
    status = "Actief" if actief else "Inactief"
    for v in versies:
        v["Contractstatus"] = status
        v["Contractversiestatus"] = "Vervallen"
    laatste["Contractversiestatus"] = "Actief"
    if actief and RNG.random() < 0.04:
        laatste["Contractversiestatus"] = "Wordt gewijzigd"
    if actief and RNG.random() < 0.05:
        concept = dict(laatste, Versie=laatste["Versie"] + 1)
        concept["Contractversiestatus"] = "Concept"
        versies.append(concept)
    return versies


def voeg_gaten_toe(basis: dict) -> dict:
    """Bewuste datakwaliteitsproblemen op contractniveau."""
    r = RNG.random
    if r() < 0.10:
        basis["Contractmanager"] = None
    if r() < 0.04:
        basis["Contractbeheerder"] = None
    if r() < 0.03:
        basis["Contracteigenaar"] = None
    if basis["Contractmanager"] and r() < 0.03:
        basis["Contractbeheerder"] = basis["Contractmanager"]
    if r() < 0.015:
        basis["Einddatum"] = pd.NaT
    roll = r()
    if roll < 0.02:
        basis["Bedrag"] = np.nan
    elif roll < 0.03:
        basis["Bedrag"] = 0.0
    return basis


def groot_infracontract() -> list[dict]:
    basis = {
        "Contractnummer": "CM-21-9001",
        "Contractnaam": "Integraal onderhoud kademuren en bruggen",
        "Contractomschrijving": "Meerjarig integraal onderhoud kademuren en bruggen",
        "Leverancier": "Kademaker Infra (fictief)",
        "Bedrag": 420_000_000.0,
        "Startdatum": pd.Timestamp("2021-01-01"),
        "Einddatum": pd.Timestamp("2032-12-31"),
        "Contractbeheerder": BEHEERDERS[3],
        "Contractmanager": MANAGERS[4],
        "Contracteigenaar": EIGENAREN[5],
        "Contracttype": "Raamovereenkomst",
        "Cluster": "Infra & onderhoud",
    }
    v2 = dict(basis, Bedrag=455_000_000.0)
    v3 = dict(v2, Contractmanager=MANAGERS[6])
    versies = [dict(basis, Versie=1), dict(v2, Versie=2), dict(v3, Versie=3)]
    return zet_status(versies)


def genereer() -> pd.DataFrame:
    rijen: list[dict] = []
    for i in range(N_CONTRACTEN):
        basis = voeg_gaten_toe(basiscontract(i))
        rijen.extend(zet_status(maak_versies(basis)))
    rijen.extend(groot_infracontract())
    df = (
        pd.DataFrame(rijen)
        .reindex(columns=KOLOMMEN)
        .sort_values(["Contractnummer", "Versie"])
        .reset_index(drop=True)
    )
    return df


def schrijf(df: pd.DataFrame, pad: Path) -> None:
    pad.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(pad, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        ws = writer.sheets["Sheet1"]
        breedtes = dict(zip("ABCDEFGHIJKLMNO", [13, 32, 48, 30, 16, 12, 12] + [20] * 8))
        for kolom, breedte in breedtes.items():
            ws.column_dimensions[kolom].width = breedte
        for rij in ws.iter_rows(min_row=2):
            rij[4].number_format = "€ #,##0.00"
            rij[5].number_format = "dd-mm-yyyy"
            rij[6].number_format = "dd-mm-yyyy"


def main() -> None:
    df = genereer()
    print(f"shape={df.shape}")
    print(df.dtypes)
    laatste = df.drop_duplicates("Contractnummer", keep="last")
    print(f"contracten={laatste.shape[0]}")
    print(laatste["Contractstatus"].value_counts().to_string())
    schrijf(df, UITVOER)
    print(f"geschreven: {UITVOER}")


if __name__ == "__main__":
    main()
