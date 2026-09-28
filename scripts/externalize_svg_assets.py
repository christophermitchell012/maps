#!/usr/bin/env python3
"""Externalize embedded SVG assets from all root HTML pages.

- Converts data:image/svg+xml URLs to assets/icons/<sha>.svg resource links.
- Converts static inline <svg>...</svg> markup outside <script> blocks to <img> resource links.
- Deduplicates identical SVG artwork by SHA-256 content hash.
- Leaves JavaScript strings/templates untouched.
- Fails if any HTML still contains an SVG data URI after conversion.
"""
from __future__ import annotations
import hashlib, html, re
from pathlib import Path
from urllib.parse import unquote_to_bytes

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "icons"
ASSETS.mkdir(parents=True, exist_ok=True)
DATA_RE = re.compile(r"data:image/svg\+xml(?:;charset=[^;,]+)?(?:;base64)?,[^\"'\s)>]+", re.I)
SCRIPT_RE = re.compile(r"(<script\b[^>]*>.*?</script\s*>)", re.I | re.S)
INLINE_RE = re.compile(r"<svg\b([^>]*)>(.*?)</svg\s*>", re.I | re.S)

def normalize_svg(raw: bytes) -> str:
    s = raw.decode("utf-8").strip()
    if not s.lower().startswith("<svg"):
        raise ValueError("decoded SVG data URI does not start with <svg")
    return s + ("\n" if not s.endswith("\n") else "")

def save(svg: str) -> str:
    digest = hashlib.sha256(svg.encode("utf-8")).hexdigest()[:16]
    rel = f"assets/icons/{digest}.svg"
    p = ROOT / rel
    if not p.exists(): p.write_text(svg, encoding="utf-8")
    return rel

def decode_data_uri(uri: str) -> str:
    head, payload = uri.split(",", 1)
    if ";base64" in head.lower():
        import base64
        raw = base64.b64decode(payload)
    else:
        raw = unquote_to_bytes(payload)
    return normalize_svg(raw)

def replace_data(text: str) -> str:
    return DATA_RE.sub(lambda m: save(decode_data_uri(m.group(0))), text)

def inline_to_img(m: re.Match) -> str:
    attrs, body = m.group(1), m.group(2)
    svg = f"<svg{attrs}>{body}</svg>\n"
    rel = save(svg)
    cls = re.search(r'\bclass=["\']([^"\']+)["\']', attrs, re.I)
    title = re.search(r'<title\b[^>]*>(.*?)</title>', body, re.I | re.S)
    out = [f'src="{html.escape(rel, quote=True)}"']
    if cls: out.append(f'class="{html.escape(cls.group(1), quote=True)}"')
    if title: out.append(f'alt="{html.escape(re.sub(r"<.*?>", "", title.group(1)).strip(), quote=True)}"')
    else: out.append('alt="" aria-hidden="true"')
    return "<img " + " ".join(out) + ">"

def replace_static_inline(text: str) -> str:
    parts = SCRIPT_RE.split(text)
    for i in range(0, len(parts), 2):
        parts[i] = INLINE_RE.sub(inline_to_img, parts[i])
    return "".join(parts)

def main() -> None:
    changed=[]
    for p in sorted(ROOT.glob("*.html")):
        old=p.read_text(encoding="utf-8")
        new=replace_data(old)
        new=replace_static_inline(new)
        if new != old:
            p.write_text(new, encoding="utf-8")
            changed.append(p.name)
    failures=[]
    for p in sorted(ROOT.glob("*.html")):
        s=p.read_text(encoding="utf-8")
        if re.search(r"data:image/svg\+xml", s, re.I): failures.append(f"{p.name}: SVG data URI remains")
        # Static inline SVG outside scripts is prohibited. Script-held SVG may be functional rendering code.
        parts=SCRIPT_RE.split(s)
        if any(re.search(r"<svg\b", parts[i], re.I) for i in range(0,len(parts),2)):
            failures.append(f"{p.name}: static inline SVG remains")
    if failures: raise SystemExit("\n".join(failures))
    print(f"externalized SVGs in {len(changed)} HTML files; assets={len(list(ASSETS.glob('*.svg')))}")

if __name__ == "__main__": main()
