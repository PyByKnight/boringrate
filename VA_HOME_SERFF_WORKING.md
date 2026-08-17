# VA Homeowners SERFF Pull — Working List

Search: Property & Casualty · TOI 04.0 Homeowners · disposition **07-01-25 → 08-17-26** · 241 results (3 pages).
Portal: https://filingaccess.serff.com/sfa/home/VA
URL scheme: `https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId=<digits>` (strip the `XXXX-` and any `G`).

Targets: `serff_home_filings.json` (VA becomes the 10th home state) + `serff_renters_filings.json`
(currently 2 rows, MI only — the tenant block below is the first real renters pull).

Triage rules applied: filing type must carry **Rate**; status must be **Closed - Filed** or
**Closed - Approved and Filed**; sub-TOI **04.0000 combos / 04.0003 owner-occupied** for the home file,
**04.0004 Tenant** for the renters file.

---

## TIER 1 — must pull (20). Roster nationals + VA regionals.

| # | Carrier (family) | Product | Type | Tracking |
|---|---|---|---|---|
| 1 | **State Farm** Fire & Casualty | HO-49200 | Rate/Rule | SFMA-134760355 |
| 2 | **USAA** (Multiple) | VA HOM Rate/Rule Filing | Rate/Rule | USAA-134827676 |
| 3 | **Erie** Insurance Company | VA ES CO HCT 1/1/26 Rate Review | Rate | ERPP-134682697 |
| 4 | **Allstate** (Multiple: AI AIC AVPIC APC) | HO MFH CON REN | Rate/Rule | ALSE-134914653 |
| 5 | **Allstate** Vehicle & Property | AVPIC HO | Rate/Rule | ALSE-134728018 |
| 6 | **Nationwide** (Multiple) | Homeowners | Rate/Rule | NWPP-134558137 |
| 7 | **Nationwide** (Multiple, not all cos) | Homeowners | Rate/Rule | NWPP-134498871 |
| 8 | **Liberty Mutual** (Multiple) | Homeowners | Rate | LBPM-135016955 |
| 9 | **Liberty Mutual** Personal Ins Co | Homeowners | Rate | LBPM-134893343 |
| 10 | **Travelers** (Multiple) | Quantum Homeowners | Rate/Rule | TRVD-G135009179 |
| 11 | **Travelers** (Multiple) | Legacy Homeowners | Rate/Rule | TRVD-G135009170 |
| 12 | **Farmers** (Multiple) | FLEX/FSPH/LHO/NGHO/SPRC/PTP/SPF/RC | Rate/Rule | FARM-134586228 |
| 13 | **Farmers** Fire Insurance Exchange | Flex Home | Rate/Rule | FARM-134992701 |
| 14 | **Virginia Farm Bureau** Fire & Cas | Homeowners Program (OOD) | Rate/Rule | VRFB-134994654 |
| 15 | **Virginia Farm Bureau** Mutual | Homeowners Program | Rate/Rule | VRFB-134994651 |
| 16 | **American Strategic (ASI = Progressive Home)** | Homeowners (04.0003) | Rate | AMSI-134485084 |
| 17 | **Amica** | VA-H-26-4-RR | Rate/Rule | AMMA-134932424 |
| 18 | **Auto-Owners** | Virginia Homeowners | Form/Rate/Rule | AOIC-134474539 |
| 19 | **Homesite (American Family)** of the Midwest | Homeowners | Form/Rate/Rule | HMSS-134894183 |
| 20 | **Hartford** (Multiple: HFIC HUIC TRUM TCFIC) | VA Home Advantage | Rate/Rule | HART-134606166 |

Notes:
- **No GEICO** — expected, GEICO brokers home rather than writing it.
- **No Progressive-branded HO** — ASI (#16) *is* the Progressive home book in VA. Map it to Progressive.
- Erie Insurance **Exchange** (NAIC 26271, the main writing entity) shows only Form rows; #3 is on Erie
  Insurance Company (26263). Check on open whether the rate review covers the Exchange too — if not,
  Erie's VA home book has no in-window rate move and should be recorded as held flat (SC precedent).

## TIER 2 — same books, earlier in-window filings (open-book completeness) + solid regionals

Per the open-book rule, every in-window filing for a book we carry matters. Pull after Tier 1.

**Amica** (3 more): AMMA-134762164 (VA-H-26-2-R) · AMMA-134691322 (26-1-RR) · AMMA-134660224 (25-4-RR)
**Allstate** (3 more): ALSE-134752066 (AIC HO) · ALSE-134746787 (AI HO) · ALSE-134532192 (ANAIC HO)
**Liberty Mutual** (5 more): LBPM-134912075 · LBPM-134904228 · LBPM-134800614 · LBPM-134699788 · LBPM-134600862
**Safeco / American Economy** (Liberty family): LBPM-135002706 · LBPM-134780617 · LBPM-134598844
**Travelers** Quantum Home 2.0: TRVD-G135001927 (newest of 5; others G134829082, G134676836, G134594472, G134581015)
**Farmers** (4 more): FARM-134839322 (FSPH/NGHO) · FARM-134923350 · FARM-134697533 · FARM-134730757 (SPRC)
**VA Farm Bureau** (4 more): VRFB-134994654's predecessors — VRFB-134925494 · VRFB-134925499 · VRFB-134713433 · VRFB-134713430
**Hartford Prevail**: HART-134873615 (HICSE) · HART-134873775 (HICIL) · HART-134606165 (HICSE)
**Hanover**: HNVR-G134962245 (PL HO 26) · HNVR-G134740066 · HNVR-G134726733 · HNVR-G134726947 · HNVR-G134605066
**Cincinnati**: CNNB-134543604 (CIC) · CNNB-134551708 (CCC)
**Encompass** (Allstate): GMMX-134873108 (C360 Home/Condo/Renter Rate) · GMMX-134594249 · GMMX-134552358
**Selective**: SELC-134669083 (Homeowners Rate Revision) · SELC-134741638 (Water Backup)
**Donegal**: DNGL-134721067
**Horace Mann**: HRMN-134871735 (VA Home Rate 11-01-26) · HRMN-134537193
**FAIG** ×3 — family unidentified from the results table, confirm entity on open: FAIG-134707306 · FAIG-134775575 · FAIG-134596093
**Openly** (Rock Ridge): OPEN-G134739870
**Stillwater**: FDLY-134843978 · FDLY-134793173
**Hippo / Spinnaker**: HIPO-134970145
**Homeowners of America (Porch)**: HAIC-134929134 · HAIC-134839415 · HAIC-134749571
**Acuity**: ACUT-134895242 · ACUT-134512280
**Rockingham (VA regional, Bluestone)**: RMUT-134090975
**Grange / Trustgard**: GRAN-134653568 (Virginia PinPoint Homeowners)
**Narragansett Bay**: BLCK-134613189 · BLCK-134591512
**Universal P&C**: UPCC-134616143
**First Protective (Frontline)**: FIMI-134868628 · MERL-134768446 · MERL-134642230
**Lemonade / Metromile**: LEMO-134181940 (MIC By-Peril)

## RENTERS TIER — 04.0004 Tenant → `serff_renters_filings.json`

First real renters pull. GSC says renters is the current demand leader and the renters file has 2 rows.

| Carrier | Product | Type | Tracking |
|---|---|---|---|
| **Allstate** (ANAIC) | ANAIC REN | Rate/Rule | ALSE-134750995 |
| **Safeco** (Liberty) of Illinois | Renters | Rate/Rule | LBPM-134801178 |
| **Assurant** / American Bankers | Renters Insurance | Rate/Rule | ASPX-134619604 |
| **Toggle** (Farmers' renters brand) | Toggle Renters | Rate/Rule | AGMK-134597456 |
| **Foremost** (Farmers) | Tenant Program | Rate/Rule | FORE-134637766 |
| **National General** (Allstate) | VA_NGIC_R8M Renters — NEW PROGRAM | Form/Rate/Rule | GMMX-134712870 |
| **MIC General** (Allstate) | VA_MICG_R8VRV Renters — NEW PROGRAM | Form/Rate/Rule | GMMX-134712892 |
| **New South** (Allstate) | VA_NSIC_R8 Renters — NEW PROGRAM | Form/Rate/Rule | GMMX-134712828 |
| **InsureMax** | IMIC VA RENTERS PROTECT | Rate/Rule | ASRN-134439015 |
| **AmTrust** / Technology Ins Co | Renters Insurance Program | Rate/Rule | UNKP-134548356 |
| **Wesco** (AmTrust) | Tenant Property Protection | Form/Rate/Rule | PERR-134966214 |
| **Chubb** / ACE P&C | Homeowners - Tenant | Form/Rate/Rule | ACEH-134633259 |

★ The three GMMX "NEW PROGRAM" rows (National General, MIC General, New South — all Allstate-family
non-standard entities) are **new renters programs launching in VA**, not rate changes. They carry base
rates rather than a % change, which makes them usable as renters *base* anchors, not drift. Grab them.

## EXCLUDED — and why (so the next pass doesn't re-triage them)

- **Rating bureaus / advisory orgs (~26 rows)**: Insurance Services Office (ISOF ×15), American
  Association of Insurance Services (AMAX ×7), Willis Towers Watson (WTWA), Zesty.ai (ZAPR).
  Loss-cost and model filings, not carrier rate changes.
- **Form-only / Form-Rule-only** rows — no rate impact.
- **Not approved**: Closed-Withdrawn, Closed-Disapproved, Closed-Returned to Company, Pending Response,
  Resubmission Received, Closed-Receipt Acknowledged. Includes Accelerant (SPRO-G134944189, disapproved),
  Liberty LBPM-134957858 (disapproved), USAA-135044201 (disapproved, form/rule only), Auto-Owners
  AOIC-134700221 (withdrawn), HAIC-134659650 (withdrawn), OCCD-134642936 (withdrawn), Grange
  GRAN-134929384 (disapproved), Berkley BKON-134752672 (disapproved), Brethren BRMT-134752522 /
  BRMT-134752541, Great American GACX-134902982 (resubmission), Dealers DACO-134588126 (renters withdrawal).
- **Mobile / manufactured home (04.0002)** — different line, not modeled: Foremost ×3, Homesite
  HMSS-134687034, Lyndon Southern, Standard Guaranty, American Bankers Mobilowners ×2, Loudoun ×2,
  Windsor-Mount Joy WNMJ-134699774, Independent Mutual IMFI-134711452.
- **Condo-only (04.0001)** — secondary, revisit if a condo page ships: AMSI-134485059, HMSS-134870024,
  MERL-134775845, FIMI-134688958, ASPX-134699792, NWPP-134610360.
- **High-net-worth / surplus, off-roster**: PURE (PRIV ×3), Vault (SPIS), Chubb Masterpiece (ACEH ×3),
  AIG Private Client (APCG-134696834), Crestbrook (NWPP-134643030), Berkley (BKON-134761661).
- **Small VA mutuals — Tier 3, only if a VA-regional angle is wanted**: Central (CEMC-134633959),
  Goodville (GDMT-134652685), MMG (MMGC-134645681), Lititz (LTTZ-134752712), Windsor-Mount Joy
  (WNMJ-134584113), Germantown (PHCT-134803125), Brethren (BRMT-134807883), Occidental (OCCD-134696311),
  Utica (UTCX-134889920, UTCX-134579451), Penn National (PNPR-135022286), American Modern (AMMH-134646456),
  Mutual Assurance Society of VA, Pulaski & Giles, Grayson-Carroll-Wythe.

## After the pull — cascade

`./rebuild.sh home` covers the recompute + patches + QA. Expect: `home/rate-changes/virginia.html` (new,
10th home tracker) + rate-filings roll-up + `home/state/virginia.html` highlights + VA carrier page
filing sections. Then reconcile against the home tool rankings per the tool↔filing consistency rule.

---

## ★ FINDING (2026-08-17): jacket book averages are LINE-BLENDED — do not use them as base anchors

Computing `written_premium / affected` off the SERFF jacket gives a number that looks like an
average premium but is not an HO-3 average. The jacket's policy count and written premium span
**every sub-line in the filed program** — homeowners + condo + tenant + mobile home — and the
blend fraction differs per carrier, so the contamination is not a constant you can divide out.

**Proof (State Farm, the one VA filing whose zip included Supporting Document attachments):**

| measure | value | source |
|---|---|---|
| jacket book average | **$1,055** | $642,413,555 / 608,900 (jacket) |
| projected EP per policy, Non-Tenant Homeowners | **$1,478.10** | Exhibit 1M, `VA HO 2026 Filing.pdf` |
| tool modeled VA price | **$1,496** | 1558 x base 0.97 x tilt 0.99 |

The jacket average is 29% BELOW the modeled price; the actuarial memo's HO-only figure is **1% below
it**. The tool's State Farm base was accurate all along. The SFMA jacket confirms the blend directly —
it discusses "Condominium Unitowners" deductible pages inside the same "Virginia Homeowners Program".

**Which VA jackets visibly mention other sub-lines** (so their book average is definitely blended):
VRFB-134994651 (condominium, mobile home, tenant) · NWPP-134558137 (condominium, tenant) ·
AOIC-134474539 (renters, tenant). The rest mention none, but absence of the word is not proof of a
pure HO-3 book — State Farm's own program name gave no hint either.

**Consequence — retracted:** an earlier pass in this session computed correlation(tool base, jacket
book average) = -0.27 across 11 VA carriers and read it as "the tool's price ordering is inverted vs
the filings." That correlation is computed on contaminated denominators and should not be relied on.
Dwelling-value mix is still a real confounder, but line mix is the larger one and it is the one proven
here.

**Consequence — method:** filings CAN anchor home bases, but only from the actuarial memo's
**projected earned premium per policy** exhibit (State Farm Exhibit 1M; other carriers file an
equivalent), never from the jacket's Company Rate Information block. That exhibit lives in
**Supporting Document Attachments**, which are a separate checkbox on the SERFF download page and were
not included in most of this pull. Jacket-derived `overall_pct` remains fully valid — it is a
percentage change, immune to the mix problem. This is why `apply_home_filings.py` treats filings as a
DRIFT layer only, and that design stands.

**Open: Virginia Farm Bureau base.** Still unrostered, still contradicting the tracker (5 mentions on
`home/rate-changes/virginia.html`). The peer argument (every Farm Bureau in the roster sits below the
state average: MI 0.90, TX 0.78, LA 0.88) and the book argument (VAFB blends at $1,603 vs State Farm's
blended $1,055, implying VAFB is materially more expensive) now point in OPPOSITE directions, and the
book argument can't be trusted until VAFB's own EP-per-policy is read. Resolve by re-downloading
**VRFB-134994651 with Supporting Document Attachments checked** and reading its EP-per-policy exhibit.
