#!/usr/bin/env python3
"""Minimal pure-python PDF text extractor for SERFF filing jackets (FlateDecode text)."""
import sys, re, zlib

def extract_text(path):
    data = open(path, 'rb').read()
    out = []
    # find all stream...endstream blocks
    for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', data, re.DOTALL):
        raw = m.group(1)
        try:
            dec = zlib.decompress(raw)
        except Exception:
            continue
        # pull text from Tj and TJ operators
        # (string) Tj
        for tm in re.finditer(rb'\((?:[^()\\]|\\.)*\)\s*Tj', dec):
            s = tm.group(0)
            out.append(_unescape(s[:s.rfind(b')')+1]))
        # [ (a) (b) ] TJ
        for tm in re.finditer(rb'\[(.*?)\]\s*TJ', dec, re.DOTALL):
            parts = re.findall(rb'\((?:[^()\\]|\\.)*\)', tm.group(1))
            out.append(''.join(_unescape(p) for p in parts))
    return '\n'.join(out)

def _unescape(b):
    # b is like (text)
    b = b[b.find(b'(')+1:b.rfind(b')')]
    b = b.replace(b'\\(', b'(').replace(b'\\)', b')').replace(b'\\\\', b'\\')
    b = b.replace(b'\\n', b' ').replace(b'\\r', b' ').replace(b'\\t', b' ')
    try:
        return b.decode('latin-1')
    except Exception:
        return b.decode('utf-8', 'replace')

if __name__ == '__main__':
    print(extract_text(sys.argv[1]))
