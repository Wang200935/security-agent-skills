# Live `device_info` Reference Output — Flipper Zero 1.4.3 Official

Captured 2026-06-30 via pyserial at 115200 baud on `/dev/cu.usbmodemflip_Ur1nicar1` (real device UID redacted example).

## `device_info` raw output

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
hardware_name                 : <your-device-name>
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

## `info device` (richer alias — same fields, dotted + radio block)

```
format.major                  : 3
format.minor                  : 3
hardware.model                : Flipper Zero
hardware.uid                  : DAE9650127E18000
hardware.otp.ver              : 2
hardware.timestamp            : 1720928799
hardware.ver                  : 12
hardware.target               : 7
hardware.body                 : 9
hardware.connect              : 6
hardware.display              : 2
hardware.color                : 2
hardware.region.builtin       : 4
hardware.region.provisioned   : TW
hardware.name                 : <your-device-name>
firmware.commit.hash          : 8622f1a2
firmware.commit.dirty         : false
firmware.branch.name          : 1.4.3
firmware.branch.num           : 0
firmware.version              : 1.4.3
firmware.build.date           : 05-12-2025
firmware.target               : 7
firmware.api.major            : 87
firmware.api.minor            : 1
firmware.origin.fork          : Official
firmware.origin.git           : https://github.com/flipperdevices/flipperzero-firmware
radio.alive                   : true
radio.mode                    : Stack
radio.fus.major               : 1
radio.fus.minor               : 2
radio.fus.sub                 : 0
radio.fus.sram2b              : 16K
radio.fus.sram2a              : 0K
radio.fus.flash               : 24K
radio.stack.type              : 3
radio.stack.major             : 1
radio.stack.minor             : 20
radio.stack.sub               : 0
```

## `info power`

```
format.major                  : 2
format.minor                  : 1
charge.level                  : 100
charge.state                  : charged
charge.voltage.limit          : 4208
battery.voltage               : 4146
battery.current               : 0
battery.temp                  : 33
battery.health                : 100
capacity.remain               : 2100
capacity.full                 : 2100
capacity.design               : 2100
```

## Field meanings cheat-sheet (verified against firmware 1.4.3 source)

| Field | Meaning | Health indicator |
|---|---|---|
| `hardware_ver` | Mainboard version (PCB revision) | 12 = current production |
| `hardware_body` | Mainboard variant | 9 = current, supports all accessories |
| `hardware_connect` | GPIO / external connector rev | 6 = 5V-tolerant pins, full accessory support |
| `hardware_display` | Display driver rev | 2 = current |
| `hardware_color` | Color of plastic case | 2 = white (other values: 1=clear, 3=black limited) |
| `hardware_region.builtin` | Factory region (from OTP) | 4 = universal |
| `hardware_region.provisioned` | Region set by `Region Provisioning` (qFlipper does this on first boot) | TW/UK/EU/US/RU/... — determines allowed SubGHz bands |
| `hardware_otp_ver` | One-time-programmable memory version | 2 = current |
| `hardware_timestamp` | Unix time when UID was burned into OTP at factory | used for warranty & lot tracking |
| `hardware_uid` | Unique 64-bit device ID | `0xDAE9650127E18000` style |
| `firmware_target` | STM32 chip family | 7 = STM32WB55 (Flipper Zero) |
| `firmware_api_major` / `.minor` | Firmware RPC API version | 87.1 = latest 1.4.3 |
| `firmware_origin_fork` | **THE definitive fork identifier** | "Official" = stock; "Momentum"/other = custom |
| `firmware_origin_git` | Git URL of the fork | should equal `https://github.com/flipperdevices/flipperzero-firmware` for Official |
| `firmware_commit_dirty` | true = uncommitted local changes in firmware build | true is rare for stock releases |
| `charge.level` | Battery percentage | 0-100 |
| `charge.state` | `charging` / `charged` / `discharging` / `not_charging` | expect `charged` when plugged in at 100% |
| `battery.health` | 100 = healthy; <80 = degraded | 100 = no replacement needed |
| `battery.temp` | °C | 20-40 normal, >45 = throttling, >55 = shutdown |
| `capacity.remain` / `.full` / `.design` | mAh | `remain == full` = full charge; `full/design` ratio <0.8 = degraded |
| `radio.alive` | SubGHz radio (CC1101) responding | true = healthy |

## Common false positives — what is NOT a fork marker

| Signal | Looks like Momentum? | Reality |
|---|---|---|
| `protobuf version: 0.25` (from qFlipper RPC handshake log) | ❌ no | Official 1.4.3 also reports 0.25 |
| `firmware_commit: 8622f1a2` not in `directory.json` | ❌ no | `directory.json` does NOT carry commit strings; only `version` + `timestamp` + `files[].sha256` |
| qFlipper "skipping to update — already installed" | ❌ no | Usually means `/ext/update/f7-update-1.4.3/` residual files from a prior `storage write_chunk` session; check `/ext/update/` and clean |
| `firmware_version: 1.4.3` showing latest version | ❌ no | Custom forks built on top of Official source inherit the upstream version string |
| `firmware_branch: 1.4.3` | ❌ no | Same — branch string is inherited from upstream |

**If `firmware_origin_fork` says "Official" AND `firmware_origin_git` matches `https://github.com/flipperdevices/flipperzero-firmware` → stock.** No need to investigate other signals.

## Battery state reference (Taiwan region device, plugged in)

| charge.level | charge.state | Expected meaning |
|---|---|---|
| 100 | charged | USB plugged, full charge reached, top-off maintenance |
| 99-95 | charging | USB plugged, finishing last 5% (CC → CV phase) |
| <95 | discharging | Not plugged in |
| 100 | discharging | Plugged in but USB providing insufficient current (low-power port or bad cable) |

If `charge.level == 100` and `charge.state == discharging`, **the USB cable or port is bad** — flipper is drawing from battery even while plugged. Common with hub ports or damaged cables.