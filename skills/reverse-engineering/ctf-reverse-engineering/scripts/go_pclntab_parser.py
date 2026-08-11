#!/usr/bin/env python3
"""
Parse Go 1.20+ pclntab to find function addresses by name.
Usage: python3 go_pclntab_parser.py <go_binary> <function_name_pattern>
"""

import sys
import struct
import re

def parse_pclntab(data):
    """Parse Go 1.20+ pclntab header and return key offsets."""
    # Find pclntab magic: f1 ff ff ff (or f0 ff ff ff for older)
    for magic in [b'\xf1\xff\xff\xff', b'\xf0\xff\xff\xff']:
        pclntab_off = data.find(magic)
        if pclntab_off != -1:
            break
    else:
        raise RuntimeError("pclntab magic not found")
    
    # Verify header structure
    if pclntab_off + 72 > len(data):
        raise RuntimeError("pclntab header truncated")
    
    # Header: magic(4), pad(2), minLC(1), ptrSize(1)
    # nfunc(8), nfiles(8)
    # textStart(8), funcnameOff(8), cuOff(8), filetabOff(8), pctabOff(8), pclnOff(8)
    header = data[pclntab_off:pclntab_off+72]
    magic, minLC, ptrSize, nfunc, nfiles, textStart, funcnameOff, cuOff, filetabOff, pctabOff, pclnOff = struct.unpack('<4s2xBBQQQQQQQQ', header)
    
    print(f"pclntab at 0x{pclntab_off:x}")
    print(f"  nfunc={nfunc}, textStart=0x{textStart:x}")
    print(f"  funcnameOff=0x{funcnameOff:x}, pclnOff=0x{pclnOff:x}")
    
    return {
        'pclntab_off': pclntab_off,
        'textStart': textStart,
        'funcnameOff': funcnameOff,
        'pclnOff': pclnOff,
        'nfunc': nfunc,
        'funcname_base': pclntab_off + funcnameOff,
        'pcln_data_off': pclntab_off + pclnOff,
    }

def find_name_offsets(data, funcname_base, pattern):
    """Find all function names matching pattern in funcname table."""
    matches = {}
    # Search for pattern + null terminator
    for m in re.finditer(pattern.encode() + b'\x00', data[funcname_base:]):
        name = data[funcname_base + m.start():funcname_base + m.end() - 1].decode('ascii', errors='replace')
        name_off = m.start()
        matches[name_off] = name
    return matches

def find_function_addresses(data, info, target_names):
    """Scan _func structs at pclnOff for target nameOff values."""
    # Convert target names to nameOff values
    name_offsets = {}
    for name_off, name in find_name_offsets(data, info['funcname_base'], '|'.join(target_names)).items():
        if any(t in name for t in target_names):
            name_offsets[name_off] = name
    
    print(f"Found {len(name_offsets)} name offsets for targets")
    
    results = {}
    # Scan _func data linearly looking for nameOff values
    # _func struct starts with: entryOff(uint32), nameOff(int32), ...
    # We search for nameOff as uint32
    search_start = info['pcln_data_off']
    search_end = min(search_start + 0x300000, len(data))
    
    for name_off, name in name_offsets.items():
        target_bytes = struct.pack('<I', name_off)
        idx = search_start
        while idx < search_end:
            idx = data.find(target_bytes, idx, search_end)
            if idx == -1:
                break
            # Check if this looks like a _func struct: 4 bytes before = entryOff
            if idx >= search_start + 4:
                entryOff = struct.unpack('<I', data[idx-4:idx])[0]
                pc = info['textStart'] + entryOff
                # Sanity check: PC should be in .text section
                if 0x400000 <= pc <= 0x700000:  # typical .text range
                    results[name] = pc
                    print(f"  {name}: PC=0x{pc:x} (entryOff=0x{entryOff:x}, _func at 0x{idx-4:x})")
                    break
            idx += 1
    
    return results

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <go_binary> <function_pattern> [function_pattern...]")
        print(f"Example: {sys.argv[0]} c2_decoded 'main.openConfig' 'main.runLine' 'main.cycle'")
        sys.exit(1)
    
    binary_path = sys.argv[1]
    target_patterns = sys.argv[2:]
    
    with open(binary_path, 'rb') as f:
        data = f.read()
    
    print(f"Loading {binary_path} ({len(data)} bytes)...")
    
    try:
        info = parse_pclntab(data)
    except Exception as e:
        print(f"Error parsing pclntab: {e}")
        sys.exit(1)
    
    # Collect all names from funcname table
    print("Scanning funcname table for matching functions...")
    all_names = find_name_offsets(data, info['funcname_base'], '')
    print(f"Total functions in table: {len(all_names)}")
    
    # Filter by patterns
    filtered_names = {}
    for name_off, name in all_names.items():
        for pattern in target_patterns:
            if re.search(pattern, name):
                filtered_names[name_off] = name
                break
    
    print(f"Matched {len(filtered_names)} functions:")
    for off, name in sorted(filtered_names.items(), key=lambda x: x[1]):
        print(f"  {name} (nameOff=0x{off:x})")
    
    # Find addresses
    print("\nFinding function addresses...")
    addresses = find_function_addresses(data, info, target_patterns)
    
    print(f"\n=== Results ===")
    for name, pc in sorted(addresses.items()):
        print(f"{name}: 0x{pc:x}")
    
    missing = [n for n in filtered_names.values() if n not in addresses]
    if missing:
        print(f"\nMissing: {missing}")

if __name__ == '__main__':
    main()