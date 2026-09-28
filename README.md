# MitchellCo Interactive Data Maps

Interactive, standalone public-data maps for weather, wildfire, earthquakes, drought, floods, geology, infrastructure, environment, public risk, space weather, marine conditions, astronomy context, and current events.

## Published collection

Browse: https://christophermitchell012.github.io/maps/

The repository contains Maps 00 through 30:

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
- 14 FEMA Disaster Declarations
- 15 Air Quality Health Risk
- 16 Reservoir Water Shortage Monitor
- 17 Agricultural Drought & Farm Exposure
- 18 National Weather Alert Impact
- 19 Aurora & Geomagnetic Impact
- 20 Earthquake Shaking Impact
- 21 Northern Hemisphere Snow & Ice Conditions
- 22 MarineWatch
- 23 VolcanoWatch
- 24 Deep Time Under Your Feet
- 25 Watershed Explorer
- 26 Dark Sky Tonight
- 27 Your Compass Lies
- 28 Daylight Explorer
- 29 Groundwater Level & Drought Stress
- 30 River Ice Jam History & Current Conditions

## Repository architecture

Numbered maps live at the repository root as `NN-map-name.html`. Saved snapshots and reusable reference data live under `data/`. Topic identity SVGs live under `assets/icons/` and are linked as resources rather than embedded in HTML.

Publication is intentionally simple: prepare the complete map/data/index/sitemap/docs state, run `python3 scripts/check_publication.py`, commit the coherent tree, then let the read-only publication Action validate it and GitHub Pages deploy the exact committed tree. Actions do not generate, commit, or push repository content.

Static, slow-changing, rate-limited, or browser-incompatible source data should be acquired and normalized at build time. Runtime cross-origin requests are reserved for authoritative anonymous/keyless browser-CORS sources with safe client fan-out.

## Current roadmap

Next candidates:
- 31 Lightning Activity & Wildfire Ignition Potential
- 32 Tornado Climatology & Current Severe Weather Context
- 33 Hail Exposure & Crop/Property Risk
- 34 High Wind & Infrastructure Exposure

Global Landslide Hazard & Rainfall Trigger Watch is at the bottom of the unnumbered backlog until a stable anonymous/keyless NASA LHASA path passes the source gate. Global Aviation Weather remains deferred. BloomWatch remains deferred until observation-record licensing/redistribution is clearly compatible with commercial/public reuse.

## Recent source contracts

- **Map 21:** U.S. National Ice Center IMS daily chart images, displayed directly; no snow-depth or ice-thickness claim.
- **Map 24:** Macrostrat surface geology plus EarthByte/GPlates reconstruction context.
- **Map 25:** USGS NLDI connected-flowline navigation with bounded distance.
- **Map 26:** NASA VIIRS Black Marble reference radiance, NOAA/NWS cloud forecast, and derived Sun/Moon context. Its build tooling may use the user-authorized `EARTHDATA_TOKEN`; the token is never published.
- **Map 27:** NOAA/BGS WMM2025 coefficients and official test vectors loaded same-origin.
- **Map 28:** Client-side solar geometry with no runtime weather claims.
- **Map 29:** USGS Water Data OGC `latest-continuous`, parameter 72019, loaded only on explicit user action; raw groundwater depth is not converted into a drought score.
- **Map 30:** USACE CRREL Ice Jam Database. The map uses a dated same-origin factual subset of the anonymous Water Year 2026 report. It is not a forecast, live closure feed, or exhaustive copy. See `data/map30-source-license.md`.

## Site/search files

`index.html` is the crawlable collection directory. `sitemap.xml` lists the index and every numbered map. `robots.txt` points to the sitemap. `_config.yml` defines the `/maps` base URL. `scripts/check_publication.py` is the read-only integrity checker and `scripts/build_sitemap.py` deterministically builds the sitemap.

## Design goals

- Browser-first standalone HTML where practical
- Authoritative or explicitly approved public sources
- Same-origin snapshots for static/slow/rate-limited data
- No credentials in public runtime code
- Zero prohibited proprietary GIS platform dependencies
- Clear attribution and source semantics
- GA4 `G-8SVEH8WD1R`
- GitHub Pages friendly and crawlable

## License

See [LICENSE](LICENSE).
