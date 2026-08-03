# -*- coding: utf-8 -*-
"""Strip now-dead CTA artifacts left by the CTA rollout, from article/** pages:
  - dead CSS: .zip-embed* / .article-email* / .email-*  (always, when block absent from body)
              .tooltiles/.tile*/.tbtn                    (only when no tooltiles block in body)
  - dead JS:  the supabase <script src> + the isolated email-handler <script> block
              (only when no .article-email block in body); the dead goZip("embedZipForm",...)
              call and the embedZipForm/embedZipInput/.article-email references in the sticky-cta.
Per-page and CONDITIONAL (never removes an artifact still used in that page's body), and each
result is validated (balanced <script>/<style>/<div>, critical tokens intact) before writing.
Run:  python3 strip_dead_cta.py --dry   then   python3 strip_dead_cta.py
"""
import re, glob, sys
from collections import Counter

DRY = '--dry' in sys.argv

# Rule-level (packing-agnostic): dead classes are always the leading token of their rule
# (verified — no compound "X .deadclass" selectors) and never appear with '{' outside CSS.
DEAD_EMAIL_CSS = re.compile(r'\.(?:article-email|email-row|email-input|email-select|email-btn|email-zip|email-month|email-thanks)[^{}]*\{[^{}]*\}')
DEAD_EMBED_CSS = re.compile(r'\.zip-embed[^{}]*\{[^{}]*\}')
DEAD_TILES_CSS = re.compile(r'(?m)^[ \t]*\.tooltiles\{.*$\n?')
SUPA_SRC = re.compile(r'[ \t]*<script src="https://cdn\.jsdelivr\.net/npm/@supabase[^"]*"></script>\n?')
SUPA_BLOCK = re.compile(r'[ \t]*<script>(?:(?!</script>).)*?supabase\.createClient(?:(?!</script>).)*?</script>\n?', re.S)
STICKY_AE = re.compile(r'[ \t]*var ae=document\.querySelector\("\.article-email"\);if\(ae\)targets\.push\(ae\);\n?')

def strip(path, html):
    # detect body blocks tolerant of trailing attributes (e.g. class="article-email" id="...")
    has_email = '<div class="article-email"' in html
    has_embed = '<div class="zip-embed"' in html
    has_tiles = '<div class="tooltiles"' in html
    out = html
    if not has_email:
        out = SUPA_SRC.sub('', out)
        out = SUPA_BLOCK.sub('', out)
        out = DEAD_EMAIL_CSS.sub('', out)
        out = STICKY_AE.sub('', out)
    if not has_embed:
        out = DEAD_EMBED_CSS.sub('', out)
        out = out.replace('.zip-embed{padding:22px 18px;}', '')
        out = out.replace('goZip("embedZipForm","embedZipInput");', '')
        out = out.replace('["zipBarForm","embedZipForm"]', '["zipBarForm"]')
        out = out.replace('document.getElementById("zipBarInput")||document.getElementById("embedZipInput")',
                          'document.getElementById("zipBarInput")')
    if not has_tiles:
        out = DEAD_TILES_CSS.sub('', out)
    if out == html:
        return ('no-change', None)
    # ---- validate: nothing structural broken; live JS not lost (RELATIVE to before) ----
    if out.count('<script') != out.count('</script>'): return ('bad-script-balance', None)
    if out.count('<style') != out.count('</style>'):   return ('bad-style-balance', None)
    if out.count('<div') != out.count('</div>'):       return ('bad-div-balance', None)
    for tok in ('function goZip', 'id="zipBarForm"', 'id="navMega"', 'id="articleStickyCta"'):
        if (tok in html) != (tok in out): return ('bad-lost:' + tok, None)
    if not has_email and ('supabase.createClient' in out or 'articleEmailBtn' in out):
        return ('bad-email-residue', None)
    return ('stripped', out)

def main():
    files = sorted(glob.glob('article/**/*.html', recursive=True))
    c = Counter(); bad = []
    for f in files:
        html = open(f, encoding='utf-8').read()
        status, out = strip(f, html)
        c[status] += 1
        if status.startswith('bad'): bad.append((status, f))
        elif status == 'stripped' and not DRY:
            open(f, 'w', encoding='utf-8').write(out)
    print('MODE:', 'DRY' if DRY else 'LIVE', '| files:', len(files))
    for k, v in sorted(c.items()): print(f'  {k}: {v}')
    if bad:
        print('!!! NOT WRITTEN (validation failed):')
        for s, f in bad: print('  ', s, f)

if __name__ == '__main__':
    main()
