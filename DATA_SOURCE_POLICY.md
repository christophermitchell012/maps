# MitchellCo public-map data source policy

Last reviewed: 2026-09-23

Operational release policy for public MitchellCo HTML maps. This is not legal advice. Live source terms must be re-checked when a source, product, license, EULA, or delivery mechanism changes.

## Release gate

Every published data layer must declare a `source` tag and a data year/acquisition year when the source requires one.

- **ALLOWED**: may publish when required attribution, license links, notices, and product-specific conditions are present.
- **BLOCKED**: do not publish.
- **NEEDS_CLEARANCE**: do not publish until the open question is resolved.
- **UNKNOWN / UNCLASSIFIED**: fail closed. Do not publish until reviewed.

Never remove or obscure notices embedded in a product. Never imply endorsement by NASA, NOAA/NWS, ESA, JAXA, METI, OSMF, or another source organization.

## Earthdata EULA acceptance status supplied by account owner

Accepted as of 2026-09-23:
- Sentinel EULA
- OB.DAAC ESA EULA for Sentinel-3 Data Use
- NASA GESDISC DATA ARCHIVE
- GLIMS Download Service
- TOLNet
- MERIS EULA (previously accepted)

Deliberately not accepted:
- ASF-family EULAs
- SmallSats EULAs
- maap-auth
- Envisat EULA
- SEDAC entries
- test / placeholder EULAs

Do not silently accept an EULA as part of map generation.

## Source registry


### US_CENSUS_GAZETTEER_2025
Status: **ALLOWED**

Use: 2025 U.S. Census Bureau Gazetteer place names and representative latitude/longitude coordinates.

Public-map rules:
- Identify the U.S. Census Bureau and the 2025 Gazetteer as the source.
- Link to the official Gazetteer page and current Census website/API policies.
- Do not imply Census Bureau endorsement.
- Use the geographic data only at aggregate place level. Do not combine Census data in a way intended to identify an individual, household, business, or respondent.

### US_CENSUS_ACS5_2024
Status: **ALLOWED**

Use: 2024 American Community Survey 5-year place population (B01003_001E) solely to construct the 100-place representative candidate set.

Public-map rules:
- Identify the U.S. Census Bureau, ACS 2024 5-year estimate, and variable purpose.
- Do not present the ACS population as current real-time population.
- Follow Census API terms prohibiting attempts to identify individual respondents or establishments.
- Do not imply Census Bureau endorsement.

### NASA_LAADS_VNP46A4
Status: **ALLOWED**

Use: VIIRS/NPP Lunar BRDF-Adjusted Nighttime Lights Yearly L3 Global 15 arc-second grid, Collection 2.

Public-map rules:
- Earthdata token may be used only at build time.
- Never write the token into HTML, JavaScript, JSON, logs, URLs, or committed files.
- Cite the actual product year separately from the publication/citation year.
- Describe VIIRS radiance as upward-emitted/nighttime radiance, not a Bortle class or direct zenith sky-brightness measurement.
- Include the DOI and full dataset citation on the public data-sources page.
- State that derived MitchellCo scores are not NASA products and do not imply NASA endorsement.

Current Map 26 prototype:
- Product year: 2024
- Collection: 2
- DOI: https://doi.org/10.5067/VIIRS/VNP46A4.002

### NASA_GIBS_WORLDVIEW_BLACK_MARBLE_2016
Status: **ALLOWED WITH ATTRIBUTION / MEDIA-USE CAUTION**

Use: GIBS/Worldview rendered Black Marble annual 2016 imagery.

Public-map rules:
- Visible map attribution: `NASA Worldview / GIBS · Suomi NPP/VIIRS via NASA Earth Observatory · Black Marble 2016`.
- Link to the NASA Worldview imagery-use guidance and NASA media-usage guidance on the data-sources page.
- Do not use NASA insignia, logotype, seal, or other NASA branding as MitchellCo branding.
- Do not imply NASA endorsement, partnership, certification, or approval.
- If a NASA-hosted image/product is separately marked as third-party copyrighted, do not assume NASA's general imagery guidance grants reuse rights.
- Preserve all notices carried by the source.

### NOAA_NWS_API
Status: **ALLOWED**

Public-map rules:
- Identify forecast values as NOAA/NWS source data.
- Do not present derived MitchellCo displays as official NWS products.
- Preserve source timestamps.
- State that internet delivery is not guaranteed.
- Link to the NWS API documentation and disclaimer.
- No NOAA/NWS logo or visual identifier unless separately authorized.

### OSM_STANDARD_TILES
Status: **ALLOWED SUBJECT TO TILE POLICY**

Public-map rules:
- Visible attribution: `© OpenStreetMap contributors`.
- Link to https://www.openstreetmap.org/copyright so the ODbL terms are clear.
- Use the canonical HTTPS tile URL.
- Do not bulk download, prefetch, or provide offline tile-download functionality.
- Honor browser caching and normal Referer behavior.
- Treat availability as best-effort; high-traffic production use may require another OSM-derived tile provider or self-hosting.

### LEAFLET_1_9_4
Status: **ALLOWED**

License: BSD-2-Clause.

Public-map rules:
- Keep a Leaflet acknowledgment/link in the public data-sources page.
- Tile/data-provider terms remain independent of Leaflet's software license.

### COPERNICUS_SENTINEL
Status: **ALLOWED WITH REQUIRED NOTICE**

Unmodified: `Copernicus Sentinel data [Year]`

Modified/adapted: `Contains modified Copernicus Sentinel data [Year]`

For Copernicus Service Information use the equivalent service-information wording. Fill the year from the actual data.

### GLIMS
Status: **ALLOWED WITH CREDIT**

General citation:
Raup, B.H.; A. Racoviteanu; S.J.S. Khalsa; C. Helm; R. Armstrong; Y. Arnaud (2007). "The GLIMS Geospatial Glacier Database: a New Tool for Studying Glacier Change". Global and Planetary Change 56:101-110. doi:10.1016/j.gloplacha.2006.07.018

Complete dataset:
GLIMS Consortium, 2005. GLIMS Glacier Database, Version 1. Boulder Colorado, USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. DOI: https://doi.org/10.7265/N5V98602 [Date accessed].

### TOLNET
Status: **ALLOWED WITH ACKNOWLEDGMENT**

Acknowledge TOLNet as the data source. Re-check current terms before first public use because applying publication wording to an interactive map is an inference.

### ASF_FAMILY
Status: **NEEDS_CLEARANCE**

Do not publish ASF-sourced layers until the scope of the International Polar Year restrictions is resolved with ASF. The reviewed bundle contains noncommercial and redistribution restrictions for IPY Data Pool material. Do not assume those restrictions apply only to a subset without written clarification.

ALOS-specific notes within the ASF bundle, if separately cleared:
- Standard/Derivative: `©JAXA,METI [Year]`
- Value Added: `Includes Material ©JAXA,METI [Year]`
- RTC: preserve existing NASA copyright notice

### SMALLSATS_CSDA
Status: **NEEDS_CLEARANCE / BLOCKED FOR PUBLIC RELEASE**

Do not publish licensed commercial SmallSat material or derivatives to a public website unless the applicable licensor/NASA terms explicitly permit it and any release restrictions have been resolved.

### MAAP_AUTH
Status: **NEEDS_CLEARANCE**

Do not use the MAAP platform for a commercial public-map workflow without written clearance.

### ESA_ENVISAT
Status: **NEEDS_CLEARANCE**

If cleared, credit:
- `Data provided by the European Space Agency.`
- `© ESA [year of reception]`

### SEDAC
Status: **UNKNOWN / NEEDS REVIEW**

Do not publish until the specific SEDAC permissions/terms for the intended dataset have been reviewed.

### TEST_PLACEHOLDER_OR_SIMULATED
Status: **BLOCKED FOR REAL CONTENT**

Includes TEMPO/ASDC early-adopter proxy or simulated data and placeholder/test entries such as VCFW Test, DB Direct, MIIC at ASDC, Contingency app, ASTER Free Data placeholder, OB.DAAC Data Access placeholder, Keyword Manager, kms, Hyrax Test Mule, and AESICS registered-user-only placeholder entries.

## Public-page attribution standard

For every map:
1. Keep concise, visible attribution in the map control.
2. Add a clearly linked **Data sources and licenses** page with full citations, direct source links, product/version/year, license/EULA notes, and non-endorsement language.
3. State when a score, ranking, transformation, or interpretation is MitchellCo-derived.
4. Include the source data timestamp or vintage where it affects interpretation.
5. Prefer over-attribution to under-attribution.
