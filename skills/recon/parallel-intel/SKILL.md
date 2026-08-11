---
name: parallel-intel
description: "Parallel intelligence gathering — run web_search + web_extract + arXiv + Playwright browser scraping + API data collection simultaneously for maximum information yield. Use for OSINT, target research, vulnerability intelligence, and competitive analysis."
version: 1.0.0
category: red-teaming
tags: [OSINT, reconnaissance, intelligence, information-gathering, parallel-search, web-scraping, dorking]
related_skills:
  - playwright-browser
  - arxiv
  - cybersecurity
---

# Parallel Intelligence Gathering

Run ALL search and data collection methods **simultaneously** to maximize information yield. Never do sequential searches when you can run them in parallel.

## Core Principle

**Every search must use ALL available methods in parallel.** The first rule of this skill:

> When Hermes needs to search for information, it MUST use `web_search` + `web_extract` + `arXiv` + `Playwright browser` + any API endpoints ALL in parallel. Never sequential.

## Method 1: Parallel Search (Standard Tools)

### Python Pattern for Parallel Searches

```python
from hermes_tools import web_search, web_extract, terminal
import concurrent.futures
import json

def parallel_intel(query: str, arxiv_query: str = None) -> dict:
    """Gather intelligence using all methods in parallel."""
    results = {}
    
    # Phase 1: Parallel search (web_search + arXiv)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(web_search, query, 10): 'web_search',
            executor.submit(web_search, f'site:arxiv.org {query}', 5): 'arxiv_search',
            executor.submit(web_search, f'{query} vulnerability CVE exploit', 5): 'vuln_search',
        }
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = {'error': str(e)}
    
    # Phase 2: Extract content from all URLs in parallel
    all_urls = []
    for source in ['web_search', 'arxiv_search', 'vuln_search']:
        if source in results and 'data' in results[source]:
            for item in results[source]['data'].get('web', []):
                all_urls.append(item['url'])
    
    # Extract in batches of 5
    extracted = []
    for i in range(0, len(all_urls), 5):
        batch = all_urls[i:i+5]
        batch_results = web_extract(batch)
        extracted.extend(batch_results.get('results', []))
    
    return {
        'search_results': results,
        'extracted_content': extracted,
        'total_urls': len(all_urls),
    }
```

### Google Dorking Cheatsheet

```python
DORKS = {
    'exposed_configs': 'intitle:"index of" "config.php" OR "wp-config.php" OR ".env"',
    'exposed_backups': 'intitle:"index of" "backup" OR "dump" OR ".sql" OR ".bak"',
    'login_panels': 'intitle:"login" "admin" inurl:/admin',
    'sensitive_files': 'filetype:pdf OR filetype:xlsx OR filetype:docx "confidential" site:target.com',
    'exposed_databases': 'intitle:"phpMyAdmin" OR intitle:"MongoDB" OR intitle:"phpPgAdmin"',
    'vulnerable_versions': 'inurl:/wp-content/plugins/ OR intext:"Powered by vBulletin"',
    'api_keys_leaked': 'site:github.com OR site:pastebin.com "api_key" OR "secret" OR "token"',
    'subdomains': 'site:*.target.com -www',
    'email_discovery': 'site:target.com "@target.com" filetype:xlsx OR filetype:csv',
    'juicy_dirs': 'intitle:"index of" "admin" OR "backup" OR "private" OR "secret"',
}
```

## OSINT Category Quick Reference

| Category | Primary Tools | Data Sources |
|:---------|:--------------|:-------------|
| **Domain/DNS** | crt.sh, Amass, Subfinder, SecurityTrails | CT logs, DNS, Passive DNS, WHOIS |
| **Technical** | Shodan, Censys, FOFA, ZoomEye, Uncover | Port scans, banners, SSL certs |
| **Email** | holehe, h8mail, HIBP, emailrep.io | Breaches, registrations, reputation |
| **Social (SOCMINT)** | Sherlock, Maigret, snscrape, Maltego | 3000+ platforms, relationships |
| **Images/Geo** | Google Images, Yandex, exiftool, Satellite | EXIF, reverse search, satellite |
| **People** | Spokeo, Whitepages, Pipl, LinkedIn X-Ray | Public records, social profiles |
| **Financial** | OpenCorporates, SEC EDGAR, Crunchbase | Company registries, filings |
| **Blockchain** | Etherscan, Blockchain.com, Arkham | Transactions, wallet clustering |
| **Code** | GitHub, GitLab, searchcode, grep.app | Source code, secrets, configs |
| **Dark Web** | Ahmia, Torch, Darkfail | .onion sites, markets, forums |
| **Wireless** | WiGLE, OpenSky, MarineTraffic | WiFi, ADS-B, AIS |
| **Archive** | Wayback Machine, Archive.today | Historical sites, deleted content |

```python
# Search arXiv for security research papers
from hermes_tools import web_search

def search_security_papers(topic: str) -> list:
    """Find relevant security research papers."""
    queries = [
        f'site:arxiv.org {topic} security 2024 2025',
        f'site:arxiv.org "{topic}" "vulnerability" OR "attack" OR "exploit"',
        f'site:arxiv.org {topic} "large language model" prompt injection',
    ]
    # Run all in parallel
    results = []
    for q in queries:
        r = web_search(q, 5)
        results.extend(r.get('data', {}).get('web', []))
    return results
```

## Method 3: Playwright Browser Intel

Use `playwright-browser` skill for:
- **JavaScript-rendered pages**: Sites that need JS to load content
- **Login-gated content**: Automate login to access protected pages
- **Dynamic scraping**: Infinite scroll, lazy loading, SPAs
- **Screenshot capture**: Visual recon of target pages
- **Form interaction**: Automated form filling and submission

```python
# Quick browser intel via execute_code
import os
exec(open(os.path.join(
    os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")),
    "skills/red-teaming/playwright-browser/scripts/browser_intel.py"
)).read())

# Gather intel from a URL including JS-rendered content
result = browser_intel(
    url="https://target.com",
    screenshot=True,
    extract_links=True,
    extract_forms=True,
    wait_for_network=True,
)
```

## Method 4: OSINT API Collection

### Shodan / Censys Recon

```bash
# Shodan search (requires API key)
curl -s "https://api.shodan.io/shodan/host/search?key=$SHODAN_KEY&query=hostname:target.com" | jq .

# Get all services on a host
curl -s "https://api.shodan.io/shodan/host/1.2.3.4?key=$SHODAN_KEY" | jq .
```

### DNS & WHOIS Recon

```bash
# WHOIS lookup
whois target.com

# DNS enumeration
dig target.com ANY
dig target.com MX
dig target.com NS
dig target.com TXT

# Subdomain discovery via certificate transparency
curl -s "https://crt.sh/?q=%25.target.com&output=json" | jq -r '.[].name_value' | sort -u
```

### Wayback Machine

```bash
# Get historical URLs
curl -s "https://web.archive.org/cdx/search/cdx?url=*.target.com&output=text&fl=original&collapse=urlkey" | sort -u
```

## Full Parallel Intel Pipeline

```python
# Complete pipeline — run ALL methods simultaneously
from hermes_tools import terminal, web_search, web_extract

def full_parallel_intel(target: str, domain: str = None):
    """
    Run ALL intelligence gathering methods in parallel.
    
    Args:
        target: Search query or company name
        domain: Optional domain for DNS/WHOIS recon
    """
    import concurrent.futures
    
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}
        
        # Web searches
        for dork_name, dork_query in [
            ('web_basic', target),
            ('vulnerabilities', f'{target} vulnerability CVE exploit 2024 2025'),
            ('security_audit', f'{target} security audit penetration test report'),
            ('breach_data', f'{target} data breach leaked credentials'),
            ('github_leaks', f'site:github.com {target} password OR secret OR api_key OR token'),
        ]:
            futures[executor.submit(web_search, dork_query, 5)] = dork_name
        
        # If domain provided, do DNS/WHOIS recon
        if domain:
            futures[executor.submit(
                terminal,
                f'whois {domain} 2>/dev/null; echo "---DNS---"; dig {domain} ANY +short 2>/dev/null; echo "---CERT---"; curl -s "https://crt.sh/?q=%25.{domain}&output=json" 2>/dev/null | python3 -c "import sys,json; [print(d[\"name_value\"]) for d in json.load(sys.stdin)]" 2>/dev/null | sort -u | head -30',
                timeout=30
            )] = 'dns_whois'
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = {'error': str(e)}
    
    return results
```

## Post-Intel Processing

After gathering raw intel:

1. **Deduplicate** URLs and findings
2. **Prioritize** by severity (credentials > vulns > recon data)
3. **Cross-reference** findings across sources
4. **Map to frameworks**: MITRE ATT&CK, OWASP, CWE
5. **Generate timeline**: When were vulns disclosed? When were they patched?

## Pitfalls

- **Rate limiting**: Many OSINT APIs have strict rate limits — use delays
- **Legal boundaries**: Scraping may violate ToS — stay within authorized testing scope
- **Data freshness**: Shodan/Censys data may be days/weeks old
- **API keys**: Many OSINT tools require API keys — store in `~/.hermes/credentials/`
- **Noise filtering**: OSINT generates lots of data — filter aggressively for actionable intel
