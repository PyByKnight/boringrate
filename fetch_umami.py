#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pull and analyse Umami analytics — the raw event stream, not the UI's summaries.

WHY THIS EXISTS. The Umami dashboard pages its activity log 20 rows at a time (235
pages at our volume) and will not export event PROPERTIES. The raw rows carry
`referrerPath` on every pageview, which is the only way to answer the question GSC
cannot: WHICH page sent someone into the rate tool.

AUTH — two paths, in priority order:
  1. ~/.umami_key          Umami Cloud API key. Requires a Pro plan ($20/mo).
  2. ~/umami_curl.txt      A request copied out of the browser (free). In Chrome:
                           Ctrl+Shift+I -> Ctrl+Shift+P -> "Show Network" ->
                           Fetch/XHR -> click to page 2 of the events list ->
                           right-click the request -> Copy as cURL -> save there.
                           The bearer token inside expires in roughly a day, so
                           re-capture when the script reports 401/403.

Both files are credentials and live OUTSIDE the repo. _umami/ is gitignored.

  python3 fetch_umami.py                 # pull -> _umami/<today>/events_raw.json
  python3 fetch_umami.py --analyze       # analyse the newest pull, no network
  python3 fetch_umami.py --days 28
"""
import json, os, re, sys, time, collections, urllib.request, urllib.parse, urllib.error
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, '_umami')
SITE = 'ce2e7f7c-eb06-4865-9d46-70143943e9b6'
CURL = os.path.expanduser('~/umami_curl.txt')
KEY  = os.path.expanduser('~/.umami_key')

# Tool landing pages — an entry is a pageview of one of these with a referrer elsewhere.
TOOLS = {'/', '/index.html', '/home/', '/home/index.html', '/renters/', '/renters/index.html'}

# A crawler walking the sitemap looks like ~1.0 events per session across many pages.
# Singapore was 982 events / 976 sessions over 480 pages in the first pull.
BOT_SESSION_MAX = 1.15


def _auth():
    """Return (base_url_template, headers). Prefers the Pro API key when present."""
    if os.path.exists(KEY):
        k = open(KEY).read().strip()
        if k:
            return ('https://api.umami.is/v1/websites/%s/events' % SITE,
                    {'x-umami-api-key': k, 'accept': 'application/json'}, {})
    if os.path.exists(CURL):
        raw = open(CURL, encoding='utf-8', errors='replace').read()
        m = re.search(r"curl\s+'([^']+)'", raw) or re.search(r'curl\s+"([^"]+)"', raw)
        if not m:
            sys.exit(f'{CURL}: no quoted URL found — re-copy with "Copy as cURL".')
        url = m.group(1)
        hdrs = {h.group(1).strip(): h.group(2).strip()
                for h in re.finditer(r"-H\s+'([^:]+):\s*([^']*)'", raw)}
        hdrs.setdefault('accept', 'application/json')
        u = urllib.parse.urlparse(url)
        return (urllib.parse.urlunparse(u._replace(query='')), hdrs,
                dict(urllib.parse.parse_qsl(u.query)))
    sys.exit('No credentials. Save a captured request to ~/umami_curl.txt '
             '(see this file\'s docstring) or an API key to ~/.umami_key.')


def _get(base, hdrs, params):
    url = base + '?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=hdrs), timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit(f'HTTP {e.code}: the captured token has expired. Re-copy the request '
                     f'into {CURL} (see docstring).')
        raise


def pull(days=90):
    base, hdrs, q = _auth()
    end = datetime.now()
    start = end - timedelta(days=days)
    q.update({'startAt': int(start.timestamp() * 1000), 'endAt': int(end.timestamp() * 1000),
              'page': 1, 'pageSize': 500})
    first = _get(base, hdrs, q)
    total, ps = first.get('count', 0), first.get('pageSize', 20)
    pages = (total + ps - 1) // ps
    print(f'  {total} events, pageSize {ps} -> {pages} calls')
    rows, seen = [], set()
    for p in range(1, pages + 1):
        d = first if p == 1 else _get(base, hdrs, dict(q, page=p))
        batch = d.get('data') or []
        for r in batch:
            if r.get('id') not in seen:
                seen.add(r['id']); rows.append(r)
        if not batch:
            break
        time.sleep(0.32)                      # 50 calls / 15s limit
    outdir = os.path.join(OUT, date.today().isoformat())
    os.makedirs(outdir, exist_ok=True)
    json.dump(rows, open(os.path.join(outdir, 'events_raw.json'), 'w'), indent=1)
    print(f'  wrote {len(rows)} rows -> {outdir}/events_raw.json')
    return rows


def _newest():
    if not os.path.isdir(OUT):
        sys.exit('No pulls yet — run without --analyze first.')
    days = sorted(d for d in os.listdir(OUT) if re.match(r'\d{4}-\d{2}-\d{2}$', d))
    if not days:
        sys.exit('No pulls found in _umami/.')
    return json.load(open(os.path.join(OUT, days[-1], 'events_raw.json'))), days[-1]


def _norm(p):
    return (p or '').split('#')[0].split('?')[0] or '/'


def section(p):
    for k, v in (('why-did-my-', 'reactive'), ('/rate-changes/', 'tracker'),
                 ('/rate-filings', 'ledger'), ('/coverage', 'coverage'),
                 ('/metro/', 'metro'), ('/state/', 'state'), ('/carrier/', 'carrier'),
                 ('/compare/', 'compare')):
        if k in p:
            return v
    return 'other'


def analyze(rows, tag=''):
    print(f'\n{"="*62}\nUmami analysis {tag} — {len(rows)} events')
    by_country = collections.Counter(r.get('country') for r in rows)

    # crawler detection by events-per-session, not by country guesswork
    sess = collections.defaultdict(list)
    for r in rows:
        sess[(r.get('country'), r.get('sessionId'))].append(r)
    per_country = collections.defaultdict(lambda: [0, 0])
    for (c, _s), evs in sess.items():
        per_country[c][0] += 1
        per_country[c][1] += len(evs)
    print('\n-- traffic by country (eps = events per session; ~1.0 means a crawler) --')
    for c, n in by_country.most_common(8):
        s, e = per_country[c]
        flag = '  <-- crawler pattern' if s >= 20 and e / s <= BOT_SESSION_MAX else ''
        print(f'   {str(c):4} {n:5} events  {s:4} sessions  eps {e/max(s,1):4.1f}{flag}')

    us = [r for r in rows if r.get('country') == 'US']
    print(f'\n   US {len(us)}/{len(rows)} ({100*len(us)/max(len(rows),1):.0f}%) — everything below is US only')

    # funnel by session
    bys = collections.defaultdict(list)
    for r in us:
        bys[r['sessionId']].append(r)
    def reached(ev):
        return sum(1 for evs in bys.values() if any(e.get('eventName') == ev for e in evs))
    nres, nq = reached('results_shown'), reached('quote_clicked')
    print(f'\n-- US funnel --\n   {len(bys)} sessions\n'
          f'   {nres} reached results_shown  ({100*nres/max(len(bys),1):.1f}% of sessions)\n'
          f'   {nq} reached quote_clicked   ({100*nq/max(nres,1):.0f}% of those who saw results)')

    # the headline: which pages feed the tool
    entries = collections.Counter()
    for r in us:
        if r.get('eventName'):
            continue
        if _norm(r.get('urlPath')) in TOOLS:
            ref = _norm(r.get('referrerPath'))
            if ref and ref not in TOOLS:
                entries[ref] += 1
    sec = collections.Counter()
    for p, n in entries.items():
        sec[section(p)] += n
    print(f'\n-- tool entries by section ({sum(entries.values())} from {len(entries)} pages) --')
    for s, n in sec.most_common():
        print(f'   {s:10} {n}')
    print('\n-- top feeder pages --')
    for p, n in entries.most_common(15):
        print(f'   {n:4}  {p}')

    # content that draws US readers but never feeds the tool
    views = collections.Counter(_norm(r.get('urlPath')) for r in us if not r.get('eventName'))
    dead = [(n, p) for p, n in views.items()
            if n >= 8 and p not in TOOLS and entries.get(p, 0) == 0]
    dead.sort(reverse=True)
    print(f'\n-- read but never feeds the tool (>=8 US views, 0 entries) --')
    for n, p in dead[:12]:
        print(f'   {n:4}  {p}')
    return entries, sec, views


if __name__ == '__main__':
    if '--analyze' in sys.argv:
        rows, tag = _newest()
        analyze(rows, tag)
    else:
        d = 90
        if '--days' in sys.argv:
            d = int(sys.argv[sys.argv.index('--days') + 1])
        analyze(pull(d), date.today().isoformat())
