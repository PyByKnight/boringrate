# BoringRate — Session Notes
_Last updated: 2026-06-11_

## What we built this session

### 1. `home/index.html` — New page (complete)
Full home insurance comparison tool modeled on renters/index.html.
- 12 carriers with base multipliers, CS grades, stability scores
- Coverage amount as a **slider** ($150k–$750k, step $50k, default $300k)
- Continuous premium scaling: `0.4 + 0.6 * (dwellingK / 300)`
- Independent agents panel (STATE_AGENTS, ~3 per state)
- Personalization banner: "Typical profile · adjust above to personalize" at defaults
- ZIP → state lookup, localStorage profile save/restore (key: `br_home_profile`)
- Supabase email capture (source: `"home"`)

### 2. Nav updated on all three pages
`<span class="nav-dd-panel-dim">Home<span class="nav-dd-soon">soon</span></span>`
→ `<a href="/home/index.html">Home</a>`
Applied to: `index.html` (auto) and `renters/index.html`

### 3. Renters pill behavior change
- Pills now start **unselected** (no default active class)
- `refinement` defaults changed to `null` (estimatePremium handles null gracefully — no multiplier fires)
- Banner: "Personalize above to refine rates" at 0 selections → increments to "X / 4 selected" → "Fully personalized"
- Profile version bump was added then **reverted** — old saved profiles are kept as-is

### 4. Mobile table layout — renters & auto
Both pages: CS rating + stability dots were invisible on mobile (6-column grid collapsed).
Fixed with 2-row mobile layout:
```
Row 1: [#]  [Carrier Name]   [mark*]  [CTA]
Row 2: [#]  [CS grade]       [●●●●○]
```
*auto has no mark column — uses 3-col grid `32px 1fr auto`

CSS added at `@media(max-width:600px)` (renters) and modified inside `@media(max-width:800px)` (auto).

### 5. Mobile product nav strip
All three pages: Auto / Renters / Home links hidden on mobile behind hamburger.
Fixed with `:has(#navDdProductPanel)` CSS — shows panel as static flex strip below header row:
```
[BoringRate]                [hamburger]
[  Auto  |  Renters  |  Home  ]
```
Applied at `@media(max-width:600px)` on all three pages.
Home page also needed `top-inner{flex-wrap:wrap}` added (auto/renters already had it).

---

## Known state / things to check next session

- **Home page not yet in the mobile product nav** — verify the `<a href="/home/index.html">Home</a>` link in `#navDdProductPanel` is present on both `index.html` and `renters/index.html` (was updated earlier this session)
- **Auto page mobile layout** — rank-row now uses `grid-template-columns:32px 1fr auto` with 3 cols. The `rank-vs` (price delta) sits at `grid-column:4` which no longer exists — may need checking
- **Home page** — no mobile table layout fix applied yet (same 6-col issue as renters/auto probably exists once users start entering ZIPs)
- **LinkedIn post** — draft written, needs: fix "$4,800" number against actual data, fix "you're" → "your", add two-stat graphic (FL vs HI)

---

## File map
| File | Purpose |
|---|---|
| `/home/knighttyler/boringrate/index.html` | Auto comparison (root) |
| `/home/knighttyler/boringrate/renters/index.html` | Renters comparison |
| `/home/knighttyler/boringrate/home/index.html` | Home comparison (new) |
| `/home/knighttyler/boringrate/CLAUDE.md` | **Read this first** — patch safety rules |

## Key rule (from CLAUDE.md)
Never replace an entire `<script>` block. Always insert a new block. See CLAUDE.md for details.
