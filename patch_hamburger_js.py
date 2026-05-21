#!/usr/bin/env python3
"""Replace old hamburger JS (data-mega-toggle / nav-mega-col pattern)
with new tab-based JS on all 251 pages."""
import os, glob

ROOT = "/home/knighttyler/boringrate"

# Unique marker in the OLD hamburger JS
OLD_MARKER = "data-mega-toggle"

NEW_JS = (
    '<script>(function(){'
    "var btn=document.getElementById('navHamburger');"
    "var mega=document.getElementById('navMega');"
    "if(!btn||!mega)return;"
    "btn.addEventListener('click',function(e){e.stopPropagation();var open=!mega.classList.contains('open');mega.classList.toggle('open',open);btn.classList.toggle('open',open);btn.setAttribute('aria-expanded',String(open));});"
    "document.addEventListener('click',function(e){if(!btn.contains(e.target)&&!mega.contains(e.target)){mega.classList.remove('open');btn.classList.remove('open');btn.setAttribute('aria-expanded','false');}});"
    "mega.addEventListener('click',function(e){"
    "var tab=e.target.closest('.nav-res-tab');"
    "if(!tab)return;"
    "e.stopPropagation();"
    "var pid=tab.dataset.panel;"
    "var isActive=tab.classList.contains('active');"
    "mega.querySelectorAll('.nav-res-tab').forEach(function(t){t.classList.remove('active');});"
    "mega.querySelectorAll('.nav-res-panel').forEach(function(p){p.classList.remove('active');});"
    "if(!isActive&&pid){tab.classList.add('active');var panel=document.getElementById(pid);if(panel)panel.classList.add('active');}"
    "});"
    '})();</script>'
)


def replace_script_block(html, marker, new_js):
    """Find the <script> block containing marker and replace it entirely."""
    m = html.find(marker)
    if m == -1:
        return html
    # Walk back to find opening <script>
    start = html.rfind('<script>', 0, m)
    if start == -1:
        return html
    # Walk forward to find closing </script>
    end = html.find('</script>', m)
    if end == -1:
        return html
    return html[:start] + new_js + html[end + 9:]


all_files = (
    glob.glob(os.path.join(ROOT, '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'compare', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'state', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'carrier', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'metro', '*.html'))
)
all_files = sorted(set(all_files))

patched = skipped = 0
for path in all_files:
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    html = replace_script_block(html, OLD_MARKER, NEW_JS)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        patched += 1
    else:
        skipped += 1
        print(f'SKIPPED: {os.path.relpath(path, ROOT)}')

print(f'\nDone: {patched} patched, {skipped} unchanged out of {len(all_files)} files.')
