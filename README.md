# MitchellCo Interactive Data Maps

Interactive, standalone public-data maps for weather, wildfire, earthquakes, drought, floods, geology, infrastructure, environment, public risk, space weather, aviation, marine conditions, volcanoes, astronomy context, and current events.

## Published collection

Browse the collection at:

https://christophermitchell012.github.io/maps/

The repository currently contains the collection index plus Maps 00 through 27:

- 00 WildfireWatch
- 01 Flash Flood & River Flood Risk
- 02 Extreme Heat Health Risk
- 03 Wildfire Smoke Exposure
- 04 Hurricane & Storm Surge Impact
- 05 Breaking News Geography
- 06 Severe Storm & Tornado Exposure
- 07 Wildfire Evacuation Risk
- 08 Drought & Water Supply Stress
- 09 Power Grid Stress & Extreme Weather
- 10 Drinking Water Quality Risk
- 11 Internet Outage Watch
- 12 Coastal Flooding & High Tide Risk
- 13 Earthquake Impact
- 14 FEMA Disaster Declarations & Community Impact
- 15 General Air Quality Health Risk
- 16 Reservoir Water Shortage Monitor
- 17 Agricultural Drought & Farm Exposure
- 18 National Weather Alert Impact
- 19 Aurora & Geomagnetic Impact
- 20 Earthquake Shaking Impact
- 21 AirTrafficWatch: U.S. Airport Delay & NAS Impact
- 22 MarineWatch: U.S. Coastal Marine Conditions
- 23 VolcanoWatch: U.S. Volcano Alert & Aviation Impact
- 24 Deep Time Under Your Feet
- 25 Watershed Explorer | What's Upstream and Downstream?
- 26 Dark Sky Tonight
- 27 Your Compass Lies


## Repository architecture

Numbered map HTML files live at the repository root as `NN-map-name.html`.

Saved public-data snapshots and reusable geographic reference data live under `data/`. Maps should use same-origin relative paths such as `data/cdc-svi-2022-county.json`, `data/county-reference-2025-gazetteer-v1.json`, and `data/newspulse.json`.

Static, slow-changing, rate-limited, or browser-incompatible source data should be acquired and normalized at build time whenever practical, committed under `data/`, and loaded with relative same-origin paths. Runtime cross-origin requests should be reserved for sources with a clear anonymous/keyless browser-access contract and safe client fan-out. Do not use `daily-maps/` for new numbered maps.

## Current roadmap

The planned series currently runs through Map 61. The next priority maps are:

- 28 Global Aviation Weather & Airspace Conditions
- 29 Global Landslide Hazard & Rainfall Trigger Watch
- 30 Northern Hemisphere Snow & Ice Conditions
- 31 Groundwater Level & Drought Stress
- 32 River Ice Jam History & Current Conditions

Later roadmap topics cover river ice, lightning, severe weather, drought, marine heatwaves, ports, dams, water stress, crop conditions, transportation, environmental exposure, infrastructure and multi-hazard synthesis. BloomWatch has moved to Map 61 and remains deferred until a clearly redistributable flowering-observation source contract is available.

## Map 24 source contract

Deep Time Under Your Feet uses Macrostrat's public geologic map tiles and point-query API for mapped surface geology, with source definitions used for original-provider attribution when available. Macrostrat data and tiles are CC BY 4.0. Plate reconstruction uses the EarthByte GPlates Web Service. The map supports MERDITH2021 and MULLER2022 through 1,000 Ma and ZAHIROVIC2022 through 410 Ma, subject to the model's own coverage. Invalid reconstructed coordinates are rejected. Surface geology is explicitly not presented as subsurface geology at foundation, aquifer, tunnel or well depth.

## Map 25 source contract

Watershed Explorer uses the current USGS Network Linked Data Index at `api.water.usgs.gov/nldi/linked-data`. A click uses the `comid/position` endpoint to resolve a NHDPlusV2 network location, then requests an explicit-distance upstream trace (all tributaries or mainstem) and downstream mainstem flowlines. The default is 25 km; 10, 50 and 100 km are user-selectable, and unconstrained navigation is never requested. Responses are GeoJSON and repeated requests are cached only in the browser session. USGS-authored data and information are public domain in the United States and are credited to the U.S. Geological Survey. The map presents network connectivity only, not contaminant travel time, discharge, flood forecasting or proof of current flow.

## Map 26 source contract

Dark Sky Tonight uses NASA GIBS VIIRS Black Marble annual nighttime imagery at 2016-01-01 as a historical proxy for upward-emitted/artificial light, not direct sky brightness. NASA Earthdata states NASA-led mission data are generally CC0 unless specifically restricted and requests source acknowledgment. Current cloud context uses the anonymous NOAA/NWS `api.weather.gov` point and forecast-grid services for U.S. locations; NWS information is public domain unless specifically noted otherwise. Moon illumination and phase are calculated client-side from the current date. The displayed viewing rating is explicitly MitchellCo-derived from cloud cover and Moon illumination only, while artificial light remains a visual context layer rather than a falsely precise score.

## Map 27 source contract

Your Compass Lies uses the NOAA NCEI / British Geological Survey World Magnetic Model 2025 (WMM2025), degree and order 12. The exact coefficient file is committed at `data/WMM2025.COF` (pinned SHA-256 `06791cd95faba7bdf4a709808f2715a53fe689b29c23b9886bc2196fa9b3eb13`) and is loaded same-origin; no magnetic-model API is called at runtime. A normalized subset of NOAA's official WMM2025 test vectors is committed at `data/wmm2025-test-values.json`; the browser verifies six vectors before enabling calculations. Values are evaluated at 0 km height above the WGS84 ellipsoid. Declination is `atan2(Y,X)`, inclination is `atan2(Z,H)`, `H=sqrt(X²+Y²)`, and `F=sqrt(H²+Z²)`; secular variation comes from WMM2025's published annual coefficient changes. NOAA's surface declination uncertainty formula `sqrt(0.26² + (5417/H)²)` degrees is displayed. The map marks WMM caution areas where 2,000 ≤ H < 6,000 nT and blackout/unreliable areas where H < 2,000 nT. It explicitly warns that WMM omits local crustal and external-field anomalies and nearby magnetic interference.

## Site and search files

- `index.html` is the crawlable collection directory and should list every numbered map.
- `sitemap.xml` contains the index and every published numbered map.
- `robots.txt` points crawlers to the sitemap.
- `_config.yml` defines GitHub Pages metadata and the `/maps` base URL.
- `site.webmanifest` identifies the collection as MitchellCo Interactive Data Maps.
- `404.html` returns visitors to the collection index.
- `data/` contains saved public-data snapshots and supporting geographic data.

## Design goals

- Browser-first standalone HTML where practical
- Authoritative or explicitly approved public data sources
- Same-origin local snapshots for static/slow/rate-limited data
- No API keys, access credentials, or account-based runtime authentication
- No prohibited proprietary GIS platform dependencies
- Clear attribution and source links
- Consistent GA4 analytics using `G-8SVEH8WD1R`
- GitHub Pages friendly
- SEO metadata, canonical URLs, and crawlable internal links

## License

See [LICENSE](LICENSE).
