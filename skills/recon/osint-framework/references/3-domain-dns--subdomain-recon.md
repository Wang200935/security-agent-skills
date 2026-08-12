# 3. Domain, DNS & Subdomain Recon

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
