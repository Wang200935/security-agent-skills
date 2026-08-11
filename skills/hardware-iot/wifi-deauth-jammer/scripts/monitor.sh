#!/bin/bash
# Serial monitor for ESP32 WiFi Killer v12
# 用法: ./monitor.sh [PORT]

set -e

PORT="${1:-/dev/cu.usbserial-0001}"

echo "=== ESP32 WiFi Killer v12 Monitor ==="
echo "Port: $PORT"
echo "Baud: 115200"
echo "Press Ctrl+C to exit"
echo ""

PYTHON=~/.hermes/hermes-agent/venv/bin/python3
$PYTHON -m serial.tools.miniterm "$PORT" 115200 --raw