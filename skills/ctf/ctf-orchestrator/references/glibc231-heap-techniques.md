# glibc 2.31 Heap Exploitation Techniques

## Environment
- Ubuntu 20.04, glibc 2.31-0ubuntu9.17
- 64-bit, PIE, FULL RELRO, NX, Stack Canary

## Tcache Structure

### Layout
- `tcache_perthread_struct` at `heap_base + 0x10` (after chunk header)
- `counts[64]` at offset 0 (1 byte each)
- `entries[64]` at offset 64 (8 bytes each, LIFO linked list)
- Total struct size: 576 bytes (0x240)

### Bin Index Formula
**CRITICAL**: On this glibc build, the formula is:
```
entry_index = chunk_size / 16 + 6
```
NOT the standard `chunk_size / 16 - 1`.

Verified empirically:
- chunk 0x30 → entry 9 (0x30/16 + 6 = 3 + 6 = 9) ✓
- chunk 0x50 → entry 11 (0x50/16 + 6 = 5 + 6 = 11) ✓
- chunk 0x210 → entry 39 (0x210/16 + 6 = 33 + 6 = 39) ✓

### Reading Tcache State via /proc/1/mem (Docker)
```bash
TS=0x55555555b010  # heap_base + 0x10
# Read counts
dd if=/proc/1/mem bs=1 skip=$TS count=64 2>/dev/null | od -A x -t x1z
# Read entries[idx]
dd if=/proc/1/mem bs=1 skip=$((TS + 64 + idx*8)) count=8 2>/dev/null | od -A x -t x8
# Read chunk header (prev_size + size)
dd if=/proc/1/mem bs=1 skip=$((chunk_addr)) count=16 2>/dev/null | od -A x -t x8
```

## Heap Overflow via MIME Parser

### Vulnerability Pattern
When `parse_mime()` fills a data buffer to exactly 0x200 bytes and the next byte is `\r` (0x0d), boundary mismatch triggers a memcpy past the buffer. The copy guard uses `jbe` (unsigned ≤) so it only fires when `data_index > buffer_size`. Binary patching the `jbe` to NOPs re-enables the overflow.

### Trigger Construction
```
SOAP body = 0x200 bytes + "\r\n--" + boundary_match_chars + mismatched_char
```
- `\r` must be at position 0x200 in the data buffer (AFTER 512 bytes stored)
- `\r` is NOT stored in data_buf — it triggers boundary detection
- Boundary in Content-Type header MUST use raw bytes (NOT escaped `\xNN`)
- Non-printable bytes (0x00-0x0c, 0x0e-0x1f, 0x7f-0xff) work as boundary bytes
- CANNOT use 0x0d (\r) or 0x0a (\n) in boundary — they trigger premature detection

### Copy Loop First-Byte Pitfall (CRITICAL)
The copy loop at 0x29b8 uses `xor edx, edx` + `jmp` over the first `movzx`, making the **first byte always 0x00**. All subsequent bytes shift by +1 offset from naive calculation.

### Corrected Overflow Byte Layout (count=N, data_index=0x200)
```
data_buf[0x200]       = 0x00 (fixed, from xor edx,edx)
data_buf[0x201]       = 0x2d ('-')         — line_buf[1] prefix byte 2
data_buf[0x202]       = 0x2d ('-')         — line_buf[2] prefix byte 3
data_buf[0x203]       = boundary[0]         — line_buf[3] first boundary char
data_buf[0x204..0x207]= boundary[1..4]
data_buf[0x208]       = boundary[5]         — TOP CHUNK SIZE[0] (0x51 original)
data_buf[0x209]       = boundary[6]         — SIZE[1] (controllable for count≥10)
data_buf[0x20a]       = boundary[7]         — SIZE[2] (touch=past heap → crash)
data_buf[0x20b]       = mismatch_byte       — SIZE[3] (from line_buf[11])
data_buf[0x20c..0x20f]= original bytes      — SIZE[4..7] (unchanged, 0x00)
```

### Maximum Safe Overflow: count=10
Overflowing past offset 0x209 (SIZE[1]) into 0x20a causes `set_foot` in glibc's `_int_realloc` to write past the heap boundary. **Count=10 is the maximum safe overflow** — controls prev_size + SIZE[0..1]. SIZE[0] must be preserved as 0x51 (original LSB) to avoid immediate crash. Only SIZE[1] (1 byte) is freely controllable.

### Keeping Valid Chunk Size
- SIZE[0] must be 0x51 (original top chunk LSB with PREV_INUSE=1)
- SIZE[1] replaces the problematic 0x0d (\r) with 0x0e or higher
- For glibc 2.31, top chunk size formula: `0x00000000 + SIZE[3..0] + original_bytes[4..7]`
- Total size must keep `set_foot` address within heap boundary (~0x21000 for default 132KB heap)

## Common Pitfalls

### Content-Type Boundary
- HTTP Content-Type `boundary="..."` value is compared byte-for-byte against MIME body separators
- Using `\xNN` escapes in the header string does NOT produce raw bytes
- Solution: send raw bytes in the Content-Type header line (no escaping)
- Non-printable bytes are fine as long as they're not CR (0x0d) or LF (0x0a)

### Overflow Position
- Adding a CMD prefix to SOAP shifts the overflow trigger position
- Must recalculate PAD: `PAD = 0x1FF - (CMD_LEN + BASE)`
- Otherwise buffer expands to 0x400 before trigger, overflow targets wrong location

### Tcache Bin Confusion
- Default formula `(chunk_size/0x10) - 1` does NOT match this glibc build
- Always verify with /proc/1/mem dump before constructing exploit

### Non-MIME Soap Attributes
- dispatch_soap may NOT allocate soap strings for unknown/arbitrary XML attributes
- Cannot rely on non-MIME requests to populate small tcache bins (0x20, 0x30)
- Use MIME node allocations (0x40 → 0x50 chunks → bin 11) instead
