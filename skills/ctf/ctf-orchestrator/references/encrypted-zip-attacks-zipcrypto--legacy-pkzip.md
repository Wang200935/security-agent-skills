# Encrypted ZIP Attacks (ZipCrypto / Legacy PKZIP)

When a CTF challenge ships an encrypted ZIP (legacy ZipCrypto, `method=8` + `flag_bits & 1`) alongside a sibling **unencrypted** archive that shares structure with the encrypted file's payload, the unencrypted archive is a known-plaintext oracle.

### Pattern A — Deflate-compressed ELF/Mach-O in encrypted ZIP

If the encrypted archive holds a single deflate-compressed Linux binary (`imgconv`/`solver`/etc.), the plaintext stream starts with:

```
78 9C  [deflate block header]  7F 45 4C 46 02 01 01 00 00 00 00 00  ...
^^^^^^^^                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
zlib CMF+FLG                  ELF64 magic (Linux, LSB, current version)
```

Run `bkcrack` with ELF magic asserted at the correct offset:

```bash
# 12-byte ZipCrypto header + 2-byte zlib header = offset 2 from start of encrypted data
~/homebrew/bin/bkcrack -C encrypted.zip -c entryname \
  -x 2 7f454c46020101010000000000000000 -o 0
```

**Important**: `-o` is the offset of the plaintext **relative to the ciphertext without the encryption header** (so `0` means "right after the 12-byte ZipCrypto header"). bkcrack needs ≥ 12 contiguous bytes of known plaintext and runs for ~10–30 minutes on modern CPUs. If the bkcrack process is killed or interrupted, use `--continue-attack <checkpoint>` to resume from the saved checkpoint rather than restarting.

### Pattern B — C-based brute force with full verification

`fcrackzip` 1–5 char brute on a real CTF ZIP often exceeds the 300s/600s terminal timeout, and worse, **false positives are easy**: the zlib header check `(CMF*256 + FLG) % 31 == 0` matches about 1 in 256 random pairs. Always verify a candidate by **fully decrypting and `zlib.decompress`ing** the resulting deflate stream and comparing its length to the uncompressed size in the ZIP central directory. A C brute forcer (`scripts/zip_crack.c`, 4-digit numeric) runs 10000 candidates in 0.6s, which is the right baseline for adding a verification step. Never declare a password "found" without a successful zlib decompression to the expected uncompressed length.

### Pattern C — Check if the challenge provides the password itself

CTF organizers frequently leak the password into adjacent artifacts. Look in: image EXIF/comments, BMP/PNG tEXt chunks, PDF metadata, archive ZIP comments, the unencrypted sibling archive's file names, or even the challenge description text. Brute forcing a CTF-distributed ZIP without first scanning every artifact for a leaked password wastes hours.

See `references/encrypted-zip-attacks.md` for the full attack matrix (false-positive rates, when to use bkcrack vs brute force vs dictionary, how to extract `comp_size` and identify the encryption header offset).
