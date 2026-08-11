# Alcor AU9540 / AK9543 Driver Internals

## Chip Overview

| Chip | USB Interface | Protocol | Notes |
|------|---------------|----------|-------|
| AU9540 | USB 2.0 Full Speed | 2-wire (SLE4442/4428) + I2C + 3-wire | Most common |
| AK9543 | USB 2.0 Full Speed | Enhanced, supports more protocols | Newer |
| AU9520 | USB 1.1 | Legacy | Rare |

**VID/PID:**
- Original Alcor: `VID_058F PID_9540` (AU9540), `VID_058F PID_9520` (AU9520)
- Pincop ICU02 (rebranded): `VID_2CE3 PID_9563`
- Other rebrands: various VIDs (all use same silicon is 0x058F silicon)

---

## Driver Components

### 1. SZCCID.sys (Kernel Driver)
- **Architecture**: AMD64 (64-bit), signed by AlcorMicro (WHQL)
- **Function**: USB device enumeration, endpoint management, I/O pipe handling
- **Interface**: Exposes device path `\\?\USB#VID_xxxx&PID_yyyy#{a5dcbf10-6530-11d2-901f-00c04fb951ed}`
- **IOCTL Interface**: Custom IOCTLs for CT-API communication

### 2. CTAlc001.dll (User-Mode CT-API)
- **Architecture**: PE32 (i386, **32-bit only**)
- **Exports**: `CT_init`, `CT_data`, `CT_close`
- **Protocol**: ISO 7816-4 CT-BCS (Card Terminal - Basic Communication Services)
- **Communication**: Uses `DeviceIoControl` to SZCCID.sys
- **Bitness issue**: Must load from 32-bit process (32-bit Python)

### 3. SzCcidV1900.dll (Co-installer / User-Mode CCID)
- **Purpose**: Windows co-installer, user-mode CCID fallback
- **Loaded by**: Windows driver framework during installation

### 4. SCPwrSetSvr.exe (Power Management Service)
- **Function**: Manages reader power states (suspend/resume)

---

## CT-API Protocol Details

### CT_init(ctn, pn)
- `ctn`: Card Terminal Number (0 = first/only)
- `pn`: Port Number
  - `100` = USB (Alcor proprietary)
  - `1-16` = COM1-COM16 (serial)
- Returns: `0` success, `-8` (0xFFF8) = device not bound to SZCCID

### CT_data(ctn, dad, sad, lenc, command, lenr, response)
- `dad`: Destination Address (0x00 = card)
- `sad`: Source Address (0x00 = terminal)
- `command`: SLE4442 command bytes (ACR38 pseudo-APDU format)
- `response`: Buffer for response
- Returns: `0` success, negative = error

### Command Mapping (CT-API → SLE4442)

The CT-API accepts ACR38-style pseudo-APDUs and translates to SLE4442 2-wire protocol.

| ACR38 Pseudo-APDU | SLE4442 2-Wire Equivalent |
|-------------------|---------------------------|
| `FF B4 00 00 04` | Read Security Memory (Cmd 0x31) |
| `FF B0 00 AA LL` | Read Main Memory (Cmd 0x30) |
| `FF 20 00 00 03 PPP` | Compare Verification Data (Cmd 0x33) |
| `FF D0 00 AA 01 VV` | Update Main Memory (Cmd 0x38) |
| `FF D2 00 00 03 NNN` | Update Security Memory (Cmd 0x39) |

---

## INF File Structure (SZCCID.INF)

### Key Sections

```ini
[Version]
Signature="$WINDOWS NT$"
Class=SmartCardReader
ClassGuid={50DD5230-BA8A-11D1-BF5D-0000F805F530}
Provider=%ProviderName%
DriverVer=01/01/2020,1.7.2.0
CatalogFile=szccid.cat

[Manufacturer]
%ProviderName%=AlcorMicro,NTamd64

[AlcorMicro.NTamd64]
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9540
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9520
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9563
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9550

[SZCCID_Device.NT]
CopyFiles=SZCCID_Files
AddReg=SZCCID_AddReg

[SZCCID_Device.NT.Services]
AddService=SZCCID,0x00000002,SZCCID_Service

[SZCCID_Service]
DisplayName=%SZCCID_SvcDesc%
ServiceType=1
StartType=3
ErrorControl=1
ServiceBinary=%12%\SZCCID.sys

[SZCCID_AddReg]
HKR,,"DeviceInterfaceGUID",,%{A5DCBF10-6530-11D2-901F-00C04FB951ED}%
HKR,,"CTAPI_DLL",,"CTAlc001.dll"

[SZCCID_Files]
SZCCID.sys
CTAlc001.dll
SzCcidV1900.dll
SCPwrSetSvr.exe
AlcGener.sys

[Strings]
ProviderName="AlcorMicro"
DeviceDesc="Alcor Micro USB Smart Card Reader"
SZCCID_SvcDesc="Alcor Micro Smart Card Reader Driver"
```

### Adding Rebranded VID/PID

To support Pincop ICU02 (`VID_2CE3 PID_9563`):

```ini
[AlcorMicro.NTamd64]
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9540
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9520
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9563
%DeviceDesc%=SZCCID_Device, USB\VID_2CE3&PID_9563   ; ADD THIS LINE
%DeviceDesc%=SZCCID_Device, USB\VID_2CE3&PID_9540   ; ADD IF NEEDED
```

---

## Communication Flow

```
32-bit Python App
       │
       ▼
CTAlc001.dll (32-bit)
       │
       ├── CT_init(0, 100)
       │    └── DeviceIoControl(SZCCID.sys, IOCTL_CT_INIT) → opens device handle
       │
       ├── CT_data(...)
       │    └── DeviceIoControl(SZCCID.sys, IOCTL_CT_DATA)
       │         ├── Sends ACR38 pseudo-APDU
       │         ├── SZCCID.sys translates to 2-wire protocol
       │         ├── USB bulk OUT → AU9540
       │         ├── AU9540 drives CLK/I/O/RST lines to SLE4442
       │         ├── SLE4442 responds
       │         ├── USB bulk IN → AU9540 → SZCCID.sys
       │         └── Response back to app
       │
       └── CT_close(ctn)
            └── DeviceIoControl(SZCCID.sys, IOCTL_CT_CLOSE) → closes handle
```

---

## Known Issues & Workarounds

### 1. CTAlc001.dll is 32-bit Only
**Problem**: 64-bit Python → `WinError 193`
**Solution**: Use 32-bit Python embed package
```
https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-win32.zip
```

### 2. Secure Boot Blocks Rebranded VIDs
**Problem**: Modified INF not accepted; PnP prefers Microsoft CCID
**Solutions**:
- Disable Secure Boot in BIOS
- Buy ACS ACR38U (native WHQL for all VIDs it supports)
- Buy Alcor AU9540 with original VID (058F:9540)

### 3. PnP Re-enumeration Overrides Registry
**Problem**: `pnputil /enable-device` reverts to WUDFRd
**Root cause**: `USB\Class_0B` CompatibleID matches Microsoft CCID INF
**Workaround**: None reliable — disable Secure Boot + modify INF

### 4. CT_init Returns -8 (ERR_CT)
**Meaning**: SZCCID.sys not bound to device
**Check**:
```
pnputil /enum-devices → should show szccid.inf (not wudfusbcciddriver.inf)
sc query szccid → should be RUNNING
```

### 5. CT_data Returns Garbage / Timeout
**Causes**:
- Wrong command format (check ACR38 pseudo-APDU mapping)
- Card not powered (check reader LED)
- Pull-up resistors missing (Bus Pirate: `P` command ×2)
- Wrong clock speed (SLE4442 max 50kHz, try 20kHz)

---

## AU9540 Firmware Versions

| Version | Date | Notes |
|---------|------|-------|
| V1.7.2.0 | 2020 | Current stable, WHQL signed |
| V1.6.x | 2018 | Older, may lack Win10 20H2+ support |

**Firmware update**: Not typically user-updatable. Requires Alcor factory tool.

---

## USB Endpoints (AU9540)

| Endpoint | Direction | Purpose |
|----------|-----------|---------|
| EP 1 OUT | Host → Device | Commands |
| EP 1 IN | Device → Host | Responses |
| EP 2 IN | Device → Host | Status/Interrupt |

---

## Registry Keys (After Installation)

```
HKLM\SYSTEM\CurrentControlSet\Services\SZCCID
  ImagePath = \SystemRoot\System32\drivers\SZCCID.sys
  Type = 1 (Kernel)
  Start = 3 (Demand)
  ErrorControl = 1

HKLM\SYSTEM\CurrentControlSet\Enum\USB\VID_058F&PID_9540\<instance>
  Service = SZCCID
  Driver = {50DD5230-BA8A-11D1-BF5D-0000F805F530}\0000
  LowerFilters = (empty or none)

HKLM\SYSTEM\CurrentControlSet\Control\Class\{50DD5230-BA8A-11D1-BF5D-0000F805F530}\0000
  DriverDesc = Alcor Micro USB Smart Card Reader
  ProviderName = AlcorMicro
  MatchingDeviceId = USB\VID_058F&PID_9540
  InfPath = oem58.inf
```

---

## Testing Checklist

```
□ 32-bit Python runs (struct.calcsize('P')*8 == 32)
□ CTAlc001.dll loads without WinError 193
□ CT_init(0, 100) returns 0
□ CT_data(FF B4 00 00 04) returns 4 bytes (EC + PSC)
□ EC byte reads correctly (0xFF = 3 attempts)
□ PSC verify with FF FF FF works (if factory default)
□ Main memory read returns 256 bytes
□ Write command works after PSC verify
```

---

## Source Code References

- **Linux kernel**: `drivers/usb/serial/alcorser.c` (related serial driver)
- **pcsc-lite**: `src/hotplug_libusb.c` (USB CCID handling)
- **OpenCT**: `drivers/alcormicro.c` (CT-API implementation reference)

Note: Alcor does not publish CTAlc001.dll source. Protocol reverse-engineered from ACR38 spec + USB captures.