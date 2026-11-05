# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Laadlichten: openbare versie voor de themadag-site (een paar VRI's in het centrum).

Leest het lokale databestand (data/private/data.js, gemaakt door
prep_laadlichten.py), houdt alleen de VRI's in SELECTIE over en schrijft naar
<doelmap>:
  - data.js     de selectie (window.LAADLICHTEN = ...)
  - index.html  dezelfde kaartpagina, die data.js uit dezelfde map laadt

Zie DECISIONS.md D-010.

Gebruik:  uv run cases/laadlichten/prototype/maak_publieke_versie.py <doelmap>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRON_DATA = HERE / "data" / "private" / "data.js"
BRON_HTML = HERE / "index.html"
PREFIX = "window.LAADLICHTEN = "
SCRIPT_LOKAAL = '<script src="data/private/data.js" charset="utf-8"></script>'
SCRIPT_PUBLIEK = '<script src="data.js" charset="utf-8"></script>'

# Acht VRI's in het centrum (Coolsingel, Blaak, Weena, Boompjes), zo gekozen dat
# elk onderdeel te zien is: geen tellingen, daling, ov-prioriteit en de schets.
SELECTIE = (
    "11160",  # Boompjes - Erasmusbrug: schets met ov-prioriteit
    "11050",  # Boompjes - Willemsbrug
    "11100",  # Blaak - Keizerstraat: geen tellingen ontvangen (iVRI)
    "11120",  # Churchillplein
    "11090",  # Aert van Nesstraat - Coolsingel
    "11110",  # Coolsingel - Doelwater: daling
    "12070",  # Weena - Karel Doormanstraat: daling
    "11060",  # Hofplein
)


def lees_data() -> dict:
    tekst = BRON_DATA.read_text(encoding="utf-8")
    if not tekst.startswith(PREFIX):
        raise ValueError(f"{BRON_DATA} begint niet met {PREFIX!r}")
    data = json.loads(tekst[len(PREFIX) :].rstrip().rstrip(";"))
    print(f"bron: {len(data['vri'])} VRI's, {len(data['geo'])} met geometrie")
    return data


def selecteer(data: dict) -> dict:
    vri = [v for v in data["vri"] if v["id"] in SELECTIE]
    ontbreekt = set(SELECTIE) - {v["id"] for v in vri}
    if ontbreekt:
        raise ValueError(f"VRI's niet gevonden in de bron: {sorted(ontbreekt)}")
    return {
        "meta": {**data["meta"], "selectie": f"{len(vri)} VRI's in het centrum"},
        "vri": vri,
        "geo": {k: g for k, g in data["geo"].items() if k in SELECTIE},
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Gebruik: maak_publieke_versie.py <doelmap>")
    doel = Path(sys.argv[1]).resolve()
    doel.mkdir(parents=True, exist_ok=True)

    sel = selecteer(lees_data())
    js = PREFIX + json.dumps(sel, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (doel / "data.js").write_text(js, encoding="utf-8")

    html = BRON_HTML.read_text(encoding="utf-8")
    if SCRIPT_LOKAAL not in html:
        raise ValueError(f"{BRON_HTML} laadt geen {SCRIPT_LOKAAL!r}")
    (doel / "index.html").write_text(
        html.replace(SCRIPT_LOKAAL, SCRIPT_PUBLIEK), encoding="utf-8"
    )

    status = {v["id"]: v["status"] for v in sel["vri"]}
    print(f"selectie: {status}")
    print(f"geschreven: {doel / 'index.html'} en data.js ({len(js) / 1e3:.0f} kB)")


if __name__ == "__main__":
    main()
