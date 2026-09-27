#!/usr/bin/env python3
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"index.html"
s=p.read_text(encoding="utf-8")
if "GENERATED:MAP-LIST:START" not in s:
 s=s.replace('<nav class="maplist" aria-label="All maps">\n','<nav class="maplist" aria-label="All maps">\n<!-- GENERATED:MAP-LIST:START -->\n',1)
 s=s.replace("\n</nav></section>","\n<!-- GENERATED:MAP-LIST:END -->\n</nav></section>",1)
if "GENERATED:THEMES:START" not in s:
 marker='<section class="panel"><h2>Explore by theme</h2><p class="hint">Related maps grouped as a visual topic graph</p><div class="graph">\n'
 s=s.replace(marker,marker+"<!-- GENERATED:THEMES:START -->\n",1)
 s=s.replace('</div></section>\n</div>\n<p class="note">','<!-- GENERATED:THEMES:END -->\n</div></section>\n</div>\n<p class="note">',1)
p.write_text(s,encoding="utf-8")
