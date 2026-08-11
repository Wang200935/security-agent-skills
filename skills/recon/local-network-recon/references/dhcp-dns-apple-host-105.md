# 192.168.68.105 DHCP DNS Misconfiguration Case

## Symptom
Some home devices had Wi‑Fi association but could not reach the internet. Switching those devices to wired Ethernet restored connectivity.

## Root cause pattern
Router DHCP on `192.168.68.1` advertised `192.168.68.105` as DNS. Direct queries to `.105` initially timed out, making Wi‑Fi look broken. The affected Mac still had connectivity because Tailscale installed supplemental resolver `100.100.100.100`, masking the failure.

## Live checks that exposed it
```bash
ipconfig getpacket en0 | sed -n '1,220p'
scutil --dns | sed -n '1,180p'
dig +time=2 +tries=1 @192.168.68.1 www.google.com A
dig +time=2 +tries=1 @192.168.68.105 www.google.com A
arp -a | grep '(192.168.68.105)'
```

Observed:
- DHCP `domain_name_server (ip_mult): {192.168.68.105}`
- Router `.1` answered DNS normally
- `.105` timed out for direct DNS queries
- ARP for `.105` was initially incomplete, then later resolved to `d4:57:63:c6:ee:90`

## Identity clues for `.105`
Later probing showed `.105` was not a DNS appliance but likely an Apple/macOS host:
- MAC vendor: Apple
- Open ports: `22`, `88`, `445`, `5000`, `5900`
- Port `5000` returned `Server: AirTunes/950.6.1`
- Port `5900` returned `RFB 003.889`
- `root/1234` and `admin/1234` both failed for SSH/SMB

## Interpretation
This combination strongly suggests a Mac or Apple-based host with:
- Remote Login (SSH)
- File Sharing (SMB)
- AirPlay/AirTunes receiver
- Screen Sharing / VNC

If such a host is advertised as DNS, treat the problem as bad DHCP configuration or a retired experiment, not a Wi‑Fi radio/backhaul fault.

## Remediation
1. Remove `.105` from DHCP DNS settings on the router.
2. Replace with router DNS or public resolvers.
3. Identify which Mac/Apple host owns `.105` and check whether it was ever intentionally configured to run DNS forwarding/caching.
4. Do not assume a remembered `root/1234` credential applies; verify the actual local account if login is needed.
