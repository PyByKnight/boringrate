#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move every SERFF citation to the NAIC-hosted domain.

SERFF Filing Access moved from serff-sfa.naic.org/serff/sfa/ to serff-sfa.naic.org in
2026. The old host is dead, which left 2,588 dead citation links across 152 live
pages - on a site whose entire positioning is primary-source citation, every
"see the filing" link pointed nowhere.

  https://<old host>/sfa/...  ->  https://serff-sfa.naic.org/serff/sfa/...

Confirmed working: https://serff-sfa.naic.org/serff/sfa/home/GA

Also fixes a separate defect found in the same sweep: gen_reactive_pages.py and
gen_reactive_derive.py build the filingId with re.sub(r'^[A-Z]+-', ...), which
leaves the G in trackings like TRVD-G134530272 and yields filingId=134530272.
The ledgers all store the clean numeric id, so these 27 generated pages were
broken independently of the domain move.

  python3 migrate_serff_domain.py            # report
  python3 migrate_serff_domain.py --apply
"""
import os, re, sys

# Assembled at runtime so this file never contains the literal old host and
# therefore cannot rewrite its own constants (it did, on the first run).
OLD = 'filing' + 'access.serff.com/sfa/'
NEW = 'serff-sfa.naic.org/serff/sfa/'
SELF = os.path.basename(__file__)
SKIP_DIRS = {'node_modules', '.git', '_serff', '_gsc', '_umami', '__pycache__'}
EXTS = ('.html', '.py', '.json', '.md', '.xml', '.js', '.txt')

def files():
    for root, dirs, fns in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in fns:
            if fn.endswith(EXTS) and fn != SELF:
                yield os.path.join(root, fn)[2:]

def convert(s):
    n = 0
    # 1. the path-bearing form
    s2 = s.replace(OLD, NEW); n += s.count(OLD)
    # 2. bare host, with or without a trailing slash, incl. plain-text mentions
    bare = r'filing' + r'access\.serff\.com(?!/sfa/)/?'
    s3 = re.sub(bare, 'serff-sfa.naic.org/serff/sfa/', s2)
    n += len(re.findall(r'filing' + r'access\.serff\.com', s2))
    # 3. filingId=123... -> filingId=123...  (the ledgers never store the G)
    s4, g = re.subn(r'(filingId=)G(\d)', r'\1\2', s3)
    return s4, n, g

def main():
    apply = '--apply' in sys.argv
    tot = totg = nf = 0
    for f in sorted(files()):
        try:
            s = open(f, encoding='utf-8').read()
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        if OLD.split('/')[0] not in s and 'filingId=G' not in s:
            continue
        out, n, g = convert(s)
        if out == s:
            continue
        nf += 1; tot += n; totg += g
        if apply:
            open(f, 'w', encoding='utf-8').write(out)
    print(f"{'APPLIED' if apply else 'DRY RUN'}: {nf} files, {tot} domain rewrites, {totg} G-prefix fixes")

if __name__ == '__main__':
    main()
