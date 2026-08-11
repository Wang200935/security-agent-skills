# CTF Solver Patterns

Reusable patterns to turn observations into scripts/exploits.

## General solver skeleton

```python
#!/usr/bin/env python3
from pathlib import Path

DATA = Path('artifacts/input.txt').read_bytes()
FLAG_PREFIXES = [b'flag{', b'ctf{', b'picoCTF{', b'HTB{']

def score(bs: bytes) -> int:
    printable = sum(32 <= b < 127 or b in b'\n\r\t' for b in bs)
    bonus = sum(p in bs for p in FLAG_PREFIXES) * 100
    return printable + bonus

candidates = []
# append (score, description, bytes)
for sc, desc, out in sorted(candidates, reverse=True)[:20]:
    print(sc, desc, out[:200])
```

## Web exploit skeleton

```python
#!/usr/bin/env python3
import requests

BASE = 'http://target'
s = requests.Session()

r = s.get(BASE + '/')
print(r.status_code, r.text[:200])

# login/register if needed
# r = s.post(BASE + '/login', data={'username':'a','password':'a'})

# exploit request
r = s.get(BASE + '/target')
print(r.status_code)
print(r.text)
```

Patterns:

- Preserve cookies in one `Session`.
- Add helper for CSRF token extraction.
- Print exact status/body snippets.
- Keep payloads as data, not string-concatenated shell commands.

## Oracle exploit skeleton

```python
import functools, requests, time
s = requests.Session()
BASE = 'http://target'

@functools.lru_cache(maxsize=None)
def oracle(x: bytes) -> bool:
    for attempt in range(3):
        try:
            r = s.post(BASE + '/oracle', data={'c': x.hex()}, timeout=5)
            return 'valid' in r.text
        except requests.RequestException:
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError('oracle failed')
```

## XOR solver pattern

```python
def xor(a,b): return bytes(x^y for x,y in zip(a,b))
def single_byte_xor(c):
    return sorted(((score(bytes([b ^ k for b in c])), k, bytes([b ^ k for b in c])) for k in range(256)), reverse=True)
```

For repeating XOR:

- estimate key size by normalized Hamming distance
- transpose blocks
- solve each key byte as single-byte XOR
- score full plaintext

## Linear/affine block-cipher variants

If a challenge removes or neuters the nonlinear layer of a known cipher (for example AES with `SubBytes` as identity), treat the cipher as an affine transform over bytes/bits rather than trying to brute force the original key. With one known plaintext/ciphertext pair, derive the effective constant and invert the same transform on the target ciphertext.

Pattern:

1. Confirm which operations remain: AddRoundKey/XOR, ShiftRows, MixColumns, key schedule.
2. Implement the provided encrypt function exactly.
3. Evaluate encryption under zero/all-known key to model the linear part.
4. Use known `pt -> ct` to recover the missing affine constant/effective key material.
5. Apply inverse transform to target and score for flag prefix.

Do not assume “AES” means standard AES; read `sub_word`, `sub_bytes`, and `rcon` implementations. Identity S-box/RCON often collapses security.

## LFSR-derived stream/key brute-force conventions

For LFSR crypto challenges, many wrong attempts come from convention mismatches, not math. Brute force the small convention space before changing strategy:

- output bit: before or after shift; first or last state bit
- shift direction: left/right
- tap indexing: 0-based vs 1-based; from left vs right
- feedback insertion side
- byte packing: MSB-first vs LSB-first
- key length/rounding when bits are converted to bytes

Build a generator parameterized by those choices, derive candidate keys/keystreams, decrypt, and rank by flag prefix/printability.

## RSA solver pattern

```python
from Crypto.Util.number import long_to_bytes, inverse
from math import gcd, isqrt, prod

def iroot(n, e):
    lo, hi = 0, 1 << ((n.bit_length()+e-1)//e)
    while lo <= hi:
        mid = (lo+hi)//2
        v = mid**e
        if v == n: return mid, True
        if v < n: lo = mid+1
        else: hi = mid-1
    return hi, False

# small e plaintext
m, ok = iroot(c, e)
if ok: print(long_to_bytes(m))

# known factors, including multi-prime RSA
factors = [p, q]  # or [p1, p2, p3, ...]
phi = prod(x - 1 for x in factors)
d = inverse(e, phi)
print(long_to_bytes(pow(c, d, prod(factors))))
```

### Close-cluster / multi-prime RSA

If challenge names hint at clusters/groups or `n` bit length is odd for semiprime RSA, try recursive close-factor splitting, not only `p*q`:

```python
from math import isqrt, prod
from Crypto.Util.number import inverse, long_to_bytes

def fermat_split(n, limit=2_000_000):
    a = isqrt(n)
    if a * a < n: a += 1
    for _ in range(limit):
        b2 = a*a - n
        b = isqrt(b2)
        if b*b == b2:
            x, y = a-b, a+b
            if 1 < x < n and n % x == 0:
                return x, y
        a += 1
    return None

def factor_close(n):
    sp = fermat_split(n)
    if not sp:
        return [n]
    out = []
    for v in sp:
        out.extend(factor_close(v))
    return out

factors = factor_close(n)
assert prod(factors) == n
phi = prod(p-1 for p in factors)
print(long_to_bytes(pow(ct, inverse(e, phi), n)))
```

Verify factors are probably prime before trusting the plaintext. For multi-prime RSA, `phi` is `prod(p_i-1)` when the factors are distinct primes.

## Z3 constraint pattern

```python
from z3 import *
N = 32
xs = [BitVec(f'x{i}', 8) for i in range(N)]
s = Solver()
for x in xs:
    s.add(x >= 32, x <= 126)
# add constraints from binary/source
if s.check() == sat:
    m = s.model()
    print(bytes([m[x].as_long() for x in xs]))
```

## Forensics extraction pattern

```python
from pathlib import Path
blob = Path('artifacts/file').read_bytes()
for marker in [b'flag{', b'ctf{', b'picoCTF{', b'PK\x03\x04', b'\x89PNG\r\n\x1a\n', b'\x1f\x8b\x08']:
    i = blob.find(marker)
    print(marker, i)
```

Patterns:

- Search magic bytes and flag prefixes.
- Carve from offsets into files.
- For images, split channels/planes with Pillow.

### FAT deleted-file recovery

When a disk-image challenge hints that deleted files are recoverable, inspect directory entries before bulk carving. In FAT, deleted short-name entries start with `0xe5`; the first cluster and file size often remain intact.

Quick approach:

1. Decompress image if needed and identify filesystem/partition.
2. Locate deleted directory entries (`0xe5` first byte, filename remnants, size, first cluster high/low).
3. Compute data offset from FAT parameters, recover `size` bytes from the first cluster chain if contiguous.
4. Check recovered bytes for magic (`1f 8b 08` gzip, `PK`, PNG, PDF) and decompress/carve again if nested.

Keep the raw image read-only; write recovered files separately and verify with `file`, `strings`, and flag-prefix search.

## Reverse extraction pattern

```python
# Example: brute inverse transform over constants
const = bytes.fromhex('')
for k in range(256):
    out = bytes((b ^ k) for b in const)
    if b'flag{' in out or all(32 <= c < 127 for c in out):
        print(k, out)
```

Patterns:

- Extract constants from decompiler/disassembly.
- Reimplement check function in Python.
- Invert simple transforms from output backward.
- Use z3 for branching constraints.

## Pwntools exploit skeleton

```python
#!/usr/bin/env python3
from pwn import *

context.binary = exe = ELF('./chall', checksec=False)
context.log_level = 'info'

def start():
    if args.REMOTE:
        return remote('host', 1337)
    return process([exe.path])

io = start()
# io.recvuntil(b'> ')
# io.sendline(payload)
io.interactive()
```

Patterns:

- Add `cyclic` offset proof.
- Separate leak phase from final payload.
- Assert base addresses are page-aligned when possible.
- Test local 5+ times before remote.

### Simple ret2win quick path

For an unstripped/non-PIE binary with a hidden `win`/`flag` function and no canary:

```python
from pwn import *
elf = ELF('./vuln', checksec=False)
win = elf.symbols.get('win') or elf.symbols.get('print_flag')
offset = 40  # prove with cyclic/cyclic_find or source layout: buffer + saved rbp
payload = b'A' * offset + p64(win)
```

On x86_64, a 32-byte stack buffer commonly needs 40 bytes to reach RIP (`32 + saved rbp`). Still prove it; do not assume across compiler options. If remote differs, verify arch/PIE/canary from provided binary and use the same payload over `remote(host, port)`.

### Raw-byte interactive services

Some beginner/general-skill CTF services ask for bytes that cannot be typed safely in a shell or chat UI. Preserve exact bytes and send through Python/pwntools or `printf`, not Unicode text.

```bash
printf '\xff\xff\xff\n' | nc host port
```

For symbol-address prompts, parse the requested symbol name and send packed little-endian addresses:

```python
from pwn import *
elf = ELF('./spellbook', checksec=False)
io = remote(HOST, PORT)
for _ in range(3):
    line = io.recvuntil(b'==> ')
    name = re.search(rb"'([^']+)'", line).group(1).decode()
    io.send(p32(elf.symbols[name]))
io.interactive()
```

Use `p32` for 32-bit ELF addresses and `p64` for 64-bit; prompts may require raw bytes with no trailing newline.

## Pyjail escape pattern

Process:

1. Record allowed characters and blocked substrings.
2. Print/evaluate available globals/builtins if possible.
3. Seek object traversal: class → base → subclasses.
4. Recover file read or command execution primitive.
5. Minify payload to satisfy filter.

Common ideas:

- `().__class__.__base__.__subclasses__()`
- `getattr`/string construction when names blocked
- Unicode confusables/normalization
- exception traceback frames
- format strings and f-string side effects

## Protocol/game automation pattern

```python
from pwn import *
io = remote('host', 1337)
while True:
    data = io.recvuntil(b'> ', timeout=5)
    print(data.decode(errors='ignore'))
    # parse state
    # compute move
    io.sendline(b'move')
```

Patterns:

- Build parser first, solver second.
- Save transcript.
- For mazes/grids: BFS/A*.
- For games: model state transitions and replay.

## Skill update pattern after solve

Patch the domain skill when:

- the decisive trick was absent;
- a command or tool behavior was non-obvious;
- a reusable script emerged;
- a taxonomy branch needs refinement.
