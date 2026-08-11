/*
 * zip_crack.c - C-based ZipCrypto brute forcer for CTF ZIPs.
 *
 * Tries 4-digit numeric passwords ("0000".."9999") against a target ZIP.
 * For each candidate, decrypts the first 14 bytes (12-byte ZipCrypto header
 * + 2 bytes after) and prints candidates where those 2 bytes look like a
 * valid zlib CMF/FLG header.
 *
 * CRITICAL: The CMF/FLG check is necessary but NOT sufficient. About 0.2%
 * of random 2-byte pairs pass it. Always pass candidates through full
 * zlib.decompress verification. See ../references/encrypted-zip-attacks.md
 * section 3 for details.
 *
 * Compile: cc -O3 -o zip_crack zip_crack.c
 * Run:     ./zip_crack
 *
 * Before running, update the two hardcoded paths/offsets for your ZIP:
 *   - ENC_PATH: path to the encrypted ZIP
 *   - ENC_OFFSET: byte offset where the 12-byte ZipCrypto header starts
 *     (typically 30 + filename_len + extra_len from the local file header)
 *   - COMP_SIZE: compressed size from the local file header
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

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

int main(int argc, char **argv) {
    init_crc_table();

    /* === CONFIG (edit for your ZIP) === */
    const char *ENC_PATH = "/Users/wang/ctf-training/forensics/hidden-message/tool.zip";
    const long ENC_OFFSET = 65;     /* byte offset of encrypted data in ZIP */
    const size_t COMP_SIZE = 331109; /* compressed size including 12-byte header */

    FILE *f = fopen(ENC_PATH, "rb");
    if (!f) { perror("open"); return 1; }
    fseek(f, ENC_OFFSET, SEEK_SET);
    static uint8_t enc[COMP_SIZE];
    if (fread(enc, 1, COMP_SIZE, f) != COMP_SIZE) { perror("read"); return 1; }
    fclose(f);

    char pwd[5] = {0};
    long long tried = 0;
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
        uint8_t cmf = dec[12], flg = dec[13];
        if ((cmf & 0xf) == 8 && (((cmf << 8) | flg) % 31) == 0) {
            printf("Candidate: %s cmf=%02x flg=%02x\n", pwd, cmf, flg);
            fflush(stdout);
        }
        tried++;
        if (tried % 1000000 == 0) fprintf(stderr, "tried %lld\n", tried);
    }
    return 0;
}