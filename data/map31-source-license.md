# Map 31 source and reuse notes

## Source contract
- **Source:** NOAA National Weather Service, Storm Prediction Center (SPC), Severe Weather Database "actual tornadoes" file.
- **File:** `1950-2025_actual_tornadoes.csv` (73,458 rows), https://www.spc.noaa.gov/wcm/data/1950-2025_actual_tornadoes.csv
- **Data page:** https://www.spc.noaa.gov/wcm/#data
- **Snapshot date:** 2026-09-30. Latest event in the file: 2025-12-28. SHA-256 of the downloaded CSV: `2b2679ead1920ab96eaa390baeb41aeeaeef49d067f613dfcc5e233403b82d76`.
- **Fields redistributed:** year, state, F/EF rating (-9 = unrated), start latitude/longitude (rounded to 0.01 degree), fatalities. Nothing else from the file is copied. Every row in the file had a usable start point, so none were dropped.
- **Rebuild:** `python scripts/map31_build_snapshot.py <csv>` writes `data/map31-tornado-1950-2025-snapshot.json`.

## Live layer
The page requests active alerts from the NWS API (`https://api.weather.gov/alerts/active?event=Tornado Warning,Tornado Watch`) in the visitor's browser. No key, account, proxy or MitchellCo backend is involved, and nothing from it is stored. If the request fails, the page says so and the historical map still works. CORS behavior of the NWS API was not verified in a browser before publication.

## Semantics
- Each tornado is counted once, at its start point. Counts are for 1-degree squares and are not population- or area-adjusted.
- The record is not uniform: detection improved over time, the EF scale replaced the F scale in 2007, and recent years are preliminary. The page states this.
- No forecast, risk score or live-safety claim is made. Warnings shown are as returned by NWS at page load.

## Reuse
SPC/NWS data are U.S. federal government works, generally not subject to U.S. copyright under 17 U.S.C. section 105. MitchellCo attribution does not imply NOAA or NWS endorsement.
