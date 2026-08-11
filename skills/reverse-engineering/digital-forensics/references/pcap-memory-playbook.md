# PCAP and Memory Forensics Playbook

## PCAP Triage

```bash
tshark -r capture.pcap -q -z io,phs
tshark -r capture.pcap -Y http
tshark -r capture.pcap -Y dns
tshark -r capture.pcap -Y 'tcp.stream eq 0' -T fields -e data
```

Check:
- HTTP objects and credentials
- DNS TXT/subdomain exfiltration
- ICMP payloads
- FTP/SMTP/POP/IMAP credentials
- TLS keylog file provided by challenge
- USB HID keyboard captures
- TCP stream reassembly

## USB HID

- Extract interrupt transfer bytes.
- Map HID keycodes to characters, considering Shift.
- Look for typed flag, password, or command sequence.

## Memory Triage with Volatility 3

```bash
vol -f memory.raw windows.info
vol -f memory.raw windows.pslist
vol -f memory.raw windows.cmdline
vol -f memory.raw windows.netscan
vol -f memory.raw windows.filescan
```

Check:
- suspicious processes and command lines
- environment variables
- clipboard/console history when available
- browser history/downloads
- dumped files containing flag
- network connections and credentials

## Common CTF Signals

- base64 in DNS labels or HTTP parameters
- repeated short packets carrying ASCII bytes
- credentials reused to decrypt archives
- process names or command line containing challenge hints
