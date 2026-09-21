# MitchellCo Interactive Data Maps

Interactive, standalone public-data maps for weather, wildfire, earthquakes, drought, floods, infrastructure, environment, public risk, space weather, aviation, marine conditions, volcanoes, and current events.

## Published collection

Browse the collection at:

https://christophermitchell012.github.io/maps/

The repository currently contains the collection index plus Maps 00 through 23:

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

## Repository architecture

Numbered map HTML files live at the repository root:

`NN-map-name.html`

Saved public-data snapshots and reusable geographic reference data live under:

`data/`

Maps should use same-origin relative paths such as:

`data/cdc-svi-2022-county.json`

`data/county-reference-2025-gazetteer-v1.json`

`data/county-geometry-2025-cb20m-v1-*.geojson`

`data/newspulse.json`

`data/newspulse-state.json`

Static or slow-changing authoritative source data should be acquired and normalized at build time whenever practical, committed under `data/`, and loaded with relative same-origin paths. Runtime cross-origin requests should be reserved for sources with a clear anonymous/keyless browser CORS contract. Do not use `daily-maps/` for new numbered maps.

## Site and search files

- `index.html` is the crawlable collection directory and should list every numbered map in the repository.
- `sitemap.xml` contains the index and every published numbered map.
- `robots.txt` points crawlers to the sitemap.
- `_config.yml` defines GitHub Pages metadata and the `/maps` base URL.
- `site.webmanifest` identifies the collection as MitchellCo Interactive Data Maps.
- `404.html` returns visitors to the collection index.
- `data/` contains saved public-data snapshots and supporting geographic data used by maps.

## Design goals

- Browser-first standalone HTML where practical
- Authoritative public data sources
- Same-origin local snapshots for static/slow-changing data
- No API keys, tokens, or account-based runtime authentication
- No ArcGIS/Esri dependencies
- Clear attribution and source links
- Consistent GA4 analytics using `G-8SVEH8WD1R`
- GitHub Pages friendly
- SEO metadata, canonical URLs, and crawlable internal links

## License

See [LICENSE](LICENSE).
