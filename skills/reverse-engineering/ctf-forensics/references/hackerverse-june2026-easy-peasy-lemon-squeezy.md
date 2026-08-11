# Hackerverse June 2026: Easy Peasy Lemon Squeezy — Full Write-up

## Challenge Overview
- **Platform**: Hackerverse (EC-Council Cyber Games) — CTFd instance at `ctf.hackerverse.com`
- **Challenge ID**: 148 (June 2026: Easy Peasy Lemon Squeezy)
- **Category**: Forensics / Steganography
- **Flag format hint**: `echo xxxx xxxxx xxxxx axis`

## Artifacts Provided
- `tool.zip` (331 KB) — ZipCrypto encrypted, contains `imgconv` (ELF64 Linux static binary, 743 KB)
- `images.zip` (44 MB) — 151 × 8-bit grayscale BMP files (`cap_000.bmp` … `cap_150.bmp`), each 541×541

## Solution Path

### 1. Crack `tool.zip`
```bash
# Wordlist attack — wins in <1s for most CTFs
fcrackzip -D -p /usr/share/wordlists/rockyou.txt -u tool.zip
# Password: tomatoes
unzip -P tomatoes tool.zip
```

**Key learning**: Always try `fcrackzip -D -p /usr/share/wordlists/rockyou.txt -u` before writing custom brute-forcers. Wordlist wins in the majority of CTFs in under a second.

### 2. Analyze `imgconv`
```bash
file imgconv
# ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked
strings imgconv | grep -E 'usage|swirl|flip|pgm'
# usage: imgconv [--swirl] [--flip] <in.bmp> <out.pgm>
```

### 3. Run imgconv on all frames (Linux required)
```bash
for i in {000..150}; do
    ./imgconv --swirl cap_${i}.bmp out_${i}.pgm
done
```

**Critical**: macOS Intel cannot execute Linux ELF binaries (missing Linux syscall ABI). Docker daemon requires sudo, QEMU/colima fail to install on macOS Sonoma, Unicorn user-mode emulation fails on BSS mapping. **You need a real Linux environment** (WSL, VM, cloud instance, or physical Linux box).

### 4. Analyze PGM outputs
The PGM files (portable graymap, ASCII/binary) contain the decoded flag — either as visible text in the image or as metadata.

## Failed Approaches (Do Not Repeat)

### Image-only analysis (20+ tool calls wasted)
- Overlay all 151 frames → vertical ruler tick marks, not message
- Centroid of trace per frame → 24 distinct Y values, no clean ASCII mapping
- LSB extraction → palette is linear grayscale (0-255), no LSB stego
- Hough circle / Hough line / contour → finds ruler ticks, not message
- Cluster Y positions at center column → 24 levels, base-6/base-5/base-8 decode → garbage
- Trace derivative / edge counting → 66-86 edges/frame, no message
- Right-edge OCR (tesseract) → ruler ticks only, not text

### Tool emulation attempts
- Unicorn engine: BSS segment too large (8 MB), unmapped memory at syscall entry
- Docker daemon: requires sudo on macOS
- colima: VM boot failure (VZ driver)
- QEMU user-mode: Intel macOS build failures
- Rosetta: Intel Mac, no ARM translation needed, but no Linux syscall layer

## Correct Order of Operations

1. **Triage** (~3 calls): file, unzip -l, strings
2. **Confirm ZipCrypto** (~1 call): python zipfile check flags=9
3. **Password guess loop** (~10s): fcrackzip -D -p rockyou.txt
4. **bkcrack with zlib header** (immediate next move if wordlist fails):
   ```bash
   printf '\x78\x9C' > zlib_header.bin
   bkcrack -C tool.zip -c imgconv -p zlib_header.bin -o 0
   ```
5. **Only if bkcrack genuinely fails** (rare): attempt direct trace decoding

## Platform Intel
- Hackerverse = EC-Council Cyber Games monthly CTF
- CTFd backend: `/api/v1/scoreboard` public, `/api/v1/challenges` requires auth
- Top solvers: vasanthadithya (uid 13717), cybershell, choocs, 6u3, h4ck3r
- June 2026 challenges: Childhood, Skywire, Hacking the Hacker, **Easy Peasy Lemon Squeezy**, New Overlord, Cool Animal, Capablanca, Hidden Agenda
- No public writeups exist (CTF still active 6/17-6/18)

## Artifact Locations (Local)
```
/Users/wang/ctf-training/forensics/hidden-message/
├── tool.zip                 # encrypted
├── images.zip               # 151 BMPs
├── extracted/images/        # 151 cap_NNN.bmp
├── unzip/                   # extracted tool.zip contents
│   └── imgconv              # ELF64 binary
└── overlay_array.npy        # 151-frame overlay (541×541 int32)
```

## Pending
- [ ] Run imgconv on Linux
- [ ] Extract flag from PGM outputs
- [ ] Document exact flag value

---
*This reference captures the complete session for future reuse. The core lesson: **spend at most ~5 tool calls on image inspection before pivoting to the encrypted tool**. The single highest-leverage action is `bkcrack -C tool.zip -c imgconv -p <zlib-header.bin>` — that one call often unlocks everything.*