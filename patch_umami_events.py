# -*- coding: utf-8 -*-
"""Insert the delegated Umami interaction-tracking block (zip_submit / outbound / cta_click)
right after the Umami tag on every page that has the tag but predates the events block.
Idempotent (EVENTS_MARKER); validated (script-tag balance). Also patches gen_metro_base.html
so regenerated metros carry it.
"""
import glob
from plausible_snippet import EVENTS, EVENTS_MARKER, SCRIPT_ID

TAG = f'<script defer src="https://cloud.umami.is/script.js" data-website-id="{SCRIPT_ID}"></script>\n'

files = set(glob.glob('**/*.html', recursive=True)) | {'gen_metro_base.html'}
patched = skipped = notag = bad = 0
for f in sorted(files):
    html = open(f, encoding='utf-8').read()
    if EVENTS_MARKER in html:
        skipped += 1; continue
    if TAG not in html:
        notag += 1; continue
    out = html.replace(TAG, TAG + EVENTS, 1)
    if out.count('<script') != out.count('</script>'):
        print('BAD script balance, skipped:', f); bad += 1; continue
    open(f, 'w', encoding='utf-8').write(out)
    patched += 1
print(f'patched {patched}, already had events {skipped}, no umami tag {notag}, bad {bad}')
