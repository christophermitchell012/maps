#!/usr/bin/env python3
"""Generate map-list and theme links in index.html from data/maps.json.

The existing index remains the visual template. The generator only replaces the
content between explicit generated markers, so CSS, header, footer, analytics,
and policy links remain hand-maintained and stable.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DATA = ROOT / "data" / "maps.json"
LIST_START = "<!-- GENERATED:MAP-LIST:START -->"
LIST_END = "<!-- GENERATED:MAP-LIST:END -->"
THEME_START = "<!-- GENERATED:THEMES:START -->"
THEME_END = "<!-- GENERATED:THEMES:END -->"

def esc(s): return html.escape(str(s), quote=True)

def img(m):
    return f'<img class="map-icon" src="{esc(m["icon"])}" alt="" aria-hidden="true">'

def map_row(m):
    return (f'<a class="maprow" data-map="{esc(m["id"])}" href="{esc(m["file"])}">'
            f'<span class="num">{esc(m["id"])}</span><span class="maptext"><span class="name">'
            f'{img(m)}{esc(m["name"])}</span><span class="desc">{esc(m["description"])}</span></span>'
            f'<span class="tag">{esc(m["tag"])}</span></a>')

def theme_link(m):
    label = m.get("theme_name", m["name"])
    return (f'<a data-map="{esc(m["id"])}" href="{esc(m["file"])}"><span>{esc(m["id"])}</span>'
            f'{img(m)}{esc(label)}</a>')

def replace_block(text, start, end, body):
    block = f"{start}\n{body.rstrip()}\n{end}"
    pattern = re.escape(start) + r".*?" + re.escape(end)
    if re.search(pattern, text, flags=re.S):
        return re.sub(pattern, block, text, count=1, flags=re.S)
    raise SystemExit(f"missing generated markers: {start} / {end}")

def main():
    cfg = json.loads(DATA.read_text(encoding="utf-8"))
    maps = sorted(cfg["maps"], key=lambda m: int(m["id"]))
    ids = [m["id"] for m in maps]
    if len(ids) != len(set(ids)): raise SystemExit("duplicate map id")
    files = [m["file"] for m in maps]
    if len(files) != len(set(files)): raise SystemExit("duplicate map file")
    for m in maps:
        if not (ROOT / m["file"]).exists(): raise SystemExit(f'missing map file: {m["file"]}')
    rows = "\n".join(map_row(m) for m in maps)
    by_id = {m["id"]: m for m in maps}
    groups = []
    for theme in cfg["themes"]:
        links = "".join(theme_link(by_id[i]) for i in theme["maps"])
        groups.append(f'<div class="group {esc(theme["class"])}"><h3>{esc(theme["name"])}</h3>{links}</div>')
    text = INDEX.read_text(encoding="utf-8")
    text = replace_block(text, LIST_START, LIST_END, rows)
    text = replace_block(text, THEME_START, THEME_END, "\n".join(groups))
    text = re.sub(r'Explore \d+ interactive maps', f'Explore {len(maps)} interactive maps', text, count=1)
    INDEX.write_text(text, encoding="utf-8")

if __name__ == "__main__": main()
