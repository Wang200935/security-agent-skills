# SpiderFoot API Keys — Full Reference

SpiderFoot has 231 modules. ~120 work without keys (passive DNS / WHOIS / crt.sh / public SOCMINT). The rest need API keys configured in `~/tools/spiderfoot/spiderfoot.cfg`.

## Configuration File

```ini
# ~/tools/spiderfoot/spiderfoot.cfg
[main]
# Most valuable keys — add what you have. Missing = module silently skipped.

# === Breach / Credential Intel ===
haveibeenpwned_api_key = YOUR_HIBP_KEY          # https://haveibeenpwned.com/API/Key
dehashed_api_key = YOUR_DH_KEY                   # https://dehashed.com (paid)
dehashed_email = your@email.com                  # DeHashed needs email + key
citadel_api_key = YOUR_LEAKLOOKUP_KEY            # https://leak-lookup.com

# === Internet / Asset Discovery ===
shodan_api_key = YOUR_SHODAN_KEY                # https://shodan.io (free tier OK)
binaryedge_api_key = YOUR_BE_KEY                # https://binaryedge.io (paid)
censys_api_id = YOUR_CENSYS_ID                  # https://censys.io
censys_api_secret = YOUR_CENSYS_SECRET

# === Malware / Threat Intel ===
virustotal_api_key = YOUR_VT_KEY                # https://virustotal.com (free tier OK)
abuseipdb_api_key = YOUR_ABUSEIPDB_KEY          # https://abuseipdb.com (free)
greynoise_api_key = YOUR_GN_KEY                 # https://greynoise.io
pulsedive_api_key = YOUR_PD_KEY                 # https://pulsedive.com
alienvault_api_key = YOUR_OTX_KEY               # AlienVault OTX

# === People / Email Enrichment ===
emailrep_api_key = YOUR_EMAILREP_KEY            # https://emailrep.io
hunter_api_key = YOUR_HUNTER_KEY                # https://hunter.io (free: 25/mo)
fullcontact_api_key = YOUR_FC_KEY               # https://fullcontact.com (paid)
seon_api_key = YOUR_SEON_KEY                    # https://seon.io (paid)
c99_api_key = YOUR_C99_KEY                      # https://c99.nl (paid)

# === DNS / Subdomain ===
securitytrails_api_key = YOUR_ST_KEY            # https://securitytrails.com (free: 50/mo)
passivedns_api_key = YOUR_PD_KEY                # https://passivedns.com (paid)
dnsdb_api_key = YOUR_DNSDB_KEY                 # https://dnsdb.info (paid)

# === Auxiliary ===
github_api_key = YOUR_GITHUB_TOKEN              # For sfp_github (rate-limit bump)
gitlab_api_key = YOUR_GITLAB_TOKEN
slack_api_token = YOUR_SLACK_TOKEN             # For sfp_slack (very limited)
builtwith_api_key = YOUR_BUILTWITH_KEY         # https://builtwith.com (paid)

# === Network Settings ===
socks_proxy =                                   # socks5://127.0.0.1:9050  for Tor routing
max_threads = 10
```

## How to Get Each Key

### Free Tier (no payment)

| Key | How | Limits |
|---|---|---|
| HaveIBeenPwned | https://haveibeenpwned.com/API/Key (verification email) | 10 req/min via API |
| Shodan | Sign up at https://shodan.io → Account → API Key | 100 query credits/mo |
| VirusTotal | https://www.virustotal.com/gui/my-apikey | 4 req/min, 500/day |
| AbuseIPDB | https://abuseipdb.com/account/api | 1000 checks/day |
| Hunter.io | https://hunter.io → API | 25 searches/mo (free) |
| SecurityTrails | https://securitytrails.com/app/account | 50 queries/mo (free) |
| AlienVault OTX | https://otx.alienvault.com/api | Free with registration |
| GitHub | `gh auth token` or personal access token | 5000 req/hr (auth) vs 60 (anon) |
| Leak-Lookup | https://leak-lookup.com | Free for limited searches |
| EmailRep | https://emailrep.io | Free with rate limit (key increases throughput) |

### Paid Only (covered only if you have a budget)

- DeHashed ($35/mo personal — needed for full breach credential dump)
- BinaryEdge ($200/mo)
- FullContact ($199/mo Lite)
- SEON ($250+/mo)
- C99 ($9/mo basic)
- SecurityTrails Pro ($50/mo)
- DNSDB ($99/mo personal)

## Module-to-Key Mapping (Top 25 by Value)

| Module | Key Required | What It Returns |
|---|---|---|
| sfp_haveibeenpwned | haveibeenpwned_api_key | Email→breach names |
| sfp_dehashed | dehashed_api_key + dehashed_email | Email→cleartext password, hash, name, phone |
| sfp_citadel | citadel_api_key | Breach DB search (alternatives to HIBP) |
| sfp_shodan | shodan_api_key | Internet asset inventory |
| sfp_virustotal | virustotal_api_key | File/URL/domain reputation + AV verdicts |
| sfp_binaryedge | binaryedge_api_key | IP vulnerability + breach dumps |
| sfp_abuseipdb | abuseipdb_api_key | IP abuse confidence score |
| sfp_greynoise | greynoise_api_key | IP noise / scanner classification |
| sfp_pulsedive | pulsedive_api_key | Threat intel indicators |
| sfp_alienvault | alienvault_api_key | OTX pulse IOCs |
| sfp_emailrep | emailrep_api_key | Email reputation + risk score |
| sfp_hunter | hunter_api_key | Email pattern + domain email list |
| sfp_fullcontact | fullcontact_api_key | Person enrichment (name/job/photos) |
| sfp_seon | seon_api_key | Email/IP/phone intelligence |
| sfp_c99 | c99_api_key | Phone/geo/proxy lookup |
| sfp_builtwith | builtwith_api_key | Web tech stack of domain |
| sfp_securitytrails | securitytrails_api_key | Historical DNS / passive DNS |
| sfp_dnsdb | dnsdb_api_key | Massive passive DNS DB |
| sfp_censys | censys_api_id + censys_api_secret | Hosted assets |

## OPSEC Considerations

- **Every module API call logs your IP** at the provider. Route via SOCKS:
  ```
  socks_proxy = socks5://127.0.0.1:9050
  ```
  But NOT every module honors socks_proxy — some bypass it.
- **Never commit spiderfoot.cfg with keys**. Add to .gitignore (already default in SpiderFoot).
- **Use an OPSEC account email for DeHashed** — DeHashed can correlate the email you use with what you search.
- **HIBP API key is per-account, tied to your email** — block usage limits if shared.
- **Shodan/Hunter free tiers are fine for security-research use** — ToS forbids commercial resale of data.
