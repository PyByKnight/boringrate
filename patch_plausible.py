#!/usr/bin/env python3
"""Add the Plausible analytics snippet to every page's <head>.

Idempotent: skips files already containing the script id. Insert-only (new
<script> blocks before </head>) per CLAUDE.md patch safety — never replaces
an existing block. The 3 tool pages got the snippet by hand (they also have
the window.track event layer); this covers the article/guide/static tree.
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).parent
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

files = subprocess.run(["git", "ls-files", "*.html"], capture_output=True,
                       text=True, cwd=ROOT).stdout.split()
patched = skipped = nohead = 0
for rel in files:
    p = ROOT / rel
    html = p.read_text(encoding="utf-8")
    if SCRIPT_ID in html:
        skipped += 1
        continue
    if "</head>" not in html:
        nohead += 1  # fragments (partials/) have no head — leave alone
        continue
    p.write_text(html.replace("</head>", SNIPPET + "</head>", 1), encoding="utf-8")
    patched += 1
print(f"patched {patched}, already had it {skipped}, no <head> {nohead}")
