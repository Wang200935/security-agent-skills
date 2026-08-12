# Universal First 10 Minutes

1. **Preserve artifacts**: copy files/URLs/source/output exactly; compute hashes for binaries/files.
2. **Classify category**: Web, Crypto, Forensics, Reverse Engineering, Pwn/Binary Exploitation, Misc, Mobile, Cloud, Blockchain, Hardware/RF/ICS, AI/ML, OSINT, Game/Protocol, or mixed.
3. **Find flag format**: challenge page, event rules, strings, examples.
4. **Inventory inputs/outputs**:
   - files: type, size, entropy, strings, metadata
   - services: URL/host/port, protocol, response shape
   - code: language, dependencies, dangerous functions
   - binaries: arch, PIE/NX/canary/RELRO, packed/static/dynamic
5. **Run low-cost probes first** before heavy tooling.
6. **Keep a solve log**: commands tried, observations, dead ends, hypotheses.
7. **Script the exploit/extraction** once the path is known.
8. **Verify flag** and produce a concise writeup.
9. **Patch the relevant CTF skill** if a new reusable trick/tooling fix appears.
