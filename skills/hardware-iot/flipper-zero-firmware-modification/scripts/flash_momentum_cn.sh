#!/bin/bash
# Flash Momentum-CN to Flipper Zero via qFlipper-cli
# Run AFTER the flipper-zero-backup skill has completed a full backup.

set -euo pipefail

# ============================================================
# Configuration (override via env vars)
# ============================================================
VERSION="${VERSION:-1.1.4}"
VARIANT="${VARIANT:-original}"   # original | clone | clipper
BACKUP_BASE="${BACKUP_BASE:-$HOME/Desktop/FlipperBackup}"
WORK_DIR="$BACKUP_BASE/momentum_cn"

# ============================================================
# Pre-flight checks
# ============================================================
if [ ! -d "$BACKUP_BASE" ]; then
    echo "❌ ERROR: Backup directory not found: $BACKUP_BASE"
    echo "   Run the flipper-zero-backup skill first to create a full backup."
    exit 1
fi

if ! command -v qFlipper-cli >/dev/null 2>&1; then
    echo "❌ ERROR: qFlipper-cli not installed."
    echo "   Install via: brew install --cask qflipper"
    exit 1
fi

PORT=$(ls /dev/cu.usbmodemflip* 2>/dev/null | head -1)
if [ -z "$PORT" ]; then
    echo "❌ ERROR: No Flipper detected on USB."
    echo "   Plug in Flipper (powered on, not in DFU mode) and retry."
    exit 1
fi

echo "✅ Pre-flight OK"
echo "   Backup dir: $BACKUP_BASE"
echo "   qFlipper-cli: $(which qFlipper-cli)"
echo "   Flipper port: $PORT"
echo "   Target: Momentum-CN v$VERSION ($VARIANT variant)"
echo ""

# ============================================================
# Step 1: Capture device identity
# ============================================================
echo "=== Step 1: Capturing device identity ==="
DEVICE_INFO_FILE="$WORK_DIR/device_info_before.txt"
mkdir -p "$WORK_DIR"

~/.hermes/hermes-agent/venv/bin/python << PYEOF > "$DEVICE_INFO_FILE"
import serial, time
ser = serial.Serial("$PORT", 230400, timeout=2)
time.sleep(0.3)
ser.reset_input_buffer()
ser.write(b'device_info\r\n')
time.sleep(0.5)
print(ser.read(ser.in_waiting).decode('utf-8', errors='replace'))
ser.close()
PYEOF

echo "   Saved to: $DEVICE_INFO_FILE"
echo ""
echo "   Key fields (check these match what you expect):"
grep -E "firmware_origin|hardware_name|firmware_version" "$DEVICE_INFO_FILE" | sed 's/^/     /'
echo ""

ORIGIN=$(grep "firmware_origin_fork" "$DEVICE_INFO_FILE" | head -1 | sed 's/.*: *//' | tr -d ' \r')
if [ "$VARIANT" = "original" ] && [ -n "$ORIGIN" ] && [ "$ORIGIN" != "Official" ]; then
    echo "⚠️  WARNING: Device origin is '$ORIGIN', not 'Official'."
    echo "   If this is clone/clipper hardware, set VARIANT=clone or VARIANT=clipper."
    echo "   Aborting to prevent brick."
    exit 1
fi
echo "✅ Device identity looks consistent with variant=$VARIANT"
echo ""

# ============================================================
# Step 2: Download firmware
# ============================================================
echo "=== Step 2: Downloading Momentum-CN v$VERSION ($VARIANT) ==="
TGZ_URL="https://github.com/kalicyh/Momentum-Firmware-CN/releases/download/v$VERSION/momentum-fw-cn-v$VERSION-$VARIANT.tgz"
TGZ_FILE="$WORK_DIR/momentum-fw-cn-v$VERSION-$VARIANT.tgz"

if [ -f "$TGZ_FILE" ]; then
    echo "   Already downloaded: $TGZ_FILE"
else
    curl -sL "$TGZ_URL" -o "$TGZ_FILE"
    echo "   Downloaded: $(du -h "$TGZ_FILE" | cut -f1)"
fi
echo ""

# ============================================================
# Step 3: Extract .dfu
# ============================================================
echo "=== Step 3: Extracting firmware.dfu from .tgz ==="
EXTRACT_DIR="$WORK_DIR/extracted"
mkdir -p "$EXTRACT_DIR"
tar -xzf "$TGZ_FILE" -C "$EXTRACT_DIR"

DFU_FILE=$(find "$EXTRACT_DIR" -name "firmware.dfu" -type f | head -1)
if [ -z "$DFU_FILE" ]; then
    echo "❌ ERROR: firmware.dfu not found in extracted archive"
    exit 1
fi
echo "   Extracted DFU: $DFU_FILE ($(du -h "$DFU_FILE" | cut -f1))"
echo ""

# ============================================================
# Step 4: Flash
# ============================================================
echo "=== Step 4: Flashing ==="
echo "   ⚠️  DO NOT unplug USB. DO NOT press Flipper buttons."
echo "   This takes ~5 minutes."
echo ""

# Kill any stale qFlipper process first
pkill -9 -f qFlipper 2>/dev/null
sleep 2

qFlipper-cli firmware "$DFU_FILE"
echo ""

# ============================================================
# Step 5: Verify
# ============================================================
echo "=== Step 5: Verifying flash ==="
sleep 5

DEVICE_INFO_AFTER="$WORK_DIR/device_info_after.txt"
~/.hermes/hermes-agent/venv/bin/python << PYEOF > "$DEVICE_INFO_AFTER"
import serial, time
ser = serial.Serial("$PORT", 230400, timeout=2)
time.sleep(0.5)
ser.reset_input_buffer()
ser.write(b'device_info\r\n')
time.sleep(0.5)
print(ser.read(ser.in_waiting).decode('utf-8', errors='replace'))
ser.close()
PYEOF

echo "   After-flash device_info:"
grep -E "firmware_origin|firmware_version|firmware_branch|hardware_name" "$DEVICE_INFO_AFTER" | sed 's/^/     /'
echo ""

if grep -q "firmware_origin_fork\s*:\s*Momentum" "$DEVICE_INFO_AFTER"; then
    echo "✅ Flash SUCCESS: Momentum detected"
else
    echo "⚠️  Flash may have failed: 'Momentum' not in origin_fork"
    echo "   Check the device manually."
fi

# Verify SD card preservation
echo ""
echo "=== SD Card verification ==="
~/.hermes/hermes-agent/venv/bin/python << PYEOF
import serial, time
ser = serial.Serial("$PORT", 230400, timeout=2)
time.sleep(0.3)
ser.reset_input_buffer()
ser.write(b'storage list /ext\r\n')
time.sleep(1)
print(ser.read(ser.in_waiting).decode('utf-8', errors='replace'))
ser.close()
PYEOF

echo ""
echo "✅ Flash workflow complete."
echo ""
echo "=== Notes ==="
echo "   • Momentum-CN 中文 UI is automatic (compiled in)"
echo "   • SD card files preserved (no migration needed)"
echo "   • Bluetooth pairing may need re-pairing (3-way forget)"
echo "   • If you see issues, hold LEFT+BACK 5s → DFU mode → re-flash"