#!/usr/bin/env python3
"""Parse aliens_eye JSON output, filter false positives, rank real hits.

Usage:
    python3 parse_aliens_eye.py /path/to/results/*.json
    python3 parse_aliens_eye.py /path/to/results/*.json --threshold 0.75 --json
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
    ap = argparse.ArgumentParser(description="Parse aliens_eye JSON, filter false positives.")
    ap.add_argument("paths", nargs="+", help="Glob or file paths")
    ap.add_argument("--threshold", type=float, default=0.75,
                    help="Minimum ai_analysis.probability for Found hits (default 0.75)")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human report")
    args = ap.parse_args()

    paths = " ".join(args.paths)
    data = load(paths)

    hits = list(filter_found(data, args.threshold))

    if args.json:
        seen = set()
        out_hits = []
        for uname, site, info in hits:
            url = info.get("url")
            if (site, url) in seen:
                continue
            seen.add((site, url))
            out_hits.append({
                "username": uname,
                "site": site,
                "probability": info.get("ai_analysis", {}).get("probability", 0),
                "code": info.get("code"),
                "url": url,
                "final_url": info.get("final_url"),
                "title": (info.get("ai_analysis", {}).get("signals", {}).get("title") or ""),
            })
        multi = cross_variant_dedup(hits)
        real = []
        for (site, final_url), entries in multi.items():
            real.append({
                "site": site,
                "variants": sorted(set(u for u, _ in entries)),
                "url": final_url,
                "title": (
                    entries[0][1].get("ai_analysis", {}).get("signals", {}).get("title", "")
                    if entries[0][1].get("ai_analysis", {}).get("signals")
                    else ""
                ),
            })
        print(json.dumps({"hits": out_hits, "real_accounts": real}, ensure_ascii=False, indent=2))
        return

    print(f"=== {len(data)} usernames scanned ===\n")
    for u, sites in data.items():
        n = sum(1 for s, i in sites.items() if i.get("status") == "Found")
        n_hc = sum(
            1 for s, i in sites.items()
            if i.get("status") == "Found"
            and i.get("ai_analysis", {}).get("probability", 0) >= args.threshold
        )
        print(f"  {u}: Found={n}  HighConf(>={args.threshold})={n_hc}  Total sites={len(sites)}")

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