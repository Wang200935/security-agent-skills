---
name: network-device-recon
description: Recon local network devices — scan ports, identify NAS/router type, list
  SMB/AFP/NFS shares, mount file shares.
version: 1.0.0
license: MIT
metadata:
  hermes:
    origin: import
tags:
- osint
- recon
- information-gathering
- network
- device
related_skills: []
---

# Network Device Recon & NAS Connection

Use when the user provides a local IP address (e.g., 192.168.x.x, 10.x.x.x) and asks to connect to, explore, or identify a device on their network. Covers NAS devices (Synology, QNAP, ASUSTOR, etc.), routers, and general servers.

## Trigger conditions
- User mentions a local IP address and asks to "connect" or "access" it
- User asks "what's running on 192.168.x.x" or "scan this NAS"
- User wants to mount a network share from a local device
- User asks to list/discover all devices on the local network (no specific IP given) → see Phase 0

## Workflow

### Phase 0: Subnet-wide device discovery (when no specific IP given)
When the user asks to discover all devices on the network without providing an IP:
```bash
# 1. Find the local subnet
ifconfig | grep -E 'inet (10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' | head -1
# Example subnet: 192.168.68.0/24 → sweep 192.168.68.1-254

# 2. Fast parallel ping sweep (must use terminal(background=true) due to &)
for i in $(seq 1 254); do
  (ping -c 1 -W 1 $SUBNET.$i >/dev/null 2>&1 && echo "ALIVE:$SUBNET.$i") &
done; wait; echo "SCAN_COMPLETE"
```
This takes ~10-30 seconds. Filter for ALIVE lines to get the device list.

**After discovering alive IPs**, proceed to Phase 1 for each device. Run a single background bash script in `terminal(background=true)` with the full port scan loop — it's the fastest approach. For targeted follow-up on a few interesting IPs, direct `terminal()` calls work fine.

### Phase 1: Connectivity check
```bash
ping -c 3 -W 2 <IP>
```
If ping fails → device is offline or unreachable. Stop and report.

### Phase 2: Port discovery (no nmap required)
Use `/dev/tcp` for port scanning (works on macOS and Linux without extra tools):
```bash
for port in 21 22 23 25 53 80 110 111 135 139 143 161 443 445 515 548 554 631 873 993 995 1080 1115 1433 1521 1723 2049 3128 3260 3306 3389 4443 5000 5001 5432 5900 5985 5986 6379 7000 7001 8000 8001 8008 8009 8080 8081 8443 8888 9000 9080 9090 9100 9200 9300 9443 9998 9999 10000 27017; do
  (echo >/dev/tcp/$IP/$port) 2>/dev/null && echo "OPEN:$port"
done
```
This takes ~60-120 seconds. Warn the user it'll take a moment.

Key port classifications:
- **Router/gateway**: 53 (DNS), 80, 443
- **AirPlay/AirTunes**: 7000 (also check 80 for device info)
- **Google Cast/Home**: 8008, 8009, 8443
- **Printer**: 515 (LPR), 631 (IPP), 9100 (JetDirect raw). Port 80 + 631 + 9100 together is a strong printer signal. Note: MAC OUI can mislead (c8:94:02 = HP/Aruba per OUI, but actual device may be Brother — trust the web UI `<title>` over MAC vendor.)
- **Smart TV / set-top box**: 8008, 8009, 8443 (Google Cast); 554 (RTSP); 9080 (TV HTTP); 9998/9999 (diagnostics/TV control)
- **NAS admin UIs**: 5000/5001 (Synology), 8000/8001 (ASUSTOR), 8080/8443 (QNAP)
- **NAS storage**: 445 (SMB), 548 (AFP), 111/2049 (NFS), 3260 (iSCSI). Having 445+548+2049+3260 open together strongly indicates a NAS.

### Phase 2.5: MAC vendor identification
After port discovery, identify devices by MAC address:
```bash
arp -a 2>/dev/null | grep -v "(incomplete)"
```
Cross-reference MAC OUI prefixes against known vendors (see `references/mac-vendors.md`). Common prefixes:
- `3c:52:a1` → TP-Link/Askey (routers, mesh nodes)
- `ac:bf:71`, `14:98:77`, `84:a9:38` → Apple
- `d8:3a:dd` → Raspberry Pi Trading Ltd
- `10:2b:41` → Google (Nest, Home, Chromecast)
- `c8:94:02` → HP/Aruba (printers, switches)

### Phase 3: Service identification
For each open port, probe with curl to identify the service:
```bash
# HTTP ports — get page content
curl -sk --connect-timeout 3 http://$IP:$port 2>&1 | head -20

# HTTPS ports — same but check for redirects
curl -sk --connect-timeout 3 -o /dev/null -w "HTTP:%{http_code} Redirect:%{redirect_url}" https://$IP:$port
```

Look for vendor fingerprints:
- **TP-Link router**: redirects to `/webpages/index.html`, meta viewport tag
- **ASUSTOR**: Copyright comment "Asustor Inc.", page title "Ready to Serve!", `var WEBMAN = 'ADM'`
- **Synology**: `/webman/index.cgi`, DSM branding
- **QNAP**: `/cgi-bin/`, QTS branding
- **AirPlay device**: port 7000 returns `Server: AirTunes/xxx.xx` header; `/info` returns a binary plist with model/firmware/manufacturer. Best discovered via `pyatv scan`, not port probing.
- **Brother printer**: web UI on port 80, title contains model name (e.g., `Brother MFC-J4340DW`). Standard printer ports 515/631/9100. JetDirect port 9100 accepts raw PJL commands but **Brother inkjets do NOT support PostScript** — use PJL commands or plain text for test pages, not PostScript. MAC OUI `c8:94:02` (HP/Aruba) is misleading for Brother devices.
- **Samsung TV**: discovered by `pyatv scan`, name format `Samsung QN95BA 65`. May have MAC OUI `10:2b:41` (Google) if it has built-in Chromecast hardware. AirPlay pairing is Mandatory.
- **Google Cast device**: ports 8008, 8009, 8443 open; `/setup/eureka_info` returns JSON.

### Phase 3.5: Protocol-specific probes
For services that don't respond to plain HTTP:

See `references/airplay-pyatv-streaming.md` for detailed AirPlay/pyatv streaming instructions, failure modes, and real-device examples.

**`pyatv` — the best discovery tool for media devices (use FIRST when available):**
```bash
pip3 install pyatv  # one-time install
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
atvremote scan
```
`pyatv scan` discovers Apple TVs, AirPlay speakers (Bose, Sonos, etc.), Samsung TVs, and other RAOP/AirPlay/Companion devices. It returns device name, model, MAC, AirPlay pairing requirements, and deep-sleep status. This is far more reliable than mDNS + RTSP probing for media devices. A MAC OUI of `10:2b:41` (Google) on a device found by pyatv is likely a Samsung TV that uses Google's MAC range for built-in Cast components — don't misclassify it as a Google Nest/Home.

**Manual protocol probes (fallback if pyatv unavailable):**
```bash
# AirPlay/AirTunes (port 7000) — RTSP OPTIONS probe
echo -e "OPTIONS * RTSP/1.0\r\nCSeq: 1\r\n\r\n" | nc -w 2 $IP 7000

# AirPlay device info (binary plist)
curl -sk --connect-timeout 3 http://$IP:7000/info 2>&1 | strings | head -20

# Google Cast (ports 8008/8009)
curl -sk --connect-timeout 3 http://$IP:8008/setup/eureka_info 2>&1 | head -20

# mDNS service discovery (macOS) — less reliable than pyatv, use as fallback
dns-sd -B _airplay._tcp local & sleep 3 && kill %1
dns-sd -B _googlecast._tcp local & sleep 3 && kill %1
dns-sd -B _printer._tcp local & sleep 3 && kill %1
dns-sd -B _ipp._tcp local & sleep 3 && kill %1
dns-sd -B _hap._tcp local & sleep 3 && kill %1  # HomeKit
# Note: dns-sd -B uses & for timeout; use terminal(background=true) or execute_code to wrap.
```

### Phase 4: Share enumeration (SMB/NFS/AFP)
```bash
# SMB — list shares (guest/anon)
smbutil view smb://$IP                    # macOS
smbutil view -g smb://$IP                 # macOS guest listing
smbclient -L //$IP -N                     # Linux

# NFS exports
showmount -e $IP

# AFP (macOS)
# Check if port 548 is open — share listing requires authentication
```

### Phase 5: Mounting (macOS)
```bash
# SMB guest mount
mount_smbfs -N "smb://$IP/ShareName" /path/to/mountpoint

# SMB with credentials
mount_smbfs "smb://user:pass@$IP/ShareName" /path/to/mountpoint

# AFP
mount_afp "afp://$IP/ShareName" /path/to/mountpoint
```

**macOS gotchas:**
- Use `mount_smbfs`, NOT `mount -t cifs` (that's Linux)
- The `-N` flag enables guest/anonymous access
- Password with special chars: URL-encode in the SMB URL or use `mount_smbfs` interactive mode (omit password from URL)
- Create mount point first: `mkdir -p /tmp/nas_mount`

### NAS vendor-specific notes

**ASUSTOR ADM:**
- See `references/asustor-nas-recon.md` for detailed recon notes from a real session.
- Admin UI default ports: 8000 (HTTP), 8001 (HTTPS) — may be firewalled
- Web server on 80/443 runs Apache, shows "Ready to Serve!" landing page
- Admin paths to try: `/portal/`, `/adm/`, `/webman/`
- SMB shares often listable without auth even if mount requires it. In one session, 19 shares were visible via guest listing.

**ASUSTOR + Jellyfin over Docker/Container Manager:**
- If the user reports a Jellyfin URL on the NAS is unreachable, first probe the expected Jellyfin ports: `8096` (HTTP), `8920` (HTTPS), plus any custom external port the user mentions (for example `28096`).
- If `80/443` are open but Jellyfin ports are closed, do not misdiagnose it as a network outage. On ASUSTOR this often means the NAS is up and Apache web server is serving the default "Ready to Serve!" page while the Jellyfin container itself is stopped or no longer publishing ports.
- With SMB credentials, inspect the `Docker` share directly: `mount_smbfs "//user:pass@IP/Docker" /tmp/nas_docker_inspect`. A common path is `Docker/Jellyfin/Config/config/network.xml`.
- `network.xml` reveals Jellyfin's intended listen ports even when the service is down. In one real case it contained `InternalHttpPort=8096`, `InternalHttpsPort=8920`, `PublicHttpPort=8096`, `PublicHttpsPort=8920` while all of those ports were closed externally.
- If the user mentions a non-default port like `28096` but `network.xml` only shows `8096/8920`, infer that `28096` was likely a Docker/Portainer published-port mapping rather than Jellyfin's internal port. If `28096` is now closed, the mapping may have been removed or the container may be stopped.
- Check for `Docker/Jellyfin/Config/log/log_*.log`. Repeated `Microsoft.AspNetCore.Server.Kestrel` heartbeat warnings indicate the app ran previously, so the problem is usually current container state / Docker startup / lost published-port mapping, not missing installation.
- On ASUSTOR, do a broader follow-up port sweep before claiming Jellyfin is the only media service. In one real case, `32400` was open and identified as Plex (`/identity` returned Plex XML) while Jellyfin ports were closed; `9001` was open and served UMS, not ADM. This distinguishes “Jellyfin down” from “all Docker/media services down.”
- If SMB access works but shell access is missing, try FTP as a second authenticated probe. FTP listing can confirm whether `Docker/Jellyfin`, `PortainerCE`, `PortainerCE_CN`, and `User Homes` actually exist even when web admin is unreachable.
- Do not assume NAS file credentials also work for SSH. In one real case the same username/password worked for SMB and FTP, but SSH kept re-prompting for the password and never granted a shell. Treat this as “need higher-privilege or SSH-enabled account,” not as proof the password is wrong everywhere.
- Recommended user-facing conclusion for this pattern: NAS reachable, Jellyfin installed before, but Jellyfin is not currently listening. Next checks belong in ADM / Docker Engine / Container Manager / Portainer: verify Docker is running, Jellyfin container is `Running`, and published ports still map as expected (for example `8096:8096`, `8920:8920`, or custom `28096:8096`). If you do not have shell/admin credentials, state clearly that the remaining blocker is lack of control-plane access rather than uncertainty about root cause.

**Synology DSM:**
- Admin UI: port 5000 (HTTP), 5001 (HTTPS)
- SMB shares require auth for both listing and mounting

**QNAP QTS:**
- Admin UI: port 8080 (HTTP), 8443 (HTTPS)
- SMB shares require auth for both listing and mounting

## Pitfalls
- **`execute_code` sandbox has NO network access.** Pings, curls, nc, and `/dev/tcp` all fail silently inside `execute_code` Python. All network operations must use native `terminal()` calls directly. When orchestrating multi-IP scans, DO NOT use `execute_code` to loop over `terminal()` calls — use a single background bash script in `terminal(background=true)` instead. The Phase 0 note about using `execute_code` to orchestrate is WRONG; use a background bash script with `&` inside `terminal(background=true)`.
- **ICMP-only sweeps (ping) miss many devices.** Windows blocks ICMP by default. Some NAS/printers drop pings when idle. After an ICMP sweep, always do a port-based follow-up scan (port 445 for Windows/SMB, 9100 for printers, 7000 for AirPlay) on the full subnet to catch stealthy devices. Also re-read the ARP table after sweeps — `arp -a | grep -v incomplete` may show MACs for devices that responded to background pings but whose ALIVE line was lost.
- **`/dev/tcp` sequential port scanning is very slow** — ~3 seconds per closed port. For 50 ports × 15 IPs = ~38 minutes. Warn the user and run it in `terminal(background=true)`. For large subnets, prefer `pyatv scan` (media devices) + targeted port checks on interesting IPs rather than full port scans on every IP.
- **Bose AirPlay devices in Deep Sleep block streaming** even when `pyatv` reports `Pairing: NotNeeded`. The RTSP connection drops during metadata exchange. The device must be woken first (Bose app, physical button, or playing something from an already-paired device). `pyatv`'s `Deep Sleep: True` flag is the indicator.
- **AirPlay `/info` endpoint returns a binary plist** — pipe through `strings` for readable output, don't expect JSON/XML.
- **MAC OUI vendors can be misleading.** `c8:94:02` maps to HP/Aruba in the OUI database but the actual device may be a Brother printer. `10:2b:41` maps to Google but the device may be a Samsung TV with built-in Cast. Always verify with HTTP titles, `pyatv scan` output, and protocol responses — don't rely on MAC OUI alone for final classification.
- Browser navigation to self-signed HTTPS sites fails with `ERR_CERT_AUTHORITY_INVALID` — use curl with `-k` flag instead
- `mount -t cifs` does NOT work on macOS; use `mount_smbfs`
- ASUSTOR ADM ports 8000/8001 may be closed if admin UI is configured to only listen on certain interfaces
- SMB guest share listing (smbutil) may succeed even when mount requires auth. ASUSTOR NAS shares are often fully guest-listable (all 19+ shares visible) without any authentication.
