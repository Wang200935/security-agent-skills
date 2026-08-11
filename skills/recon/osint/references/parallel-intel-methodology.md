# Parallel Intelligence Gathering Methodology

## Core Principle

> When Hermes needs to search for information, it MUST use `web_search` + `web_extract` + `arXiv` + **Playwright browser** + any API endpoints ALL in parallel. Never sequential.

The user explicitly requires Playwright for research tasks. Playwright is essential for JS-rendered pages, GitHub READMEs, forum discussions, and dynamic SPAs that `web_extract` cannot handle.

## Parallel Search Pattern

```python
from hermes_tools import web_search, web_extract, terminal
import concurrent.futures

def parallel_intel(query: str, domain: str = None) -> dict:
    """Gather intelligence using all methods in parallel."""
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}
        
        # Web searches (multiple angles)
        for name, q in [
            ('web_basic', query),
            ('vulnerabilities', f'{query} vulnerability CVE exploit 2025 2026'),
            ('security_audit', f'{query} security audit penetration test report'),
            ('breach_data', f'{query} data breach leaked credentials'),
            ('github_leaks', f'site:github.com {query} password OR secret OR api_key'),
        ]:
            futures[executor.submit(web_search, q, 5)] = name
        
        # DNS/WHOIS recon if domain provided
        if domain:
            futures[executor.submit(
                terminal,
                f'whois {domain} 2>/dev/null; echo "---DNS---"; dig {domain} ANY +short 2>/dev/null; echo "---CERT---"; curl -s "https://crt.sh/?q=%25.{domain}&output=json" 2>/dev/null | python3 -c "import sys,json; [print(d["name_value"]) for d in json.load(sys.stdin)]" 2>/dev/null | sort -u | head -30',
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

## Google Dorking Cheatsheet

```python
DORKS = {
    'exposed_configs': 'intitle:"index of" "config.php" OR "wp-config.php" OR ".env"',
    'exposed_backups': 'intitle:"index of" "backup" OR "dump" OR ".sql" OR ".bak"',
    'login_panels': 'intitle:"login" "admin" inurl:/admin',
    'sensitive_files': 'filetype:pdf OR filetype:xlsx OR filetype:docx "confidential" site:target.com',
    'exposed_databases': 'intitle:"phpMyAdmin" OR intitle:"MongoDB" OR intitle:"phpPgAdmin"',
    'api_keys_leaked': 'site:github.com OR site:pastebin.com "api_key" OR "secret" OR "token"',
    'subdomains': 'site:*.target.com -www',
    'email_discovery': 'site:target.com "@target.com" filetype:xlsx OR filetype:csv',
}
```

## OSINT Category Quick Reference

| Category | Primary Tools | Data Sources |
|:---------|:--------------|:-------------|
| **Domain/DNS** | crt.sh, Amass, Subfinder, SecurityTrails | CT logs, DNS, Passive DNS, WHOIS |
| **Technical** | Shodan, Censys, FOFA, ZoomEye | Port scans, banners, SSL certs |
| **Email** | holehe, h8mail, HIBP, emailrep.io | Breaches, registrations, reputation |
| **Social (SOCMINT)** | Sherlock, Maigret, snscrape, Maltego | 3000+ platforms, relationships |
| **Images/Geo** | Google Images, Yandex, exiftool, Satellite | EXIF, reverse search, satellite |
| **Blockchain** | Etherscan, Blockchain.com, Arkham | Transactions, wallet clustering |

## Post-Intel Processing

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
