#!/usr/bin/env python3
from __future__ import annotations
import html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; INDEX=ROOT/"index.html"; DATA=ROOT/"data"/"maps.json"
LS="<!-- GENERATED:MAP-LIST:START -->"; LE="<!-- GENERATED:MAP-LIST:END -->"; TS="<!-- GENERATED:THEMES:START -->"; TE="<!-- GENERATED:THEMES:END -->"
def esc(s): return html.escape(str(s),quote=True)
def img(m): return f'<img class="map-icon" src="{esc(m["icon"])}" alt="" aria-hidden="true">'
def row(m): return f'<a class="maprow" data-map="{esc(m["id"])}" href="{esc(m["file"])}"><span class="num">{esc(m["id"])}</span><span class="maptext"><span class="name">{img(m)}{esc(m["name"])}</span><span class="desc">{esc(m["description"])}</span></span><span class="tag">{esc(m["tag"])}</span></a>'
def link(m): return f'<a data-map="{esc(m["id"])}" href="{esc(m["file"])}"><span>{esc(m["id"])}</span>{img(m)}{esc(m.get("theme_name",m["name"]))}</a>'
def repl(t,a,b,body):
 p=re.escape(a)+r".*?"+re.escape(b)
 if not re.search(p,t,re.S): raise SystemExit("missing generated markers")
 return re.sub(p,a+"\n"+body.rstrip()+"\n"+b,t,count=1,flags=re.S)
cfg=json.loads(DATA.read_text()); maps=sorted(cfg["maps"],key=lambda m:int(m["id"])); by={m["id"]:m for m in maps}
if len(by)!=len(maps): raise SystemExit("duplicate id")
for m in maps:
 if not (ROOT/m["file"]).exists(): raise SystemExit("missing "+m["file"])
t=INDEX.read_text(); t=repl(t,LS,LE,"\n".join(row(m) for m in maps))
groups=[f'<div class="group {esc(g["class"])}"><h3>{esc(g["name"])}</h3>{"".join(link(by[i]) for i in g["maps"])}</div>' for g in cfg["themes"]]
t=repl(t,TS,TE,"\n".join(groups)); t=re.sub(r"Explore \d+ interactive maps",f"Explore {len(maps)} interactive maps",t,count=1); INDEX.write_text(t)
