# BoringRate — Session Notes
_Last updated: 2026-06-11 (follow-up session, Opus 4.8)_

## This session (2026-06-11, Opus 4.8) — shipped

All 3 pending tasks DONE + bug fixes + conversion + SEO. **All commits pushed to
origin/main (auto-deploys to boringrate.com via GitHub Pages).** Later batch
(newest first): broken-link fixes (404s); sitemap +14 missing pages (home tool,
AAA compares); Twitter Card tags on 415 pages + 16 og:image backfills; reverse
cross-sell (renters+home → auto); quote-domain trim (csaa-insurance.aaa.com →
aaa.com); uniform quote-CTA box width (`min-width` border-box, fixes ragged
right edge). Earlier batch:

- **renters articles: sticky mobile CTA parity (147 pages)** — extended the
  sticky CTA to the renters article tree (`renters/{state,metro,carrier}/`);
  `patch_article_sticky_cta.py` now handles both trees (renters fallback
  `/renters/`, own label format).
- **tool: absolute `$X/yr est.` premium per rank row (auto/home/renters)** —
  rows previously showed only "Save $X vs median"; since the median moves with
  the profile, profile changes looked invisible. Added a per-row absolute
  premium (`.rank-premium`) so changes are legible. The model DOES vary
  (3-4x swings, reorderings) — see [[boringrate-rate-model]]. Rates are MODELED
  client-side (`base × stateAvg × sensitivities`), not live-quoted.
- **tool: ZIP submit clears `demo` + lands on personalization CTA** — the
  `zipForm` submit handler added `.active` but never removed `.demo`, so
  `.result.demo .refine-zip-row` / `.refine` stayed `display:none` and the ZIP
  chip + "Add Personalization" CTA were hidden after a real ZIP. Now removes
  demo, scrolls to `#refineZipRow` (scroll-margin-top:84px clears sticky header).
- **article: sticky mobile CTA strip (263 auto pages)** — Task #2.
- **auto: cross-sell renters after results** — Task #3 (`#crossSellRenters`).
- **article: activate Home nav link (263 pages)** — Task #1.

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

## Pending — execute next

All three signed-off tasks are DONE (see "This session" above). The sticky CTA
ended up scroll-to-own-form (honest: reader's real ZIP) rather than a fake
representative ZIP, and the cross-sell carries the entered ZIP into
`/renters/?zip=`. Implementation differs slightly from the original sketch below
but achieves the same goals.

Open follow-ups (not yet signed off):
- **Cross-sell the other direction** — renters→auto, and a home cross-sell.
  Currently only auto results surface renters.
- **Decide rate-display philosophy** — we now show absolute `$X/yr est.`
  alongside "Save $X vs median". If the user prefers one or the other, easy to
  adjust in each `renderRanking` (search `rank-premium`).

## Mobile rank-row streamline (2026-06-11)

Mobile-only (auto ≤800px, home/renters ≤600px); **desktop untouched**. Rows now
show: carrier name + tagline, Rate Stability score (with an inline "Rate
Stability" label via `.rank-stability::after`, since the column header is
desktop-only), and the rate/quote box (`$X/yr est.` + Save/quote). Hidden on
mobile: `.rank-grade` (Customer Service), `.rank-review-link` (BoringRate
Research), `.rank-cb` (Compare), and `.rank-mark` (NAIC, renters/home only).
Quote box is `min-width:0` on mobile so carrier names keep room.

Follow-up fixes (after first phone review): quote box is now fixed 144px +
ellipsis (was content-sized → ragged + bled past the row); Compare/grade/mark
hidden with `!important` (a base `.rank-cb` rule and a 480px research re-show
sat after the media block and were overriding the plain hides); "BoringRate
Research" text link replaced by a compact **(i) circle inline next to the
carrier name** (all viewports — user said the icon "captures enough"); long
names now wrap. Note: home rows never had a Research link or Compare box.

**Two judgment calls to confirm on a phone:**
1. NAIC quality mark hidden on mobile — stability is the single mobile quality
   signal (auto's NAIC lived in the removed grade's tooltip, so this keeps the 3
   pages consistent). Un-hide `.rank-mark` in the mobile blocks if you want it back.
2. "Rate Stability header" was implemented as a per-row inline label, not a
   single header at the top of the list.
3. The (i) icon replaced the Research text link on DESKTOP too. If you want the
   desktop text back, gate `.rank-review-icon` styles to the mobile media query.

## Pre-rendered state/metro rankings (2026-06-12) — SEO "best rates in [X]" play, DONE

`gen_state_rankings.js` (Node, evals the model from index.html) injects an indexable
static "Cheapest carriers in [State/Metro]" ranked table into every state + metro
article — Google reads the real rankings → matches "best rates in [state]" intent →
the page ranks, and the existing ZIP CTA drops users into the live JS tool. Same
model: state avg × carrier base × STATE_CARRIER_ADJ (× METRO_CARRIER_ADJ for metros).
Idempotent (markers `<!-- state-rankings-start/end -->`); re-run to refresh.
- `node gen_state_rankings.js --states` (51) · `--metros` (95) · or `TN CO ...`.
- Live on **all 51 states + 95 metros = 146 pages**, verified 0 JS errors
  (`node verify_states.js`). User approved: "do it the way Google rewards, don't
  overthink, I love the JS tool, just get users there."

## Rate-tracker pages redesigned + QA clean (2026-06-15)
- Tracker per-state pages were "sparse/ugly" (single-filing pages = 1-row table). Rebuilt:
  data-driven headline + "shop for a better rate" CTA → embedded cheapest-carriers
  ranking + ZIP entry box (→ /?zip=) → sourced filing detail → "are you getting it" callout.
- `node gen_state_rankings.js --export` → `state_rankings.json` (consumed by gen_rate_tracker.py).
  `render()` uses lambda re.sub replacements (HTML has `\d` in ZIP onsubmit — string repl broke).
- 9 deep tracker states (CA/FL/GA/LA/NV/SC/TN/TX) + hub 50-state table + State Farm $4.6B note.
- **RESOLVED user decision:** per-row delta wording = **"−$X vs avg"** (confirmed 2026-06-15; memory updated).
- Full QA pass clean: verify_rate.js / verify_states.js / verify_funnel.js all 0 JS errors.
- STILL pending user: prominent on-homepage tracker link (currently nav + footer only).

## Rankings — to top + ZIP box + renters parity (2026-06-13/14)
- Rankings now injected at the TOP of every state+metro article (first thing after
  the headline) — `gen_state_rankings.js` strips+re-inserts at top.
- Ranking block CTA is a real **ZIP entry box** (input+button) that redirects to the
  tool: `/?zip=` (auto state+metro) / `/renters/?zip=` (renters). Inline onsubmit (no
  CSP). Was an anchor "red box".
- **Renters parity**: `gen_renters_rankings.js` → "Cheapest renters carriers in [State]"
  on all 51 renters/state pages (avg×base, carrier availability filter).
- Refine trigger CTA → **"Edit Personal Profile"** (accordion, text left/chevron right).
- 80132/80133 → Colorado Springs via `ZIP5_METRO` override in index.html lookupZip.
- Note: jsdom prints a benign stderr "addEventListener null" for article bottom
  scripts (present pre-change, browser-works) — error-listener count is 0; ignore.

## Results UI tweaks from user feedback (2026-06-12)
- Top of results: compact **"Avg rate in [ZIP]: $X/yr"** banner (was a big dark
  "Median rate" block — user: too big). Light paper-deep bar, 16px.
- Per-row delta: **"−$X vs avg" / "+$X vs avg"** (was "Save $X" — user: unclear what
  it's vs). All 3 tool pages.
- Removed the redundant `rank-table-label` bar above the rank list (was stacking with
  the new banner) to kill the growing gap between the ZIP CTA and the rankings.
- PENDING USER: confirm the "vs avg" wording + compact banner look on a phone.

## Rate-change tracker (2026-06-12) — new traffic play, IN PROGRESS

Tracks who raised/cut auto rates by state + the "are you actually getting the new
rate?" angle. **Data discipline: every entry has a real source + URL; nothing invented.**
- `rate_changes.json` — `changes[]` (carrier-level filings, each sourced) +
  `statewide_2026` (Insurify projected avg for 49 states+DC, one source) + `_meta`
  (national + $5B State Farm dividend callout).
- `gen_rate_tracker.py` — builds the hub (`article/rate-changes/index.html`: national
  context, dividend callout, deep-state links, full 50-state projection table) + a
  rich per-state page for each state with carrier-level data. FAQPage+Breadcrumb schema.
- Linked from each covered state's article + sitemap + **Guides nav site-wide**
  (`patch_nav_tracker.py`, 418 pages).
- **Verify: `node verify_rate.js`** (jsdom, scans all rate pages; 0 JS errors expected).

**Deep states so far (5):** NV (8 increases, Review-Journal/NV DOI), LA (Progressive
-6.6%/-4%, LA DOI), CA (State Farm -6.2% + $5B dividend, SF newsroom), TX (State Farm
-4.1%, SF newsroom), FL (top-5 cuts -8/-10%, WFLX Mar 2026). **Hub table covers all
states** via Insurify projection.

**To add a state:** research via WebSearch (+ WebFetch where allowed; SERFF/many DOI
sites are 403-blocked to bots), add sourced rows to `changes[]`, run
`python3 gen_rate_tracker.py`, add sitemap + a state-page callout. ONLY publish
figures you can date to 2026 + attribute (excluded CA Mercury/GEICO +6.9% — traced to
2023-25; excluded FL dividend-per-state specifics — unverified in-source).

**Pending/ideas:** more states (LA has more cuts to add — Farm Bureau -11.8%, Allstate
-7.6%, Encompass -15%, need source verify); the email "your carrier filed a change"
trigger; quarterly freshness refresh; footer link. **Data note:** CA state article says
"+6.1% projected 2026" but Insurify says +1.0% — pre-existing source discrepancy, not
yet reconciled.

## Metro page expansion (2026-06-12)

Two generators added:
- `gen_metro_page.py` — `build_page(cfg)` builds one metro page from the
  `article/metro/atlanta.html` template (state-base × metro-offset; see
  [[boringrate-metro-model]]). Full SEO (title/meta/OG/Twitter/canonical,
  FAQPage+BreadcrumbList schema, sticky CTA). `STATE` dict mirrors STATE_DATA.
- `gen_metros_batch.py` — adds a list of metros: generates pages **and** wires the
  tool (`METRO_NAMES`, `METRO_CARRIER_ADJ` via a carrier `SPREAD` around the offset,
  `ZIP_PREFIX_METRO` add/reassign), sitemap, and state-page links. Re-runnable.
  **To add more metros: append to `METROS` (slug, name, state, offset, key, zips) and
  run `python3 gen_metros_batch.py`.** ZIP reassign is replace-all (a dup "374" key
  bit us once — JS last-wins).

Done so far: 84 → 95 metros. Colorado Springs (pilot) + batch of 11 (Grand Rapids,
Reno, Worcester, Allentown, Savannah, Pensacola, Asheville, Lexington; splits:
Dayton←Cincinnati, Akron←Cleveland, Chattanooga←Nashville).

**Still deferred: nav mega-menu** lists all metros and is duplicated across 410+
pages — new metros aren't in it yet (reachable via state links + sitemap). Worth a
batch patch (like `patch_article_sticky_cta.py`) for internal-link SEO. Offsets are
directional; offset moves price level only, NOT carrier ranking.

Note: state coverage is COMPLETE (930/930 ZIP3 prefixes → no national-fallback bug).
ZIP→metro is ~543/930 (rest legitimately state-only/rural).

## Analytics event layer (built 2026-06-11 — connect a vendor to go live)

A vendor-agnostic `window.track(name, props)` is defined in `<head>` of all three
tool pages (`index.html`, `home/index.html`, `renters/index.html`). It buffers
events in `window.brEvents` and **sends nowhere** until a transport is wired.

**To connect tomorrow:** uncomment ONE line in the `track()` transport block (same
in all 3 files):
- Plausible: add their `<script>` to `<head>`, then `window.plausible(name, {props: ev.props})`
- GA4: add gtag snippet, then `window.gtag("event", name, ev.props)`
- Supabase: POST `ev` to an `events` table (reuse existing supabase client)

Debug now: set `window.BR_DEBUG = true` in console to see events log; inspect
`window.brEvents`.

**Events already firing** (props in braces): `zip_submitted` {zip, product, source:
form|url}, `refine_expanded` {product}, `quote_clicked` {carrier, product, href},
`email_signup` {product}, `cross_sell_clicked` {from, to, href}, `demo_cta_clicked`
{product}. `product` is auto|home|renters. Article zip-bar searches redirect to the
tool and fire `zip_submitted` with `source:url`.

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
