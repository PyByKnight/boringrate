#!/usr/bin/env python3
"""Inject a mobile-only sticky bottom CTA strip into every article page.

The strip is hidden by default and shown (via IntersectionObserver) only on
mobile widths once the page's top ZIP bar / inline embed / footer email form
have all scrolled out of view — so a reader deep in a long article always has a
one-tap path back to the rate tool without doubling up on visible CTAs.

Tapping the strip scrolls back to the page's OWN ZIP form and focuses it, so the
reader enters their real ZIP (no fake "representative" ZIP that would show a
stranger's rates).

Safety (see CLAUDE.md): inserts NEW <style>/<script> blocks before </body>.
Never rewrites an existing block. Idempotent — skips files already patched.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent / "article"
MARKER = "articleStickyCta"

# Location label, parsed from each page's existing zip-embed-label.
RE_EMBED_LABEL = re.compile(r'zip-embed-label">([^<]+)<')
RE_IN = re.compile(r'^Compare rates in (.+)$')
RE_RANKS = re.compile(r'^See where (.+?) ranks', re.I)


def cta_text(html):
    m = RE_EMBED_LABEL.search(html)
    if m:
        label = m.group(1).strip()
        mi = RE_IN.match(label)
        if mi and mi.group(1).strip().lower() != "your area":
            return "Compare " + mi.group(1).strip() + " rates"
        mr = RE_RANKS.match(label)
        if mr:
            return "Compare " + mr.group(1).strip() + " rates"
    return "Compare auto rates"


CSS = """<!-- article-sticky-cta-style --><style>
.article-sticky-cta{position:fixed;left:0;right:0;bottom:0;z-index:60;display:none;align-items:center;justify-content:center;gap:10px;padding:13px 18px;background:var(--ink);border-top:3px solid var(--accent);color:var(--paper);font-family:var(--mono);font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;text-decoration:none;cursor:pointer;box-shadow:0 -4px 18px rgba(0,0,0,0.18);}
.article-sticky-cta .ascta-arrow{color:var(--accent);font-size:15px;}
@media(max-width:800px){.article-sticky-cta.show{display:flex;}}
</style>"""

HTML = ('<a class="article-sticky-cta" id="articleStickyCta" href="#zipBarInput" '
        'aria-label="__LABEL__">__LABEL__ <span class="ascta-arrow">&rarr;</span></a>')

JS = """<!-- article-sticky-cta-script --><script>
(function(){
  var strip=document.getElementById("articleStickyCta");
  if(!strip)return;
  var targets=[];
  ["zipBarForm","embedZipForm"].forEach(function(id){var e=document.getElementById(id);if(e)targets.push(e);});
  var ae=document.querySelector(".article-email");if(ae)targets.push(ae);
  var ft=document.querySelector("footer");if(ft)targets.push(ft);
  if(!targets.length)return;
  var visible=new Set();
  var io=new IntersectionObserver(function(entries){
    entries.forEach(function(en){if(en.isIntersecting)visible.add(en.target);else visible.delete(en.target);});
    strip.classList.toggle("show",visible.size===0);
  },{rootMargin:"0px 0px -10% 0px"});
  targets.forEach(function(t){io.observe(t);});
  strip.addEventListener("click",function(e){
    e.preventDefault();
    var inp=document.getElementById("zipBarInput")||document.getElementById("embedZipInput");
    if(inp){inp.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(function(){try{inp.focus();}catch(_){}}, 450);}
    else{window.location.href="/";}
  });
})();
</script>"""

INSERT = "\n" + CSS + "\n" + HTML + "\n" + JS + "\n"

changed = skipped = 0
for path in sorted(ROOT.rglob("*.html")):
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        skipped += 1
        continue
    if "</body>" not in html:
        print(f"  ! no </body>: {path.relative_to(ROOT.parent)}")
        continue
    block = INSERT.replace("__LABEL__", cta_text(html))
    html = html.replace("</body>", block + "</body>", 1)
    path.write_text(html, encoding="utf-8")
    changed += 1

print(f"{changed} patched, {skipped} already had it")
