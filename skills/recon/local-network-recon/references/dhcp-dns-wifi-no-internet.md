# DHCP DNS failure can masquerade as Wi‑Fi failure

Use when the user says some devices cannot reach the internet on Wi‑Fi, but wired devices or one specific machine still work.

## Verification sequence

1. Confirm subnet, interface, gateway:
```bash
ifconfig | grep -E 'inet (10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' | head -5
route -n get default | grep 'gateway\|interface'
```

2. Inspect the live DHCP lease on the affected interface:
```bash
ipconfig getpacket en0 | sed -n '1,220p'
```
Look specifically for:
- `router`
- `domain_name_server`
- `server_identifier`

3. Compare effective resolver order vs DHCP-advertised DNS:
```bash
scutil --dns | sed -n '1,180p'
```
Watch for supplemental resolvers from VPN/Tailscale that can hide the problem on the current Mac.

4. Test the advertised DNS server directly:
```bash
dig +time=2 +tries=1 @<dhcp_dns_ip> www.google.com A
ping -c 3 <dhcp_dns_ip>
arp -a | grep '(<dhcp_dns_ip>)'
```

5. Test the router or known-good public DNS directly:
```bash
dig +time=2 +tries=1 @<router_ip> www.google.com A
dig +time=2 +tries=1 @1.1.1.1 www.google.com A
```

## Interpretation pattern

- DHCP advertises DNS `X`
- `dig @X` times out
- `dig @router` succeeds
- affected devices rely only on DHCP DNS
- current Mac still works because a VPN / Tailscale supplemental resolver is higher priority

=> Root cause is usually broken DHCP DNS, not Wi‑Fi PHY/link failure.

## Remediation

- Change router DHCP DNS to a working resolver:
  - router IP itself, or
  - `1.1.1.1` / `8.8.8.8`
- Or restore the intended internal DNS host if `X` was a Pi-hole / AdGuard / custom DNS server.
- Renew leases or reconnect Wi‑Fi on affected devices after the DHCP change.

## Real example from Wang network

- Gateway: `192.168.68.1`
- DHCP-advertised DNS: `192.168.68.105`
- `dig @192.168.68.105 www.google.com A` => timeout
- `dig @192.168.68.1 www.google.com A` => success
- Mac still resolved names because Tailscale resolver `100.100.100.100` was installed as a higher-priority supplemental resolver.
