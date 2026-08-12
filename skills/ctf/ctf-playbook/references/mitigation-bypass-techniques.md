# Mitigation Bypass Techniques

```python
MITIGATION_BYPASS = {
    'NX/DEP': {
        'desc': 'Non-executable stack/heap',
        'bypass': 'ROP/JOP (reuse existing code), ret2libc, mprotect to re-enable',
    },
    'ASLR': {
        'desc': 'Randomized base addresses',
        'bypass': 'Info leak (format string, UAF, OOB), partial overwrite, brute force (32-bit), side channel',
    },
    'PIE': {
        'desc': 'Position-independent executable (ASLR for binary)',
        'bypass': 'PIE leak (same as ASLR), partial overwrite on return addr (2 bytes on x86_64), _dl_fixup tricks',
    },
    'Stack Canary': {
        'desc': 'Random value before return address, checked before ret',
        'bypass': 'Leak canary via format string/OOB, brute force (fork server), master canary overwrite (TLS), SSP leak via __stack_chk_fail message',
    },
    'Full RELRO': {
        'desc': 'GOT is read-only',
        'bypass': 'Target __malloc_hook/__free_hook (glibc < 2.34), vtable/function pointers, libc GOT (if writable), destructor array (.fini_array)',
    },
    'CFI': {
        'desc': 'Control Flow Integrity (clang CFI, MS Control Flow Guard)',
        'bypass': 'COOP (Counterfeit Object-oriented Programming), reuse allowed targets, corrupt virtual call dispatch',
    },
    'CET/Shadow Stack': {
        'desc': 'Hardware-enforced shadow stack (Intel CET)',
        'bypass': 'Target data pointers instead of return addresses, corrupt exception handlers, signal frame manipulation',
    },
    'SEHOP': {
        'desc': 'Structured Exception Handler Overwrite Protection (Windows)',
        'bypass': 'Overwrite final exception handler, use vectored exception handlers',
    },
}

# Format String — Canary + PIE Bypass
def format_string_full_bypass():
    """
    Single format string vulnerability can bypass BOTH canary and PIE:
    
    1. Leak stack canary: %N$p where N is canary's position on stack
    2. Leak PIE base: %M$p where M is return address position (contains code addr)
    3. Leak libc: %L$p for libc return address (__libc_start_main+offset)
    4. Now craft payload with correct canary + ROP chain
    """
    from pwn import *
    
    # Example fmtstr payload generation
    def fmtstr_payload(offset, writes, written=0):
        """Generate format string payload for arbitrary write."""
        payload = b''
        for addr, value in writes.items():
            # Write value to addr using %n
            pass
        return payload

# Partial Overwrite Bypass
def partial_overwrite_bypass():
    """
    ASLR randomizes high bytes but low 12 bits of page offsets are fixed.
    On x86_64, only 4 bits of address within a page are randomized.
    
    Partial overwrite (e.g., overwrite last 1-2 bytes of return address):
    - Success probability: 1/16 for 1 byte, 1/4096 for 2 bytes
    
    Useful when: write primitive is limited, or when avoiding full overwrite
    that would require known addresses.
    """
    pass

# GOT Overwrite with Partial RELRO
def got_overwrite():
    """
    Partial RELRO: GOT is writable.
    1. Overwrite printf@GOT → system
    2. Call printf("/bin/sh") → system("/bin/sh")!
    
    Full RELRO: GOT is read-only after loading.
    Alternatives: __malloc_hook (glibc < 2.34), __free_hook, .fini_array, _dl_fini
    """
    pass
```

---
