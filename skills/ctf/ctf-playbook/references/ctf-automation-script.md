# CTF Automation Script

```python
#!/usr/bin/env python3
"""CTF auto-solver helper — try common patterns."""

import requests
import re
import base64
import sys

def auto_try_web(url: str):
    """Quick web challenge analysis."""
    results = {}
    
    # Get page
    r = requests.get(url)
    html = r.text
    
    # Check for flags in source
    flag_patterns = [
        r'flag\{[^}]+\}', r'CTF\{[^}]+\}', r'ctf\{[^}]+\}',
        r'FLAG\{[^}]+\}', r'answer\{[^}]+\}',
    ]
    for pattern in flag_patterns:
        match = re.search(pattern, html)
        if match:
            results['flag_in_source'] = match.group()
    
    # Check common endpoints
    for path in ['robots.txt', '.git/HEAD', '.env', 'flag.txt', 'flag', 
                 'admin', 'backup', '.svn/entries', '.DS_Store']:
        try:
            r2 = requests.get(f'{url.rstrip("/")}/{path}', timeout=5)
            if r2.status_code == 200:
                results[f'found_{path}'] = r2.text[:500]
        except:
            pass
    
    # Check HTTP headers
    for header in ['X-Flag', 'Flag', 'X-CTF-Flag', 'X-Hint']:
        if header in r.headers:
            results[f'flag_in_header_{header}'] = r.headers[header]
    
    # Check cookies
    for cookie in r.cookies:
        flag_match = re.search(r'flag\{[^}]+\}', cookie.value)
        if flag_match:
            results['flag_in_cookie'] = flag_match.group()
    
    return results

# Quick crypto brute force
def try_common_crypto(ciphertext: str):
    """Try common crypto on ciphertext."""
    results = []
    
    # Caesar (all shifts)
    for shift in range(1, 26):
        decoded = caesar(ciphertext, -shift)
        if 'flag' in decoded.lower() or 'ctf' in decoded.lower():
            results.append(('caesar', shift, decoded))
    
    # Base64
    try:
        decoded = base64.b64decode(ciphertext)
        if b'flag' in decoded.lower() or b'ctf' in decoded.lower():
            results.append(('base64', 0, decoded))
    except:
        pass
    
    # ROT13
    decoded = caesar(ciphertext, 13)
    if 'flag' in decoded.lower():
        results.append(('rot13', 13, decoded))
    
    return results
```

---
