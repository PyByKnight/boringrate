#!/usr/bin/env python3
"""Single source of the Plausible analytics snippet + an idempotent inserter.

Generators that emit their own <head> (home/renters/press/rate-filings) call ensure() at write
time so the analytics snippet is baked in natively — it survives a regen without depending on
patch_plausible.py being re-run afterward. patch_plausible.py imports SNIPPET from here too, so
the script id is defined in exactly one place.
"""

SCRIPT_ID = "pa-v219GyiG5lJT1bQSRxP_Z.js"
SNIPPET = (
    "<!-- Privacy-friendly analytics by Plausible -->\n"
    f'<script async src="https://plausible.io/js/{SCRIPT_ID}"></script>\n'
    "<script>\n"
    "  window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},"
    "plausible.init=plausible.init||function(i){plausible.o=i||{}};\n"
    "  plausible.init()\n"
    "</script>\n"
)


def ensure(html):
    """Return html with the Plausible snippet before the first </head>. No-op if already present
    or if the document has no <head> (fragments)."""
    if SCRIPT_ID in html or "</head>" not in html:
        return html
    return html.replace("</head>", SNIPPET + "</head>", 1)
