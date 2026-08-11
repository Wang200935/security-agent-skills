# Encrypted ZIP Attack Reference

When a CTF challenge provides a ZIP file encrypted with legacy PKZIP ZipCrypto (`method=8` + flag bit 0 set), this reference is the practical attack matrix. Covers detection, bkcrack known-plaintext, brute force, and the false-positive trap.

## 1. Confirm It Is ZipCrypto (Not AES or Fake Encryption)

```python
import zipfile
with zipfile.ZipFile('encrypted.zip') as z:
    for info in z.infolist():
        print(info.compress_type, info.flag_bits, info.filename)
        # ZipCrypto: method=8, flag_bits has bit 0 (value & 1 == 1)
        # WinZip AES: extra field tag 0x9901 present in info.extra
        # Fake encryption: bit 0 set but data has no real encryption header
```

A real ZipCrypto header in the encrypted data stream is 12 bytes. After those 12 bytes, the deflate (or stored) stream starts. `comp_size` in the local file header includes the 12-byte encryption header, so the actual deflate stream is `comp_size - 12` bytes long.

## 2. Attack Decision Matrix

| Situation | Attack |
|---|---|
| Encrypted ZIP holds a deflate-compressed Linux ELF | bkcrack with ELF magic at offset 2 (after 12-byte ZipCrypto header + 2-byte zlib header) |
| Encrypted ZIP holds a stored (no-compression) file with any plaintext known | bkcrack directly |
| Plaintext unknown; password is short (<=6 digits) | C-based brute force with full zlib verification |
| Plaintext unknown; password might be a word | `fcrackzip -D -u -p <wordlist>` |
| Brute force exceeds 600s and no `comp_size` is large | Stop, switch to bkcrack or external research |
| Sibling unencrypted archive exists with the same artifact | Inspect for password hints / known plaintext |
| README/description mentions a password hint | Try it first |

## 3. False-Positive Trap (CRITICAL)

The ZipCrypto decryption output's first byte after the 12-byte header is the start of the deflate stream. A deflate stream begins with a 2-byte zlib header `CMF FLG` where:

- `CMF` low 4 bits must equal 8 (deflate)
- `(CMF << 8 | FLG) % 31 == 0`

For a random 2-byte pair, the probability of satisfying both constraints is `(16 / 256) * (1 / 31) ≈ 0.2%`. So in a 10000-candidate brute force you expect ~20 false positives that "look" like valid zlib headers.

**Never declare a password found based on the header check alone.** Always fully decrypt and decompress, then compare the resulting length to `uncomp_size` in the ZIP central directory:

```python
import zlib
decrypted_full = decrypt_all(ciphertext, password)  # 12-byte header + comp data
comp_data = decrypted_full[12:]
uncomp_size = 743432  # from the central directory
try:
    out = zlib.decompress(comp_data, -15)
    if len(out) == uncomp_size:
        print(f'FOUND pwd={password!r}')
        # Further verify the first 4 bytes are a known magic
except zlib.error:
    pass  # not the right password
```

## 4. C Brute Force Skeleton (4-digit numeric, ~0.6s for 10000 candidates)

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

static uint32_t crc_table[256];
static void init_crc_table(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >> 1)) : (c >> 1);
        crc_table[i] = c;
    }
}
static inline uint32_t crc32_byte(uint32_t c, uint8_t b) {
    return crc_table[(c ^ b) & 0xff] ^ (c >> 8);
}
static inline void decrypt_byte(uint32_t *k, uint8_t *out) {
    uint32_t tmp = (k[2] & 0xffff) | 2;
    uint32_t res = (tmp * (tmp ^ 1));
    res = (res >> 16) & 0xff;
    k[0] = crc32_byte(k[0], res);
    k[1] = ((k[1] + (k[0] & 0xff)) * 134775813 + 1);
    k[2] = crc32_byte(k[2], (k[1] >> 24) & 0xff);
    *out = (uint8_t)res;
}

int main(void) {
    init_crc_table();
    static uint8_t enc[331109];
    FILE *f = fopen("encrypted.zip", "rb");
    fseek(f, 65, SEEK_SET);  /* offset of encrypted data; depends on local header size */
    fread(enc, 1, sizeof(enc), f);
    fclose(f);

    char pwd[5] = {0};
    for (int a='0'; a<='9'; a++)
    for (int b='0'; b<='9'; b++)
    for (int c='0'; c<='9'; c++)
    for (int d='0'; d<='9'; d++) {
        pwd[0]=a; pwd[1]=b; pwd[2]=c; pwd[3]=d;
        uint32_t k[3] = { 305419896, 591751049, 878082192 };
        for (int i = 3; i >= 0; i--) k[0] = crc32_byte(k[0], pwd[i]);
        uint8_t dec[14];
        for (int i = 0; i < 14; i++) {
            uint8_t ks;
            decrypt_byte(k, &ks);
            dec[i] = enc[i] ^ ks;
        }
        /* dec[12..13] = CMF, FLG */
        if ((dec[12] & 0xf) == 8 && (((dec[12] << 8) | dec[13]) % 31) == 0) {
            printf("Header-match: %s cmf=%02x flg=%02x\n", pwd, dec[12], dec[13]);
        }
    }
    return 0;
}
```

Compile and run:
```bash
cc -O3 -o zip_crack zip_crack.c
./zip_crack | tee /tmp/brute.log
```

The "Header-match" output is **only a candidate**. Pass each to Python's `zlib.decompress` for full verification.

## 5. bkcrack Known-Plaintext for ELF Binaries

If the encrypted ZIP holds a single deflate-compressed ELF binary:

```bash
# 12-byte ZipCrypto header + 2-byte zlib header = first plaintext byte at offset 2 (after the 12-byte header, which is at the start of comp_size data; bkcrack -o is relative to ciphertext AFTER the 12-byte header)
~/homebrew/bin/bkcrack -C tool.zip -c imgconv \
  -x 2 7f454c46020101010000000000000000 -o 0
```

The 12-byte ELF magic for Linux x86-64 ELF little-endian:
```
7F 45 4C 46 02 01 01 00 00 00 00 00 00 00 00 00
```

bkcrack requires at least 12 contiguous bytes of known plaintext. The first 12 bytes above are sufficient. The `-x 2 <hex>` flag asserts those 16 bytes at offset 2 within the ciphertext (offset 0 = right after the 12-byte ZipCrypto header).

bkcrack typically takes 10–30 minutes on modern hardware. **Save its checkpoint** — kill the process with SIGTERM (not SIGKILL) so it writes the checkpoint, then resume with `--continue-attack <path>`.

Once bkcrack returns the 3 internal keys, decrypt the archive:
```bash
~/homebrew/bin/bkcrack -C tool.zip -c imgconv \
  -k <key0> <key1> <key2> -D decrypted.zip
unzip decrypted.zip
```

## 6. Companion Artifacts as Known-Plaintext

When the challenge ships a sibling unencrypted archive (e.g., `images.zip` alongside `tool.zip`), the unencrypted files' known structure is sometimes a free plaintext source:

- BMP headers always start with `42 4D` (BM) followed by file size, then reserved bytes `00 00 00 00`, then pixel data offset (4 bytes little-endian)
- If the encrypted ZIP holds a copy of the same file (perhaps with extra data appended or stripped), bkcrack can recover the full archive from a 12-byte BMP header snippet

```bash
# 14-byte BMP header (file_size is variable; 0x36 = 54 = typical offset for 8-bit grayscale)
printf '\x42\x4d\x36\x05\x12\x00\x00\x00\x00\x00\x36\x00\x00\x00' > /tmp/bmp.bin
~/homebrew/bin/bkcrack -C encrypted.zip -c image.bmp -p /tmp/bmp.bin -o 0
```

## 7. Realistic False-Positive Numbers (4-digit numeric brute)

| Step | Expected matches |
|---|---|
| Random pairs satisfy zlib CMF/FLG constraint | ~20 / 10000 (0.2%) |
| Those that fully decompress without zlib error | ~0.02 / 10000 (most decompress partially then fail) |
| Decompressed length matches `uncomp_size` exactly | < 0.001 / 10000 |

So in a 4-digit brute with 10000 candidates, expect ~20 "looks like a zlib header" but 0 actual matches. **Header check is necessary, not sufficient.**