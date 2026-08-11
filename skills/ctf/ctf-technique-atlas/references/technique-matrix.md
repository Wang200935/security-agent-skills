# CTF Technique Matrix

This is a clue-to-technique atlas. Use it to choose the next attack path quickly.

## Universal clues

| Clue | Likely direction | First action |
|---|---|---|
| Provided source code | Source review, trust boundaries | Search input sinks, auth checks, dangerous APIs |
| Provided binary + nc host | Pwn or reverse | `file`, checksec, run locally, identify prompt/crash |
| Provided ciphertext/source | Crypto | Extract math objects and mode/nonce/key assumptions |
| Provided pcap/image/archive/dump | Forensics | Preserve artifact, hash, file/magic/strings/metadata |
| Weird text only | Misc/encoding/crypto | Try encodings, frequency, structure, constraints |
| Login/register/admin bot | Web auth/XSS/CSRF | Map session, roles, cookies, bot behavior |
| Dockerfile | Reproduce env; pwn/web/cloud clue | Build container or inspect versions/secrets |

## Web exploitation

| Clue | Technique families | Probes |
|---|---|---|
| User ids in URLs/API | IDOR/BOLA | Change id, enumerate, compare roles |
| JWT cookie/token | none/alg confusion/weak secret/kid/jku | Decode header, check alg, brute weak secret only in CTF |
| SQL errors/search/login | SQLi/NoSQLi/ORM injection | Boolean/time/error probes; source query review |
| Template syntax reflected | SSTI | `{{7*7}}`, `${7*7}`, engine-specific payloads |
| URL fetch/import/avatar by URL | SSRF | localhost, 127.0.0.1 variants, metadata, parser confusion |
| File upload | Extension/MIME/polyglot/path traversal | Upload benign, inspect storage, try double ext/content type |
| File read/download path | LFI/path traversal | `../`, absolute paths, encoding, symlink/zip tricks |
| Serialized cookie/body | Deserialization/signature confusion | Identify framework, secret, gadget surface |
| Admin bot/XSS | XSS/exfil/CSP bypass | Reflected/stored/DOM; cookie accessibility; webhook receiver |
| Coupon/order/rate limits | Race/logic | Parallel requests, replay, state transition review |
| Host/header/cache behavior | Host injection/cache poisoning/smuggling | Vary Host/XFH/CL-TE headers cautiously in lab |

## Cryptography

| Clue | Technique families | Probes |
|---|---|---|
| XOR-looking bytes/repeated key | Single/repeating XOR, many-time pad | Hamming distance, crib flag prefix, pairwise XOR |
| Repeated 16-byte blocks | ECB | Block frequency, cut-and-paste possibility |
| CBC with decrypt oracle | Padding oracle/bit flipping | Check padding error distinction; IV malleability |
| CTR/GCM nonce reuse | Keystream reuse/tag misuse | Compare nonces, XOR ciphertexts, known plaintext |
| `n,e,c` RSA | Textbook RSA/small e/factoring | bit length, integer root, gcd, Fermat, FactorDB/Sage |
| Multiple RSA moduli | Shared prime/broadcast/common modulus | gcd all n, Håstad, common modulus equations |
| Small d hint | Wiener/Boneh-Durfee | Check d size hints; use Sage tools |
| Partial p/q/plaintext | Coppersmith/lattice | Model small root polynomial |
| ECDSA repeated r | Nonce reuse/private key recovery | Group signatures by r; solve k,d |
| Biased/partial nonce | HNP lattice | Build LLL instance |
| PRNG outputs | State/seed recovery | Identify RNG, output width/truncation, consecutive outputs |
| Secret-prefix MAC | Length extension | Test MD5/SHA1/SHA256 constructions |

## Forensics

| Clue | Technique families | Probes |
|---|---|---|
| Image | EXIF, appended data, PNG chunks, LSB, palette, QR | exiftool, binwalk, pngcheck, zbar, channel split |
| Audio | Spectrogram, Morse/DTMF/SSTV, hidden metadata | spectrogram/waveform, exiftool, strings |
| Video | Frames/subtitles/metadata | ffmpeg frame extraction, subtitle tracks |
| Archive | Nested/password/corrupt/known plaintext | list, test, strings hints, repair headers |
| PCAP | HTTP objects, DNS exfil, TCP streams, USB HID, TLS secrets | tshark stats, follow streams, export objects |
| Memory dump | Volatility process/files/env/clipboard/net | volatility3 info, pslist, filescan, cmdline |
| Disk image | Partitions/deleted/slack | mmls/fls/tsk_recover, mount read-only |
| PDF/Office | Metadata/macros/hidden layers/embedded objects | exiftool, pdfimages, oletools, strings |

## Reverse engineering

| Clue | Technique families | Probes |
|---|---|---|
| Plain binary crackme | Strings/constants/compare checks | strings, imports, decompile, locate comparisons |
| Encoded constants | XOR/add/rotate/base transforms | Extract constants, brute transforms, z3 if constraints |
| Complex validation | Constraint solving | Model branches in z3/angr |
| Anti-debug | Patch/jump/time/env bypass | Search ptrace/isDebuggerPresent/timing calls |
| Packed/self-modifying | Unpack/dump after init | Check entropy/sections, run under sandbox/debugger |
| Custom VM | Bytecode disasm/emulation | Identify dispatch loop/opcodes; write emulator |
| APK | Java/Kotlin/native/storage/API | jadx/apktool, manifest, resources, native libs |
| WASM | wasm decompile + JS glue | wasm2wat, strings, browser calls |
| Python bytecode | decompile or disassemble | uncompyle/pycdc/dis, inspect constants |

## Pwn / binary exploitation

| Clue | Technique families | Probes |
|---|---|---|
| Overflow + no canary | ret2win/ROP/ret2libc/shellcode | cyclic offset, check NX/PIE, find win/gadgets |
| Format string | Leak/write primitive | `%p` sweep, positional args, `%n` targets |
| Canary present | Leak canary/off-by-one/format string | Search leak path; avoid blind brute unless intended |
| PIE/ASLR | Info leak/partial overwrite | Leak GOT/stack/code pointer; compute base |
| Heap menu | UAF/double free/tcache/unsorted leak | Script allocator actions; identify glibc version |
| NX off | Shellcode | Badchars, arch ABI, stack/executable memory |
| Seccomp | ORW or allowed syscall chain | dump seccomp, open/read/write/openat/sendfile |
| Full RELRO | No GOT overwrite | Return addr, hooks if old libc, exit handlers, data-only |

## Misc / Jail / Puzzle

| Clue | Technique families | Probes |
|---|---|---|
| Python eval jail | Builtin/import recovery, object graph, Unicode | enumerate globals, subclasses, filters |
| JS jail | Prototype/constructor escape | inspect allowed chars/builtins |
| Shell jail | glob/env/IFS/path expansion | test filters, wildcard reads |
| Weird encodings | base, Morse, Braille, Bacon, esolang | automated decode triage |
| Maze/game/protocol | State-machine automation | interact manually, script parser/solver |
| Proof-of-work | Hash brute force | script optimized solver |
| Math puzzle | SAT/SMT/graph/search | z3, BFS/DFS, ILP where suitable |

## OSINT

| Clue | Technique families | Probes |
|---|---|---|
| Photo/location | Geolocation/time/weather/shadows | metadata, visual landmarks, maps, sun angle |
| Username/email | Account correlation | search exact, archives, platform variants |
| Website/domain | DNS/WHOIS/archives/Git leaks | crt.sh, Wayback, DNS records, robots/sitemap |
| Document | Metadata/authors/history | exiftool, revision history |

## Mobile

| Clue | Technique families | Probes |
|---|---|---|
| APK | Static reverse, storage/API secrets | jadx, apktool, manifest, resources, strings |
| Cert pinning/API | Frida/patch/proxy | locate pinning code, patch in lab |
| Native libs | JNI reverse | file, strings, Ghidra/radare |
| Local DB/prefs | Secret/token extraction | inspect SQLite/shared prefs/assets |

## Cloud / DevOps

| Clue | Technique families | Probes |
|---|---|---|
| Bucket name/URL | Public object listing/misconfig | list/read allowed paths in lab |
| IAM policy | Privilege escalation path | simulate allowed actions mentally/tooling |
| CI logs | Secret/artifact leak | grep tokens, env vars, cache/artifacts |
| SSRF to metadata | Cloud credentials | IMDS endpoints, headers, role creds |
| Kubernetes | Serviceaccount/RBAC/secrets | inspect manifests, tokens, namespaces |

## Blockchain

| Clue | Technique families | Probes |
|---|---|---|
| Solidity contract | Logic/reentrancy/access/storage | read source, ABI, storage layout |
| Unprotected owner/admin setter | Missing access control | call setter to become owner, then call win/solve/getFlag |
| Private variable flag | Storage is public | read storage slots or events; `private` is not secret on-chain |
| Weak private key | Crypto/key search | inspect nonce/key generation, brainwallet hints |
| ABI/calldata | Decode calls/events | cast/ethers/abi decode |
| Storage puzzle | Read private variables | storage slot calculation |

## Hardware / RF / ICS

| Clue | Technique families | Probes |
|---|---|---|
| Firmware blob | binwalk/filesystem/default creds | binwalk, strings, squashfs extraction |
| SDR/IQ/audio | Modulation/protocol decode | inspect spectrum, baud/symbol rate |
| Logic trace | SPI/I2C/UART decode | sigrok/pulseview decoders |
| ICS packets | Modbus/CAN/DNP3 | protocol decode, register/function analysis |

## Game / Protocol

| Clue | Technique families | Probes |
|---|---|---|
| Text TCP service | Parser/state automation | pwntools tube, state machine |
| Maze/grid | BFS/A*/dynamic programming | parse map, solve path |
| Bot/chess/game | Minimax/search/replay | model state, automate optimal moves |

## AI / ML

| Clue | Technique families | Probes |
|---|---|---|
| Prompt endpoint | Prompt injection/lab exfil | identify policy/hidden instruction boundaries |
| Pickle/model file | Unsafe deserialization/reverse | inspect safely, never unpickle untrusted blindly |
| Classifier | Adversarial examples | perturb inputs, gradient-free search |
| ONNX/Torch | Model metadata/weights secrets | inspect graph/strings/state dict safely |
