# CTF Mastery Drills

Use these to strengthen practical solving skill. A drill counts only if there is a solver/exploit/extractor and writeup.

## Phase 1 — Core recognition

- Web: solve one IDOR/auth bypass, one SQLi, one SSTI.
- Crypto: solve one single-byte XOR, one repeating XOR, one textbook RSA/small-e.
- Forensics: solve one image metadata/appended-data task, one pcap stream task.
- Reverse: solve one strings/encoded-constant crackme.
- Pwn: solve one ret2win/no-canary binary.
- Misc: solve one encoding chain and one simple pyjail.

## Phase 2 — Intermediate exploitation

- Web: SSRF to localhost/metadata lab, upload bypass, stored XSS/admin bot.
- Crypto: CBC padding oracle, CBC bitflip, RSA shared-prime/common modulus, ECDSA nonce reuse.
- Forensics: LSB stego, nested/corrupt archive, USB HID pcap, memory dump process/file extraction.
- Reverse: z3 constraint solve, APK static reverse, WASM reverse.
- Pwn: ret2libc with leak, format string leak/write, basic tcache double-free.
- Misc: protocol automation, maze solver, Unicode/parser jail bypass.

## Phase 3 — Advanced families

- Web: cache poisoning/smuggling lab, deserialization chain, race condition.
- Crypto: lattice small roots/HNP, invalid-curve/small-subgroup ECC, PRNG state clone.
- Forensics: disk image deleted-file recovery, audio spectrogram/DTMF/SSTV, document macro/embedded object.
- Reverse: custom VM emulator, anti-debug patch, packed binary unpacking.
- Pwn: heap overlap/unsorted leak, seccomp ORW ROP, stack pivot/ret2csu.
- Misc: cloud IAM policy puzzle, blockchain storage/reentrancy, AI prompt/model file lab.

## Phase 4 — Breadth gaps

- OSINT: geolocation from image, username correlation, archived web history.
- Mobile: API secret extraction and cert-pinning bypass in a lab APK.
- Cloud: public bucket/IAM/CI artifact lab.
- Blockchain: Foundry/Hardhat exploit script against a local challenge.
- Hardware/RF/ICS: firmware extraction and one signal/protocol decode.
- Game/Protocol: bot/state-machine challenge with automated solver.

## Per-drill deliverables

```text
challenge/
  artifacts/
  solve/solver_or_exploit.*
  notes.md
  writeup.md
```

Ledger row must include:

- challenge name/source
- category/family
- decisive technique
- script path
- skill updated yes/no

## Review cadence

After each batch:

1. List solved/failed attempts.
2. Identify repeated blockers.
3. Patch skills/scripts.
4. Pick next drills to cover weak families.
