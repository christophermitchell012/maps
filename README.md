# MitchellCo Interactive Data Maps

Interactive, standalone public-data maps for weather, wildfire, earthquakes, drought, floods, geology, infrastructure, environment, public risk, space weather, aviation, marine conditions, volcanoes, astronomy context, and current events.

## Published collection

Browse the collection at:

https://christophermitchell012.github.io/maps/

The repository currently contains the collection index plus Maps 00 through 29:

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
- 21 Northern Hemisphere Snow & Ice Conditions
- 22 MarineWatch: U.S. Coastal Marine Conditions
- 23 VolcanoWatch: U.S. Volcano Alert & Aviation Impact
- 24 Deep Time Under Your Feet
- 25 Watershed Explorer | What's Upstream and Downstream?
- 26 Dark Sky Tonight
- 27 Your Compass Lies
- 28 Daylight Explorer | Where Is the Sun Right Now?
- 29 Groundwater Level & Drought Stress

## Repository architecture

Before publishing a new map, update its gallery row, map HTML, sitemap, README and source/license notes as one complete publication state. `python3 scripts/check_publication.py` checks gallery and sitemap coverage, canonical URLs, descriptions, same-origin links, and links between the map collection and the product blog. GitHub Actions runs that check read-only on publication-relevant pushes and pull requests.

Numbered map HTML files live at the repository root as `NN-map-name.html`.

Saved public-data snapshots and reusable geographic reference data live under `data/`. Maps should use same-origin relative paths such as `data/cdc-svi-2022-county.json`, `data/county-reference-2025-gazetteer-v1.json`, and `data/newspulse.json`.

Static, slow-changing, rate-limited, or browser-incompatible source data should be acquired and normalized at build time whenever practical, committed under `data/`, and loaded with relative same-origin paths. Runtime cross-origin requests should be reserved for sources with a clear anonymous/keyless browser-access contract and safe client fan-out. Do not use `daily-maps/` for new numbered maps.

## Current roadmap

The planned numbered series currently runs through Map 61. The next priority maps are:

- 30 River Ice Jam History & Current Conditions
- 31 Lightning Activity & Wildfire Ignition Potential
- 32 Tornado Climatology & Current Severe Weather Context
- 33 Hail Exposure & Crop/Property Risk

Later roadmap topics cover severe weather, drought, marine heatwaves, ports, dams, water stress, crop conditions, transportation, environmental exposure, infrastructure and multi-hazard synthesis. Global Aviation Weather & Airspace Conditions remains deferred until a browser-safe source or acceptable backend/build-time refresh architecture is available. BloomWatch remains deferred at the end of the numbered series until a clearly redistributable flowering-observation source contract is available. Global Landslide Hazard & Rainfall Trigger Watch has been moved to the bottom of the backlog because the preferred NASA LHASA anonymous download path is currently unreliable and the archive path conflicts with the zero-auth publication rule.

## Map 29 source contract

Groundwater Level & Drought Stress uses the USGS modern Water Data OGC API `latest-continuous` collection for parameter 72019, depth to water below land surface. Runtime requests are anonymous/keyless and only occur after an explicit user action at zoom level 5 or closer. The client caps each request at 500 records and enforces a 60-second cooldown; it does not poll or fetch automatically on map movement. USGS data are U.S. public domain. Raw depth-to-water values are displayed as measurements, not converted into a drought severity score, because drought interpretation requires each well's historical context. See `data/map29-source-license.md`.

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
