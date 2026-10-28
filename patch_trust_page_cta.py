#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add one inline ZIP CTA to the three trust pages that had none.

WHY. In the 2026-10-28 Umami pull, 55 of 210 US tool entries arrived WITHOUT a
?zip= and so had to type one on arrival. Only 16 of those came from pages with no
inline ZIP form at all; the rest came from pages that have one. Auditing the whole
site found just 6 pages lacking an entry point, three of which ARE the tool. That
left about.html, methodology.html and editorial-standards.html.

This is a small fix - roughly 6 entries a quarter - and it is deliberately the LAST
of the CTA work, not the start of more. The conversion layer is otherwise done:
74% of entries already carry a ZIP and 26% of ranking-viewers click a carrier.

Appends after the closing </article>, inserts its own scoped <style> (these pages
carry no .rz-zip CSS), touches no existing block, and is idempotent.

  python3 patch_trust_page_cta.py --apply
"""
import sys

PAGES = {
 'methodology.html':        'See what this model estimates for your ZIP:',
 'about.html':              'See what we estimate for your ZIP:',
 'editorial-standards.html':'See the rankings for your ZIP:',
}

CSS = ('<style>/* trust-page-cta */\n'
       '.tp-zip{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:8px auto 48px;padding:14px 18px;'
       'max-width:660px;background:var(--paper-deep);border:1px solid var(--rule);}\n'
       '.tp-zip-label{font-family:var(--sans);font-size:15px;font-weight:600;color:var(--ink);}\n'
       '.tp-zip form{display:flex;gap:8px;margin:0;}\n'
       '.tp-zip input{font-family:var(--mono);font-size:14px;padding:8px 10px;border:1px solid var(--rule);'
       'background:var(--paper);color:var(--ink);width:92px;}\n'
       '.tp-zip button{font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;'
       'padding:8px 16px;background:var(--accent);color:var(--paper);border:none;cursor:pointer;white-space:nowrap;}\n'
       '.tp-zip button:hover{opacity:0.9;}\n'
       '@media (max-width:480px){.tp-zip{flex-direction:column;align-items:flex-start;}}\n'
       '</style>\n')

def block(label):
    return ('\n<div class="tp-zip"><span class="tp-zip-label">' + label + '</span>'
            '<form onsubmit="event.preventDefault();'
            "var z=(this.zc.value||'').replace(/\\D/g,'').slice(0,5);"
            "if(/^\\d{5}$/.test(z)){location.href='/?zip='+z}else{this.zc.focus()}\">"
            '<input name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" '
            'aria-label="ZIP code" />'
            '<button type="submit">Compare &rarr;</button></form></div>\n')

def main():
    apply = '--apply' in sys.argv
    for f, label in PAGES.items():
        s = open(f, encoding='utf-8').read()
        if 'tp-zip' in s:
            print(f'  {f:28} already patched'); continue
        i = s.rfind('</article>')
        if i < 0:
            print(f'  {f:28} SKIP (no </article>)'); continue
        out = s[:i + len('</article>')] + block(label) + s[i + len('</article>'):]
        k = out.find('</head>')
        out = out[:k] + CSS + out[k:]
        if apply:
            open(f, 'w', encoding='utf-8').write(out)
        print(f'  {f:28} {"patched" if apply else "would patch"}')
    print(f'\n{"APPLIED" if apply else "DRY RUN"}')

if __name__ == '__main__':
    main()
