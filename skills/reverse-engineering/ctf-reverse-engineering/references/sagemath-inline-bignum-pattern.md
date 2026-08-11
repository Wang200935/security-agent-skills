# SageMath / Cython Whole-Program Binary Pattern

## Triage Indicators

| Signal | What it means |
|---|---|
| `.rodata` < 100 bytes (only `Correct!`/`Fail...`/`Input flag:`/prefix) | All bignum constants inlined in `.text` |
| PLT imports **only** libc (calloc/abort/exit/fgets/printf/puts/strlen/strncmp/strcspn/getrlimit/setrlimit/fflush) | No external GMP/NTL/Python libs |
| Build path leak in `.dynstr`: `~/miniconda3/envs/sage/lib` | Compiled with conda-forge SageMath toolchain |
| `.text` > 2 MB | Entire Sage ring/field arithmetic statically linked |
| `strings` finds **zero** decimal/hex integer literals > 12 chars | Constants encoded as `movabsq` immediates or data in `.eh_frame_hdr` |
| Indirect `callq *%rcx` / `*%rdx` throughout checker | Dispatch via per-type descriptor tables (vtable-like) |
| Each element = 2-quad `[vtable_ptr, value_ptr]` | Sage element representation |
| Operations followed by `test %rax,%rax` + `jns`/`js` | Exception-like state machine for Sage `try/except` |

## Callback Dispatch Pattern

```asm
; success callback registration (0x2169b3: puts "Correct!" ; exit 0)
leaq 0xab5d(%rip), %rdx   # -> 0x2169b3
movabsq $-0x8000000000000000, %rax
orq %rdx, %rax            ; tagged pointer
callq *%rcx

; fail callback registration (0x2169dc: puts "Fail..." ; exit 1)
leaq 0xab17(%rip), %rdx   # -> 0x2169dc
...
callq *%rcx
```

## Why macOS arm64 Cannot Host Symbolic Execution for These

| Blocker | Detail |
|---|---|
| Binary is x86-64 Linux ELF | macOS arm64 kernel cannot execve it natively |
| Docker Desktop (Apple Silicon) | Runs **aarch64** Linux VM — no x86-64 emulation by default |
| QEMU user-mode `qemu-x86_64` | Available via `colima` + `binfmt_misc` registration (`update-binfmts --enable qemu-x86_64`) |
| `gdb` / `ptrace` under QEMU | **Not supported** — `gdb` attach fails with `ptrace: Function not implemented` |
| `angr` on macOS arm64 | No pre-built wheels; building from source takes > 30 min and often fails on `pyvex`/`unicorn` compilation |
| `angr` inside x86-64 container | Works but needs full x86-64 userspace (use `--platform linux/amd64` image with `qemu-user-static` binfmt already registered in host) |

**Only viable path for symbolic execution**: x86-64 Linux machine (bare metal or CI runner) OR a Docker host with native x86-64 kernel (not Apple Silicon).

## Constant Extraction Technique

1. **`movabsq` scan** across `.text`:
   ```python
   # pattern: 48 B8..BF + 8 bytes = movabsq r64, imm64
   # pattern: 48 BA + 8 bytes = movabsq rdx, imm64
   ```
2. **Sparse data in `.eh_frame_hdr` / `.eh_frame`**: Look for sequences of 8 `movabsq` with regular spacing (0x40 bytes) — these are 512-bit multi-precision integers split across 8 registers (little-endian order: r0 = LSB).
3. **Descriptor tables** at fixed offsets (e.g., 0xd5bf2, 0xd5d0a, …) are **not** constants — they are C++ exception/Sage type descriptors.

## Three 512-bit Constants from This Session

```
# Base 0x222584 (a)
reg0: 0xb868ffebfe450004
reg1: 0xb968ffec00e70004
reg2: 0xba68ffec03890004
reg3: 0xbb68ffec062b0004
reg4: 0xbc68ffec08cd0004
reg5: 0xbd68ffec0b6f0004
reg6: 0xbe68ffec0e110004
reg7: 0xbf68ffec10b30004

# Base 0x226584 (b)
reg0: 0xb868ffefcf640005
...

# Base 0x22a584 (c)
reg0: 0xb868fff4070e0006
...
```

**Differences** (`b-a`, `c-b`) are NOT clean powers — they are Hensel-lifted polynomial roots at successive p-adic precisions.

## Attack Shape for Hensel Lifting Crackmes

1. **Identify the polynomial** `f(x)` — search checker for `PolynomialRing`, `x^N` coefficients, or loop patterns computing `f(x) % p^k`.
2. **Extract the highest-precision constant** (here `c` at 0x22a584) — this is the fully lifted root `r_k`.
3. **Descend precisions**: `r_{k-1} = r_k mod p^{k-1}`, `r_{k-2} = r_{k-1} mod p^{k-2}`, … until `p^1`.
4. **Solve `f(x) ≡ 0 (mod p)`** by brute force (p is usually small prime: 2, 3, 5, 7, 11…).
5. **Re-lift** using Hensel lemma to verify the chain matches `a → b → c`.
6. **The 256-bit flag** is the solution at the final precision (here 32 bytes = 256 bits).

## Tools That Worked in This Session

| Tool | Role |
|---|---|
| `colima start --arch aarch64` + `update-binfmts --enable qemu-x86_64` | x86-64 execution on macOS |
| `docker run --platform linux/amd64` | Binary execution & strace/ltrace alternative |
| Python `struct.unpack` + raw binary scan | Constant extraction without disassembler |
| `gmpy2` / SageMath (on x86-64) | Polynomial root solving & Hensel lifting |

## Failed Tools (Documented for Next Time)

| Tool | Failure Mode |
|---|---|
| `angr` pip install on macOS arm64 | No wheel; pyvex build hangs > 30 min |
| `gdb` in QEMU container | `ptrace: Function not implemented` |
| `ltrace`/`strace` in QEMU container | Same ptrace issue |
| `objdump` in QEMU container | SIGSEGV in qemu-user |

## References

- Session analysis: `R3CTF` "lift" challenge (SageMath Hensel lifting crackme)
- Flag format: `R3CTF{` + 32 chars + `}` (39 total)
- Inner 32 bytes = 256-bit integer input to checker at `0x20c195(0, &struct_32bytes)`