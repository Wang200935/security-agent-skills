# 9. Financial & Corporate Intelligence

```python
CORPORATE_SOURCES = {
    'opencorporates': 'Global company registry — free API',
    'SEC EDGAR': 'US public company filings (10-K, 10-Q, 8-K, S-1)',
    'Companies House': 'UK company registry',
    'ICIJ Offshore Leaks': 'Offshore entities database',
    'OpenOwnership': 'Beneficial ownership register',
    'Dun & Bradstreet': 'Business credit reports (paid)',
    'Clearbit': 'Company enrichment API',
    'Crunchbase': 'Startup funding, investors, employees',
    'AngelList': 'Startup jobs and investors',
    'PitchBook': 'Private company data (paid)',
}

# SEC EDGAR search
# site:sec.gov "Target Corp" filetype:10-K

# OpenCorporates API
"""
curl -s "https://api.opencorporates.com/v0.4/companies/search?q=tesla" | jq .
"""
```

---
