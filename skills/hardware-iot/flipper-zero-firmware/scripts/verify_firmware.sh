#!/usr/bin/env bash
# verify_firmware.sh — read Flipper Zero device_info via pyserial
# and print only the fork-discriminating fields.
#
# Usage: verify_firmware.sh [serial_port]
#   default serial_port: /dev/cu.usbmodemflip_Ur1nicar1
#   (replace Ur1nicar1 with your device name from `ls /dev/cu.usbmodemflip*`)
#
# Requires: pyserial installed in the active venv

set -euo pipefail

PORT="${1:-/dev/cu.usbmodemflip_Ur1nicar1}"
PY="${HERMES_PY:-/Users/wang/.hermes/hermes-agent/venv/bin/python}"

if [ ! -x "$PY" ]; then
  PY="$(command -v python3)"
fi

"$PY" - "$PORT" <<'PY'
import serial, sys, time, re
port = sys.argv[1]
BAUD = 115200
# Fields to print — focus on fork discrimination
KEYS = [
    'firmware_version',
    'firmware_commit',
    'firmware_branch',
    'firmware_api_major',
    'firmware_api_minor',
    'firmware_origin_fork',   # THE fork discriminator
    'firmware_origin_git',
    'hardware_target',
    'hardware_region_provisioned',
    'hardware_name',
]
s = serial.Serial(port, BAUD, timeout=3)
s.reset_input_buffer(); s.reset_output_buffer()
time.sleep(0.2)
s.write(b'device_info\r\n')
time.sleep(1.0)
out = s.read(4000).decode(errors='replace')
s.close()

print(f'--- Flipper Zero @ {port} ---')
hit = False
for k in KEYS:
    m = re.search(rf'^{k}\s*:\s*(.+)$', out, re.MULTILINE)
    if m:
        print(f'  {k:30s} = {m.group(1).strip()}')
        hit = True
if not hit:
    print('  (no fields captured — check port + baud + Flipper powered on)')
    sys.exit(1)

# Quick verdict
fork_match = re.search(r'^firmware_origin_fork\s*:\s*(.+)$', out, re.MULTILINE)
if fork_match:
    fork = fork_match.group(1).strip()
    if fork.lower() == 'official':
        print('\n✓ Stock official firmware')
    else:
        print(f'\n⚠ Custom fork detected: {fork}')
PY