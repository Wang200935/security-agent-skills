# 8. Phone Number Intelligence

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
