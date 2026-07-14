#!/usr/bin/env python3
"""The 'why did my rate go up when rates are flat' guide (Fable idea #1, consumer framing).

Data-driven from serff_home_filings.json so the hero examples stay accurate: pulls the most
dramatic low-filed-average / high-by-ZIP filings (the 'the statewide average is not your rate'
proof) + a '0% overall but big swing' redistribution example + a 'wanted more than they filed'
example. Output: home/why-did-my-home-insurance-go-up.html."""
import json, pathlib
from datetime import date
from gen_metro_page import STATE, esc, _json

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "home" / "why-did-my-home-insurance-go-up.html"
RED, GREEN = "#b4321a", "#2f6b3a"

scaff = (ROOT / "home" / "state" / "florida.html").read_text(encoding="utf-8")
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>") + len("</style>")]
NAV = scaff[scaff.index('<header class="top">'):scaff.index("</header>") + len("</header>")]
TAIL = scaff[scaff.index("<footer>"):]


def pct(v):
    return f'{"+" if v > 0 else ("−" if v < 0 else "±")}{abs(v):g}%'


def build():
    F = [r for r in json.load(open(ROOT / "serff_home_filings.json"))["filings"]
         if r.get("max_pct") is not None]
    # hero: small filed average, big single-territory increase
    heroes = sorted([r for r in F if abs(r["overall_pct"]) <= 6 and r["max_pct"] >= 30],
                    key=lambda r: -r["max_pct"])[:6]
    # redistribution: ~0% overall but wide swing
    zeros = sorted([r for r in F if abs(r["overall_pct"]) < 0.5 and (r["max_pct"] - r["min_pct"]) >= 25],
                   key=lambda r: -(r["max_pct"] - r["min_pct"]))
    # wanted-more: indicated materially above what was filed
    wanted = sorted([r for r in F if r.get("indicated_pct") is not None
                     and r["indicated_pct"] - r["overall_pct"] >= 4 and r["overall_pct"] >= 0],
                    key=lambda r: -(r["indicated_pct"] - r["overall_pct"]))
    n_states = len({r["state"] for r in F})

    def li(r):
        return (f'<li><strong>{esc(r["carrier"])}</strong> in {esc(STATE[r["state"]][0])} filed a '
                f'<strong>{pct(r["overall_pct"])}</strong> statewide average &mdash; but the change ranged up to '
                f'<strong style="color:{RED};">{pct(r["max_pct"])}</strong> depending on the ZIP '
                f'(<a class="ca-link" href="{r["url"]}" target="_blank" rel="noopener nofollow">see the filing</a>).</li>')

    hero_list = "".join(li(r) for r in heroes)
    z = zeros[0] if zeros else None
    zero_para = ""
    if z:
        zero_para = (
            f'<p>A filing can even average <strong>{pct(z["overall_pct"])}</strong> and still move your bill a lot. '
            f'{esc(z["carrier"])}&rsquo;s {esc(STATE[z["state"]][0])} filing was essentially flat overall, yet it '
            f'raised some ZIPs by <strong style="color:{RED};">{pct(z["max_pct"])}</strong> while cutting others by '
            f'<strong style="color:{GREEN};">{pct(z["min_pct"])}</strong>. &ldquo;No overall change&rdquo; is often a '
            f'<em>redistribution</em> &mdash; the total premium the carrier collects stays flat, but who pays it shifts.</p>')
    w = wanted[0] if wanted else None
    wanted_para = ""
    if w:
        wanted_para = (
            f'<h2>Sometimes the increase you got is smaller than the one they wanted</h2>'
            f'<p>Every rate filing includes the carrier&rsquo;s own actuarial &ldquo;indicated&rdquo; number &mdash; what '
            f'their analysis says they <em>need</em>. They often file for less than that. {esc(w["carrier"])} in '
            f'{esc(STATE[w["state"]][0])} filed <strong>{pct(w["overall_pct"])}</strong> but indicated it wanted '
            f'<strong>{pct(w["indicated_pct"])}</strong>. When the filed number trails the indicated one, it usually '
            f'means more increases are queued for future renewals &mdash; a reason to lock in a better price now rather '
            f'than wait.</p>')

    today = date.today()
    url = "https://boringrate.com/home/why-did-my-home-insurance-go-up.html"
    title = "Why Did My Home Insurance Go Up If Rates Are &ldquo;Flat&rdquo;?"
    desc = ("Your homeowners insurance went up but your carrier says rates are flat or barely changed? A statewide-average "
            "rate filing can move your ZIP far more than the headline number. Here's why — with the real filings.")

    faq = [
        ("Why did my home insurance go up if my insurer says rates are flat?",
         "The rate change a carrier files is a statewide average. Within that one filing, individual rating territories "
         "(roughly your ZIP) can move far more — or less — than the average. A filing that averages 0% can still raise "
         "your ZIP by 20-40% while lowering others, because the carrier is redistributing where the risk sits."),
        ("What is a statewide average rate change?",
         "It's the single percentage a carrier reports to the state for a filing — the change to its total premium across "
         "everyone it insures in that state. It is not your personal rate change. Your change depends on your territory, "
         "home age, roof, and coverage."),
        ("Can my rate go up when my insurer filed a 0% change?",
         "Yes. A 0% overall filing means the carrier's total premium doesn't change — but it can still shift premium "
         "between ZIPs, raising higher-risk areas and cutting lower-risk ones. We've logged 0%-overall home filings that "
         "moved individual territories by more than 40 percentage points."),
        ("How do I find out my actual rate change?",
         "Re-shop your exact ZIP. Filed changes reach you at renewal, and a cut often reaches new customers first. "
         "Comparing carriers for your address is the only way to see where you actually land versus the average."),
    ]
    faq_ld = ('<script type="application/ld+json">\n{"@context":"https://schema.org","@type":"FAQPage","mainEntity":['
              + ",".join('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
                         % (_json(q), _json(a)) for q, a in faq) + ']}\n</script>')

    zipbox = ('<form onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);'
              'if(/^\\d{5}$/.test(z)){location.href=\'/home/?zip=\'+z}else{this.zc.focus()}" '
              'style="display:flex;gap:0;max-width:360px;margin:18px 0;">'
              '<input name="zc" type="text" inputmode="numeric" maxlength="5" placeholder="Enter your ZIP" aria-label="ZIP code" '
              'style="flex:1;min-width:0;font-family:var(--mono);font-size:16px;letter-spacing:0.12em;padding:12px 14px;border:2px solid var(--ink);border-right:none;background:var(--paper);color:var(--ink);outline:none;" />'
              '<button type="submit" style="font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:0 20px;border:2px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;white-space:nowrap;">Compare home rates &rarr;</button></form>')

    faq_html = "".join(f'<h3 style="margin-bottom:4px;">{esc(q)}</h3><p>{esc(a)}</p>' for q, a in faq)

    body = f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/home/index.html">Home Insurance</a> &nbsp;·&nbsp; Rate Guide &nbsp;·&nbsp; Updated {today:%B %Y}</div>
    <h1 class="article-title">Why did your home insurance go up when your carrier says rates are &ldquo;flat&rdquo;?</h1>
    <p class="article-dek">Your renewal jumped, but the headlines (and your insurer) say rates barely moved. Both can be true &mdash; because the number they file isn&rsquo;t your number.</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; from primary-source rate filings</div>
  </div>
  <div class="article-body">
    <p style="font-size:20px;line-height:1.5;max-width:660px;">You open your renewal and it&rsquo;s up double digits. But the news says your carrier &ldquo;held rates steady,&rdquo; or the filing you find says <strong>+2%</strong>. You&rsquo;re not being gaslit, and the filing isn&rsquo;t wrong &mdash; <strong>the rate a carrier files is a statewide average, not your rate.</strong></p>

    <h2>The average hides an enormous spread</h2>
    <p>A single rate filing covers everyone a carrier insures in your state. Inside that one filing, different rating territories &mdash; roughly, different ZIP codes &mdash; can move by wildly different amounts. The statewide number is just the blended result. Real examples from filings we&rsquo;ve pulled across {n_states} states:</p>
    <ul class="pr-movers">{hero_list}</ul>
    <p>Same filing, same &ldquo;average.&rdquo; One neighborhood barely moves; another jumps 30, 60, even 100+ percent.</p>

    <h2>&ldquo;No change overall&rdquo; can still mean a big change for you</h2>
    {zero_para}

    {wanted_para}

    <h2>What to actually do about it</h2>
    <p>Filed changes reach you at <em>renewal</em> &mdash; and a cut often reaches new customers before existing ones. The only way to see where <em>you</em> land, versus the statewide average, is to compare carriers for your exact ZIP.</p>
    {zipbox}
    <p style="font-size:14px;"><a class="ca-link" href="/home/rate-changes/">See who&rsquo;s raising and cutting home rates in your state &rarr;</a></p>

    <h2>Common questions</h2>
    {faq_html}

    <p style="font-size:13px;color:var(--ink-mute);margin-top:20px;">Figures are filed statewide-average changes and their by-territory ranges, taken from carriers&rsquo; own rate filings with state insurance regulators. Individual rates vary by home, roof age, and risk. Not a quote.</p>
  </div>
</div>'''

    style_extra = ('<style>.pr-movers{list-style:none;padding:0;margin:14px 0;max-width:660px;}'
                   '.pr-movers li{padding:9px 0;border-bottom:1px solid var(--rule);font-size:15px;line-height:1.5;}'
                   '.article-body h2{margin-top:32px;}</style>')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title} | BoringRate</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
{style_extra}
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
{faq_ld}
</head>
<body>
{NAV}
{body}
{TAIL}'''
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} — {len(heroes)} hero examples, {len(F)} filings with range data")


if __name__ == "__main__":
    build()
