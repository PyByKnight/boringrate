#!/usr/bin/env python3
"""Single source of the analytics snippet + an idempotent inserter.

Provider: **Umami** (Umami Cloud) as of 2026-08-03 — swapped from Plausible. Filename kept as
plausible_snippet.py so the ~8 generators + patch_plausible.py that import it are unaffected
(rename is a possible later cleanup). Umami auto-tracks pageviews from the tag; custom events use
window.umami.track(name, props) via the window.track layer on the tool pages.

Generators that emit their own <head> (home/renters/press/rate-filings) call ensure() at write
time so the snippet is baked in natively — it survives a regen without depending on
patch_plausible.py being re-run afterward. SCRIPT_ID = the Umami website id, used as the
idempotency marker (defined in exactly one place).
"""

SCRIPT_ID = "ce2e7f7c-eb06-4865-9d46-70143943e9b6"  # Umami website id (idempotency marker)

# Delegated interaction tracking (one listener set, works for dynamically-added result CTAs).
# Fires umami events: zip_submit {source,zip3}, outbound {host,cta}, cta_click {cta}.
# EVENTS_MARKER lets patch_umami_events.py add this to pages that predate it.
EVENTS_MARKER = "br-analytics-events"
EVENTS = (
    '<!-- br-analytics-events --><script>(function(){'
    'function T(n,d){try{if(window.umami)window.umami.track(n,d)}catch(e){}}'
    "var C=['rank-quote-cta','qcta-action','rank-cta','cross-sell-cta','refine-coverage-cta','article-sticky-cta'];"
    'function cta(el){for(var e=el;e&&e.nodeType===1;e=e.parentElement){'
    "var c=' '+((typeof e.className==='string'?e.className:'')||'')+' ';"
    "for(var i=0;i<C.length;i++)if(c.indexOf(' '+C[i]+' ')>-1)return C[i];}return '';}"
    "document.addEventListener('submit',function(e){var f=e.target;if(!f||f.tagName!=='FORM')return;"
    'var inp=f.querySelector(\'input[name="zc"],#zipBarInput\');if(!inp)return;'
    "var z=(inp.value||'').replace(/\\D/g,'').slice(0,5);var cl=(f.className||'')+'';"
    "var s=cl.indexOf('zip-bar')>-1?'zipbar':cl.indexOf('tile')>-1?'tile':'rz';"
    "T('zip_submit',{source:s,zip:z,path:location.pathname});},true);"
    "document.addEventListener('click',function(e){var a=e.target.closest?e.target.closest('a'):null;"
    "if(a&&a.hostname&&a.hostname!==location.hostname&&/^https?:/.test(a.protocol)){"
    "T('outbound',{url:a.href,cta:cta(a)||'link',path:location.pathname});return;}"
    "var k=cta(e.target);if(k)T('cta_click',{cta:k,path:location.pathname});},true);"
    '})();</script>\n'
)
SNIPPET = (
    "<!-- Privacy-friendly analytics by Umami -->\n"
    f'<script defer src="https://cloud.umami.is/script.js" data-website-id="{SCRIPT_ID}"></script>\n'
    + EVENTS
)


def ensure(html):
    """Return html with the Plausible snippet before the first </head>. No-op if already present
    or if the document has no <head> (fragments)."""
    if SCRIPT_ID in html or "</head>" not in html:
        return html
    return html.replace("</head>", SNIPPET + "</head>", 1)
