---
name: osint-framework
description: "Complete OSINT (Open Source Intelligence) framework — SOCMINT, DNS/domain recon, email/phone intelligence, geolocation, image analysis, technical recon, financial/crypto OSINT, dark web, government records, and automated toolchains."
version: 1.0.0
category: red-teaming
tags: [OSINT, intelligence, reconnaissance, SOCMINT, geolocation, dorking, Shodan, darkweb, crypto, blockchain]
related_skills:
  - parallel-intel
  - web-app-pentest
  - ctf-playbook
  - cybersecurity
  - username-scanner
  - spiderfoot-osint
---

# OSINT — Complete Open Source Intelligence

## OSINT Methodology

```
1. PLANNING        → 2. COLLECTION     → 3. PROCESSING    → 4. ANALYSIS      → 5. REPORTING
   - Define target     - Run all tools     - Deduplicate       - Link entities    - Visualize
   - Set scope         - Parallel exec     - Correlate         - Identify patterns - Timeline
   - Legal check       - Multi-engine      - Enrich data       - Score confidence  - Deliver
```

### Golden Rule: Always Run in Parallel

Every OSINT operation MUST use ALL available sources simultaneously:
- Search engines (Google Dorking + Bing + Yandex + DuckDuckGo)
- Technical scanners (Shodan + Censys + FOFA + ZoomEye)
- DNS tools (crt.sh + SecurityTrails + Amass)
- Social media (X/Twitter + Instagram + LinkedIn + TikTok + Reddit)
- Image tools (Google Images + TinEye + Yandex Images)
- Code repos (GitHub + GitLab + Bitbucket)
- Archive (Wayback Machine + Archive.today)

---

## 1. Google Dorking — Complete Operator Reference

### Core Operators

```python
GOOGLE_DORKS = {
    'site:':        'Limit to domain: site:example.com',
    '-site:':       'Exclude domain: -site:evil.com',
    'intitle:':     'Word in page title: intitle:"admin panel"',
    'allintitle:':  'All words in page title: allintitle:login password',
    'inurl:':       'Word in URL: inurl:admin',
    'allinurl:':    'All words in URL: allinurl:login admin',
    'intext:':      'Word in page body: intext:password',
    'allintext:':   'All words in body: allintext:username password',
    'filetype:':    'Specific file type: filetype:pdf OR filetype:xlsx',
    'ext:':         'Alias for filetype:',
    'cache:':       'Google cached version: cache:example.com',
    'related:':     'Similar sites: related:example.com',
    'link:':        'Pages linking to URL (deprecated, limited)',
    'define:':      'Dictionary definition',
    'AROUND(X)':    'Proximity search: "john" AROUND(3) "doe"',
    '"exact phrase"': 'Exact match',
    'OR / |':       'Logical OR: admin OR administrator',
    '*':            'Wildcard: "john * doe"',
    '..':           'Range: 2020..2025',
    'before:':      'Before date: before:2024',
    'after:':       'After date: after:2023',
    'source:':      'News source: source:reuters',
    'loc:':         'Location: loc:"San Francisco"',
    'map:':         'Map search results',
}
```

### Offensive Dork Library

```python
# Exposed sensitive files
EXPOSED_DORKS = {
    'env_files':        'intitle:"index of" ".env"',
    'config_files':     'intitle:"index of" "config.php" OR "wp-config.php" OR "config.yml"',
    'backup_files':     'intitle:"index of" "backup" OR "dump" OR ".sql" OR ".bak" OR ".tar.gz"',
    'ssh_keys':         'intitle:"index of" "id_rsa" OR "id_dsa" OR "*.pem"',
    'log_files':        'intitle:"index of" "access.log" OR "error.log" OR "debug.log"',
    'database_files':   'intitle:"index of" "*.mdb" OR "*.sqlite" OR "*.db"',
    'password_files':   'intitle:"index of" "password" OR "credentials" OR "secret"',
    'docker_files':     'intitle:"index of" "Dockerfile" OR "docker-compose.yml"',
    'git_repos':        'intitle:"index of" ".git"',
    'aws_credentials':  'intitle:"index of" "credentials" "aws"',
}

# Camera & IoT
IOT_DORKS = {
    'webcams':          'intitle:"webcamXP" OR intitle:"Live View / - AXIS"',
    'routers':          'intitle:"Login" "NETGEAR" OR "TP-Link" OR "D-Link"',
    'printers':         'intitle:"HP LaserJet" OR "Phaser" OR "Xerox"',
    'nas':              'intitle:"Synology" OR "QNAP" OR "FreeNAS"',
    'ipmi':             'intitle:"IPMI" OR "iDRAC" OR "iLO"',
}

# Login panels
LOGIN_DORKS = {
    'admin_panels':     'intitle:"admin" inurl:/admin OR inurl:/administrator',
    'phpmyadmin':       'intitle:phpMyAdmin "Welcome to phpMyAdmin"',
    'wordpress':        'inurl:wp-admin OR inurl:wp-login',
    'joomla':           'inurl:administrator "Joomla"',
    'jenkins':          'intitle:"Dashboard [Jenkins]"',
    'grafana':          'intitle:"Grafana" "Welcome to Grafana"',
    'kibana':           'intitle:"Kibana"',
    'tomcat':           'intitle:"Apache Tomcat"',
    'cpanel':           'intitle:"cPanel" "Login"',
    'webmin':           'intitle:"Webmin" "Login"',
}

# Data leaks
LEAK_DORKS = {
    'paste_sites':      'site:pastebin.com OR site:justpaste.it "password" OR "api_key"',
    'github_leaks':     'site:github.com "BEGIN RSA PRIVATE KEY" OR "api_key" OR "password"',
    's3_buckets':       'site:s3.amazonaws.com "target"',
    'email_lists':      'filetype:xlsx OR filetype:csv "email" "@target.com"',
    'financial':        'filetype:xlsx "confidential" "budget" OR "salary" OR "invoice"',
}

# Google Hacking Database (GHDB) — additional categories
GHDB_CATEGORIES = [
    'Advisories and Vulnerabilities',
    'Error Messages',
    'Files Containing Juicy Info',
    'Files Containing Passwords',
    'Files Containing Usernames',
    'Footholds',
    'Network or Vulnerability Data',
    'Pages Containing Login Portals',
    'Sensitive Directories',
    'Sensitive Online Shopping Info',
    'Various Online Devices',
    'Vulnerable Files',
    'Web Server Detection',
]
```

---

## 2. Technical Reconnaissance Engines

### Shodan

```python
SHODAN_QUERIES = {
    'org':           'org:"Target Corp" — filter by organization',
    'hostname':      'hostname:target.com — exact hostname',
    'port':          'port:22 — open SSH ports',
    'product':       'product:"Apache httpd" — specific service',
    'version':       'version:2.4.49 — vulnerable Apache version',
    'country':       'country:CN — filter by country code',
    'city':          'city:"San Francisco"',
    'os':            'os:"Windows Server 2019"',
    'net':           'net:1.2.3.0/24 — CIDR range',
    'ssl':           'ssl:"target.com" — SSL certificates',
    'http.title':    'http.title:"Dashboard"',
    'http.status':   'http.status:200',
    'vuln':          'vuln:CVE-2021-41773 — known vulnerable',
    'has_screenshot': 'has_screenshot:true',
    'before/after':  'http.component:"jQuery" before:2020',
}

# Shodan API
def shodan_search(query: str, api_key: str):
    import requests
    r = requests.get(f'https://api.shodan.io/shodan/host/search',
                     params={'key': api_key, 'query': query})
    return r.json()

# Censys equivalent
def censys_search(query: str, api_id: str, api_secret: str):
    import requests
    r = requests.get('https://search.censys.io/api/v2/hosts/search',
                     auth=(api_id, api_secret),
                     params={'q': query, 'per_page': 100})
    return r.json()

# FOFA (Chinese engine — great for APAC targets)
FOFA_QUERIES = {
    'domain':        'domain="target.com"',
    'title':         'title="admin"',
    'body':          'body="password"',
    'header':        'header="server: nginx"',
    'cert':          'cert="target.com"',
    'ip':            'ip="1.2.3.4"',
    'country':       'country="JP"',
    'protocol':      'protocol="rdp"',
    'banner':        'banner="SSH-2.0"',
}
```

### ProjectDiscovery Uncover — Multi-Engine

```bash
# Search across Shodan, Censys, FOFA, ZoomEye simultaneously
uncover -q 'ssl:"target.com"' -e shodan,censys,fofa

# Filter and probe live hosts
uncover -q 'title:"admin"' -e shodan,censys | httpx -mc 200 -title -tech-detect
```

---

## 3. Domain, DNS & Subdomain Recon

### Certificate Transparency

```bash
# crt.sh — primary source
curl -s "https://crt.sh/?q=%25.target.com&output=json" | \
  python3 -c "import sys,json; [print(d['name_value']) for d in json.load(sys.stdin)]" | \
  sort -u

# Use jq for better filtering
curl -s "https://crt.sh/?q=%25.target.com&output=json" | \
  jq -r '.[].name_value' | sed 's/\\*\\.//g' | sort -u

# certspotter API
curl -s "https://api.certspotter.com/v1/issuances?domain=target.com&expand=dns_names" | \
  jq -r '.[].dns_names[]' | sort -u
```

### Passive DNS Sources

```python
PASSIVE_DNS_SOURCES = {
    'SecurityTrails': 'https://securitytrails.com/app/api — API-based, historical DNS',
    'VirusTotal': 'https://www.virustotal.com/api/v3/domains/{domain}/subdomains',
    'AlienVault OTX': 'https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns',
    'DNSDumpster': 'https://dnsdumpster.com/ — free web-based DNS recon',
    'Netlas': 'https://netlas.io/ — Russian, good for CIS region',
    'URLScan': 'https://urlscan.io/api/v1/search/?q=domain:target.com',
    'Riddler': 'https://riddler.io/search?q=pld:target.com',
    'Robtex': 'https://www.robtex.com/dns-lookup/',
    'ThreatCrowd': 'https://www.threatcrowd.org/domain.php?domain=target.com',
}
```

### Automated Subdomain Enumeration

```python
# Amass (OWASP) — most comprehensive
"""
amass enum -passive -d target.com -o passive.txt
amass enum -active -d target.com -o active.txt
amass intel -org "Target Corp" -o asn.txt
"""

# Subfinder + HTTP probing pipeline
"""
subfinder -d target.com -o subs.txt
cat subs.txt | httpx -mc 200,403 -title -tech-detect -status-code -o alive.txt
cat subs.txt | httpx -path /admin -mc 200 -o admin_panels.txt
"""

# PureDNS + wordlist bruteforce
"""
puredns bruteforce wordlist.txt target.com -r resolvers.txt -w bruteforce.txt
"""
```

### DNS Record Enumeration

```bash
# All record types
for rtype in A AAAA MX NS TXT CNAME SOA PTR SRV CAA; do
    echo "=== $rtype ==="
    dig +short target.com $rtype
done

# Zone transfer attempt
dig AXFR target.com @ns1.target.com

# DNS rebinding check
dig @1.1.1.1 target.com  # Test different resolvers

# SPF/DMARC/DKIM
dig TXT target.com | grep -i "spf\|v=spf1"
dig TXT _dmarc.target.com
dig TXT google._domainkey.target.com
```

---

## 4. Email Intelligence

### Email Discovery & Verification

```python
EMAIL_TOOLS = {
    'hunter.io': 'Find emails by domain — pattern: firstname.lastname@company.com',
    'holehe': 'Check if email is registered on 100+ services (GitHub, Twitter, Spotify...)',
    'h8mail': 'Email breach hunting — query against breaches and data dumps',
    'haveibeenpwned': 'Check email against known data breaches (via API)',
    'emailrep.io': 'Email reputation and risk scoring',
    'verifyemail': 'SMTP verification — check if mailbox exists',
    'ghunt': 'Google account OSINT — Google IDs, Maps reviews, YouTube',
    'theHarvester': 'Email enumeration from search engines',
    'mosint': 'All-in-one email OSINT tool',
    'infoga': 'Email information gathering',
}
```

### Email Patterns

```python
# Common corporate email patterns
EMAIL_PATTERNS = [
    ' {first}.{last}@{domain}',
    ' {first}{last}@{domain}',
    ' {first}_{last}@{domain}',
    ' {f}{last}@{domain}',
    ' {first}.{middle}.{last}@{domain}',
    ' {first}{last_initial}@{domain}',
]

# Generate all variants
def generate_emails(first, last, domain):
    variants = [
        f'{first}.{last}@{domain}',
        f'{first}{last}@{domain}',
        f'{first}_{last}@{domain}',
        f'{first[0]}{last}@{domain}',
        f'{first}{last[0]}@{domain}',
        f'{first[0]}.{last}@{domain}',
        f'{last}.{first}@{domain}',
    ]
    return variants
```

### Breach Data Queries

```python
# HIBP API v3
def check_hibp(email: str, api_key: str):
    """Check HaveIBeenPwned for breaches."""
    import requests
    headers = {'hibp-api-key': api_key, 'user-agent': 'OSINT-tool'}
    r = requests.get(f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}',
                     headers=headers)
    if r.status_code == 200:
        return [b['Name'] for b in r.json()]
    return []

# Dehashed — search across breaches
def search_dehashed(email: str, api_key: str, username: str):
    """Search Dehashed for credentials."""
    import requests
    auth = (username, api_key)
    r = requests.get(f'https://api.dehashed.com/search?query=email:{email}',
                     auth=auth)
    return r.json()
```

---

## 5. Social Media Intelligence (SOCMINT)

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

## 6. Image & Geolocation OSINT

### Reverse Image Search

```python
IMAGE_SEARCH_ENGINES = {
    'Google Images': 'https://images.google.com — most comprehensive',
    'Yandex Images': 'https://yandex.com/images — best for faces/Eastern Europe',
    'TinEye': 'https://tineye.com — oldest, best for copyright',
    'Bing Images': 'https://www.bing.com/images',
    'Baidu Images': 'https://image.baidu.com — Chinese web',
    'PimEyes': 'https://pimeyes.com — facial recognition (paid)',
}
```

### EXIF / Metadata Extraction

```python
# exiftool — extract all metadata
# exiftool -a -u -g1 image.jpg

EXIF_CHECKLIST = [
    'GPS coordinates (GPSLatitude, GPSLongitude)',
    'Camera make/model',
    'Timestamp (DateTimeOriginal, CreateDate)',
    'Software used (editing traces)',
    'Device serial number',
    'Thumbnail (may contain original uncropped image)',
    'XMP metadata (Lightroom edits, ratings)',
    'ICC profile (color space info)',
]

# Strip metadata (privacy)
# exiftool -all= image.jpg
```

### Satellite & Street View

```python
SATELLITE_TOOLS = {
    'Google Earth Pro': 'Historical imagery timeline (desktop app)',
    'Sentinel Hub': 'https://apps.sentinel-hub.com — ESA free satellite',
    'Zoom Earth': 'https://zoom.earth — live satellite/hurricane tracker',
    'Maxar': 'High-resolution commercial imagery (paid)',
    'Planet': 'Daily satellite imagery (paid)',
    'TerraServer': 'Historical US aerial photos',
    'OpenStreetCam': 'Crowdsourced street-level imagery',
    'Mapillary': 'Crowdsourced street-level photos (by Meta)',
    'Baidu Street View': 'China street view',
    'Yandex Panorama': 'Russia/CIS street view',
}

# Google Earth Pro — historical analysis
# 1. Navigate to location
# 2. Click clock icon → timeline slider
# 3. Compare images at different dates
# 4. Measure distances, areas, elevations

# Geolocation methodology (Bellingcat):
GEOLOCATION_METHOD = """
1. Identify key landmarks in image (buildings, signs, mountains)
2. Note: architectural style, vegetation, road markings, license plates
3. Check shadows for time-of-day + latitude estimation
4. Reverse image search to find original source
5. Cross-reference with satellite imagery for exact match
6. Verify with street view for confirmation
7. Document evidence: screenshots, coordinates, timestamps
"""
```

### Image Forensics & Verification

```python
IMAGE_FORENSICS = {
    'FotoForensics': 'https://fotoforensics.com — ELA (Error Level Analysis)',
    'Forensically': 'https://29a.ch/photo-forensics — clone detection, noise analysis',
    'InVID': 'Browser extension — video verification toolkit',
    'Jeffrey\'s EXIF': 'Web-based metadata viewer',
    'Ghiro': 'Automated image forensics (open source)',
    'Sherloq': 'SQLite-based image forensics GUI',
}

# Check image manipulation:
# 1. ELA (Error Level Analysis): different compression levels → edited regions
# 2. Clone detection: find duplicated pixel regions
# 3. Noise analysis: inconsistent noise patterns → spliced images
# 4. Metadata vs visual cross-check: timestamp vs shadows/weather
# 5. JPEG compression analysis: multiple compressions → edited
```

---

## 7. People & Identity Intelligence

```python
PEOPLE_SEARCH = {
    # Global
    'WebMii': 'Aggregated web presence score',
    'Pipl': 'Deep people search (paid, powerful)',
    'Spokeo': 'US people search',
    'Whitepages': 'US phone/address lookup',
    'TruePeopleSearch': 'Free US people search',
    
    # Professional
    'LinkedIn X-Ray': 'site:linkedin.com/in/ "first last" company',
    'Crunchbase': 'Startup/executive connections',
    'ZoomInfo': 'B2B contact database (paid)',
    'RocketReach': 'Professional email/phone finder',
    
    # Criminal/Public Records
    'PACER': 'US federal court records (paid per page)',
    'JudyRecords': 'US court records search',
    'FamilySearch': 'Genealogical records',
    'Companies House': 'UK company director search',
    'SEC EDGAR': 'US corporate filings with executive info',
    
    # Username cross-reference
    'NameChk': 'Username availability check across platforms',
    'CheckUserNames': 'Check username on 160+ social networks',
    'NameCheckup': 'Domain + username availability',
}
```

---

## 8. Phone Number Intelligence

```python
PHONE_OSINT = {
    'phone2location': 'Geolocation and carrier lookup',
    'numverify': 'API-based phone validation',
    'truecaller': 'Crowdsourced caller ID (India/developing world — very effective)',
    'sync.me': 'Caller ID and spam detection',
    'spytox': 'Free reverse phone lookup (US)',
    'opencnam': 'Caller ID API',
    'twilio': 'Programmatic phone lookup',
    'ignorant': 'Check phone presence on services (Amazon, Instagram, Snapchat...)',
}

# Phone format normalization
def normalize_phone(phone: str) -> dict:
    """Parse phone number into components."""
    import re
    # Strip non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Try to identify country code
    if digits.startswith('1') and len(digits) == 11:  # US/Canada
        return {'country': 'US', 'cc': '1', 'number': digits[1:]}
    elif digits.startswith('86') and len(digits) >= 13:  # China
        return {'country': 'CN', 'cc': '86', 'number': digits[2:]}
    elif digits.startswith('44'):  # UK
        return {'country': 'GB', 'cc': '44', 'number': digits[2:]}
    
    return {'raw': digits}
```

---

## 9. Financial & Corporate Intelligence

```python
CORPORATE_SOURCES = {
    'opencorporates': 'Global company registry — free API',
    'SEC EDGAR': 'US public company filings (10-K, 10-Q, 8-K, S-1)',
    'Companies House': 'UK company registry',
    'ICIJ Offshore Leaks': 'Offshore entities database',
    'OpenOwnership': 'Beneficial ownership register',
    'Dun & Bradstreet': 'Business credit reports (paid)',
    'Clearbit': 'Company enrichment API',
    'Crunchbase': 'Startup funding, investors, employees',
    'AngelList': 'Startup jobs and investors',
    'PitchBook': 'Private company data (paid)',
}

# SEC EDGAR search
# site:sec.gov "Target Corp" filetype:10-K

# OpenCorporates API
"""
curl -s "https://api.opencorporates.com/v0.4/companies/search?q=tesla" | jq .
"""
```

---

## 10. Blockchain & Cryptocurrency OSINT

```python
BLOCKCHAIN_OSINT = {
    # BTC explorers
    'blockchain.com': 'Most popular, address/tx visualization',
    'blockchair': 'Multi-blockchain, address clustering hints',
    'oxt.me': 'Advanced BTC analysis, privacy metrics',
    'walletexplorer': 'Wallet clustering (algorithmic grouping)',
    'crystalblockchain': 'Visual transaction graph (paid)',
    
    # ETH/ EVM explorers
    'etherscan': 'ETH main explorer — contract code, events, tokens',
    'ethplorer': 'Token-focused ETH explorer',
    'debank': 'DeFi portfolio tracker — see all wallets',
    'zapper': 'Multi-chain DeFi dashboard',
    
    # Multi-chain
    'blockscan': 'Multi-chain by Etherscan team',
    'breadcrumbs': 'Transaction tracing and risk scoring (paid)',
    'chainalysis': 'Enterprise blockchain intelligence',
    'elliptic': 'Crypto compliance and forensics',
    
    # Entity attribution
    'arkham': 'Blockchain deanonymization (paid, powerful)',
    'nansen': 'Smart money tracking, wallet labeling (paid)',
}

# Quick Blockchain Recon
def blockchain_recon(address: str):
    """Gather intelligence from a blockchain address."""
    import requests
    
    results = {}
    
    # Check multiple explorers
    for chain, api in [
        ('ETH', f'https://api.etherscan.io/api?module=account&action=txlist&address={address}'),
        ('BTC', f'https://blockchain.info/rawaddr/{address}'),
    ]:
        try:
            r = requests.get(api)
            results[chain] = r.json()
        except:
            pass
    
    return results

# NFT OSINT
NFT_OSINT = {
    'opensea_activity': 'Track NFT purchases, transfers, holdings',
    'nftgo': 'NFT portfolio analytics',
    'icy_tools': 'NFT market intelligence',
    'context': 'NFT social graph and feed',
}

# Crypto AML red flags
CRYPTO_RED_FLAGS = [
    'Transactions involving OFAC-sanctioned addresses',
    'Deposits from darknet market wallets',
    'Mixing/tumbling service interactions',
    'Chain-hopping (ETH → BTC → XMR) — privacy coin conversion',
    'Peel chains — splitting large amounts into small tx',
    'Use of non-KYC exchanges (Bisq, HodlHodl)',
    'Flash loan attacks — borrowed funds → exploit → repay',
    'Dust attacks — small amounts sent to deanonymize wallets',
]
```

---

## 11. Dark Web Intelligence

```python
DARKWEB_SOURCES = {
    'ahmia': 'Tor search engine',
    'torch': 'Oldest Tor search engine',
    'darkfail': 'List of verified .onion sites',
    'onionland': 'Tor directory',
    'darknetlive': 'Darknet market news and statistics',
    'ransomwatch': 'Ransomware leak site monitoring',
    'darkfeed': 'Threat intelligence from dark web sources',
}

# Note: Always use Tor browser or torify when accessing .onion sites
# torify curl http://darknetlidvrs.onion/
```

---

## 12. Wireless & RF Intelligence

```python
WIRELESS_OSINT = {
    'wigle': 'WiFi network geolocation database — 1B+ networks',
    'opensky-network': 'ADS-B flight tracking (free API)',
    'flightradar24': 'Commercial flight tracking',
    'marinetraffic': 'AIS vessel tracking',
    'shodan_iot': 'WiFi cameras, SCADA, industrial control',
    'cellmapper': 'Cell tower location mapping',
    'opencellid': 'Cell tower database API',
    'nperf': 'Network coverage maps',
}

# ADS-B Flight Intelligence
"""
curl -s "https://opensky-network.org/api/states/all" | jq '.states[] | select(.[1] | startswith("N"))'
"""
```

---

## 13. Automated OSINT Workflow

```python
#!/usr/bin/env python3
"""Complete automated OSINT pipeline for a target."""

import subprocess
import json
import concurrent.futures

def full_osint_pipeline(target_domain: str, target_email: str = None, 
                         target_username: str = None, target_phone: str = None):
    """Run complete OSINT pipeline in parallel."""
    
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {}
        
        # Domain recon
        futures[executor.submit(domain_recon, target_domain)] = 'domain'
        
        # Certificate transparency
        futures[executor.submit(ct_search, target_domain)] = 'cert_transparency'
        
        # Shodan search
        futures[executor.submit(shodan_org_search, target_domain)] = 'shodan'
        
        # Google dorking
        futures[executor.submit(google_dorks, target_domain)] = 'dorks'
        
        # Wayback Machine
        futures[executor.submit(wayback_urls, target_domain)] = 'wayback'
        
        # Email OSINT (if provided)
        if target_email:
            futures[executor.submit(email_osint, target_email)] = 'email'
        
        # Username search (if provided)
        if target_username:
            futures[executor.submit(username_search, target_username)] = 'username'
        
        # Phone lookup (if provided)
        if target_phone:
            futures[executor.submit(phone_lookup, target_phone)] = 'phone'
        
        # GitHub search
        futures[executor.submit(github_search, target_domain)] = 'github'
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = {'error': str(e)}
    
    return results

def domain_recon(domain: str):
    """DNS and subdomain enumeration."""
    results = {}
    
    # WHOIS
    r = subprocess.run(['whois', domain], capture_output=True, text=True, timeout=15)
    results['whois'] = r.stdout[:2000]
    
    # DNS records
    for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']:
        r = subprocess.run(['dig', '+short', domain, rtype], 
                          capture_output=True, text=True, timeout=10)
        results[rtype] = r.stdout.strip()
    
    return results

def ct_search(domain: str):
    """Certificate transparency subdomain search."""
    import requests
    r = requests.get(f'https://crt.sh/?q=%25.{domain}&output=json', timeout=30)
    if r.status_code == 200:
        subs = set()
        for entry in r.json():
            name = entry.get('name_value', '')
            for n in name.split('\n'):
                n = n.strip().lstrip('*.')
                if n.endswith(domain):
                    subs.add(n)
        return sorted(list(subs))
    return []

def google_dorks(domain: str):
    """Run key Google dorks."""
    dorks = [
        f'site:{domain}',
        f'site:{domain} filetype:pdf',
        f'site:{domain} intitle:"index of"',
        f'site:{domain} inurl:admin',
        f'site:{domain} ext:sql OR ext:bak OR ext:old',
    ]
    return {'dorks': dorks, 'note': 'Execute in browser or via custom search API'}

def wayback_urls(domain: str):
    """Get historical URLs from Wayback Machine."""
    import requests
    r = requests.get(f'https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&fl=original&collapse=urlkey', timeout=30)
    if r.status_code == 200:
        return [row[0] for row in r.json()[1:]]  # skip header
    return []

def github_search(domain: str):
    """GitHub code search for secrets."""
    queries = [
        f'"{domain}" password OR secret OR api_key OR token',
        f'"{domain}" BEGIN RSA PRIVATE KEY',
        f'"{domain}" "DB_PASSWORD" OR "DATABASE_URL" OR "SECRET_KEY"',
    ]
    return {'queries': queries, 'note': 'Search manually at github.com/search?q=...'}
```

---

## 14. OSINT Tool Matrix

```python
TOOL_MATRIX = {
    'all_in_one': {
        'spiderfoot': '200+ data sources, automated scanning, web UI. **INSTALLED at ~/tools/spiderfoot/** (SpiderFoot 4.0, 231 modules, Python 3.11). Use skill `spiderfoot-osint` for CLI/HX2/fallback automation. One-line scan: `sfo.py scan -s target@example.com -o ~/osint-reports/`.',
        'recon-ng': 'Modular CLI, marketplace of modules',
        'maltego': 'Graph visualization, transform hub (paid CE free tier)',
        'sn0int': 'Rust-based, semi-automatic OSINT framework',
        'lampyre': 'One-click data collection, paid but powerful',
        'osint_industries': '2026: Email/phone/username enrichment API with 100+ modules, pay-per-use',
        'hunchly': '2026: Automated evidence capture & case management for OSINT investigations',
        'whatsmyname_web': '2026: Web-based username checker across 600+ platforms (whatsmyname.app)',
    },
    'domain': {
        'amass': 'Subdomain enumeration, ASN mapping',
        'subfinder': 'Fast passive subdomain discovery',
        'puredns': 'DNS bruteforce with resolution',
        'dnsrecon': 'DNS enumeration and zone transfer',
        'od_crawler': '2026: OD Crawler - automated web crawler for OSINT (OD-Crawler GitHub)',
        'dorkgpt': '2026: DorkGPT - AI-generated Google dorks for target recon',
        'dork_search_pro': '2026: Dork Search Pro - advanced dork builder & executor',
    },
    'email': {
        'holehe': 'Account presence checker',
        'h8mail': 'Breach data hunting',
        'ghunt': 'Google account OSINT: Google account OSINT',
        'infoga': 'Email information gathering',
    },
    'social': {
        'sherlock': 'Username search (300+ sites)',
        'maigret': 'Username search (3000+ sites, v2026+ covers 3000+ platforms)',
        'snscrape': 'Social media scraper (Twitter, Reddit, TikTok)',
        'tokintel': '2026: TokIntel - TikTok OSINT: account creation date via snowflake ID, video timestamps, cross-platform pivot',
        'discordosint': '2026: DiscordOSINT - Discord user/server enumeration, message scraping via Discord API',
        'telegram_osint_lib': '2026: telegram-osint-lib - Python lib for Telegram channel/group scraping, member enumeration',
        'threads_osint': '2026: Threads.net OSINT via Meta Graph API + public profile scraping',
        'bluesky_osint': '2026: Bluesky AT Protocol OSINT - public firehose, profile resolution, feed analysis',
    },
    'technical': {
        'shodan': 'IoT/device search',
        'censys': 'Internet asset discovery',
        'nmap': 'Port scanning and service detection',
        'httpx': 'HTTP probing with tech detection',
        'uncover': 'Multi-engine (Shodan/Censys/FOFA/ZoomEye) unified search',
    },
    'image': {
        'exiftool': 'Metadata extraction',
        'fotoforensics': 'Image forensics (ELA)',
        'google_images': 'Reverse image search',
        'pimeyes': 'AI facial recognition search (paid, most powerful)',
        'yandex_images': 'Best for Eastern Europe/faces reverse image search',
        'lenso_ai': '2026: Lenso.ai - AI reverse image search with face/place/duplicate filters',
        'eyematch_ai': '2026: EyeMatch.ai - AI face search + digital footprint monitoring',
        'social_catfish': 'Reverse image + social profile verification (paid)',
    },
    'ai_osint': {
        'pimeyes': 'Facial recognition search engine (paid)',
        'clearview_ai': 'LE-only facial recognition (law enforcement)',
        'yandex_images': 'Best free facial recognition for Eastern Europe/Russia',
        'deepfake_detector': '2026: DeepFake-O-Meter / Sensity / Microsoft Video Authenticator / InVID-WeVerify plugin',
        'sentinel_hub': 'Copernicus Browser - free Sentinel-2/Landsat multispectral satellite imagery',
        'esri_wayback': 'Esri World Imagery Wayback - historical satellite layers with timestamps',
        'bellingcat_shadow_finder': '2026: Shadow Finder - geolocation via shadow length + sun angle calculation',
        'bellingcat_osm_search': '2026: OSM Search - OpenStreetMap feature search for geolocation seeding',
    },
    'blockchain': {
        'arkham': 'Blockchain deanonymization (paid, powerful)',
        'nansen': 'Smart money tracking, wallet labeling (paid)',
        'chainalysis': 'Enterprise blockchain intelligence, Reactor for investigations',
        'elliptic': '99% chain coverage, cross-chain tracing, compliance',
        'trm_labs': '2026: TRM Forensics - 65+ chains, AI assistant, glass-box attribution, off-chain graph elements',
        'allium': '2026: Allium - flexible data infra, new chain support in days, custom detection models',
        'blockscan': 'Multi-chain explorer by Etherscan team',
        'breadcrumbs': 'Transaction tracing + risk scoring (paid)',
    },
    'darkweb': {
        'ahmia': 'Tor search engine',
        'torch': 'Oldest Tor search engine',
        'darkfail': 'Verified .onion site list',
        'ransomwatch': 'Ransomware leak site monitoring',
        'socradar_darkweb_radar': '2026: SOCRadar Dark Web Radar - continuous monitoring of markets, forums, Telegram, stealer logs',
        'whiteintel': '2026: WhiteIntel - stealer logs, marketplaces, combolists, lookalike domains, secrets in code',
        'huntress_darkweb': '2026: Huntress Dark Web Monitoring - credential monitoring with automated remediation',
        'deepstrike': '2026: DeepStrike - free/paid dark web monitoring for stolen data detection',
    },
    'breach_intel': {
        'haveibeenpwned': 'Email breach check (free + API)',
        'dehashed': '2026: Largest breach database, API, domain/IP/username/email search, stealer logs',
        'leak_lookup': '2026: Leak-Lookup - real-time breach search engine with API',
        'intelligence_x': '2026: Intelligence X - archives + dark web + leaks, search by selector (email/domain/IP/CIDR/BTC)',
        'databreach_com': '2026: DataBreach.com - latest breach timeline, 2025-2026 incidents',
        'bitsight_pulse': '2026: Bitsight Pulse - continuous breach monitoring + underground forum intel',
    },
    'geolocation': {
        'google_earth_pro': 'Historical imagery timeline (desktop)',
        'sentinel_hub': 'Copernicus Browser - free Sentinel multispectral (5-10 day revisit)',
        'esri_wayback': 'Esri World Imagery Wayback - historical high-res satellite layers',
        'maxar': 'Commercial 30cm imagery (paid)',
        'planet': 'Daily satellite imagery (paid)',
        'stadia_maps': '2026: Stadia Maps / Alidade Satellite - 37M km² at 30cm resolution',
        'bellingcat_shadow_finder': 'Shadow-based geolocation via sun angle calculation',
        'bellingcat_osm_search': 'OSM feature search for geolocation seeding',
        'mapillary': 'Crowdsourced street-level (Meta)',
        'openstreetcam': 'Crowdsourced street-level',
    },
    'aviation_maritime': {
        'adsb_exchange': '2026: ADS-B Exchange - largest independent ADS-B network, unfiltered, 500ms latency, historical',
        'opensky_network': 'OpenSky - free ADS-B/Mode-S/FLARM data, research API, 14th Symposium 2026',
        'flightradar24': 'Commercial flight tracking, 50k+ receivers',
        'adsb_im': '2026: adsb.im - unified feeder image for ADS-B + AIS (ships) + Sonde + ACARS/VDL2/HFDL',
        'marinetraffic': 'Global AIS vessel tracking, real-time routes/ports/speed',
        'vesselfinder': 'Alternative AIS vessel tracking',
    },
    'china_asia_osint': {
        'zhihu_osint': '2026: Zhihu OSINT program (EPCyber) - Chinese Quora, real-name, expert profiles',
        'wechat_osint': '2026: WeChat OSINT - public articles (sogou.com search), Moments via OSINT Combine course',
        'weibo_osint': '2026: Weibo OSINT - Chinese Twitter, search via weibo.com + advanced operators',
        'douyin_osint': '2026: Douyin (TikTok CN) OSINT - Xigua/Toutiao ecosystem, watermark analysis',
        'bilibili_osint': '2026: Bilibili OSINT - video metadata, user activity, danmaku analysis',
        'xhs_osint': '2026: XiaoHongShu (Little Red Book) OSINT - lifestyle/shopping, geotagged posts',
        'tianyancha': '2026: Tianyancha / Qichacha - Chinese company registry, shareholder, legal cases',
        'courts_china': '2026: China Judgments Online (wenshu.court.gov.cn) - court records, requires CN IP/account',
        'osint_tools_china_github': 'paulpogoda/OSINT-Tools-China - curated list: courts, data portals, legal entities, stocks, vehicles',
    },
    'privacy_regulatory': {
        'eu_ai_act': '2026: EU AI Act full enforcement Aug 2, 2026 - high-risk AI requires DPIA+FRIA, GPAI transparency',
        'gdpr_enforcement': '2026: Stricter GDPR - consent management, DPIAs for AI training/facial rec, 80%+ global pop covered',
        'us_state_laws': '2026: 20+ US state privacy laws (Kentucky, Rhode Island, Indiana GPC recognition Jan 2026)',
        'china_pipl': 'China PIPL extraterritorial - overseas processors of CN data must appoint CN rep + register with CAC',
        'india_dpdp': '2026: India DPDP Act - consent managers, verifiable parental consent for minors',
        'osint_impact': 'OSINT collectors must: honor GPC signals, document lawful basis, minimize personal data, enable DSAR',
    },
}
```

## 2025-2026 OSINT Updates

### New OSINT Landscape

```python
OSINT_2026 = """
# OSINT market 2025: $11.6-12.7B, growing 20-28% CAGR.
# 2026: 93 commercial OSINT tools across 12 categories (joinmassive.com).
# Key shift: AI-powered collection + automated enrichment replacing manual workflows.

# New platform categories:
# 1. Attack Surface Management (ASM) — Bitsight, ShadowDragon Horizon
# 2. AI-OSINT — LLM-powered entity resolution + auto-reporting
# 3. Dark web Monitoring-as-a-Service — Ransomware leak site tracking
# 4. Supply chain OSINT — SBOM + dependency graph intelligence
"""
```

### New Social Platforms (2025-2026)

```python
NEW_PLATFORMS = {
    'threads': 'Meta Threads — 350M+ MAU, growing for OSINT',
    'bluesky': 'Bluesky — AT Protocol, growing dev/journalist user base',
    'mastodon': 'Federated, harder to search — use instance-specific search',
    'nostr': 'Decentralized protocol — note IDs are global, search via nostr.band',
    'discord': 'Use Discord ID lookup + guild enumeration (requires bot token)',
    'telegram': 'TelegramDB, Telemetr, TGStat — channel analytics + search',
    'tiktok_search': 'TikTok search has surpassed Google for Gen Z queries',
}
```

### AI-Powered OSINT (2025-2026)

```python
AI_OSINT = """
# Facial Recognition:
# - PimEyes (paid) — still most powerful public face search
# - FaceCheck.ID — free tier, growing database
# - Search4Faces — VK-heavy, good for Russian/CIS targets

# Deepfake Detection:
# - Deepware Scanner — API-based detection
# - Sensity AI — deepfake + face manipulation detection
# - Truepic — photo authenticity verification

# LLM-Powered OSINT:
# - SpiderFoot 4.x — LLM-powered entity enrichment
# - ShadowDragon — 600+ data sources with AI correlation
"""
```

### Blockchain Forensics 2025

```python
BLOCKCHAIN_2025 = """
# New: Cross-chain tracing
# - Chainflip, THORChain, LayerZero bridges → trace across chains
# - Bridge exploits are the new mixers (large volume, hard to follow)

# DeFi OSINT:
# - DeBank: track wallet across all chains + DeFi positions
# - Zapper: multi-chain portfolio with historical data
# - Arkham: deanonymize wallet-to-entity attribution (paid)

# NFT forensics:
# - NFTGo: NFT portfolio + trading history
# - icy.tools: wallet NFT holdings + transfers
# - Wash trading detection: look for self-transfers + zero-value sales
"""
```

### Dark Web Monitoring 2025

```python
DARKWEB_2025 = """
# Ransomware leak sites (2025-2026 active groups):
# - LockBit 5.0 (resurgent after takedown)
# - BlackCat/ALPHV (rebranded as RansomHub)
# - CL0P (active — CitrixBleed 2, Oracle EBS campaigns)
# - Play, Akira, Medusa, BianLian, Hunting Hooligan

# Monitoring tools:
# - ransomwatch (open source) — tracks leak sites
# - darkfeed — threat intel from dark web
# - Ahmia — Tor search engine
# - DarkOwl (paid) — dark web content indexing
"""
```

---

## 2025-2026 OSINT Updates

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

## Username Disambiguation — Critical OSINT Pattern (NEW)

**The `yuanhan@mail.tca.org.tw` investigation revealed a universal OSINT trap:**

Common usernames (`yuanhan`, `john`, `admin`, `alex`, `chen`, `wang`, `lee`, `kim`, `smith`, `test`, `demo`, etc.) are **shared by many different people** across platforms. A single username seed like `yuanhan` resolves to **multiple distinct real-world identities**:

| Platform | Displayed Identity | Likely Distinct Person |
|---|---|---|
| GitHub (`github.com/yuanhan`) | **袁晗 / Han Yuan** — 上海財經大學助理教授, 經濟學博士 | Person A |
| GitLab (`gitlab.com/yuanhan`) | **Henry Lee** | Person B |
| Behance (`behance.net/yuanhan`) | **YUAN HAN in USA** (designer) | Person C |
| SoundCloud (`soundcloud.com/yuanhan`) | Located **Shanghai** | Person D |
| TCA Innoserve Awards | `yuanhan@mail.tca.org.tw` — 專案承辦人, 電話 #879 | Person E (target) |

**Key insight**: `yuanhan` is a common romanization for 袁瀚 / 源瀚 / 苑涵 / 遠涵 / 元瀚… — **at least 4-5 different people** actively use this handle. The 110 "high-confidence" accounts from username-scanner are a **collage of multiple identities**, not one person.

### Disambiguation Protocol (Add to Your Workflow)

1. **Treat username hits as "candidate profiles", not confirmed identities**
   - Every `ACCOUNT_EXTERNAL_OWNED` hit from a common username is a *hypothesis*, not a fact.

2. **Require cross-platform attribute correlation for confirmation**
   - Same avatar hash (Gravatar) across GitHub + GitLab + Behance?
   - Same bio snippet ("PhD Economics, Arizona") on LinkedIn + GitHub + personal site?
   - Same email in public commits (GitHub) matching the seed email?
   - Same location (Shanghai / Taipei / USA) declared consistently?

3. **Use "anchor attributes" to cluster profiles into personas**
   - Anchor = rare, specific attribute (personal site URL, ORCID, unique email, published paper DOI, ORCID)
   - Cluster all profiles sharing ≥1 anchor → persona
   - Profiles with zero anchors → "unattributed candidate"

4. **Document attribution confidence per profile**
   - **Confirmed**: ≥2 independent anchors match seed
   - **Probable**: 1 anchor + consistent bio/location
   - **Candidate**: Username match only, no anchors
   - **Different person**: Conflicting anchors (different PhD university, different name, different country)

5. **In reports, always separate "seed-attributed" vs "username-candidate" findings**
   - Seed-attributed: breach events for `yuanhan@mail.tca.org.tw`, TCA contact page listing
   - Username-candidate: 110 username-scanner accounts (flag as "requires disambiguation")

See `spiderfoot-osint` skill for full Disambiguation Protocol, templates, and investigation patterns.
- **Yahoo TW noise traps on cold CJK names** (R1): When the queried Chinese name is rare/cold, Yahoo TW does TWO things that look like hits but aren't: (a) **phonetic / semantic substitution** — "王池川" silently becomes "王治川"/"王義川" and the result list is *all* those substituted names (Wang Yi-chuan, the DPP politician); (b) **`OR` operator is silently dropped** — `"王池川" 老師 OR 教授` becomes `"王池川" 老師 教授` and then `王` (single character), returning 233,000 "王" dictionary entries. Mitigation: never trust a hit count alone — always extract `<h3 class="title"><a href=...>TITLE</a></h3>` titles AND the rendered snippet text and grep for the **exact 3-character name** in the visible text. If `name in title_text` is 0, the count is noise. See `references/cjk-yahoo-tw-noise-trap.md` for the diagnostic recipe + worked example (王池川 2026-06-30), and `scripts/yahoo_cold_name_detector.py` for an automated detector.
- **NDLTD vs TDR captcha asymmetry**: `ndltd.ncl.edu.tw` (國家圖書館 台灣博碩士論文知識加值系統) returns **graphical captcha** on every request when accessed via curl or Playwright from a non-TANet IP — no captcha bypass without (a) TANet IP, (b) library reader account, or (c) OCR. `tdr.lib.ntu.edu.tw` (台大 TDR, different system) does **not** captcha-block but suffers from Tor-SOCKS5 DNS instability. For thesis searches, prefer TDR first; NDLTD only if you can satisfy one of the three conditions.
- **Tor-SOCKS5 DNS for .edu.tw / .gov.tw**: `tdr.lib.ntu.edu.tw`, `moe.edu.tw` and similar Taiwan academic domains **sometimes time out** via `curl --socks5-hostname 127.0.0.1:9050` (curl exit 28, ~12s) — this is the Tor exit's DNS resolution failing, NOT a block. Fallback: Playwright (uses system DNS) or direct curl without Tor. Don't waste cycles re-trying Tor.
- **Legal**: Always verify OSINT is legal in target jurisdiction
- **Privacy laws**: GDPR (EU), CCPA (California), LGPD (Brazil) restrict personal data collection
- **API costs**: Many services have paid tiers beyond free limits
- **Rate limiting**: Aggressive scraping triggers IP bans — use VPN/proxy rotation
- **Data freshness**: OSINT data can be stale — cross-reference with timestamps
- **Attribution**: OSINT alone may not be sufficient for legal attribution
- **OPSEC**: Your searches are logged by providers — use anonymous infrastructure for sensitive ops
