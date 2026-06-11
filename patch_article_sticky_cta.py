#!/usr/bin/env python3
"""Inject a mobile-only sticky bottom CTA strip into every article page.

The strip is hidden by default and shown (via IntersectionObserver) only on
mobile widths once the page's top ZIP bar / inline embed / footer email form
have all scrolled out of view — so a reader deep in a long article always has a
one-tap path back to the rate tool without doubling up on visible CTAs.

Tapping the strip scrolls back to the page's OWN ZIP form and focuses it, so the
reader enters their real ZIP (no fake "representative" ZIP that would show a
stranger's rates).

Covers both article trees:
  - article/        (auto)    -> fallback link "/"
  - renters/{state,metro,carrier}/ (renters) -> fallback link "/renters/"

Safety (see CLAUDE.md): inserts NEW <style>/<script> blocks before </body>.
Never rewrites an existing block. Idempotent — skips files already patched.
"""
import pathlib
import re

BASE = pathlib.Path(__file__).parent
MARKER = "articleStickyCta"

RE_EMBED_LABEL = re.compile(r'zip-embed-label">([^<]+)<')

# Per-tree label rules: list of (regex, format) applied to the zip-embed-label
# text. First match wins; group(1) is the location/carrier name. A captured
# value of "your area" is treated as no-match (falls through to default).
AUTO_RULES = [
    (re.compile(r'^Compare rates in (.+)$'), "Compare {} rates"),
    (re.compile(r'^See where (.+?) ranks', re.I), "Compare {} rates"),
]
RENTERS_RULES = [
    (re.compile(r'^Compare renters insurance in (.+)$'), "Compare {} renters rates"),
    (re.compile(r'^Compare (.+?) against other carriers$', re.I), "Compare {} renters rates"),
]

TREES = [
    {"roots": ["article"], "rules": AUTO_RULES,
     "default": "Compare auto rates", "fallback": "/"},
    {"roots": ["renters/state", "renters/metro", "renters/carrier"], "rules": RENTERS_RULES,
     "default": "Compare renters rates", "fallback": "/renters/"},
]

CSS = """<!-- article-sticky-cta-style --><style>
.article-sticky-cta{position:fixed;left:0;right:0;bottom:0;z-index:60;display:none;align-items:center;justify-content:center;gap:10px;padding:13px 18px;background:var(--ink);border-top:3px solid var(--accent);color:var(--paper);font-family:var(--mono);font-size:13px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;text-decoration:none;cursor:pointer;box-shadow:0 -4px 18px rgba(0,0,0,0.18);}
.article-sticky-cta .ascta-arrow{color:var(--accent);font-size:15px;}
@media(max-width:800px){.article-sticky-cta.show{display:flex;}}
</style>"""

HTML = ('<a class="article-sticky-cta" id="articleStickyCta" href="#zipBarInput" '
        'aria-label="__LABEL__">__LABEL__ <span class="ascta-arrow">&rarr;</span></a>')

JS_TPL = """<!-- article-sticky-cta-script --><script>
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
    else{window.location.href="__FALLBACK__";}
  });
})();
</script>"""


def cta_text(html, rules, default):
    m = RE_EMBED_LABEL.search(html)
    if m:
        label = m.group(1).strip()
        for rx, fmt in rules:
            mm = rx.match(label)
            if mm and mm.group(1).strip().lower() != "your area":
                return fmt.format(mm.group(1).strip())
    return default


total_changed = total_skipped = 0
for tree in TREES:
    js = JS_TPL.replace("__FALLBACK__", tree["fallback"])
    insert = "\n" + CSS + "\n" + HTML + "\n" + js + "\n"
    for root in tree["roots"]:
        for path in sorted((BASE / root).rglob("*.html")):
            html = path.read_text(encoding="utf-8")
            if MARKER in html:
                total_skipped += 1
                continue
            if "</body>" not in html:
                print(f"  ! no </body>: {path.relative_to(BASE)}")
                continue
            block = insert.replace("__LABEL__", cta_text(html, tree["rules"], tree["default"]))
            path.write_text(html.replace("</body>", block + "</body>", 1), encoding="utf-8")
            total_changed += 1

print(f"{total_changed} patched, {total_skipped} already had it")
