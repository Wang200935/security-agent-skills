# Category Router

| Category | Typical artifacts | Core skills / attack families | Hermes route |
|---|---|---|---|
| Web | URL, HTTP API, source, cookies | auth, IDOR, SQLi/NoSQLi, SSTI, SSRF, upload, XSS, deserialization, cache/request smuggling, races | `ctf-web-exploitation` |
| Crypto | ciphertext, key material, oracle, math source | XOR, block modes, hash/MAC, RSA, ECC, lattices, PRNG, signatures, protocols | `ctf-cryptography` |
| Forensics | image, pcap, disk/memory dump, archive, docs, logs | metadata, carving, stego, network streams, USB HID, volatility, filesystem recovery | `ctf-forensics` |
| Reverse | executable, APK/JAR, WASM, bytecode, firmware | decompile, disassemble, anti-debug, obfuscation, custom VM, constraint solving | `ctf-reverse-engineering` |
| Pwn | ELF/PE + libc/ld, nc service, C/C++ source | stack/heap overflow, format strings, ROP, ret2libc, shellcode, seccomp ORW, sandbox escape | `ctf-pwn-binary-exploitation` |
| Kernel | bzImage/vmlinux, rootfs.cpio, QEMU script | QEMU TCG bugs, kernel module vulns, modprobe_path overwrite, physmap R/W, KASLR bypass | `ctf-kernel-exploitation` |
| Misc / Jail | service prompt, restricted eval, puzzle text | pyjail/JS/shell jail, Unicode/parser tricks, encodings, proof-of-work, state machines | `ctf-misc` |
| OSINT | image, username, website clue, location/time | geolocation, metadata, archives, DNS/history, social correlation | `ctf-misc` plus web search/browser |
| Mobile | APK/IPA, mobile API, emulator target | manifest/resources, Java/Kotlin/Swift, native libs, cert pinning, local storage | start `ctf-reverse-engineering`; add `ctf-web-exploitation` for APIs |
| Cloud / DevOps | IAM policy, S3/GCS bucket, Kubernetes, CI logs, Terraform | exposed secrets, metadata SSRF, weak IAM, public buckets, CI artifact leaks | start `ctf-misc`; add `ctf-web-exploitation` for SSRF |
| Blockchain | Solidity/Vyper, ABI, RPC, wallet/key hints | ABI decoding, storage layout, reentrancy, integer/logic bugs, weak private keys | start `ctf-misc`; use crypto where key math appears |
| Hardware / RF / ICS | firmware, captures, logic traces, SDR/audio, Modbus/CAN | binwalk firmware, protocol decode, signal analysis, default creds, embedded web | `ctf-forensics` + `ctf-reverse-engineering` |
| Game / Protocol | TCP game, maze, bot, custom binary/text protocol | state-machine modeling, pathfinding, automation, replay, fuzzing grammar | `ctf-misc` |
| AI / ML | model, prompt endpoint, classifier, pickle/ONNX | prompt injection in labs, adversarial examples, model extraction, unsafe pickle | `ctf-misc`; add web/reverse as needed |

**Cross-references to comprehensive skills:**
- `reverse-engineering` — comprehensive RE framework (Ghidra, IDA, angr, deobfuscation, unpacking, anti-debug bypass, Go/Rust/.NET/Java/Android/iOS/WASM)
- `pentest` — AD/cloud/container pentesting, privilege escalation, C2, EDR evasion
- `web-app-pentest` — full web app methodology (OWASP Top 10, auth, injection, file bugs, SSRF, XSS, deserialization, race/logic)
- `api-security-testing` — REST/GraphQL/WebSocket/gRPC API security
- `ai-mcp-security` — LLM, Agent, MCP, RAG security assessment
