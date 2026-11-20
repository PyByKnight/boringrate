"""Footer: mention referral links + add ADVERTISING DISCLOSURE link (-> editorial-standards §02).
Idempotent text replace inside the .legal footer line only."""
import glob, sys
OLD = ('MAY EARN MONEY FROM ADVERTISING AND SPONSORED PLACEMENTS; RANKINGS AND RATE ESTIMATES ARE NEVER ORDERED OR CHANGED BY PAYMENT.',
       '<a href="/privacy.html" style="color:inherit;">PRIVACY POLICY</a>.')
NEW = ('MAY EARN MONEY FROM ADVERTISING, SPONSORED PLACEMENTS, AND REFERRAL LINKS; RANKINGS AND RATE ESTIMATES ARE NEVER ORDERED OR CHANGED BY PAYMENT.',
       '<a href="/editorial-standards.html#independence" style="color:inherit;">ADVERTISING DISCLOSURE</a> &middot; <a href="/privacy.html" style="color:inherit;">PRIVACY POLICY</a>.')
n = 0
for f in glob.glob('**/*.html', recursive=True):
    if f.startswith('node_modules'): continue
    s = open(f).read()
    if OLD[0] not in s: continue
    i = s.index(OLD[0]); seg_end = s.index('</div>', i)
    seg = s[i:seg_end]
    assert seg.count(OLD[1]) == 1, f
    s = s[:i] + seg.replace(*[OLD[0], NEW[0]]).replace(OLD[1], NEW[1]) + s[seg_end:]
    open(f, 'w').write(s); n += 1
print('patched', n)
