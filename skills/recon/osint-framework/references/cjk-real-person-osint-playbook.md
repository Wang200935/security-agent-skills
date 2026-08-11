# CJK Real-Person OSINT Playbook (Taiwan / China / HK Names)

> **Use case**: User asks "find <中文姓名>" with or without a profession hint
> (老師 / 教授 / 醫師 / 工程師 / 律師 etc.). Username scanners **cannot solve
> this** — CJK users rarely have ASCII usernames. You need a fundamentally
> different playbook.

> **Verified**: 2026-06-30 across two back-to-back sessions (趙鴻中 + 王池川).

## ⚠ READ THIS BEFORE COUNTING HITS

Yahoo TW has two **noise-trap behaviors** that produce huge fake hit counts
on cold CJK names — see `references/cjk-yahoo-tw-noise-trap.md` for the full
diagnostic recipe and `scripts/yahoo_cold_name_detector.py` for an automated
checker. **Never trust Yahoo TW's hit count alone** — always grep the actual
visible text for the exact 3-character name. If you see "約 10,000 項" but
zero `h3.title` blocks contain the full name, the count is noise.

The two noise traps:
1. **Phonetic / semantic auto-substitution** — Yahoo rewrites your cold name
   to a famous name and shows the famous name's results (e.g. 王池川 → 王義川).
2. **`OR` operator silently dropped** — `"王池川" 老師 OR 教授` degenerates
   to single-character `王`, returning 233,000 "王" dictionary entries.

## Why username scanners fail on Chinese names

| What you might try | Why it fails |
|:---|:---|
| `aliens_eye 張三` | Tool is ASCII-only, rejects non-ASCII positional args |
| URL-encoded: `aliens_eye %E5%BC%B5%E4%B8%89` | Still rejected; tool expects ASCII chars |
| Pinyin variants: `aliens_eye zhangsan` | Some Chinese netizens have ASCII usernames, but **most don't** — and you don't know which pinyin romanization they used |
| Sherlock / Maigret same problem | Same ASCII-only limitation |

**Exception**: If you ALREADY know their English handle (e.g. user said
"他的 GitHub 是 abc123"), use the username scanner directly. This playbook is
for "I have nothing but a Chinese name + maybe a profession/region."

## The 5-Leg Parallel Playbook

Run ALL five in parallel. Most yield nothing; the one that yields becomes your
ground truth. Don't sequentially try each — fire all at once and aggregate.

### Leg 1 — Yahoo TW (`tw.search.yahoo.com`)  ⭐ THE KILLER

For Taiwan/Chinese names, **Yahoo TW is the single most reliable source**.
Why it beats Google:
- Yahoo TW does **not** return captcha to bot UA (Google/Bing/DDG all do)
- Yahoo TW indexes Taiwanese school websites, BBS posts, forum profiles, news — exactly where a Taiwanese person's name will appear
- Yahoo TW results are richer than Google Scholar for Chinese academic names

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
curl -sL --max-time 20 -A "$UA" \
  "https://tw.search.yahoo.com/search?p=%22<URLENCODED_NAME>%22" \
  | python3 -c "
import sys, re, html
data = sys.stdin.read()
# Strip tags, keep text
text = re.sub(r'<[^>]+>', ' ', data)
text = html.unescape(text)
text = re.sub(r'\s+', ' ', text)
# Extract URLs
urls = re.findall(r'href=\"(https?://[^\"]+)', data)
# Filter: prefer .edu.tw, .gov.tw, news, school domains
for u in urls:
    if any(k in u for k in ['edu.tw', 'gov.tw', 'tc.', 'tn.', 'kh.', 'cps.', 'ntu', 'nthu', 'ncku', 'yahoo', 'youtube', 'pixnet']):
        print('URL:', u)
"
```

**Hit query variations** in parallel:
- `"<name>"` (plain)
- `"<name>" 老師` (if profession hint given)
- `"<name>" 教授` (university)
- `"<name>" 校長` / `主任` / `醫師` / `工程師`
- `"<name>" site:tcjh.tn.edu.tw` (or specific school if known)

### Leg 2 — Google Scholar (`scholar.google.com`)

```bash
curl -sL --max-time 30 -A "$UA" \
  "https://scholar.google.com/scholar?q=author%3A%22<URLENCODED_NAME>%22" \
  | python3 -c "
import sys, re, html
data = sys.stdin.read()
text = re.sub(r'<[^>]+>', ' ', data)
text = html.unescape(text)
text = re.sub(r'\s+', ' ', text)
# Find 'About X results' or '項結果'
m = re.search(r'(?:About|約有)\s*([\d,]+)\s*(?:results|項結果)', text)
if m:
    print(f'Scholar hit count: {m.group(1)}')
# Print first 1500 chars of text
print(text[:1500])
"
```

For Taiwan academics: try `作者:"<name>"` (Chinese operator).

### Leg 3 — Airiti Library (`airitilibrary.com`)

Taiwan's main thesis/journal aggregator. Has its own search UI but is mostly
JS-rendered → **must use Playwright** (curl will return shell only).

```python
# In a Playwright subagent
page.goto(f"https://www.airitilibrary.com/Search/alinksuggest?QueryText={name}")
# Or directly: https://www.airitilibrary.com/Search/alinksuggest?QueryText=...
```

### Leg 4 — 台灣博碩士論文知識加值系統 (`tdr.lib.ntu.edu.tw`)

Best for finding the **thesis advisor + student relationship**, which is
how you verify a "老師" hypothesis (e.g., if 趙鴻中 advised thesis X, he must
be faculty somewhere).

```bash
curl -sL --max-time 30 -A "$UA" \
  "https://tdr.lib.ntu.edu.tw/simple-search?query=<URLENCODED_NAME>"
```

### Leg 5 — Direct school website hit (if region known)

If user gives region/school hint, skip Yahoo TW and hit the school website
directly. Most .edu.tw sites have a faculty directory with name + subject +
ext + email.

```bash
# Example pattern for Taiwan high schools
curl -sL "https://<school>.tn.edu.tw/" -A "$UA" | grep -o "<name>[^<]*"
```

### Optional Leg 6 — Brave Search (English fallback)

For CJK names, Brave sometimes surfaces cross-references from English-language
Taiwan media (e.g. Taiwan News, Taipei Times).

```bash
curl -sL --max-time 20 -A "$UA" --socks5-hostname 127.0.0.1:9050 \
  "https://search.brave.com/search?q=%22<URLENCODED_NAME>%22" \
  | python3 -c "...URL extraction..."
```

## Hard-Earned Lessons (cost real session time)

### L1. Google / Bing / DuckDuckGo WILL captcha-block you

| Engine | Behavior under bot UA |
|:---|:---|
| Google.com | Captcha page after 1 query |
| Scholar (Google) | **Often passes** (separate bot policy) |
| Bing | Captcha immediately |
| DuckDuckGo HTML (`html.duckduckgo.com/html/`) | Returns "If this persists, please email us" — useless |
| Yahoo TW | **No captcha**, full results |
| Brave Search | Mostly passes, fewer results than Yahoo |
| SearX instances | Mixed; some rate-limit hard |

**Implication**: Don't even try Google / Bing / DDG with curl. Either use
Playwright (gets through sometimes) or skip them entirely and rely on Yahoo
TW + Scholar + Airiti.

### L2. Tavily API (= built-in `web_search` / `web_extract`) is unreliable

`Tavily search failed: Client error '432 '` is a **persistent** outage, not
a transient one. When you see this, immediately switch to:
- Yahoo TW via curl
- Playwright subagent for JS-rendered pages
- Direct school/government website fetches

Do NOT keep retrying Tavily — it wastes 5-10 min before giving up.

### L3. School websites often use JS rendering for content

Many .edu.tw sites render faculty lists via JS. `curl` returns the page
shell but not the names. Use Playwright for these.

### L4. Ministry of Education 不適任 teacher DB is unreliable

`https://www.eye.gov.tw/` (the historical URL for 不適任教育人員資料庫) returns
**DNS_PROBE_FINISHED_NXDOMAIN** as of 2026-06-30 — the URL is dead. The
official entry point is now under `https://www.edu.tw/` site search.

### L5. Don't trust "X is a teacher" — always verify

A user saying "他是老師" doesn't tell you:
- 中學 vs 大學 vs 補習班
- 學科（國文 / 數學 / 自然 / 社會 / 英語...）
- 縣市
- 在職 vs 退休

Always cast a wide net first. If you find he/she is a 高中教師 at 台南土城
高中, **verify 2026 現職** by phone — public records lag by 2-4 years.

## Output template

After running the playbook, produce:

```markdown
# 「<name>」OSINT 結果報告

## 重點結論
| 項目 | 內容 | 信心 |
|:---|:---|:---:|
| 現任單位 | <學校/公司> | 高/中/低 |
| 職務 | <職稱> | 高/中/低 |
| 學歷 | <最高學歷 + 學校 + 年度> | 高/中/低 |
| 著作 / 公開活動 | <論文 / 課程 / 報導> | 高/中/低 |
| 聯絡 | <電話 / email / 地址> | 高/中/低 |

## 來源 → 實際抓到內容
### 1) Yahoo TW
URL: ...
回傳：...

### 2) Google Scholar
...

## 失敗 / 需人工覆核
- 教育不適任 DB: eye.gov.tw 已死，需手動查 edu.tw
- 2026 現職: 公開紀錄停在 2024，建議打電話

## 副帶效益
- 跑了 Aliens Eye 5 變體 × 820 平台 = 4100 請求
- 真實命中：<列出>
- 假陽性過濾：<說明>
```

## Cross-reference with Aliens Eye

The username scanner should be run **in parallel** but as a **secondary
track**, not the primary:

```bash
# Generate pinyin variants for Chinese name
python3 -c "
name = '王池川'  # input
import re
# Quick pinyin is hard without a library; assume user gives romanization
# OR generate plausible patterns:
variants = [
  'wangchichuan', 'wang_chichuan', 'chichuan_wang', 'chichuanwang',
  'chichuan_w', 'chichuan_wang',
  # Add full-surname-last, given-only, etc.
]
for v in variants:
    print(v)
" | while read v; do
  ~/.hermes/hermes-agent/venv/bin/aliens_eye "$v" --no-nsfw --profile quick \
    --output /tmp/cjk_osint-framework/aliens_eye/ --format json
done
```

**Realistic expectation**: For CJK names, ~5% chance the user has an ASCII
account with **any** pinyin spelling. Check the result anyway because
TradingView, Spotify, Civitai sometimes have real matches (see 王池川 2026-06-30:
TradingView `wangchichuan` was a real 2023 account).

## Reference: Tor OPSEC

For sensitive targets (celebrities, public figures, estranged family, etc.),
run all Leg 1-6 through Tor:

```bash
brew services start tor  # one-time
curl --socks5-hostname 127.0.0.1:9050 -A "$UA" \
  "https://tw.search.yahoo.com/..."
```

**Caveat**: Tor doesn't bypass Google/Bing captcha — they detect Tor exits.
For those, use a residential proxy or skip them.

## Cheat sheet: When user says "找 XXX"

| User says | First ask | Then run |
|:---|:---|:---|
| "找 張三" | "他是什麼職業？大概哪個縣市？" | Yahoo TW + Scholar + Aliens Eye |
| "張三 是老師" | "中學還是大學？大概在哪？" | Yahoo TW + Scholar + direct school site |
| "張三 的 email" | **Push back**: "email 通常不公開，請說明用途" | School website + Hunter.io (if domain known) |
| "張三 住哪" | **Refuse**: 隱私疑慮 | — |
| "張三 不適任查詢" | Note: eye.gov.tw 已死 | Manual edu.tw 站內搜 |

## Files produced for a successful run

- `/tmp/<name>_results/<name>_zh_result.md` — final writeup
- `/tmp/<name>_results/raw_findings.jsonl` — per-source raw
- `/tmp/<name>_results/summary.json` — JSON summary
- `/tmp/<name>_results/snaps/` — Playwright screenshots
- `/tmp/<name>_results/<variant>_basic_*.json` — Aliens Eye raw output