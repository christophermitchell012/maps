#!/usr/bin/env python3
"""One-time helper: derive data/maps.json from the current index.html.

Run before generate_index.py when migrating an existing index. It extracts the
already-embedded SVG data URIs and descriptions so no artwork is regenerated.
"""
from __future__ import annotations
import html, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
text=(ROOT/'index.html').read_text(encoding='utf-8')
row_re=re.compile(r'<a class="maprow" data-map="(?P<id>\d+)" href="(?P<file>[^"]+)"><span class="num">.*?</span><span class="maptext"><span class="name"><img class="map-icon" src="(?P<icon>[^"]+)" alt="" aria-hidden="true">(?P<name>.*?)</span><span class="desc">(?P<desc>.*?)</span></span><span class="tag">(?P<tag>.*?)</span></a>',re.S)
maps=[]
for x in row_re.finditer(text):
 d=x.groupdict(); maps.append({'id':d['id'],'file':html.unescape(d['file']),'name':html.unescape(re.sub('<.*?>','',d['name'])),'description':html.unescape(re.sub('<.*?>','',d['desc'])),'tag':html.unescape(re.sub('<.*?>','',d['tag'])),'icon':html.unescape(d['icon'])})
if not maps: raise SystemExit('no map rows found')
# Existing visual grouping, kept explicit so changing a tag does not silently move a map.
themes=[
 {'class':'fire','name':'Fire & smoke','maps':['00','03','07']},
 {'class':'weather','name':'Weather & severe hazards','maps':['02','04','06','18','21']},
 {'class':'water','name':'Water, flood & drought','maps':['01','08','10','12','16','22','25']},
 {'class':'earth','name':'Earth & deep time','maps':['13','14','20','23','24','27']},
 {'class':'infra','name':'Infrastructure','maps':['09','11']},
 {'class':'env','name':'Environment & agriculture','maps':['15','17']},
 {'class':'space','name':'Space & sky','maps':['19','26','28']},
 {'class':'news','name':'News & current events','maps':['05']},
]
(ROOT/'data/maps.json').write_text(json.dumps({'maps':maps,'themes':themes},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(f'wrote {len(maps)} maps')
