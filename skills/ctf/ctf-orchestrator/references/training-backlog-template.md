# Training Backlog Template

| Domain | Representative families | Minimum practical drills |
|---|---|---|
| Web | auth/IDOR, SQLi, SSTI, SSRF, upload, XSS admin bot, deserialization, race | 2 source-review + 2 black-box + 1 browser/admin-bot |
| Crypto | XOR, RSA, ECC signatures, block/oracle, hash/MAC, PRNG, lattice | 1 scripted solver per family |
| Forensics | image/stego, pcap, memory, disk, archive, document, audio | 1 extraction workflow per artifact type |
| Reverse | native crackme, APK, WASM, bytecode, custom VM, obfuscation | 1 static solve + 1 dynamic solve + 1 z3 solve |
| Pwn | ret2win, ret2libc, format string, heap/tcache, shellcode/ORW, seccomp | 1 exploit per mitigation pattern |
| Misc | pyjail, encoding, OSINT, protocol/game, cloud toy, blockchain toy | 1 automation/escape per family |
