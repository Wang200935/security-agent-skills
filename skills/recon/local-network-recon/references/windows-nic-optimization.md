# Windows NIC + TCP/IP Optimization for Gaming (via SSH)

Registry-level network adapter tuning and TCP/IP stack optimization for low-latency gaming on Windows. All commands executed via SSH from macOS using CMD syntax (PowerShell over SSH has encoding issues with CJK Windows).

## Prerequisites

- SSH to Windows gaming PC configured (`Host win` in `~/.ssh/config`)
- Windows OpenSSH Server running
- User has admin privileges on Windows (SSH session inherits them)

## Finding the NIC Registry Key

The Realtek PCIe GbE Family Controller lives under the Windows network adapter class registry:

```
HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0002
```

To find the correct subkey (0000, 0001, 0002, etc.) for your specific NIC:

```bash
ssh win "reg query \"HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\" /s 2>&1 | findstr /R \"Realtek DriverDesc\""
```

The subkey containing `DriverDesc REG_SZ Realtek PCIe GbE Family Controller` is the one to modify. In this session it was `0002`, but it may differ on other machines.

You can also get the NIC's `NetCfgInstanceId` GUID from the same registry key — this is needed for TCP/IP interface settings:

```bash
ssh win "reg query \"HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0002\" /v NetCfgInstanceId 2>&1"
# Example: {360C2113-1C1B-428F-8995-996B25A7834B}
```

## Registry Optimizations (NIC Driver Layer)

All commands use `reg add` with `/f` (force). Apply all at once:

```bash
# Define the key path once
NIC_KEY="HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0002"

ssh win "reg add \"$NIC_KEY\" /v *EEE /t REG_SZ /d 0 /f
& reg add \"$NIC_KEY\" /v EnableGreenEthernet /t REG_SZ /d 0 /f
& reg add \"$NIC_KEY\" /v PowerDownPll /t REG_SZ /d 0 /f
& reg add \"$NIC_KEY\" /v *InterruptModeration /t REG_SZ /d 0 /f
& reg add \"$NIC_KEY\" /v ASPM /t REG_DWORD /d 0 /f
& reg add \"$NIC_KEY\" /v CLKREQ /t REG_DWORD /d 0 /f
& reg add \"$NIC_KEY\" /v *WakeOnPattern /t REG_SZ /d 0 /f
& reg add \"$NIC_KEY\" /v *WakeOnMagicPacket /t REG_SZ /d 0 /f
& echo REG_DONE"
```

### What each setting does

| Registry Value | Default | Optimized | Effect |
|---|---|---|---|
| `*EEE` | `1` (on) | `0` (off) | Energy Efficient Ethernet — puts link into sleep states between packets, causes wake-up latency spikes |
| `EnableGreenEthernet` | `1` (on) | `0` (off) | Realtek's green ethernet power saving — same problem as EEE |
| `PowerDownPll` | `1` (on) | `0` (off) | PLL power-down when link idle — wake-up adds 10-50ms jitter |
| `*InterruptModeration` | `1` (on) | `0` (off) | **🔴 Critical for gaming**: coalesces interrupts to reduce CPU usage, but delays packet processing by 50-200μs per packet. Disabling = more CPU interrupts but lower latency. |
| `ASPM` | `2` (L0s+L1) | `0` (off) | PCIe Active State Power Management — puts PCIe link into sleep states, wake-up causes latency |
| `CLKREQ` | `1` (on) | `0` (off) | PCIe clock request power management — same family as ASPM |
| `*WakeOnPattern` | `1` (on) | `0` (off) | Keeps pattern-matching circuitry active, consumes power and adds processing overhead |
| `*WakeOnMagicPacket` | `1` (on) | `0` (off) | Same — WoL features not needed during gaming |

### Settings NOT changed (already optimal or needed)

| Setting | Value | Why kept |
|---|---|---|
| `PowerSavingMode` | `0` (off) | Already off on this machine |
| `AdvancedEEE` | `0` (off) | Already off |
| `*FlowControl` | `3` (Rx&Tx) | Flow control prevents packet drop — keep on |
| `*PriorityVLANTag` | `3` | QoS tagging — keep on |
| `*ReceiveBuffers` | `512` | Good buffer size |
| `*TransmitBuffers` | `128` | Could increase to 512, but 128 is adequate |
| `*JumboPacket` | `1514` | Standard MTU — don't change for internet |
| `*RSS` | `1` (on) | Receive Side Scaling — keep on for multi-core |
| `*LsoV2IPv4/IPv6` | `1` (on) | Large Send Offload — keep on |

## TCP/IP Stack Optimization

### Disable TCP Auto-Tuning + RSC + ECN

```bash
ssh win "netsh interface tcp set global autotuninglevel=disabled 2>&1
& netsh interface tcp set global ecncapability=disabled 2>&1
& netsh interface tcp set global rss=enabled 2>&1
& netsh interface tcp set global rsc=disabled 2>&1
& echo TCP_DONE"
```

| Setting | Default | Optimized | Effect |
|---|---|---|---|
| `autotuninglevel` | normal | disabled | Stops dynamic TCP window resizing (adds jitter for small packets) |
| `ecncapability` | disabled | disabled | ECN marks packets during congestion — unnecessary for gaming |
| `rss` | enabled | enabled | Receive Side Scaling — distributes packets across CPU cores (keep on) |
| `rsc` | enabled | disabled | Receive Segment Coalescing — merges packets, adds delay |

### Set TcpAckFrequency + TCPNoDelay (per-interface)

Find the interface GUID from the NIC registry key's `NetCfgInstanceId` value, then:

```bash
# Replace {GUID} with the actual NetCfgInstanceId
IFACE_KEY="HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{360C2113-1C1B-428F-8995-996B25A7834B}"

ssh win "reg add \"$IFACE_KEY\" /v TcpAckFrequency /t REG_DWORD /d 1 /f
& reg add \"$IFACE_KEY\" /v TCPNoDelay /t REG_DWORD /d 1 /f
& echo TCPACK_DONE"
```

| Setting | Default | Optimized | Effect |
|---|---|---|---|
| `TcpAckFrequency` | 5 (200ms ACK delay) | `1` (immediate ACK) | **🔴 Critical for gaming**: forces TCP to ACK every packet immediately instead of waiting for 2 packets or 200ms. Reduces latency by up to 200ms per round-trip. |
| `TCPNoDelay` | not set (Nagle on) | `1` (Nagle off) | **🔴 Critical for gaming**: disables Nagle's algorithm which coalesces small packets. Games send small frequent packets — Nagle delays them. |

### Disable NetBIOS over TCP/IP

```bash
ssh win "reg add \"HKLM\SYSTEM\CurrentControlSet\Services\Netbt\Parameters\Interfaces\Tcpip_{GUID}\" /v NetbiosOptions /t REG_DWORD /d 2 /f & echo NETBIOS_DONE"
```

`NetbiosOptions=2` disables NetBIOS on this interface (disables NetBIOS name resolution broadcasts which waste airtime).

## Power Plan: High Performance

```bash
ssh win "powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>&1 & echo POWERPLAN_DONE"
# Verify
ssh win "powercfg /getactivescheme 2>&1"
```

GUID `8c5e7fda-...` is the built-in "High Performance" plan. This prevents CPU frequency scaling and PCIe power-down that causes jitter.

## Disable AllowComputerToTurnOffDevice

```bash
# Via PowerShell (the only way for this setting)
ssh win "powershell -Command \"Set-NetAdapterPowerManagement -Name '乙太網路' -AllowComputerToTurnOffDevice Disabled\""
```

Note: the interface name `乙太網路` is the Chinese display name for "Ethernet" on a Taiwan Chinese Windows. On English Windows, use `Ethernet` or whatever `Get-NetAdapter` shows.

## Applying Changes: NIC Restart

Registry changes require a NIC restart to take effect. **This will temporarily drop the SSH connection:**

```bash
# Restart the NIC (connection will drop for 5-10 seconds)
ssh win "powershell -Command \"Disable-NetAdapter -Name '乙太網路' -Confirm:0; Start-Sleep 3; Enable-NetAdapter -Name '乙太網路' -Confirm:0\""
# This will timeout the SSH session — that's expected
# Wait 5-10 seconds, then reconnect:
sleep 5
ssh -o ConnectTimeout=10 win "echo RECONNECTED"
```

### ⚠️ PCIe-layer changes may need a full reboot

`ASPM`, `CLKREQ`, and `PowerDownPll` are PCIe link-layer settings. A NIC disable/enable cycle may NOT fully apply them — they need a **system reboot**. After the NIC restart, test latency and if jitter persists, tell the user to reboot Windows for full effect.

## Verification

```bash
# Ping router 20-50 times
ssh win "ping -n 20 192.168.68.1"
# Watch for: min should be 1ms, avg should be <10ms, max should be <50ms

# Ping internet
ssh win "ping -n 20 8.8.8.8"
# Watch for: avg should be <30ms (ISP-dependent)

# Cross-machine from Mac
ping -c 30 -i 0.1 192.168.68.112
# Compare to pre-optimization baseline
```

## Expected Improvement

Based on 2026-07-03 session (before → after VPN removal + NIC optimization):

| Metric | Before | After | Improvement |
|---|---|---|---|
| Mac→Win avg | 15.4 ms | 10.9 ms | **-29%** |
| Mac→Win min | 3.1 ms | 2.7 ms | -13% |
| Mac→Win stddev | 22.2 ms | 19.7 ms | -11% |
| Win→Router min | 2 ms | 1 ms | -50% |

Full effect (especially PCIe ASPM/CLKREQ) requires a Windows reboot.

## Pitfalls

- **PowerShell `Set-NetAdapter*` commands over SSH may produce no output** — the SSH session encoding can eat PowerShell's return stream. The command may have succeeded silently. Always verify with `reg query` or `Get-NetAdapter` afterwards.
- **`Disable-NetAdapter` drops SSH** — don't panic when the terminal times out. Wait 5-10 seconds and reconnect.
- **Interface display name is localized** — on Taiwan Chinese Windows, Ethernet shows as `乙太網路`, not `Ethernet`. Always check with `Get-NetAdapter` first, or use the `-InterfaceDescription` parameter with `Realtek PCIe GbE Family Controller` which is always English.
- **`net stop` exit code 36 on Chinese Windows** — don't rely on exit codes; check `sc query` output for `STATE : 1 STOPPED` instead.
- **Registry values with `*` prefix** — values like `*EEE`, `*InterruptModeration`, `*WakeOnPattern` are standard NDIS keywords. The `*` is part of the value name. Use `reg add` with the `*` included: `reg add "..." /v *EEE /t REG_SZ /d 0 /f`.
- **`PowerSavingMode` (no `*`) vs `*EEE` (with `*`)** — these are different settings. `PowerSavingMode` is Realtek-specific; `*EEE` is the NDIS-standard EEE toggle. Disable both.
- **VMware/WSL adapters** — user may need VMware and WSL intermittently. Don't disable them unless the user confirms. NIC registry changes apply to the physical Realtek adapter only and don't affect virtual adapters.
