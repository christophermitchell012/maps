#!/usr/bin/env python3
"""Build the map sitemap from gallery links and the last meaningful git edit."""

import argparse
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://christophermitchell012.github.io/maps/"


class GalleryLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.maps = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and "maprow" in values.get("class", "").split():
            self.maps.append(values["href"])


def lastmod(path):
    result = subprocess.check_output(
        ["git", "log", "-1", "--format=%cs", "--", path], cwd=ROOT, text=True
    ).strip()
    if not result:
        raise ValueError(f"No committed history for {path}")
    return result


def build():
    parser = GalleryLinks()
    parser.feed((ROOT / "index.html").read_text())
    maps = parser.maps
    files = sorted(p.name for p in ROOT.glob("[0-9][0-9]-*.html"))
    if len(maps) != len(set(maps)) or sorted(maps) != files:
        raise ValueError("Gallery links and numbered map files differ")
    entries = [(BASE, "index.html")] + [(BASE + name, name) for name in maps]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, path in entries:
        lines.append(f"  <url><loc>{escape(url)}</loc><lastmod>{lastmod(path)}</lastmod></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--check", action="store_true", help="Fail if the committed sitemap is stale")
    options = args.parse_args()
    output = build()
    destination = ROOT / "sitemap.xml"
    if options.check:
        if destination.read_text() != output:
            raise SystemExit("sitemap.xml is stale; run python scripts/build_sitemap.py")
        print("sitemap.xml matches the gallery and committed pages")
    else:
        destination.write_text(output)
        print(f"Wrote {destination}")
