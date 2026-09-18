#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch Illinois rate filings from IDOI's own Company Rate Information app — no SERFF session.

★ THIS IS THE RICHEST NON-SERFF SOURCE FOUND. Unlike the TX and CA feeds (which give a percent
and little else), IDOI publishes per filing:

    Submission Date · SERFF Track # · Overall % Rate INDICATED · Overall % Rate IMPACT (taken)
    · Written Premium Change $ · # Policy Holders · Written Premium $ · Max % Change · Min % Change

That is nearly everything we open a SERFF jacket to read — including indicated-vs-taken and the
max/min spread, which drive the /rate-filings/ detail panels — and it returns MULTIPLE YEARS in
one call. Real example (State Farm, IL homeowners):

    06/02/2025  SFMA-134393024  indicated 32.5%  taken 27.2%  1,491,665 PH  spread +39.9%/0%

Terms: `idoi.illinois.gov/robots.txt` is `Allow: /`; the app is state-hosted (not SERFF), needs no
account, and presents no CAPTCHA. Requests are serialised with a delay — this is a small legacy
WebForms app and there is no reason to hammer it.

THE CHAIN (three stateful steps; ASP.NET WebForms, so VIEWSTATE must be carried forward):
  1. RegEntPortal: GET, postback rdbCriteria=5 ("Company Rate Information") to reveal the search
     box, postback the company name + year -> links carrying ?EntityNumber=NNNNNN
  2. SearchRF3 PageMethod `TOINamesForFein(EntityIDStr, filingYear)` -> the TOI list for that
     entity/year (JSON)
  3. SearchRF3 postback with the chosen TOI -> the filing table above

Coverage is PARTIAL and skews to older years — in spot checks only ~6 of 24 entity/year combos
returned anything, and IDOI's own page tells you to use SERFF for electronic filings. So this
supplements the manual pull for Illinois; it does not replace it.

Reports rather than appends: the ledgers are curated, so merging stays a human decision.

  python3 fetch_il_filings.py --carrier "State Farm" --year 2025
  python3 fetch_il_filings.py --carrier "Allstate" --year 2025 --line home
  python3 fetch_il_filings.py --carrier "State Farm" --year 2025 --write
"""
import argparse, json, re, sys, time, gzip, datetime, urllib.request, urllib.parse

REG = "https://insurance.illinois.gov/Applications/RegEntPortal/Default.aspx"
RF3 = "https://insurance.illinois.gov/Applications/CompanyRateInfo/SearchRF3.aspx"
TOI_API = RF3 + "/TOINamesForFein"
UA = {"User-Agent": "boringrate/1.0 (+https://boringrate.com; rate-filing research)"}
PAUSE = 0.6
LINE_OF = {"04.0": ("home", "HO"), "19.0": ("auto", "PPA")}


def _open(url, data=None, json_body=None):
    h = dict(UA)
    if json_body is not None:
        data = json.dumps(json_body).encode()
        h["Content-Type"] = "application/json; charset=utf-8"
        h["X-Requested-With"] = "XMLHttpRequest"
    elif data is not None:
        h["Content-Type"] = "application/x-www-form-urlencoded"
    r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=40)
    raw = r.read()
    if r.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    time.sleep(PAUSE)
    return raw.decode("utf-8", "replace")


def hidden(html):
    out = {}
    for m in re.finditer(r'<input[^>]*type="hidden"[^>]*>', html):
        n = re.search(r'name="([^"]+)"', m.group(0))
        v = re.search(r'value="([^"]*)"', m.group(0))
        if n:
            out[n.group(1)] = v.group(1) if v else ""
    return out


def find_entities(carrier, year):
    """Company name -> [(EntityNumber, display name)] via the two RegEntPortal postbacks."""
    h1 = _open(REG)
    f = hidden(h1)
    f.update({"ctl00$ContentPlaceHolder1$rdbCriteria": "5",
              "__EVENTTARGET": "ctl00$ContentPlaceHolder1$rdbCriteria", "__EVENTARGUMENT": ""})
    h2 = _open(REG, urllib.parse.urlencode(f).encode())

    f2 = hidden(h2)
    f2.update({"ctl00$ContentPlaceHolder1$rdbCriteria": "5",
               "ctl00$ContentPlaceHolder1$RF3Name": carrier,
               "ctl00$ContentPlaceHolder1$RF3Date": str(year),
               "ctl00$ContentPlaceHolder1$searchRF3": "Search"})
    h3 = _open(REG, urllib.parse.urlencode(f2).encode())

    seen, out = set(), []
    for m in re.finditer(r'href="[^"]*EntityNumber=(\d+)[^"]*"[^>]*>(.*?)</a>', h3, re.S):
        eid = m.group(1)
        if eid in seen:
            continue
        seen.add(eid)
        out.append((eid, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(2))).strip()))
    return out


def tois(entity, year):
    try:
        return _open(TOI_API, json_body={"EntityIDStr": str(entity), "filingYear": str(year)})
    except Exception as e:
        return f'{{"d":[]}}  # {e}'


def filings_for(entity, year, toi):
    """Step 3 postback. Both TOINameList (the AJAX-populated select) and TOINameListHold must be
    sent — sending only the hold field makes the server throw 'Index was outside the bounds'."""
    h = _open(f"{RF3}?EntityNumber={entity}&Year={year}")
    f = hidden(h)
    f.update({
        "ctl00$ctl00$MainContent$mainContent$TOINameList": toi,
        "ctl00$ctl00$MainContent$mainContent$TOINameListHold": toi,
        "ctl00$ctl00$MainContent$mainContent$FilingYear": str(year),
        "ctl00$ctl00$MainContent$mainContent$PostBackIndicator": "POSTBACK",
        "ctl00$ctl00$MainContent$mainContent$FirstRunIndicator": "N",
        "ctl00$ctl00$MainContent$mainContent$GetRF3": "Get Rate Filing Information",
    })
    page = _open(RF3, urllib.parse.urlencode(f).encode())
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page))
    i = txt.find("Min % Change")
    if i < 0:
        return []
    rows = []
    # date | track# | indicated | impact | $wp-change | phs | $wp | max | min
    pat = re.compile(
        r"(\d{2}/\d{2}/\d{4})\s+([A-Z]{3,5}-[A-Za-z0-9]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+"
        r"\$([\d,\-]+)\s+([\d,]+)\s+\$([\d,]+)\s+(-?[\d.]+)\s+(-?[\d.]+)")
    for m in pat.finditer(txt[i:]):
        d, trk, ind, imp, wpc, ph, wp, mx, mn = m.groups()
        num = lambda s: float(s.replace(",", "")) if s not in ("", "-") else None
        rows.append({"submitted": d, "tracking": trk, "indicated_pct": float(ind),
                     "overall_pct": float(imp), "written_premium_change": num(wpc),
                     "affected": int(ph.replace(",", "")), "written_premium": num(wp),
                     "max_pct": float(mx), "min_pct": float(mn)})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carrier", required=True)
    ap.add_argument("--year", default=str(datetime.date.today().year))
    ap.add_argument("--line", choices=["auto", "home", "both"], default="both")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    try:
        ents = find_entities(args.carrier, args.year)
    except Exception as e:
        sys.exit(f"IDOI unreachable: {e}")
    if not ents:
        sys.exit(f"no IL entities matched {args.carrier!r} for {args.year}")
    print(f"{len(ents)} entit{'y' if len(ents)==1 else 'ies'} matched {args.carrier!r}:")
    for eid, nm in ents:
        print(f"   {eid}  {nm[:64]}")

    have = set()
    for f in ("serff_filings.json", "serff_home_filings.json"):
        try:
            have |= {r["tracking"] for r in json.load(open(f))["filings"]}
        except Exception:
            pass

    out, seen = [], set()
    for eid, nm in ents:
        raw = tois(eid, args.year)
        try:
            names = json.loads(raw.split("  #")[0]).get("d") or []
        except Exception:
            names = []
        for toi in dict.fromkeys(names):
            pre = toi.split()[0]
            if pre not in LINE_OF:
                continue
            line, product = LINE_OF[pre]
            if args.line != "both" and line != args.line:
                continue
            for r in filings_for(eid, args.year, toi):
                if r["tracking"] in seen:
                    continue
                seen.add(r["tracking"])
                d, mth = r.pop("submitted"), None
                mm, dd, yy = d.split("/")
                r.update({"state": "IL", "line": line, "carrier": args.carrier,
                          "entity": nm, "product": product, "toi": toi,
                          "url": f"{RF3}?EntityNumber={eid}&Year={args.year}",
                          "disposition_date": f"{yy}-{mm}-{dd}",
                          "in_ledger": r["tracking"] in have,
                          "source_note": "IL DOI Company Rate Information app (non-SERFF)."})
                out.append(r)

    out.sort(key=lambda r: r["disposition_date"], reverse=True)
    new = [r for r in out if not r["in_ledger"]]
    print(f"\n{len(out)} filings found ({len(new)} not in our ledger)")
    if out:
        print(f"  {'date':<11} {'line':<5} {'ind':>7} {'taken':>7} {'PHs':>10}  "
              f"{'spread':<15} tracking")
        for r in out:
            sp = f"{r['max_pct']:+.1f}/{r['min_pct']:+.1f}"
            flag = "" if r["in_ledger"] else "  ← NEW"
            print(f"  {r['disposition_date']:<11} {r['line']:<5} {r['indicated_pct']:>6.1f}% "
                  f"{r['overall_pct']:>6.1f}% {r['affected']:>10,}  {sp:<15} {r['tracking']}{flag}")

    if args.write and new:
        fn = f"il_filings_{args.carrier.lower().replace(' ', '_')}_{args.year}.json"
        json.dump({"_meta": {"source": "IL DOI Company Rate Information app",
                             "fetched": datetime.date.today().isoformat(),
                             "carrier": args.carrier, "year": args.year, "count": len(new)},
                   "filings": new}, open(fn, "w"), indent=1)
        print(f"\nwrote {fn} — review before merging.")


if __name__ == "__main__":
    main()
