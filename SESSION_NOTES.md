# BoringRate — Session Notes
_Last updated: 2026-06-11 (long evening session, Opus 4.7)_

## How to resume (read this first when you come back)

You will likely restart Claude Code with `--dangerously-skip-permissions` and lose chat history. When you re-open:

1. Say: **"Read SESSION_NOTES.md and CLAUDE.md, then continue the three pending tasks."**
2. The three pending tasks are listed under **Pending — execute next** below.
3. The strategic roadmap and user preferences are below that.

## What we shipped this session (in commit order, newest at top)

Run `git log --oneline -40` to see all commits. Highlights:

### Auto page (index.html)
- New headline: **"Best Auto Insurance Rates *in your ZIP*."** + subhead "No calls. No spam. No selling your info."
- Trust line: "Editorial · Updated quarterly from state DOI rate filings & NAIC complaint indices."
- **California demo example** on first load (no profile, no ?zip) — boots an example CA ranking + dark editorial callout: "EXAMPLE ONLY · Enter ZIP above ↑ to see rates."
- **Persistent ZIP confirmation chip** "SHOWING BEST RATES IN 80132" (dynamic) above refine bar
- **Inline personalization progress bar** next to ZIP chip — 4 fields (Own, Vehicles, Age, Credit). Default 1/4 (Credit preset "Good"). Goes **green at 4/4** ("Fully Personalized").
- **Refine bar collapsed by default**. Prominent trigger button: "Add Personalization Here for More Accurate Rates ↓". Click expands, text swaps to "Personalize Your Profile ↑", arrow flips. Two-way toggle.
- Inside refine: Home / Vehicles / Age / Coverage chips + Coverage Calculator CTA above the Min/Std/Premium chips + "Add Specific Coverage Selections" sub-toggle ("Coverage choice can swing rate ~30%") for liability/deductible drawer.
- **Quote CTAs**: `Save $300 / @ geico.com →` format. Domain extracted from CARRIER_LINKS via `quoteDomain()` helper.
- **Removed**: scrolling rate-ticker, "Boring Rank: Quote First" decorative header, redundant rank-table-label, hidden state-banner/personalization in demo mode.

### Renters page (renters/index.html)
- Full parity with Auto: headline, hero, trust line, ZIP chip, inline personalization bar, collapsed refine trigger, @-domain CTAs, California demo example.
- Refine fields: Property coverage, Deductible, Bundle w/auto, Prior claims.

### Home page (home/index.html)
- Full parity with Auto + Renters.
- **Critical bug fix**: mobile rank-row 2-row grid (was collapsing invisibly on <600px — same bug Renters had previously been fixed for).
- Refine fields: Dwelling coverage slider, Deductible, Bundle w/auto, Prior claims.

### Articles
- **Carrier mentions hyperlinked** — first occurrence of each carrier name in body text wrapped in `<a class="ca-link" href="/article/carrier/{slug}.html">`. 3,087 mentions across 222 files via `patch_carrier_links.py`. Editorial accent-red underline style.

## Pending — execute next (the three tasks the user signed off on tonight)

### 1. Article nav Home link update (~30 min, mechanical)
**What:** ~200+ article files still show the old "Home (soon)" dim span in the Product dropdown nav.

**Find:** `<span class="nav-dd-panel-dim">Home<span class="nav-dd-soon">soon</span></span>`

**Replace with:** `<a href="/home/index.html">Home</a>`

**Where:** Every file in `/home/knighttyler/boringrate/article/**/*.html`.

**Approach:** Write a Python script `patch_article_home_nav.py` similar to `patch_carrier_links.py`. Idempotent (skip files that don't have the old markup). Walk state/, metro/, carrier/, compare/, plus loose articles.

Verify with: `grep -rl 'nav-dd-panel-dim">Home' /home/knighttyler/boringrate/article/ | wc -l` (should drop to 0 after pass).

### 2. Sticky mobile article CTA (~1 hour)
**What:** Articles are long. On mobile, a reader 60% down a Florida deep-dive can't quickly act. Add a persistent bottom strip with `Compare [State] rates →` linking back to the rate comparison tool.

**Where:** Article pages — state/, metro/, carrier/, compare/, plus loose articles.

**Approach:**
- CSS: `.article-sticky-cta { position: fixed; bottom: 0; left: 0; right: 0; ... }` shown only on `@media (max-width: 800px)` and only when scrolled past the top of the article body
- Content: state name pulled from article context. For state pages, link to `/?zip=...` with a representative ZIP for that state. For renters article pages, link to `/renters/?zip=...`. For home, similar.
- JS: hide the strip when zip-bar at top is in view (avoid double CTA); show when scrolled past it.

Use a script to inject the same CSS + HTML + JS into every article file. Keep it mobile-only — no impact on desktop layout.

### 3. Cross-sell after auto results (~30 min)
**What:** After a user sees their auto rate ranking, there's zero cross-sell. They just demonstrated buy-intent. Surface the renters page.

**Where:** `/home/knighttyler/boringrate/index.html` — inside the `.result` section, after the `.rank-list` but before the email capture / footer.

**Copy:** *"Also need renters insurance? Most carriers offer a 5-15% bundle discount. → Compare renters rates in [State]"* (state name from `stateData.name`) linking to `/renters/?zip=` + saved ZIP.

**Approach:**
- HTML element with id like `crossSellRenters`, inside `.result`
- CSS for a editorial accent card (paper-deep bg, left accent stripe — same style as the carrier-link callout in articles)
- JS in renderRanking: read zipInput and stateData.name, populate the link + state copy
- Hidden in demo mode via `.result.demo #crossSellRenters { display: none; }`

## Strategic roadmap (after these three)

### Tier 1 — Measurement (user said they'd set up tomorrow)
- **Analytics** — Plausible is the brand-aligned pick ($9/mo, no cookies, fits the boringrate "no tracking" promise). GA4 is free but hypocritical for this site. Or: first-party Supabase events table — write events ourselves, query manually.
- Events to track: ZIP submitted, refine expanded, Get Quote clicked (by carrier + state + product), email signup, demo banner CTA click.

### Tier 2 — Conversion lifts
- Already addressed: Quote-on-domain CTAs, sticky mobile article CTA, cross-sell. Once shipped tonight.

### Tier 3 — Trust / authority
- **Carrier monochrome wordmarks** in rank rows (~3-4 hours; need to gather/optimize ~25 SVGs).

### Tier 4 — Hygiene
- Move ~17 `patch_*.py` scripts into `/scripts/`
- Clean unused CSS: `.kicker`, `.coverage-nudge` (unused after recent edits)
- Remove hidden HTML: `boring-rank-header`, `rank-table-label` elements (CSS-hidden, can be deleted)

## Critical rules (from CLAUDE.md — also memorized)

**Never replace an entire `<script>...</script>` block** when patching. The pattern in old `patch_hamburger_js.py` wiped widespread JS across 66+ pages because pages had unique JS co-located in the same block as the targeted marker. Required git extraction from `41fb75c` to recover.

**Safe pattern:** Insert a *new* `<script>` block before the marker, or use surgical Edit tool replacements that don't touch existing block boundaries.

Style blocks are safer to surgically edit, but still — when in doubt, insert a new `<style>` block rather than rewrite an existing one.

## User preferences I've learned

- **Honest critique > hedged feedback.** "Don't holdback punches" was an explicit directive.
- **Concise responses.** No hedge language. State decisions directly.
- **Editorial tone preserved.** The boringrate brand is editorial, magazine-like, "boring on purpose." Avoid hype language ("Unlock!", "Save Big!").
- **CTA format**: `Save $X / @ domain.com →` (the @ symbol is the link signal).
- **Personalization bar**: 4 options not 5; Coverage tier excluded from count (it's an assumption, not a personalization).
- **Refine UX**: Trigger should STAY VISIBLE when expanded (the user pushed back when it disappeared on click).
- **Demo state**: shows California example on first load — refine bar hidden in demo mode, only the ZIP form + example callout + ranks visible.
- **Aggressive clutter trimming.** Removed rate ticker, decorative headers, redundant labels. User specifically called out "too many blocks before they see the actual ranks."
- Likes **product-named headlines** (e.g., "Best Auto Insurance Rates in your ZIP") over generic ones.
- **No new files unless necessary** — surgical edits to existing files preferred.
- **Commit per logical change** so changes are independently reversible via `git log` review.

## File map
| File | Purpose |
|---|---|
| `/home/knighttyler/boringrate/index.html` | Auto comparison (~5400 lines) |
| `/home/knighttyler/boringrate/renters/index.html` | Renters comparison (~1700 lines) |
| `/home/knighttyler/boringrate/home/index.html` | Home comparison (~1300 lines) |
| `/home/knighttyler/boringrate/article/state/*.html` | 50 state articles |
| `/home/knighttyler/boringrate/article/metro/*.html` | 80+ metro articles |
| `/home/knighttyler/boringrate/article/carrier/*.html` | ~30 carrier pages |
| `/home/knighttyler/boringrate/article/compare/*.html` | Head-to-head compare pages |
| `/home/knighttyler/boringrate/CLAUDE.md` | **Patch safety rules — read first** |
| `/home/knighttyler/boringrate/patch_carrier_links.py` | Recent reference for write-script patches |

## Git state at session end
- Branch: `main`
- Remote: `git@github.com:PyByKnight/boringrate.git`
- Auto-deployed via GitHub Pages on push (CNAME → boringrate.com)
- Latest commits (run `git log --oneline -8` for current state)
