# 4. Email Intelligence

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
