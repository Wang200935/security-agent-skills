#!/usr/bin/env python3
"""Try common text decodings/transforms for CTF misc puzzles.

Usage: python3 misc_decode_triage.py TEXT_OR_FILE [--file]
"""
from __future__ import annotations

import argparse
import base64
import binascii
import html
import re
import urllib.parse
from pathlib import Path

FLAG_RE = re.compile(rb"(?:flag|ctf|picoCTF|HTB)\{[^\r\n]{0,120}\}", re.I)


def score(b: bytes) -> int:
    printable = sum(32 <= x <= 126 or x in (9, 10, 13) for x in b)
    bonus = 100 if FLAG_RE.search(b) else 0
    return printable + bonus - (len(b) - printable) * 2


def as_bytes(s: str) -> bytes:
    return s.encode("utf-8", "replace")


def candidates(raw: bytes):
    text = raw.decode("utf-8", "ignore").strip()
    yield "raw", raw
    yield "url_decode", as_bytes(urllib.parse.unquote(text))
    yield "html_unescape", as_bytes(html.unescape(text))

    compact = re.sub(r"\s+", "", text)
    for name, func in [
        ("hex", binascii.unhexlify),
        ("base64", base64.b64decode),
        ("base32", base64.b32decode),
        ("base85", base64.b85decode),
    ]:
        try:
            yield name, func(compact)
        except Exception:
            pass

    # Binary ASCII: 01100110 01101100 ...
    bits = re.findall(r"[01]{8}", text)
    if bits:
        try:
            yield "binary_ascii", bytes(int(x, 2) for x in bits)
        except Exception:
            pass

    nums = re.findall(r"\b\d{2,3}\b", text)
    if nums:
        vals = []
        ok = True
        for n in nums:
            v = int(n)
            if not 0 <= v <= 255:
                ok = False
                break
            vals.append(v)
        if ok:
            yield "decimal_ascii", bytes(vals)

    # Caesar shifts for letters.
    alpha = text
    for shift in range(1, 26):
        out = []
        for ch in alpha:
            if "a" <= ch <= "z":
                out.append(chr((ord(ch) - 97 - shift) % 26 + 97))
            elif "A" <= ch <= "Z":
                out.append(chr((ord(ch) - 65 - shift) % 26 + 65))
            else:
                out.append(ch)
        yield f"caesar_-{shift}", as_bytes("".join(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--file", action="store_true")
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()

    raw = Path(args.input).read_bytes() if args.file else as_bytes(args.input)
    seen = set()
    rows = []
    for name, b in candidates(raw):
        if b in seen:
            continue
        seen.add(b)
        rows.append((score(b), name, b))
    rows.sort(reverse=True, key=lambda x: x[0])
    for sc, name, b in rows[: args.top]:
        preview = b[:300].decode("utf-8", "replace").replace("\n", "\\n")
        print(f"[{sc:4d}] {name}: {preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
