# OSINT (in CTF Context)

```python
OSINT_CHECKS = [
    'Google Image Search — reverse image search',
    'Shodan — find exposed services by banner',
    'WHOIS — domain registration details',
    'crt.sh — SSL certificate transparency logs',
    'Wayback Machine — historical versions of websites',
    'GitHub search — code commits, gists, comments',
    'EXIF data — GPS coordinates, camera info, timestamps',
    'Social media — Twitter, LinkedIn, Instagram, Reddit',
    'HaveIBeenPwned — email/password breach data',
    'Wigle.net — WiFi network geolocation',
]

# Google dorking for CTF OSINT
CTF_DORKS = {
    'github_flag': 'site:github.com "flag{" ',
    'pastebin': 'site:pastebin.com "ctf{" ',
    'twitter': 'from:@target_user since:2024-01-01',
    'linkedin': 'site:linkedin.com/in/ "ctf" "target"',
}
```

---
