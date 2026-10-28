#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pull Umami Cloud analytics to _umami/<date>/ — no clicking, no 234 pages of copy-paste.

The Umami UI shows the activity stream a page at a time and will not export event
PROPERTIES (the state / from_path / carrier fields our events carry), which are the
only reason the export is worth having. The API returns them.

  Base URL : https://api.umami.is/v1
  Auth     : x-umami-api-key: <key>
  Limit    : 50 calls / 15 seconds (we sleep to stay under it)

KEY HANDLING. The key is a credential: it is read from $UMAMI_API_KEY or
~/.umami_key and is never accepted on the command line (argv leaks into shell
history and ps). _umami/ is gitignored, same as _gsc/ and _serff/.

  export UMAMI_API_KEY=...        # or: echo '<key>' > ~/.umami_key && chmod 600 ~/.umami_key
  python3 fetch_umami.py --probe  # report which endpoints this account exposes
  python3 fetch_umami.py          # pull last 90 days -> _umami/<today>/
  python3 fetch_umami.py --days 28
"""
import json, os, sys, time, urllib.request, urllib.error, urllib.parse
from datetime import date, datetime, timedelta

BASE = 'https://api.umami.is/v1'
SITE = 'ce2e7f7c-eb06-4865-9d46-70143943e9b6'   # from data-website-id in the page source
OUT  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_umami')
PAUSE = 0.35                                     # 50 calls / 15s = 0.3s floor


def api_key():
    k = os.environ.get('UMAMI_API_KEY')
    if k:
        return k.strip()
    p = os.path.expanduser('~/.umami_key')
    if os.path.exists(p):
        return open(p).read().strip()
    sys.exit('No API key. Set $UMAMI_API_KEY or write it to ~/.umami_key (chmod 600).\n'
             'Umami Cloud -> Settings -> API keys.')


def get(path, params=None, key=None):
    url = f'{BASE}{path}'
    if params:
        url += '?' + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers={
        'x-umami-api-key': key, 'Accept': 'application/json',
        'User-Agent': 'boringrate-fetch-umami/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode()), None
    except urllib.error.HTTPError as e:
        return None, f'HTTP {e.code}'
    except Exception as e:
        return None, str(e)[:90]


def ms(d):
    """Umami wants epoch milliseconds."""
    return int(datetime.combine(d, datetime.min.time()).timestamp() * 1000)


def main():
    key = api_key()
    days = 90
    if '--days' in sys.argv:
        days = int(sys.argv[sys.argv.index('--days') + 1])
    end, start = date.today() + timedelta(days=1), date.today() - timedelta(days=days)
    at = {'startAt': ms(start), 'endAt': ms(end)}

    # Endpoint names have shifted across Umami versions, so probe rather than assume.
    jobs = [
        ('stats',            f'/websites/{SITE}/stats',       dict(at)),
        ('events_series',    f'/websites/{SITE}/events',      dict(at, unit='day', timezone='America/New_York')),
        ('event_names',      f'/websites/{SITE}/metrics',     dict(at, type='event')),
        ('urls',             f'/websites/{SITE}/metrics',     dict(at, type='url',      limit=500)),
        ('referrers',        f'/websites/{SITE}/metrics',     dict(at, type='referrer', limit=200)),
        ('countries',        f'/websites/{SITE}/metrics',     dict(at, type='country',  limit=200)),
        ('devices',          f'/websites/{SITE}/metrics',     dict(at, type='device',   limit=50)),
        ('pageviews',        f'/websites/{SITE}/pageviews',   dict(at, unit='day', timezone='America/New_York')),
        ('event_fields',     f'/websites/{SITE}/event-data/fields',  dict(at)),
        ('event_data_stats', f'/websites/{SITE}/event-data/stats',   dict(at)),
        ('sessions',         f'/websites/{SITE}/sessions',    dict(at, pageSize=1000)),
    ]

    if '--probe' in sys.argv:
        print(f'probing {len(jobs)} endpoints ({start} -> {date.today()})\n')
        for name, path, params in jobs:
            data, err = get(path, params, key)
            n = (len(data) if isinstance(data, list)
                 else len(data.get('data', [])) if isinstance(data, dict) and 'data' in data
                 else ('obj' if data is not None else 0))
            print(f'  {name:18} {"OK " if err is None else "-- "} {err or n}')
            time.sleep(PAUSE)
        return

    outdir = os.path.join(OUT, date.today().isoformat())
    os.makedirs(outdir, exist_ok=True)
    got = {}
    for name, path, params in jobs:
        data, err = get(path, params, key)
        if err:
            print(f'  {name:18} skipped ({err})')
        else:
            json.dump(data, open(os.path.join(outdir, name + '.json'), 'w'), indent=1)
            got[name] = data
            n = len(data) if isinstance(data, list) else len(data.get('data', [])) if isinstance(data, dict) and 'data' in data else 1
            print(f'  {name:18} wrote {n}')
        time.sleep(PAUSE)

    # Per-event property values — the whole point of using the API over the UI.
    names = []
    if isinstance(got.get('event_names'), list):
        names = [e.get('x') for e in got['event_names'] if e.get('x')]
    for ev in names:
        for prop in ('state', 'product', 'from_path', 'source', 'carrier', 'path', 'segment'):
            data, err = get(f'/websites/{SITE}/event-data/values',
                            dict(at, eventName=ev, propertyName=prop), key)
            if not err and data:
                fn = f'evprop_{ev}__{prop}.json'
                json.dump(data, open(os.path.join(outdir, fn), 'w'), indent=1)
                print(f'  {ev}.{prop}: {len(data)} values')
            time.sleep(PAUSE)

    latest = os.path.join(OUT, 'latest')
    if os.path.islink(latest) or os.path.exists(latest):
        try: os.remove(latest)
        except IsADirectoryError: pass
    try: os.symlink(date.today().isoformat(), latest)
    except Exception: pass
    print(f'\n-> {outdir}')


if __name__ == '__main__':
    main()
