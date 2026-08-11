# Aliens Eye JSON Output — Schema Reference & Working Parser

Captured from a real 6-variant scan (2026-06-30, OSINT on a Taiwanese teacher's name) using `username-scanner` v2.1.0.

## Actual schema

`aliens_eye <username> --format json --output <dir>` produces:

```json
{
  "scan_summary": {
    "base_username": "<username>",
    "scan_level": "basic",
    "timestamp": "YYYYMMDD_HHMMSS",
    "total_variations": 1,
    "total_sites_scanned": 820,
    "total_found": 99,
    "total_high_confidence": 4,
    "best_variation": {...}
  },
  "variations": {
    "<username>": {
      "scan_info": {
        "username": "<username>",
        "sites_scanned": 820,
        "found": 99,
        "maybe": 146,
        "not_found": 150,
        "errors": 425,
        "high_confidence_matches": 4
      },
      "sites": {
        "<platform_name>": {
          "status": "Found" | "Maybe" | "Not Found",
          "code": 200,
          "url": "https://...",
          "final_url": "https://...",
          "response_time": 0.86,
          "confidence": 86,                // ⚠️ shape varies — sometimes int 0-100, sometimes missing
          "ai_analysis": {
            "method": "ml+heuristic",
            "score": 24.0,                 // raw heuristic score
            "probability": 0.86,           // ✅ USE THIS — always float 0-1
            "features": {                  // 25-dim feature vector
              "http_200": 1.0,
              "http_3xx": 0.0,
              "http_404": 0.0,
              "http_4xx": 0.0,
              "http_5xx": 0.0,
              "has_username_in_path": 1.0,
              "is_homepage": 0.0,
              "has_auth_pattern": 0.0,
              "error_keyword_count": 1.0,
              "positive_keyword_count": 2.0,
              "meta_error_keyword_count": 0.0,
              "meta_positive_keyword_count": 1.0,
              "profile_section_count": 2.0,
              "error_section_count": 0.0,
              "img_count": 0.0,
              "input_count": 0.0,
              "form_count": 0.0,
              "title_has_username": 1.0,
              "meta_has_username": 1.0,
              "response_time": 0.86,
              "content_length": 9673.0,
              "redirect_count": 0.0,
              "og_type_profile": 0.0,
              "has_json_ld_person": 0.0,
              "username_in_canonical": 0.0,
              "link_count": 4.0,
              "text_length": 1675.0,
              "fingerprint_match_found": 0.0,
              "fingerprint_match_not_found": 0.0,
              "heuristic_score": 24.0
            },
            "signals": {
              "site": "<platform>",
              "title": "Telegram: Contact @username",
              "meta_samples": [...],
              "url_analysis": {
                "domain": "t.me",
                "path": "/username",
                "has_username_in_path": true,
                "has_auth_pattern": false,
                "is_homepage": false
              },
              "dom": {...},
              "headers": {...}
            }
          }
        }
      }
    }
  }
}
```

## Field-discoverability pitfalls

| Field | Gotcha |
|:------|:-------|
| `info["confidence"]` | Sometimes int 0-100, sometimes missing. **Don't trust it.** |
| `info["ai_analysis"]["probability"]` | Always float 0-1. **Use this.** |
| `info["status"]` | "Found" / "Maybe" / "Not Found". **Threshold gate on probability, not status.** |
| `info["ai_analysis"]["signals"]["title"]` | Often generic ("GIFs - Find & Share on GIPHY") even when status is "Found". **Inspect to confirm.** |
| `info["url"]` vs `info["final_url"]` | `url` is the input URL. `final_url` is after redirects. **Use final_url for dedup.** |

## Working parser

Save as `scripts/parse_aliens_eye.py` and run after each scan:

```python
#!/usr/bin/env python3
"""Parse aliens_eye JSON output, filter false positives, rank real hits.

Usage:
    python3 parse_aliens_eye.py /path/to/results/*.json
    python3 parse_aliens_eye.py /path/to/results/*.json --threshold 0.75
"""
import json
import sys
import glob
from collections import defaultdict


def load(paths):
    """Load multiple aliens_eye JSON files into a single nested structure."""
    data = {}
    for f in sorted(glob.glob(paths) if '*' in paths else paths):
        try:
            with open(f) as fp:
                d = json.load(fp)
        except Exception as e:
            print(f"ERR {f}: {e}", file=sys.stderr)
            continue
        for uname, v in d.get("variations", {}).items():
            data.setdefault(uname, {})
            for site, info in v.get("sites", {}).items():
                data[uname][site] = info
    return data


def filter_found(data, threshold=0.75):
    """Yield (username, platform, info) for high-confidence Found hits."""
    for uname, sites in data.items():
        for site, info in sites.items():
            if info.get("status") != "Found":
                continue
            prob = info.get("ai_analysis", {}).get("probability", 0)
            if prob < threshold:
                continue
            yield uname, site, info


def cross_variant_dedup(hits):
    """Group hits by (platform, final_url). Sites hit by 2+ variants are real."""
    by_url = defaultdict(list)
    for uname, site, info in hits:
        url = info.get("final_url") or info.get("url")
        by_url[(site, url)].append((uname, info))
    multi = {k: v for k, v in by_url.items() if len(set(u for u, _ in v)) >= 2}
    return multi


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="Glob or file paths")
    ap.add_argument("--threshold", type=float, default=0.75)
    args = ap.parse_args()

    paths = " ".join(args.paths)
    data = load(paths)

    print(f"=== {len(data)} usernames scanned ===\n")
    for u, sites in data.items():
        n = sum(1 for s, i in sites.items() if i.get("status") == "Found")
        n_hc = sum(
            1 for s, i in sites.items()
            if i.get("status") == "Found"
            and i.get("ai_analysis", {}).get("probability", 0) >= args.threshold
        )
        print(f"  {u}: Found={n}  HighConf(>={args.threshold})={n_hc}  Total sites={len(sites)}")

    hits = list(filter_found(data, args.threshold))

    print(f"\n=== High-confidence Found (>= {args.threshold}) ===\n")
    seen = set()
    for uname, site, info in hits:
        url = info.get("url")
        if (site, url) in seen:
            continue
        seen.add((site, url))
        prob = info.get("ai_analysis", {}).get("probability", 0)
        title = (info.get("ai_analysis", {}).get("signals", {}).get("title") or "")[:60]
        print(f"  [{uname:>20s}] {site:25s} p={prob:.2f} code={info.get('code')} | {title}")
        print(f"      {url}")

    multi = cross_variant_dedup(hits)
    print(f"\n=== LIKELY REAL HITS (cross-variant evidence: 2+ variants) ===\n")
    print(f"  {len(multi)} platforms with cross-variant evidence\n")
    for (site, final_url), entries in sorted(multi.items(), key=lambda x: -len(x[1])):
        variants = sorted(set(u for u, _ in entries))
        probs = [info.get("ai_analysis", {}).get("probability", 0) for _, info in entries]
        title = (
            entries[0][1].get("ai_analysis", {}).get("signals", {}).get("title", "")[:60]
            if entries[0][1].get("ai_analysis", {}).get("signals")
            else ""
        )
        print(f"    {site} | variants={variants} | p_max={max(probs):.2f}")
        print(f"      title: '{title}'")
        print(f"      url:   {final_url}")


if __name__ == "__main__":
    main()
```

## Real output example

For 6-variant scan of variants `zhaohongzhong`, `zhao_hongzhong`, `hongzhong_zhao`, `hzzhao`, `zhzhong`, `hongzhong`:

```
=== 6 usernames scanned ===
  hongzhong: Found=295  HighConf(>=0.75)=74
  hongzhong_zhao: Found=102  HighConf(>=0.75)=12
  hzzhao: Found=267  HighConf(>=0.75)=47
  zhao_hongzhong: Found=94  HighConf(>=0.75)=9
  zhaohongzhong: Found=99  HighConf(>=0.75)=12
  zhzhong: Found=260  HighConf(>=0.75)=47

=== LIKELY REAL HITS (cross-variant evidence: 2+ variants) ===
  1 platforms with cross-variant evidence
    mewe | variants=['hongzhong', 'hzzhao'] | p_max=0.77
      title: 'mewe - The Next-Gen Social Network'
      url:   https://mewe.com/404
```

The single cross-variant hit was a 404 — i.e., **zero confirmed real accounts across 6 variants × 840 platforms**. The lesson: trust cross-variant dedup, not the headline `Found: 99` count.

## Why the high-confidence count is unreliable

Platforms that **always** return Found for any username string (path-prefix artifacts, not real profiles):

- `t.me/<username>` (Telegram — even non-existent handles return 200 with username in title)
- `snapchat.com/add/<username>` (resolves to placeholder "Stories, Spotlight & Lenses" page)
- `civitai.com/user/<username>` (AI art profile placeholder)
- `roblox.com/user.aspx?username=<username>` (404-page often scores high)
- `ourdjtalk.com/members?username=<username>` (member directory lists all)
- `habbo.com/home/<username>` (always 200)
- `profile.codersrank.io/user/<username>` (CodersRank auto-creates)
- `chatujme.cz/<username>` (Czech chat — but title says "neexistuje" → it's a 404!)

For these, the only signal of "real vs. placeholder" is whether the title contains the username *with profile content* (e.g., "Felix Zhao (@zhaohongzhong) | Snapchat Stories" indicates a real account, "GIFs - Find & Share on GIPHY" indicates a placeholder).

The parser above is a starting point — for production OSINT, always do a final manual review of the cross-variant list before reporting.