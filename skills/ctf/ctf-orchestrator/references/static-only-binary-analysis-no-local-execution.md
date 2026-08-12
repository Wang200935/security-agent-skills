# Static-Only Binary Analysis (No Local Execution)

When the challenge binary is for a different architecture than the host (e.g., Linux x86-64 binary on macOS ARM64) and local execution tools (qemu-user, Docker) are unavailable:

1. **Strings first**: `strings binary | grep -iE '<keywords>'` for protocol hints, function names, error messages, format strings.
2. **Symbol table**: `nm binary` to map function addresses; cross-reference with `objdump -d`.
3. **Security features via ELF parsing**: Python script to check PIE (e_type), RELRO (PT_GNU_RELRO vs .got boundaries), stack canary (`__stack_chk_fail` in imports), NX (GNU_STACK segment flags).
4. **Disassemble per-function**: `objdump -d -M intel binary | sed -n '/<func>:/,/^$/p'` to isolate each function. Build a map: context struct offsets, dispatch table, parser logic.
5. **Read-only data**: `objdump -s -j .rodata binary` to extract format strings, SOAP/XML templates, protocol constants that reveal handler structure.
6. **Trace data flow from input to output**: For each handler, follow `recv`/`read` → buffer → parsing → response `send`. The vulnerability is almost always at the parsing stage where bounds checks are missing or incorrect.
7. **Validate remotely**: Once the vulnerability hypothesis is formed, script the remote interaction to confirm (send crafted input, observe crash vs normal response, measure response differences that might indicate leaks).
