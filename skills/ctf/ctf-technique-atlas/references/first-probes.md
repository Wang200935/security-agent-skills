# CTF First Probes

Use these before expensive tooling. They are designed to reveal category, structure, and easy wins.

## File/artifact baseline

```bash
mkdir -p artifacts solve
sha256sum <file>
file <file>
stat <file>
xxd -l 256 <file>
strings -a <file> | head -200
```

If available:

```bash
binwalk <file>
exiftool <file>
```

## Text baseline

- Preserve exact bytes; avoid copy/paste Unicode corruption.
- Check length, alphabet, delimiters, repeated patterns.
- Try hex/base64/base32/ascii85/url/jwt/pem recognition.
- Check flag prefix crib possibilities.

Python snippet:

```python
from collections import Counter
s = open('input.txt','rb').read()
print(len(s), Counter(s).most_common(20))
print(s[:200])
```

## Web target baseline

```bash
curl -i -sS <url>
curl -i -sS <url>/robots.txt
curl -i -sS <url>/sitemap.xml
curl -i -sS <url>/.git/HEAD
```

Then map like a user:

- register/login/logout
- role boundaries
- cookies/session/JWT
- forms and hidden fields
- API endpoints
- upload/download/fetch features
- admin-only or bot-triggered behavior

## Source code baseline

Search for:

- auth/role checks
- input parsing
- SQL/NoSQL queries
- template rendering
- file path joins
- subprocess/eval/deserialization
- HTTP fetch/client behavior
- crypto key/nonce generation
- debug routes and test credentials

## Crypto baseline

- Identify all constants and byte/int conversions.
- Check whether encryption is deterministic.
- Check repeated nonces/IVs/blocks.
- For RSA: bit length, e, n factor smell, gcd if multiple n.
- For ECC signatures: repeated r, curve order, nonce source.
- For PRNG: language/library, seed source, output width, truncation.

## Forensics baseline

Images:

```bash
exiftool image
binwalk image
strings -a image | head
```

PCAP:

```bash
tshark -r capture.pcap -q -z io,phs
```

Archives:

```bash
file archive
7z l archive
strings -a archive | head
```

Disk/memory:

- identify format first
- mount/extract read-only
- list processes/files/partitions before carving

## Reverse baseline

```bash
file chall
sha256sum chall
strings -a chall | head -200
objdump -x chall 2>/dev/null | head -100
```

Then identify:

- format/arch
- stripped or symbols
- suspicious strings/imports
- compare/crypto/check functions
- anti-debug/time/env checks

## Pwn baseline

```bash
file chall
checksec --file=chall 2>/dev/null || true
./chall
```

Then:

- reproduce prompt
- find crash with cyclic pattern if overflow suspected
- inspect mitigations
- record libc/ld/Dockerfile
- create pwntools skeleton early

## Misc/jail baseline

For jails:

- enumerate allowed characters
- test builtins/globals/imports
- test quotes, dots, underscores, brackets, Unicode normalization
- find introspection/object graph path

For protocols:

- interact manually once
- log transcript
- write parser/state machine

## OSINT baseline

- Extract metadata first.
- Search exact unique strings/usernames/domains.
- Check archives/DNS/cert transparency where relevant.
- For images, separate metadata clues from visual clues.

## Mobile baseline

APK:

```bash
file app.apk
unzip -l app.apk | head
strings -a app.apk | head
```

Then use jadx/apktool if installed; inspect manifest, resources, strings, native libs, storage/API endpoints.

## Cloud baseline

- Read IAM/policy/config exactly.
- Identify provider and service.
- Look for public read/list vs write actions.
- For SSRF labs, check metadata service assumptions carefully and only in authorized CTF target.

## Blockchain baseline

- Read contract source and ABI.
- Identify win condition.
- Inspect access control, storage layout, payable/reentrancy, arithmetic, block timestamp/randomness.
- Decode calldata/events when transaction history is provided.
