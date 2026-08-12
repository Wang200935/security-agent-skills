# 2025-2026 OSINT Updates

### New Tools & Platforms (2025-2026)

```python
OSINT_TOOLS_2025_2026 = {
    'deepfake_detection': {
        'tools': ['Deepfake Analyzer (Sensity)', 'FaceForensics++', 'Deepware Scanner'],
        'note': 'AI-generated content proliferation requires OSINT practitioners to verify media authenticity.',
    },
    'satellite_imagery': {
        'tools': ['Planet Labs (commercial)', 'Sentinel Hub', 'Google Earth Engine', 'SkyFi', 'BlackSky'],
        'note': 'Near-real-time satellite imagery now available for OSINT.',
    },
    'social_media_2025': {
        'tools': ['Maltego CE', 'Spiderfoot', 'Social Mapper', 'Instaloader'],
        'note': 'Platforms increasingly restrict API access. Use browser automation (Playwright) for JS-rendered pages.',
    },
    'darkweb_monitoring': {
        'tools': ['Ahmia (Tor search)', 'DarkOwl', 'IntelX', 'DeHashed'],
        'note': 'Breach data appears on dark web within hours of incident.',
    },
    'blockchain_osint': {
        'tools': ['Chainalysis', 'Elliptic', 'BitQuery', 'Etherscan', 'Crystal'],
        'note': 'Trace cryptocurrency transactions for fraud investigation.',
    },
    'username_scanning': {
        'tools': ['username_scanner (840+ platforms, ML detection)', 'Sherlock (300+)', 'Maigret (2500+)', 'WhatsMyName (500+)'],
        'note': 'username_scanner supports Tor, Playwright fallback, ML-blended detection. Cross-variant username scanning is strongest signal.',
    },
    'ai_osint': {
        'tools': ['GeoSpy AI (Geolocation from photos)', 'OSINT-GPT (experimental)'],
        'note': 'AI-assisted OSINT: LLMs can summarize large document corpora, identify entities, and cross-reference findings.',
    },
}
```

### OPSEC Best Practices (2025-2026)

```
1. ALWAYS use Tor/VPN for sensitive OSINT — your IP is logged by every platform queried
2. Use separate browser profiles for different investigation targets
3. Metadata in screenshots can leak your identity — strip EXIF before sharing
4. Use Playwright with stealth mode for JS-heavy sites (anti-bot detection is increasing)
5. Set up burner accounts for social media investigation (never use personal accounts)
6. DNS leaks can expose your real location even through VPN — use DNS over HTTPS
7. Timezone and language settings in browser fingerprint can identify your real location
8. Clear cookies and local storage between sessions
9. Use Yahoo TW for Chinese-language searches (Google/Bing/DDG block Tor and bot UA)
10. Cross-reference findings across multiple sources for verification
```

### Pitfalls

- **SpiderFoot v4 + macOS fd limit**: SpiderFoot 4.x runs ~200 modules in concurrent subprocesses and needs ~10K file descriptors. The macOS default `ulimit -n` is 256 — silently kills most modules with "Too many open files" errors. Always raise: `ulimit -n 10240` before launching, or use `sfo.py wrapper` which does it automatically.
- **SpiderFoot v4 CLI stdout is NOT the authoritative event source**: v4 CLI runs the scan in a subprocess; events go to `~/.spiderfoot/spiderfoot.db` SQLite. stdout is a JSON-array stream that can be cut short by pipe deadlock or closed before flush. Always read events from SQLite post-scan. The `sfo.py` wrapper does this automatically.
- **SpiderFoot "231 modules" is misleading**: Without API keys, ~50% of valuable modules (HIBP/Shodan/VT/DeHashed) silently skip. The `sfp_citadel` (Leak-Lookup) module works without key (free) and returns hundreds of breach hits for any well-known email — this is the highest-value no-key module. See `spiderfoot-osint/references/api-keys-full.md` for key registration guide.
- **CJK real-person names**: Username scanners (username_scanner, sherlock, maigret) cannot solve "find 中文姓名" — they are ASCII-only and Chinese users rarely have ASCII handles. Use the **CJK Real-Person Playbook** instead: `references/cjk-real-person-osint-playbook.md`. Key insight: Yahoo TW (`tw.search.yahoo.com`) is the single most reliable source — Google/Bing/DDG all captcha-block bot UA, but Yahoo TW doesn't, and it indexes Taiwanese school sites, BBS, news exactly where Chinese names appear.
