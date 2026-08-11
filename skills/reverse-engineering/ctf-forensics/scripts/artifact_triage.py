#!/usr/bin/env python3
"""First-pass artifact triage for CTF forensics.

Usage: python3 artifact_triage.py FILE
Outputs hashes, size, magic bytes, simple entropy, printable strings, and marker hints.
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
from pathlib import Path

MARKERS = {
    b"PK\x03\x04": "zip archive marker",
    b"%PDF": "PDF marker",
    b"\x89PNG\r\n\x1a\n": "PNG marker",
    b"JFIF": "JPEG/JFIF marker",
    b"ID3": "MP3 ID3 marker",
    b"flag{": "flag-like marker",
    b"CTF{": "flag-like marker",
    b"picoCTF{": "picoCTF marker",
}


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    ent = 0.0
    for c in counts:
        if c:
            p = c / len(data)
            ent -= p * math.log2(p)
    return ent


def strings(data: bytes, min_len: int = 5) -> list[str]:
    pat = rb"[\x20-\x7e]{%d,}" % min_len
    return [m.group().decode("latin1", "replace") for m in re.finditer(pat, data)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--max-strings", type=int, default=80)
    args = ap.parse_args()
    p = Path(args.file)
    data = p.read_bytes()

    print(f"path: {p}")
    print(f"size: {len(data)} bytes")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")
    print(f"md5: {hashlib.md5(data).hexdigest()}")
    print(f"magic16: {data[:16].hex()}")
    print(f"entropy: {entropy(data):.3f} bits/byte")

    print("\nmarkers:")
    found = False
    for marker, desc in MARKERS.items():
        idx = data.find(marker)
        if idx >= 0:
            found = True
            print(f"  offset {idx}: {desc} ({marker!r})")
    if not found:
        print("  none of built-in markers found")

    ss = strings(data)
    print(f"\nstrings ({min(len(ss), args.max_strings)}/{len(ss)}):")
    for s in ss[: args.max_strings]:
        print("  " + s[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
