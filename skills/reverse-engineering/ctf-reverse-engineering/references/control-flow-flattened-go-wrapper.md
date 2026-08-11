# Control-Flow Flattened VM Wrapper with Embedded Go Binary

## Pattern Overview

A CTF challenge binary that:
1. Uses **control-flow flattening** with magic constant dispatch (switch-on-magic-values pattern)
2. Contains a massive `.rodata` section (~12MB) with **custom bytecode encoding**
3. **Decodes** the bytecode in-memory via a simple VM interpreter
4. **Writes** the decoded payload to `memfd_secret()` + `fchmod()` + `execveat()`
5. The payload is a **Go binary** (module `ops/client`) acting as a C2 client/implant

## Outer Wrapper Analysis (WhC2 v0.1)

### Binary Properties
- 64-bit ELF, PIE, stripped, dynamically linked, Go 1.24.2 (inner payload)
- ~12MB `.rodata` section with low entropy (structured bytecode)
- Stripped, minimal symbols

### Control-Flow Flattening
- Dispatch loop at `0x1420` compares `eax` against magic constants
- Each handler updates state and jumps back to dispatch
- Magic constants used: `0x600DB9CE`, `0x6802E03D`, `0x2712870F`, `0xE7B816A7`, `0xDCA26958`, `0xCDBD1A38`, etc.
- Handlers implement: decode loop, write to memfd, fchmod, execveat

### Bytecode Decoding (at `0x18E7-0x191D`)
```assembly
# r13 = rodata base + 4 (skip header)
# r14 = chunk count (capped at 0x1000)
# rdx = index
movzbl  (%r13,%rdx,2), %eax      # byte1
movzbl  1(%r13,%rdx,2), %ecx     # byte2
shlb    $4, %al                  # byte1 << 4
andb    $0xf, %cl                # byte2 & 0xF
orb     %al, %cl                 # combine
movb    %cl, 0x250(%rsp,%rdx)    # output buffer
inc     %rdx
cmp     %r14, %rdx               # loop
jne     decode_loop
```

**Encoding**: Two bytes (values 0x80-0x9F) → one decoded byte:
```
decoded = ((byte1 << 4) | (byte2 & 0x0F)) & 0xFF
```

### Header
First 4 bytes of rodata: `01 00 02 00` (two uint16: count=1, type=2)

### Memory Execution
```
memfd_secret(0)          # syscall 319
write(fd, decoded, size)
fchmod(fd, 0x1c0)        # 0700
execveat(fd, "", argv, envp, AT_EMPTY_PATH)  # syscall 322
```

### XOR Decryption (at `0x1DAB-0x1DBE`)
Simple single-byte XOR loop used on 6-byte string at `.data+0x10`:
```
key = 0xBF
"cache" = DC DE DC D7 DA BF ^ 0xBF
```

## Inner Go Binary Analysis (c2_decoded)

### Module Info
```
path: ops/client
build: -buildmode=exe -compiler=gc -trimpath
Go: 1.24.2, CGO_ENABLED=1
```

### Key Functions (from pclntab)
| Function | Address | Purpose |
|---|---|---|
| `main.main` | 0x650CA0 | Entry: openConfig → cycle (15s sleep) |
| `main.openConfig` | 0x64F4A0 | Load config, call `run_digest` |
| `main.endpoint` | 0x64FB00 | Parse C2 endpoint URL |
| `main.postJSON` | 0x64FCE0 | HTTP POST beacon |
| `main.pullFile` | 0x64FF20 | Download file from C2 |
| `main.pushFile` | 0x650300 | Upload file to C2 |
| `main.runLine` | 0x6506C0 | **Execute commands** ("getfile", "putfile") |
| `main.cycle` | 0x650980 | Main loop: endpoint → beacon → runLine |
| `main._Cfunc_open_box` | 0x64DE60 | cgo: decrypt config box |
| `main._Cfunc_run_digest` | 0x64DFA0 | cgo: compute HMAC/digest |

### C2 Protocol (JSON)
```json
{
  "up": "base64_encoded_data",
  "cmd": "command_string",
  "base": "base64_encoded_data", 
  "down": "task_payload"
}
```

### Embedded Key
At file offset `0x3DC` (start of .data):
```
SJoPw5xCRp-P9c84bjo6/bzxnj-mPBiCLFVbjQvnB/8XnXR_WVQ5iIRmQY8sNt/SavZgSt2UOdC8bEkX_oX
```
URL-safe Base64 → 62 bytes (likely AES-256 key + IV + HMAC key or similar)

## Solving Strategy

1. **Static decode outer wrapper**: Write decoder for the bytecode → extract Go binary
2. **Parse Go pclntab**: Map function names to addresses (see `scripts/go_pclntab_parser.py` concept)
3. **Identify C2 logic**: Focus on `runLine`, `postJSON`, `cycle`
4. **Extract embedded key**: Base64 decode the 62-byte string
5. **Reverse cgo functions**: `open_box` (config decryption), `run_digest` (auth)
6. **Simulate or intercept**: 
   - Run in VM with network capture
   - Or patch `endpoint` to point to controlled server
   - Or call `runLine` directly with crafted input ("getfile flag.txt")

## Tools & Scripts

### Outer Wrapper Decoder
```python
def decode_rodata(rodata_bytes):
    """Decode the two-byte encoding to payload."""
    assert rodata_bytes[:4] == b'\x01\x00\x02\x00'
    out = bytearray()
    for i in range(4, len(rodata_bytes) - 1, 2):
        b1 = rodata_bytes[i]
        b2 = rodata_bytes[i + 1]
        out.append(((b1 << 4) | (b2 & 0x0F)) & 0xFF)
    return bytes(out)
```

### Go pclntab Function Finder
See `scripts/go_pclntab_parser.py` concept — scan `_func` structs at `pclnOff` for target names.

## Mitre ATT&CK Mapping
- T1027.006: Obfuscated/Stored Files - Virtual Machine Software Protection
- T1055.013: Process Injection - Memfd Secret
- T1105: Ingress Tool Transfer (C2 download)
- T1059: Command and Scripting Interpreter

## References
- Session: WhC2 v0.1 (July 2026)
- Challenge: "How to hack a hacker, this is a good question!"
- C2 restart every 15 minutes (matches `cycle` 15s sleep in main)