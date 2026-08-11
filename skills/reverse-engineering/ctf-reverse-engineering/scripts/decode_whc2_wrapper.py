#!/usr/bin/env python3
"""
Decode the outer wrapper's rodata bytecode to extract the embedded Go binary.
Usage: python3 decode_whc2_wrapper.py <input_binary> [output_binary]
"""

import sys
import struct

def decode_rodata(rodata_bytes):
    """Decode the two-byte encoding to payload."""
    # Verify header: 01 00 02 00 (two uint16 LE)
    if len(rodata_bytes) < 4:
        raise ValueError("rodata too small")
    count, typ = struct.unpack('<HH', rodata_bytes[:4])
    if count != 1 or typ != 2:
        print(f"Warning: unexpected header: count={count}, type={typ}")
    
    out = bytearray()
    # Decode: each pair of bytes -> one output byte
    # Formula: (byte1 << 4) | (byte2 & 0x0F)
    for i in range(4, len(rodata_bytes) - 1, 2):
        b1 = rodata_bytes[i]
        b2 = rodata_bytes[i + 1]
        out.append(((b1 << 4) | (b2 & 0x0F)) & 0xFF)
    return bytes(out)

def extract_rodata_from_elf(elf_path):
    """Extract .rodata section from ELF."""
    import subprocess
    # Use readelf to get section info
    result = subprocess.run(['readelf', '-S', elf_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"readelf failed: {result.stderr}")
    
    # Parse section headers to find .rodata
    lines = result.stdout.split('\n')
    rodata_idx = None
    rodata_offset = None
    rodata_size = None
    rodata_addr = None
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 6 and '.rodata' in line:
            # Idx Name Size VMA ...
            try:
                rodata_idx = int(parts[0])
                rodata_size = int(parts[2], 16)
                rodata_addr = int(parts[3], 16)
            except:
                continue
    
    if rodata_idx is None:
        raise RuntimeError(".rodata section not found")
    
    # Get section header details for file offset
    result2 = subprocess.run(['readelf', '-S', '-W', elf_path], capture_output=True, text=True)
    # Find the .rodata line with offset
    for line in result2.stdout.split('\n'):
        if f'[{rodata_idx}]' in line and '.rodata' in line:
            parts = line.split()
            if len(parts) >= 6:
                rodata_offset = int(parts[4], 16)
                break
    
    if rodata_offset is None:
        raise RuntimeError("Could not find .rodata file offset")
    
    print(f".rodata: offset=0x{rodata_offset:x}, size=0x{rodata_size:x}, vma=0x{rodata_addr:x}")
    
    with open(elf_path, 'rb') as f:
        f.seek(rodata_offset)
        return f.read(rodata_size)

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <wrapper_binary> [output_binary]")
        sys.exit(1)
    
    wrapper_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'decoded_payload'
    
    print(f"Extracting .rodata from {wrapper_path}...")
    rodata = extract_rodata_from_elf(wrapper_path)
    
    print(f"Decoding {len(rodata)} bytes of bytecode...")
    payload = decode_rodata(rodata)
    
    print(f"Decoded payload size: {len(payload)} bytes ({len(payload)/1024/1024:.2f} MB)")
    
    # Verify it's an ELF
    if payload[:4] == b'\x7fELF':
        print("✓ Payload is a valid ELF binary")
        elf_class = {1: '32-bit', 2: '64-bit'}.get(payload[4], 'unknown')
        elf_data = {1: 'LE', 2: 'BE'}.get(payload[5], 'unknown')
        print(f"  Class: {elf_class}, Data: {elf_data}")
    else:
        print(f"⚠ Payload magic: {payload[:8].hex()}")
    
    with open(output_path, 'wb') as f:
        f.write(payload)
    
    print(f"✓ Written to {output_path}")

if __name__ == '__main__':
    main()