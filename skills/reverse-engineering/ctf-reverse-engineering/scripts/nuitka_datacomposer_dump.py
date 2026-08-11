#!/usr/bin/env python3
"""Dump constants from Nuitka DataComposer blobs.

Usage:
  python3 scripts/nuitka_datacomposer_dump.py payload.bin [start_offset]

This is intentionally partial: it recovers enough constants for CTF reversing
(function names, large ints, tuples, bytes, password hashes, file magic) without
trying to fully reconstruct Nuitka native code.
"""
from __future__ import annotations

from pathlib import Path
import reprlib
import struct
import sys


class Reader:
    def __init__(self, data: bytes):
        self.b = data
        self.i = 0
        self.last = None

    def read1(self) -> int:
        if self.i >= len(self.b):
            raise EOFError("read past end")
        c = self.b[self.i]
        self.i += 1
        return c

    def var(self) -> int:
        shift = 0
        out = 0
        while True:
            c = self.read1()
            out |= (c & 0x7F) << shift
            if c < 0x80:
                return out
            shift += 7

    def c_string(self) -> bytes:
        j = self.b.index(0, self.i)
        out = self.b[self.i:j]
        self.i = j + 1
        return out

    def obj(self):
        pos = self.i
        tag = self.read1()
        if tag == ord("."):
            raise EOFError("end marker")
        if tag == ord("p"):
            return self.last

        def setlast(value):
            self.last = value
            return value

        if tag == ord("n"):
            return setlast(None)
        if tag == ord("t"):
            return setlast(True)
        if tag == ord("F"):
            return setlast(False)
        if tag == ord("T"):
            n = self.var(); self.last = None
            return setlast(tuple(self.obj() for _ in range(n)))
        if tag == ord("L"):
            n = self.var(); self.last = None
            return setlast([self.obj() for _ in range(n)])
        if tag == ord("D"):
            n = self.var(); self.last = None
            keys = [self.obj() for _ in range(n)]
            self.last = None
            vals = [self.obj() for _ in range(n)]
            return setlast(dict(zip(keys, vals)))
        if tag == ord("S"):
            n = self.var(); self.last = None
            return setlast(set(self.obj() for _ in range(n)))
        if tag == ord("P"):
            n = self.var(); self.last = None
            return setlast(frozenset(self.obj() for _ in range(n)))
        if tag == ord("l"):
            return setlast(self.var())
        if tag == ord("q"):
            return setlast(-self.var())
        if tag in (ord("g"), ord("G")):
            n = self.var(); x = 0
            for _ in range(n):
                x = (x << 31) + self.var()
            return setlast(-x if tag == ord("G") else x)
        if tag == ord("i"):
            return setlast(self.var())
        if tag == ord("I"):
            return setlast(-self.var())
        if tag == ord("f"):
            v = struct.unpack("d", self.b[self.i:self.i+8])[0]
            self.i += 8
            return setlast(v)
        if tag == ord("s"):
            return setlast("")
        if tag == ord("w"):
            return setlast(chr(self.read1()))
        if tag in (ord("u"), ord("a")):
            return setlast(self.c_string().decode("utf-8", "surrogatepass"))
        if tag == ord("v"):
            n = self.var(); raw = self.b[self.i:self.i+n]; self.i += n
            return setlast(raw.decode("utf-8", "surrogatepass"))
        if tag == ord("d"):
            return setlast(bytes([self.read1()]))
        if tag == ord("c"):
            return setlast(self.c_string())
        if tag == ord("b"):
            n = self.var(); raw = self.b[self.i:self.i+n]; self.i += n
            return setlast(raw)
        if tag == ord("B"):
            n = self.var(); raw = bytearray(self.b[self.i:self.i+n]); self.i += n
            return setlast(raw)
        if tag == ord(":"):
            self.last = None
            return setlast(("slice", self.obj(), self.obj(), self.obj()))
        if tag == ord(";"):
            self.last = None
            return setlast(("range", self.obj(), self.obj(), self.obj()))
        if tag == ord("X"):
            n = self.var(); raw = self.b[self.i:self.i+n]; self.i += n
            return setlast(("blob", raw))
        if tag == ord("C"):
            flags = self.var(); name = self.obj(); line = self.var() + 1
            varnames = self.obj(); argc = self.var()
            qualprefix = self.obj() if (flags & 1) else None
            free = self.obj() if (flags & 2) else None
            kwonly = self.var() + 1 if (flags & 4) else None
            posonly = self.var() + 1 if (flags & 8) else None
            return setlast({
                "code": True, "flags": flags, "name": name, "line": line,
                "varnames": varnames, "argc": argc, "qualprefix": qualprefix,
                "free": free, "kwonly": kwonly, "posonly": posonly,
            })
        raise ValueError(f"bad tag {tag:02x} {chr(tag)!r} at {pos:x}")


def parse_chunks(data: bytes, start: int = 0):
    pos = start
    while pos < len(data):
        nul = data.find(b"\0", pos)
        if nul < 0 or nul + 5 > len(data):
            break
        name_bytes = data[pos:nul]
        if not name_bytes or any(c < 32 or c > 126 for c in name_bytes):
            break
        try:
            name = name_bytes.decode("utf-8")
        except UnicodeDecodeError:
            break
        size = struct.unpack_from("<I", data, nul + 1)[0]
        part_start = nul + 5
        part_end = part_start + size
        if size <= 1 or part_end > len(data):
            break
        part = data[part_start:part_end]
        count = struct.unpack_from("<H", part, 0)[0]
        r = Reader(part[2:])
        objs = []
        err = None
        try:
            for _ in range(count):
                objs.append(r.obj())
        except Exception as exc:  # keep partial output useful
            err = f"{type(exc).__name__}: {exc} at reader offset 0x{r.i:x}"
        yield name, pos, size, count, objs, err
        pos = part_end


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    data = Path(argv[1]).read_bytes()
    start = int(argv[2], 0) if len(argv) > 2 else 0
    chunks = list(parse_chunks(data, start))
    print(f"chunks {len(chunks)}")
    for idx, (name, pos, size, count, objs, err) in enumerate(chunks):
        print(f"\nCHUNK {idx} {name!r} pos=0x{pos:x} size={size} count={count} parsed={len(objs)} err={err}")
        interesting = name in {"__main__", ".__main__", "__parents_main__"} or any(
            needle in repr(objs) for needle in ("derive_", "PASSWORD", "flag", "enc.bin", "data.bin")
        )
        if interesting:
            for i, obj in enumerate(objs):
                print(f"  {i:4d} {type(obj).__name__:10s} {reprlib.repr(obj)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
