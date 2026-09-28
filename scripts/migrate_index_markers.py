#!/usr/bin/env python3
import re
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"index.html"
s=p.read_text(encoding="utf-8")
if "GENERATED:MAP-LIST:START" not in s:
 pattern=r'(<nav\s+class="maplist"\s+aria-label="All maps"[^>]*>)(.*?)(</nav>)'
 m=re.search(pattern,s,re.S)
 if not m: raise SystemExit("map list nav not found")
 block=m.group(1)+"\n<!-- GENERATED:MAP-LIST:START -->\n"+m.group(2).strip()+"\n<!-- GENERATED:MAP-LIST:END -->\n"+m.group(3)
 s=s[:m.start()]+block+s[m.end():]
if "GENERATED:THEMES:START" not in s:
 start=re.search(r'<div\s+class="graph"[^>]*>',s)
 if not start: raise SystemExit("theme graph not found")
 note=s.find('<p class="note">',start.end())
 if note < 0: raise SystemExit("note after theme graph not found")
 segment=s[start.end():note]
 # The graph's final closing div is the last </div> before the note. Keep it outside the generated block.
 close=segment.rfind('</div>')
 if close < 0: raise SystemExit("theme graph closing div not found")
 body=segment[:close].strip()
 replacement=s[start.start():start.end()]+"\n<!-- GENERATED:THEMES:START -->\n"+body+"\n<!-- GENERATED:THEMES:END -->\n"+segment[close:]
 s=s[:start.start()]+replacement+s[note:]
p.write_text(s,encoding="utf-8")
