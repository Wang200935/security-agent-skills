#!/usr/bin/env python3
"""
暗網探測器 — Hermes 2026-07-19
走 Tor SOCKS5 (127.0.0.1:9050),對一批 .onion 探活,
抓 title, 紀錄 response time, 存到 JSON。

用法:
  python3 onion_probe.py input.txt -o out.json --limit 30 --timeout 60

input.txt 一行一個 URL (含 .onion)。
"""

import argparse
import concurrent.futures as cf
import json
import os
import re
import socket
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import socks  # pip install PySocks  -- 但我們用 stdlib 不用 PySocks
import urllib.request

# ---- Monkey-patch socket 用 Tor SOCKS5 ----
import socks as _socks  # pip install PySocks

PROXY = ("127.0.0.1", 9050)

def _make_tor_socket(*args, **kwargs):
    s = _socks.socksocket()
    s.set_proxy(_socks.SOCKS5, PROXY[0], PROXY[1])
    # 連 target 用原參數
    if args:
        s.connect(args[0] if isinstance(args[0], tuple) else (args[0], 80))
    return s

# 把 socket.create_connection 換成走 Tor
_orig_create_connection = socket.create_connection
_orig_socket = socket.socket

def tor_create_connection(addr, *args, **kwargs):
    s = _socks.socksocket()
    s.set_proxy(_socks.SOCKS5, PROXY[0], PROXY[1])
    s.settimeout(kwargs.get("timeout", 60))
    s.connect(addr)
    return s

socket.create_connection = tor_create_connection

# ---- HTTP fetch via Tor ----
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

def probe(url, timeout=60):
    t0 = time.time()
    result = {
        "url": url,
        "ts": datetime.now(timezone.utc).isoformat(),
        "http_code": None,
        "title": "",
        "size": 0,
        "elapsed": 0,
        "error": "",
        "final_url": url,
    }
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": UA, "Accept": "text/html,*/*"},
        )
        # urllib 經 socket (已被 monkey-patch) 不支援 .onion socks5h 解析?
        # URL 是 .onion host, DNS 走 Tor 才對。我們用 socks5h 讓 Tor 解析 onion.
        # urllib.create_connection 收到的 host 是 .onion 字符串,
        # PySocks 在 SOCKS5 模式會問 Tor 做 remote resolve, 不是本地,
        # 所以 onion DNS 也由 Tor 完成。OK。
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(200_000)
            result["http_code"] = resp.status
            result["size"] = len(body)
            result["final_url"] = resp.geturl()
            # title
            m = re.search(rb"<title[^>]*>(.*?)</title>",
                           body, re.I | re.S)
            if m:
                try:
                    result["title"] = m.group(1).decode(
                        "utf-8", "replace").strip()[:200]
                except Exception:
                    result["title"] = repr(m.group(1)[:200])
    except urllib.error.HTTPError as e:
        result["http_code"] = e.code
        result["error"] = f"HTTPError {e.code}"
    except urllib.error.URLError as e:
        result["error"] = str(e.reason)[:200]
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"[:200]
    result["elapsed"] = round(time.time() - t0, 2)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="file with one URL per line, or '-' for stdin")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--limit", type=int, default=0, help="max URLs to probe (0=all)")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--workers", type=int, default=5,
                   help="concurrent; 保守值勿太高,避免 Tor overload")
    p.add_argument("--filter-prefix", default=None,
                   help="只保留 URL 開頭符合此 prefix 的站")
    args = p.parse_args()

    if args.input == "-":
        urls = [ln.strip() for ln in sys.stdin if ln.strip()]
    else:
        urls = [ln.strip() for ln in Path(args.input).read_text().splitlines()
                if ln.strip() and not ln.startswith("#")]
    # 去重
    seen = set()
    filtered = []
    for u in urls:
        if u in seen:
            continue
        if args.filter_prefix and not u.startswith(args.filter_prefix):
            continue
        seen.add(u)
        filtered.append(u)
    if args.limit:
        filtered = filtered[: args.limit]
    print(f"[*] {len(filtered)} URLs queued, {args.workers} workers", file=sys.stderr)

    results = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(probe, u, args.timeout): u for u in filtered}
        done_count = 0
        for f in cf.as_completed(futs):
            r = f.result()
            results.append(r)
            done_count += 1
            ok = "OK" if r["http_code"] and 200 <= r["http_code"] < 400 else "FAIL"
            print(f"[{done_count}/{len(filtered)}] {ok} "
                  f"HTTP {r['http_code']} {r['elapsed']:.1f}s {r['url'][:60]} | "
                  f"{r['title'][:50] if r['title'] else r['error'][:50]}",
                  file=sys.stderr)

    # 排序:活著的 + title
    results.sort(key=lambda x: (
        0 if x["http_code"] and 200 <= x["http_code"] < 400 else 1,
        -x["size"],
    ))
    Path(args.out).write_text(json.dumps(results, indent=2, ensure_ascii=False))
    ok = sum(1 for r in results if r["http_code"] and
             200 <= r["http_code"] < 400)
    print(f"[*] done: {ok}/{len(results)} OK -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
