# -*- coding: utf-8 -*-
"""One-time swap: Plausible -> Umami across every page.
  - replace the Plausible <script src> + window.plausible init block with the Umami tag
  - drop the old "analytics by Plausible" comment
  - remap the event call window.plausible(name,{props}) -> window.umami.track(name, props)
    on the 3 tool pages (index / home / renters), keeping the window.track layer intact
Exact-string replacements (markup is byte-identical across all 603 pages), validated per file.
Run:  python3 migrate_to_umami.py --dry   then   python3 migrate_to_umami.py
"""
import glob, sys
from collections import Counter

DRY = '--dry' in sys.argv

OLD_COMMENT = "<!-- Privacy-friendly analytics by Plausible -->\n"
OLD_CORE = (
    '<script async src="https://plausible.io/js/pa-v219GyiG5lJT1bQSRxP_Z.js"></script>\n'
    "<script>\n"
    "  window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};\n"
    "  plausible.init()\n"
    "</script>\n"
)
NEW_SNIPPET = (
    "<!-- Privacy-friendly analytics by Umami -->\n"
    '<script defer src="https://cloud.umami.is/script.js" data-website-id="ce2e7f7c-eb06-4865-9d46-70143943e9b6"></script>\n'
)
OLD_CALL = "try { window.plausible(name, { props: ev.props }); } catch (e) {}"
NEW_CALL = "try { if (window.umami) window.umami.track(name, ev.props); } catch (e) {}"

WEBSITE_ID = "ce2e7f7c-eb06-4865-9d46-70143943e9b6"


# prose / JS-comment mentions of the tool name (keep the copy accurate post-swap)
EXTRA = [
    ("cookieless analytics (Plausible)", "cookieless analytics (Umami)"),
    ("Plausible transport live", "Umami transport live"),
    ("broken down by landing page type in Plausible.", "broken down by landing page type in Umami."),
]


def migrate(html):
    out = html.replace(OLD_COMMENT, "")
    out = out.replace(OLD_CORE, NEW_SNIPPET)
    out = out.replace(OLD_CALL, NEW_CALL)
    for old, new in EXTRA:
        out = out.replace(old, new)
    if out == html:
        return ('no-change', None)
    # validate: no plausible residue, umami present, structure intact
    if 'plausible' in out.lower():                 return ('bad-plausible-residue', None)
    if WEBSITE_ID not in out:                       return ('bad-no-umami', None)
    if out.count('<script') != out.count('</script>'): return ('bad-script-balance', None)
    if out.count('<div') != out.count('</div>'):    return ('bad-div-balance', None)
    return ('migrated', out)


def main():
    files = sorted(glob.glob('**/*.html', recursive=True))
    c = Counter(); bad = []; toolpages = []
    for f in files:
        html = open(f, encoding='utf-8').read()
        status, out = migrate(html)
        c[status] += 1
        if status.startswith('bad'): bad.append((status, f))
        if out and 'window.umami.track' in out: toolpages.append(f)
        if status == 'migrated' and not DRY:
            open(f, 'w', encoding='utf-8').write(out)
    print('MODE:', 'DRY' if DRY else 'LIVE', '| files:', len(files))
    for k, v in sorted(c.items()): print(f'  {k}: {v}')
    print('event-firing (tool) pages remapped:', toolpages)
    if bad:
        print('!!! NOT WRITTEN:')
        for s, f in bad: print('  ', s, f)


if __name__ == '__main__':
    main()
