#!/usr/bin/env bash
# darkweb-weekly-reindex.sh — Hermes 2026-07-19
# Cron no_agent watchdog:**靜默**模式,只在「有新站時」吐 stdout 才通知,
# 空 stdout 不打擾。
# 邏輯:
#   1. 拉取 Ahmia clearnet /onions 全清單 (透過 Tor)
#   2. 與 scans/idx.db 已 indexed URL 比較, 抽出新站 (跳過 drug/dark/cann 等 BAD prefix)
#   3. 用 darksearch.py onion_probe 探測這些新站 (上限 50 個/週, 避免刷用戶)
#   4. 若有新站 → echo title + url 列表 (cron 會發通知); 都死了就靜默

set -euo pipefail
SHARED=/Users/wang/Documents/darkweb-research
TOOLS=$SHARED/tools
TOR_SOCKS=127.0.0.1:9050
UA="Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
BAD='^https?://(drug|dark|deep|cann|card|hack|black|wolf|silver|2222|buy|clone|fullz|guns|pills|hitman|pistol|weed|cocaine|heroin|fentanyl|xanax|lsd|mdma|meth)'

cd $TOOLS

# 確定 Tor 在跑
if ! curl -s --max-time 10 --socks5-hostname $TOR_SOCKS \
        https://check.torproject.org/api/ip 2>/dev/null | grep -q '"IsTor":true'; then
    brew services start tor >/dev/null 2>&1
    sleep 30
fi

# 拉新清單
curl -sL --max-time 60 --socks5-hostname $TOR_SOCKS -A "$UA" \
    "https://ahmia.fi/onions" -o /tmp/ahmia-weekly.html 2>/dev/null || exit 0
grep -oE "https?://[a-z0-9]{16,56}\.onion" /tmp/ahmia-weekly.html | sort -u | \
    grep -vE "$BAD" > /tmp/ahmia-weekly.txt

[[ -s /tmp/ahmia-weekly.txt ]] || exit 0

# 與 idx.db 比對 找新站
python3 << 'PYEOF' > /tmp/new-urls.txt 2>/dev/null
import sqlite3
db = sqlite3.connect('/Users/wang/Documents/darkweb-research/scans/idx.db')
try:
    indexed = set(r[0] for r in db.execute('SELECT url FROM urls').fetchall())
except sqlite3.OperationalError:
    indexed = set()
with open('/tmp/ahmia-weekly.txt') as f:
    new = [ln.strip() for ln in f if ln.strip() and ln.strip() not in indexed]
print('\n'.join(new[:50]))
PYEOF

NEW_COUNT=$(grep -c . /tmp/new-urls.txt 2>/dev/null || echo 0)
NEW_COUNT=${NEW_COUNT:-0}

if [[ "$NEW_COUNT" -lt 1 ]]; then
    exit 0                      # 無新站, 靜默
fi

# 探測新站
python3 onion_probe.py /tmp/new-urls.txt -o /tmp/new-probed.json \
    --workers 4 --timeout 45 >/dev/null 2>&1

# 把活的塞進 idx.db
python3 << 'PYEOF'
import json, sqlite3, datetime, re
results = json.load(open('/tmp/new-probed.json'))
db = sqlite3.connect('/Users/wang/Documents/darkweb-research/scans/idx.db')
db.execute("""CREATE TABLE IF NOT EXISTS urls(
    url TEXT PRIMARY KEY, title TEXT, http_code INT, size INT, elapsed REAL,
    probed_at TEXT, category TEXT, error TEXT)""")
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
ok = []
for r in results:
    if r.get('http_code') and 200 <= r['http_code'] < 400 and r.get('title'):
        cat = 'other'                       # cron 不分類, 都 other
        db.execute("INSERT OR REPLACE INTO urls VALUES (?,?,?,?,?,?,?,?)",
                   (r['url'], r['title'], r['http_code'], r['size'],
                    r['elapsed'], now, cat, r.get('error','')))
        ok.append((r['url'], r['title'], r['http_code']))
db.commit()
if ok:
    print(f"[*] 新站索引: {len(ok)} 個")
    for url, title, code in ok[:20]:
        print(f"  [{code}] {title[:60]}")
        print(f"       {url}")
PYEOF
