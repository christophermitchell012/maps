#!/usr/bin/env python3
"""Build Map 26's production 100-place "Tonight" ranking snapshot.

Architecture
------------
* Candidate names/coordinates: U.S. Census Bureau 2025 Gazetteer.
* Population used only to build the representative candidate set: 2024 ACS 5-year.
* Artificial-light baseline: NASA VIIRS VNP46A4 Collection 2, 2024 annual radiance.
* Cloud forecast: NOAA/NWS forecast-grid skyCover.
* Sun/Moon geometry: PyEphem, calculated build-time.
* Public output: one compact JSON file. EARTHDATA_TOKEN never enters public output.

The ranking is explicitly among 100 representative Census places. It is a
MitchellCo heuristic, not an official astronomical forecast or a claim to rank
every possible observing site in the United States.
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
import re
import time
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

import ephem
import requests

from map26_darksky_prototype import (
    LAADS_BASE, UA, YEAR, addr, download, extract, granule, listing, value_at
)

CANDIDATES = Path("data/map26-candidate-places.json")
RADIANCE = Path("data/map26-radiance-baseline.json")
GRID_CACHE = Path("data/map26-nws-grid-map.json")
OUTPUT = Path("data/map26-tonight.json")
BENCH = Path("artifacts/map26-production-build.json")

CENSUS_GAZ_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/2025_Gaz_place_national.zip"
ACS_BASE = "https://api.census.gov/data/2024/acs/acs5"
CONTIGUOUS = {
    "AL","AZ","AR","CA","CO","CT","DE","DC","FL","GA","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA",
    "MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD",
    "TN","TX","UT","VT","VA","WA","WV","WI","WY"
}
EXTRA_ORDER = [
    ("TX", "Alpine"), ("NV", "Ely"), ("UT", "Moab"), ("TX", "Marfa"),
    ("CA", "Borrego Springs"), ("CA", "Joshua Tree"), ("TX", "Terlingua"), ("UT", "Torrey")
]
STATE_FIPS = {
    "AL":"01","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11","FL":"12","GA":"13",
    "ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21","LA":"22","ME":"23","MD":"24","MA":"25",
    "MI":"26","MN":"27","MS":"28","MO":"29","MT":"30","NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35",
    "NY":"36","NC":"37","ND":"38","OH":"39","OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46",
    "TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53","WV":"54","WI":"55","WY":"56"
}
WORKERS = 6


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def ms(t0):
    return round((time.perf_counter() - t0) * 1000, 1)


def clean_name(name: str) -> str:
    return re.sub(
        r"\s+(city and borough|consolidated government|metropolitan government|municipality|borough|city|town|village|CDP)$",
        "", name, flags=re.I
    ).strip()


def get_json(url, *, headers=None, attempts=4, timeout=40):
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers=headers or {"User-Agent": UA}, timeout=timeout)
            if r.status_code not in (429, 500, 502, 503, 504):
                r.raise_for_status()
                return r.json()
            last = RuntimeError(f"HTTP {r.status_code}: {url}")
        except Exception as e:
            last = e
        time.sleep(1.0 + 1.5 * i)
    raise last or RuntimeError(url)


def get_bytes(url, attempts=4):
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
            r.raise_for_status()
            return r.content
        except Exception as e:
            last = e
            time.sleep(1.0 + i)
    raise last or RuntimeError(url)


def load_gazetteer():
    raw = get_bytes(CENSUS_GAZ_URL)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        txt = next(n for n in zf.namelist() if n.lower().endswith(".txt"))
        text = zf.read(txt).decode("utf-8-sig")
    rows = []
    for r in csv.DictReader(io.StringIO(text), delimiter="|"):
        if r["USPS"] not in CONTIGUOUS:
            continue
        try:
            area = float(r["ALAND_SQMI"])
            lat = float(r["INTPTLAT"])
            lon = float(r["INTPTLONG"])
        except Exception:
            continue
        rows.append({
            "geoid": r["GEOID"],
            "state": r["USPS"],
            "official_name": r["NAME"],
            "name": clean_name(r["NAME"]),
            "lat": lat,
            "lon": lon,
            "land_sqmi": area,
            "lsad": r.get("LSAD"),
        })
    return rows


def populations_for_state(state_abbr):
    fips = STATE_FIPS[state_abbr]
    url = f"{ACS_BASE}?get=NAME,B01003_001E&for=place:*&in=state:{fips}"
    data = get_json(url)
    hdr = data[0]
    idx_pop = hdr.index("B01003_001E")
    idx_state = hdr.index("state")
    idx_place = hdr.index("place")
    out = {}
    for row in data[1:]:
        try:
            pop = int(row[idx_pop])
        except Exception:
            continue
        out[row[idx_state] + row[idx_place]] = pop
    return state_abbr, out


def make_candidates():
    rows = load_gazetteer()
    pop_by_geoid = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(populations_for_state, st) for st in sorted(CONTIGUOUS)]
        for fut in as_completed(futs):
            _, vals = fut.result()
            pop_by_geoid.update(vals)

    for r in rows:
        r["population_2024_acs5"] = pop_by_geoid.get(r["geoid"])
        pop = r["population_2024_acs5"]
        r["density_per_sqmi"] = None if pop is None or r["land_sqmi"] <= 0 else pop / r["land_sqmi"]

    by_state = defaultdict(list)
    for r in rows:
        if r["population_2024_acs5"] is not None:
            by_state[r["state"]].append(r)

    chosen = []
    used = set()
    for st in sorted(CONTIGUOUS):
        vals = by_state[st]
        if not vals:
            raise RuntimeError(f"No Census/ACS place candidates for {st}")

        major = max(vals, key=lambda x: x["population_2024_acs5"])
        chosen.append({**major, "candidate_type": "major"})
        used.add(major["geoid"])

        rural_pool = [
            x for x in vals
            if x["geoid"] not in used
            and 100 <= x["population_2024_acs5"] <= 10000
            and 0.25 <= x["land_sqmi"] <= 250
            and x["density_per_sqmi"] is not None
        ]
        if not rural_pool:
            rural_pool = [x for x in vals if x["geoid"] not in used and x["population_2024_acs5"] >= 100]
        rural = min(rural_pool, key=lambda x: (x["density_per_sqmi"] if x["density_per_sqmi"] is not None else 1e30, -x["land_sqmi"]))
        chosen.append({**rural, "candidate_type": "low_density"})
        used.add(rural["geoid"])

    # 48 contiguous states + DC = 49 jurisdictions => 98 places. Add two named,
    # Census-sourced western gateway places to reach exactly 100.
    by_key = {(r["state"], r["name"].lower()): r for r in rows}
    for st, name in EXTRA_ORDER:
        if len(chosen) >= 100:
            break
        r = by_key.get((st, name.lower()))
        if r and r["geoid"] not in used:
            chosen.append({**r, "candidate_type": "dark_sky_gateway"})
            used.add(r["geoid"])

    if len(chosen) != 100:
        raise RuntimeError(f"Expected 100 candidates, got {len(chosen)}")

    for i, p in enumerate(chosen, 1):
        p["id"] = f"US{i:03d}"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(chosen),
        "scope": "100 representative Census places in the contiguous United States and District of Columbia",
        "source_tags": ["US_CENSUS_GAZETTEER_2025", "US_CENSUS_ACS5_2024"],
        "selection_method": "Highest-population and low-density place per contiguous state/DC, plus two Census-sourced western gateway places.",
        "places": chosen,
    }
    CANDIDATES.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    return payload


def load_or_make_candidates():
    if CANDIDATES.exists():
        try:
            p = json.loads(CANDIDATES.read_text(encoding="utf-8"))
            if p.get("count") == 100 and len(p.get("places", [])) == 100:
                return p, True
        except Exception:
            pass
    return make_candidates(), False


def build_radiance_baseline(candidates, token):
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    html = listing(session)
    groups = defaultdict(list)
    for p in candidates:
        a = addr(p["lat"], p["lon"])
        groups[a.tile].append((p, a))

    cache = Path(".cache/map26-production-vnp46a4")
    cache.mkdir(parents=True, exist_ok=True)
    vals = {}
    total_bytes = 0
    for tile in sorted(groups):
        fname = granule(tile, html)
        path = download(fname, token, cache, session)
        total_bytes += path.stat().st_size
        for p, a in groups[tile]:
            rad, qa = extract(path, a)
            vals[p["id"]] = {
                "radiance_nw_cm2_sr": None if rad is None else round(rad, 4),
                "radiance_quality": qa,
                "tile": tile,
            }
        # Baseline is committed as tiny numeric JSON, so retaining multi-GB HDF5
        # tiles is unnecessary after the one-time annual extraction.
        try:
            path.unlink()
        except OSError:
            pass

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product": f"VNP46A4.{YEAR}.Collection2",
        "product_year": YEAR,
        "source_tag": "NASA_LAADS_VNP46A4",
        "candidate_signature": [p["geoid"] for p in candidates],
        "values": vals,
        "downloaded_hdf5_bytes": total_bytes,
    }
    RADIANCE.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    return payload, False


def load_or_make_radiance(candidates, token):
    sig = [p["geoid"] for p in candidates]
    if RADIANCE.exists():
        try:
            p = json.loads(RADIANCE.read_text(encoding="utf-8"))
            if p.get("product_year") == YEAR and p.get("candidate_signature") == sig and len(p.get("values", {})) == 100:
                return p, True
        except Exception:
            pass
    return build_radiance_baseline(candidates, token)


def resolve_grid(p):
    h = {"Accept": "application/geo+json", "User-Agent": UA}
    j = get_json(f"https://api.weather.gov/points/{p['lat']:.4f},{p['lon']:.4f}", headers=h)
    url = j.get("properties", {}).get("forecastGridData")
    if not url:
        raise RuntimeError("No forecastGridData")
    return p["id"], url


def load_or_make_grid_cache(candidates):
    sig = [p["geoid"] for p in candidates]
    if GRID_CACHE.exists():
        try:
            j = json.loads(GRID_CACHE.read_text(encoding="utf-8"))
            if j.get("candidate_signature") == sig and len(j.get("values", {})) == 100:
                return j["values"], True
        except Exception:
            pass

    vals = {}
    errors = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(resolve_grid, p): p["id"] for p in candidates}
        for fut in as_completed(futs):
            pid = futs[fut]
            try:
                k, v = fut.result()
                vals[k] = v
            except Exception as e:
                errors[pid] = f"{type(e).__name__}: {e}"
    if errors:
        raise RuntimeError(f"NWS point-resolution failures: {errors}")

    GRID_CACHE.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_tag": "NOAA_NWS_API",
        "candidate_signature": sig,
        "values": vals,
    }, separators=(",", ":")) + "\n", encoding="utf-8")
    return vals, False


def fetch_skycover(pid, url):
    h = {"Accept": "application/geo+json", "User-Agent": UA}
    j = get_json(url, headers=h)
    vals = j.get("properties", {}).get("skyCover", {}).get("values") or []
    if not vals:
        raise RuntimeError("No skyCover values")
    return pid, vals


def astronomy_sample(lat, lon, dt):
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.pressure = 0
    obs.date = dt.astimezone(timezone.utc).replace(tzinfo=None)
    sun = ephem.Sun(obs)
    moon = ephem.Moon(obs)
    return {
        "sun_alt_deg": math.degrees(float(sun.alt)),
        "moon_alt_deg": math.degrees(float(moon.alt)),
        "moon_illumination_percent": float(moon.phase),
    }


def light_score(rad):
    if rad is None:
        return None
    return clamp(100.0 - 30.0 * math.log10(1.0 + max(0.0, rad)))


def moon_score(illum, alt_deg):
    if alt_deg <= 0:
        return 100.0, 0.0
    altitude_factor = math.sqrt(max(0.0, math.sin(math.radians(alt_deg))))
    penalty = clamp(illum * altitude_factor)
    return 100.0 - penalty, penalty


def score_place(p, rad, sky_values, now):
    lscore = light_score(rad)
    if lscore is None:
        return None

    # Half-hour samples over the next 24 h. Only astronomical darkness
    # (Sun <= -18 degrees) participates in the ranking.
    start = now.replace(minute=0 if now.minute < 30 else 30, second=0, microsecond=0)
    samples = []
    for i in range(49):
        dt = start + timedelta(minutes=30 * i)
        astro = astronomy_sample(p["lat"], p["lon"], dt)
        if astro["sun_alt_deg"] > -18.0:
            continue
        cv = value_at(sky_values, dt)
        if cv is None:
            continue
        cloud = clamp(float(cv))
        mscore, mpen = moon_score(astro["moon_illumination_percent"], astro["moon_alt_deg"])
        core = 0.50 * lscore + 0.35 * (100.0 - cloud) + 0.15 * mscore
        samples.append({
            "time": dt,
            "cloud": cloud,
            "moon_alt": astro["moon_alt_deg"],
            "moon_illum": astro["moon_illumination_percent"],
            "moon_penalty": mpen,
            "core": core,
        })

    if not samples:
        return None

    dark_hours = len(samples) * 0.5
    dark_hours_score = clamp((dark_hours / 8.0) * 100.0)

    # Pick the best contiguous 3-hour (6 sample) window. If less than 3 hours
    # of forecast-covered astronomical darkness exist, use the longest available window.
    windows = []
    win_n = min(6, len(samples))
    for i in range(0, len(samples) - win_n + 1):
        w = samples[i:i + win_n]
        if len(w) > 1 and (w[-1]["time"] - w[0]["time"]) > timedelta(minutes=30 * (win_n - 1) + 1):
            continue
        avg_core = sum(x["core"] for x in w) / len(w)
        windows.append((avg_core, w))
    if not windows:
        return None
    best_core, best = max(windows, key=lambda x: x[0])
    final = clamp(0.90 * best_core + 0.10 * dark_hours_score)

    return {
        "score": math.floor(final * 10 + 0.5) / 10,
        "light_score": round(lscore, 1),
        "best_window_start_utc": best[0]["time"].isoformat(),
        "best_window_end_utc": (best[-1]["time"] + timedelta(minutes=30)).isoformat(),
        "best_window_cloud_percent": round(sum(x["cloud"] for x in best) / len(best), 1),
        "best_window_moon_penalty": round(sum(x["moon_penalty"] for x in best) / len(best), 1),
        "best_window_moon_alt_deg": round(sum(x["moon_alt"] for x in best) / len(best), 1),
        "moon_illumination_percent": round(sum(x["moon_illum"] for x in best) / len(best), 1),
        "astronomical_dark_hours": round(dark_hours, 1),
    }


def main():
    t_all = time.perf_counter()
    token = os.environ.get("EARTHDATA_TOKEN", "").strip()
    if not token:
        raise SystemExit("EARTHDATA_TOKEN is not set")
    timings = {}

    t = time.perf_counter()
    cand_payload, candidates_cached = load_or_make_candidates()
    candidates = cand_payload["places"]
    timings["candidate_load_or_build_ms"] = ms(t)

    t = time.perf_counter()
    rad_payload, radiance_cached = load_or_make_radiance(candidates, token)
    timings["radiance_load_or_build_ms"] = ms(t)

    t = time.perf_counter()
    grids, grid_cached = load_or_make_grid_cache(candidates)
    timings["nws_grid_load_or_build_ms"] = ms(t)

    t = time.perf_counter()
    sky = {}
    errors = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch_skycover, p["id"], grids[p["id"]]): p["id"] for p in candidates}
        for fut in as_completed(futs):
            pid = futs[fut]
            try:
                k, vals = fut.result()
                sky[k] = vals
            except Exception as e:
                errors[pid] = f"{type(e).__name__}: {e}"
    timings["nws_100_skycover_ms"] = ms(t)

    t = time.perf_counter()
    now = datetime.now(timezone.utc)
    results = []
    for p in candidates:
        pid = p["id"]
        rv = rad_payload["values"].get(pid, {})
        rad = rv.get("radiance_nw_cm2_sr")
        ranked = score_place(p, rad, sky.get(pid, []), now) if pid in sky else None
        row = {
            "id": pid,
            "name": p["name"],
            "official_name": p["official_name"],
            "state": p["state"],
            "candidate_type": p["candidate_type"],
            "lat": round(float(p["lat"]), 5),
            "lon": round(float(p["lon"]), 5),
            "population_2024_acs5": p.get("population_2024_acs5"),
            "radiance_nw_cm2_sr": rad,
            "radiance_quality": rv.get("radiance_quality"),
            "status": "ranked" if ranked else "unavailable",
        }
        if ranked:
            row.update(ranked)
        else:
            row["error"] = errors.get(pid, "Insufficient forecast-covered astronomical darkness")
        results.append(row)

    ranked_rows = sorted([x for x in results if x.get("score") is not None], key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(ranked_rows, 1):
        r["rank"] = i
    timings["astronomy_score_sort_ms"] = ms(t)

    payload = {
        "generated_at": now.isoformat(),
        "valid_for": "next 24 hours from generation time",
        "candidate_count": len(candidates),
        "ranked_count": len(ranked_rows),
        "scope": cand_payload["scope"],
        "source_tags": ["NASA_LAADS_VNP46A4", "NOAA_NWS_API", "US_CENSUS_GAZETTEER_2025", "US_CENSUS_ACS5_2024"],
        "method": {
            "name": "MitchellCo Tonight Score v2",
            "official": False,
            "description": "Ranks only the 100 representative Census places in this snapshot.",
            "astronomical_darkness": "Sun altitude <= -18 degrees",
            "window": "Best contiguous 3-hour forecast-covered astronomical-dark window",
            "core_weights": {"artificial_light": 0.50, "clear_sky": 0.35, "moon": 0.15},
            "final": "90% best-window core + 10% astronomical-dark-hours score",
            "light_transform": "100 - 30*log10(1 + VNP46A4 radiance), clamped 0..100",
            "moon_penalty": "Moon illumination percent multiplied by sqrt(sin(moon altitude)); zero below horizon",
        },
        "locations": results,
    }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")

    timings["total_ms"] = ms(t_all)
    bench = {
        "generated_at": now.isoformat(),
        "candidate_cached": candidates_cached,
        "radiance_cached": radiance_cached,
        "nws_grid_cached": grid_cached,
        "ranked_count": len(ranked_rows),
        "nws_failure_count": len(errors),
        "public_json_bytes": OUTPUT.stat().st_size,
        "timings_ms": timings,
        "best_10": [{"rank": x["rank"], "name": x["name"], "state": x["state"], "score": x["score"]} for x in ranked_rows[:10]],
        "worst_10": [{"rank": x["rank"], "name": x["name"], "state": x["state"], "score": x["score"]} for x in ranked_rows[-10:]],
        "errors": errors,
    }
    BENCH.parent.mkdir(parents=True, exist_ok=True)
    BENCH.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
    print("MAP26_PRODUCTION_BUILD=" + json.dumps(bench, separators=(",", ":")))


if __name__ == "__main__":
    main()
