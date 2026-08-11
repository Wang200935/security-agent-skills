#!/usr/bin/env python3
"""First-pass triage for CTF reverse engineering artifacts.

Usage: python3 rev_triage.py FILE
Does not execute the artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

SUSPICIOUS = [
    b"strcmp", b"strncmp", b"memcmp", b"ptrace", b"IsDebuggerPresent",
    b"flag", b"CTF{", b"picoCTF", b"Base64", b"AES", b"RC4", b"xor",
    b"/bin/sh", b"system", b"exec", b"eval", b"password", b"license",
]

MAGICS = {
    b"\x7fELF": "ELF",
    b"MZ": "PE/DOS",
    b"\xca\xfe\xba\xbe": "Mach-O fat / Java class depending context",
    b"\xfe\xed\xfa": "Mach-O",
    b"PK\x03\x04": "ZIP/APK/JAR/Python wheel-like archive",
    b"\x00asm": "WebAssembly",
}


def printable_strings(data: bytes, min_len: int = 5) -> list[str]:
    return [m.group().decode("latin1", "replace") for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, data)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--max-strings", type=int, default=120)
    args = ap.parse_args()
    p = Path(args.file)
    data = p.read_bytes()

    print(f"path: {p}")
    print(f"size: {len(data)} bytes")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")
    print(f"magic16: {data[:16].hex()}")
    for magic, label in MAGICS.items():
        if data.startswith(magic):
            print(f"format_hint: {label}")

    print("\nsuspicious markers:")
    any_marker = False
    low = data.lower()
    for marker in SUSPICIOUS:
        idx = low.find(marker.lower())
        if idx >= 0:
            any_marker = True
            print(f"  offset {idx}: {marker.decode('latin1', 'replace')}")
    if not any_marker:
        print("  none")

    ss = printable_strings(data)
    ranked = sorted(ss, key=lambda s: ("flag" not in s.lower(), "ctf" not in s.lower(), len(s)))
    print(f"\nstrings ({min(len(ranked), args.max_strings)}/{len(ranked)}):")
    for s in ranked[: args.max_strings]:
        print("  " + s[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
