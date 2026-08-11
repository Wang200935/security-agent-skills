# Session Reference: Pincop ICU02 / Alcor AK9543 + SLE4442 (2026-07-01)

## Device Details
- **Reader**: Pincop (品可) ICU02
- **USB ID**: VID=2CE3, PID=9563
- **Controller**: Alcor AK9543 (same family as AU9540)
- **Target Card**: Siemens SLE4442 synchronous memory card (256 bytes + 3-byte PIN + error counter)
- **OS**: Windows 10 (tested via SSH to Windows machine)
- **Secure Boot**: ENABLED (blocks test signing)

## Full Attack History — What Worked and What Didn't

### Phase 1: PC/SC via Microsoft CCID (FAILED)
| Attempt | Result | Error |
|---------|--------|-------|
| `SCardListReadersW` | Found "Alcor Micro USB Smart Card Reader 0" | — |
| `SCardConnectW(DIRECT)` | NO_SMARTCARD | 0x00000006 |
| `SCardConnectW(T0)` | NO_SMARTCARD | 0x00000006 |
| `SCardConnectW(T1)` | NO_SMARTCARD | 0x00000006 |
| `SCardConnectW(RAW)` | NO_SMARTCARD | 0x00000006 |
| All 3 registered reader names | NO_SMARTCARD | 0x00000006 |

**Why**: MS CCID tries ISO 7816 ATR negotiation. SLE4442 is synchronous — no ATR → card appears absent.

### Phase 2: Direct DeviceIoControl (FAILED)
| IOCTL | Result |
|-------|--------|
| `CreateFileW(\\?\USB#VID_2CE3...#{a5dcbf10...})` | **Opens OK** (handle valid) |
| GET_FEATURE_REQUEST | `ERROR_INVALID_FUNCTION` |
| SET_CARD_TYPE (various) | `ERROR_INVALID_FUNCTION` |
| POWER (cold/warm) | `ERROR_INVALID_FUNCTION` |
| TRANSMIT | `ERROR_INVALID_FUNCTION` |
| SET_PROTOCOL | `ERROR_INVALID_FUNCTION` |
| IS_PRESENT | `ERROR_INVALID_FUNCTION` |
| CCID_ESCAPE (0x004) with raw CCID msgs | `ERROR_INVALID_FUNCTION` |
| WriteFile/ReadFile | `written=0` / no data |

**Only 2 IOCTLs work**:
- `+0x028` → empty ack
- `+0x038` → `02000000` (DWORD = version/capabilities)

**Conclusion**: WUDF CCID is a sealed driver. No CCID escape or SET_CARD_TYPE possible.

### Phase 3: SZCCID Installation + Registry Force-Bind (FAILED)
| Step | Result |
|------|--------|
| Install SZCCID via `pnputil /add-driver` | OK (oem58.inf) |
| `sc start SzCCID` | RUNNING (but `Enum\Count = 0`) |
| Registry: `Service = SzCCID` | Value written |
| Registry: `LowerFilters = ∅` | Value written |
| Registry: delete WUDF params | Done |
| `pnputil /enable-device` | **PnP re-binds to WUDF CCID** |
| `CT_init(0, 0..255)` via 32-bit Python | All return 248 (= -8 signed = ERR_CT) |

**Why**: PnP re-enumeration matches `USB\Class_0B&SubClass_00&Prot_00` CompatibleID → selects highest-ranked **signed** driver (Microsoft inbox). Registry Service value persists but is ignored.

### Phase 4: Test Signing (FAILED)
| Step | Result |
|------|--------|
| `bcdedit /set testsigning on` | "Protected by Secure Boot policy" |
| Modified SZCCID.INF (added VID_2CE3) | Written to `C:\Temp\SZCCID_Pincop\` |
| `pnputil /add-driver SZCCID.INF /install` | "INF does not contain digital signature" |

**Why**: Secure Boot prevents test signing. No way to install unsigned INF without disabling Secure Boot in UEFI first.

### Phase 5: Modified INF with CatalFile removed (FAILED)
- Removed `CatalogFile=SzCCID.cat` line from INF
- Still rejected: Windows requires digital signature even without catalog reference

## Key Findings Summary

1. **MS WUDF CCID = sealed box** — only 2 benign IOCTLs respond, no smartcard/CCID functionality exposed via DeviceIoControl
2. **Registry force-bind = cosmetic** — PnP overrides Service/Driver on enable-device
3. **Secure Boot = hard wall** — no test signing, no unsigned INF installation
4. **CTAlc001.dll is 32-bit PE32** even in x64 driver package — must use 32-bit Python
5. **CT_init returns -8 (0xFFF8)** when SZCCID.sys isn't bound to the device
6. **The only working path**: Disable Secure Boot → test signing → modified INF → CT-API

## 32-bit Python Setup (Verified Working)
```powershell
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-win32.zip" -OutFile "C:\Temp\py311-32.zip"
Expand-Archive -Path C:\Temp\py311-32.zip -DestinationPath C:\Python311-32 -Force
C:\Python311-32\python.exe -c "import struct; print(struct.calcsize('P')*8)"
# → 32
```

## CT-API Status (After Registry Bind, 32-bit Python)
```python
dll = ctypes.CDLL(r"...\CTAlc001.dll")
CT_init(0, 0)  # → 248 (unsigned) = -8 signed = ERR_CT
# All pn values 0-255 return same error
# This confirms DLL cannot communicate with SZCCID.sys
# because the device is still bound to WUDF CCID
```

## Resolution Options (Priority Order)
1. **Disable Secure Boot in UEFI** → reboot → `bcdedit /set testsigning on` → reboot → install modified SZCCID.INF → `CT_init` should return 0
2. **Replace reader** — ACS ACR38U (蝦皮搜 `ACR38U`, NT$300-800) or Alcor AU9540 with VID_058F PID_9540 (NT$150-350)

## Vendor DLL API (CTAlc001.dll — for reference when binding works)

### Exports Confirmed
```
CT_init(ctn: uint16, pn: uint16) -> int16
CT_data(ctn, dad*, sad*, lenc, cmd*, lenr*, rsp*) -> int16
CT_close(ctn) -> int16
```

### Also has IC_* API (not tested — requires working driver)
```
IC_InitComm(port=100) → HANDLE
IC_ExitComm(handle)
IC_Check_4442(handle) → 0 if card present
IC_InitType(handle, 0x10) → set SLE4442 mode
IC_Read(handle, offset, len, buf)
IC_Write(handle, offset, len, buf)
IC_CheckPass_4442hex(handle, "ffffff\0")
```

## Cross-References
- `smart-card-driver-debug` skill → complete driver binding tactics
- `smart-card-usb-direct` skill → vendor DLL API patterns and pitfalls
- `references/windows-driver-binding-tactics.md` → all binding methods tested
- `references/alcor-au9540-driver-notes.md` → driver internals, bitness, INF structure
