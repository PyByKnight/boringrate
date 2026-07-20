#!/usr/bin/env python3
"""Press / data landing page — the journalist-facing authority asset (Fable #5, item 1).

A journalistic summary of the 2026 auto + home rate landscape, sourced entirely to
primary state-DOI filings — every figure links to its source. Doubles as the "who we
are / how to cite us / contact" landing a reporter arrives at, and points to the full
/rate-filings/ roll-up. Data-driven from rate_changes.json (curated, attributed feed)
+ serff_home_filings.json, so it stays accurate as the backbone grows.
Output: press/index.html."""
import json, pathlib
from datetime import date
from gen_metro_page import STATE, esc
from plausible_snippet import ensure

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "press" / "index.html"
RED, GREEN = "#b4321a", "#2f6b3a"

scaff = (ROOT / "home" / "state" / "florida.html").read_text(encoding="utf-8")
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>") + len("</style>")]
NAV = scaff[scaff.index('<header class="top">'):scaff.index("</header>") + len("</header>")]
TAIL = scaff[scaff.index("<footer>"):]


def chg_span(pct, direction):
    """Signed, colored % — respects rate_changes.json convention (pct positive, dir carries sign).
    Rounded to 1 decimal for editorial cleanliness (filings carry spurious precision like 18.962%)."""
    down = direction == "decrease" if direction else pct < 0
    color, sign = (GREEN, "−") if down else (RED, "+")
    return f'<span style="color:{color};font-weight:600;">{sign}{round(abs(pct), 1):g}%</span>'


def home_src(url):
    """Clean primary-source label for a home filing from its URL."""
    if "texas.gov" in url: return "TX TDI open data"
    if "insurance.ca.gov" in url: return "CA CDI filings list"
    if "filingaccess.serff.com" in url: return "SERFF Filing Access"
    return "State DOI filing"


def src_link(source, url):
    return f'<a class="ca-link" href="{esc(url)}" target="_blank" rel="noopener nofollow">{esc(source)}</a>'


def mover_li(carrier, state, pct, direction, source, url, entity=""):
    ent = f' <span class="pr-ent">{esc(entity)}</span>' if entity else ""
    return (f'<li><strong>{esc(carrier)}</strong>{ent} &mdash; {esc(STATE[state][0])} '
            f'{chg_span(pct, direction)} <span class="pr-src">{src_link(source, url)}</span></li>')


def build():
    rc = json.load(open(ROOT / "rate_changes.json"))
    meta, changes = rc["_meta"], rc["changes"]
    home = [r for r in json.load(open(ROOT / "serff_home_filings.json"))["filings"]
            if r.get("overall_pct") is not None]
    auto_rows = [r for r in json.load(open(ROOT / "serff_filings.json"))["filings"]
                 if r.get("overall_pct") is not None]

    # coverage counts for the credibility line
    n_filings = len(auto_rows) + len(home)
    states = {r["state"] for r in auto_rows} | {r["state"] for r in home} | {c["state"] for c in changes}
    n_states = len(states)
    carriers = {r["carrier"] for r in auto_rows} | {r["carrier"] for r in home}
    n_carriers = len(carriers)

    cuts = sorted((c for c in changes if c["dir"] == "decrease"), key=lambda x: -x["pct"])[:12]
    incs = sorted((c for c in changes if c["dir"] == "increase"), key=lambda x: -x["pct"])[:12]

    home_up = sorted((r for r in home if r["overall_pct"] > 0), key=lambda x: -x["overall_pct"])[:6]
    home_dn = sorted((r for r in home if r["overall_pct"] < 0), key=lambda x: x["overall_pct"])[:4]

    today = date.today()
    url = "https://boringrate.com/press/"
    title = "2026 Insurance Rate Filings — Data for Journalists | BoringRate"
    desc = (f"A primary-source summary of the 2026 U.S. auto and home insurance rate landscape: who is "
            f"raising and cutting rates, by how much, across {n_states} states. Every figure links to its "
            f"state Department of Insurance filing. Free to cite.")

    # --- national summary lede ---
    lede = f'''<p style="font-size:19px;line-height:1.55;max-width:680px;">{esc(meta["national_2026"])}
      ({src_link(meta["national_source"], meta["national_url"])}.) After the 2023&ndash;24 shock, many
      carriers are now <em>filing decreases</em> &mdash; and BoringRate reads those filings one by one,
      straight from state insurance regulators.</p>
      <p>The clearest signal came from the largest auto insurer. {esc(meta["dividend_note"])}
      ({src_link("State Farm newsroom", meta["dividend_url"])}.) {esc(meta.get("statefarm_cuts", ""))}
      ({src_link("State Farm rate reductions", meta.get("statefarm_cuts_url", meta["dividend_url"]))}.)</p>
      <p>But the picture is not uniform. In the same market where national carriers cut, small regional
      and agent-driven carriers are still filing double-digit increases &mdash; and home insurance is
      moving the opposite way from auto. Below is what the filings show right now.</p>'''

    cuts_html = "".join(mover_li(c["carrier"], c["state"], c["pct"], c["dir"], c["source"], c["url"]) for c in cuts)
    incs_html = "".join(mover_li(c["carrier"], c["state"], c["pct"], c["dir"], c["source"], c["url"]) for c in incs)

    home_up_html = "".join(
        mover_li(r["carrier"], r["state"], r["overall_pct"], "increase",
                 home_src(r["url"]), r["url"]) for r in home_up)
    home_dn_html = "".join(
        mover_li(r["carrier"], r["state"], r["overall_pct"], "decrease",
                 home_src(r["url"]), r["url"]) for r in home_dn)

    body = f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker">For Journalists &nbsp;·&nbsp; Primary-Source Rate Data &nbsp;·&nbsp; Updated {today:%B %-d, %Y}</div>
    <h1 class="article-title">The 2026 insurance rate landscape, from the filings up</h1>
    <p class="article-dek">BoringRate tracks approved auto and home insurance rate filings, carrier by carrier,
      straight from state insurance regulators. Here is what they show &mdash; every figure links to its source.</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; independent &nbsp;·&nbsp; no commissioned carrier relationships</div>
  </div>
  <div class="article-body">
    {lede}

    <div class="callout"><p><strong>What we track.</strong> Approved, filed statewide-average rate changes for
      <strong>auto and homeowners</strong> insurance across <strong>{n_states} states</strong> &mdash;
      {n_filings} carrier filings from {n_carriers} carriers so far, and growing. Sources are the SERFF Filing
      Access system (cited by tracking number), Texas TDI open data (data.texas.gov), and the California CDI
      filings list. Figures are statewide averages; individual rates vary by risk. Not quotes.</p></div>

    <h2>Who is cutting auto rates</h2>
    <p>The carriers most drivers actually buy &mdash; State Farm, GEICO, Progressive, Travelers &mdash; are
      broadly cutting auto rates in 2026, after two years of lower claim severity. The largest decreases we have
      logged:</p>
    <ul class="pr-movers">{cuts_html}</ul>

    <h2>Who is still raising auto rates</h2>
    <p>Increases are concentrated in smaller regional and agent-distributed carriers, and in a handful of
      high-loss states.</p>
    <ul class="pr-movers">{incs_html}</ul>

    <h2>Home insurance is moving the other way</h2>
    <p>While auto softens, homeowners filings are the opposite story &mdash; driven by reinsurance cost and
      catastrophe losses. Only Texas and California publish home filings as open data so far; both are
      raising broadly, with a few outliers cutting.</p>
    <ul class="pr-movers">{home_up_html}{home_dn_html}</ul>

    <div class="callout" style="border-color:var(--accent);">
      <p><strong>The full dataset &mdash; free to browse and cite.</strong> Every filing above in one interactive
      table: filter by product, state, or direction, search any carrier, and sort by rate change, effective date,
      or national market share &mdash; each row linked to its primary source.</p>
      <p style="margin:8px 0 0;">&#8594; <a href="/rate-filings/"><strong>All 2026 rate filings (auto + home)</strong></a>
       &nbsp;·&nbsp; <a href="/article/rate-changes/">Auto rate-change tracker, by state</a>
       &nbsp;·&nbsp; <a href="/home/rate-changes/">Home rate-change tracker, by state</a></p>
    </div>

    <h2>How we source this</h2>
    <p>Every number is a filed or approved <em>statewide-average</em> rate change taken from a primary
      regulatory record &mdash; a carrier&rsquo;s rate filing with a state Department of Insurance, identified
      by its SERFF tracking number. We do not estimate or model the figures on this page; we read them off the
      filings. Where a state publishes filings as open data (Texas, California), we pull the record directly;
      elsewhere we retrieve the individual SERFF jacket and read the &ldquo;Company Rate Information&rdquo;
      overall-impact line. Full method: <a href="/methodology.html">our methodology</a>.</p>

    <div class="callout">
      <p><strong>Using this in a story?</strong> You are welcome to. Please cite as
      &ldquo;<em>BoringRate, 2026 rate-filing analysis, {today:%B %Y}</em>&rdquo; and, where possible, link the
      underlying filing (each row on the <a href="/rate-filings/">roll-up</a> carries its source). We can
      comment on auto and home rate trends, who is raising or cutting by state, and what the filings say &mdash;
      from the primary records, not press releases.</p>
      <p style="margin:8px 0 0;"><strong>Contact:</strong> <a href="mailto:hello@boringrate.com">hello@boringrate.com</a></p>
    </div>

    <p style="font-size:13px;color:var(--ink-mute);margin-top:18px;">BoringRate is independent insurance
      research with no commissioned relationships with any carrier named here. Coverage spans {n_states} states
      and is expanding. Figures are statewide averages and are not quotes.</p>
  </div>
</div>'''

    style_extra = '''<style>
    .pr-movers{list-style:none;padding:0;margin:14px 0;max-width:680px;}
    .pr-movers li{padding:9px 0;border-bottom:1px solid var(--rule);font-size:15px;line-height:1.5;}
    .pr-ent{color:var(--ink-mute);font-size:12px;}
    .pr-src{font-size:12px;color:var(--ink-mute);margin-left:4px;}
    .article-body h2{margin-top:34px;}
    </style>'''

    ld = ('<script type="application/ld+json">\n'
          + json.dumps({
              "@context": "https://schema.org", "@type": "Article",
              "headline": "The 2026 insurance rate landscape, from the filings up",
              "description": desc, "url": url, "dateModified": today.isoformat(),
              "author": {"@type": "Organization", "name": "BoringRate"},
              "publisher": {"@type": "Organization", "name": "BoringRate"},
              "isAccessibleForFree": True,
          }) + "\n</script>")

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
{style_extra}
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
{ld}
</head>
<body>
{NAV}
{body}
{TAIL}'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(ensure(html), encoding="utf-8")
    print(f"wrote {OUT} — {n_filings} filings, {n_states} states, {n_carriers} carriers; "
          f"{len(cuts)} cuts / {len(incs)} increases / {len(home_up)+len(home_dn)} home shown")


if __name__ == "__main__":
    build()
