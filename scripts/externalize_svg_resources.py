#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import unquote
import hashlib, html, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'icons'
OUT.mkdir(parents=True, exist_ok=True)
PAT = re.compile(r'(?P<prefix>\b(?:href|src)=")data:image/svg\+xml(?:;charset=utf-8|;utf8)?(?:;base64)?,(?P<data>[^"]+)"', re.I)
changed = 0
assets = {}
for p in sorted(ROOT.glob('*.html')):
    text = p.read_text(encoding='utf-8')
    def repl(m):
        payload = m.group('data')
        raw = html.unescape(unquote(payload)).strip()
        if not raw.lstrip().startswith('<svg'):
            raise SystemExit(f'not SVG markup in {p.name}: {raw[:60]!r}')
        if '</svg>' not in raw:
            raise SystemExit(f'incomplete SVG markup in {p.name}: {raw[:60]!r}')
        digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
        rel = f'assets/icons/{digest}.svg'
        target = ROOT / rel
        if target.exists() and target.read_text(encoding='utf-8').rstrip('\n') != raw:
            raise SystemExit(f'hash collision: {rel}')
        target.write_text(raw + '\n', encoding='utf-8')
        assets[rel] = raw
        return m.group('prefix') + rel + '"'
    new = PAT.sub(repl, text)
    if new != text:
        p.write_text(new, encoding='utf-8')
        changed += 1
remaining=[p.name for p in ROOT.glob('*.html') if 'data:image/svg+xml' in p.read_text(encoding='utf-8').lower()]
if remaining:
    raise SystemExit('embedded SVG data URIs remain: ' + ', '.join(remaining))
print(f'changed_html={changed} unique_svg_assets={len(assets)}')
