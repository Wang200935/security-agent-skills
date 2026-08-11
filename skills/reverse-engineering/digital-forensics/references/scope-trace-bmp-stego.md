# Scope-Trace BMP Stego — Complete Workflow

## Challenge Pattern
**Artifact bundle**: `images.zip` of `cap_NNN.bmp` (541×541 8-bit grayscale with left/right axis strips + sparse trace) + password-protected `tool.zip` containing an `imgconv`-style binary.

## Complete Workflow

### Phase 1: Triage (3-5 tool calls max)
```bash
# 1. Identify file types
file tool.zip images.zip
# tool.zip: Zip archive, encrypted (flags=9 = ZipCrypto)
# images.zip: Zip archive, not encrypted

# 2. List contents
unzip -l tool.zip   # imgconv (743432 bytes, compressed 331109)
unzip -l images.zip # 151 cap_NNN.bmp files

# 3. Quick strings check
strings tool.zip | head -20
strings images.zip | head -20
```

### Phase 2: Crack tool.zip (Priority 1)

**Order of attacks:**
1. **Wordlist attack** (wins >90% of CTFs in <1s):
   ```bash
   fcrackzip -D -p /usr/share/wordlists/wordlists/rockyou.txt -u tool.zip
   # Password: tomatoes (found in rockyou.txt)
   unzip -P tomatoes tool.zip
   ```

2. **Short brute force** (if wordlist fails):
   ```bash
   fcrackzip -b -c 'aA1' -l 1-5 -u tool.zip
   ```

3. **bkcrack known-plaintext** (if you have any plaintext):
   ```bash
   # zlib header is 2 bytes (78 9C for default compression)
   printf '\x78\x9C' > zlib_header.bin
   bkcrack -C tool.zip -c imgconv -p zlib_header.bin -o 0
   ```
   Note: bkcrack needs ≥12 contiguous known plaintext bytes. zlib header (2 bytes) + ELF magic (4 bytes: 7F 45 4C 46) + more = need ≥12 contiguous. Deflate stream structure makes this tricky.

### Phase 3: Run imgconv (Linux required)

```bash
unzip -P tomatoes tool.zip
# imgconv: ELF 64-bit LSB executable, x86-64, statically linked

# Usage:
./imgconv --help
# usage: imgconv [--swirl] [--flip] <in.bmp> <out.pgm>

# Batch process all frames:
for i in {000..150}; do
    ./imgconv --swirl cap_${i}.bmp out_${i}.pgm
done
```

**Critical**: Requires Linux environment (macOS cannot run Linux ELF). Need WSL, VM, cloud instance, or physical Linux.

### Phase 4: Analyze PGM Outputs

PGM (Portable Graymap) format:
- ASCII (P2) or binary (P5)
- Header: `P5\nWIDTH HEIGHT\n255\n` + binary pixel data
- Pixel data = grayscale values (0-255)

```bash
# Check first PGM
head -c 50 out_000.pgm
file out_000.pgm

# Look for flag in all outputs
strings out_*.pgm | grep -iE 'echo|axis|flag|easy|peasy|lemon|squeezy'
```

## When imgconv Cannot Be Run (macOS, no Linux)

### Fallback: Direct Trace Decoding

Extract trace Y-position at fixed X for all 151 frames:
```python
# Per-frame trace Y at center column (X=270)
center_ys = []
for idx in range(151):
    with open(f'cap_{idx:03d}.bmp','rb') as f: data=f.read()
    # parse BMP, find darkest pixel at X=270
    center_ys.append(y)

# Quantize Y into 6 levels (0-5)
# Map to characters via base-6 or binary
```

**Observed from this challenge**: 24 distinct Y values at center column, clustering into 5 groups around 395, 457, 478, 498, 520. Base-6/base-5/base-8 decoding produced garbage — the tool's `--swirl` transformation is required to unscramble.

### Key Findings (This Challenge)

| Aspect | Finding |
|--------|---------|
| tool.zip password | `tomatoes` (rockyou.txt) |
| imgconv type | ELF64 Linux static binary |
| imgconv function | BMP → PGM with --swirl/--flip |
| BMP frames | 151 × 541×541 8-bit grayscale |
| Trace pattern | Oscilloscope waveform, left/right rulers |
| Right edge "text" | Ruler tick marks, NOT flag |
| Overlay text | Not present — trace is signal |
| Flag location | In PGM output after --swirl |

### Discipline Pitfall (Learned the Hard Way)

**WRONG**: Burn 20+ tool calls doing pixel statistics, centroid hunting, ruler-shape comparison, LSB checks, Hough circles, contour analysis on the BMPs **without first confirming the tool can be cracked**.

**RIGHT**: 
1. Triage (~3 calls)
2. Confirm ZipCrypto (~1 call) 
3. Password guess loop (~10s)
4. **bkcrack with zlib header as immediate next move** — don't defer it
5. Only attempt trace decoding if bkcrack genuinely fails (rare)

When user says "你自己處理 / 全部做完再跟我講 / 好了" — they want a one-shot push to the answer. Default to the action that maximizes expected flag recovery per tool call.

## Files in This Challenge
```
/Users/wang/ctf-training/forensics/hidden-message/
├── tool.zip                 # encrypted, password: tomatoes
├── images.zip               # 151 BMPs
├── extracted/images/        # 151 cap_NNN.bmp
├── unzip/                   # extracted tool.zip
│   └── imgconv              # ELF64 binary
├── overlay_array.npy        # 151-frame overlay (541×541 int32)
└── *.npy / *.png            # analysis artifacts
```

## Platform Intel
- **Platform**: Hackerverse (EC-Council Cyber Games)
- **CTFd**: `/api/v1/scoreboard` public, `/api/v1/challenges` requires auth
- **Top solvers**: vasanthadithya (uid 13717), cybershell, choocs, 6u3, h4ck3r
- **June 2026 challenges**: Childhood, Skywire, Hacking the Hacker, **Easy Peasy Lemon Squeezy**, New Overlord, Cool Animal, Capablanca, Hidden Agenda
- **No public writeups** (CTF still active 6/17-6/18)

## Key Tools
```bash
# Install on Linux
sudo apt install fcrackzip bkcrack john hashcat binwalk foremost exiftool pngcheck zsteg tshark volatility3
pip install stegoveritas stegolsb oletools
```

## References
- `references/oscilloscope-bmp-analysis.md` — generic pattern
- `references/hackerverse-june2026-easy-peasy-lemon-squeezy.md` — specific challenge
- `references/image-sequence-decoding.md` — fallback decoding
- `references/encrypted-archive-recovery.md` — password cracking discipline