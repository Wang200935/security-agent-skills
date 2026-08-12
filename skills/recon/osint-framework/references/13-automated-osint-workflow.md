# 13. Automated OSINT Workflow

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
