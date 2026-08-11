# Running x86-64 Linux Binaries on macOS arm64 via Colima + qemu-user-static

## Prerequisites

```bash
brew install colima
# Colima provides Docker daemon + aarch64 Linux VM on macOS
```

## Setup (One-time)

```bash
# Start colima with aarch64 VM (native on Apple Silicon)
colima start --arch aarch64 --cpu 4 --memory 8 --disk 30

# Inside the colima VM, register qemu-x86_64 binfmt for x86-64 execution
colima ssh -- bash -c '
  sudo apt-get update -qq
  sudo apt-get install -y -qq qemu-user-static binfmt-support
  sudo update-binfmts --enable qemu-x86_64
'
```

## Verification

```bash
# Test that x86-64 binary runs
docker run --rm --platform linux/amd64 -v /path/to/binary:/chall:ro ubuntu:22.04 /chall <<< "test input"
```

## How It Works

| Layer | Technology |
|---|---|
| Host | macOS (arm64) |
| Colima VM | aarch64 Linux (native, no emulation overhead) |
| qemu-user-static | x86-64 user-mode emulation inside VM |
| binfmt_misc | Kernel handler that intercepts ELF x86-64 execve and routes to qemu-x86_64 |
| Docker `--platform linux/amd64` | Pulls amd64 image; qemu-user-static executes the binaries |

## Limitations & Gotchas

| Operation | Supported? | Notes |
|---|---|---|
| Basic execution (`/chall`) | ✅ | Full syscall translation |
| `strace` / `ltrace` | ❌ | Requires `ptrace` — **not implemented in qemu-user** |
| `gdb` attach | ❌ | `ptrace: Function not implemented` |
| `objdump` / `readelf` on binary | ✅ | Works on host (static analysis) |
| Symbolic execution (`angr`) | ❌ in container | Use native x86-64 machine or CI runner |
| Network syscalls | ✅ | Full translation |
| File I/O | ✅ | Host filesystem via Docker volume mount |

## Docker Image Selection

| Image | Size | Notes |
|---|---|---|
| `ubuntu:22.04` | ~80 MB | Good base, `apt` works |
| `debian:bookworm` | ~80 MB | Slightly newer packages |
| `alpine` | ~5 MB | **No glibc** — SageMath binaries need glibc |
| `gcc` / `buildpack-deps` | ~500 MB | Includes build tools if you need `gdb`/`strace` (won't work anyway) |

## Recommended Workflow for CTF binaries

```bash
# 1. Static analysis on host (fast, no emulation)
objdump -d chall > chall.dis
strings -t x chall
python3 -c "import struct; ..."  # raw binary parsing

# 2. Dynamic execution in container (for I/O traces)
docker run --rm --platform linux/amd64 -v $(pwd):/data:ro ubuntu:22.04 \
  bash -c 'cp /data/chall /tmp/ && /tmp/chall <<< "R3CTF{...}"'

# 3. If you need gdb/angr → use a real x86-64 Linux machine or GitHub Actions runner
```

## Why Not Docker Desktop?

Docker Desktop on Apple Silicon also runs an aarch64 VM, but it **does not register qemu-x86_64 binfmt by default** and the VM is harder to SSH into for `update-binfmts`. Colima is lighter and more scriptable.

## Why Not QEMU System Emulation (`qemu-system-x86_64`)?

`qemu-system` emulates the entire kernel + hardware — extremely slow for userspace binaries. `qemu-user-static` only translates syscalls, near-native speed for compute-bound workloads.

## Reference

This setup was used to execute the **R3CTF 2024 "lift" SageMath binary** (2.7 MB, x86-64, libc-only PLT, 512-bit Hensel lifting constants) on macOS arm64 for dynamic validation of flag format and I/O behavior.