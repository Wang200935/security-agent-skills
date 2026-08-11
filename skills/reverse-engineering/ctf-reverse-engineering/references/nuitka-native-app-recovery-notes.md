# Nuitka native app recovery notes

Session-derived notes from an EasyPAINT-style CTF binary where the outer artifact was a Nuitka onefile wrapper and the inner Linux x86-64 ELF contained a GUI crypto app compiled by Nuitka.

## Key lessons

- Do not assume every embedded marshal code object belongs to the challenge app. Modern Nuitka bundles many stdlib / dependency modules as marshal blobs while compiling the user's `app.py` to native C/C++ code. If a marshal scan finds only stdlib, numpy, pygame, etc. and no `app.py`, pivot to native-code recovery rather than trying more pyc tooling.
- DataComposer constants can still reveal almost all source-level structure: module name, filename (`app.py`), function names, locals, string constants, integer constants, tuple-shaped varname lists, UI labels, magic bytes, hashes, and alphabets.
- A DataComposer stream may continue for many chunks after `__main__`; parsing from the first `__main__` chunk can walk into `__parents_main__` and dependency chunks. Keep chunk names and object indexes so constants can be mapped back to source-level functions.
- Strings inside DataComposer blobs often have no ordinary xrefs in disassemblers. Lack of xrefs to `derive_secret`, `PASSWORD_SHA256`, or `app.py` is expected and does not mean the constants are unused.
- When DataComposer constants expose function names but normal RIP-relative string xrefs are absent, pivot to CPython/Nuitka runtime-call clustering. Scan disassembly for dense calls to APIs such as `PyLong_*`, `PyNumber_*`, `PyList_Append`, `PyBytes_*`, and `PyObject_GetItem`; group nearby calls into candidate source functions. For crypto apps, `mat_vec_mul` usually has nested multiply/add/mod/append patterns, while stream-XOR helpers often show byte loops plus XOR or raw byte-buffer operations.
- Filter CPython/runtime clusters aggressively. Dense calls around symbols such as `PyInit__tokenize` or arithmetic helper implementations may be standard library / interpreter internals, not challenge code. Before spending time decompiling a cluster, corroborate it with app-specific constants, module/function-table references, varname slot access, or control-flow from the app module init.
- Duplicate constant blobs (`__main__` and `__parents_main__`) are common. Confirm which one is used by runtime native functions, but either can be sufficient for source-level metadata.

## Triage pattern

1. Extract inner onefile payload and identify the inner ELF.
2. Search for markers: `__main__`, `__parents_main__`, `app.py`, challenge function names, UI strings, hashes, file magics.
3. Parse DataComposer chunks: `name\0 + uint32_le(part_len) + uint16_le(count) + tagged objects + '.'`.
4. Dump constants with stable indexes. Record:
   - global constants (`DIM`, `P`, `Q`, file paths, magic values)
   - password/hash/alphabet constants
   - function names and local-variable tuples
   - error strings that delimit code paths
5. Try marshal code-object scanning only as a quick check. If no app code appears, treat app logic as native.
6. Build a native map using function entry candidates near app-specific helper calls and source-line/error constant references. Use Capstone/objdump plus known CPython/Nuitka helper targets.
7. For crypto hybrids, stop speculative math if constants show missing derivation routines. Recover exact native logic for functions like `derive_secret`, `build_matrix`, `derive_message_vector`, and `stream_xor_*` before lattice/Z3 work.

## Reporting discipline

When context/tool limits force a stop before the flag, summarize only verified facts:
- artifact paths and hashes
- recovered file layout and constants
- confirmed packer/runtime structure
- exact scripts/dumps created
- dead ends that were actually tested
- next highest-leverage reversing target

Avoid presenting random-looking decrypted candidates or linear-algebra outputs as progress unless they satisfy a verification condition such as flag format, file magic, or source-level equation checks.
