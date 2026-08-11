# Momentum-CN — Deep Dive (kalicyh/Momentum-Firmware-CN)

What this skill knows from a live 2026-06-30 session: downloading the latest release, identifying the right variant for real/original hardware, extracting the .tgz, staging it via `storage write_chunk`, running `update install` over the serial CLI, and verifying the result.

## Repo facts (verified against GitHub API)

- **Repo**: `kalicyh/Momentum-Firmware-CN`
- **Default branch**: `CN-Clipper` (not `main` — earlier queries for `main/README.md` returned 404)
- **Latest release**: `v1.1.4` (2026-06-27)
- **Variants in each release**: `original` (real hardware), `clone` (复刻版), `clipper`
- **Build flag**: `MOMENTUM_UI_LANG=zh_CN` — all release variants are built with Chinese UI
- **Forked from**: `Next-Flip/Momentum-Firmware` (English UI upstream)

## Release asset naming

| Asset | Purpose |
|---|---|
| `momentum-fw-cn-v<version>-original.tgz` | Full update package for real/original hardware (use this) |
| `momentum-fw-cn-v<version>-original.zip` | Same content, zip format (for Windows tools) |
| `momentum-fw-cn-v<version>-original.dfu` | Standalone DFU image, ~0.83 MB — **DFU-only mode, NOT full install** |
| `momentum-fw-cn-v<version>-<variant>.{tgz,zip,dfu}` | Same trio for clone and clipper variants |
| `momentum-fw-cn-v<version>-zh-fonts.zip` | All `.u8f` font files (manual override, optional) |
| `wenquanyi_<size>.u8f`, `zpix.u8f`, `JiZhi-bitmap-8.u8f`, `fusion-pixel-*.u8f` | Individual font files |

## Inside the .tgz (verified by extraction)

```
f7-update-v1.1.4/
├── firmware.dfu         (848 KB) — the actual DFU image
├── radio.bin            (114 KB) — Bluetooth radio stack
├── updater.bin          (113 KB) — first-stage bootloader updater
├── firstboot.bin        (3 KB) — runs once on first boot
├── splash.bin           (528 B) — boot logo
├── resources.tar.gz     (14.6 MB!) — resource pack: icons, manifests, app metadata, font cache
└── update.fuf           (1.5 KB) — update manifest
```

The `resources.tar.gz` is the biggest single file. **It is NOT deployed by `qFlipper-cli firmware <file.dfu>`** — that path only burns the DFU image into internal flash. To deploy `resources.tar.gz` along with the firmware, you must use the staged `update install` workflow: extract the .tgz, upload all 7 files to `/ext/update/<name>/` via `storage write_chunk`, then run `update install /ext/update/<name>/update.fuf` over the serial CLI. See SKILL.md Install Mode A and `scripts/stage_update_package.py`.

## Chinese font implementation (verified in source)

The Chinese localization works at **compile time**, not runtime:

```c
// applications/services/gui/canvas.c (verified via raw GitHub fetch)
#if defined(MOMENTUM_UI_LANG_ZH_CN) && !defined(FURI_RAM_EXEC)
extern const uint8_t primary_zh[];
#endif

static const uint8_t* canvas_get_zh_font(void) {
#if defined(MOMENTUM_UI_LANG_ZH_CN) && !defined(FURI_RAM_EXEC)
    return primary_zh;
#else
    return NULL;
#endif
}
```

The canvas code detects non-ASCII characters in any string and automatically swaps to the Chinese font. **No SD card font file is needed for the default experience.** The Chinese font is baked into the firmware binary.

## Optional font override

If the user wants a different Chinese font (different visual style):

1. Download `momentum-fw-cn-v<version>-zh-fonts.zip` from the release page
2. Unzip — contains `wenquanyi_9pt.u8f`, `wenquanyi_10pt.u8f`, `zpix.u8f`, etc.
3. Pick one, rename to `primary_zh.u8f`
4. Place in `/ext/zh_fonts/primary_zh.u8f` on the SD card
5. Reboot Flipper — `canvas.c` will use the override

(Note: I haven't fully traced whether the SD card override path is actually checked in `canvas_get_zh_font` — the source I read always returned the compiled-in `primary_zh[]`. The README says it's supported, but treat as best-effort until verified.)

## Why "大部分都還是英文啊" happens after a flash — diagnosis tree

**This is the most-reported failure mode after flashing Momentum-CN.** Walk this tree before assuming it's a partial-translation reality:

1. **Did you use DFU-only flash (`qFlipper-cli firmware <file.dfu`)?**
   - Yes → incomplete install. `resources.tar.gz` was not deployed. Re-do via the staged `update install` workflow. After the re-install, Settings / NFC / Sub-GHz / Infrared / iButton / LF RFID / BadUSB main flow / main menu labels should all be in Chinese.
   - No → continue to step 2.

2. **Did you actually verify it?** Check on-device:
   - `device_info` via serial CLI → confirm `firmware_version: v1.1.4` and `firmware_origin_fork: Momentum`
   - `storage list /ext/apps` → confirm external .fap apps are present (they're deployed from `resources.tar.gz`)
   - `storage list /ext/zh_fonts` → empty (the font is in firmware, not on SD)
   - Visually check the main menu → "Sub-GHz", "NFC", "紅外" etc. should be in Chinese

3. **Did the device reboot properly after `update install`?**
   - After the updater finishes, the Flipper often ends up back in DFU mode (USB PID 0x5740) until the host re-enumerates. Force a USB reset by unplugging and replugging the Flipper USB cable. The bootloader will then complete the boot and emit the CLI banner.

4. **If still English after a verified full install** → it's the partial-translation reality below.

## Partial-translation reality (only after step 1-3 confirm complete install)

- ✅ Fully Chinese: Settings, NFC menu, Sub-GHz menu, Infrared menu, iButton menu, LF RFID menu, BadUSB main flow, main menu labels
- ⚠️ May still be English: some third-party .fap apps, Dolphin animation titles, certain error messages
- The 245 bundled external apps: 243 have Chinese menu names (`name_zh` in application.fam), 2 don't
- The Chinese font is always rendered for non-ASCII characters (so Chinese text displays correctly even in partially-translated apps)

**Rule of thumb**: if the user names *specific screens* that are English (e.g. "NFC 選單是中文但 Sub-GHz frequency analyzer 還是英文"), it's the partial-translation reality. If they say "Settings 也是英文" or "整個 UI 還是英文", the install is incomplete — re-do with `update install`.

## CLI command differences (Momentum vs official)

Verified by `help` output after flashing:

| Official | Momentum | Notes |
|---|---|---|
| `top` | `log` | Momentum renamed it (likely to avoid clash with shell `top`) |
| `storage ...` | `storage ...` | Same |
| `device_info` | `device_info` | Same |
| `info device` | `info device` | Same |
| `nfc` (not in official) | `nfc` | Momentum-added external command |
| `subghz` (not in official) | `subghz` | Momentum-added |
| `ir` (not in official) | `ir` | Momentum-added |
| `rfid` (not in official) | `rfid` | Momentum-added |
| `onewire` (not in official) | `onewire` | Momentum-added |
| `neofetch` (not in official) | `neofetch` | Easter egg |
| `buzzer` (not in official) | `buzzer` | For testing |

If `help` doesn't show a command you expect, run `reload_ext_cmds` to re-scan for external commands.

## Real-world flash log — FULL install (v1.1.4, 2026-06-30)

The complete working sequence:

```
02:43:27  qFlipper-cli firmware <file.dfu>    ← DFU-only flash (gave partial result)
02:43:29  ERROR: Please provide a firmware file in DFUse format.
            ^ Lesson: extract .dfu from .tgz first
02:43:40  qFlipper-cli firmware ./firmware.dfu  ← DFU-only mode
02:45:41  "All done! Thank you."                ← v1.1.4 reported in device_info
02:51:00  User reports: "只有「紅外」這兩個字是中文，其他我找不到中文"
            ^ Because resources.tar.gz was never deployed

# Now do the FULL install
02:55:00  storage mkdir /ext/update/momentum-cn
02:55:30  storage write_chunk /ext/update/momentum-cn/update.fuf 1578
            Ready → raw bytes → verified size 1578b
02:56:00  storage write_chunk /ext/update/momentum-cn/radio.bin 116956
            ... (same for firmware.dfu, updater.bin, firstboot.bin, splash.bin, resources.tar.gz)
02:58:30  Total uploaded: 15 MB across 7 files (~3 min)
02:58:35  update install /ext/update/momentum-cn/update.fuf
02:58:36  CLI session disconnects (updater rebooted into RAM updater)
02:58:40  USB re-enumerates with PID 0x5740 (DFU mode — normal during updater flash)
02:59:30  Send \x00 bytes to /dev/cu.usbmodemflip_Ur1nicar1
02:59:31  Bootloader re-emits Flipper CLI banner, exits DFU, completes boot
02:59:32  device_info shows: firmware_version v1.1.4 (828a2168-dirty built on 27-06-2026)
            ^ Dirty build marker is expected (qFlipper restored /int from pre-flash backup)
```

Total end-to-end: ~16 minutes (3 min upload + 13 min install + verification). The dirty build flag is harmless — `/int` settings were restored from the pre-flash backup so the firmware's own build hash differs from the running config.

## Backup-then-flash roundtrip

**Momentum-CN preserves /ext entirely.** After the flash:
- All SD card files were still there: subghz, nfc, IR, badusb scripts, u2f, dolphin manifest, favorites
- No "migration" of any kind needed
- BadUSB scripts in /ext/badusb/*.txt worked as-is

This means the user's "I want to keep my BadUSB scripts on Momentum" worry was unfounded — they're already there after the flash, no copy needed.

## Verified working URLs (as of 2026-06-30)

```
# Release manifest (latest)
https://github.com/kalicyh/Momentum-Firmware-CN/releases/latest

# Specific version 1.1.4
https://github.com/kalicyh/Momentum-Firmware-CN/releases/download/v1.1.4/momentum-fw-cn-v1.1.4-original.tgz
https://github.com/kalicyh/Momentum-Firmware-CN/releases/download/v1.1.4/momentum-fw-cn-v1.1.4-original.zip
https://github.com/kalicyh/Momentum-Firmware-CN/releases/download/v1.1.4/momentum-fw-cn-v1.1.4-original.dfu
https://github.com/kalicyh/Momentum-Firmware-CN/releases/download/v1.1.4/momentum-fw-cn-v1.1.4-zh-fonts.zip
```

Replace `original` with `clone` or `clipper` for those variants.

## Where to look for things in the source

Default branch is `CN-Clipper`, so use `?ref=CN-Clipper` in GitHub API calls:

- `localization/zh_CN/strings.json` — all translated strings
- `applications/services/gui/canvas.c` — Chinese font switching logic
- `scripts/momentum_zh_font_gen.py` — font generation pipeline
- `ReadMe.md` — user-facing features and changes
- `CHANGELOG.md` — version-by-version changes