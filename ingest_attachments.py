#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ingest SERFF zips pulled WITH attachments, and find the per-coverage exhibits.

Normal pulls take the jacket only. This handles the other case: a zip that also contains
`Rate-Rule Attachments/` and `Supporting Document Attachments/` — which is where the
per-coverage tables actually live ("Exhibit L - Impact of Rate Change by Coverage and
Component"). See backfill_coverage_changes.py --pull-list for which filings to pull.

Extracts every PDF (jacket + attachments), runs BOTH text extractors and keeps the better
result — attachments are frequently subset-CID-font exports that the jacket extractor returns
empty on, which reads as "no text" rather than "wrong decoder" — then reports which files
actually contain a parseable coverage table so the reading pass is targeted.

Text lands in `_serff/<STATE>_att_txt/<TRACKING>__<attachment name>.txt`, which keeps it beside
the existing `<STATE>_txt/` jackets and inside the `*_txt` glob that mine_filing_text.py and
serff_compact.py already walk.

  python3 ingest_attachments.py VA                 # ingest ~/*.zip as Virginia
  python3 ingest_attachments.py MI --keep-pdfs     # don't delete PDFs after extraction
"""
import sys, os, re, glob, zipfile, shutil, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
COVER = re.compile(r'bodily\s+injury|property\s+damage|comprehensive|collision|'
                   r'uninsured|underinsured|medical\s+payments|med\s*pay|\bPIP\b', re.I)
PCT = re.compile(r'[-+]?\d+(?:\.\d+)?\s*%')

sys.path.insert(0, ROOT)
import serff_pdftext
import serff_pdftext_cid


def extract(pdf):
    best = ''
    for fn in (serff_pdftext.extract_text, serff_pdftext_cid.extract):
        try:
            t = fn(pdf)
        except Exception:
            t = ''
        if len(t) > len(best):
            best = t
    return best


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.exit('usage: python3 ingest_attachments.py <STATE> [--keep-pdfs]')
    state = args[0].upper()
    keep = '--keep-pdfs' in sys.argv

    zips = [z for z in glob.glob(os.path.join(HOME, '*.zip'))
            if not os.path.basename(z).startswith('boringrate.com-')]
    if not zips:
        sys.exit(f'no SERFF zips in {HOME}')

    out_txt = os.path.join(ROOT, '_serff', f'{state}_att_txt')
    tmp = os.path.join(ROOT, '_serff', f'_tmp_{state}')
    os.makedirs(out_txt, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)

    hits, plain, n_pdf = [], [], 0
    for z in sorted(zips):
        trk = re.sub(r' \(\d+\)$', '', os.path.basename(z)[:-4])
        try:
            zf = zipfile.ZipFile(z)
        except Exception as e:
            print(f'  SKIP {os.path.basename(z)}: {e}')
            continue
        for member in zf.namelist():
            if not member.lower().endswith('.pdf'):
                continue
            if 'usage agreement' in member.lower():
                continue
            name = os.path.basename(member.replace('\\', '/'))
            dest = os.path.join(tmp, f'{trk}__{name}')
            try:
                with zf.open(member) as src, open(dest, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
            except Exception as e:
                print(f'  SKIP {member}: {e}')
                continue
            n_pdf += 1
            body = extract(dest)
            if len(body) < 200:
                plain.append((trk, name, len(body)))
            else:
                safe = re.sub(r'[^A-Za-z0-9._-]+', '_', name)[:80]
                tp = os.path.join(out_txt, f'{trk}__{safe}.txt')
                open(tp, 'w', encoding='utf-8').write(body)
                # does this file carry an actual coverage table?
                cov = len(COVER.findall(body))
                pcts = len(PCT.findall(body))
                if cov >= 3 and pcts >= 3:
                    hits.append((trk, name, cov, pcts, tp))
            if not keep:
                os.remove(dest)
    if not keep and os.path.isdir(tmp) and not os.listdir(tmp):
        os.rmdir(tmp)

    print(f'\n{len(zips)} zips, {n_pdf} PDFs -> text in _serff/{state}_att_txt/')
    if plain:
        print(f'\n{len(plain)} files produced no text (scanned/raster — need a visual read):')
        for trk, name, n in plain[:12]:
            print(f'   {trk}  {name[:56]}  ({n} chars)')

    print(f'\n★ {len(hits)} file(s) look like a per-coverage table '
          f'(>=3 coverage terms AND >=3 percentages):')
    for trk, name, cov, pcts, tp in sorted(hits, key=lambda x: -x[2]):
        print(f'   {trk:<20} {name[:50]:<50} cov={cov} pct={pcts}')
        print(f'      {tp}')
    if hits:
        print('\nNext: read those files, then add verified splits to VERIFIED in '
              'backfill_coverage_changes.py and run it.')


if __name__ == '__main__':
    main()
