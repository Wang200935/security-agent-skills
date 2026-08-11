# Reverse Engineering CTF Playbook

## Universal Binary Triage

```bash
file chall
sha256sum chall
strings -a chall | head -200
objdump -x chall 2>/dev/null | head
```

For ELF, also check security flags when tools are available: PIE, NX, RELRO, canary.

## Static-First Strategy

1. Search strings for flag fragments, prompts, error messages, crypto constants.
2. Identify main and input validation functions.
3. Follow comparisons, memcmp/strcmp, hash checks, loops over user input.
4. Rename variables/functions in decompiler as understanding improves.
5. Extract constants and reimplement the check in Python.

## Dynamic Strategy

- Break on input comparison functions.
- Inspect transformed input and expected values.
- Patch conditional jumps only to explore behavior, not as the final solve unless required.
- Watch memory buffers around validation.

## Common Patterns

- XOR/add/sub/rol/ror encoded flag or key.
- Per-character constraints solvable with z3.
- Hash compare with hardcoded digest.
- Anti-debug checks: ptrace, timing, environment, process name.
- Custom VM: bytecode dispatcher, opcode table, stack/register state.
- Packed/self-modifying code: dump after unpacking.

## APK/JAR

- Decompile Java/Kotlin with JADX.
- Inspect manifest, resources, native libraries.
- Search for URLs, keys, Base64, crypto calls.
- If native lib exists, reverse it separately.

## WASM

- Inspect JS glue for exported functions and memory access.
- Convert wasm to wat or decompile with available tools.
- Look for validation exports and constants.
