# Map 30 source and reuse notes

## Source contract
- **Source:** U.S. Army Corps of Engineers, Cold Regions Research and Engineering Laboratory (CRREL), Ice Jam Database.
- **Official page:** https://icejam.sec.usace.army.mil/
- **Anonymous query used:** https://icejam.sec.usace.army.mil/ords/f?p=1001:2
- **Snapshot date:** 2026-09-28.
- **Source report:** Water Year 2026, 68 records reported by the official application.
- **Committed subset:** 20 factual records visible in the default anonymous report. This is not an exhaustive copy of the 68-record report.
- **Fields redistributed:** CRREL record/index number, city, state, river, jam date, water year, jam type, latitude, longitude, and recorded current condition. Narrative descriptions and damage prose are deliberately not redistributed.

## Semantics
The CRREL site describes the database as containing more than 18,000 current and historic U.S. ice-jam records and provides anonymous Text Query and Map View interfaces. Map 30 is a dated build-time snapshot, not a forecast and not a live closure feed. A record's `current condition` is the value recorded by CRREL for that event at source publication time.

## Reuse
USACE/CRREL is a U.S. federal government source. The map republishes only factual database fields rather than third-party narrative/source text. U.S. Government works are generally not subject to U.S. copyright under 17 U.S.C. §105; factual data are also not protected as original expression. MitchellCo attribution does not imply USACE endorsement.

## Architecture
No runtime CRREL API request is made. The browser loads the same-origin JSON snapshot. No account, API key, token, OAuth, signed URL, ArcGIS/Esri service, or CORS proxy is used.
