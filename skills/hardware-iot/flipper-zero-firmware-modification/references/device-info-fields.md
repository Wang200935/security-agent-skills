# Flipper Zero `device_info` Field Reference

Verified against stock Official firmware 1.4.3 (commit `8622f1a2`, built 2025-05-12) on 2026-06-30.

## Complete Output (verbatim)

```
device_info_major             : 2
device_info_minor             : 4
hardware_model                : Flipper Zero
hardware_uid                  : DAE9650127E18000
hardware_otp_ver              : 2
hardware_timestamp            : 1720928799
hardware_ver                  : 12
hardware_target               : 7
hardware_body                 : 9
hardware_connect              : 6
hardware_display              : 2
hardware_color                : 2
hardware_region               : 4
hardware_region_provisioned   : TW
hardware_name                 : Ur1nicar
firmware_commit               : 8622f1a2
firmware_commit_dirty         : false
firmware_branch               : 1.4.3
firmware_branch_num           : 0
firmware_version              : 1.4.3
firmware_build_date           : 05-12-2025
firmware_target               : 7
firmware_api_major            : 87
firmware_api_minor            : 1
firmware_origin_fork          : Official
firmware_origin_git           : https://github.com/flipperdevices/flipperzero-firmware
```

## Field-by-field meaning

### Identity / hardware

| Field | Meaning |
|---|---|
| `device_info_major` / `device_info_minor` | Protobuf schema version running on this firmware. 2.4 = current. |
| `hardware_model` | Always `Flipper Zero` on real hardware. |
| `hardware_uid` | Unique 64-bit ID per device (hex string of bytes). |
| `hardware_otp_ver` | One-Time-Programmable memory version. |
| `hardware_timestamp` | Production timestamp (Unix epoch seconds). |
| `hardware_ver` | Hardware revision. |
| `hardware_target` | SoC target. `7` = STM32WB55 (f7 = standard Flipper Zero). |
| `hardware_body` | Body revision. |
| `hardware_connect` | Connector revision. |
| `hardware_display` | Display revision. |
| `hardware_color` | Body color code. |
| `hardware_region` | Region code (numeric). `4` = TW. |
| `hardware_region_provisioned` | Provisioned region. `TW`, `EU`, `US`, etc. — controls allowed Sub-GHz bands. |
| `hardware_name` | User-set name. Defaults to Flipper's hostname. |

### Firmware

| Field | Meaning | Notes |
|---|---|---|
| `firmware_commit` | Git commit SHA the firmware was built from. | **NOT** a fork discriminator — forgeries are common, official commit may match a fork built on top. |
| `firmware_commit_dirty` | `true` if built from uncommitted source. | Forks sometimes mark this `true`. |
| `firmware_branch` | Source branch name. | "1.4.3" for stock release. "v1.1.4" / "Momentum" for forks. |
| `firmware_branch_num` | Numeric branch ID. | |
| `firmware_version` | Human-readable version. | Stock matches release version. Forks usually match upstream they were forked from. |
| `firmware_build_date` | Build date string. | |
| `firmware_target` | Same as hardware_target. | |
| `firmware_api_major` / `firmware_api_minor` | SDK API version. | 87.1 = latest as of 1.4.3. |
| **`firmware_origin_fork`** | **Authoritative fork identifier.** | `Official` = stock. `Momentum` / `Unleashed` / `Xtreme` / etc. for forks. |
| `firmware_origin_git` | Source repo URL the fork was built from. | Forks often point to their own repo, but stock always points to flipperdevices/flipperzero-firmware. |

## Authoritative fork detection rule

**Only `firmware_origin_fork` (and secondarily `firmware_origin_git`) is reliable.**

The other firmware fields are unreliable for fork detection:

- `firmware_commit` — can be spoofed, shared between stock and forks built on same source
- `firmware_version` — forks usually mirror upstream version
- `firmware_branch` — same
- protobuf version (from qFlipper RPC) — `0.25` is current for stock 1.4.3 too, not a Momentum marker

## CLI usage

```bash
# Read device_info via serial CLI (default 115200 baud works for read-only)
~/.hermes/hermes-agent/venv/bin/python <<'PY'
import serial, time
s = serial.Serial('/dev/cu.usbmodemflip_Ur1nicar1', 115200, timeout=3)
s.reset_input_buffer(); s.reset_output_buffer()
time.sleep(0.2)
s.write(b'device_info\r\n')
time.sleep(1)
print(s.read(4000).decode(errors='replace'))
s.close()
PY
```

Output includes ASCII art banner first, then the `>: device_info` prompt echo, then key:value lines. Filter on lines starting with the field name you want.

## See also

- `flipper-zero-firmware-modification` SKILL.md → "Is this Momentum or Official?" decision tree
- `flipper-zero-backup` SKILL.md → "Verify Firmware After Any Change" section