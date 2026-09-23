#!/usr/bin/env python3
"""Map 26 dark-sky three-location prototype.

Build-time only. Reads EARTHDATA_TOKEN from the environment, downloads the
annual VNP46A4 tiles needed for Austin, Big Bend and New York City, extracts
AllAngle_Composite_Snow_Free radiance + QA, queries NWS skyCover, computes the
same Moon model as Map 26, and emits JSON. The token is never written to output.
"""
from __future__ import annotations
import json, math, os, re, subprocess, tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
import h5py, requests

LAADS_BASE="https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A4"
YEAR=2024
N=2400
DEG=10.0
UA="MitchellCo-Map26-Prototype/0.2 (+https://christophermitchell012.github.io/maps/)"
RAD="AllAngle_Composite_Snow_Free"
QA="AllAngle_Composite_Snow_Free_Quality"
LOCATIONS={"Austin":(30.2672,-97.7431),"Big Bend":(29.25,-103.25),"New York City":(40.7128,-74.0060)}

@dataclass(frozen=True)
class Addr:
    tile:str; row:int; col:int

def addr(lat,lon):
    lon=min(lon,180-1e-12); lat=max(lat,-90+1e-12)
    h=int(math.floor((lon+180)/DEG)); v=int(math.floor((90-lat)/DEG))
    west=-180+h*DEG; north=90-v*DEG
    col=int((lon-west)/DEG*N); row=int((north-lat)/DEG*N)
    return Addr(f"h{h:02d}v{v:02d}",max(0,min(N-1,row)),max(0,min(N-1,col)))

def target_tonight(lon, now=None):
    now=now or datetime.now(timezone.utc)
    off=timedelta(hours=lon/15)
    local=now+off
    t=datetime(local.year,local.month,local.day,22,tzinfo=timezone.utc)-off
    return t+timedelta(days=1) if t<now-timedelta(hours=1) else t

def moon(dt):
    syn=29.530588853; known=datetime(2000,1,6,18,14,tzinfo=timezone.utc)
    age=((dt-known).total_seconds()/86400)%syn
    frac=(1-math.cos(2*math.pi*age/syn))/2
    names=[(1.85,"New Moon"),(5.54,"Waxing Crescent"),(9.23,"First Quarter"),(12.92,"Waxing Gibbous"),(16.61,"Full Moon"),(20.30,"Waning Gibbous"),(23.99,"Last Quarter"),(27.68,"Waning Crescent"),(99,"New Moon")]
    return round(frac*100), next(n for x,n in names if age<x)

def duration_hours(s):
    m=re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?",s)
    if not m: raise ValueError(s)
    d,h,mi,se=(int(x or 0) for x in m.groups())
    return d*24+h+mi/60+se/3600

def value_at(values,target):
    for it in values or []:
        if "/" not in it.get("validTime",""): continue
        a,b=it["validTime"].split("/",1)
        st=datetime.fromisoformat(a.replace("Z","+00:00")).astimezone(timezone.utc)
        if st<=target<st+timedelta(hours=duration_hours(b)): return it.get("value")
    return None

def find_ds(h5, base):
    out=[]
    h5.visititems(lambda name,obj: out.append(obj) if isinstance(obj,h5py.Dataset) and name.rsplit("/",1)[-1]==base else None)
    if len(out)!=1: raise KeyError(f"{base}: found {len(out)}")
    return out[0]

def _scalar(v, default=None):
    if v is None: return default
    if hasattr(v, "reshape"):
        arr=v.reshape(-1)
        return arr[0].item() if hasattr(arr[0], "item") else arr[0]
    if isinstance(v,(list,tuple)):
        return v[0] if v else default
    return v

def extract(path,a):
    with h5py.File(path,"r") as h5:
        r=find_ds(h5,RAD); q=find_ds(h5,QA)
        raw=_scalar(r[a.row,a.col]); fill=_scalar(r.attrs.get("_FillValue"))
        scale=float(_scalar(r.attrs.get("scale_factor"),1.0))
        offset=float(_scalar(r.attrs.get("offset"),0.0))
        rv=None if fill is not None and int(raw)==int(fill) else float(raw)*scale+offset
        qr=_scalar(q[a.row,a.col]); qfill=_scalar(q.attrs.get("_FillValue"))
        qv=None if qfill is not None and int(qr)==int(qfill) else int(qr)
        return rv,qv

def listing(session):
    r=session.get(f"{LAADS_BASE}/{YEAR}/001/",timeout=30); r.raise_for_status(); return r.text

def granule(tile,html):
    m=sorted(set(re.findall(rf"VNP46A4\.A{YEAR}001\.{tile}\.002\.\d{{13}}\.h5",html)))
    if not m: raise RuntimeError(f"No granule for {tile}")
    return m[-1]

def download(name,token,cache,session):
    p=cache/name
    if p.exists() and p.stat().st_size>1024*1024 and h5py.is_hdf5(p): return p
    if p.exists(): p.unlink()
    url=f"{LAADS_BASE}/{YEAR}/001/{name}"
    # NASA LAADS documents EDL-token downloads with curl -L -b session.
    # Feed the config over stdin so the token never appears in argv or output.
    cfg=(
        "location\n"
        "fail\n"
        "silent\n"
        "show-error\n"
        'cookie = "session"\n'
        f'header = "Authorization: Bearer {token.strip()}"\n'
        f'url = "{url}"\n'
        f'output = "{p}"\n'
    )
    cp=subprocess.run(["curl","--config","-"],input=cfg,text=True,capture_output=True)
    if cp.returncode:
        raise RuntimeError("NASA curl download failed: "+cp.stderr.strip()[-500:])
    if not p.exists() or not h5py.is_hdf5(p):
        if p.exists(): p.unlink()
        raise RuntimeError("NASA response was not a valid HDF5 file")
    return p

def nws(lat,lon,target,session):
    h={"Accept":"application/geo+json","User-Agent":UA}
    p=session.get(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}",headers=h,timeout=30); p.raise_for_status()
    g=session.get(p.json()["properties"]["forecastGridData"],headers=h,timeout=30); g.raise_for_status()
    v=value_at(g.json()["properties"]["skyCover"]["values"],target)
    if v is None: raise RuntimeError("No skyCover for target time")
    return max(0,min(100,float(v)))

def score(rad,cloud,moonpct):
    lp=max(0,min(100,25*math.log10(1+max(0,rad))))
    raw=max(0,min(100,100-(.55*lp+.35*cloud+.10*moonpct)))
    # Match JavaScript Math.round semantics for positive scores.
    return math.floor(raw*10+0.5)/10

def self_test():
    exp={"Austin":("h08v05",2335,541),"Big Bend":("h07v06",180,1620),"New York City":("h10v04",2228,1438)}
    for n,(lat,lon) in LOCATIONS.items():
        a=addr(lat,lon); assert (a.tile,a.row,a.col)==exp[n],(n,a)
    print("SELF-TEST PASS")

def main():
    self_test()
    token=os.environ.get("EARTHDATA_TOKEN")
    if not token: raise SystemExit("EARTHDATA_TOKEN is not set")
    cache=Path(".cache/map26-vnp46a4"); cache.mkdir(parents=True,exist_ok=True)
    s=requests.Session(); s.headers.update({"User-Agent":UA})
    html=listing(s)
    out=[]
    for name,(lat,lon) in LOCATIONS.items():
        a=addr(lat,lon); target=target_tonight(lon); mp,phase=moon(target)
        fname=granule(a.tile,html)
        path=download(fname,token,cache,s)
        rad,qa=extract(path,a)
        cloud=nws(lat,lon,target,s)
        out.append({"name":name,"lat":lat,"lon":lon,"tile":a.tile,"row":a.row,"col":a.col,
                    "radiance_nw_cm2_sr":None if rad is None else round(rad,4),
                    "radiance_quality":qa,"cloud_percent":round(cloud,1),
                    "moon_illumination_percent":mp,"moon_phase":phase,
                    "target_time_utc":target.isoformat(),
                    "prototype_score":None if rad is None else score(rad,cloud,mp)})
    out.sort(key=lambda x: -1 if x["prototype_score"] is None else x["prototype_score"],reverse=True)
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),"product":f"VNP46A4.{YEAR}.Collection2",
             "note":"Prototype only. VIIRS upward-emitted radiance is not a Bortle or zenith sky-brightness measurement.","results":out}
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/map26-three-location-test.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2))

if __name__=="__main__": main()
