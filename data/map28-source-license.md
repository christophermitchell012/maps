# Map 28 — Daylight Explorer source and license record

## Methodological source

Map 28 uses an independent client-side implementation of solar-position and sunrise/sunset equations documented by NOAA Global Monitoring Laboratory (GML), based on Jean Meeus, *Astronomical Algorithms*. NOAA states that its Solar Calculator is no longer actively supported or maintained. NOAA gives theoretical sunrise/sunset accuracy of about one minute between ±72° latitude and about ten minutes outside that range, with observed times also affected by atmospheric conditions.

Source: https://gml.noaa.gov/grad/solcalc/calcdetails.html

NOAA GML states that information on its government servers is public domain unless specifically annotated otherwise and may be used freely subject to attribution/non-endorsement conditions.

Terms: https://gml.noaa.gov/about/disclaimer.html

## Derived calculations

All solar geometry is calculated in the browser. There are no solar-data runtime API calls. The map calculates the subsolar point, geometric day/night terminator, solar elevation and azimuth, solar noon, sunrise, sunset, day length, and civil/nautical/astronomical twilight. Sunrise/sunset uses the conventional −0.833° solar elevation. Twilight boundaries use −6°, −12°, and −18°. Polar day/night is explicitly reported when no crossing exists.

The map labels the calculations as MitchellCo-derived and does not present them as a NOAA product or certified astronomical data.

## Basemap and rendering

Basemap: OpenStreetMap standard raster tiles for normal interactive viewing, with visible © OpenStreetMap contributors attribution. No offline download or bulk prefetch is implemented.

Tile policy: https://operations.osmfoundation.org/policies/tiles/

Rendering library: Leaflet 1.9.4, BSD-2-Clause.

## Runtime and dependency contract

- Solar-data API calls: ZERO
- ArcGIS/Esri dependencies: ZERO
- Key/token/auth dependencies: ZERO
- Custom backend/API: ZERO
- Third-party CORS proxy: ZERO
- Topic SVG background: transparent
- Analytics: GA4 G-8SVEH8WD1R

Reviewed: 2026-09-26.
