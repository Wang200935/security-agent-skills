# Encrypted Archive Recovery — Password Cracking Discipline

## Overview
When facing an encrypted archive (ZIP, 7z, RAR) in CTF, follow this disciplined progression. The key insight: **wordlist wins >90% of CTF encrypted archives in under 1 second**. Custom brute-force scripts are almost always a waste of time.

## Attack Progression (Strict Order)

### 1. Wordlist Attack (Priority 1)
```bash
# ZIP (fcrackzip)
fcrackzip -D -p /usr/share/wordlists/rockyou.txt -u archive.zip

# 7z (7z2john + john)
7z2john archive.7z > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# RAR
rar2john archive.rar > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

**Why rockyou first?** 
- Contains 14M passwords including `tomatoes`, `password`, `admin`, CTF-specific terms
- fcrackzip tests ~100K passwords/second
- Most CTF authors use common passwords from rockyou

**Time budget**: 30 seconds max. If no hit, move to step 2.

### 2. Short Brute Force (Priority 2)
```bash
# ZIP: 1-5 chars alphanumeric
fcrackzip -b -c 'aA1' -l 1-5 -u archive.zip

# 7z: use hashcat mask
hashcat -m 11600 -a 3 hash.txt ?a?a?a?a?a?a?a
```

**Time budget**: 2 minutes max. 6-char alphanumeric = 62^6 ≈ 56B combinations — infeasible.

### 3. bkcrack Known-Plaintext (Priority 3)
Use when you have ≥12 contiguous known plaintext bytes from the compressed stream.

```bash
# For ZIP with deflate + zlib header (78 9C most common)
printf '\x78\x9C' > zlib_header.bin
bkcrack -C archive.zip -c filename -p zlib_header.bin -o 0
```

**Critical**: bkcrack requires **≥12 contiguous known plaintext bytes**.
- zlib header = 2 bytes (78 9C)
- ELF magic = 4 bytes (7F 45 4C 46)
- Need 6+ more contiguous bytes from deflate stream
- Deflate block structure makes contiguous bytes tricky to predict

### 4. Full Brute Force / GPU (Priority 4 — Rare)
```bash
# Only if you're certain password is short and not in rockyou
hashcat -m 13600 -a 3 hash.zip ?a?a?a?a?a?a
```
**Almost never needed for CTFs**.

## False Positive Pitfall (Critical)

When brute-forcing ZipCrypto with only CRC check:
- **False positives are common** — 1/65536 chance per password
- A "matching" CRC does NOT mean correct password
- **Must verify by full decompression**:
  ```python
  import zlib
  def verify(password):
      decrypted = decrypt_zipcrypto(encrypted_data, password)
      try:
          zlib.decompress(decrypted)
          return True
      except zlib.error:
          return False
  ```

**Our session example**: 17 "candidates" passed CRC check but ALL failed full decompression. Only `tomatoes` (found via rockyou) worked.

## Tool Selection Guide

| Archive Type | Primary Tool | Fallback |
|--------------|--------------|----------|
| ZIP | `fcrackzip` (wordlist) → `bkcrack` (if plaintext) | `hashcat` |
| 7z | `7z2john` + `john` | `hashcat -m 11600` |
| RAR | `rar2john` + `john` | `hashcat -m 13000` |
| PDF | `pdf2john` + `john` | `hashcat -m 10400/10500` |

## Quick Install (Debian/Ubuntu)
```bash
sudo apt install -y fcrackzip bkcrack john hashcat binwalk
pip install stegoveritas stegolsb
```

## Discipline Checklist
- [ ] Try rockyou wordlist FIRST (30s max)
- [ ] If no hit, try 1-5 char brute (2 min max)
- [ ] If still no hit, check for known plaintext → bkcrack
- [ ] ALWAYS verify by full decompression, not just CRC
- [ ] NEVER write custom C/Python brute-forcers — existing tools are faster and tested

## References
- `references/hackerverse-june2026-easy-peasy-lemon-squeezy.md` — real example where rockyou found `tomatoes`
- `references/scope-trace-bmp-stego.md` — challenge using this pattern
- `fcrackzip --help`, `bkcrack --help`, `john --help`