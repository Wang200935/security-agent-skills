---
name: local-network-recon
description: Comprehensive local network device discovery, identification, and interaction.
  Use when the user asks to find/scan/list/control devices on their local network.
  Covers multi-pass scanning, port-based identification, printer/NAS/smart-home control
  patterns, and common pitfalls.
version: 1.0.0
license: MIT
metadata:
  hermes_origin: import
tags:
- osint
- recon
- information-gathering
- local
- network
related_skills: []
---

# Local Network Reconnaissance & Device Control

Use when the user asks to find, list, scan, identify, or control devices on their local network. This skill consolidates lessons from scanning 192.168.68.0/24 (11 devices found: router, NAS, 2×Pi, 2×mesh nodes, printer, soundbar, smart TV, Mac, Apple device).

## Trigger Conditions
- "scan my network" / "list all devices" / "what's on my network"
- "find my NAS" / "find my printer" / "find smart home devices"
- "can you control X on my network"
- "打遊戲延遲高" / "網路很慢" / "lag" / game latency diagnosis (see `references/game-latency-diagnosis.md`)
- "刪掉 Tailscale" / "停掉 WireGuard" / VPN removal on Windows (see `references/windows-vpn-removal.md`)
- "降低延遲" / "optimize network for gaming" / "調網卡" / NIC tuning on Windows (see `references/windows-nic-optimization.md`)
- Any local network discovery task

---

## Phase 1: Subnet Discovery

First, determine the local subnet:

```bash
ifconfig | grep -E 'inet (10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' | head -5
```

Extract the IP and netmask. For /24 subnets, scan range is x.x.x.1–254.

---

## Phase 2: Multi-Pass Alive Discovery (CRITICAL)

**A single ping sweep is NOT enough.** Devices may be temporarily unresponsive, block ICMP, or wake/sleep between sweeps.

### Pass 1: ARP Table (fast, no network traffic)
```bash
arp -a | grep -v incomplete | grep "192.168" | sort -t. -k4 -n
```
This catches devices the machine has recently communicated with. Filter out `(incomplete)` entries and multicast/broadcast addresses (224.x, 239.x, .255).

### Pass 2: Ping Sweep (background mode required)
```bash
for i in $(seq 1 254); do
  ping -c 1 -W 1 192.168.x.$i >/dev/null 2>&1 && echo "ALIVE:192.168.x.$i"
done
```
**Must use `terminal(background=true)`** — foreground rejects `&` backgrounding. The sweep takes 30–60 seconds.

### Pass 3+: Repeat sweeps later
Devices join/leave the network. After finding new MACs in the ARP table, re-scan. In one session, we found .104 (NAS) only on the 3rd sweep.

### Merge results
Combine all passes into a unique IP list. The ARP table often reveals devices that ping misses (ICMP-blocking devices, transient DHCP leases).

---

## Phase 3: MAC Vendor Identification

Extract MACs from `arp -a` for all alive IPs. Use known OUI prefixes:

| OUI Prefix | Vendor | Common Device Types |
|---|---|---|
| `3c:52:a1` | TP-Link / Askey | Router, mesh nodes, extenders |
| `ac:bf:71` | Apple | Apple TV, HomePod, Mac, Bose (uses Apple chips) |
| `14:98:77` | Apple | Mac, MacBook, Mac mini |
| `84:a9:38` | Apple | iPhone, iPad, Apple Watch |
| `d8:3a:dd` | Raspberry Pi | Raspberry Pi (any model) |
| `10:2b:41` | Google | Google Nest/Home, Chromecast, **also Samsung TVs** |
| `78:72:64` | Asustor | Asustor NAS |
| `c8:94:02` | HP / Aruba | HP printers, Aruba APs, **also Brother printers** |

### ⚠️ MAC OUI Can Mislead
- **Samsung QN95BA TV** had MAC `10:2b:41` (Google OUI) — Samsung uses Google's chipset
- **Brother MFC-J4340DW printer** had MAC `c8:94:02` (HP OUI) — shared OUI pool
- **Bose Soundbar 900** had MAC `ac:bf:71` (Apple OUI) — uses Apple AirPlay chip

**Always verify with service probes, not just MAC.**

---

## Phase 4: Port Scanning

Use `/dev/tcp` in bash (no nmap needed, works on macOS):

```bash
for port in 22 53 80 135 139 443 445 515 548 554 631 873 1115 2049 3128 3260 3306 3389 5000 5001 5432 5900 5985 6379 7000 8000 8008 8009 8080 8081 8443 8888 9000 9080 9100 9200 9443 9999 10000 27017; do
  (echo >/dev/tcp/$IP/$port) 2>/dev/null && echo "OPEN:$port"
done
```

**Use `terminal(background=true)` for large batches.** Sequential /dev/tcp scans are slow (~2s per closed port).

### Critical: `execute_code` Has No Network Access
Do NOT run ping or port scans inside `execute_code` — its Python sandbox blocks raw sockets and ICMP. Use native `terminal()` tool directly.

---

## Phase 5: Device Identification by Port Signature

### NAS (Network Attached Storage)
**Signature ports:** 139, 445 (SMB), 548 (AFP), 2049 (NFS), 3260 (iSCSI)

Vendor-specific admin ports:
- **Synology:** 5000 (HTTP), 5001 (HTTPS)
- **QNAP:** 8080 (HTTP), 8443 (HTTPS)
- **Asustor:** 80, 443 (landing page: "Ready to Serve!")
- **TrueNAS/FreeNAS:** 80, 443

**SMB share enumeration (guest):**
```bash
smbutil view -g smb://$IP    # macOS guest listing
```

### Printer
**Signature ports:** 515 (LPR), 631 (IPP), 9100 (JetDirect)

**Identify model via IPP:**
```bash
# Check document-format-supported to know what formats work
ipptool -tv http://$IP:631/ipp/print get-printer-attributes.test
```

**Print via CUPS (recommended):**
```bash
lpadmin -p PrinterName -v ipp://$IP/ipp/print -E -m everywhere
lp -d PrinterName file.jpg
```

Common printer formats: `image/jpeg`, `image/urf`, `image/pwg-raster`, `application/octet-stream`. Most inkjets do NOT support PostScript.

### Smart TV / Streaming Device
**AirPlay discovery (best tool):**
```bash
pip3 install pyatv
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
atvremote scan
```
This reveals device name, model, AirPlay pairing status, and deep sleep state.

**Google Cast ports:** 8008, 8009, 8443
**DLNA/SSDP:** port 1900 (multicast, hard to query without proper tooling)

### Smart Speaker / Soundbar
AirPlay discovery via `pyatv` is most reliable. Direct RTSP probing:
```bash
printf "OPTIONS * RTSP/1.0\r\nCSeq: 1\r\n\r\n" | nc -w 2 $IP 7000
```
A successful response confirms AirPlay/RAOP capability.

### Router / Gateway
Typically `.1` on the subnet. Ports: 53 (DNS), 80, 443.
Admin panel URL often redirects (e.g., `/webpages/index.html` for TP-Link).

### Apple / macOS Host
A host exposing this combination is very likely a Mac or Apple-based host:
- `22` SSH (Remote Login)
- `445` SMB file sharing
- `5000` AirTunes / AirPlay audio receiver
- `5900` VNC / Screen Sharing

Strong fingerprint example:
```bash
curl -skI --connect-timeout 4 http://$IP:5000 | sed -n '1,12p'
```
If it returns `Server: AirTunes/...`, treat the host as Apple/macOS-class even if hostname discovery is missing. Do not misclassify it as a DNS appliance just because it was handed out as DNS by DHCP.

### IoT / Misc
- **Raspberry Pi:** SSH (22) + HTTP (80) + custom service ports
- **Mesh nodes:** No open ports, identified by MAC OUI + ARP only

---

## Phase 6: Interaction & Control

### Printer — ✅ Most Controllable
1. Query IPP for supported formats
2. Add to CUPS via `lpadmin`
3. Print images (JPEG is universally supported)
4. For test pages, generate BMP → convert to JPEG via `sips` (macOS built-in)

### AirPlay Streaming — ⚠️ Device-Dependent
```bash
atvremote --id $DEVICE_ID stream_file=/path/to/audio.wav
```

**Limitations:**
- **Deep Sleep:** Device unreachable until woken (Bose Soundbar 900 requires physical interaction or Bose Music app)
- **Pairing Mandatory:** Requires PIN shown on device screen (Samsung TV)
- **Pairing NotNeeded:** Direct streaming possible (Mac mini AirPlay receiver)

Generate test audio:
```python
python3 -c "
import struct, math
sr = 44100; dur = 3; freq = 440
samples = [struct.pack('<h', int(32767*0.5*math.sin(2*math.pi*freq*i/sr))) for i in range(int(sr*dur))]
# ... write WAV file ...
"
```

### NAS — SMB Shares
Guest enumeration via `smbutil view -g smb://$IP`. Mount with:
```bash
mount_smbfs -N "smb://$IP/ShareName" /path/to/mountpoint
```

### Raspberry Pi
SSH available if you have credentials. Web services on port 80/8000 can be probed with curl.

---

## Pitfalls & Lessons Learned

1. **Single ping sweep misses devices.** Always do 2+ sweeps at different times + check ARP table.

2. **MAC OUI is not definitive.** Samsung TV has Google MAC. Brother printer has HP MAC. Always verify with service probes.

3. **`execute_code` has no network access.** Ping/port scan must use native `terminal()`.

4. **Foreground terminal rejects `&`.** Use `terminal(background=true)` for parallel operations.

5. **Deep Sleep breaks AirPlay.** IoT speakers/soundbars may require physical wake-up. Check `atvremote scan` for `Deep Sleep: True`.

6. **PostScript is NOT universal.** Most inkjet printers don't support it. Check `document-format-supported` via IPP. JPEG is safest.

7. **`/dev/tcp` is slow for closed ports** (~2s each). Combine with background mode for bulk scanning, or target specific port ranges per device type.

8. **SMB enumeration is slow for unreachable hosts.** Use `smbutil` with individual IPs, not subnet-wide.

9. **mDNS/dns-sd often returns empty** on macOS when run non-interactively. Prefer `atvremote scan` for AirPlay, direct port probes for other services.

10. **Devices come and go on WiFi.** An 11-device network at 17:30 might have different devices at 18:00. Pi's (.108, .112) were offline in early sweeps, online later.

11. **An Apple/macOS host can masquerade as a mystery infrastructure box.** On this network, `192.168.68.105` looked at first like a dead DNS server, but later probing showed `22`, `445`, `5000`, and `5900` with `Server: AirTunes/950.6.1` on port 5000 — a strong Apple/macOS signature. If DHCP points clients at such a host for DNS, the failure is usually bad DHCP configuration or a retired experiment, not a Wi‑Fi problem.

12. **"Wi‑Fi connected but no internet" can be a broken DHCP-advertised DNS server, not a radio/link problem.** When some devices fail only on Wi‑Fi while others still work, inspect the live DHCP lease and resolver order before blaming APs or mesh backhaul:
   ```bash
   ipconfig getpacket en0 | sed -n '1,220p'   # shows router + domain_name_server from DHCP
   scutil --dns | sed -n '1,180p'             # shows effective resolver order
   dig +time=2 +tries=1 @<router_ip> www.google.com A
   dig +time=2 +tries=1 @<dhcp_dns_ip> www.google.com A
   arp -a | grep '(<dhcp_dns_ip>)'
   ```
   In one real case, the router at `192.168.68.1` handed out `192.168.68.105` as DNS, but direct queries to `.105` timed out and ARP stayed incomplete. Devices that relied only on DHCP DNS appeared to have "Wi‑Fi but no internet", while this Mac still worked because Tailscale installed a higher-priority supplemental resolver `100.100.100.100`. Fix path: change router DHCP DNS to a working resolver (router itself or public DNS) or restore the broken DNS host.

---

## Known Device Inventory (192.168.68.0/24)

Last scanned: 2026-05-02. 11 devices online, 2 Windows machines offline.

### Gateway / Router
| IP | MAC | Device | Ports |
|---|---|---|---|
| `192.168.68.1` | `3c:52:a1:f9:09:14` (TP-Link) | TP-Link Router | 53 (DNS), 80, 443 |

### Mesh Nodes
| IP | MAC | Device | Ports |
|---|---|---|---|
| `192.168.68.249` | `3c:52:a1:f9:0c:18` (TP-Link) | TP-Link Mesh Node #1 | — |
| `192.168.68.250` | `3c:52:a1:f9:09:1c` (TP-Link) | TP-Link Mesh Node #2 | — |

### NAS
| IP | MAC | Device | Ports |
|---|---|---|---|
| `192.168.68.104` | `78:72:64:40:0f:55` (Asustor) | Asustor NAS | 80, 139, 443, 445 (SMB), 548 (AFP), 631, 2049 (NFS), 3260 (iSCSI) |

**SMB shares (19, guest listable):** `Surveillance` `RD` `行政部` `Media` `財務部` `Web` `PM` `採購部` `Download` `Plex` `Music` `Comics` `Photos` `Video` `Public` `Docker` `Home` `User Homes` `IPC$`

Mount: `mount_smbfs -N "smb://192.168.68.104/ShareName" /path/to/mountpoint`

### Printers
| IP | MAC | Device | Ports |
|---|---|---|---|
| `192.168.68.103` | `c8:94:02:b2:a7:c9` (HP/Brother) | Brother MFC-J4340DW | 80, 515 (LPR), 631 (IPP), 9100 (JetDirect) |

- **Formats:** JPEG, URF, PWG-Raster, Brother-HBP, octet-stream. **NO PostScript.**
- **CUPS name:** `Brother-MFC-J4340DW` (added via `lpadmin -p Brother-MFC-J4340DW -v ipp://192.168.68.103/ipp/print -E -m everywhere`)
- **Print:** `lp -d Brother-MFC-J4340DW file.jpg`
- Ink levels visible via `curl http://192.168.68.103/home/status.html`
- Status: Ready. Non-Brother ink detected (M, C, Y). Page yields: M:1000, C:1200, Y:1200, BK:4800.

### Raspberry Pi
| IP | MAC | Device | Ports | Service |
|---|---|---|---|---|
| `192.168.68.108` | `d8:3a:dd:19:73:f3` | Raspberry Pi #1 | 22 (SSH), 80, 8000 | ScamGuard 可疑網址分析 |
| `192.168.68.112` | `d8:3a:dd:19:73:f4` | Raspberry Pi #2 | 22 (SSH), 80, 8000 | ScamGuard 可疑網址分析 |

### Smart TV
| IP | MAC | Device | Ports |
|---|---|---|---|
| `192.168.68.111` | `10:2b:41:b8:11:b6` (Google — misleading!) | Samsung QN95BA 65 | 7000 (AirPlay), 9999 |

- AirPlay pairing: **Mandatory** (requires PIN shown on TV screen)
- Deep Sleep: False
- Model: QBQ95

### Smart Speaker / Soundbar
| IP | MAC | Device | Ports |
|---|---|---|---|
| Dynamic | `ac:bf:71:59:3e:11` (Apple → Bose) | Bose Smart Soundbar 900「客廳」 | 7000 (AirPlay/RAOP) |

- AirPlay pairing: NotNeeded (RAOP)
- **Deep Sleep**: 閒置後進入；Bonjour 仍廣播但 AirPlay session 中斷；需實體鍵/Bose App/手機 AirPlay 喚醒
- WOL: 不可靠
- **已可程式控制**: `bose-ctl switch` 切換（需 Bose 已在 HAL）；`bose-ctl monitor` 監控 Bonjour 在線
- Bonjour: `_airplay._tcp` 和 `_raop._tcp`
- AirPlay UID: `00000000-0000-0000-0000-ACBF71593E11`
- 控制 skill: `bose-ctl`

### Mac
| IP | MAC | Device | Ports |
|---|---|---|---|
| `192.168.68.110` | `14:98:77:47:0f:3d` (Apple) | Mac mini「王池川的Mac mini」 | AirPlay receiver (7000), RAOP, Companion (49154) |

- AirPlay pairing: NotNeeded. Can receive streamed audio.
- Stream to self: `atvremote --id 9AD6C0F7EDAB stream_file=/tmp/audio.wav`

### Other Apple Devices / Hosts
| IP | MAC | Device | Notes |
|---|---|---|---|
| `192.168.68.100` | `84:a9:38:30:e1:57` (Apple) | Apple device (iPhone / iPad / Apple Watch) | Generic Apple client |
| `192.168.68.105` | `d4:57:63:c6:ee:90` (Apple) | Unknown Apple/macOS host | Open ports: 22, 88, 445, 5000, 5900. Port 5000 returns `Server: AirTunes/950.6.1`; likely Mac or Apple-based host. Was mistakenly advertised by DHCP as DNS and caused Wi‑Fi clients to appear offline. Root/1234 and admin/1234 were both rejected. |

### Offline / Updated (not found during original scan)
- **Windows gaming PC** — now confirmed at `192.168.68.112` (was listed as Raspberry Pi #2 in original scan; the IP was reassigned). SSH configured as `Host win` in `~/.ssh/config` (user: `ellis`). Runs Windows with OpenSSH Server. Ethernet (Realtek PCIe GbE) at 1 Gbps. Had Tailscale + WireGuard causing gaming latency (removed 2026-07-03). See `references/game-latency-diagnosis.md` and `references/windows-vpn-removal.md`.
- **1× Windows machine** — still offline/unknown

---

See also `references/dhcp-dns-wifi-no-internet.md` for the generic diagnostic pattern where DHCP-advertised DNS failure makes Wi‑Fi look broken even though routing/radio are fine.
See also `references/dhcp-dns-apple-host-105.md` for the concrete `.105` case where the advertised DNS target turned out to be an Apple/macOS-class host.
See also `references/game-latency-diagnosis.md` for the 5-layer game latency diagnosis protocol (WiFi signal → router hop → VPN interference → ISP path → DNS), including percentile-based jitter analysis and the WiFi retransmit detection technique.
See also `references/windows-vpn-removal.md` for step-by-step Tailscale complete uninstall + WireGuard disable via SSH on Windows.
See also `references/windows-nic-optimization.md` for Windows NIC + TCP/IP registry-level gaming optimization (Realtek EEE/Green/InterruptModeration off, TCP NoDelay/AckFrequency on) via SSH.

## Tool Prerequisites

Install these before scanning (one-time):
```bash
pip3 install pyatv        # AirPlay discovery & streaming
# CUPS is built into macOS
# ipptool is built into macOS (/usr/bin/ipptool)
# smbutil is built into macOS
```
