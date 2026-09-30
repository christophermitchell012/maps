# MitchellCo Maps: legacy URL redirects

The interactive map collection has moved to [mitchellcoinc.com/maps/](https://mitchellcoinc.com/maps/).

Authoritative publication repository: `christophermitchell012/mitchellcoinc`, directory `maps/`, branch `main`.

This repository remains online to preserve previously published URLs. Its HTML pages redirect to corresponding new pages using an immediate meta refresh and a canonical URL. JavaScript preserves query strings and URL fragments. GitHub Pages cannot supply configurable server-side 301 redirects here.

Historical data remains for cached old pages. Do not publish new map content or refresh snapshots in this repository. Original map source is preserved in Git history before the migration, commit `b5021a92f98e7e4bf87928bd760b6d56160b78ab`.

Validate redirects with `python3 scripts/check_publication.py`.
