#!/usr/bin/env python3
"""SERFF attachment text extractor for CID/subset-font PDFs.

serff_pdftext.py handles jackets, whose text is literal `(string) Tj`. Rate manuals and
factor pages exported from Word/Excel instead use subset CID fonts: the text is hex glyph
IDs (`<0057><018C> TJ`) with a ToUnicode CMap mapping glyph -> character. Those return
EMPTY from the jacket extractor, which reads as "no text" rather than "wrong decoder".

Builds the glyph->unicode map from every embedded CMap, then decodes the hex strings.
Maps are merged across fonts; subset fonts in one document normally agree on glyph IDs
because they come from the same source font, but see --per-font if output looks scrambled.
"""
import sys, re, zlib


def _streams(data):
    for m in re.finditer(rb'stream\r?\n', data):
        s = m.end()
        e = data.find(b'endstream', s)
        if e < 0:
            continue
        try:
            yield zlib.decompress(data[s:e])
        except Exception:
            continue


def build_cmap(data):
    """glyph id (int) -> unicode str, merged over every CMap in the file."""
    cmap = {}
    for dec in _streams(data):
        if b'beginbfchar' not in dec and b'beginbfrange' not in dec:
            continue
        txt = dec.decode('latin-1')
        for blk in re.findall(r'beginbfchar(.*?)endbfchar', txt, re.S):
            for src, dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
                cmap[int(src, 16)] = _uni(dst)
        for blk in re.findall(r'beginbfrange(.*?)endbfrange', txt, re.S):
            for lo, hi, dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
                lo, hi, base = int(lo, 16), int(hi, 16), int(dst, 16)
                for i in range(lo, min(hi, lo + 65535) + 1):
                    cmap[i] = _uni(f'{base + i - lo:04X}')
    return cmap


def _uni(h):
    try:
        return ''.join(chr(int(h[i:i + 4], 16)) for i in range(0, len(h), 4))
    except ValueError:
        return ''


def extract(path):
    data = open(path, 'rb').read()
    cmap = build_cmap(data)
    if not cmap:
        return ''
    out = []
    for dec in _streams(data):
        if b'Tj' not in dec and b'TJ' not in dec:
            continue
        txt = dec.decode('latin-1')
        # Text is positioned per-line via Tm; treat each BT/ET block as its own run and
        # each Tm as a break, so table cells don't run together into one blob.
        for blk in re.split(r'\bET\b', txt):
            if 'Tj' not in blk and 'TJ' not in blk:
                continue
            line = []
            for seg in re.split(r'\bTm\b', blk):
                buf = []
                for hexstr in re.findall(r'<([0-9A-Fa-f]+)>', seg):
                    buf.append(''.join(cmap.get(int(hexstr[i:i + 4], 16), '')
                                       for i in range(0, len(hexstr), 4)))
                s = ''.join(buf).strip()
                if s:
                    line.append(s)
            if line:
                out.append('\t'.join(line))
    return '\n'.join(out)


if __name__ == '__main__':
    print(extract(sys.argv[1]))
