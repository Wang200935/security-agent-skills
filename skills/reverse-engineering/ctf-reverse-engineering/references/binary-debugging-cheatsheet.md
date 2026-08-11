# Binary Debugging Cheatsheet

## LLDB Basics macOS/Linux

```bash
lldb ./chall
(lldb) run
(lldb) breakpoint set --name main
(lldb) breakpoint set --name strcmp
(lldb) register read
(lldb) memory read --size 1 --format x --count 64 ADDRESS
(lldb) disassemble --name main
```

## GDB Basics

```bash
gdb ./chall
break main
run
info registers
x/64bx $rsp
x/s ADDRESS
disassemble main
```

## What to Break On

- `strcmp`, `strncmp`, `memcmp`
- `scanf`, `fgets`, `read`
- crypto/hash functions if dynamically linked
- failure/success print sites

## Z3 Constraint Skeleton

```python
from z3 import *

n = 32
xs = [BitVec(f'x{i}', 8) for i in range(n)]
s = Solver()
for x in xs:
    s.add(x >= 0x20, x <= 0x7e)
# add constraints from binary
assert s.check() == sat
m = s.model()
print(bytes([m[x].as_long() for x in xs]))
```
