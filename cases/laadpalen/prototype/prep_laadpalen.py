# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "geopandas",
#     "pyogrio",
#     "shapely>=2",
#     "numpy",
#     "scipy",
#     "requests",
# ]
# ///
"""Laadpalen-prototype: toets parkeervakken aan de Beleidsregel laadpunten 2025.

Leest lokale gemeentelijke lagen (parkeervakken, bijzondere vakken, bomen,
buurtgrenzen), haalt de BGT op bij PDOK en leest de CBS 100 m-vierkanten.
Schrijft `data/private/data.js` (buiten git, zie DECISIONS D-002).

Per openbaar parkeervak:
- stoeprand = de rand tegenover de rijbaan; stoepbreedte = lengte van een
  loodrechte lijn vanaf die rand door aaneengesloten BGT-voetpad (D-005);
- paalpunt = hoek van de stoeprand bij het buurvak, 50 cm uit de band;
- afstand van het paalpunt tot de kroonrand van de dichtstbijzijnde grote
  boom, en tot een BGT-inrit (D-004);
- binnen 200 m: openbare vakken, bestaande laadvakken, CBS-woningen (D-006).

Draaien (paden naar de lokale bronnen meegeven):
    uv run prep_laadpalen.py --parkeren <dir> --tir <dir> --bomen <shp> --cbs <json>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import requests
import shapely
from scipy.spatial import cKDTree
from shapely.geometry import Point, shape

HERE = Path(__file__).parent
REPO = HERE.parents[2]
SRC = REPO / "_private" / "laadpalen" / "data"
OUT = HERE / "data" / "private" / "data.js"
CACHE = HERE / "data" / "private" / "cache"

BUURTEN = [
    "Oude Noorden",
    "Agniesebuurt",
    "Provenierswijk",
    "Bergpolder",
    "Liskwartier",
    "Blijdorp",
]
PRESETS = [
    ("Zwaanshals", "Zwaanshals 250, Rotterdam"),
    ("Bergweg", "Bergweg 150, Rotterdam"),
    ("Statenweg", "Statenweg 100, Rotterdam"),
]
RADIUS = 200.0  # m, beleidsregel: laadlocatie binnen 200 m
CONTEXT_BUF = 250.0  # m rond het demogebied, zodat tellingen aan de rand kloppen
PAAL_UIT_BAND = 0.5  # m, beleidsregel: "50 cm uit de band"
RAY_BACK, RAY_LEN = 1.0, 15.0  # m, meetlijn begint 1 m binnen het vak
GROTE_BOOM = {"12-15 m.", "15-18 m.", "18-24 m.", "> 24 m."}  # D-004 aanname
KROON_DEFAULT = 8.0  # m, als kroondiameter ontbreekt

BGT = "https://api.pdok.nl/lv/bgt/ogc/v1/collections/{c}/items"
RD = "http://www.opengis.net/def/crs/EPSG/0/28992"
LOCATIESERVER = "https://api.pdok.nl/bzk/locatieserver/search/v3_1/free"

# BGT-wegdeelfunctie -> klasse
WEG = {
    "voetpad": "voetpad",
    "voetgangersgebied": "voetpad",
    "voetpad op trap": "voetpad",
    "woonerf": "woonerf",
    "fietspad": "fietspad",
    "parkeervlak": "parkeren",
    "inrit": "inrit",
    "OV-baan": "rijbaan",
    "spoorbaan": "rijbaan",
    "overweg": "rijbaan",
    "rijbaan lokale weg": "rijbaan",
    "rijbaan regionale weg": "rijbaan",
    "rijbaan autoweg": "rijbaan",
    "rijbaan autosnelweg": "rijbaan",
}
KLASSEN = [
    "voetpad",
    "groen",
    "fietspad",
    "parkeren",
    "rijbaan",
    "inrit",
    "woonerf",
    "overig",
    "geen",
]
K = {k: i for i, k in enumerate(KLASSEN)}

# Bijzondere vakken -> categorie (volgorde = voorrang bij overlap)
EIGEN = {"Eigen terrein", "Gebied met hekjes", "Tankstation-garage"}
LAAD = {"Elektrische oplaadpunten"}
TIJD = {"Blauwe zones", "Parkeerplaats tijdsafhankelijk"}
NEGEER = {"Langsparkeren"}  # vorm, geen regime
CAT = ["regulier", "laadvak", "parkeerduur", "bijzonder"]


def load_area(tir: Path) -> gpd.GeoDataFrame:
    bu = gpd.read_file(tir / "Buurten" / "Buurten_vlakken.shp")
    bu = bu[bu["BUURTNAAM"].isin(BUURTEN)][["BUURTNAAM", "geometry"]]
    missing = set(BUURTEN) - set(bu["BUURTNAAM"])
    if missing:
        raise SystemExit(f"Buurten niet gevonden in TIR: {missing}")
    assert bu.crs.to_epsg() == 28992, bu.crs
    print(f"buurten: {bu.shape}")
    return bu.reset_index(drop=True)


def load_bays(parkeren: Path, area, ctx) -> gpd.GeoDataFrame:
    bb = tuple(ctx.bounds)
    pv = gpd.read_file(
        parkeren / "ParkeerVakken.shp", bbox=bb, columns=["TYPE", "GUID"]
    )
    bz = gpd.read_file(parkeren / "ParkeerVakkenBijzonder.shp", bbox=bb)
    print(f"vakken (bbox): {pv.shape}, bijzonder (bbox): {bz.shape}")
    print(pv.dtypes)
    pv["rp"] = pv.geometry.representative_point()
    pv = pv[pv["rp"].within(ctx)].reset_index(drop=True)

    # subtype per vak: representatief punt in bijzonder-vlak, zwaarste wint
    bz = bz[~bz["TYPE"].isin(NEGEER)].reset_index(drop=True)
    rank = np.where(
        bz["TYPE"].isin(EIGEN),
        4,
        np.where(bz["TYPE"].isin(LAAD), 3, np.where(bz["TYPE"].isin(TIJD), 2, 1)),
    )
    tree = shapely.STRtree(bz.geometry.values)
    bi, oi = tree.query(pv["rp"].values, predicate="within")
    best_rank = np.zeros(len(pv), int)
    best_type = np.full(len(pv), "", object)
    for b, o in zip(bi, oi):
        if rank[o] > best_rank[b]:
            best_rank[b], best_type[b] = rank[o], bz.at[o, "TYPE"]
    pv["eigen"] = best_rank == 4
    pv["cat"] = np.select(
        [best_rank == 3, best_rank == 2, best_rank == 1], [1, 2, 3], default=0
    )
    pv["bijz_type"] = best_type
    pv["in_area"] = pv["rp"].within(area)
    print(
        f"vakken in context: {len(pv)}, in demogebied: {pv['in_area'].sum()}, "
        f"eigen terrein: {pv['eigen'].sum()}, laadvakken: {(pv['cat'] == 1).sum()}"
    )
    return pv


def fetch_bgt(collection: str, bb: tuple) -> list[dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    cache = CACHE / f"bgt_{collection}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    url, feats = BGT.format(c=collection), []
    params = {
        "f": "json",
        "limit": 1000,
        "bbox": ",".join(f"{v:.1f}" for v in bb),
        "bbox-crs": RD,
        "crs": RD,
    }
    while url:
        r = requests.get(url, params=params, timeout=120)
        r.raise_for_status()
        d = r.json()
        feats += d["features"]
        url = next((lk["href"] for lk in d["links"] if lk["rel"] == "next"), None)
        params = None
        print(f"  {collection}: {len(feats)}", end="\r")
    feats = [
        {"p": f["properties"], "g": f["geometry"]}
        for f in feats
        if not f["properties"].get("eind_registratie")
        and f["properties"].get("relatieve_hoogteligging", 0) in (0, None)
    ]
    print(f"  {collection}: {len(feats)} actueel op maaiveld")
    cache.write_text(json.dumps(feats), encoding="utf-8")
    return feats


def classify(collection: str, p: dict) -> str:
    if collection == "wegdeel":
        return WEG.get(p.get("functie"), "overig")
    if collection == "begroeidterreindeel":
        return "groen"
    fv = (p.get("fysiek_voorkomen") or "").lower()  # ondersteunendwegdeel
    return "groen" if any(w in fv for w in ("groen", "gras", "struik")) else "overig"


def load_bgt(ctx) -> gpd.GeoDataFrame:
    bb = tuple(ctx.bounds)
    rows = []
    for c in ["wegdeel", "ondersteunendwegdeel", "begroeidterreindeel"]:
        for f in fetch_bgt(c, bb):
            g = shape(f["g"])
            if g.geom_type not in ("Polygon", "MultiPolygon"):
                continue
            if not g.is_valid:
                g = g.buffer(0)
            rows.append((classify(c, f["p"]), g))
    bgt = gpd.GeoDataFrame(
        {"klasse": [r[0] for r in rows]}, geometry=[r[1] for r in rows], crs=28992
    )
    print(f"bgt: {bgt.shape}")
    print(bgt["klasse"].value_counts().to_string())
    return bgt


def ray_profiles(
    origins: np.ndarray, normals: np.ndarray, bgt: gpd.GeoDataFrame
) -> list[list[tuple[int, float, float]]]:
    """Per meetlijn: lijst (klasse, t0, t1) langs de normaal, gesorteerd, samengevoegd."""
    a = origins - RAY_BACK * normals
    b = origins + RAY_LEN * normals
    rays = shapely.linestrings(np.stack([a, b], axis=1))
    polys = bgt.geometry.values
    kl = bgt["klasse"].map(K).to_numpy()
    ri, pi = shapely.STRtree(polys).query(rays, predicate="intersects")
    inter = shapely.intersection(rays[ri], polys[pi])
    parts, pidx = shapely.get_parts(inter, return_index=True)
    keep = shapely.get_type_id(parts) == 1  # LineString
    parts, pidx = parts[keep], pidx[keep]
    coords, cidx = shapely.get_coordinates(parts, return_index=True)
    ray_of_part = ri[pidx]
    t = np.einsum(
        "ij,ij->i", coords - origins[ray_of_part[cidx]], normals[ray_of_part[cidx]]
    )
    t0 = np.full(len(parts), np.inf)
    t1 = np.full(len(parts), -np.inf)
    np.minimum.at(t0, cidx, t)
    np.maximum.at(t1, cidx, t)
    out: list[list] = [[] for _ in range(len(rays))]
    for r, k, s, e in zip(ray_of_part, kl[pi[pidx]], t0, t1):
        if e - s > 0.02:
            out[r].append((int(k), float(s), float(e)))
    merged = []
    for segs in out:
        segs.sort(key=lambda x: x[1])
        m: list[list] = []
        for k, s, e in segs:
            if m and m[-1][0] == k and s - m[-1][2] <= 0.25:
                m[-1][2] = max(m[-1][2], e)
            else:
                m.append([k, s, e])
        merged.append([tuple(x) for x in m])
    return merged


def read_edge(prof: list[tuple[int, float, float]]) -> tuple[int, float, float, int]:
    """(klasse aan deze kant, begin, breedte, klasse erachter) voor één meetlijn."""
    segs = [s for s in prof if s[2] > 0.1]
    i = 0
    # sla BGT-parkeervlak en smalle 'overig'-stroken (band) vlak achter de rand over
    while i < len(segs):
        k, s, e = segs[i]
        if k == K["parkeren"] and e <= 1.5 or k == K["overig"] and e - max(s, 0) <= 0.8 and e <= 1.5:
            i += 1
        else:
            break
    if i >= len(segs) or segs[i][1] > 1.5:
        return K["geen"], np.nan, np.nan, K["geen"]
    k, s, e = segs[i]
    achter = (
        segs[i + 1][0]
        if i + 1 < len(segs) and segs[i + 1][1] - e <= 0.5
        else K["overig"]
    )
    width = e - max(s, -RAY_BACK)
    if k == K["voetpad"] and e >= RAY_LEN - 0.1:
        achter = K["overig"]  # pleinachtig: breder dan de meetlijn
    return k, max(s, 0.0), width, achter


def kerb_analysis(pv: gpd.GeoDataFrame, bgt: gpd.GeoDataFrame) -> dict:
    n = len(pv)
    mrr = shapely.oriented_envelope(pv.geometry.values)
    ring = shapely.get_exterior_ring(mrr)
    cnt = shapely.get_num_coordinates(ring)
    if (cnt != 5).any():
        raise SystemExit(
            f"{(cnt != 5).sum()} vakken zonder geldige omsluitende rechthoek"
        )
    corners = shapely.get_coordinates(ring).reshape(n, 5, 2)[:, :4]
    cen = corners.mean(axis=1)
    a, b = corners, np.roll(corners, -1, axis=1)
    mid = (a + b) / 2
    d = b - a
    nrm = np.stack([d[..., 1], -d[..., 0]], axis=-1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    flip = np.einsum("ijk,ijk->ij", nrm, mid - cen[:, None]) < 0
    nrm[flip] *= -1
    prof = ray_profiles(mid.reshape(-1, 2), nrm.reshape(-1, 2), bgt)
    edges = np.array([read_edge(p) for p in prof], dtype=float).reshape(n, 4, 4)

    kant = np.full(n, K["geen"])
    sw = np.full(n, np.nan)
    achter = np.full(n, K["geen"])
    kerb = np.full(n, -1)
    for i in range(n):
        ek = edges[i, :, 0]
        road = np.where(ek == K["rijbaan"])[0]
        if len(road):
            j = road[np.argmin(edges[i, road, 1])]
            kb = (j + 2) % 4
        else:
            vp = np.where(ek == K["voetpad"])[0]
            if not len(vp):
                continue
            kb = vp[np.argmin(edges[i, vp, 1])]
        kerb[i] = kb
        kant[i] = int(edges[i, kb, 0])
        sw[i] = edges[i, kb, 2] if kant[i] == K["voetpad"] else np.nan
        achter[i] = int(edges[i, kb, 3])

    # paalpunt: hoek van de stoeprand die aan een buurvak grenst, 50 cm uit de band
    tree = shapely.STRtree(pv.geometry.values)
    paal = np.full((n, 2), np.nan)
    partner = np.full(n, -1)
    nbr_count = np.zeros(n, int)
    for i in np.where(kerb >= 0)[0]:
        kb = kerb[i]
        best = None
        for c in (a[i, kb], b[i, kb]):
            hits = tree.query(Point(c), predicate="dwithin", distance=0.6)
            hits = hits[hits != i]
            if len(hits):
                nbr_count[i] += 1
                h = hits[
                    np.argmin(shapely.distance(pv.geometry.values[hits], Point(c)))
                ]
                if best is None or pv.at[h, "cat"] == 0:
                    best = (c, h)
        c, h = best if best else (a[i, kb], -1)
        paal[i] = c + PAAL_UIT_BAND * nrm[i, kb]
        partner[i] = h
    return {
        "kant": kant,
        "sw": sw,
        "achter": achter,
        "paal": paal,
        "partner": partner,
        "kop": (nbr_count <= 1) & (kerb >= 0),
    }


def tree_clearance(paal: np.ndarray, bomen: Path, ctx) -> tuple[gpd.GeoDataFrame, dict]:
    bt = gpd.read_file(bomen, bbox=tuple(ctx.bounds), columns=["HOOGTE", "KROONDIAME"])
    print(f"bomen (bbox): {bt.shape}")
    print(bt.dtypes)
    bt = bt[bt.geometry.within(ctx)].reset_index(drop=True)
    bt["groot"] = bt["HOOGTE"].isin(GROTE_BOOM)
    bt["r"] = (bt["KROONDIAME"].fillna(KROON_DEFAULT).clip(lower=2) / 2).astype(float)
    big = bt[bt["groot"]]
    xy = np.c_[big.geometry.x, big.geometry.y]
    kd = cKDTree(xy)
    ok = ~np.isnan(paal[:, 0])
    clear = np.full(len(paal), np.nan)
    dist = np.full(len(paal), np.nan)
    rad = np.full(len(paal), np.nan)
    dd, ii = kd.query(paal[ok], k=8, distance_upper_bound=40)
    rr = np.where(np.isfinite(dd), big["r"].to_numpy()[np.minimum(ii, len(big) - 1)], 0)
    cl = np.where(np.isfinite(dd), dd - rr, np.inf)
    j = np.argmin(cl, axis=1)
    sel = np.arange(len(j))
    clear[ok] = cl[sel, j]
    dist[ok] = dd[sel, j]
    rad[ok] = rr[sel, j]
    print(f"bomen in context: {len(bt)}, groot: {bt['groot'].sum()}")
    return bt, {"boom_clear": clear, "boom_d": dist, "boom_r": rad}


def inrit_distance(paal: np.ndarray, bgt: gpd.GeoDataFrame) -> np.ndarray:
    ir = bgt[bgt["klasse"] == "inrit"].geometry.values
    out = np.full(len(paal), np.nan)
    ok = ~np.isnan(paal[:, 0])
    if len(ir):
        pts = shapely.points(paal[ok])
        tree = shapely.STRtree(ir)
        idx = tree.query_nearest(
            pts, max_distance=30, return_distance=True, all_matches=False
        )
        (pi, _gi), dd = idx
        tmp = np.full(ok.sum(), np.inf)
        tmp[pi] = dd
        out[ok] = tmp
    return out


def load_cbs(cbs: Path, ctx) -> gpd.GeoDataFrame:
    raw = json.loads(cbs.read_text(encoding="utf-8"))
    x = np.array([int(r["code"][1:5]) * 100 + 50 for r in raw], float)
    y = np.array([int(r["code"][6:10]) * 100 + 50 for r in raw], float)
    w = np.array([max(r.get("aantal_woningen") or 0, 0) for r in raw], float)
    g = gpd.GeoDataFrame({"woningen": w}, geometry=gpd.points_from_xy(x, y), crs=28992)
    g = g[g.within(ctx.buffer(100))].reset_index(drop=True)
    print(f"cbs-vierkanten in context: {g.shape}, woningen: {g['woningen'].sum():.0f}")
    return g


def geocode(q: str) -> tuple[float, float] | None:
    try:
        r = requests.get(
            LOCATIESERVER,
            params={
                "q": q,
                "rows": 1,
                "fq": "type:adres",
                "fl": "weergavenaam,centroide_ll",
            },
            timeout=20,
        )
        r.raise_for_status()
        doc = r.json()["response"]["docs"][0]
    except (requests.RequestException, IndexError, KeyError) as e:
        print(f"  geocode mislukt voor {q}: {e}")
        return None
    lon, lat = map(float, doc["centroide_ll"][6:-1].split())
    print(f"  {q} -> {doc['weergavenaam']}")
    return lat, lon


def to_ll(xy: np.ndarray) -> np.ndarray:
    """RD -> [lat, lon] in 1e-6 graden (int)."""
    ok = ~np.isnan(xy[:, 0])
    out = np.zeros((len(xy), 2), np.int64)
    if ok.any():
        p = gpd.GeoSeries(gpd.points_from_xy(xy[ok, 0], xy[ok, 1]), crs=28992).to_crs(
            4326
        )
        out[ok, 0] = np.round(p.y.to_numpy() * 1e6)
        out[ok, 1] = np.round(p.x.to_numpy() * 1e6)
    return out


def ring_ll(geoms, tol: float = 0.3) -> list[list[int]]:
    """Polygonen -> lijst ringen [lat0, lon0, lat1, lon1, ...] in 1e-6 graden."""
    s = gpd.GeoSeries(geoms, crs=28992).simplify(tol).to_crs(4326)
    rings = []
    for g in s:
        for p in getattr(g, "geoms", [g]):
            if p.is_empty or p.geom_type != "Polygon":
                continue
            c = np.round(np.asarray(p.exterior.coords)[:, ::-1] * 1e6).astype(np.int64)
            rings.append(c.ravel().tolist())
    return rings


def bay_rings_ll(geoms) -> list[list[int]]:
    """Precies één ring per vak (grootste deel), zodat index = vaknummer blijft."""
    s = gpd.GeoSeries(geoms, crs=28992).simplify(0.05).to_crs(4326)
    rings = []
    for g in s:
        p = max(getattr(g, "geoms", [g]), key=lambda q: q.area)
        c = np.round(np.asarray(p.exterior.coords)[:, ::-1] * 1e6).astype(np.int64)
        rings.append(c.ravel().tolist())
    return rings


def r1(v: np.ndarray, f: float = 10) -> list:
    """Afronden naar int (dm bij f=10); NaN -> -1, inf -> 9999."""
    v = np.where(np.isinf(v), 9999 / f, v)
    return np.where(np.isnan(v), -1, np.round(v * f)).astype(int).tolist()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--parkeren", type=Path, default=SRC / "Parkeren")
    ap.add_argument("--tir", type=Path, default=SRC / "TIR")
    ap.add_argument("--bomen", type=Path, default=SRC / "bomen" / "Bomen.shp")
    ap.add_argument(
        "--cbs", type=Path, default=SRC / "cbs" / "cbs_vierkant100_2024_rotterdam.json"
    )
    args = ap.parse_args()

    bu = load_area(args.tir)
    area = bu.union_all()
    ctx = area.buffer(CONTEXT_BUF)
    pv = load_bays(args.parkeren, area, ctx)
    pv = pv[~pv["eigen"]].reset_index(drop=True)  # eigen terrein doet niet mee
    bgt = load_bgt(ctx)

    ev = pv[pv["in_area"]].reset_index(drop=True)
    kerb = kerb_analysis(ev, bgt)
    bt, boom = tree_clearance(kerb["paal"], args.bomen, ctx)
    inrit = inrit_distance(kerb["paal"], bgt)

    # dekking binnen 200 m (hemelsbreed, D-007), tellen over context incl. rand
    rp_all = np.c_[pv["rp"].x, pv["rp"].y]
    kd_all = cKDTree(rp_all)
    kd_laad = cKDTree(rp_all[pv["cat"].to_numpy() == 1])
    cbs = load_cbs(args.cbs, ctx)
    kd_cbs = cKDTree(np.c_[cbs.geometry.x, cbs.geometry.y])
    wcbs = cbs["woningen"].to_numpy()

    def ctx_counts(xy: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        n200 = kd_all.query_ball_point(xy, RADIUS, return_length=True)
        l200 = kd_laad.query_ball_point(xy, RADIUS, return_length=True)
        w200 = np.array([wcbs[i].sum() for i in kd_cbs.query_ball_point(xy, RADIUS)])
        return n200, l200, w200

    rp_ev = np.c_[ev["rp"].x, ev["rp"].y]
    n200, l200, w200 = ctx_counts(rp_ev)

    # overzichtslaag: CBS-vierkanten in het demogebied
    cells = cbs[cbs.within(area)].reset_index(drop=True)
    cxy = np.c_[cells.geometry.x, cells.geometry.y]
    cn, cl, cw = ctx_counts(cxy)

    # --- controles -------------------------------------------------------------
    kant = kerb["kant"]
    sw = kerb["sw"]
    pub = ev["cat"].to_numpy() == 0
    print("\nkant van de stoeprand (reguliere vakken):")
    vals, cnts = np.unique(kant[pub], return_counts=True)
    for v, c in zip(vals, cnts):
        print(f"  {KLASSEN[v]:9s} {c:6d}  ({c / pub.sum():.0%})")
    s = sw[pub & (kant == K["voetpad"])]
    print(
        f"stoepbreedte: mediaan {np.nanmedian(s):.2f} m, p10 {np.nanpercentile(s, 10):.2f}, "
        f"p90 {np.nanpercentile(s, 90):.2f}, >=2,0 m: {np.mean(s >= 2.0):.0%}, "
        f">=1,7 m: {np.mean(s >= 1.7):.0%}"
    )
    bc = boom["boom_clear"][pub]
    print(
        f"kroonrand grote boom: <0 m {np.mean(bc < 0):.0%}, <1 m {np.mean(bc < 1):.0%}, "
        f"<3 m {np.mean(bc < 3):.0%}; stam <3 m {np.mean(boom['boom_d'][pub] < 3):.0%}"
    )
    print(
        f"inrit <2 m: {np.mean(inrit[pub] < 2):.0%}; kop van rij: {kerb['kop'][pub].mean():.0%}"
    )
    print(
        f"dekking (laadvakken/vakken binnen 200 m): mediaan {np.median(l200 / np.maximum(n200, 1)):.1%}"
    )
    if (kant[pub] == K["geen"]).mean() > 0.4:
        raise SystemExit(
            "Meer dan 40% van de vakken zonder herkende rand: check BGT/CRS."
        )

    # --- schrijven -------------------------------------------------------------
    poly_ll = bay_rings_ll(ev.geometry.values)
    assert len(poly_ll) == len(ev), (len(poly_ll), len(ev))
    bijz_types = sorted(set(ev["bijz_type"]) - {""})
    presets = []
    for naam, q in PRESETS:
        ll = geocode(q)
        if ll:
            presets.append({"naam": naam, "adres": q, "lat": ll[0], "lon": ll[1]})
    buurt_of = np.full(len(ev), -1)
    bi, ai = shapely.STRtree(bu.geometry.values).query(
        ev["rp"].values, predicate="within"
    )
    buurt_of[bi] = ai
    bt_in = bt[bt.geometry.within(area.buffer(RADIUS + 50))]
    bgt_draw = bgt[bgt.intersects(ctx)]
    data = {
        "meta": {
            "gebied": "Noord (vooroorlogs)",
            "buurten": bu["BUURTNAAM"].tolist(),
            "straal": RADIUS,
            "klassen": KLASSEN,
            "cat": CAT,
            "bijz_types": bijz_types,
            "bronnen": [
                "Parkeervakken en bijzondere vakken, gemeente Rotterdam",
                "Bomen, gemeente Rotterdam",
                "BGT, PDOK/Kadaster (CC0)",
                "CBS vierkantstatistiek 100 m, 2024",
                "Beleidsregel plaatsing laadpunten in de openbare ruimte gemeente Rotterdam 2025 (Gmb 2025, 307736)",
            ],
        },
        "buurtgrenzen": [
            {"naam": nm, "rings": ring_ll([g], 1.0)}
            for nm, g in zip(bu["BUURTNAAM"], bu.geometry)
        ],
        "vakken": {
            "rp": to_ll(rp_ev).ravel().tolist(),
            "poly": poly_ll,
            "type": ev["TYPE"]
            .map({"LANGS": 0, "DWARS": 1, "SCHUIN": 2})
            .fillna(0)
            .astype(int)
            .tolist(),
            "cat": ev["cat"].astype(int).tolist(),
            "bijz": [bijz_types.index(t) if t else -1 for t in ev["bijz_type"]],
            "buurt": buurt_of.tolist(),
            "kant": kant.astype(int).tolist(),
            "achter": kerb["achter"].astype(int).tolist(),
            "sw": r1(sw),
            "paal": to_ll(kerb["paal"]).ravel().tolist(),
            "partner": kerb["partner"].astype(int).tolist(),
            "kop": kerb["kop"].astype(int).tolist(),
            "boomc": r1(boom["boom_clear"]),
            "boomd": r1(boom["boom_d"]),
            "boomr": r1(boom["boom_r"]),
            "inrit": r1(inrit),
            "n200": n200.astype(int).tolist(),
            "l200": l200.astype(int).tolist(),
            "w200": w200.astype(int).tolist(),
        },
        "bomen": {
            "ll": to_ll(np.c_[bt_in.geometry.x, bt_in.geometry.y]).ravel().tolist(),
            "groot": bt_in["groot"].astype(int).tolist(),
            "r": r1(bt_in["r"].to_numpy()),
        },
        "bgt": {
            k: ring_ll(bgt_draw[bgt_draw["klasse"] == k].geometry.values, 0.2)
            for k in ["groen", "voetpad", "fietspad", "inrit"]
        },
        "groen_m2": {
            "ll": to_ll(
                shapely.get_coordinates(
                    shapely.centroid(bgt[bgt["klasse"] == "groen"].geometry.values)
                )
            )
            .ravel()
            .tolist(),
            "m2": np.round(bgt[bgt["klasse"] == "groen"].area).astype(int).tolist(),
        },
        "cellen": {
            "ll": to_ll(cxy).ravel().tolist(),
            "woningen": cells["woningen"].astype(int).tolist(),
            "n200": cn.astype(int).tolist(),
            "l200": cl.astype(int).tolist(),
            "w200": cw.astype(int).tolist(),
        },
        "presets": presets,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    js = "window.LAADPALEN = " + json.dumps(data, separators=(",", ":")) + ";\n"
    OUT.write_text(js, encoding="utf-8")
    print(f"\n{OUT} geschreven: {len(js) / 1e6:.1f} MB, {len(ev)} vakken")


if __name__ == "__main__":
    main()
