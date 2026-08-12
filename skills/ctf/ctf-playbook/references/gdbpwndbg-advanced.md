# GDB/pwndbg Advanced

```python
GDB_COMMANDS = {
    'analysis': [
        'checksec — check binary protections at runtime',
        'vmmap — memory mappings (ASLR verification)',
        'vis_heap_chunks — visual heap layout (pwndbg)',
        'arenas — show heap arenas',
        'bins — show all free bins (tcache, fastbin, unsortedbin, smallbin, largebin)',
        'telescope $rsp 50 — view stack with pointer resolution',
        'context — show registers, stack, code, backtrace (auto-refresh)',
    ],
    'exploitation': [
        'search "/bin/sh" — find string in memory',
        'find_fake_fast 0x7ffe1234 0x80 — find fake chunk near address',
        'parseheap — parse heap metadata',
        'ropgadget <regex> — search ROP gadgets in memory',
        'fsbase / gsbase — read TLS (canary is at fs:0x28 on x86_64)',
    ],
    'debugging': [
        'b *0x400123 if $rdi==0xdead — conditional breakpoint',
        'commands → set breakpoint auto-commands',
        'watch *(long*)0x601018 — hardware watchpoint',
        'rwatch — read watchpoint',
        'record full → reverse-step — reverse execution!',
    ],
}

# Pwndbg-specific tricks
PWNTOOLS_GDB = """
# Load .gdbinit for pwndbg
echo "source /path/to/pwndbg/gdbinit.py" >> ~/.gdbinit

# Common pwndbg settings
set context-sections 'regs disasm code stack backtrace'
set show-flags on
set show-retaddr on
set hexdump-width 16
"""
```

---
