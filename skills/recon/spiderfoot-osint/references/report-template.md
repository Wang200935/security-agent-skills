# SpiderFoot Scan Report

## Target

- **Seed:** `{TARGET}`
- **Seed type:** {email|domain|username|phone|ip|bitcoin}
- **Scan use case:** {passive|footprint|investigate|all}
- **Scan timestamp:** {ISO 8601}
- **Total events:** {N}

## Summary — Top Findings

### Breaches & Leaks
| Breach | Date | Data leaked |
|---|---|---|
| {breach_name} | {date} | {fields} |

### Linked Accounts
| Platform | Username | URL | Confidence |
|---|---|---|---|
| {platform} | {username} | {url} | High/Medium/Low |

### Identity
| Field | Value | Source |
|---|---|---|
| Real name | {name} | {module} |
| Phone | {phone} | {module} |
| Location | {geo} | {module} |
| Photo URL | {url} | {module} |

### Credentials
| Hash type | Value | Source breach |
|---|---|---|

(only include if breach modules returned data; never store plaintext passwords in a cloud-synced file)

### Domain / Infrastructure
| Domain | A | MX | NS | Tags |
|---|---|---|---|---|

## Entity Graph

```
                  ┌──────────────────────────┐
                  │  {TARGET} ({seed_type})  │
                  └────────────┬─────────────┘
                               │
        ┌───────────┬─────────┼───────────┬───────────┐
        ▼           ▼         ▼           ▼           ▼
   breach_1    account_1  account_2   domain_1    phone_1
   ─ pylab     ─ github   ─ reddit    ─ A=1.2.3.4
   ─ hibp      ─ twitter  ─ twitch    ─ MX=...
```

(export full GEXF from HX2 for interactive graph view)

## Methodology Notes

- SpiderFoot use case: {passive|footprint|investigate|all}
- Fallback pipeline: {yes/no} → file `fallback_{ts}/`
- Cross-validation sources: {aliens-eye, maigret, h8mail, holehe, ...}
- Confidence scoring: High (3+ sources agree), Medium (1-2 sources), Low (inferred)

## OPSEC

- Scan ran via: {direct | Tor.SOCKS5}
- User-agent: {SpiderFoot default | custom}
- Time on target: {N} seconds

## Limitations / Unknowns

- {e.g., "HIBP key not configured — breach list may be incomplete"}
- {e.g., "Email local-part as username is a guess — confirm with aliens-eye"}
- {e.g., "Chinese real-name not searched — use cjk-real-person playbook"}

## Appendix — Raw Files

- `spiderfoot_{seed}_{ts}.json` — raw SpiderFoot output
- `spiderfoot_{seed}_{ts}.entities.json` — normalized
- `fallback_{seed}_{ts}/` — fallback pipeline results
- `merged_{seed}_{ts}.json` — combined entity graph (if merge ran)

## Legal Notice

This report compiles publicly available OSINT data under authorized investigation
scope {reference authorization}. Storage of personal data subject to applicable
privacy law (GDPR / CCPA / PIPL / 等). Use exclusively for {purpose}.
