# Flipper Zero — Verified Research Notes (2026-06-29)

## Authoritative URLs (verified live)

| Purpose | URL |
|---|---|
| Firmware manifest (JSON) | `https://update.flipperzero.one/firmware/directory.json` |
| Latest official release | **1.4.3** (2025-12-05) |
| Release update .tgz | `https://update.flipperzero.one/builds/firmware/1.4.3/flipper-z-f7-update-1.4.3.tgz` |
| Release full .dfu | `https://update.flipperzero.one/builds/firmware/1.4.3/flipper-z-f7-full-1.4.3.dfu` |
| Release updater .dfu | `https://update.flipperzero.one/builds/firmware/1.4.3/flipper-z-f7-updater-1.4.3.dfu` |
| **NOT THIS** (qFlipper app) | `https://update.flipperzero.one/qFlipper/directory.json` |
| GitHub source repo | `https://github.com/flipperdevices/flipperzero-firmware` |
| qFlipper source repo | `https://github.com/flipperdevices/qFlipper` |

**Note**: GitHub releases on `flipperzero-firmware` contain NO prebuilt firmware binaries — only source tarballs. All `.tgz`/`.dfu` files are on the `update.flipperzero.one` CDN, fetched via the directory.json manifest.

## Firmware manifest JSON schema

```json
{
  "channels": [
    {
      "id": "release" | "release-candidate" | "development",
      "title": "...",
      "description": "...",
      "versions": [
        {
          "version": "1.4.3",
          "changelog": "...",
          "timestamp": 1764963226,
          "files": [
            {
              "url": "https://update.flipperzero.one/builds/firmware/1.4.3/...",
              "target": "f7" | "f18" | "any",
              "type": "update_tgz" | "full_dfu" | "updater_dfu" | "resources_tgz" | "scripts_tgz" | "core2_firmware_tgz" | "full_bin" | "firmware_elf" | "appsymbols_tgz" | "debugapps_tgz" | "sdk_zip" | "full_json" | "updater_json" | "updater_bin" | "updater_elf",
              "sha256": "hex..."
            }
          ]
        }
      ]
    }
  ]
}
```

### Useful `type` values for backup/restore

| Type | What it is | When to use |
|---|---|---|
| `update_tgz` | Full update package | qFlipper Install from file / SD card /ext/update/ |
| `full_dfu` | Complete DFU image | qFlipper DFU recovery / `qFlipper-cli firmware` |
| `updater_dfu` | Just the updater (small) | First stage of two-stage update |
| `resources_tgz` | Just assets/icons/fonts | Already inside `update_tgz` — usually not needed separately |

## Flipper CLI (verified against firmware 1.4.3 source)

Source files in `flipperzero-firmware` repo:
- `applications/services/storage/storage_cli.c` → `storage` command
- `applications/system/updater/cli/updater_cli.c` → `update` command
- `applications/services/cli/` → `version`, `device_info`, etc.

**Storage subcommands** (only these exist):
- `list` — list directory
- `info` — file metadata
- `read` — print file
- `write` — write file (interactive)
- `remove` — delete

**Update subcommands**:
- `backup` — saves `/int` to `/ext/update/backup/backup.tar`
- `restore` — restores from `/ext/update/backup/backup.tar` to `/int`

**No** `storage usb`, `storage mount`, `storage export`, `storage pull`. Mass Storage toggle lives in the Apps menu only.

## Mass Storage behavior on macOS

When Flipper enters Mass Storage mode (Apps → USB Mass Storage):
- macOS auto-mounts as `/Volumes/FLIPPER SD/` (sometimes `/Volumes/FLIPPER SD 1/` for re-mounts)
- Flipper's screen shows "USB Mass Storage" status
- Flipper cannot read/write SD while in this mode
- Press BACK on Flipper to exit

## DFU recovery (the ultimate safety net)

To enter DFU mode from any state:
- **Normal state**: Settings → Power → Reboot → Firmware Upgrade
- **Operational but stuck**: Hold LEFT + BACK for 5 seconds → release BACK, keep holding LEFT until blue LED
- **Hard brick**: Unplug USB, hold OK + BACK for 30 seconds, then plug USB

Once in DFU:
- `qFlipper-cli firmware <file.dfu>` to flash
- Or qFlipper GUI → Repair (auto-downloads latest)
- The DFU bootloader lives in protected ROM — can never be overwritten by firmware

## qFlipper CLI (qFlipper-cli 1.3.3)

Binary path after `brew install --cask qflipper`: `~/homebrew/bin/qFlipper-cli` (case-sensitive).

Subcommands:
- `backup <file.tgz>` — backup /int
- `restore <file.tgz>` — restore /int
- `erase` — erase /int
- `wipe` — wipe entire MCU flash
- `firmware <file.dfu>` — flash core1 firmware
- `core2radio <file.bin>` — flash radio stack
- `core2fus <file.bin> <addr>` — flash FUS

**Warning**: All subcommands wait indefinitely for a connected device. If no Flipper is plugged in, they hang rather than failing fast.

## Chinese firmware forks (for context, not used in backup)

- `kalicyh/Momentum-Firmware-CN` — Momentum + 簡體中文 (zh_CN)
  - Latest: v1.1.4 (2026-06-27)
  - Branch: `CN-Clipper`
  - Built via: `MOMENTUM_UI_LANG=zh_CN ./fbt COMPACT=1 DEBUG=0`
  - Release URL: `https://github.com/kalicyh/Momentum-Firmware-CN/releases`
  - Has 3 device variants: real (原版), clone (复刻版), clipper
  - Mobile app compatible (need 3-way forget + re-pair after switching)
- `flippercn.com` (宅人改造家) — MNTM+ variant, paid firmware+apps sold separately
- Standard Momentum has English UI only; Chinese comes only via forks

## SD card structure (from official sd-card-examples)

```
/ext/
├── favorites.txt
├── Manifest
├── badusb/           # .txt scripts
├── dolphin/          # L1_Furippa1_128x64/ animation frames
├── ibutton/          # .ibtn keys
├── infrared/         # .ir remotes + assets/
├── lfrfid/           # .rfid keys
├── music_player/     # .fmf tunes
├── nfc/              # .nfc cards + assets/
├── subghz/           # .sub captures + assets/
├── u2f/              # U2F cert + key
└── update/           # staging for firmware updates
```

`/int/` is internal flash — holds settings, dolphin level, BT pairing, U2F secrets, key cache.
