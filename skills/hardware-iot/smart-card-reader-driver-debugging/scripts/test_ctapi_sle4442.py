#!/usr/bin/env python3
"""
SLE4442 CT-API Test Script
Requires: 32-bit Python + CTAlc001.dll + SZCCID driver bound to device
"""

import ctypes
import sys
import os

# Path to CTAlc001.dll (32-bit)
DLL_PATH = r"C:\Users\ellis\Downloads\ICCARD-Driver\ICCARD-AB22+AB23+AB24+AB25+KA02\Windows Driver\AU9540_V1.7.2.0\program_files\AlcorMicro\x64\CTAlc001.dll"

# Check 32-bit
import struct
print(f"Python bitness: {struct.calcsize('P')*8}-bit")
if struct.calcsize('P')*8 != 32:
    print("ERROR: This script MUST run with 32-bit Python")
    sys.exit(1)

# Load DLL
try:
    dll = ctypes.windll.LoadLibrary(DLL_PATH)
    print(f"Loaded DLL: {DLL_PATH}")
except Exception as e:
    print(f"Failed to load DLL: {e}")
    sys.exit(1)

# Define function signatures
dll.CT_init.argtypes = [ctypes.c_uint16, ctypes.c_uint16]
dll.CT_init.restype = ctypes.c_int16

dll.CT_data.argtypes = [
    ctypes.c_uint16,                    # ctn (handle)
    ctypes.POINTER(ctypes.c_ubyte),     # dad
    ctypes.POINTER(ctypes.c_ubyte),     # sad
    ctypes.c_uint16,                    # lenc
    ctypes.POINTER(ctypes.c_ubyte),     # command
    ctypes.POINTER(ctypes.c_uint16),    # lenr
    ctypes.POINTER(ctypes.c_ubyte),     # response
]
dll.CT_data.restype = ctypes.c_int16

dll.CT_close.argtypes = [ctypes.c_uint16]
dll.CT_close.restype = ctypes.c_int16

# Initialize - port 100 = USB for Alcor AU9540
print("Initializing CT-API (port 100)...")
ctn = ctypes.c_uint16(0)
pn = ctypes.c_uint16(100)
rc = dll.CT_init(ctn, pn)
print(f"CT_init(0, 100) = {rc}")
if rc != 0:
    print(f"ERROR: CT_init returned {rc} (0x{rc:04X})")
    if rc == -8 or rc == 0xFFF8:
        print("  -> Device NOT bound to SZCCID.sys kernel driver")
        print("  -> Fix: bind device to Alcor SZCCID driver (see skill docs)")
    sys.exit(1)

print("CT-API initialized successfully!")

def send_cmd(cmd_bytes, expected_len=256):
    """Send CT-API command and return response"""
    ctn_handle = ctypes.c_uint16(0)
    dad = (ctypes.c_ubyte * 1)(0x00)
    sad = (ctypes.c_ubyte * 1)(0x00)
    command = (ctypes.c_ubyte * len(cmd_bytes))(*cmd_bytes)
    lenr = ctypes.c_uint16(expected_len)
    response = (ctypes.c_ubyte * expected_len)()
    
    rc = dll.CT_data(ctn_handle, dad, sad, len(cmd_bytes), command, ctypes.byref(lenr), response)
    
    if rc != 0:
        print(f"CT_data returned {rc} (0x{rc:04X})")
        return None
    
    return bytes(response[:lenr.value])

# Test commands
print("\n=== Testing SLE4442 Commands ===\n")

# 1. Read Security Memory (EC + PSC)
# Command: 0x31 (Read Security Memory), addr 0x01, read 4 bytes
# Note: Some sources use different command bytes for CT-API
# Let's try the standard ACR38 pseudo-APDU mapped to CT-API

test_commands = [
    ("Read Security Memory (EC+PSC)", bytes([0xFF, 0xB4, 0x00, 0x00, 0x04])),
    ("Read Main Memory at 0x00 (4 bytes)", bytes([0xFF, 0xB0, 0x00, 0x00, 0x04])),
    ("Read Error Counter (addr 0x1F)", bytes([0xFF, 0xB0, 0x00, 0x1F, 0x01])),
    ("ATR/Reset", bytes([0xFF, 0x30, 0x00, 0x00, 0x04])),  # Reset/ATR command
]

for name, cmd in test_commands:
    print(f"--- {name} ---")
    print(f"Command: {' '.join(f'{b:02X}' for b in cmd)}")
    resp = send_cmd(cmd)
    if resp:
        print(f"Response ({len(resp)} bytes): {' '.join(f'{b:02X}' for b in resp)}")
    else:
        print("FAILED")
    print()

# 2. Try default PSC verify: FF FF FF
print("--- Verify PSC: FF FF FF ---")
verify_cmd = bytes([0xFF, 0x20, 0x00, 0x00, 0x03, 0xFF, 0xFF, 0xFF])
resp = send_cmd(verify_cmd)
if resp:
    print(f"Response: {' '.join(f'{b:02X}' for b in resp)}")
else:
    print("FAILED")

# 3. If verify succeeded, read main memory again
print("\n--- Read Main Memory after verify ---")
resp = send_cmd(bytes([0xFF, 0xB0, 0x00, 0x00, 0x10]))
if resp:
    print(f"First 16 bytes: {' '.join(f'{b:02X}' for b in resp)}")

# Close
print("\nClosing CT-API...")
dll.CT_close(ctypes.c_uint16(0))
print("Done.")