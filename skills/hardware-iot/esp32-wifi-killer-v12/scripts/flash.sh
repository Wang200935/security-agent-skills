#!/bin/bash
# 一鍵編譯燒錄 ESP32 WiFi Killer v12
# 用法: ./flash.sh [PORT]

set -e

PORT="${1:-/dev/cu.usbserial-0001}"
SKETCH_DIR="$(dirname "$0")/../firmware"
BUILD_DIR="/tmp/esp32_wifi_killer_v12_build"
BIN_DIR="/tmp/esp32_wifi_killer_v12_bin"

echo "=== ESP32 WiFi Killer v12 Flash Script ==="
echo "Port: $PORT"
echo "Sketch dir: $SKETCH_DIR"

# 清理舊建構
rm -rf "$BUILD_DIR" "$BIN_DIR"
mkdir -p "$BUILD_DIR" "$BIN_DIR"

# 編譯
echo "[1/3] Compiling..."
arduino-cli compile --fqbn esp32:esp32:esp32 \
  --build-path "$BUILD_DIR" \
  --output-dir "$BIN_DIR" \
  "$SKETCH_DIR"

# 找到 bin 檔
BIN_FILE=$(find "$BIN_DIR" -name "*.ino.bin" | head -1)
if [ -z "$BIN_FILE" ]; then
  echo "ERROR: No .bin file found!"
  exit 1
fi
echo "Binary: $BIN_FILE"

# 燒錄
echo "[2/3] Flashing..."
PYTHON=~/.hermes/hermes-agent/venv/bin/python3
$PYTHON -m esptool --chip esp32 --baud 115200 \
  --before default-reset --after hard-reset --port "$PORT" \
  write-flash 0x10000 "$BIN_FILE"

echo "[3/3] Done! Opening monitor in 2 seconds..."
sleep 2

# 開啟 monitor
$PYTHON -m serial.tools.miniterm "$PORT" 115200 --raw