# Home Network Game Latency Diagnosis

Session-proven technique for diagnosing high game latency on a home network where the user games on a Windows PC and the Hermes agent SSHes in from a Mac.

## Trigger

- User reports "打遊戲延遲高" / "lag" / "ping too high" while gaming on a different machine than the Mac
- User asks "為什麼網路這麼慢" in a gaming context
- Windows machine has SSH enabled (see session 20260630 for setup)

## Prerequisites

- SSH to Windows machine configured in `~/.ssh/config` (e.g. `Host win → 192.168.68.x`)
- Windows machine must have OpenSSH Server running

## Diagnosis Protocol (5 layers)

### Layer 1: WiFi Signal Quality (Mac side)

```bash
sudo wdutil info 2>/dev/null | grep -E "RSSI|Noise|Tx Rate|CCA|Channel|PHY"
```

Key metrics and interpretation:

| Metric | Excellent | Acceptable | Bad |
|---|---|---|---|
| RSSI | >-50 dBm | -50 to -65 | <-70 |
| Noise | <-90 dBm | -85 to -90 | >-80 |
| SNR (RSSI - Noise) | >40 dB | 25-40 | <20 |
| CCA (channel busy) | <10% | 10-30% | >50% |
| Tx Rate | >500 Mbps | 200-500 | <100 |

**Signal can be excellent but jitter still exists** — the WiFi link layer retransmits packets even with good signal, causing periodic 50-135ms spikes. This is the #1 cause of gaming lag on WiFi.

### Layer 2: Router Hop Latency (the critical test)

```bash
# From the gaming machine:
ssh win "ping -n 50 192.168.68.1"

# From the Mac (for comparison):
ping -c 50 -i 0.2 192.168.68.1
```

**Interpretation**:

| Router ping | Diagnosis |
|---|---|
| <1ms consistent | ✅ Ethernet, perfect |
| 1-3ms consistent | ✅ Good WiFi |
| 5-10ms with occasional 50ms+ spikes | ⚠️ WiFi retransmit (see Layer 3) |
| 10-50ms avg with 100ms+ spikes | 🔴 VPN tunnel interference or WiFi congestion |
| 50ms+ avg | 🔴 Severe WiFi problem or router overloaded |

**Percentile analysis** (more useful than avg for gaming):

```bash
# Sort pings and look at p90, p99 (games care about worst-case, not average)
ping -c 30 -i 0.1 192.168.68.1 2>&1 | grep "time=" | sed 's/.*time=//; s/ ms//' | sort -n | awk '
{
  a[NR]=$1; sum+=$1;
}
END {
  n=NR;
  printf "min=%.1f  p50=%.1f  p90=%.1f  p99=%.1f  max=%.1f  avg=%.1f\n", a[1], a[int(n*0.5)], a[int(n*0.9)], a[int(n*0.99)], a[n], sum/n
}'
```

**Games care about p99, not avg.** If p99 > 100ms to your own router, you will feel lag.

### Layer 3: VPN/Tunnel Interference (the #1 hidden cause)

Check for VPN software running on the gaming machine:

```bash
ssh win "powershell -Command \"Get-Process | Where-Object { \$_.ProcessName -match 'tailscale|wireguard|openvpn|clash|surge|v2ray|trojan|ss|netch' } | Format-Table ProcessName,Id -AutoSize\""
```

**Key finding (2026-07-03)**: Tailscale + WireGuard running simultaneously on Windows caused **10 network interfaces UP**, and `tailscaled` daemon intercepted every packet to check tunnel eligibility. This inflated Ethernet latency from 1ms to 16-99ms.

Each VPN tunnel daemon adds a per-packet intercept cost that manifests as jitter — even if the default route doesn't go through the tunnel.

Count active network interfaces:

```bash
ssh win "powershell -Command \"Get-NetAdapter | Where-Object Status -eq 'Up' | Format-Table Name,InterfaceDescription,LinkSpeed -AutoSize\""
```

**More than 5 active interfaces (excluding physical) = likely jitter source.**

Cleanup actions (see `references/windows-vpn-removal.md` for details):
- Tailscale: stop service, msiexec uninstall, delete AppData/ProgramData/registry
- WireGuard: disable service, kill process
- VMware/WSL: disable virtual adapters via `Disable-NetAdapter`

### Layer 4: ISP Path Latency

```bash
# Traceroute from gaming machine to game servers
ssh win "tracert -d -h 12 -w 2000 8.8.8.8"
ssh win "tracert -d -h 12 -w 2000 1.1.1.1"

# Ping game server endpoints (example IPs)
ssh win "ping -n 10 103.242.68.1"   # Riot SEA (Singapore)
ssh win "ping -n 10 155.133.248.1"  # Steam HK

# pathping for hop-by-hop jitter
ssh win "pathping -h 10 -q 5 -p 100 8.8.8.8"
```

HiNet (common Taiwan ISP) baseline:
- Router to HiNet first hop: 2-26ms (acceptable)
- HiNet to Google DNS: 7-13ms (excellent)
- HiNet to Cloudflare: 8-13ms (excellent)
- HiNet to game servers (Tokyo/HK/SG): 220-300ms (physical distance, unavoidable)

### Layer 5: DNS Resolver Check

Slow DNS causes initial connection lag (not packet lag, but match-join delay):

```bash
ssh win "powershell -Command \"Get-DnsClientServerAddress | Where-Object ServerAddresses -ne \$null | Format-Table InterfaceAlias,ServerAddresses -AutoSize\""
```

If DNS is Tailscale's `fec0:0:0:ffff::1` → rip out Tailscale. If `192.168.68.1` → router DNS (acceptable). If `8.8.8.8`/`1.1.1.1` → public DNS (ideal for gaming).

## Output Template

Present results in this format to the user:

```
| 測試 | min | avg | p90 | p99 | max | 評估 |
|---|---|---|---|---|---|---|
| Router (本地) | | | | | | |
| 8.8.8.8 (Google) | | | | | | |
| Game server | | | | | | |
```

Root cause priority:
1. **WiFi retransmit jitter** (if router ping p99 > 50ms on WiFi) → switch to Ethernet
2. **VPN/tunnel interference** (if >3 tunnel interfaces UP) → remove VPN or disable interfaces
3. **Virtual adapters** (VMware/WSL/Hyper-V) → disable when not in use
4. **ISP distance to game server** (220ms+ to Tokyo/HK) → use game accelerator (UU/雷神)
5. **Router QoS/bufferbloat** → configure QoS on router

## Pitfalls

- **`du -sh` won't work over SSH on Windows** — use `ping` and PowerShell commands instead.
- **`ping -n 50` over SSH can timeout the SSH session** at 30s default timeout. Set hermes terminal timeout to 60s or use `ping -n 20`.
- **`chcp 65001` needed for Traditional Chinese output on Windows** — `ssh win "chcp 65001 >nul & ping ..."` makes ping output readable. Without it, Big5 encoding garbles PowerShell output.
- **Windows `ping` uses 1-second interval by default** — for jitter detection, the default interval is fine (you want to see the pattern). For burst jitter, add `-n 50` and analyze percentiles.
- **wdutil requires sudo on macOS** — `sudo wdutil info` for WiFi stats. Without sudo, it prints usage. The alternative `system_profiler SPAirPortDataType` works without sudo but is slower.
- **WiFi signal quality ≠ low jitter** — signal can be -46 dBm (excellent) but the MAC layer can still retransmit 20% of packets, causing 50-135ms spikes. Always test latency, not just signal.
- **Multiple utun interfaces on Mac are normal** — Tailscale creates utun0-3, utun10-11. They show in `ifconfig` and `netstat -rn` with fe80:: default routes. These are normal on the Mac side (the agent's side). The problem is when they're on the **gaming machine** (Windows side).
