#!/usr/bin/env python3
"""Build the Map 31 same-origin snapshot from the NOAA SPC actual-tornado CSV.

Usage: python scripts/map31_build_snapshot.py path/to/1950-2025_actual_tornadoes.csv
Source: https://www.spc.noaa.gov/wcm/data/1950-2025_actual_tornadoes.csv
Only factual fields are kept: year, state, rating, start point, fatalities.
"""
import csv, json, sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(__file__).resolve().parents[1] / "data" / "map31-tornado-1950-2025-snapshot.json"
rows = list(csv.DictReader(src.open(newline="", encoding="utf-8-sig")))
states = sorted({r["st"] for r in rows})
idx = {s: i for i, s in enumerate(states)}
cols = {k: [] for k in ("y", "s", "m", "la", "lo", "f")}
dropped = 0
for r in rows:
    lat, lon = float(r["slat"]), float(r["slon"])
    if lat == 0 or lon == 0:
        dropped += 1
        continue
    cols["y"].append(int(r["yr"]) - 1950)
    cols["s"].append(idx[r["st"]])
    cols["m"].append(int(r["mag"]))          # -9 = unrated/unknown
    cols["la"].append(round(lat * 100))
    cols["lo"].append(round(lon * 100))
    cols["f"].append(int(r["fat"]))
last = max(r["date"] for r in rows)
data = {
    "source": "NOAA NWS Storm Prediction Center, 1950-2025_actual_tornadoes.csv",
    "source_url": "https://www.spc.noaa.gov/wcm/data/1950-2025_actual_tornadoes.csv",
    "snapshot_date": "2026-09-30",
    "last_event_date": last,
    "year0": 1950,
    "source_rows": len(rows),
    "dropped_no_start_point": dropped,
    "count": len(cols["y"]),
    "states": states,
    "scale": 100,
    **cols,
}
out.write_text(json.dumps(data, separators=(",", ":")))
print(out, out.stat().st_size, "bytes;", data["count"], "rows;", dropped, "dropped; last", last)
