# MitchellCo Maps

Interactive, standalone HTML maps built from public data sources.

## Map collection

The repository contains 21 numbered maps, beginning with **00 WildfireWatch** and continuing through Map 20. Browse the complete collection from [index.html](index.html), which lists every map numerically and groups related maps by theme.

- Fire and smoke
- Weather and severe hazards
- Water, flood and drought
- Earthquakes and disasters
- Infrastructure
- Environment and agriculture
- Space weather
- News and current events

The primary wildfire map is [00-wildfire-watch.html](00-wildfire-watch.html).

## Design goals

- Browser-first, standalone HTML where practical
- Public data sources
- No ArcGIS/Esri dependencies
- No API keys, tokens, or account-based runtime authentication
- Clear attribution and source links inside each map
- GitHub Pages friendly

## Repository files

- `index.html` searchable/crawlable map directory
- `00-wildfire-watch.html` through `20-earthquake-shaking-impact.html` map applications
- `robots.txt` and `sitemap.xml` for search-engine discovery
- `_config.yml` for GitHub Pages/Jekyll metadata
- `.gitignore` for local development artifacts
- `LICENSE` for repository licensing

## Publishing

GitHub Pages can serve this repository directly from the `main` branch. The collection index provides normal HTML links to every map so search crawlers and visitors can discover the individual pages.

## License

See [LICENSE](LICENSE).
