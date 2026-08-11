# SLE4442 CT-API Command Reference (Complete)

## Command Format

All commands use the ACR38 pseudo-APDU format mapped through CTAlc001.dll:

```
CT_data(ctn, dad=0x00, sad=0x00, lenc, command, lenr, response)
```

---

## Card Initialization

### Select SLE4442 Card Type
```
Command:  FF A4 00 00 01 05
Response: 90 00 (success)
```

### Reset / ATR
```
Command:  FF 30 00 00 04
Response: A2 13 10 91 (SLE4442 ATR)
          A2 = SLE44xx series
          13 = 256 bytes EEPROM
          10 = 2-wire interface
          91 = CRC/checksum
```

---

## Memory Read Commands

### Read Main Memory (0x00-0xFF)
```
Command:  FF B0 00 AA LL
  AA = Start address (0x00-0xFF)
  LL = Length (1-256, 0x00 = 256)

Response: LL bytes of data
```

### Read Security Memory (EC + PSC[3])
```
Command:  FF B4 00 00 04
Response: 4 bytes = [EC, PSC1, PSC2, PSC3]

Note: Some clones mask PSC (return 00 00 00), but EC is always readable
```

### Read Protection Memory (First 32 bytes)
```
Command:  FF B8 00 00 04
Response: 4 bytes = 32 protection bits (1 bit per byte 0x00-0x1F)
  Bit = 1 → Write protected (OTP)
  Bit = 0 → Writable
```

### Read Presentation Error Counter (SLE4428/5528 only)
```
Command:  FF B2 00 00 04
Response: 4 bytes (EC in different format)
```

---

## PSC Verification

### Compare Verification Data (CT-API / Bus Pirate - 3 bytes)
```
Command:  FF 20 00 00 03 P1 P2 P3
Response: 00 (success) or error code

Note: This is the raw 3-byte PSC format for CT-API / direct 2-wire
```

### Present Code (ACR38 Pseudo-APDU - 2 bytes)
```
Command:  FF 20 00 00 02 CC
  CC = 2-byte code (ACR38 handles EC internally)

Response: SW1 SW2
  SW1 = 90 (success)
  SW2 = EC value (0xFF, 0xFB, 0xF7, 0xF3...)
```

---

## Memory Write Commands (Require PSC Verified)

### Write Main Memory (Single Byte)
```
Command:  FF D0 00 AA 01 VV
  AA = Address (0x00-0xFF)
  VV = Value byte

Response: 00 (success) or error
```

### Write Main Memory (Multiple Bytes)
```
Command:  FF D0 00 AA LL VV1 VV2 ...
  AA = Start address
  LL = Length
  VV... = Data bytes

Response: 00 (success) or error
```

### Change PSC (After Successful Verify)
```
Command:  FF D2 00 00 03 NP1 NP2 NP3
  NP1, NP2, NP3 = New 3-byte PSC

Response: 00 (success) or error

Note: Can only be done AFTER successful PSC verification in same session
```

---

## Protection Commands (OTP - IRREVERSIBLE)

### Write Protection Bit (Permanently Protect Byte)
```
Command:  FF 8E 00 AA 01 00
  AA = Byte address (0x00-0x1F only)

Response: 00 (success) → bit permanently set to 1
Warning: CANNOT BE UNDONE
```

### Read Protection Bits
```
Command:  FF B8 00 00 04
Response: 4 bytes = 32 protection bits
```

---

## Error Codes (CT-API / ACR38)

| Code | Meaning |
|------|---------|
| 0x00 / 90 00 | Success |
| 0x06 / 63 00 | No card / card removed |
| 0x05 / 6D 00 | Protocol mismatch |
| 0x12 / 63 CX | PSC verify failed, X = remaining attempts |
| 0x1F / 69 83 | Write protected / authentication failed |
| 0x25 / 69 85 | Conditions not satisfied (PSC not verified) |
| 0xFFF8 (-8) | CT_init failed — device not bound to SZCCID |

---

## Complete CT-API Python Example

```python
import ctypes

# Load 32-bit DLL
dll = ctypes.windll.LoadLibrary(r"C:\path\CTAlc001.dll")

dll.CT_init.argtypes = [ctypes.c_uint16, ctypes.c_uint16]
dll.CT_init.restype = ctypes.c_int16

dll.CT_data.argtypes = [
    ctypes.c_uint16,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_uint16,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(ctypes.c_uint16),
    ctypes.POINTER(ctypes.c_ubyte),
]
dll.CT_data.restype = ctypes.c_int16

dll.CT_close.argtypes = [ctypes.c_uint16]
dll.CT_close.restype = ctypes.c_int16

def send_cmd(cmd_bytes, expect_len=256):
    ctn = ctypes.c_uint16(0)
    dad = (ctypes.c_ubyte * 1)(0x00)
    sad = (ctypes.c_ubyte * 1)(0x00)
    cmd = (ctypes.c_ubyte * len(cmd_bytes))(*cmd_bytes)
    lenr = ctypes.c_uint16(expect_len)
    resp = (ctypes.c_ubyte * expect_len)()
    
    rc = dll.CT_data(ctn, dad, sad, len(cmd_bytes), cmd, ctypes.byref(lenr), resp)
    if rc != 0:
        return None
    return bytes(resp[:lenr.value])

# Initialize
if dll.CT_init(ctypes.c_uint16(0), ctypes.c_uint16(100)) != 0:
    print("CT_init failed - device not bound to SZCCID")
    exit(1)

# Select card type
send_cmd(bytes([0xFF, 0xA4, 0x00, 0x00, 0x01, 0x05]))

# Read Security Memory
sec = send_cmd(bytes([0xFF, 0xB4, 0x00, 0x00, 0x04]), 4)
print(f"Security Memory: {sec.hex().upper()}")

# Try default PSC
verify = send_cmd(bytes([0xFF, 0x20, 0x00, 0x00, 0x03, 0xFF, 0xFF, 0xFF]))
if verify is not None:
    print("PSC FF FF FF SUCCESS!")
else:
    print("PSC FF FF FF failed")

# Read full memory
mem = send_cmd(bytes([0xFF, 0xB0, 0x00, 0x00, 0x00]), 256)
print(f"Full dump: {mem.hex().upper()}")

dll.CT_close(ctypes.c_uint16(0))
```

---

## Bus Pirate 2-WIRE Raw Commands

### Setup
```
m 2wire
20          # 20kHz clock (SLE4442 max 50kHz)
W 5         # 5V power
P           # Pull-up enable (run TWICE!)
P
L           # LSB first
```

### ATR
```
} { ^ } r:4
# Expected: A2 13 10 91
```

### Read Security Memory
```
{ 0x31 0x01 r:4 }
# Returns: EC PSC1 PSC2 PSC3
```

### Verify PSC (3 bytes)
```
{ 0x33 PSC1 PSC2 PSC3 }
# Returns: 00 on success
```

### Read Main Memory
```
{ 0x30 ADDR r:LEN }
```

### Write Main Memory (after PSC verified)
```
{ 0x38 ADDR VALUE }
```

### Change PSC (after PSC verified)
```
{ 0x39 NP1 NP2 NP3 }
```

---

## ACR38 Pseudo-APDU Quick Reference

| Operation | APDU |
|-----------|------|
| Select SLE4442 | FF A4 00 00 01 05 |
| Read Main Mem | FF B0 00 AA LL |
| Write Main Mem | FF D0 00 AA LL VV... |
| Read Security Mem | FF B4 00 00 04 |
| Verify PSC | FF 20 00 00 02 CC |
| Change PSC | FF D2 00 00 03 PP QQ RR |
| Read Protection | FF B8 00 00 04 |
| Write Protection | FF 8E 00 AA 01 00 |

---

## Default PSC Values by Region/Supplier

| PSC | Region/Supplier | Notes |
|-----|----------------|-------|
| FF FF FF | Factory default (blank cards) | Most common |
| B2 B2 B2 | Chinese OEM suppliers | Very common in Taiwan |
| 55 55 55 | Indian/Middle East | Some vendors |
| 00 00 00 | Lazy config | Rare |
| AA AA AA | Some Korean vendors | Rare |
| FF 00 FF | Specific systems | Rare |

**For Taiwan campus AC cards**: Try FF FF FF first (60-70%), then B2 B2 B2.