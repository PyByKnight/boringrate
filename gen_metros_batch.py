#!/usr/bin/env python3
"""Batch-add metros: generate pages + wire the tool (METRO_NAMES, METRO_CARRIER_ADJ,
ZIP_PREFIX_METRO) + sitemap + state-page links. Directional model (state avg x offset).

Two kinds: unmapped metros (ZIPs currently state-only) and mis-fold splits (ZIPs
currently inheriting a distant metro's pricing — reassigned to their own metro).

Re-runnable: pages overwrite; tool/sitemap/state inserts are skipped if the key/url
is already present.
"""
import pathlib
import re
from gen_metro_page import build_page, STATE

ROOT = pathlib.Path(__file__).parent
IDX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"

# carrier multiplier spread around the metro's central offset (from existing entries)
SPREAD = [("GEICO",-0.01),("State Farm",0.01),("Progressive",0.00),("Allstate",0.03),
("Liberty Mutual",0.05),("Farmers",0.02),("Nationwide",0.00),("USAA",-0.02),
("Erie Insurance",-0.01),("American Family",0.00),("Amica Mutual",0.00),("Auto-Owners",-0.01),
("Travelers",0.02),("Safeco",-0.01),("The Hartford",0.00),("Root Insurance",-0.06)]

METROS = [
    dict(slug="grand-rapids", name="Grand Rapids", state="MI", offset=0.60, key="grr", zips=["493","495","496"]),
    dict(slug="reno",         name="Reno",         state="NV", offset=0.73, key="rno", zips=["895","897"]),
    dict(slug="worcester",    name="Worcester",    state="MA", offset=0.93, key="wor", zips=["015","016"]),
    dict(slug="allentown",    name="Allentown",    state="PA", offset=0.95, key="abe", zips=["180","181"]),
    dict(slug="savannah",     name="Savannah",     state="GA", offset=0.88, key="sav", zips=["314"]),
    dict(slug="pensacola",    name="Pensacola",    state="FL", offset=0.52, key="pns", zips=["325"]),
    dict(slug="asheville",    name="Asheville",    state="NC", offset=1.00, key="avl", zips=["288"]),
    dict(slug="lexington",    name="Lexington",    state="KY", offset=0.92, key="lex", zips=["405"]),
    # mis-fold splits (reassigned away from a distant metro)
    dict(slug="dayton",       name="Dayton",       state="OH", offset=1.00, key="day", zips=["453","454","455"]),
    dict(slug="akron",        name="Akron",        state="OH", offset=1.00, key="akr", zips=["443"]),
    dict(slug="chattanooga",  name="Chattanooga",  state="TN", offset=0.95, key="cha", zips=["373","374"]),
]


def carrier_adj(offset):
    parts = []
    for name, d in SPREAD:
        v = round(max(0.85, offset + d), 2)
        parts.append(f'"{name}":{v}')
    return "{ " + ",".join(parts) + " }"


def wire_index(html, m):
    key, name = m["key"], m["name"]
    # METRO_NAMES
    if f'\n  {key}:' not in html.split("METRO_CARRIER_ADJ")[0]:
        html = html.replace("const METRO_NAMES = {\n",
                            f'const METRO_NAMES = {{\n  {key}: "{name} metro",\n', 1)
    # METRO_CARRIER_ADJ
    if f"\n  {key}: {{" not in html:
        html = html.replace("const METRO_CARRIER_ADJ = {\n",
                            f'const METRO_CARRIER_ADJ = {{\n  {key}: {carrier_adj(m["offset"])},\n', 1)
    # ZIP_PREFIX_METRO: reassign if present, else insert
    for z in m["zips"]:
        if re.search(rf'"{z}":"[a-z]+"', html):
            html = re.sub(rf"\"{z}\":\"[a-z]+\"", f"\"{z}\":\"{key}\"", html)
        else:
            html = html.replace("const ZIP_PREFIX_METRO = {\n",
                                f'const ZIP_PREFIX_METRO = {{\n  "{z}":"{key}",\n', 1)
    return html


def wire_state_link(m):
    st_name, st_slug, _ = STATE[m["state"]]
    sp = ROOT / "article" / "state" / f"{st_slug}.html"
    if not sp.exists():
        return False
    h = sp.read_text(encoding="utf-8")
    href = f"../../article/metro/{m['slug']}.html"
    if href in h:
        return True
    link = f'<a href="{href}">{m["name"]} &rarr;</a>'
    if 'class="internal-links internal-links-metro"' in h:
        h = re.sub(r'(<div class="internal-links internal-links-metro">)(.*?)(</div>)',
                   lambda mm: mm.group(1) + mm.group(2) + link + mm.group(3), h, count=1, flags=re.DOTALL)
        sp.write_text(h, encoding="utf-8")
        return True
    return False


def main():
    idx = IDX.read_text(encoding="utf-8")
    sm = SITEMAP.read_text(encoding="utf-8")
    for m in METROS:
        out, avg, p = build_page(m)
        idx = wire_index(idx, m)
        url = f"https://boringrate.com/article/metro/{m['slug']}.html"
        if url not in sm:
            entry = f'  <url><loc>{url}</loc><lastmod>2026-06-12</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'
            sm = sm.replace("</urlset>", entry + "</urlset>", 1)
        linked = wire_state_link(m)
        print(f"  {m['slug']:14} ${avg:>5} ({p:+d}% nat)  key={m['key']}  zips={','.join(m['zips'])}  state-link={'ok' if linked else 'SKIP'}")
    IDX.write_text(idx, encoding="utf-8")
    SITEMAP.write_text(sm, encoding="utf-8")
    print(f"\n{len(METROS)} metros wired.")


if __name__ == "__main__":
    main()
