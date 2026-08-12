# Universal Commands

```bash
file <artifact>
sha256sum <artifact>
strings -a <artifact> | head
xxd -l 256 <artifact>
binwalk <artifact>
exiftool <artifact>
```

On macOS, install missing common tools with `~/homebrew/bin/brew` where appropriate.

**Cross-compilation for Linux targets**: use zig as a zero-setup cross-compiler:
```bash
~/homebrew/bin/brew install zig
~/homebrew/bin/zig cc -target x86_64-linux-musl -static -O2 -o exploit exploit.c
```
Produces fully static Linux binaries from macOS. Note: zig's clang rejects Intel-syntax inline assembly — use AT&T syntax (`movq %0, %%rsp` not `mov rsp, %0`).
