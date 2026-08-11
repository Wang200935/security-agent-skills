# MAC OUI → Vendor Quick Reference

Used in Phase 2.5 to identify devices from their MAC addresses. First 3 octets (OUI) are the key.

## Consumer Electronics
| OUI | Vendor | Typical Devices |
|---|---|---|
| `14:98:77` | Apple | Macs, MacBooks |
| `ac:bf:71` | Apple | iPhones, iPads, AirPlay speakers, HomePods |
| `84:a9:38` | Apple | AirPort, Apple TV, misc |
| `10:2b:41` | Google | Nest speakers, Google Home, Chromecast, Google WiFi |
| `d8:3a:dd` | Raspberry Pi Trading Ltd | Raspberry Pi 3/4/5 |
| `b8:27:eb` | Raspberry Pi | Raspberry Pi (older) |

## Networking
| OUI | Vendor | Typical Devices |
|---|---|---|
| `3c:52:a1` | TP-Link / Askey | Routers, mesh nodes, range extenders |

## NAS / Storage
| OUI | Vendor | Typical Devices |
|---|---|---|
| `78:72:64` | Asustor | ASUSTOR NAS (AS-series, Lockerstor, etc.) |

## Printers & Enterprise
| OUI | Vendor | Typical Devices |
|---|---|---|
| `c8:94:02` | HP / Aruba | Printers, Aruba switches/APs |

## How to use
```bash
# Extract MACs from ARP table (filter out incomplete entries)
arp -a 2>/dev/null | grep -v '(incomplete)' | grep -oE '([0-9a-f]{1,2}:){5}[0-9a-f]{1,2}'
# Then match first 8 chars (e.g. "ac:bf:71") against the table above
```

## ⚠️ OUI Traps (verified misleading cases)
| OUI | OUI Says | Actually Was |
|---|---|---|
| `10:2b:41` | Google | Samsung QN95BA TV (has built-in Chromecast using Google MAC) |
| `c8:94:02` | HP/Aruba | Brother MFC-J4340DW printer |
| `ac:bf:71` | Apple (iPhone/iPad) | Bose Smart Soundbar 900 (uses Apple AirPlay chipset) |

**Rule**: MAC OUI is a first-pass hint, not a final classification. Always verify with HTTP titles, `pyatv scan`, and protocol responses.
