#!/usr/bin/env python3
"""
flipper_inspect.py — read-only Flipper Zero inspection via serial CLI.

Auto-detects the serial port, sends a curated set of read-only CLI commands,
prints a markdown status table. **Does NOT modify any state on the Flipper.**

Designed for the "檢查一下 / 看一下 / 檢查" (read-only inspection) workflow:
- No writes, no factory reset, no power off, no firmware install
- All commands are observation-only: device_info, info power, free, uptime, top
- Hard 8s timeout per command — bails on hangs (see SKILL.md CLI shell pitfall)
- Skips `storage list /ext/apps` because it wedges the VCP shell on populated SD cards

Usage:
    ~/.hermes/hermes-agent/venv/bin/python flipper_inspect.py
    ~/.hermes/hermes-agent/venv/bin/python flipper_inspect.py --port /dev/cu.usbmodemflip_xxx
"""
import argparse
import glob
import re
import signal
import sys
import time
from typing import Optional

try:
    import serial
except ImportError:
    print("ERROR: pyserial not installed. Run: ~/.hermes/hermes-agent/venv/bin/pip install pyserial")
    sys.exit(1)


def detect_port(explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    candidates = sorted(
        glob.glob("/dev/cu.usbmodemflip*")
        + glob.glob("/dev/tty.usbmodemflip*")
        + glob.glob("/dev/cu.usbmodem*")
        + glob.glob("/dev/tty.usbmodem*")
    )
    if not candidates:
        print("ERROR: no Flipper serial port detected. Plug in USB and ensure device is ON.")
        sys.exit(2)
    return candidates[0]


class CLI:
    def __init__(self, port: str, baud: int = 115200):
        self.s = serial.Serial(port, baud, timeout=4, write_timeout=4)

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass

    def _raw(self, cmd: str, wait: float, hard_timeout: float) -> str:
        """Send one CLI command with a hard wall-clock timeout. Returns raw text or 'TIMEOUT'."""
        result = {"text": None}

        def _alarm(_sig, _frame):
            raise TimeoutError(f"{cmd} exceeded {hard_timeout}s")

        # Abort any prior top/storage list
        for _ in range(2):
            try:
                self.s.write(b"\x03")
                time.sleep(0.2)
            except Exception:
                pass
        try:
            self.s.flushInput()
            self.s.flushOutput()
        except Exception:
            pass

        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(int(hard_timeout) + 1)
        try:
            self.s.write((cmd + "\r\n").encode())
            time.sleep(wait)
            data = bytearray()
            deadline = time.time() + hard_timeout
            while time.time() < deadline:
                chunk = self.s.read(8000)
                if not chunk:
                    break
                data.extend(chunk)
                if b">:" in chunk:
                    break
            result["text"] = data.decode(errors="replace")
        except TimeoutError:
            result["text"] = "TIMEOUT"
        except Exception as e:
            result["text"] = f"ERR {type(e).__name__}: {e}"
        finally:
            signal.alarm(0)
        return result["text"]

    def cli(self, cmd: str, wait: float = 1.5, hard_timeout: float = 8.0) -> str:
        """Send one CLI command. Strips the welcome banner, returns body after last '>:'."""
        raw = self._raw(cmd, wait, hard_timeout)
        if raw in ("TIMEOUT",) or raw.startswith("ERR "):
            return raw
        if ">:" in raw:
            return raw.rsplit(">:", 1)[1].strip()
        return raw.strip()


def parse_kv(text: str) -> dict[str, str]:
    """Parse 'key.subkey : value' lines from a CLI response."""
    out = {}
    for line in text.splitlines():
        if ":" in line and "\t" not in line:
            k, _, v = line.partition(":")
            k = k.strip()
            v = v.strip()
            if k and not k.startswith(">"):
                out[k] = v
    return out


def status_badge(value: str) -> str:
    """Heuristic status badge."""
    v = value.lower()
    if v in ("official", "true", "charged", "tw") or "100" in v or "ok" in v:
        return "🟢"
    if v in ("",) or "false" in v:
        return "⚪"
    if "timeout" in v or "err" in v:
        return "🔴"
    return "🟢"


def main():
    ap = argparse.ArgumentParser(description="Read-only Flipper Zero inspection")
    ap.add_argument("--port", default=None, help="Serial port (auto-detect if omitted)")
    args = ap.parse_args()

    port = detect_port(args.port)
    print(f"# Flipper Zero Inspection\n")
    print(f"**Port:** `{port}`  **Mode:** read-only (no state changes)\n")
    print(f"---\n")

    cli = CLI(port)

    # --- Section A: device_info ---
    print("## A. device_info\n")
    di_text = cli.cli("device_info", wait=2.0, hard_timeout=10.0)
    di = parse_kv(di_text)
    rows = []
    for k in [
        "device_info_major", "device_info_minor",
        "hardware_model", "hardware_ver", "hardware_target", "hardware_body",
        "hardware_connect", "hardware_display", "hardware_color",
        "hardware_region", "hardware_region_provisioned", "hardware_name",
        "hardware_otp_ver", "hardware_timestamp", "hardware_uid",
        "firmware_version", "firmware_branch", "firmware_branch_num",
        "firmware_commit", "firmware_commit_dirty", "firmware_build_date",
        "firmware_target", "firmware_api_major", "firmware_api_minor",
        "firmware_origin_fork", "firmware_origin_git",
    ]:
        v = di.get(k, "(missing)")
        rows.append(f"| `{k}` | `{v}` | {status_badge(v)} |")
    print("| Field | Value | Status |")
    print("|---|---|---|")
    print("\n".join(rows))
    print()

    # --- Section B: info power ---
    print("## B. info power\n")
    pw = parse_kv(cli.cli("info power", wait=2.0, hard_timeout=8.0))
    print("| Field | Value | Status |")
    print("|---|---|---|")
    for k in ["charge.level", "charge.state", "charge.voltage.limit",
              "battery.voltage", "battery.current", "battery.temp",
              "battery.health", "capacity.remain", "capacity.full", "capacity.design"]:
        v = pw.get(k, "(missing)")
        print(f"| `{k}` | `{v}` | {status_badge(v)} |")
    print()

    # --- Section C: memory ---
    print("## C. memory\n")
    fr = cli.cli("free", wait=1.0, hard_timeout=5.0)
    print("```\n" + fr[:400] + "\n```\n")
    fb = cli.cli("free_blocks", wait=1.0, hard_timeout=5.0)
    print("**free_blocks:**\n```\n" + fb[:400] + "\n```\n")

    # --- Section D: uptime / date ---
    print("## D. uptime / date\n")
    print("- " + cli.cli("uptime", wait=1.0, hard_timeout=5.0).replace("\n", " "))
    print("- " + cli.cli("date", wait=1.0, hard_timeout=5.0).replace("\n", " "))
    print()

    # --- Section E: /int storage (small + safe) ---
    print("## E. /int storage (11 settings files)\n")
    print("```")
    print(cli.cli("storage info /int", wait=1.5, hard_timeout=5.0)[:400])
    print(cli.cli("storage list /int", wait=1.5, hard_timeout=5.0)[:800])
    print("```\n")

    # --- Section F: /ext storage info + manifest size (small) ---
    print("## F. /ext storage (SD card summary)\n")
    print("```")
    print(cli.cli("storage info /ext", wait=1.5, hard_timeout=5.0)[:600])
    print("```\n")

    # --- Section G: top (services) — short, then abort ---
    print("## G. top (process snapshot, 3 lines only)\n")
    top = cli.cli("top", wait=2.0, hard_timeout=5.0)
    lines = [ln for ln in top.splitlines() if ln.strip()]
    print("```")
    print("\n".join(lines[:8]))
    print("```\n")

    # NOTE: We DELIBERATELY skip `storage list /ext/apps` and `storage list /ext/update`
    # because they wedge the VCP CLI shell on populated SD cards (see SKILL.md pitfall).
    print("> ⚠️ `storage list /ext/apps` and `storage list /ext/update` **skipped** — known to wedge the CLI shell.\n")

    cli.close()
    print("---\n")
    print("Inspection complete. **No state was modified.**\n")


if __name__ == "__main__":
    main()