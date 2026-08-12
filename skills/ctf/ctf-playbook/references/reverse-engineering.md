# REVERSE ENGINEERING

### Quick Analysis

```bash
# File identification
file binary
strings binary | grep -i flag
strings binary | grep -i ctf
strings binary | grep -i pass

# Check binary security
checksec --file=binary
# Check for: PIE, NX, Stack Canary, RELRO, FORTIFY

# Dynamic analysis
ltrace ./binary  # library calls
strace ./binary  # system calls
```

### Common Obfuscation Patterns

```python
# XOR string deobfuscation
def deobfuscate_xor_strings(data: bytes, start_pattern: bytes = b'\\x48\\x8d'):
    """Find and deobfuscate XOR-encoded strings in binaries."""
    import re
    
    strings = []
    for i in range(len(data)):
        # Look for common string loading patterns
        if data[i:i+2] == start_pattern:
            # Extract string from nearby bytes
            pass
    
    return strings

# Base64 decode from binary
def extract_base64_from_binary(filepath: str) -> list:
    """Extract base64 strings from binary."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    import re
    pattern = re.compile(b'[A-Za-z0-9+/]{20,}={0,2}')
    matches = pattern.findall(data)
    
    import base64
    decoded = []
    for m in matches:
        try:
            decoded.append(base64.b64decode(m))
        except:
            pass
    
    return decoded
```

### Python Bytecode Reversing

```python
# Decompile .pyc files
# Use uncompyle6 or pycdc

# Common Python obfuscation:
# - marshal + base64 + exec
# - eval with encoded strings
# - lambda obfuscation
# - zlib compressed code

import marshal
import base64
import zlib

def deobf_python_common(code_str: str):
    """Try common Python obfuscation unwrapping."""
    
    # Try base64 → marshal
    try:
        decoded = base64.b64decode(code_str)
        obj = marshal.loads(decoded)
        return obj
    except:
        pass
    
    # Try base64 → zlib → marshal
    try:
        decoded = base64.b64decode(code_str)
        decompressed = zlib.decompress(decoded)
        obj = marshal.loads(decompressed)
        return obj
    except:
        pass
    
    return None
```

### Ghidra/Radare2 Quick Commands

```bash
# r2 quick analysis
r2 -A binary     # Analyze all
> afl            # List functions
> s main         # Seek to main
> pdf            # Print disassembly
> iz             # List strings
> axt <addr>     # Cross-references to address

# Find "flag" references
r2 -q -c '/ flag' binary
r2 -q -c 'izz | grep flag' binary
```

---
