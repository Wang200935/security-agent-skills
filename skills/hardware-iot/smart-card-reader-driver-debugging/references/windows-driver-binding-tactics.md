# Windows Driver Binding Tactics for Synchronous Smart Card Readers

## The Core Problem

Windows 10/11 forces Microsoft CCID driver (`wudfusbcciddriver.inf`) on ALL USB CCID devices.
Synchronous cards (SLE4442, SLE4428, AT88SC) need vendor CT-API driver (Alcor `SZCCID.sys`).

**Microsoft CCID limitations for synchronous cards:**
- Returns empty feature list (no `SET_CARD_TYPE`)
- `SCardConnect` with T=0/T=1 fails with `SCARD_E_PROTO_MISMATCH` (0x80100005)
- `SCardConnect` with DIRECT fails with `SCARD_E_NO_SMARTCARD` (0x80100006) — no ATR
- IOCTL interface sealed — only returns version, no CCID escape

---

## Binding Strategies (Ranked by Reliability)

### Strategy 1: Disable Secure Boot + Test Signing + Modified INF (Most Reliable)

**Prerequisites:**
- UEFI/BIOS access to disable Secure Boot
- Admin rights

**Steps:**
```
1. BIOS/UEFI → Security → Secure Boot → Disabled → Save & Exit
2. Boot Windows → Admin PowerShell:
   bcdedit /set testsigning on
3. Reboot
4. Modify SZCCID.INF:
   - Copy driver folder to writable location
   - Edit [DeviceList.NTamd64] section
   - Add your VID/PID:
     %DeviceDesc%=SZCCID_Device, USB\VID_2CE3&PID_9563
   - (Optionally) Re-sign .cat with self-signed cert
5. Install:
   pnputil /add-driver "path\SZCCID.INF" /install
6. Force re-enumeration:
   pnputil /remove-device "USB\VID_2CE3&PID_9563\<instance>"
   pnputil /scan-devices
7. Verify:
   pnputil /enum-devices | findstr "VID_2CE3"
   → Should show driver: szccid.inf (oemXX.inf)
```

**Pros:** Permanent, survives reboots, driver loads correctly
**Cons:** Requires BIOS access, Secure Boot disabled (BitLocker may need suspend)

---

### Strategy 2: Registry Force-Bind (No Reboot, Fragile)

**How it works:** Modify Enum key Service value before device enumeration.

```
# 1. Find device instance
pnputil /enum-devices | findstr "VID_2CE3"
# → Instance: USB\VID_2CE3&PID_9563\5&3639e268&0&4

# 2. Disable device (prevents PnP override)
pnputil /disable-device "USB\VID_2CE3&PID_9563\5&3639e268&0&4"

# 3. Set Service to SzCCID
reg add "HKLM\SYSTEM\CurrentControlSet\Enum\USB\VID_2CE3&PID_9563\5&3639e268&0&4" \
  /v Service /t REG_SZ /d "SzCCID" /f

# 4. Remove WUDF lower filters
reg delete "HKLM\SYSTEM\CurrentControlSet\Enum\USB\VID_2CE3&PID_9563\5&3639e268&0&4\Device Parameters\WUDF" /f

# 5. Re-enable
pnputil /enable-device "USB\VID_2CE3&PID_9563\5&3639e268&0&4"

# 6. Restart Smart Card service
net stop SCardSvr && net start SCardSvr
```

**Why it fails:** `pnputil /enable-device` triggers full PnP re-enumeration.
Windows sees `USB\Class_0B` CompatibleID → picks highest-ranked signed driver → Microsoft CCID.
Registry shows `Service=SzCCID` but actual driver stack is WUDF.

**Pros:** No reboot, no BIOS changes
**Cons:** Doesn't survive enable-device, useless with Secure Boot enabled

---

### Strategy 3: DevCon (If Available)

```
devcon update "SZCCID.INF" "USB\VID_2CE3&PID_9563"
```

**Pros:** Clean Microsoft tool
**Cons:** DevCon deprecated, same Secure Boot constraints

---

### Strategy 4: Buy Native WHQL Driver Reader (Pragmatic)

| Reader | VID:PID | Driver | Works Out of Box |
|--------|---------|--------|------------------|
| ACS ACR38U | 072B:021C | ACS WHQL | ✅ Yes |
| ACS ACR39U | 072B:021D | ACS WHQL | ✅ Yes |
| Alcor AU9540 (orig) | 058F:9540 | Alcor WHQL | ✅ Yes |

**Cost:** NT$300-800 | **Time:** 1 day shipping | **Effort:** Zero

---

## Secure Boot Reality Check

| Scenario | Test Signing | Modified INF | Registry Force-Bind |
|----------|-------------|--------------|---------------------|
| Secure Boot ON | ❌ Blocked | ❌ Rejected | ❌ Overridden by PnP |
| Secure Boot OFF | ✅ Works | ✅ Works | ⚠️ Fragile |

**Bottom line:** If you cannot disable Secure Boot, **buy a different reader**.
The Alcor SZCCID driver is WHQL-signed but only for Alcor's original VIDs (058F).
Rebranded VIDs (2CE3, etc.) are NOT in the INF → Windows rejects binding.

---

## Driver Package Structure (Alcor AU9540)

```
AU9540_V1.7.2.0/
├── program_files/
│   └── AlcorMicro/
│       └── x64/
│           ├── CTAlc001.dll       ← 32-bit PE (CT-API)
│           ├── SZCCID.sys         ← 64-bit kernel driver
│           ├── SzCcidV1900.dll    ← User-mode co-installer
│           ├── SCPwrSetSvr.exe    ← Power management
│           ├── SZCCID.INF         ← Install INF
│           ├── szccid.cat         ← WHQL signature
│           └── AlcGener.sys       ← Generic helper
```

**Key files for modification:**
- `SZCCID.INF` — add VID/PID to `[DeviceList.NTamd64]`
- `szccid.cat` — must be re-signed if INF modified (or use test signing)

---

## INF Modification Template

```ini
; Original section in SZCCID.INF
[DeviceList.NTamd64]
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9540
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9520
%DeviceDesc%=SZCCID_Device, USB\VID_058F&PID_9563  ; Add your PID here
%DeviceDesc%=SZCCID_Device, USB\VID_2CE3&PID_9563  ; Add rebranded VID here
```

**String section:**
```ini
[Strings]
DeviceDesc = "Alcor Micro USB Smart Card Reader"
ProviderName = "AlcorMicro"
```

---

## Verification Checklist

After any binding attempt:

```
1. pnputil /enum-devices /instanceid "USB\VID_xxxx&PID_yyyy\*"
   → Driver should be: szccid.inf (oemXX.inf)
   → NOT: wudfusbcciddriver.inf

2. sc query szccid
   → STATE: RUNNING (not STOPPED)

3. 32-bit Python test:
   C:\Python311-32\python.exe test_ctapi_sle4442.py
   → CT_init(0, 100) must return 0

4. If CT_init returns -8 (0xFFF8):
   → Device still on Microsoft CCID
   → Binding failed
```

---

## Common Mistakes

| Mistake | Result |
|---------|--------|
| Using 64-bit Python with 32-bit CTAlc001.dll | WinError 193 |
| Forgetting pull-up resistors on Bus Pirate | All reads return 0x00 |
| Trying PSC verify without checking EC first | Accidental lockout |
| Modifying INF but not re-signing .cat (Secure Boot ON) | Driver rejected |
| Assuming registry force-bind survives enable-device | PnP overrides to MS CCID |

---

## Emergency Recovery

If you accidentally lock a card (EC exhausted):
1. **Clone path**: Read all 256 bytes → write to blank card (PSC=FFF)
2. **Glitching path**: Voltage/clock glitch to bypass EC (needs ChipWhisperer)
3. **Invasive path**: Decap + microprobe (Flylogic style)

**For campus cards:** Clone path is almost always sufficient.