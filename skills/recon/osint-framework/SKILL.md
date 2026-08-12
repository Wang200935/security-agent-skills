---
name: osint-framework
description: Complete OSINT (Open Source Intelligence) framework — SOCMINT, DNS/domain
  recon, email/phone intelligence, geolocation, image analysis, technical recon, financial/crypto
  OSINT, dark web, government records, and automated toolchains.
version: 1.0.0
category: red-teaming
license: MIT
metadata:
  hermes:
    tags:
    - OSINT
    - intelligence
    - reconnaissance
    - SOCMINT
    - geolocation
    - dorking
    - Shodan
    - darkweb
    - crypto
    - blockchain
    related_skills:
    - web-app-pentest
    - ctf-playbook
    - security-orchestrator
    - username-scanner
    - spiderfoot-osint-automation
    origin: import
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

## See Also

- `references/3-domain-dns--subdomain-recon.md` — 3 Domain Dns  Subdomain Recon
- `references/4-email-intelligence.md` — 4 Email Intelligence
- `references/5-social-media-intelligence-socmint.md` — 5 Social Media Intelligence Socmint
- `references/6-image--geolocation-osint.md` — 6 Image  Geolocation Osint
- `references/7-people--identity-intelligence.md` — 7 People  Identity Intelligence
- `references/8-phone-number-intelligence.md` — 8 Phone Number Intelligence
- `references/9-financial--corporate-intelligence.md` — 9 Financial  Corporate Intelligence
- `references/10-blockchain--cryptocurrency-osint.md` — 10 Blockchain  Cryptocurrency Osint
- `references/11-dark-web-intelligence.md` — 11 Dark Web Intelligence
- `references/12-wireless--rf-intelligence.md` — 12 Wireless  Rf Intelligence
- `references/13-automated-osint-workflow.md` — 13 Automated Osint Workflow
- `references/14-osint-tool-matrix.md` — 14 Osint Tool Matrix
- `references/2025-2026-osint-updates.md` — 2025 2026 Osint Updates
- `references/2025-2026-osint-updates.md` — 2025 2026 Osint Updates
- `references/username-disambiguation--critical-osint-pattern-new.md` — Username Disambiguation  Critical Osint Pattern New
