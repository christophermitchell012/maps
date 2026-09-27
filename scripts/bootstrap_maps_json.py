#!/usr/bin/env python3
import html,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
text=(root/"index.html").read_text(encoding="utf-8")
pattern=re.compile(r'<a class="maprow" data-map="(?P<id>\d+)" href="(?P<file>[^"]+)"><span class="num">.*?</span><span class="maptext"><span class="name"><img class="map-icon" src="(?P<icon>[^"]+)" alt="" aria-hidden="true">(?P<name>.*?)</span><span class="desc">(?P<description>.*?)</span></span><span class="tag">(?P<tag>.*?)</span></a>',re.S)
maps=[]
for match in pattern.finditer(text):
 d=match.groupdict()
 maps.append({k:html.unescape(re.sub("<.*?>","",v)) for k,v in d.items()})
if not maps: raise SystemExit("no map rows found")
themes=[
 {"class":"fire","name":"Fire & smoke","maps":["00","03","07"]},
 {"class":"weather","name":"Weather & severe hazards","maps":["02","04","06","18","21"]},
 {"class":"water","name":"Water, flood & drought","maps":["01","08","10","12","16","22","25"]},
 {"class":"earth","name":"Earth & deep time","maps":["13","14","20","23","24","27"]},
 {"class":"infra","name":"Infrastructure","maps":["09","11"]},
 {"class":"env","name":"Environment & agriculture","maps":["15","17"]},
 {"class":"space","name":"Space & sky","maps":["19","26","28"]},
 {"class":"news","name":"News & current events","maps":["05"]}]
(root/"data/maps.json").write_text(json.dumps({"maps":maps,"themes":themes},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("wrote",len(maps),"maps")
