#!/usr/bin/env python3
"""
建立加密 Keepass 資料庫 — Hermes 2026-07-19
用途: 保護暗網研究期間收集到的 credentials、URL、筆記。

不採用人類密碼 — 改用隨機 32-byte key 儲存到 OS keychain (macOS Keychain),
開 DB 時從 keychain 取。使用者也可改成本地 file 模式 (受 file permission 保護)。

輸出: ~/Documents/darkweb-research/keepass/research.kdbx
     + keychain 中的 'darkweb-research-kp-key'
"""
import os
import secrets
import subprocess
import sys
from pathlib import Path

from pykeepass import PyKeePass, create_database

DB_PATH = Path("${DARKWEB_HOME:-./darkweb-research}/keepass/research.kdbx")
KEYCHAIN_NAME = "darkweb-research-kp-key"


def get_or_create_key() -> str:
    """從 macOS Keychain 取或建 random 32-byte"""
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", KEYCHAIN_NAME],
            capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            print(f"[*] 從 Keychain 取得現有 key", file=sys.stderr)
            return out.stdout.strip()
    except Exception:
        pass
    # 建立
    key = secrets.token_urlsafe(32)
    subprocess.run(
        ["security", "add-generic-password", "-a", os.environ["USER"],
         "-s", KEYCHAIN_NAME, "-w", key], check=True)
    print(f"[*] 已建立 Keychain 項目 '{KEYCHAIN_NAME}'", file=sys.stderr)
    return key


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    pwd = get_or_create_key()
    if DB_PATH.exists():
        print(f"[!] DB 已存在: {DB_PATH}", file=sys.stderr)
        kp = PyKeePass(str(DB_PATH), password=pwd)
    else:
        kp = create_database(str(DB_PATH), password=pwd)
        # 建立預設 groups
        kp.add_group(kp.root_group, "Onion URLs")
        kp.add_group(kp.root_group, "Credentials")
        kp.add_group(kp.root_group, "Notes")
        kp.add_group(kp.root_group, "Investigation Logs")
        kp.save()
        print(f"[*] 建立 Keepass DB: {DB_PATH}", file=sys.stderr)

    # 加範例 entry
    grp = kp.find_groups(name="Onion URLs", first=True)
    if grp and not kp.find_entries(title="Tor circuit sample", first=True):
        kp.add_entry(grp, title="Tor circuit sample",
                     username="",
                     password="",
                     url="check.torproject.org",
                     notes="Sample. Replace with real entries.")
        kp.save()
        print(f"[*] 新增 1 sample entry", file=sys.stderr)

    # 檢查
    print(f"\n=== Keepass DB 狀態 ===")
    print(f"路徑: {DB_PATH}")
    print(f"size: {DB_PATH.stat().st_size} bytes")
    print(f"加密: AES-256 (pykeepass default)")
    print(f"Keychain item: {KEYCHAIN_NAME}")
    print(f"\nGroups:")
    for g in kp.groups:
        print(f"  - {g.name}  ({len(g.entries)} entries)")


if __name__ == "__main__":
    main()
