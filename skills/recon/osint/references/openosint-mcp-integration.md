# OpenOSINT MCP Server + OSINT-Framework Integration

## OpenOSINT MCP Server (19 tools)

Configure in Hermes `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  openosint:
    command: "python"
    args: ["/absolute/path/to/openosint/mcp_server.py"]
    env:
      ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"
      HIBP_API_KEY: "${HIBP_API_KEY}"
      SHODAN_API_KEY: "${SHODAN_API_KEY}"
      VIRUSTOTAL_API_KEY: "${VIRUSTOTAL_API_KEY}"
```

### Exposed MCP Tools (19)

| Tool | Description | Required Env |
|------|-------------|--------------|
| `search_email` | holehe — email → registered services | - |
| `search_username` | sherlock — username → 300+ platforms | - |
| `search_breach` | HaveIBeenPwned v3 — email breach check | `HIBP_API_KEY` |
| `search_whois` | python-whois — domain registration info | - |
| `search_ip` | ipinfo.io — IP geolocation/ASN | `IPINFO_TOKEN` (optional) |
| `search_domain` | sublist3r — subdomain enumeration | - |
| `generate_dorks` | 12 targeted Google dork URLs | - |
| `search_paste` | psbdmp.ws — pastebin dumps search | - |
| `search_phone` | phoneinfoga — phone carrier/geo | - |
| `search_shodan` | Shodan host/banner search | `SHODAN_API_KEY` |
| `search_virustotal` | VirusTotal 70+ engine scan | `VIRUSTOTAL_API_KEY` |
| `search_censys` | Censys internet-wide scan | `CENSYS_API_ID` + `CENSYS_SECRET` |
| `search_ip2location` | IP2Location enhanced (VPN/Proxy/Tor) | `IP2LOCATION_API_KEY` |
| `search_abuseipdb` | AbuseIPDB reputation score | `ABUSEIPDB_API_KEY` |
| `search_github` | GitHub profile/repos/commits | `GITHUB_TOKEN` (optional) |
| `search_dns` | dnspython — full DNS + SPF/DMARC/DKIM | - |
| `search_dorks_live` | Bright Data SERP — live Google results | `BRIGHTDATA_API_KEY` + zones |
| `scrape_url` | Bright Data Web Unlocker — clean markdown | `BRIGHTDATA_API_KEY` + zone |
| `search_footprint` | Entity-aware Google queries + correlation graph | `BRIGHTDATA_API_KEY` + zone |
| `investigate_multi` | Parallel multi-target investigation | `ANTHROPIC_API_KEY` |

## OSINT-Framework Resource Catalog (1100+ tools)

### Top Categories

| Category | Tools | Description |
|----------|-------|-------------|
| Domain Name | 146 | WHOIS, subdomains, certificates, passive DNS |
| Images / Videos / Docs | 94 | Reverse image, EXIF, satellite, forensics |
| Search Engines | 77 | Google, Bing, Yandex, specialized engines |
| Social Networks | 70 | Platform-specific OSINT tools |
| IP & MAC Address | 56 | Geolocation, Shodan, Censys, abuse DBs |
| Public Records | 49 | Court, business, government records |
| Blockchain & Cryptocurrency | 33 | Explorers, wallet clustering, AML |
| OpSec | 47 | Anonymity, VPN, Tor, browser fingerprinting |
| Tools (Automation) | 36 | SpiderFoot, Recon-ng, DataSploit, Photon |

## Unified Workflows

### Email Investigation Pipeline
```
search_email → search_breach → search_paste → generate_dorks → search_dorks_live
```

### Domain Reconnaissance Pipeline
```
search_whois → search_domain → search_dns → search_shodan → search_censys → search_footprint
```

### Username / Identity Investigation
```
search_username → search_github → search_paste → generate_dorks
```

### IP Intelligence
```
search_ip → search_shodan → search_censys → search_virustotal → search_abuseipdb → search_ip2location
```

## API Keys Required

```bash
ANTHROPIC_API_KEY=sk-ant-...
HIBP_API_KEY=...              # HaveIBeenPwned breach data
SHODAN_API_KEY=...            # Shodan internet scanning
VIRUSTOTAL_API_KEY=...        # VirusTotal malware scanning
IP2LOCATION_API_KEY=...       # IP2Location VPN/Proxy/Tor detection
CENSYS_API_ID=...             # Censys internet intelligence
CENSYS_SECRET=...
ABUSEIPDB_API_KEY=...         # AbuseIPDB IP reputation
GITHUB_TOKEN=ghp_...          # GitHub API (5000 req/hr vs 60)
BRIGHTDATA_API_KEY=...        # Bright Data SERP/Web Unlocker
```

## References

- OpenOSINT Repo: https://github.com/OpenOSINT/OpenOSINT
- OSINT-Framework: https://osintframework.com
- MCP Spec: https://modelcontextprotocol.io
