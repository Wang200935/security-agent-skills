#!/usr/bin/env python3
"""
Quick verification script for Alcor CTAlc001.dll / DCULC-style vendor DLL.
Run on Windows with the DLL in the same directory or provide full path.

Usage:
    python verify_vendor_dll.py [path/to/CTAlc001.dll]
"""

import sys
import ctypes
from ctypes import c_short, c_void_p, c_char_p, POINTER, c_ubyte, create_string_buffer

def test_dll(dll_path):
    print(f"Loading: {dll_path}")
    try:
        dll = ctypes.windll.LoadLibrary(dll_path)
        print("✓ DLL loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load DLL: {e}")
        return False

    # Define signatures
    dll.IC_InitComm.argtypes = [c_short]
    dll.IC_InitComm.restype = c_void_p
    
    dll.IC_ExitComm.argtypes = [c_void_p]
    
    dll.IC_Check_4442.argtypes = [c_void_p]
    dll.IC_Check_4442.restype = c_short
    
    dll.IC_InitType.argtypes = [c_void_p, c_short]
    dll.IC_InitType.restype = c_short
    
    dll.IC_Read.argtypes = [c_void_p, c_short, c_short, POINTER(c_ubyte)]
    dll.IC_Read.restype = c_short
    
    dll.IC_CheckPass_4442hex.argtypes = [c_void_p, c_char_p]
    dll.IC_CheckPass_4442hex.restype = c_short
    
    dll.IC_ReadCount_SLE4442.argtypes = [c_void_p]
    dll.IC_ReadCount_SLE4442.restype = c_short

    USB_PORT = 100
    TYPE_SLE4442 = 0x10

    print("\n1. Connecting to reader (IC_InitComm)...")
    handle = dll.IC_InitComm(USB_PORT)
    if not handle or handle <= 0:
        print(f"   ✗ IC_InitComm returned {handle}")
        return False
    print(f"   ✓ Handle: {handle}")

    print("\n2. Checking for SLE4442 (IC_Check_4442)...")
    ret = dll.IC_Check_4442(handle)
    if ret != 0:
        print(f"   ✗ IC_Check_4442 returned {ret} (card not present or wrong type)")
        dll.IC_ExitComm(handle)
        return False
    print("   ✓ SLE4442 detected")

    print("\n3. Initializing card type (IC_InitType 0x10)...")
    ret = dll.IC_InitType(handle, TYPE_SLE4442)
    if ret != 0:
        print(f"   ✗ IC_InitType returned {ret}")
        dll.IC_ExitComm(handle)
        return False
    print("   ✓ Type initialized")

    print("\n4. Verifying default PIN (IC_CheckPass_4442hex 'ffffff')...")
    pin_buf = create_string_buffer(b"ffffff\x00")
    ret = dll.IC_CheckPass_4442hex(handle, pin_buf)
    if ret != 0:
        print(f"   ✗ PIN verify returned {ret}")
        # Don't exit - maybe PIN is different
    else:
        print("   ✓ PIN verified (default FFFFFF)")

    print("\n5. Reading PIN counter (error counter (IC_ReadCount_SLE4442)...")
    counter = dll.IC_ReadCount_SLE4442(handle)
    print(f"   Remaining attempts: {counter}")

    print("\n6. Reading full 256-byte EEPROM (IC_Read)...")
    buf = (c_ubyte * 256)()
    ret = dll.IC_Read(handle, 0, 256, buf)
    if ret != 0:
        print(f"   ✗ IC_Read returned {ret}")
    else:
        data = bytes(buf)
        print(f"   ✓ Read 256 bytes")
        print(f"   Hex: {data.hex()}")
        # Show first 32 bytes as ASCII where printable
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[:32])
        print(f"   ASCII (first 32): {ascii_part}")

    print("\n7. Reading error counter at offset 0x1F...")
    err_buf = (c_ubyte * 1)()
    ret = dll.IC_Read(handle, 0x1F, 1, err_buf)
    if ret == 0:
        print(f"   Error counter: {err_buf[0]} (0x{err_buf[0]:02X})")
    else:
        print(f"   ✗ Read error counter failed: {ret}")

    print("\n8. Disconnecting (IC_ExitComm)...")
    dll.IC_ExitComm(handle)
    print("   ✓ Disconnected")

    return True

if __name__ == "__main__":
    dll_path = sys.argv[1] if len(sys.argv) > 1 else "CTAlc001.dll"
    success = test_dll(dll_path)
    sys.exit(0 if success else 1)