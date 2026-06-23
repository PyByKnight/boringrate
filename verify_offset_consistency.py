#!/usr/bin/env python3
"""
verify_offset_consistency.py — cross-surface consistency check for the auto model.

WHAT THIS DOES (and does not) MEASURE
-------------------------------------
BoringRate represents "cheapest carriers per state" in two places, BOTH in-house
and modeled — neither is scraped external ground truth:

  (A) the live model:   STATE_DATA.avg × carrier.base × STATE_CARRIER_ADJ
                        (index.html — also drives the static ranking blocks)
  (B) the editorial page: per-state cheapest-5 in article/state-rankings.html
                        ("editorial estimates based on public rate data")

This script compares the model's cheapest-N carriers per state (A) against the
editorial cheapest-5 (B). High overlap means the two surfaces AGREE — i.e. the
tool won't contradict the rankings page a user just read. It does NOT prove the
model is accurate vs. real-world rates; both sides are estimates. Treat (B) as
the closer-to-published reference (a human wrote it per state) and use this to
keep the formula (A) from drifting away from it.

Reports overall top-5 overlap plus, for EVERY national carrier, how often the
model puts it in the top-5 when the editorial page doesn't ("model-only", i.e.
the offset makes it look too cheap) and vice-versa ("editorial-only", too
expensive). Those per-carrier columns are where to look when tuning offsets.

Exit code: 0 if overall overlap >= --min (default 0.92 of 5), else 1 — so it can
gate offset changes in CI the way audit_rates.py gates rate drift.

Usage:
  python3 verify_offset_consistency.py            # full report
  python3 verify_offset_consistency.py --top 5 --min 0.92
  python3 verify_offset_consistency.py --carrier Progressive   # focus one carrier
"""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def block(s, start, end="\n};"):
    i = s.index(start)
    j = s.index(end, i)
    return s[i + len(start):j]


def slugify(name):
    return name.lower().replace(".", "").replace("'", "").replace(" ", "-")


def norm(name):
    """Collapse the two surfaces' naming to a comparable key (Farm Bureau Financial
    Services / NC Farm Bureau -> 'farm bureau'; CSAA / AAA -> 'aaa'; Root Insurance
    -> 'root'; etc.) so set-overlap reflects real agreement, not naming style."""
    n = name.lower().split("(")[0].strip()
    n = re.sub(r"\s*/\s*", " ", n)
    if "farm bureau" in n:
        return "farm bureau"
    if "aaa" in n or "auto club" in n or n.startswith("csaa"):
        return "aaa"
    for suf in (" insurance", " mutual", " financial services", " group", " company", " general"):
        if n.endswith(suf):
            n = n[: -len(suf)]
    return n.strip()


def load_model():
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    # national carriers (get the per-state offset)
    nat = []
    for chunk in re.split(r"\n  \{", block(s, "CARRIERS_STANDARD = [", "\n];")):
        nm = re.search(r'name:\s*"([^"]+)"', chunk)
        bs = re.search(r"base:\s*([0-9.]+)", chunk)
        if nm and bs:
            nat.append((nm.group(1), float(bs.group(1))))
    # regional carriers: base only, no offset (state-appropriate base by construction)
    reg_base = {m.group(1): float(m.group(2)) for m in
                re.finditer(r'"([^"]+)":\s*\{\s*base:\s*([0-9.]+)', block(s, "LOCAL_CARRIER_DEFS = {"))}
    state_reg = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\[([^\]]*)\]', block(s, "STATE_LOCAL_CARRIERS = {")):
        state_reg[m.group(1)] = re.findall(r'"([^"]+)"', m.group(2))
    sd = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{\s*name:\s*"([^"]+)"\s*,\s*avg:\s*(\d+)',
                         block(s, "STATE_DATA = {")):
        sd[m.group(1)] = (m.group(2), int(m.group(3)))
    adj = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', block(s, "STATE_CARRIER_ADJ = {")):
        adj[m.group(1)] = {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
    return nat, reg_base, state_reg, sd, adj


def load_editorial():
    s = (ROOT / "article" / "state-rankings.html").read_text(encoding="utf-8")
    pub = {}
    # single-word keys are bare (alabama:), multi-word are quoted ("new-hampshire":)
    for m in re.finditer(r'"?([\w-]+)"?:\s*\{ market:\[.*?\],\s*rates:\[(.*?)\] \}', s):
        pub[m.group(1)] = re.findall(r'\["([^"]+)",', m.group(2))
    return pub


def model_top(code, nat, reg_base, state_reg, sd, adj, n):
    """Mirror the tool's active roster for a state: nationals (avg*base*offset) +
    the regionals shown there (avg*base). Returns normalized names."""
    avg = sd[code][1]
    tilt = adj.get(code, {})
    priced = [(c, avg * b * tilt.get(c, 1)) for c, b in nat]
    for c in state_reg.get(code, []):
        if c in reg_base:
            priced.append((c, avg * reg_base[c]))
    priced.sort(key=lambda x: x[1])
    return [norm(c) for c, _ in priced[:n]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5, help="ranking depth to compare (default 5)")
    ap.add_argument("--min", type=float, default=None,
                    help="optional regression gate: fraction 0-1 of top-N overlap required "
                         "to exit 0 (e.g. 0.45). Omitted = report only, always exit 0.")
    ap.add_argument("--carrier", help="only report divergences for this carrier")
    args = ap.parse_args()

    nat, reg_base, state_reg, sd, adj = load_model()
    pub = load_editorial()

    total, n = 0, 0
    unmatched = []
    model_only = {}   # norm-name -> [states where model top-N but not editorial top-5]
    editorial_only = {}
    for code, (name, _) in sd.items():
        slug = slugify(name)
        if slug not in pub:
            unmatched.append("%s(%s)" % (name, slug))
            continue
        mt = set(model_top(code, nat, reg_base, state_reg, sd, adj, args.top))
        pb = set(norm(c) for c in pub[slug])
        total += len(mt & pb)
        n += 1
        for c in mt - pb:
            model_only.setdefault(c, []).append(code)
        for c in pb - mt:
            editorial_only.setdefault(c, []).append(code)

    mean = total / n if n else 0
    print("Cross-surface consistency: model (STATE_CARRIER_ADJ) vs editorial rankings")
    print("  NOTE: both sides are in-house estimates; this measures agreement, not accuracy.")
    print("  states compared : %d  (%d unmatched: %s)" % (n, len(unmatched), ", ".join(unmatched) or "none"))
    print("  mean top-%d overlap: %.3f / %d  (%.1f%%)\n" % (args.top, mean, args.top, mean / args.top * 100))

    names = sorted(set(model_only) | set(editorial_only),
                   key=lambda c: -(len(model_only.get(c, [])) + len(editorial_only.get(c, []))))
    if args.carrier:
        names = [c for c in names if c == args.carrier]
    print("  per-carrier divergence (where the two surfaces disagree on top-%d):" % args.top)
    print("    %-18s %-12s %-12s" % ("carrier", "model-only", "editorial-only"))
    for c in names:
        mo, eo = model_only.get(c, []), editorial_only.get(c, [])
        if not mo and not eo:
            continue
        flag = "  <- offset may be too LOW" if len(mo) >= 5 else (
               "  <- offset may be too HIGH" if len(eo) >= 5 else "")
        print("    %-18s %-12s %-12s%s" % (
            c, "%d (%s)" % (len(mo), ",".join(mo)) if mo else "0",
            "%d (%s)" % (len(eo), ",".join(eo)) if eo else "0", flag))

    frac = mean / args.top if args.top else 0
    if args.min is None:
        print("\nreport-only (no --min gate). full-roster top-%d agreement: %.1f%%" % (args.top, frac * 100))
        raise SystemExit(0)
    ok = frac >= args.min
    print("\n%s full-roster agreement %.1f%% vs gate %.0f%%" % (
        "PASS" if ok else "FAIL", frac * 100, args.min * 100))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
