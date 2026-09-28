# Map 29 source and license memo

## Groundwater Level & Drought Stress

Primary runtime source: U.S. Geological Survey modern Water Data OGC API, version 1, `latest-continuous` collection. The map requests parameter code `72019`, defined by USGS as depth to water level in feet below land surface, and restricts results to groundwater sites (`site_type_code=GW`) in the current map bounding box.

USGS documents these APIs as anonymously accessible; credentials increase rate limits rather than being required for basic access. To avoid unsafe client fan-out, Map 29 performs zero automatic data requests. A user must zoom to level 5 or closer and explicitly press **Load wells in view**. Requests are limited to 500 records and the browser enforces a 60-second cooldown. There is no polling, pan/zoom-triggered fetching, proxy, backend, credential, or secret placeholder.

USGS states data provided by the Water Data APIs are U.S. Government work in the public domain. USGS attribution is retained. The basemap is OpenStreetMap standard tiles with required contributor attribution; Leaflet 1.9.4 provides map rendering.

Parameter 72019 is a raw depth measurement, not a drought index. Well depth-to-water values are not directly comparable across different aquifers, geology, land-surface elevations, or well constructions. The map deliberately does not convert raw depth into a drought severity score. USGS/NGWMN historical percentile methods are cited as the appropriate conceptual framework for interpreting groundwater conditions relative to a site's own record.

References: USGS Water Data OGC API documentation, USGS rate-limit documentation, USGS parameter-code documentation, NGWMN statistics methods, and USGS public-domain guidance. Checked 2026-09-28.

ArcGIS/Esri dependencies: ZERO. Key/token/auth dependencies: ZERO.
