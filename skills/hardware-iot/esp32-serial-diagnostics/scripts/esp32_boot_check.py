#!/usr/bin/env python3
"""
ESP32 Boot Check — read boot log via pyserial soft-reset.
Works in non-TTY environments where pio device monitor crashes.

Usage:
  python3 esp32_boot_check.py /dev/cu.usbserial-210
  python3 esp32_boot_check.py /dev/cu.usbserial-210 --read-only
  python3 esp32_boot_check.py /dev/cu.usbserial-210 --baud 9600

Exit codes:
  0 = boot:0x13 (SPI_FAST_FLASH_BOOT) — normal boot
  1 = boot:0x3 (DOWNLOAD_BOOT) — stuck in download mode
  2 = No output / connection failed
  3 = Other boot mode
"""
import serial, time, sys, argparse

def soft_reset_and_read(port, baud=115200, duration=10):
    """Reset ESP32 via DTR/RTS and read boot log."""
    ser = serial.Serial(port, baud, timeout=1)
    time.sleep(0.3)
    ser.dtr = True
    ser.rts = True     # EN low = reset hold
    time.sleep(0.1)
    ser.dtr = False
    ser.rts = False    # release reset = boot
    time.sleep(0.5)
    
    buf = b''
    start = time.time()
    while time.time() - start < duration:
        data = ser.read(4096)
        if data:
            buf += data
        else:
            time.sleep(0.05)
    ser.close()
    return buf.decode('utf-8', errors='replace')

def read_only(port, baud=115200, duration=12):
    """Just read whatever the ESP32 is emitting (no reset)."""
    ser = serial.Serial(port, baud, timeout=1)
    buf = b''
    start = time.time()
    while time.time() - start < duration:
        if ser.in_waiting:
            buf += ser.read(ser.in_waiting)
        else:
            time.sleep(0.15)
    ser.close()
    return buf.decode('utf-8', errors='replace')

def interpret_boot_log(text):
    """Parse boot log and return exit code + diagnosis."""
    if not text.strip():
        print("[NO OUTPUT] — no serial data received. Check port, baud rate, and USB cable.")
        return 2
    
    print(text)
    print("\n" + "="*60)
    
    if 'boot:0x13' in text or 'SPI_FAST_FLASH_BOOT' in text:
        print("[✅] Normal boot — firmware loaded successfully")
        if 'psram' in text.lower() and 'error' in text.lower():
            print("[ℹ️] PSRAM error is normal for ESP32-D0WD-V3 (no PSRAM)")
        if 'rst:0x3' in text or 'SW_CPU_RESET' in text:
            print("[ℹ️] Software reset detected (watchdog or crash)")
        return 0
    elif 'boot:0x3' in text or 'DOWNLOAD_BOOT' in text:
        print("[⚠️] DOWNLOAD_BOOT — GPIO0 held low, stuck in download mode")
        print("      Check wiring: GPIO2/CSN may be pulling GPIO0 low")
        return 1
    elif 'No bootable app partitions' in text or 'No partition table' in text:
        print("[❌] Flash corrupted — re-flash firmware")
        return 2
    elif 'rst:0x10' in text or 'RTCWDT' in text or 'WDT' in text:
        print("[⚠️] Watchdog reset detected — possible crash or starvation")
        return 3
    else:
        print("[?] Unrecognized boot pattern — check output above")
        return 3

def main():
    parser = argparse.ArgumentParser(description='ESP32 boot log checker')
    parser.add_argument('port', help='Serial port (e.g. /dev/cu.usbserial-210)')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate (default 115200)')
    parser.add_argument('--read-only', action='store_true', help="Don't reset, just read current output")
    parser.add_argument('--duration', type=int, default=10, help='Read duration in seconds')
    args = parser.parse_args()
    
    try:
        if args.read_only:
            text = read_only(args.port, args.baud, args.duration)
        else:
            text = soft_reset_and_read(args.port, args.baud, args.duration)
        sys.exit(interpret_boot_log(text))
    except serial.SerialException as e:
        print(f"[ERROR] Serial connection failed: {e}", file=sys.stderr)
        print(f"        Check port name and USB connection", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == '__main__':
    main()
