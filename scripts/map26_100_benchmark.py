#!/usr/bin/env python3
"""Map 26 100-location build/performance prototype.

Purpose:
- benchmark build-time NASA VNP46A4 + NWS acquisition for 100 deterministic U.S. test points
- write one small public JSON file for browser-side performance testing
- keep all Earthdata authentication build-time only

The 100 points are algorithmically generated test coordinates, not a curated public
observing-location recommendation set.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

from map26_darksky_prototype import (
    LAADS_BASE, LOCATIONS, RAD, QA, UA, YEAR,
    addr, download, extract, granule, listing, moon, score, target_tonight, value_at
)

MAX_NWS_WORKERS = 6
OUT = Path("data/map26-100-prototype.json")
ARTIFACT = Path("artifacts/map26-100-python-benchmark.json")
GRID_CACHE = Path("data/map26-100-nws-grid-map.json")


def ms(t0: float) -> float:
    return round((time.perf_counter() - t0) * 1000, 1)


def grid_points(region: str, lats: list[float], lons: list[float], start: int) -> list[dict]:
    out = []
    n = start
    for lat in lats:
        for lon in lons:
            out.append({
                "id": f"P{n:03d}",
                "name": f"{region} {n:03d}",
                "region": region,
                "lat": round(lat, 4),
                "lon": round(lon, 4),
            })
            n += 1
    return out


def make_points() -> list[dict]:
    # All coordinates are intentionally inside broad U.S. regions with NWS coverage.
    # They are synthetic benchmark points so no third-party place-name dataset is introduced.
    pts = []
    pts += grid_points(
        "Central Texas",
        [30.25, 30.75, 31.25, 31.75, 32.25],
        [-99.75, -99.25, -98.75, -98.25, -97.75, -97.25, -96.75, -96.25],
        1,
    )  # 40
    pts += grid_points(
        "New Mexico",
        [32.25, 32.75, 33.25, 33.75, 34.25],
        [-105.75, -105.25, -104.75, -104.25, -103.75, -103.25],
        41,
    )  # 30
    pts += grid_points(
        "Northeast",
        [40.50, 40.85, 41.20, 41.55, 41.90],
        [-76.25, -75.95, -75.65, -75.35, -75.05, -74.75],
        71,
    )  # 30
    assert len(pts) == 100
    return pts


def retry_get(url: str, headers: dict, attempts: int = 3, timeout: int = 30) -> requests.Response:
    last = None
    for i in range(attempts):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code not in (429, 500, 502, 503, 504):
                r.raise_for_status()
                return r
            last = RuntimeError(f"HTTP {r.status_code} for {url}")
        except Exception as e:
            last = e
        time.sleep(1.0 + i * 1.5)
    raise last or RuntimeError(f"request failed: {url}")


def resolve_grid(point: dict) -> tuple[str, str]:
    h = {"Accept": "application/geo+json", "User-Agent": UA}
    url = f"https://api.weather.gov/points/{point['lat']:.4f},{point['lon']:.4f}"
    r = retry_get(url, h)
    grid = r.json().get("properties", {}).get("forecastGridData")
    if not grid:
        raise RuntimeError("No forecastGridData")
    return point["id"], grid


def fetch_cloud(point: dict, grid_url: str, target) -> tuple[str, float]:
    h = {"Accept": "application/geo+json", "User-Agent": UA}
    r = retry_get(grid_url, h)
    vals = r.json().get("properties", {}).get("skyCover", {}).get("values")
    v = value_at(vals, target)
    if v is None:
        raise RuntimeError("No skyCover value for target time")
    return point["id"], max(0.0, min(100.0, float(v)))


def parallel_map(fn, items, workers=MAX_NWS_WORKERS):
    results, errors = {}, {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(fn, *args): key for key, args in items}
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                k, value = fut.result()
                results[k] = value
            except Exception as e:
                errors[key] = f"{type(e).__name__}: {e}"
    return results, errors


def main():
    token = os.environ.get("EARTHDATA_TOKEN", "").strip()
    if not token:
        raise SystemExit("EARTHDATA_TOKEN is not set")

    total0 = time.perf_counter()
    timings = {}

    t0 = time.perf_counter()
    points = make_points()
    for p in points:
        a = addr(p["lat"], p["lon"])
        p["tile"], p["row"], p["col"] = a.tile, a.row, a.col
        target = target_tonight(p["lon"])
        mp, phase = moon(target)
        p["_target"] = target
        p["target_time_utc"] = target.isoformat()
        p["moon_illumination_percent"] = mp
        p["moon_phase"] = phase
    timings["generate_points_and_moon_ms"] = ms(t0)

    unique_tiles = sorted({p["tile"] for p in points})

    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    t0 = time.perf_counter()
    html = listing(session)
    tile_files = {tile: granule(tile, html) for tile in unique_tiles}
    timings["laads_listing_and_granule_discovery_ms"] = ms(t0)

    cache = Path(".cache/map26-vnp46a4")
    cache.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    tile_paths = {}
    for tile in unique_tiles:
        tile_paths[tile] = download(tile_files[tile], token, cache, session)
    timings["nasa_tile_download_or_cache_ms"] = ms(t0)
    nasa_bytes = sum(p.stat().st_size for p in tile_paths.values())

    t0 = time.perf_counter()
    for p in points:
        rad, qa = extract(tile_paths[p["tile"]], addr(p["lat"], p["lon"]))
        p["radiance_nw_cm2_sr"] = None if rad is None else round(rad, 4)
        p["radiance_quality"] = qa
    timings["extract_100_radiance_pixels_ms"] = ms(t0)

    # NWS /points -> forecastGridData mapping is much more stable than the forecast.
    # Persist it so normal refreshes can skip 100 point-resolution requests.
    t0 = time.perf_counter()
    grids, grid_errors, grid_cache_hit = {}, {}, False
    if GRID_CACHE.exists():
        try:
            cached = json.loads(GRID_CACHE.read_text(encoding="utf-8"))
            entries = cached.get("locations", [])
            by_id = {x["id"]: x for x in entries}
            if len(by_id) == len(points) and all(
                pid in by_id
                and abs(float(by_id[pid]["lat"]) - float(pt["lat"])) < 1e-8
                and abs(float(by_id[pid]["lon"]) - float(pt["lon"])) < 1e-8
                and by_id[pid].get("forecast_grid_url")
                for pid, pt in ((p["id"], p) for p in points)
            ):
                grids = {pid: by_id[pid]["forecast_grid_url"] for pid in by_id}
                grid_cache_hit = True
        except Exception:
            grids = {}
    if not grid_cache_hit:
        resolve_items = [(p["id"], (p,)) for p in points]
        grids, grid_errors = parallel_map(resolve_grid, resolve_items)
        if len(grids) == len(points):
            GRID_CACHE.parent.mkdir(parents=True, exist_ok=True)
            GRID_CACHE.write_text(json.dumps({
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_tag": "NOAA_NWS_API",
                "note": "Build-time cache of NWS /points forecastGridData mappings for synthetic Map 26 benchmark points.",
                "locations": [
                    {"id": p["id"], "lat": p["lat"], "lon": p["lon"], "forecast_grid_url": grids[p["id"]]}
                    for p in points
                ],
            }, separators=(",", ":")) + "\n", encoding="utf-8")
    timings["nws_resolve_100_grid_urls_ms"] = ms(t0)

    t0 = time.perf_counter()
    cloud_items = []
    for p in points:
        if p["id"] in grids:
            cloud_items.append((p["id"], (p, grids[p["id"]], p["_target"])))
    clouds, cloud_errors = parallel_map(fetch_cloud, cloud_items)
    timings["nws_fetch_100_skycover_forecasts_ms"] = ms(t0)

    t0 = time.perf_counter()
    failures = []
    for p in points:
        pid = p["id"]
        cloud = clouds.get(pid)
        p["cloud_percent"] = None if cloud is None else round(cloud, 1)
        if pid in grid_errors or pid in cloud_errors:
            failures.append({
                "id": pid,
                "grid_error": grid_errors.get(pid),
                "cloud_error": cloud_errors.get(pid),
            })
        rad = p["radiance_nw_cm2_sr"]
        p["prototype_score"] = (
            None if rad is None or cloud is None
            else score(rad, cloud, p["moon_illumination_percent"])
        )
        p.pop("_target", None)
    ranked = [p for p in points if p["prototype_score"] is not None]
    ranked.sort(key=lambda p: p["prototype_score"], reverse=True)
    timings["score_and_sort_100_ms"] = ms(t0)

    public = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prototype": True,
        "purpose": "100-point performance prototype; synthetic benchmark coordinates, not curated observing-site recommendations.",
        "source_tags": [
            "NASA_LAADS_VNP46A4",
            "NOAA_NWS_API",
        ],
        "product": f"VNP46A4.{YEAR}.Collection2",
        "product_year": YEAR,
        "locations": points,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    compact = json.dumps(public, separators=(",", ":"), ensure_ascii=False)
    OUT.write_text(compact + "\n", encoding="utf-8")

    timings["total_build_ms"] = ms(total0)
    bench = {
        "generated_at": public["generated_at"],
        "location_count": len(points),
        "rankable_count": len(ranked),
        "nws_failure_count": len(failures),
        "nws_grid_cache_hit": grid_cache_hit,
        "unique_nasa_tiles": unique_tiles,
        "unique_nasa_tile_count": len(unique_tiles),
        "nasa_hdf5_bytes": nasa_bytes,
        "public_json_bytes": OUT.stat().st_size,
        "timings_ms": timings,
        "best_5_prototype": [
            {"id": p["id"], "region": p["region"], "score": p["prototype_score"], "radiance": p["radiance_nw_cm2_sr"], "cloud": p["cloud_percent"]}
            for p in ranked[:5]
        ],
        "worst_5_prototype": [
            {"id": p["id"], "region": p["region"], "score": p["prototype_score"], "radiance": p["radiance_nw_cm2_sr"], "cloud": p["cloud_percent"]}
            for p in ranked[-5:]
        ],
        "failures": failures,
    }

    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(bench, indent=2) + "\n", encoding="utf-8")
    print("MAP26_100_BENCHMARK=" + json.dumps(bench, separators=(",", ":")))


if __name__ == "__main__":
    main()
