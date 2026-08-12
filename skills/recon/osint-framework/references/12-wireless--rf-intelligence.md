# 12. Wireless & RF Intelligence

```python
WIRELESS_OSINT = {
    'wigle': 'WiFi network geolocation database — 1B+ networks',
    'opensky-network': 'ADS-B flight tracking (free API)',
    'flightradar24': 'Commercial flight tracking',
    'marinetraffic': 'AIS vessel tracking',
    'shodan_iot': 'WiFi cameras, SCADA, industrial control',
    'cellmapper': 'Cell tower location mapping',
    'opencellid': 'Cell tower database API',
    'nperf': 'Network coverage maps',
}

# ADS-B Flight Intelligence
"""
curl -s "https://opensky-network.org/api/states/all" | jq '.states[] | select(.[1] | startswith("N"))'
"""
```

---
