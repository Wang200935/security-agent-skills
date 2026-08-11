#!/usr/bin/env python3
"""
stage_update_package.py — Upload a Flipper Zero .tgz update package to /ext/update/<name>/
so you can run `update install /ext/update/<name>/update.fuf` over the serial CLI.

This is the headless equivalent of "drag the .tgz onto the SD card in qFlipper GUI".
Use it for the full-install path when you want the resource pack, firstboot.bin, and
external .fap manifests deployed — qFlipper-cli firmware <file.dfu> alone skips all of that.

Usage:
    python3 stage_update_package.py <extracted_pkg_dir> <remote_subdir> [--port /dev/cu.usbmodemflip_*]

Example:
    # After: tar -xzf momentum-fw-cn-v1.1.4-original.tgz -C /tmp/momentum/
    python3 stage_update_package.py /tmp/momentum/f7-update-v1.1.4 momentum-cn

    # Then over the serial CLI:
    #   > update install /ext/update/momentum-cn/update.fuf

Verified live (2026-06-30, Momentum-CN v1.1.4, 15 MB total upload in ~3 min on macOS).
"""

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

import serial  # pyserial


def read_until_prompt(ser, timeout=20):
    end = time.time() + timeout
    data = b""
    while time.time() < end:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            data += chunk
        if data.endswith(b">: ") or b"\r\n>: " in data[-20:]:
            break
    return data


def cmd(ser, c, timeout=3):
    ser.reset_input_buffer()
    ser.write(c.encode() + b"\r\n")
    return read_until_prompt(ser, timeout).decode("utf-8", errors="replace")


def stage_file(ser, local_path: Path, remote_path: str):
    """Upload one file via storage write_chunk. Verified sizes against source."""
    size = local_path.stat().st_size
    print(f"  = {remote_path} ({size:,} bytes) =")
    # Ensure parent dir exists (mkdir is idempotent)
    parent = os.path.dirname(remote_path)
    if parent:
        cmd(ser, f'storage mkdir "{parent}"', timeout=2)
    # Tell Flipper how many bytes we're sending
    print(f"    -> storage write_chunk {size} bytes")
    ser.reset_input_buffer()
    ser.write(f'storage write_chunk "{remote_path}" {size}\r\n'.encode())
    # Wait for "Ready" prompt
    ready_data = b""
    end = time.time() + 5
    while time.time() < end and b"Ready" not in ready_data:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            ready_data += chunk
    if b"Ready" not in ready_data:
        raise RuntimeError(f"Flipper did not respond with 'Ready' for {remote_path}")
    # Stream the bytes
    sent = 0
    CHUNK = 4096
    t0 = time.time()
    with open(local_path, "rb") as f:
        while True:
            data = f.read(CHUNK)
            if not data:
                break
            ser.write(data)
            sent += len(data)
    # Wait for the >: prompt back
    read_until_prompt(ser, timeout=30)
    elapsed = time.time() - t0
    print(f"    uploaded {sent:,} bytes in {elapsed:.1f}s ({sent/elapsed/1024:.0f} KB/s)")
    # Verify size on device
    stat = cmd(ser, f'storage stat "{remote_path}"', timeout=3)
    expected = f"File, size: {size}b"
    if expected in stat:
        print(f"    size verified OK ({size} bytes match)")
    else:
        print(f"    !! size MISMATCH: expected {size}, got: {stat.strip()[:200]}")
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pkg_dir", help="Path to extracted .tgz directory (e.g. f7-update-v1.1.4/)")
    ap.add_argument("remote_subdir", help="Subdir under /ext/update/ (e.g. momentum-cn)")
    ap.add_argument("--port", default=None, help="Serial port (auto-detect Flipper if omitted)")
    ap.add_argument("--baud", type=int, default=230400)
    args = ap.parse_args()

    pkg_dir = Path(args.pkg_dir)
    if not pkg_dir.is_dir():
        sys.exit(f"ERROR: {pkg_dir} is not a directory")

    # Auto-detect port if not given
    port = args.port
    if not port:
        import glob
        cands = sorted(glob.glob("/dev/cu.usbmodemflip*") + glob.glob("/dev/cu.usbmodem*"))
        cands = [c for c in cands if "Bluetooth" not in c and "debug" not in c.lower()]
        if not cands:
            sys.exit("ERROR: no Flipper serial port found")
        port = cands[0]
    print(f"Using serial port: {port}")

    # Find all files to stage
    files = sorted([p for p in pkg_dir.iterdir() if p.is_file()])
    total = sum(p.stat().st_size for p in files)
    print(f"Staging {len(files)} files, {total/1024/1024:.2f} MB total:")
    for p in files:
        print(f"  - {p.name} ({p.stat().st_size:,} bytes)")

    ser = serial.Serial(port, args.baud, timeout=5)
    time.sleep(0.4)

    # Make /ext/update/<subdir> directory
    remote_dir = f"/ext/update/{args.remote_subdir}"
    print(f"\nCreating {remote_dir} on Flipper...")
    print(cmd(ser, f'storage mkdir "{remote_dir}"', timeout=3))

    ok = True
    for p in files:
        if not stage_file(ser, p, f"{remote_dir}/{p.name}"):
            ok = False
            print(f"  !! FAILED: {p.name}")

    ser.close()
    print()
    if ok:
        print(f"OK: all files staged to {remote_dir}")
        print()
        print("Now run on the Flipper CLI:")
        print(f"  update install {remote_dir}/update.fuf")
        print()
        print("The CLI session will disconnect during the updater reboot.")
        print("Wait 60-90 s, then verify with `device_info` from a new CLI session.")
    else:
        sys.exit("FAILED: see errors above")


if __name__ == "__main__":
    main()