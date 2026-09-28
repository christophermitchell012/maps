#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import unquote
import hashlib, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'icons'
OUT.mkdir(parents=True, exist_ok=True)
# SVG data URIs are inside double-quoted href/src attributes. Internal SVG attrs use single quotes.
PAT = re.compile(r'(?P<prefix>\b(?:href|src)=")data:image/svg\+xml,(?P<data>[^"]+)"')
changed = 0
assets = {}
for p in sorted(ROOT.glob('*.html')):
    text = p.read_text(encoding='utf-8')
    def repl(m):
        raw = unquote(m.group('data'))
        if not raw.lstrip().startswith('<svg') or '</svg>' not in raw:
            raise SystemExit(f'invalid SVG data URI in {p.name}')
        raw = raw.strip()
        digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
        rel = f'assets/icons/{digest}.svg'
        target = ROOT / rel
        if target.exists() and target.read_text(encoding='utf-8') != raw:
            raise SystemExit(f'hash collision: {rel}')
        target.write_text(raw + '\n', encoding='utf-8')
        assets[rel] = raw
        return m.group('prefix') + rel + '"'
    new = PAT.sub(repl, text)
    if new != text:
        p.write_text(new, encoding='utf-8')
        changed += 1

remaining=[]
for p in ROOT.glob('*.html'):
    if 'data:image/svg+xml' in p.read_text(encoding='utf-8'):
        remaining.append(p.name)
if remaining:
    raise SystemExit('embedded SVG data URIs remain: ' + ', '.join(remaining))
for rel, raw in assets.items():
    if '<rect width="100%"' in raw or "<rect width='100%'" in raw:
        raise SystemExit(f'possible opaque full-canvas background in {rel}')
print(f'changed_html={changed} unique_svg_assets={len(assets)}')
