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
SNIPPET = (
    "<!-- Privacy-friendly analytics by Umami -->\n"
    f'<script defer src="https://cloud.umami.is/script.js" data-website-id="{SCRIPT_ID}"></script>\n'
)


def ensure(html):
    """Return html with the Plausible snippet before the first </head>. No-op if already present
    or if the document has no <head> (fragments)."""
    if SCRIPT_ID in html or "</head>" not in html:
        return html
    return html.replace("</head>", SNIPPET + "</head>", 1)
