# Flipper Zero Backup — No SD Card Mode

When the user hands you a Flipper Zero **without an SD card inserted**, the standard 3-layer backup collapses: `/int` and `/ext` filesystems refuse to mount, qFlipper-cli hangs, and `update backup` fails.

## Verified failure modes (from live session 2026-06-30)

```
storage list /int       → Storage error: filesystem not ready
storage stat /int       → Storage error: filesystem not ready
update backup           → requires /ext path (no SD = blocked)
qFlipper-cli backup     → hangs at "RPC session starting"; or
                          errors with "Permission error while locking the device"
                          (because previous run left a stale serial lock)
```

## What still works without SD card

| Method | Output |
|---|---|
| `serial.Serial('/dev/cu.usbmodemflip_*', 230400)` + `device_info` | Full hardware UID, region, firmware version, build date, commit, API major/minor, origin fork |
| `info device` / `info power` / `info power_debug` | Detailed power/battery state |
| `top` | List of running system services |
| `free` / `free_blocks` | Heap state, max block |
| `uptime` | Device uptime |
| `help` | Full CLI command list |
| `qFlipper-cli firmware <file.dfu>` | Flash firmware (DFU mode still works — no SD needed) |

## What does NOT work without SD card

| Lost | Reason |
|---|---|
| `/int` settings | storage service not mounted |
| Dolphin level/XP | stored in /int |
| Bluetooth pairing list | stored in /int/.bt |
| U2F keys | stored in /int/nfc.u2f |
| `/ext/*` (subghz, nfc, IR, scripts, apps) | ext filesystem doesn't exist |
| Theme/animations/dolphin assets | on SD card |
| Asset packs | on SD card |

## Workflow when user says "我給你沒有 SD 卡的 Flipper"

1. **Confirm device presence via pyserial** — connect at 230400 baud, send `\r\n`, then `device_info` to read UID/region/firmware.
2. **Record everything serial CLI can give you**: device_info, info device, info power, top, free, uptime, help.
3. **Skip the qFlipper-cli backup** — it will hang or fail. Document why in MANIFEST.
4. **Pre-download official firmware from CDN** — `https://update.flipperzero.one/firmware/directory.json`, parse `release` channel, fetch `update_tgz` and `full_dfu`. This works offline (no Flipper needed).
5. **Document what's missing** in MANIFEST.txt so the user knows to re-pair BT / reset Dolphin level after a flash.

## Recovery script template (no SD card)

```python
#!/usr/bin/env python3
import serial, time, sys

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbmodemflip_Unknown"
ser = serial.Serial(PORT, 230400, timeout=2)
time.sleep(0.3)

def cmd(c, wait=0.5):
    ser.reset_input_buffer()
    ser.write(c.encode() + b'\r\n')
    time.sleep(wait)
    return ser.read(ser.in_waiting).decode('utf-8', errors='replace')

# Essential reads
print(cmd('device_info'))    # hardware UID, firmware version, commit, region
print(cmd('info device'))    # power/charger state
print(cmd('top'))            # running services
print(cmd('free'))           # memory state
print(cmd('uptime'))
print(cmd('help'))           # full CLI surface

# Things that WILL fail (document them)
print("--- /int requires SD card ---")
print(cmd('storage list /int'))     # filesystem not ready
print(cmd('update backup'))         # needs /ext path

ser.close()
```

## Why qFlipper-cli hangs on no-SD

The RPC flow does:
1. System Protobuf Version (OK)
2. Property Get (OK)
3. **Storage Info @/ext** ← blocks here waiting for SD
4. ...

The backup command waits for `/ext` to mount before issuing `Storage List @/int`. With no SD, it polls forever.

## Pitfalls

- **Don't use qFlipper-cli backup** on a no-SD Flipper — it appears to work for ~1 second then hangs at "Storage List @/int SUCCESS". The timeout in the user-facing script should be ≤30s, then kill and use pyserial fallback.
- **Don't pkill qFlipper-cli blindly during a backup** — it leaves the serial port in a locked state that requires `pkill -9` + USB replug to clear. Next backup will fail with "Permission error while locking the device".
- **The flipper serial port path** (`/dev/cu.usbmodemflip_<name>`) is stable per device. Capture it once at start of session.
- **The firmware version reported by `device_info` is the truth** — not what you find on GitHub releases or the CDN directory.json. Use it to decide if a flip-back is needed.