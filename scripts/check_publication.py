#!/usr/bin/env python3
"""Validate legacy redirect destinations without modifying files."""
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://mitchellcoinc.com/maps/"

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.refresh = []
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href"))
        if tag == "meta" and values.get("http-equiv") == "refresh":
            self.refresh.append(values.get("content"))

def main():
    files = sorted(ROOT.glob("*.html"))
    for path in files:
        target = BASE if path.name in ("index.html", "404.html") else BASE + path.name
        page = Page()
        page.feed(path.read_text())
        assert page.canonicals == [target], path
        assert page.refresh == ["0;url=" + target], path
        assert "location.search + location.hash" in path.read_text(), path
    print(f"Validated {len(files)} legacy redirects")

if __name__ == "__main__":
    main()
