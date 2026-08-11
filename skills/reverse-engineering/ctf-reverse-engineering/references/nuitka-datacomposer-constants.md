# Nuitka DataComposer constants in CTF reversing

Use this when a Nuitka-compiled Python challenge exposes source-level names in a large binary blob but normal ELF symbol/xref searches do not lead directly to function bodies.

## Recognize the pattern

Common indicators:

- packed/inner Linux ELF is stripped and built by Nuitka
- `strings` finds Python module/function names such as `__main__`, `app.py`, `derive_*`, `pack_*`, `PASSWORD_*`, but no useful symbols
- source `.pyc` files are absent
- a large data blob contains chunks with names like `.bytecode`, `__main__`, `__parents_main__`, and package/module names

## DataComposer chunk layout

Modern Nuitka constants blobs can be parsed as consecutive chunks:

```text
chunk_name NUL
uint32_le(part_len)
part bytes
```

The `part` usually starts with:

```text
uint16_le(constant_count)
serialized_constants...
optional '.' end marker
```

Useful tags observed/documented in `nuitka/build/include/nuitka/constants_blob_spec.h`:

- containers: `T` tuple, `L` list, `D` dict, `S` set, `P` frozenset
- integers: `l` positive varint, `q` negative varint, `g/G` large signed integers, `i/I` short signed forms in some versions
- strings/bytes: `a`, `u`, `v` strings; `b`, `c`, `d` bytes; `B` bytearray
- structural: `:` slice, `;` range, `p` previous object, `.` end marker
- code-object specs: `C` in some versions; absence of `C` does not mean source-level constants are useless

## Practical parser workflow

1. Locate a likely constants stream by searching for `.bytecode\0`, `__main__\0`, `__parents_main__\0`, or a module name followed by a plausible little-endian length.
2. Validate chunk boundaries before parsing tags: `name\0 + uint32_le(size)` should land exactly at the next printable chunk name.
3. Parse only enough object types to recover constants first. Do not block on full code reconstruction.
4. Dump module chunks (`__main__`, `__parents_main__`) with stable indices; constants often reveal:
   - crypto parameters (`DIM`, `P/Q`, byte widths)
   - password hashes and allowed alphabets
   - file magic and serialization layout
   - function names and local variable tuples
   - GUI prompts and error strings
5. For native-code recovery after constants extraction, map ELF file offsets to VMAs with program headers, then use Capstone to scan RIP-relative references from executable sections into the constants/data regions.

## Pitfalls

- Do not rely only on printable strings; tag-adjacent bytes encode tuple structure, large integers, byte strings, and varname lists.
- Do not assume code-object specs are present in every constants chunk. Nuitka may keep Python code specs separate from source constants, or compile source functions entirely to native code.
- If `marshal.loads()` fails on `.bytecode` entries, first verify the Python marshal version. Nuitka may embed Python 3.14 bytecode; macOS system `python3` can be 3.9 and will report `bad marshal data`. Try an interpreter matching the embedded version (for example `~/homebrew/bin/python3.14`) before concluding the blob is custom.
- Even when `.bytecode` entries can be unmarshalled, they may be mostly frozen/stdlib modules while the challenge app (`app.py` / `__main__`) is compiled to native code and appears only in DataComposer constants. If bytecode scanning finds only standard-library hits, pivot to native xref recovery instead of spending time decompiling unrelated stdlib code.
- DataComposer streams can have a leading `.bytecode` chunk followed by additional chunks at a later offset. After parsing the first chunk, compute `end = name_nul + 5 + size` and scan forward for printable chunk names such as `__main__\0` / `__parents_main__\0`; do not assume parse failure at the immediate next byte means there are no more chunks.
- On macOS/ARM analyzing Linux x86-64 ELFs, do not stop because the binary cannot run locally; static ELF mapping + Capstone scanning is still enough to locate relevant native blocks.
- Running a Linux/x86-64 Nuitka onefile under Docker `--platform linux/amd64` can validate extraction and Python/pygame startup, but qemu-user + gdb/ptrace may fail with register/CS errors. Treat that as a signal to use static recovery or a real x86_64 Linux debugger, not as evidence the binary is unanalyzable.

## Reporting discipline

For CTF solving, constants recovery is progress but not a flag. When context/tool limits force a stop, report durable recovered facts and the exact next reversing step, not guessed plaintext or speculative flags.
