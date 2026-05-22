#!/usr/bin/env python3
"""
Nav v3 patch:
  1. Add Carrier Comparison as 3rd nav-tab on every page (if missing)
  2. Remove the inline "Method" link from the top bar
  3. Add "About" section to hamburger mega nav with Methodology link
"""
import glob, re

CARRIER_LINK = '<a href="/article/compare/index.html">Carrier Comparison</a>'

FAQ_SECTION = (
    '<div class="nav-section">'
    '<p class="nav-section-label">About</p>'
    '<div class="nav-res-guides">'
    '<a href="/methodology.html">Methodology — how we collect and rank rate data</a>'
    '</div>'
    '</div>'
)

# Unique anchor: end of mega nav guides panel (Florida Rates is the last item)
# Use chr() to avoid quote/apostrophe ambiguity in the source file
FLORIDA_LINK = (
    'florida-rates-dropping.html">'
    'Florida Rates — What' + chr(39) + 's Changing in 2026</a>'
)

OLD_MEGA_TAIL = FLORIDA_LINK + '</div></div></div></div></div>'
NEW_MEGA_TAIL = FLORIDA_LINK + '</div></div></div>' + FAQ_SECTION + '</div></div>'


def add_carrier_tab(html):
    """Insert Carrier Comparison link after Coverage Calculator in nav-tabs."""
    mega_start = html.find('id="navMega"')
    if mega_start == -1:
        return html
    header = html[:mega_start]
    if '/article/compare/index.html' in header:
        return html  # already has it

    def inserter(m):
        indent = m.group(2)  # indentation of the coverage link
        return m.group(1) + '\n' + indent + CARRIER_LINK + m.group(3)

    new_header = re.sub(
        r'(\n( +)<a href="/coverage\.html"(?:[^>]*)>Coverage Calculator</a>)(\n +</div>)',
        inserter,
        header,
        count=1
    )
    return new_header + html[mega_start:]


def remove_nav_method(html):
    """Remove the inline Method link from the top nav bar."""
    return re.sub(
        r'\n\s+<a href="/methodology\.html" class="nav-method">Method</a>',
        '',
        html,
        count=1
    )


def add_faq_section(html):
    """Add About/FAQ section to hamburger mega nav."""
    if OLD_MEGA_TAIL not in html:
        return html
    if FAQ_SECTION in html:
        return html  # already patched
    return html.replace(OLD_MEGA_TAIL, NEW_MEGA_TAIL, 1)


all_files = sorted(glob.glob('**/*.html', recursive=True))
all_files = [f for f in all_files if '.git' not in f]

tab_patched = method_removed = faq_added = 0

for path in all_files:
    with open(path) as f:
        html = f.read()

    orig = html
    html = add_carrier_tab(html)
    if html != orig:
        tab_patched += 1
    prev = html
    html = remove_nav_method(html)
    if html != prev:
        method_removed += 1
    prev = html
    html = add_faq_section(html)
    if html != prev:
        faq_added += 1

    if html != orig:
        with open(path, 'w') as f:
            f.write(html)

print(f'Carrier tab added:   {tab_patched} files')
print(f'Method link removed: {method_removed} files')
print(f'FAQ section added:   {faq_added} files')
print(f'Total files scanned: {len(all_files)}')
