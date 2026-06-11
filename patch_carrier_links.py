"""
Wrap the FIRST mention of each carrier name in each article body with a
link to its carrier page. One-shot pass — re-running is idempotent via
the STYLE_MARKER sentinel.

Processes:
  - /article/state/*.html
  - /article/metro/*.html
  - /article/compare/*.html  (skips self-references in the filename)
  - Loose guide articles in /article/*.html

Skips:
  - /article/carrier/*.html  (carrier landing pages — would self-link)

Per CLAUDE.md: this script does NOT touch <script>...</script> blocks.
It (a) edits HTML body text inside <div class="article-body"> and
(b) inserts a small <style> block right before </head>.
"""

import re
from pathlib import Path

# Longer multi-word names FIRST so they match before single-word substrings.
CARRIERS = [
    ("Texas Farm Bureau",      "texas-farm-bureau"),
    ("Georgia Farm Bureau",    "georgia-farm-bureau"),
    ("Tennessee Farm Bureau",  "tennessee-farm-bureau"),
    ("Kentucky Farm Bureau",   "kentucky-farm-bureau"),
    ("Louisiana Farm Bureau",  "louisiana-farm-bureau"),
    ("NC Farm Bureau",         "nc-farm-bureau"),
    ("Liberty Mutual",         "liberty-mutual"),
    ("American Family",        "american-family"),
    ("Country Financial",      "country-financial"),
    ("Mercury Insurance",      "mercury"),
    ("Shelter Insurance",      "shelter"),
    ("Alfa Insurance",         "alfa"),
    ("Root Insurance",         "root-insurance"),
    ("The Hartford",           "the-hartford"),
    ("Auto-Owners",            "auto-owners"),
    ("State Farm",             "state-farm"),
    ("Nationwide",             "nationwide"),
    ("Progressive",            "progressive"),
    ("Travelers",              "travelers"),
    ("Wawanesa",               "wawanesa"),
    ("Allstate",               "allstate"),
    ("Farmers",                "farmers"),
    ("MAPFRE",                 "mapfre"),
    ("PEMCO",                  "pemco"),
    ("GEICO",                  "geico"),
    ("Safeco",                 "safeco"),
    ("USAA",                   "usaa"),
    ("Amica",                  "amica"),
    ("NYCM",                   "nycm"),
    ("Erie",                   "erie"),
    ("NJM",                    "njm"),
    ("AAA",                    "aaa"),
]

STYLE_MARKER = "<!-- ca-link-style -->"
LINK_STYLE = (
    STYLE_MARKER
    + "<style>"
    + ".article-body a.ca-link{color:var(--accent);text-decoration:none;"
    + "border-bottom:1px solid rgba(180,50,26,0.3);transition:border-color 120ms;}"
    + ".article-body a.ca-link:hover{border-bottom-color:var(--accent);}"
    + "</style>\n"
)


def link_carriers(body_section: str, skip_slugs: set[str]) -> tuple[str, int]:
    """Wrap the first occurrence of each carrier name with an <a class="ca-link">.
    Skips matches inside existing <a> tags or inside h1-h4 headings."""
    new = body_section
    count = 0
    for name, slug in CARRIERS:
        if slug in skip_slugs:
            continue
        pat = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")
        for m in pat.finditer(new):
            pos = m.start()
            # Skip if inside an existing <a>...</a>
            if new.rfind("<a ", 0, pos) > new.rfind("</a>", 0, pos):
                continue
            # Skip if inside a heading
            in_h = False
            for h in ("h1", "h2", "h3", "h4"):
                if new.rfind("<" + h, 0, pos) > new.rfind("</" + h + ">", 0, pos):
                    in_h = True
                    break
            if in_h:
                continue
            url = "/article/carrier/" + slug + ".html"
            repl = '<a class="ca-link" href="' + url + '">' + name + "</a>"
            new = new[: m.start()] + repl + new[m.end() :]
            count += 1
            break  # only first occurrence per carrier per article
    return new, count


def slugs_in_filename(path: Path) -> set[str]:
    """For compare pages like aaa-vs-geico.html, skip linking aaa and geico
    (the page is about them — linking would be self-referential)."""
    stem = path.stem  # e.g. "aaa-vs-geico"
    if "-vs-" not in stem:
        return set()
    parts = stem.split("-vs-")
    slugs = set()
    for p in parts:
        slugs.add(p)
    return slugs


def process_file(path: Path) -> tuple[bool, int]:
    text = path.read_text()
    if STYLE_MARKER in text:
        return False, 0  # already processed
    start_tag = '<div class="article-body">'
    i = text.find(start_tag)
    if i == -1:
        return False, 0
    j = text.find("<footer", i)
    if j == -1:
        return False, 0
    body = text[i:j]
    new_body, count = link_carriers(body, slugs_in_filename(path))
    if count == 0:
        return False, 0
    new_text = text[:i] + new_body + text[j:]
    new_text = new_text.replace("</head>", LINK_STYLE + "</head>", 1)
    path.write_text(new_text)
    return True, count


def main():
    root = Path("/home/knighttyler/boringrate/article")
    files: list[Path] = []
    files.extend(sorted((root / "state").glob("*.html")))
    files.extend(sorted((root / "metro").glob("*.html")))
    files.extend(sorted((root / "compare").glob("*.html")))
    # Loose guides at /article/ root
    for fn in [
        "coverage-guide.html",
        "credit-score-insurance.html",
        "florida-rates-dropping.html",
        "market-share.html",
        "premium-went-up.html",
        "shopping-strategy.html",
        "sr22-insurance.html",
        "state-rankings.html",
        "young-drivers.html",
    ]:
        f = root / fn
        if f.exists():
            files.append(f)

    total_files = 0
    total_links = 0
    skipped = 0
    for f in files:
        ok, count = process_file(f)
        if ok:
            total_files += 1
            total_links += count
        else:
            skipped += 1
    print(f"Linked {total_links} carrier mentions across {total_files} files "
          f"({skipped} skipped — already processed or no body match).")


if __name__ == "__main__":
    main()
