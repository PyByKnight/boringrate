#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Cascade runner — recompute every derived page after new filings land.
#
#   ./rebuild.sh [auto|home|all]     (default: all)
#
# ASSUMES the DATA step is already done by hand (this script does NOT parse zips):
#   • rows added to serff_filings.json (auto) and/or serff_home_filings.json (home)
#   • new-state prep: regional base entries / expanded state lists in the rosters
#
# Then this runs the deterministic recompute → primary-source citations → nav → QA,
# in the order the owner has run by hand across every pull (empirically idempotent),
# plus the subsystems added since (auto stability, per-carrier filing sections). Every
# generator/patch here is safe to re-run: on unchanged data the only diff is the
# "Updated <date>" stamps. Review `git diff` before committing.
#
# NOT handled (still manual): parsing filings, adding NEW page URLs to sitemap.xml,
# the commit, and the IndexNow ping.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"
MODE="${1:-all}"
step(){ echo; echo "▶ $*"; "$@"; }

if [[ "$MODE" != "auto" && "$MODE" != "home" && "$MODE" != "all" ]]; then
  echo "usage: ./rebuild.sh [auto|home|all]" >&2; exit 2
fi

if [[ "$MODE" == "auto" || "$MODE" == "all" ]]; then
  echo "══════════ AUTO cascade ══════════"
  step python3 apply_filed_changes.py        # dry-run drift REPORT only — never edits pages
  step python3 gen_auto_stability.py         # filing-derived stability → index.html
  step python3 gen_rate_tracker.py           # auto rate-change trackers (+ SERFF cites)
  step python3 gen_filing_highlights.py      # who-cut/raised block on auto state pages
  step python3 gen_metros_batch.py           # regen generator-managed auto metro pages
fi

if [[ "$MODE" == "home" || "$MODE" == "all" ]]; then
  echo "══════════ HOME cascade ══════════"
  step python3 apply_home_filings.py --apply # HOME_DRIFT → home/index.html
  step python3 gen_home_stability.py         # filing-derived stability → home/index.html
  step python3 gen_home_metro_offsets.py     # sub-state offsets (recompute; safe always)
  step python3 gen_home_rate_tracker.py      # home rate-change trackers
  step python3 gen_home_state_pages.py       # 51 home state pages (regen)
  step python3 gen_home_filing_highlights.py # who-cut/raised block — AFTER state pages
  step python3 gen_home_metro_page.py        # home metro pages
fi

echo "══════════ SHARED tail ══════════"
step python3 gen_rate_filings_rollup.py      # /rate-filings/ ledger (auto + home)
step python3 gen_press_page.py               # /press/ journalist page
step python3 patch_metro_citations.py        # Layer-2 sources note on auto metros (incl. 83 legacy)
step python3 patch_carrier_filings.py        # per-carrier SERFF filing sections on carrier pages
step python3 patch_plausible.py              # analytics backstop (generators now bake it in)
step python3 build_nav.py                    # stamp single-source nav across every page
step python3 patch_sitemap_lastmod.py        # refresh <lastmod> from git dates

echo "══════════ VALIDATE ══════════"
step node qa_sweep.js
step python3 audit_prose.py

echo
echo "✅ cascade complete. Review 'git diff', then commit."
echo "   Reminders: add any NEW page URLs to sitemap.xml by hand; ping IndexNow; clear ~/*.zip + scratchpad."
