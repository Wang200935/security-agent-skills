# Cross-Architecture PWN

```python
ARCH_DIFFERENCES = {
    'x86_64': {
        'call_conv': 'System V AMD64: rdi,rsi,rdx,rcx,r8,r9 (stack for rest)',
        'ret': 'ret pops 8 bytes from stack → rip',
        'stack': 'Grows downward, 16-byte aligned before call',
    },
    'ARM32': {
        'call_conv': 'r0-r3 for args, LR (r14) for return address',
        'ret': 'pop {pc} or bx lr — NO dedicated ret instruction!',
        'thumb': 'Thumb mode: bit 0 of address = 1, 16-bit instructions',
    },
    'AArch64': {
        'call_conv': 'x0-x7 for args, x30 (LR) for return',
        'ret': 'ret uses x30 — overwrite LR then trigger ret',
        'pac': 'Pointer Authentication (PAC) on ARMv8.3+ — sign/verify return addresses',
    },
    'MIPS': {
        'call_conv': '$a0-$a3 for args, $ra for return',
        'delay_slot': 'Instruction AFTER branch executes before branch takes effect!',
        'cache': 'Separate I-cache and D-cache — need cache flush after code modification',
    },
    'RISC-V': {
        'call_conv': 'a0-a7 for args, ra for return',
        'compress': 'C extension: 16-bit compressed instructions',
        'no_flags': 'No condition flags — branch on register comparison',
    },
}

# ARM32 ROP specifics
def arm32_rop_notes():
    """
    - Gadgets end with: pop {pc}, bx lr, pop {..., pc}
    - Need to handle Thumb mode (bit 0 address)
    - System call: SVC 0 (supervisor call), syscall number in r7
    - execve("/bin/sh", 0, 0): r7=11, r0="/bin/sh", r1=0, r2=0, SVC 0
    """
    pass

# MIPS ROP specifics  
def mips_rop_notes():
    """
    - Delay slot: instruction after jump executes BEFORE jump
    - GOT is ALWAYS at a fixed offset from .text (no full ASLR on many MIPS systems)
    - Stack finders: gadget to move $sp to controlled heap area
    - Cache coherency: after writing shellcode, flush D-cache+I-cache for execution
    """
    pass
```

---
