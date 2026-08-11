#!/usr/bin/env python3
"""
darksearch.py — 暗網 URL 索引/搜尋工具 — Hermes 2026-07-19

兩個模式:
  index  : 從 Ahmia 全 URL 清單讀入, 按站名 prefix 篩掉非法類別,
           逐個探測 + 擷取 title, 建立本地 sqlite 索引
  search : 對本地索引做 title/url 包含查詢

索引 schema:
  urls(url PRIMARY KEY, title TEXT, http_code INT, size INT, elapsed REAL,
        probed_at TEXT, category TEXT)

  category 透過站名 prefix heuristic:
    news/forum/wiki/freedrop/leaks/privacy/search/market/scam/spam/other

用法:
  python3 darksearch.py index /tmp/ahmia-urls.txt --db ~/Documents/darkweb-research/scans/idx.db
  python3 darksearch.py search privacy --db ~/Documents/darkweb-research/scans/idx.db
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# 沿用 onion_probe 的 Tor 路由
import socks
import urllib.request

PROXY = ("127.0.0.1", 9050)
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

# 排除非法/低價值 prefix (站名從 URL hostname 推)
BAD_PREFIXES = {
    "drug", "dark", "deep", "cann", "card", "hack", "black", "wolf", "silver",
    "2222",                          # spam 系列
}
GOOD_PREFIXES = {
    "wiki", "news", "bbc", "nyt", "pro", "guard", "leak", "secure", "tor",
    "ahmia", "news", "journal", "archive", "research", "civil", "privacy",
    "eff", "freedom", "land", "piuk", "piy", "ddose", "aleph", "wikileaks",
}


def categorize(host):
    """host = hostname (no scheme)"""
    h = host.lower()
    # 先匹配 good
    for p in GOOD_PREFIXES:
        if h.startswith(p) or f"-{p}" in h or f".{p}" in h:
            return "good"
    # 再匹配 bad
    for p in BAD_PREFIXES:
        if h.startswith(p):
            return "exclude"
    return "other"


def fetch(url, timeout=45):
    info = {"code": None, "title": "", "size": 0,
            "elapsed": 0.0, "error": "", "final_url": url}
    t0 = time.time()
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(200_000)
            info["code"] = r.status
            info["size"] = len(body)
            info["final_url"] = r.geturl()
            m = re.search(rb"<title[^>]*>(.*?)</title>", body, re.I | re.S)
            if m:
                info["title"] = m.group(1).decode("utf-8", "replace").strip()[:300]
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {str(e)[:200]}"
    info["elapsed"] = round(time.time() - t0, 2)
    return info


# Monkey-patch:讓 stdlib urllib + socket.create_connection 走 Tor SOCKS5h
# (.onion host 由 Tor 解析,不是本地 DNS)
import socks as _socks_pkg
import socket as _socket_mod

def _tor_create_connection(addr, *a, **kw):
    timeout = kw.get("timeout", 45) or (a[0] if a else 45)
    s = _socks_pkg.socksocket()
    s.set_proxy(_socks_pkg.SOCKS5, PROXY[0], PROXY[1], rdns=True)
    s.settimeout(timeout)
    s.connect(addr)
    return s

_socket_mod.create_connection = _tor_create_connection


def cmd_index(args):
    inp = Path(args.input).read_text().splitlines()
    urls = [ln.strip() for ln in inp if ln.strip() and not ln.startswith("#")]
    urls = list(dict.fromkeys(urls))                            # 去重保序
    # 篩掉 bad prefix
    filtered = []
    skip = 0
    for u in urls:
        m = re.match(r"https?://([a-z0-9]+)\.onion", u)
        if not m:
            continue
        host = m.group(1)
        cat = categorize(host)
        if cat == "exclude" and not args.include_exclude:
            skip += 1
            continue
        filtered.append((u, cat))
    if args.limit:
        filtered = filtered[: args.limit]
    print(f"[*] input {len(urls)} -> filtered {len(filtered)} (skipped {skip})",
          file=sys.stderr)

    db = sqlite3.connect(args.db)
    db.execute("""CREATE TABLE IF NOT EXISTS urls(
        url TEXT PRIMARY KEY, title TEXT, http_code INT, size INT, elapsed REAL,
        probed_at TEXT, category TEXT, error TEXT)""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_title ON urls(title)")
    db.commit()

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch, url, args.timeout): (url, cat)
                for url, cat in filtered}
        for fut in as_completed(futs):
            url, cat = futs[fut]
            info = fut.result()
            db.execute(
                "INSERT OR REPLACE INTO urls VALUES (?,?,?,?,?,?,?,?)",
                (info["final_url"], info["title"], info["code"],
                 info["size"], info["elapsed"],
                 datetime.now(timezone.utc).isoformat(), cat, info["error"]))
            db.commit()
            done += 1
            ok = "OK" if info["code"] and 200 <= info["code"] < 400 else "FAIL"
            print(f"[{done}/{len(filtered)}] {ok} {info['code']} "
                  f"{info['elapsed']}s {url[:60]} | "
                  f"{info['title'][:50] or info['error'][:50]}", file=sys.stderr)
    print(f"[*] index -> {args.db}", file=sys.stderr)


def cmd_search(args):
    db = sqlite3.connect(args.db)
    q = f"%{args.query}%"
    rows = db.execute(
        "SELECT url, title, http_code, size FROM urls "
        "WHERE title LIKE ? OR url LIKE ? "
        "ORDER BY size DESC LIMIT ?",
        (q, q, args.limit)).fetchall()
    print(f"[*] {len(rows)} results for '{args.query}':")
    for url, title, code, size in rows:
        print(f"  [{code} {size}B] {url}")
        if title:
            print(f"     title: {title}")
    if not rows:
        print("  (none — try `index` 模式先建立索引)")


# 資安相關關鍵字 (與 references/security-onion-map.md 鑑定方法一致)
SECURITY_KW = [
    "exploit", "cve-", "zero day", "0day", "payload", "shellcode",
    "metasploit", "rat", "rootkit", "implant",
    "pentest", "pen test", "penetration", "red team", "offensive",
    "ethical hacker", "hackerone", "bug bounty", "bugbounty",
    "malware", "ransomware", "botnet", "c2 ", "command control",
    "ddos", "stresser", "booter",
    "hacking services", "hack android", "hack gmail", "hire hacker",
    "leak", "breach", "dump", "database", "fullz", "cvv",
    "forum", "community", "dread", "breached", "xss.is", "raidforums",
    "osint", "shodan", "recon", "reverse dns", "ip lookup",
    "ctf", "pwn", "forensic", "crypto challenge", "steganograph",
    "stego", "vaultify",
    "mirror", "archive", "wikileaks", "ddoecrets",
    "privacy", "freedom", "civil rights", "acl", "eff",
    "security dashboard", "audit", "ssl", "tls",
    "tor project", "torbrowser",
]


def cmd_tag(args):
    """對 idx.db 做 keyword-tag 查詢, 預先定義好的 tag set 跑 WHERE LIKE UNION。
    要求**至少命中 N 個**不同 keyword 才視為該 tag (減少 false positive,
    e.g. 藥物站 title 提到 "hack" 一次不該被算成 security)。

    內建 tags:
      security   - 資安類 (見 references/security-onion-map.md)
      forum      - 論壇/社群類
      leak       - 資料外洩/leak 搜尋引擎
      news       - 新聞/吹哨 (SecureDrop 等)
      wiki       - Hidden Wiki / 目錄站
      finance    - 加密貨幣 / 自由交易市場
    """
    # 改: 收緊 keyword set (移除會被 generic site 通用命中的)
    # 並且要求多 keyword 命中 (args.min_hits)
    TAGS = {
        "security": [
            "exploit", "cve", "zero day", "0day", "shellcode",
            "metasploit", "rootkit", "implant",
            "pentest", "penetration test", "red team", "offensive security",
            "hackerone", "bug bounty", "bugbounty",
            "ransomware", "botnet", "ddos", "stresser", "booter",
            "steganograph", "stego", "vaultify", "forensic",
            "encrypted email", "securedrop", "anonymity network",
            "torproject", "tor project", "lanodan", "snapwonders", "netforge",
            "cve feed", "cve-", "audit example", "ssh-audit",
            "imageboard chan",         # owasps chan 等
            "hacked database",         # leakfind / database store
            "leaked database",         # leaklook
            "leak.cx", "leaks.cx",
        ],
        "forum":   ["forum", "board", "community", "dread",
                    "breached", "xss.is", "raidforums", "imageboard",
                    "chan"],
        "leak":    ["leaked database", "leak.cx", "leaks.cx",
                    "fullz", "cvv dumps", "dumps store", "stealer log",
                    "hacked database store"],
        "news":     ["securedrop", "press centre", "newsroom", "whistleblow"],
        "wiki":     ["hidden wiki", "link list", "onionland", "linklist"],
        "finance":  ["bitcoin escrow", "monero escrow", "multisig escrow",
                      "multivendor", "crypto voucher"],
    }
    if args.tag not in TAGS:
        print(f"[!] unknown tag: {args.tag}")
        print(f"    available tags: {', '.join(sorted(TAGS))}")
        return
    kws = [k.lower() for k in TAGS[args.tag]]
    min_hits = max(1, args.min_hits)

    db = sqlite3.connect(args.db)
    rows = db.execute(
        "SELECT url, title, http_code, size FROM urls "
        "WHERE http_code BETWEEN 200 AND 399 AND title != ''").fetchall()

    matched = []
    for url, title, code, size in rows:
        tlow = (title or "").lower()
        ulow = (url or "").lower()
        hits = sum(1 for k in kws if k in tlow or k in ulow)
        if hits >= min_hits:
            matched.append((url, title, code, size, hits))

    matched.sort(key=lambda x: (-x[4], -x[3]))                 # 命中數 desc 後 size desc

    print(f"[*] tag={args.tag}: {len(matched)} unique hits "
          f"(threshold: {min_hits} keyword matches)")
    for url, title, code, size, hits in matched[:args.limit]:
        print(f"  [{code} {size:>7}B hits={hits}] "
              f"{title[:55] if title else '(no title)':55s}")
        print(f"                       {url[:100]}")
    if not matched:
        print("  (none — try `index` 先建立索引, 確認 idx.db 有資料)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", default=os.path.expanduser(
        "~/Documents/darkweb-research/scans/idx.db"))
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("index")
    pi.add_argument("input")
    pi.add_argument("--limit", type=int, default=0)
    pi.add_argument("--timeout", type=int, default=45)
    pi.add_argument("--workers", type=int, default=4)
    pi.add_argument("--include-exclude", action="store_true")

    ps = sub.add_parser("search")
    ps.add_argument("query")
    ps.add_argument("--limit", type=int, default=20)

    pt = sub.add_parser("tag")
    pt.add_argument("tag", help="內建 tag: security / forum / leak / news / wiki / finance")
    pt.add_argument("--limit", type=int, default=300)
    pt.add_argument("--min-hits", type=int, default=1,
                    help="至少命中 N 個不同 keyword 才視為 hit (default 1; 用 2 收緊)")

    args = p.parse_args()
    if args.cmd == "index":
        cmd_index(args)
    elif args.cmd == "tag":
        cmd_tag(args)
    else:
        cmd_search(args)


if __name__ == "__main__":
    main()
