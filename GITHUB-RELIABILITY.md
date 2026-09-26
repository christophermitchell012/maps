# GitHub publication reliability

## Publication model

Treat GitHub as the publication destination, not the editing workspace. Prepare and validate the complete map release before writing whenever possible.

A normal numbered-map release should be one logical push containing the new map, local data, `index.html`, regenerated `sitemap.xml`, README/source-license updates, and any supporting scripts. Avoid chains of temporary commits used only to mutate another file.

## Write rules

1. Batch related files into one commit/tree update where the available client supports it.
2. Do not write the same path concurrently. Fetch its current blob SHA immediately before replacement.
3. On HTTP 409 or 422, refresh the branch/file state and reconcile. Do not blind-retry.
4. On HTTP 429, honor `Retry-After`. On primary-rate exhaustion, wait until the reported reset time.
5. On secondary-rate responses, transient 5xx, or network failures, retry with jittered exponential backoff: approximately 60, 120, 240, then 480 seconds, stopping after four retries.
6. Record HTTP status, GitHub request ID, `Retry-After`, `x-ratelimit-remaining`, and `x-ratelimit-reset` whenever the client exposes them.
7. Run `python3 scripts/build_sitemap.py` and `python3 scripts/check_publication.py` before publication when a local/working checkout is available.
8. Keep SVG identity artwork embedded in the map HTML and index, per collection design. Do not create standalone icon files merely to simplify writes.

## Actions policy

Only one Pages deployment workflow is retained. It uses concurrency with `cancel-in-progress: true` so obsolete deployments do not queue behind newer releases. Documentation-only and workflow-only changes do not deploy Pages.

Publication validation runs only when site/publication files change and also cancels superseded checks on the same ref.

Do not add scheduled or frequent Actions for map data refresh without explicit approval. Do not add authenticated/token-dependent data acquisition to numbered maps under the current zero-auth architecture.

## Large-file handling

GitHub itself can handle the current repository and `index.html`; the practical risk is transport through clients that truncate large responses or require complete-file replacement. Keep `index.html` human-readable where practical, but preserve embedded SVGs. For surgical edits through a constrained client, prefer Git tree/blob operations or a complete verified replacement over reconstructing truncated content.

## Release sequence

1. Validate source, licensing, CORS/build-time architecture and zero-Esri/zero-auth requirements.
2. Build map and local data.
3. Update index, README and source/license documentation.
4. Regenerate sitemap.
5. Run publication and mechanical checks.
6. Inspect the complete diff.
7. Publish one logical commit/push.
8. Verify the commit, Actions result and live Pages output.
