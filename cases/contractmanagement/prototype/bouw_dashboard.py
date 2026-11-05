# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas",
#     "openpyxl",
# ]
# ///
"""Bouw het contractmanagement-dashboard (één offline HTML-bestand) uit een export.

De export moet de 15 vaste kolommen hebben (zie KOLOMMEN). Alle signalen worden in
de browser berekend, zodat normen en peildatum in het dashboard aan te passen zijn.
Het HTML-bestand bevat de data zelf: niets gaat over het netwerk.

Gebruik:
    uv run bouw_dashboard.py                        # nieuwste dummydata in ./data
    uv run bouw_dashboard.py pad/naar/export.xlsx   # eigen export, lokaal draaien
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import date
from pathlib import Path

import pandas as pd

HIER = Path(__file__).parent
TEMPLATE = HIER / "dashboard_template.html"

KOLOMMEN = {
    "Contractnummer": "nr",
    "Contractnaam": "naam",
    "Contractomschrijving": "oms",
    "Leverancier": "lev",
    "Bedrag": "bedrag",
    "Startdatum": "start",
    "Einddatum": "eind",
    "Contractbeheerder": "cb",
    "Contractmanager": "cm",
    "Contracteigenaar": "ce",
    "Contractstatus": "status",
    "Contracttype": "type",
    "Versie": "versie",
    "Contractversiestatus": "vstatus",
    "Cluster": "cluster",
}

# Kolommen die nu ontbreken maar nodig zijn voor betere signalen/adviezen.
GEWENSTE_KOLOMMEN = [
    "Verlengingsoptie",
    "Opzegtermijn",
    "Uitputting",
    "KPI-score",
    "Laatste voortgangsgesprek",
    "Aanbestedingsprocedure",
    "Thema",
]

log = logging.getLogger("bouw_dashboard")


def nieuwste_dummydata() -> Path:
    kandidaten = sorted(
        (HIER / "data" / "private").glob("* dummydata contractrapport.xlsx")
    )
    if not kandidaten:
        raise SystemExit(
            "Geen dummydata gevonden. Draai eerst: uv run genereer_dummydata.py"
        )
    return kandidaten[-1]


def laad(pad: Path) -> pd.DataFrame:
    df = pd.read_excel(pad).dropna(how="all")
    print(f"shape={df.shape}")
    print(df.dtypes)
    ontbrekend = [k for k in KOLOMMEN if k not in df.columns]
    if ontbrekend:
        raise SystemExit(f"Export mist verplichte kolommen: {', '.join(ontbrekend)}")
    extra = [k for k in df.columns if k not in KOLOMMEN]
    if extra:
        log.info("Extra kolommen genegeerd: %s", ", ".join(map(str, extra)))
    return df


def naar_records(df: pd.DataFrame) -> list[dict]:
    def tekst_nr(x: object) -> object:
        # Numerieke contractnummers komen uit Excel soms als float (123.0).
        if isinstance(x, float) and x.is_integer():
            return str(int(x))
        return None if pd.isna(x) else str(x)

    out = (
        df[list(KOLOMMEN)]
        .rename(columns=KOLOMMEN)
        .assign(
            regel=lambda d: d.index + 2,  # Excel-regelnummer, voor bronverwijzing
            nr=lambda d: d["nr"].map(tekst_nr),
            start=lambda d: pd.to_datetime(d["start"], errors="coerce").dt.strftime(
                "%Y-%m-%d"
            ),
            eind=lambda d: pd.to_datetime(d["eind"], errors="coerce").dt.strftime(
                "%Y-%m-%d"
            ),
            bedrag=lambda d: pd.to_numeric(d["bedrag"], errors="coerce"),
            versie=lambda d: pd.to_numeric(d["versie"], errors="coerce"),
        )
        .pipe(lambda d: d.astype(object).where(d.notna(), None))
    )
    return out.to_dict(orient="records")


def bouw(pad: Path, peildatum: date, uit: Path, terug: str | None = None) -> Path:
    df = laad(pad)
    meta = {
        "bron": pad.name,
        "regels": int(df.shape[0]),
        "peildatum": peildatum.isoformat(),
        "gebouwd": date.today().isoformat(),
        "dummy": "dummydata" in pad.name.lower(),
        "gewenst_ontbrekend": [k for k in GEWENSTE_KOLOMMEN if k not in df.columns],
        "terug": terug,
    }
    data = json.dumps(
        {"meta": meta, "rows": naar_records(df)}, ensure_ascii=False, default=str
    ).replace("<", "\\u003c")  # veilig binnen <script>: geen </script> of <!--
    html = TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", data)

    uit.parent.mkdir(parents=True, exist_ok=True)
    uit.write_text(html, encoding="utf-8")
    return uit


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("export", nargs="?", type=Path, help="Excel-export (15 kolommen)")
    p.add_argument(
        "--peildatum",
        type=date.fromisoformat,
        default=date.today(),
        help="JJJJ-MM-DD, standaard vandaag",
    )
    p.add_argument(
        "--uit",
        type=Path,
        default=HIER / "index.html",
        help="uitvoerbestand, standaard index.html naast dit script",
    )
    p.add_argument(
        "--terug",
        help="link terug naar een overzichtspagina, bijv. ../../resultaten.html",
    )
    args = p.parse_args()
    uit = bouw(
        args.export or nieuwste_dummydata(), args.peildatum, args.uit, args.terug
    )
    log.info("Dashboard geschreven: %s", uit)


if __name__ == "__main__":
    main()
