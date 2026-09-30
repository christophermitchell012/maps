#!/usr/bin/env python3
"""Check that all legacy redirect HTML has deployed."""
import concurrent.futures
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://christophermitchell012.github.io/maps/"
SHA = os.environ.get("GITHUB_SHA", "migration")

def verify(path):
    url = BASE + path.name + "?verify=" + SHA
    with urlopen(Request(url, headers={"User-Agent": "MitchellCo-Redirect-Check/1.0"}), timeout=30) as response:
        assert response.status == 200, url
        assert response.read() == path.read_bytes(), path.name
    return path.name

def main():
    for attempt in range(20):
        try:
            verify(ROOT / "index.html")
            break
        except Exception as error:
            print(f"Waiting for redirects ({attempt + 1}/20): {error}", flush=True)
            if attempt == 19:
                raise
            time.sleep(15)
    paths = sorted(ROOT.glob("*.html"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        verified = list(pool.map(verify, paths))
    print(f"PASS: all {len(verified)} legacy HTML redirects match the committed bytes")

if __name__ == "__main__":
    main()
