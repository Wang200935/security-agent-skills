# 5. Social Media Intelligence (SOCMINT)

### Cross-Platform Username Search

```python
# Platform checkers
USERNAME_TOOLS = [
    'username_scanner',       # 840+ platforms — ML+heuristic detection (BEST quality) — pip install username-scanner
    'sherlock',         # 300+ platforms — pip install sherlock-project
    'maigret',          # 2500+ sites — especially good for non-English
    'whatsmyname',      # 500+ platforms — web-based
    'socialscan',       # Fast async checker (Python)
    'blackbird',        # 600+ platforms (Go-based, very fast)
    'nexfil',           # Username profiling (Python)
]

# ── Username Scanner (preferred for quality) ──
# Full scan with ML detection + all export formats:
#   username_scanner username --profile full --format all --output results/
# Advanced level checks prefix/suffix variations:
#   username_scanner username -l advanced --format json
# Through Tor for OPSEC:
#   username_scanner username --tor --profile full
# Target specific platforms:
#   username_scanner username --site github,reddit,gitlab
# Run alongside others for maximum coverage:
#   username_scanner username --profile full & sherlock username & maigret username --all-sites

# Sherlock usage
# sherlock username1 username2 --output results/

# Maigret (more comprehensive, Russian platforms)
# maigret username --all-sites --html
```

### Platform-Specific Tools

```python
# X (Twitter) OSINT
TWITTER_OSINT = {
    'advanced_search': 'https://twitter.com/search-advanced',
    'nitter': 'https://nitter.net/ — anonymous browsing',
    'twint_replacement': 'snscrape — safer and maintained',
    'birdwatch': 'Community notes analysis',
}

# snscrape Twitter
"""
snscrape twitter-user username
snscrape twitter-search 'from:user since:2024-01-01'
snscrape --jsonl twitter-search 'keyword' > tweets.json
"""

# Instagram OSINT
INSTAGRAM_OSINT = {
    'imginn':       'Anonymous Instagram viewer',
    'instaloader':  'pip install instaloader — download profiles',
    'dumpchat':     'Instagram chat downloader',
    'pimeyes':      'Facial recognition search (paid)',
    'searchmy.bio': 'Instagram bio search engine',
}

# Instagram profile download
# instaloader profile username

# TikTok OSINT
TIKTOK_OSINT = {
    'snscrape': 'snscrape tiktok-user username',
    'tiktok-scraper': 'npm-based scraper',
    'tikrank': 'Influence metrics',
}

# LinkedIn OSINT
LINKEDIN_OSINT = {
    'recruitment_geek': 'X-Ray search via Google',
    'linkedin_dork': 'site:linkedin.com/in/ "Target Corp" "software engineer"',
    'rocketreach': 'Email lookup (paid)',
    'contactout': 'Email/phone lookup (paid)',
}

# Reddit OSINT
REDDIT_OSINT = {
    'redditsearch.io': 'Full text search across Reddit',
    'reveddit': 'View deleted/removed comments',
    'camas': 'Reddit post/comment history search',
    'pushshift': 'Historical Reddit data API (archive)',
}

# Telegram OSINT
TELEGRAM_OSINT = {
    'telegramdb': 'Telegram group/channel search',
    'telemetr': 'Telegram analytics',
    'tgstat': 'Channel statistics and search',
    'lyzem': 'Telegram search engine',
}
```

### Relationship Mapping (Maltego)

```python
MALTEGO_TRANSFORMS = """
Maltego graph-based investigation:
1. Start with seed entity (email, domain, name, phone)
2. Run transforms to discover connected entities
3. Visualize relationship graph
4. Identify key nodes and attack paths

Common transforms:
- Domain → DNS → Subdomains → IPs → Netblocks
- Email → Social profiles → Usernames → More accounts
- Phone → Carrier lookup → Possible owner
- IP → Geolocation → Nearby infrastructure
- Person → Social media → Associates → Organization
"""
```

---
