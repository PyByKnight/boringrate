# E-E-A-T & Primary-Source Citation Plan
_Author: Opus 4.8, autonomous session 2026-07-16. Source: Fable strategy consult + repo audit._
_Read order: (1) what shipped, (2) DECISIONS THAT NEED YOU, (3) ready-to-run citation system, (4) data-capture notes._

---

## 1) Shipped this session (safe / additive — already on disk, not yet committed)
- **`/about.html`** — "Who's behind BoringRate": what it is, how it's funded (self-funded, no lead sales, no email capture, no carrier commissions), where the numbers come from (SERFF / DOI open data / NAIC, cross-checked), editorial independence, corrections + contact. Cloned from the methodology shell (nav/footer/scripts identical). Includes AboutPage + Organization JSON-LD.
- **`/editorial-standards.html`** — sourcing hierarchy (primary filings → regulator → NAIC → aggregator guardrail), independence, "how pages are produced," estimates-not-quotes, **dated corrections policy + empty corrections log**, privacy. WebPage JSON-LD.
- Wired both into the single-source nav ("About" section of `partials/nav-mega.html` → `build_nav.py`, 580 pages) + `sitemap.xml`.
- Generator: **`gen_trust_pages.py`** (idempotent; regenerates both from `methodology.html`).

**Why this was safe to do without you:** two brand-new pages + one nav-partial edit + a generator. No mass per-page edits, no primary-source links inserted into existing content, no invented persona.

---

## 2) DECISIONS THAT NEED YOU (I prepped, did NOT execute)

### A. Named founder / real identity  — *the single cheapest E-E-A-T win*
Fable's verdict: a **named human** is the highest-leverage credibility unit we're missing, and the honest version already exists — your real, demonstrable Experience is *having read and parsed hundreds of approved rate filings*. No invented credentials needed; you are explicitly **not** a licensed agent, and that independence is an asset for the blindsided-shopper positioning.
- **To ship:** replace the `<!-- OWNER-FILL -->` comment in `about.html` §05 with a named byline + one honest paragraph, and add real profile URLs (LinkedIn / GitHub / X) to the empty `sameAs: []` arrays in the Organization JSON-LD (both `about.html` and the site-wide Organization block on `index.html`/carrier pages).
- **Then:** change article bylines from generic "BoringRate Editorial" → "By [Name], BoringRate" linking `/about.html`, and add `Person` author JSON-LD (`worksFor` the Organization). *This byline change touches many article pages → treat as the same mass-edit review as §D.*
- **If you decline the real name:** the org-level About page carries Trust adequately, but leaves Experience/Expertise on the floor. Fable (and I) recommend the name.

### B. AI-assistance disclosure (optional)
`editorial-standards.html` §02b has an `<!-- OWNER-FILL -->` slot. Disclosing AI tooling in the pipeline is increasingly expected and low-cost/honest, but it's your call and could be read either way. Left blank pending you.

### C. Footer link retarget (mechanical, low-risk, but a 581-page edit)
The footer's **"About"** and **"Editorial standards"** links currently BOTH point to `/methodology.html` (aliased — not broken, but now suboptimal since the real pages exist). Retargeting them to `/about.html` and `/editorial-standards.html` is a mechanical find/replace, but it rewrites the inline footer on ~581 pages. Held per patch-safety. **Recommend:** approve a scoped `sed` on exactly those two `href`s. (Nav menu already points to the new pages correctly; only the footer lags.)

### D. THE PRIMARY-SOURCE CITATION SYSTEM  — *your explicit "lmk when I return" item*
This is the big one and the reason credibility currently sits on `/press/` + `/rate-filings/` (where nobody lands) instead of on trackers + guides (where traffic lands). Fable's three-layer pattern, ready to build — see §3.

---

## 3) Ready-to-run: the three-layer citation system (FLAGGED — awaiting go)

### Layer 1 — `/rate-filings/` becomes the citation *ledger* (keystone; do first)
- **Change:** `gen_rate_filings_rollup.py` — give every filing row a stable `id` anchor, e.g. `id="fl-state-farm-2026-03"` (state-carrier-YYYY-MM, slugified, dedup-suffixed).
- **Why first:** every other page cites *through* these anchors, so source URLs live in exactly one place; concentrates internal links on our most citable asset; gives journalists + AI answer engines a deep-linkable unit.
- **Add:** `Dataset` JSON-LD on the roll-up (cheap; aids dataset discovery + machine citation).
- Risk: LOW — single generated page; anchors are additive.

### Layer 2 — Data pages cite inline, at the number, via generators (highest credibility-per-hour)
- **Change:** `gen_rate_tracker.py`, `gen_home_rate_tracker.py`, `gen_home_metro_page.py`, `gen_filing_highlights.py`, `gen_home_filing_highlights.py` — after each carrier's filed % figure, emit a muted one-liner:
  `Source: SERFF <tracking#>, approved <Mon YYYY> · via rate-filings (internal anchor) · DOI portal (external)`.
- Two links per citation: internal anchor (Layer 1) for site structure + external `.gov`/portal for verifiability.
- **Why:** one template edit → applied to every state tracker + metro page at once. Patch-safe by construction (regenerate, never hand-edit). Dated tracking numbers next to figures = what makes a page quotable by AI answer engines, which for a sandboxed domain likely delivers referrals before Google does.
- Risk: LOW-MED — generator edits; must confirm each data row actually carries a tracking # + portal URL (see §4 — some don't).

### Layer 3 — Evergreen guides: cite forms/statute/DOI, NOT filings
- **Do NOT** cite rate filings on coverage guides ("does homeowners cover mold") — that's overclaiming.
- Honest source per coverage claim, inline at the claim:
  1. **ISO standard form language** — HO 00 03 (home), PP 00 01 (auto), with the caveat "your carrier's form may differ." The caveat is itself a trust signal.
  2. **State DOI consumer bulletins/guides** — link the specific page, not the portal home.
  3. **State statute** where the claim is statutory (min limits, cancellation-notice rules).
  4. **NAIC** for market-level claims; III acceptable as secondary, prefer `.gov`.
- **Scope (Fable): top 5–10 guides by GSC impressions only** — demand-driven, per [[boringrate-strategy-content-first]]. NOT all 28. Hand edits, **one commit per article** (per your commit-per-logical-change pref). This is the part most clearly inside your "articles" flag → your call on scope + go.
- Risk: MED — hand edits to article prose; do NOT touch co-located `<script>` blocks (CLAUDE.md rule).

### DO-NOW-next vs DEFER (Fable's ROI ranking)
- **Do now (on your go):** Layer 1 → Layer 2 → About/editorial named byline (2A) → Layer 3 top-5–10 → Dataset JSON-LD.
- **Defer (busywork a sandboxed domain won't be paid for yet):** mass citation retrofit across ALL articles; soliciting a licensed-agent "expert reviewer"; Wikidata/knowledge-panel chasing, trust badges, review widgets; any `sameAs` padding beyond real profiles; anything resembling outreach (PR stays reactive).

---

## 4) Data-capture notes — what to add for better SOURCE DOCS
_(so Layers 1–2 can be generated cleanly — this is where new SERFF-pull discipline pays off)_

Per-filing fields we need present in `serff_filings.json` / `serff_home_filings.json` for citation generation:
- **`tracking`** (SERFF tracking #) — HAVE for SERFF-jacket states (NY/PA/OH/IL/NJ/GA/SC/TN home + auto). **MISSING** where the source was open-data: **TX** (data.texas.gov, has `serff_id` — usable) and **CA** (CDI Excel, carries SERFF # — usable). Backfill the SERFF id into the row where the open-data record has it.
- **`source_url`** (deep link to the primary doc) — currently we cite the *portal*, not the *filing*. SERFF FilingAccess is session-bound (no deep links) → best stable external link is the state DOI record or the data-portal row (TX Socrata row URL, CA has none). **Decision needed:** for SERFF-only states, external link = SERFF FilingAccess home + tracking # as the locator (honest; that's how anyone re-finds it). Document this convention on `/methodology.html`.
- **`effective_date`** — HAVE (needed for "approved <Mon YYYY>").
- **stable anchor id** — DERIVED at generation (Layer 1), no new capture needed.

New reference dataset to build for Layer 3 (small, one-time):
- **`coverage_sources.json`** — map each evergreen guide topic → its honest primary source (ISO form section, DOI consumer-guide URL, statute cite). ~15 guide topics. This is what lets Layer 3 be consistent instead of ad-hoc. Candidate for a `gen_`-driven citation block.
- **State DOI consumer-bulletin URL library** — as we pull each state's filings, grab the DOI's consumer-guide URLs too (the SERFF_RUNBOOK "while pulling, look for…" note already primes this).

**If pursued, these two items ARE a new SERFF/data-capture strategy → your flagged category.** Nothing here changes the existing pull recipe; it *adds* fields to capture opportunistically on the next pull.

---

## 5) Open questions for you
1. Ship the **real name / About byline** (2A)? Strongly recommended.
2. **AI-disclosure** line in editorial standards (2B)? Yes / no.
3. Approve the **footer retarget** (2C)? (2-href scoped sed.)
4. Green-light the **citation system** (§3) and in what order/scope — especially Layer 3's article list?
5. Start capturing **`tracking` + source-url convention** on the next pull (§4)?
