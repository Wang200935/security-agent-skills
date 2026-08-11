# Identifying Flipper Zero Hardware Variant

Before flashing any custom firmware, you MUST identify which variant of Flipper Zero the user has. Flashing the wrong variant can brick the device (different bootloader target, different flash layout).

## Quick check via `device_info`

```bash
~/.hermes/hermes-agent/venv/bin/python <<'PY'
import serial, time
ser = serial.Serial('/dev/cu.usbmodemflip_Ur1nicar1', 230400, timeout=2)
time.sleep(0.3)
ser.reset_input_buffer()
ser.write(b'device_info\r\n')
time.sleep(0.5)
print(ser.read(ser.in_waiting).decode('utf-8', errors='replace'))
ser.close()
PY
```

## Fields to inspect

| Field | What to look for | Maps to variant |
|---|---|---|
| `firmware_origin_fork` | `Official` = real hardware. Anything else = clone | real / original |
| `hardware_name` | `Ur1nicar`, `Bobcat`, etc. (random cute names per batch) | Random, NOT a variant identifier |
| `hardware_target` | `7` = F7 (real Flipper Zero) | real |
| `hardware_region` | Region provisioning code | NOT a variant identifier |
| `firmware_branch` | `release`, `dev`, `rc` | NOT a variant identifier |

## Real hardware identification

The strongest signal is `firmware_origin_fork`:

```
firmware_origin_fork        : <something>
firmware_origin_git         : https://github.com/...
```

- `firmware_origin_fork: ` (empty after `:`) and `firmware_origin_git: https://github.com/flipperdevices/flipperzero-firmware` → **Official / real hardware**
- `firmware_origin_fork: Momentum` → real hardware running Momentum (already custom)
- `firmware_origin_fork: Unleashed` → real hardware running Unleashed
- `firmware_origin_fork: ` (empty) + `firmware_origin_git: https://github.com/...clone...` → clone hardware

For clone/clipper hardware (sold on AliExpress, Taobao, etc. at lower prices):
- The device may report as `Flipper` in the origin field (instead of empty)
- Hardware target may still be 7 (F7) but the chip marking differs
- These need `clone` or `clipper` firmware variants

## Variant naming across forks

| Real hardware | Clone | Clipper |
|---|---|---|
| **Momentum-CN**: `original` | `clone` | `clipper` |
| **Unleashed**: `f7` (real) | `f7` (clone) — single variant | n/a |
| **Xtreme**: `f7` for both | (same) | n/a |
| **Official Flipper**: only one variant for F7 | n/a | n/a |

The naming convention differs by fork. When downloading from a fork's release page, **always check the README or release notes for which asset matches your device**.

## Firmware variant matching cheat sheet

For each user query, check:

1. **What does their `device_info` say for `firmware_origin_fork`?**
2. **What does their `firmware_origin_git` point to?**
3. **Match that against the release asset names.**

Example: User has `firmware_origin_fork:` (empty) and `firmware_origin_git: https://github.com/flipperdevices/flipperzero-firmware`. They want Momentum-CN. → download `momentum-fw-cn-v1.1.4-original.tgz` (NOT clone, NOT clipper).

## If you're not sure

If the device_info output is ambiguous (clone pretending to be real, etc.), the safest bet is:

1. Ask the user where they bought it
2. Check the back of the Flipper for a sticker/seal from Flipper Devices (real) vs nothing (clone)
3. Default to the safe choice: real/original variant. If that fails to flash, switch to clone.

## Pitfalls

- **Don't trust `hardware_name`** — `Ur1nicar`, `Bobcat`, `Dolphin-7` etc. are random cute names, not variant identifiers
- **Don't trust `hardware_region`** — this is the WiFi/provisioning region (TW, EU, US), not a firmware variant
- **The `origin` field can lie** — clones can be flashed with official firmware and report `Official` origin. Cross-check with the physical device (no Flipper Devices sticker = clone)
- **Custom forks add `firmware_origin_fork` field** — official firmware's `device_info` doesn't always include this. Don't panic if it's missing on official.
- **Hardware version 12 with `Ur1nicar` name and TW region** (the case from 2026-06-30 session) = real hardware, use `original` variant for Momentum-CN