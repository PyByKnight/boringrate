#!/usr/bin/env python3
"""Compact _serff/: extract every jacket/attachment PDF to text, then drop the PDFs.

SERFF PDFs are bulky (~32MB for 10 states) and re-downloadable from the portal, but the
text is not re-derivable once deleted and carries context the ledger JSON does not:
program scope, DOI objection letters, supporting-document schedules (which is how you
tell "no actuarial memo exists" from "we didn't download it"), and rate-manual base rates.

So: text is the durable artifact, the PDF is the cache. Run after a pull is parsed and
appended. Refuses to delete a PDF whose extraction failed, so a bad decode never silently
destroys the source.

  python3 serff_compact.py            # dry run — show what would happen
  python3 serff_compact.py --apply    # extract missing text, then delete extracted PDFs

Text goes to a sibling `<dir>_txt/` directory, matching the existing VA_home_txt/NJ_txt layout.
"""
import sys, pathlib, shutil

import serff_pdftext
import serff_pdftext_cid

ROOT = pathlib.Path(__file__).parent / "_serff"
MIN_CHARS = 200          # below this the extraction is presumed failed, PDF is kept
APPLY = "--apply" in sys.argv


def extract(pdf):
    """Jacket extractor first, CID extractor second — return the better of the two."""
    best = ""
    for fn in (serff_pdftext.extract_text, serff_pdftext_cid.extract):
        try:
            t = fn(str(pdf))
        except Exception:
            t = ""
        if len(t) > len(best):
            best = t
    return best


def main():
    if not ROOT.exists():
        sys.exit(f"{ROOT} not found")
    pdfs = sorted(ROOT.rglob("*.pdf"))
    if not pdfs:
        print("no PDFs under _serff/ — already compacted")
        return

    wrote = reused = kept = 0
    freed = 0
    to_delete = []
    for pdf in pdfs:
        src_dir = pdf.parent
        txt_dir = src_dir.parent / (src_dir.name + "_txt") if not src_dir.name.endswith("_txt") else src_dir
        txt = txt_dir / (pdf.stem + ".txt")
        if txt.exists() and len(txt.read_text(encoding="utf-8", errors="replace")) >= MIN_CHARS:
            reused += 1
            to_delete.append(pdf)
            freed += pdf.stat().st_size
            continue
        body = extract(pdf)
        if len(body) < MIN_CHARS:
            kept += 1
            print(f"  KEEP (extract failed, {len(body)} chars): {pdf.relative_to(ROOT)}")
            continue
        if APPLY:
            txt_dir.mkdir(parents=True, exist_ok=True)
            txt.write_text(body, encoding="utf-8")
        wrote += 1
        to_delete.append(pdf)
        freed += pdf.stat().st_size

    print(f"\n{len(pdfs)} PDFs: {wrote} newly extracted, {reused} already had text, {kept} kept (no text)")
    print(f"{'freed' if APPLY else 'would free'}: {freed / 1e6:.1f} MB")
    if APPLY:
        for pdf in to_delete:
            pdf.unlink()
        for d in sorted({p.parent for p in to_delete}):
            if d.exists() and not any(d.iterdir()):
                shutil.rmtree(d)
        print("PDFs deleted; text retained.")
    else:
        print("dry run — re-run with --apply")


if __name__ == "__main__":
    main()
