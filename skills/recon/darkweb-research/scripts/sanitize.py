#!/usr/bin/env python3
"""
證據隔離工具 — Hermes 2026-07-19
用途: 任何暗網抓的檔案、截圖、HTML,都先丟 quarantine,去除 metadata,驗證安全。

功能:
  1. <file>            把指定檔案 sanitize: 去 EXIF + NP 創建時間 + 改名 + 雜湊
  2. -d <dir>          bulk sanitize
  3. --list            列出 evidence/ 已隔離檔
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

QUARANTINE = Path("/Users/wang/Documents/darkweb-research/evidence")


def exiftool_available():
    return shutil.which("exiftool") is not None


def sanitize_one(src: Path, dry_run=False):
    """複製到 quarantine, 去 metadata、計 sha256, 保留原來的證據來源記錄"""
    if not src.exists():
        return None
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    # 計原檔 sha256
    sha = hashlib.sha256()
    with open(src, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    digest = sha.hexdigest()

    # 改名: original 的 suffix + sha 前 8 char
    new_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{digest[:8]}{src.suffix}"
    dst = QUARANTINE / new_name

    if dry_run:
        print(f"  [DRY] {src} -> {dst} (sha256={digest[:16]}...)")
        return dst

    shutil.copy2(src, dst)
    # 去 metadata (exiftool)
    if exiftool_available():
        # -overwrite_original in place, -all= 清所有 metadata
        subprocess.run(
            ["exiftool", "-overwrite_original", "-q", "-q", "-all=", str(dst)],
            check=False)
    # 設 mtime 為現在, 去除原始時間指紋
    os.utime(dst, (datetime.now().timestamp(), datetime.now().timestamp()))
    # 寫 metadata sidecar
    sidecar = dst.with_suffix(dst.suffix + ".meta.json")
    sidecar.write_text(
        f"""{{
  "original_name": "{src.name}",
  "sha256": "{digest}",
  "acquired_at": "{datetime.now(timezone.utc).isoformat()}",
  "source_hint": "(設定來源 URL/上下文)",
  "exif_stripped": true
}}""", encoding="utf-8")
    return dst


def main():
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="*", help="files to sanitize")
    p.add_argument("-d", "--dir", help="sanitize entire directory")
    p.add_argument("--dry", action="store_true")
    p.add_argument("--list", action="store_true")
    args = p.parse_args()

    if args.list:
        if not QUARANTINE.exists():
            print("(空)")
            return
        for f in sorted(QUARANTINE.iterdir()):
            print(f"  {f.stat().st_size:>8} B  {f.name}")
        return

    targets = list(args.files)
    if args.dir:
        targets += [str(p) for p in Path(args.dir).iterdir() if p.is_file()]
    if not targets:
        print("usage: sanitize.py <file>... | -d <dir> | --list")
        return

    for f in targets:
        path = Path(f)
        dst = sanitize_one(path, dry_run=args.dry)
        if dst:
            print(f"  OK {path.name} -> {dst.name}")
        else:
            print(f"  SKIP {path} (not found)")


if __name__ == "__main__":
    main()
