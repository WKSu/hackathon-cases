# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "duckdb",
#     "geopandas",
#     "pandas",
#     "pyogrio",
# ]
# ///
"""Laadlichten: lokale VRI-dataset -> data/private/data.js voor de levende kaart.

Leest de (niet-openbare) VRI-dataset uit `<repo>/data/` en schrijft alleen
aggregaten naar `data/private/data.js`; dat pad staat in .gitignore.
Zie DECISIONS.md (D-002, D-007).

Gebruik (vanuit de repo-root):  uv run cases/laadlichten/prototype/prep_laadlichten.py
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import duckdb
import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "data"
OUT = HERE / "data" / "private" / "data.js"

LOC = DATA / "location" / "vri_locaties.gpkg"
ITF = DATA / "location" / "260520_ITF.gpkg"
INT = (
    DATA
    / "intensity"
    / "261103 SO-MOB VRI-intensiteit per uur 2024-09 tm 2026-09.parquet"
)

BASIS = ("2025-09-01", "2025-10-01")  # september vorig jaar
NU = ("2026-09-01", "2026-10-01")  # september dit jaar
ACTIEF = 5.0  # gem. vtg/uur in de basis: signaalgroep telt normaal verkeer
DALING = 0.5  # nu < 50% van de basis = daling
LEEG = {"", "0", "#N/B", "nan", "None"}


def schoon(s: pd.Series) -> pd.Series:
    """Strip tekst en maak lege/placeholder-waarden leeg ('')."""
    s = s.astype(str).str.strip()
    return s.where(~s.isin(LEEG), "")


def nan_naar_null(o: object) -> object:
    """NaN (bv. geen basismeting, lege sensorgeometrie) wordt null in de JSON."""
    if isinstance(o, float) and math.isnan(o):
        return None
    if isinstance(o, dict):
        return {k: nan_naar_null(v) for k, v in o.items()}
    if isinstance(o, list):
        return [nan_naar_null(v) for v in o]
    return o


def load_locaties() -> pd.DataFrame:
    gdf = gpd.read_file(LOC)
    print(f"locaties ruw shape={gdf.shape}")
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
    df = pd.DataFrame(
        {
            "id": schoon(gdf["Installatienr."]),
            "naam": schoon(gdf["VRI naam"]),
            "type": schoon(gdf["Installatietype"]),
            "gebied": schoon(gdf["Deelgebied"]),
            "prio": schoon(gdf["Prioriteit"]),
            "vervangjaar": pd.to_numeric(gdf["vervangjaar"], errors="coerce"),
            "ivri": ~schoon(gdf["TLC-ID nummer (iVRI)"]).eq(""),
            "ratel": schoon(gdf["Rateltikker"]).eq("Rateltikker"),
            "lat": gdf.geometry.y.round(6),
            "lon": gdf.geometry.x.round(6),
        }
    )
    print(f"locaties shape={df.shape}")
    print(df.dtypes)
    return df


def load_itf() -> tuple[pd.DataFrame, dict[str, dict]]:
    """Tel lussen/drukknoppen per VRI en verzamel geometrie om te tekenen."""
    lanes = gpd.read_file(ITF, layer="lanes")
    sensors = gpd.read_file(ITF, layer="sensors")
    print(f"itf lanes shape={lanes.shape}, sensors shape={sensors.shape}")
    print(sensors.dtypes)

    lanes = lanes[lanes.geometry.notna()].assign(
        id=lambda d: d["intersection"].str.split("-").str[0]
    )
    pts = sensors.geometry.representative_point()
    sensors = sensors.assign(
        id=sensors["intersection"].str.split("-").str[0],
        t=sensors["type"].map({"inductionLoop": "l", "pushButton": "k"}).fillna("o"),
        lat=pts.y.round(6),
        lon=pts.x.round(6),
    )

    tel = (
        sensors.groupby("id")["t"]
        .agg(
            lussen=lambda t: int((t == "l").sum()),
            knoppen=lambda t: int((t == "k").sum()),
        )
        .reset_index()
    )

    geo: dict[str, dict] = {}
    for vri, geoms in lanes.groupby("id").geometry:
        geo.setdefault(vri, {})["lanes"] = [
            [[round(y, 6), round(x, 6)] for x, y, *_ in g.coords] for g in geoms
        ]
    for vri, grp in sensors.groupby("id"):
        geo.setdefault(vri, {})["sensors"] = grp[["lat", "lon", "t"]].values.tolist()
    return tel, geo


def load_intensiteit() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gemiddelde per signaalgroep en werkdagprofiel per uur, basis vs nu."""
    con = duckdb.connect()
    con.execute(
        f"""
        create view i as
        select vri_id as id, sg, intensiteit,
               case when ts < '{NU[0]}' then 'b' else 'n' end as p,
               hour(ts) as uur, isodow(ts) <= 5 as werkdag
        from read_parquet('{INT.as_posix()}')
        where (ts >= '{BASIS[0]}' and ts < '{BASIS[1]}')
           or (ts >= '{NU[0]}' and ts < '{NU[1]}')
        """
    )
    gem = con.sql("select id, sg, p, avg(intensiteit) gem from i group by all").df()
    prof = con.sql(
        "select id, sg, p, uur, avg(intensiteit) gem from i where werkdag group by all"
    ).df()
    print(f"intensiteit gem shape={gem.shape}, profiel shape={prof.shape}")
    print(gem.dtypes)
    return gem, prof


def signaalgroepen(gem: pd.DataFrame, prof: pd.DataFrame) -> pd.DataFrame:
    """Eén rij per VRI x signaalgroep met basis, nu, status en twee dagprofielen."""
    sg = (
        gem.pivot_table(index=["id", "sg"], columns="p", values="gem")
        .reindex(columns=["b", "n"])
        .rename(columns={"b": "basis", "n": "nu"})
        .reset_index()
        .assign(nu=lambda d: d["nu"].fillna(0.0))
    )
    actief = sg["basis"] >= ACTIEF
    sg["status"] = "ok"
    sg.loc[actief & (sg["nu"] < DALING * sg["basis"]), "status"] = "daling"
    sg.loc[actief & (sg["nu"] == 0), "status"] = "stil"
    sg["actief"] = actief

    def profiel(p: str) -> pd.Series:
        wide = (
            prof[prof["p"] == p]
            .pivot_table(index=["id", "sg"], columns="uur", values="gem")
            .reindex(columns=range(24))
            .fillna(0)
            .round()
            .astype(int)
        )
        return pd.Series(wide.values.tolist(), index=wide.index, name=f"prof_{p}")

    sg = sg.join(profiel("b"), on=["id", "sg"]).join(profiel("n"), on=["id", "sg"])
    leeg24 = [0] * 24
    for c in ("prof_b", "prof_n"):
        sg[c] = sg[c].apply(lambda v: v if isinstance(v, list) else leeg24)
    # Signaalgroepen die in beide periodes niets tellen, laten we weg.
    return sg[(sg["basis"].fillna(0) > 0) | (sg["nu"] > 0)]


def vri_status(sg: pd.DataFrame) -> pd.DataFrame:
    per = sg.groupby("id").agg(
        n_actief=("actief", "sum"),
        n_stil=("status", lambda s: int((s == "stil").sum())),
        n_daling=("status", lambda s: int((s == "daling").sum())),
    )
    per["status"] = "ok"
    per.loc[per["n_daling"] > 0, "status"] = "daling"
    per.loc[per["n_stil"] > 0, "status"] = "storing"
    per.loc[(per["n_actief"] > 0) & (per["n_stil"] == per["n_actief"]), "status"] = (
        "uitval"
    )
    return per.reset_index()


def main() -> None:
    loc = load_locaties()
    tel, geo = load_itf()
    gem, prof = load_intensiteit()
    sg = signaalgroepen(gem, prof)
    per = vri_status(sg)

    vri = (
        loc.merge(tel, on="id", how="left")
        .merge(per, on="id", how="left")
        .assign(
            lussen=lambda d: d["lussen"].fillna(0).astype(int),
            knoppen=lambda d: d["knoppen"].fillna(0).astype(int),
            status=lambda d: d["status"].fillna("geen"),
            vervangjaar=lambda d: d["vervangjaar"].astype("Int64"),
        )
        .drop(columns=["n_actief"])
    )
    sg_per_vri = {
        k: g[["sg", "basis", "nu", "status", "prof_b", "prof_n"]]
        .assign(basis=lambda d: d["basis"].round(1), nu=lambda d: d["nu"].round(1))
        .sort_values("sg")
        .values.tolist()
        for k, g in sg.groupby("id")
    }

    records = json.loads(vri.to_json(orient="records"))
    for r in records:
        r["sg"] = sg_per_vri.get(r["id"], [])
        r["geo"] = 1 if r["id"] in geo else 0

    out = {
        "meta": {
            "gemaakt": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "basis": "september 2025",
            "nu": "september 2026",
            "actief": ACTIEF,
            "daling": DALING,
        },
        "vri": records,
        "geo": {k: v for k, v in geo.items() if k in set(vri["id"])},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "window.LAADLICHTEN = "
        + json.dumps(
            nan_naar_null(out),
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        + ";\n",
        encoding="utf-8",
    )
    print(vri["status"].value_counts().to_string())
    print(f"geschreven: {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
