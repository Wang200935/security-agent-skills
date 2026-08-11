#!/usr/bin/env python3
"""Yahoo TW cold-name noise-trap detector.

When you query a cold/rare CJK name on tw.search.yahoo.com and the result
page claims 10,000+ hits but the visible content has zero real hits, this
script tells you whether Yahoo silently substituted the name (陷阱 1) or
dropped the OR operator and fell back to a single common character (陷阱 2).

Usage:
    python3 yahoo_cold_name_detector.py <raw_html_path> "<full 3-char name>"

Exit codes:
    0  → at least one result block (h3 title) contains the exact query name → REAL HIT
    1  → no result blocks contain the name → NOISE (auto-substituted or OR-stripped)
    2  → script error or invalid usage

Heuristics checked:
  - 搜尋結果包含: <other-name>     → 自動替換（陷阱 1）
  - 全部 h3 title 內無完整姓名      → 噪音
  - 可見文字內出現次數 = 1 (僅 search bar)  → 噪音
"""
import re
import sys
import html as h
from pathlib import Path


def detect(raw_html: str, target_name: str) -> dict:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", raw_html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    # Yahoo's auto-substitution hint
    hint = re.search(r"搜尋結果包含[：:]\s*([^<\"]+?)(?=[\"<])", raw_html)
    hint_text = h.unescape(hint.group(1).strip()) if hint else None

    # Reported hit count (if present)
    count = re.search(r"約\s*([\d,]+)\s*項", raw_html)
    count_text = count.group(1) if count else None

    # All h3.title links (Yahoo's natural-result block)
    titles = re.findall(
        r'<h3[^>]*class="[^"]*title[^"]*"[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        raw_html, flags=re.DOTALL | re.IGNORECASE,
    )
    title_texts = []
    for href, title in titles:
        t = re.sub(r"<[^>]+>", "", title)
        t = h.unescape(re.sub(r"\s+", " ", t)).strip()
        title_texts.append(t)

    # How many titles contain the exact target name
    title_hits = sum(1 for t in title_texts if target_name in t)

    # How many total occurrences in visible text
    text_count = text.count(target_name)

    # Noise verdict
    is_noise = False
    noise_reason = []
    if hint_text and hint_text != target_name:
        is_noise = True
        noise_reason.append(f"yahoo_did_you_mean={hint_text}")
    if titles and title_hits == 0:
        is_noise = True
        noise_reason.append(f"zero_title_hits (titles={len(title_texts)})")
    if text_count <= 1 and titles and title_hits == 0:
        noise_reason.append("text_count<=1 (only in search bar)")

    return {
        "target": target_name,
        "reported_count": count_text,
        "did_you_mean_hint": hint_text,
        "titles_found": len(title_texts),
        "title_hits": title_hits,
        "text_count": text_count,
        "is_noise": is_noise,
        "noise_reasons": noise_reason,
        "first_titles": title_texts[:5],
    }


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    raw = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    result = detect(raw, sys.argv[2])
    print(f"target              : {result['target']}")
    print(f"yahoo_reported_count: 約 {result['reported_count']} 項"
          if result['reported_count'] else "yahoo_reported_count: ?")
    print(f"did_you_mean        : {result['did_you_mean_hint'] or 'none'}")
    print(f"h3 titles found     : {result['titles_found']}")
    print(f"titles containing query: {result['title_hits']}")
    print(f"query in visible text: {result['text_count']}")
    print(f"VERDICT             : {'NOISE TRAP ⚠' if result['is_noise'] else 'REAL HIT ✓'}")
    if result['is_noise']:
        print(f"  reasons: {', '.join(result['noise_reasons'])}")
    print("first 5 titles:")
    for t in result['first_titles']:
        print(f"  · {t}")
    sys.exit(0 if result['title_hits'] > 0 else 1)


if __name__ == "__main__":
    main()