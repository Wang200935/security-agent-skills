#!/usr/bin/env python3
"""
sfo.py — SpiderFoot OSINT wrapper for Hermes Agent.

Subcommands:
  scan        Run a SpiderFoot scan with sensible defaults, output normalized JSON.
  normalize   Convert raw SpiderFoot JSON report → entity-keyed dict.
  merge       Merge multiple normalized reports (SpiderFoot + fallback).
  fallback    Run the no-API-key fallback pipeline (aliens-eye/maigret/holehe/h8mail/crt.sh/etc.)
  modules     List modules, optionally filter (api-key / email / domain).
  event-types List event types, filter by category (email / account / breach).
  hx2         Start SpiderFoot HX2 web UI (background).

Usage:
  sfo.py scan -s target@example.com -u investigate -o ~/osint-reports/
  sfo.py fallback -s target@example.com -o ~/osint-reports/
  sfo.py normalize -i report.json -o report.entities.json
  sfo.py merge -i a.json b.json -o merged.json
  sfo.py modules --filter api-key
  sfo.py hx2 -l 127.0.0.1:5001
"""
import argparse
import json
import os
import re
import resource
import shlex
import signal
import sqlite3
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SPIDERFOOT_DIR = Path.home() / "tools" / "spiderfoot"
SPIDERFOOT_VENV = Path.home() / "tools" / "spiderfoot-venv"
REPORT_DIR = Path.home() / "osint-reports"
SPIDERFOOT_DB = Path.home() / ".spiderfoot" / "spiderfoot.db"

# Seed classification
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$")
PHONE_RE = re.compile(r"^\+?\d{7,15}$")
IP_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
BTC_RE = re.compile(r"^(bc1|[13])[a-zA-Z0-9]{25,42}$")


def classify_seed(seed: str) -> str:
    if EMAIL_RE.match(seed):
        return "email"
    if IP_RE.match(seed):
        return "ip"
    if BTC_RE.match(seed):
        return "bitcoin"
    if PHONE_RE.match(seed) or seed.startswith("+"):
        return "phone"
    if DOMAIN_RE.match(seed):
        return "domain"
    # No spaces + no special chars → probably username
    if re.match(r"^[A-Za-z0-9_.-]+$", seed) and "@" not in seed:
        return "username"
    return "unknown"


def ensure_venv():
    """Return the python executable path in the venv."""
    pyp = SPIDERFOOT_VENV / "bin" / "python3"
    if not pyp.exists():
        print(f"[!] venv not found at {pyp}", file=sys.stderr)
        print("    Run: python3.11 -m venv ~/tools/spiderfoot-venv && "
              "source ~/tools/spiderfoot-venv/bin/activate && "
              "cd ~/tools/spiderfoot && pip install -r requirements.txt",
              file=sys.stderr)
        sys.exit(1)
    return str(pyp)


def cmd_scan(args):
    """Run a SpiderFoot scan (SpiderFoot v4 + macOS path).

    On SpiderFoot v4, the CLI runs the scan in a subprocess; events go to the
    SQLite database at ~/.spiderfoot/spiderfoot.db. The stdout output is a
    JSON/TSV stream but it is only emitted *while the scan runs* and can be cut
    short by the multi-process output filter. The robust path is: wait for the
    scan to FINISHED, then read events from the DB keyed by the scan GUID.

    Additionally, SpiderFoot v4 with the full 200+ module set opens a LOT of
    file descriptors; on macOS the default ulimit -n is 256 which is too low
    and causes "Too many open files" errors that silently kill most modules.
    We raise the soft fd limit before launching sf.py.
    """
    # Raise fd limit (this is process-local; does not affect caller)
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        new_soft = min(hard, 10240)
        if soft < new_soft:
            resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))
            print(f"[*] Raised fd limit: {soft} → {new_soft} (hard={hard})")
    except (ImportError, ValueError, OSError) as e:
        print(f"[!] Could not raise fd limit: {e}", file=sys.stderr)

    seed = args.seed
    seed_type = classify_seed(seed)
    print(f"[*] Seed: {seed}  classified as: {seed_type}")

    # Pick use case if not specified
    use_case = args.use_case or {
        "email": "investigate",
        "domain": "all",
        "username": "passive",
        "ip": "all",
        "phone": "investigate",
        "bitcoin": "all",
    }.get(seed_type, "investigate")
    print(f"[*] Use case: {use_case}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_seed = re.sub(r"[^A-Za-z0-9._-]", "_", seed)
    out_dir = Path(args.output)
    if out_dir.is_file() or (not out_dir.exists() and out_dir.suffix == ".json"):
        # treat as file path
        out_file = out_dir
    else:
        out_file = out_dir / f"spiderfoot_{safe_seed}_{ts}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    pyp = ensure_venv()
    cmd = [
        pyp, str(SPIDERFOOT_DIR / "sf.py"),
        "-s", seed,
        "-o", "json",
        "-n",  # strip newlines
        "-q",  # quiet
    ]
    # If user specified modules, use -m (overrides -u). Else -u use case.
    if args.modules:
        cmd.extend(["-m", args.modules])
    else:
        cmd.extend(["-u", use_case])
    if args.types:
        cmd.extend(["-t", args.types])
    if args.max_threads:
        cmd.extend(["-max-threads", str(args.max_threads)])

    print(f"[*] Running: {' '.join(shlex.quote(c) for c in cmd)}")
    t0 = time.time()
    # Run SpiderFoot as detached background so we don't block on pipe deadlock
    # under agent terminal wrappers. We poll the SQLite DB scan status.
    raw_stdout_file = out_file.with_suffix(".raw.stdout")
    raw_stderr_file = out_file.with_suffix(".raw.stderr")
    with open(raw_stdout_file, "wb") as fout, open(raw_stderr_file, "wb") as ferr:
        proc = subprocess.Popen(cmd, stdout=fout, stderr=ferr, text=False)
    # Snapshot pre-scan max scan guid for diff
    pre_scan_guids = set_existing_scan_guids(SPIDERFOOT_DB)

    # Poll until process exits or timeout
    deadline = time.time() + args.timeout
    last_status = None
    while True:
        time.sleep(2)
        if proc.poll() is not None:
            rc = proc.returncode
            print(f"[*] Process exited (rc={rc})")
            break
        if time.time() > deadline:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            rc = -1
            print(f"[!] Timed out after {args.timeout}s — partial results retrieved",
                  file=sys.stderr)
            break
        # Print progress every 15s
        new_guids = set_existing_scan_guids(SPIDERFOOT_DB) - pre_scan_guids
        if new_guids:
            status_now = db_scan_status(SPIDERFOOT_DB, list(new_guids)[0])
            if status_now != last_status:
                last_status = status_now
                print(f"[*] t+{int(time.time()-t0)}s — scan status: {status_now}")

    elapsed = time.time() - t0
    print(f"[*] Process done in {elapsed:.1f}s")

    # The authoritative event source for v4 is the SQLite DB
    events = fetch_events_from_db(SPIDERFOOT_DB, pre_scan_guids)
    print(f"[*] Fetched {len(events)} events from SQLite DB (post-scan GUIDs)")

    # Move raw stdout/stderr files to the output directory (already there as siblings)
    print(f"[+] Raw stdout: {raw_stdout_file}  ({raw_stdout_file.stat().st_size if raw_stdout_file.exists() else 0} bytes)")
    print(f"[+] Raw stderr: {raw_stderr_file}  ({raw_stderr_file.stat().st_size if raw_stderr_file.exists() else 0} bytes)")

    # Build normalized entities file
    entities_file = out_file.with_suffix(".entities.json")
    build_normalized(events, str(out_file), entities_file, raw_stdout=str(raw_stdout_file),
                    raw_stderr=str(raw_stderr_file), use_case=use_case, seed=seed)
    print(f"[+] Entities file: {entities_file}")
    if not events:
        print(f"[!] No events collected. Possible causes:", file=sys.stderr)
        print(f"    - All API-key modules were skipped (configure spiderfoot.cfg)",
              file=sys.stderr)
        print(f"    - Network/firewall blocked outbound", file=sys.stderr)
        print(f"    - Scan aborted early (check ~/tools/spiderfoot/spiderfoot.log)",
              file=sys.stderr)
        print(f"    - Try '-u passive' for faster/lower-friction modes", file=sys.stderr)


def set_existing_scan_guids(db_path: Path) -> set:
    """Return set of scan guids that exist in the DB right now (pre-scan state)."""
    if not db_path.exists():
        return set()
    try:
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        rows = c.execute("SELECT guid FROM tbl_scan_instance").fetchall()
        conn.close()
        return {r[0] for r in rows}
    except sqlite3.Error:
        return set()


def db_scan_status(db_path: Path, guid: str) -> str:
    """Return latest scan status string (RUNNING, FINISHED, ERROR-FAILED, etc.)."""
    try:
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        row = c.execute(
            "SELECT status FROM tbl_scan_instance WHERE guid = ?", (guid,)
        ).fetchone()
        conn.close()
        return row[0] if row else "UNKNOWN"
    except sqlite3.Error:
        return "UNKNOWN"


def fetch_events_from_db(db_path: Path, exclude_guids: set) -> list:
    """Read all events from new scan guids added after snapshot."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    new_rows = c.execute(
        "SELECT guid, seed_target, status, started, ended "
        "FROM tbl_scan_instance ORDER BY started DESC"
    ).fetchall()

    target_guids = []
    for row in new_rows:
        guid = row[0]
        # Only consider scans not in exclude set (i.e., post-snapshot)
        # If exclude set is empty (pre-existing setup), take the latest 1
        if (exclude_guids and guid not in exclude_guids) or \
           (not exclude_guids and len(target_guids) == 0):
            target_guids.append(guid)
        if len(target_guids) >= 1:
            # We only want the single latest scan we just ran
            break

    if not target_guids:
        conn.close()
        return []

    guid = target_guids[0]
    rows = c.execute(
        "SELECT type, module, data, generated, confidence, risk, source_event_hash "
        f"FROM tbl_scan_results WHERE scan_instance_id = ? AND type != 'ROOT' "
        "ORDER BY generated",
        (guid,)
    ).fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "type": row[0],
            "module": row[1],
            "data": row[2],
            "generated": row[3],
            "confidence": row[4],
            "risk": row[5],
            "source_event_hash": row[6],
            "scan_guid": guid,
        })
    return events


def build_normalized(events: list, source_file: str, out_path: Path,
                     raw_stdout: str = "", raw_stderr: str = "",
                     use_case: str = "", seed: str = ""):
    """Group events by type into a single normalized JSON file."""
    by_type = defaultdict(list)
    for ev in events:
        by_type[ev["type"]].append(ev)

    summary = {
        "meta": {
            "input_file": source_file,
            "generated_at": datetime.now().isoformat(),
            "total_events": len(events),
            "event_type_count": len(by_type),
            "raw_stdout": raw_stdout,
            "raw_stderr": raw_stderr,
            "use_case": use_case,
            "seed": seed,
        },
        "events_by_type": {k: v for k, v in by_type.items()},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"[*] Normalized {len(events)} events into {len(by_type)} types")


def normalize_report(in_path: Path, out_path: Path):
    """DEPRECATED: kept for compat with `normalize` subcommand."""
    content = in_path.read_text()
    entities = defaultdict(list)
    raw_events = []

    # Try JSONL / JSON Array
    stripped = content.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            if stripped.startswith("["):
                # JSON array; strip trailing/leading whitespace
                arr = json.loads(content)
                for ev in arr:
                    raw_events.append(ev)
                    etype = ev.get("_type") or ev.get("type") or "UNKNOWN"
                    entities[etype].append(ev)
            else:
                # JSONL
                for line in content.splitlines():
                    line = line.strip().rstrip(",")
                    if not line or line in ("[", "]"):
                        continue
                    try:
                        ev = json.loads(line)
                        raw_events.append(ev)
                        etype = ev.get("type") or ev.get("_type") or "UNKNOWN"
                        entities[etype].append(ev)
                    except json.JSONDecodeError:
                        pass
        except json.JSONDecodeError:
            pass
    else:
        # TSV
        for line in content.splitlines():
            parts = line.split("\t")
            if len(parts) >= 4:
                ev = {
                    "module": parts[0],
                    "source": parts[1],
                    "type": parts[2],
                    "data": parts[3],
                }
                raw_events.append(ev)
                entities[ev["type"]].append(ev)

    summary = {
        "meta": {
            "input_file": str(in_path),
            "generated_at": datetime.now().isoformat(),
            "total_events": len(raw_events),
            "event_type_count": len(entities),
        },
        "events_by_type": dict(entities),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"[*] {in_path}: normalized {len(raw_events)} events → {len(entities)} types")


def cmd_normalize(args):
    normalize_report(Path(args.input), Path(args.output))


def cmd_merge(args):
    """Merge multiple normalized entity files."""
    merged = defaultdict(list)
    sources = []
    for path in args.inputs:
        data = json.loads(Path(path).read_text())
        sources.append(path)
        for etype, events in data.get("events_by_type", data.get("event_types", {})).items():
            for ev in events:
                if not isinstance(ev, dict):
                    continue
                # Tag source
                if "_source_files" not in ev:
                    ev["_source_files"] = []
                ev["_source_files"].append(path)
                merged[etype].append(ev)
    out = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "sources": sources,
            "total_events": sum(len(v) for v in merged.values()),
            "event_type_count": len(merged),
        },
        "events_by_type": dict(merged),
    }
    Path(args.output).write_text(json.dumps(out, indent=2, default=str))
    print(f"[+] Merged {len(sources)} files → {out['meta']['total_events']} events → {args.output}")


def cmd_fallback(args):
    """Run the no-API-key fallback OSINT pipeline.

    Strategy:
      - If email:    holehe (account presence) + h8mail (public breaches) +
                     email local-part as username + GHunt (if Gmail)
      - If username: aliens-eye + maigret + sherlock parallel
      - If domain:   crt.sh + Wayback + amass (if available)
      - If phone:    numverify public page (limited)
      - Cross-cut:   Yahoo TW search for CJK contexts
    """
    seed = args.seed
    seed_type = classify_seed(seed)
    print(f"[*] Fallback pipeline for {seed_type}: {seed}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_seed = re.sub(r"[^A-Za-z0-9._-]", "_", seed)
    out_dir = Path(args.output) / f"fallback_{safe_seed}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    username = None
    domain = None
    if seed_type == "email":
        local, _, dom = seed.partition("@")
        username = local
        domain = dom
    elif seed_type == "username":
        username = seed
    elif seed_type == "domain":
        domain = seed

    results = {}

    # Parallel subprocess calls
    futures = {}

    if username:
        # holehe — email account presence
        futures["holehe"] = subprocess.Popen(
            ["holehe", "--no-icolor", "--only-positive", seed]
            if seed_type == "email" else ["true"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # aliens-eye
        futures["aliens_eye"] = subprocess.Popen(
            ["aliens_eye", "username", "--profile", "full",
             "--format", "json", "--output", str(out_dir / "aliens_eye.json")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # maigret (best for non-English platforms)
        futures["maigret"] = subprocess.Popen(
            ["maigret", username, "--json",
             "--output", str(out_dir / "maigret")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    if seed_type == "email":
        # h8mail — public breach hunt
        futures["h8mail"] = subprocess.Popen(
            ["h8mail", "-t", seed, "-o", str(out_dir / "h8mail.json")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    if domain:
        # crt.sh
        crt_cmd = ["curl", "-s",
                   f"https://crt.sh/?q=%25.{domain}&output=json",
                   "-o", str(out_dir / "crt.json")]
        futures["crt_sh"] = subprocess.Popen(
            crt_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        # Wayback Machine
        wb_cmd = ["curl", "-s",
                  f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*"
                  "&output=json&fl=original&collapse=urlkey",
                  "-o", str(out_dir / "wayback.json")]
        futures["wayback"] = subprocess.Popen(
            wb_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    if seed_type == "email" and seed.endswith("@gmail.com"):
        futures["ghunt"] = subprocess.Popen(
            ["ghunt", "email", seed, "--json", str(out_dir / "ghunt.json")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

    # Wait for all
    for name, p in futures.items():
        out, err = p.communicate()
        rc = p.returncode
        results[name] = {
            "returncode": rc,
            "stdout_len": len(out),
            "stderr": err[:500] if err else "",
        }
        status = "ok" if rc == 0 else f"rc={rc}"
        print(f"  - {name}: {status}")

    # Cross-cutting: Yahoo TW search (for CJK real-person)
    # (Yahoo TW doesn't block bot UA — see osint skill cjk playbook)
    if seed_type in ("email", "username"):
        query = username or seed
        yahoo_cmd = [
            "curl", "-s",
            f"https://tw.search.yahoo.com/search?p={query}&fr=yfp-search",
            "-A", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "-o", str(out_dir / "yahoo_tw.html"),
        ]
        subprocess.run(yahoo_cmd, capture_output=True, text=True, timeout=30)
        results["yahoo_tw"] = {"returncode": 0, "note": "saved HTML, parse separately"}

    # Save summary
    summary = {
        "meta": {
            "seed": seed,
            "seed_type": seed_type,
            "generated_at": datetime.now().isoformat(),
            "output_dir": str(out_dir),
        },
        "tools_run": results,
    }
    summary_path = out_dir / "fallback_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"[+] Fallback pipeline complete → {out_dir}")
    print(f"    Summary: {summary_path}")


def cmd_modules(args):
    """List SpiderFoot modules."""
    pyp = ensure_venv()
    result = subprocess.run(
        [pyp, str(SPIDERFOOT_DIR / "sf.py"), "-M"],
        capture_output=True, text=True
    )
    modules = {}
    for line in result.stdout.splitlines():
        if not line.strip() or line.startswith("sfp_") is False:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            name, desc = parts
            modules[name] = desc

    if args.filter == "api-key":
        # Heuristic: modules whose description mentions API/key/token
        filtered = {n: d for n, d in modules.items()
                    if re.search(r"\bapi\b|\bkey\b|\btoken\b", d, re.I)}
    elif args.filter == "email":
        filtered = {n: d for n, d in modules.items()
                    if re.search(r"\bemail\b|\bbreach\b|\bpwned\b|\bpassword\b", d, re.I)}
    elif args.filter == "domain":
        filtered = {n: d for n, d in modules.items()
                    if re.search(r"\bdomain\b|\bdns\b|\bsubdomain\b|\bwhois\b", d, re.I)}
    else:
        filtered = modules

    for name, desc in sorted(filtered.items()):
        print(f"{name:30s} {desc}")
    print(f"\n{len(filtered)} modules ({len(modules)} total)")


def cmd_event_types(args):
    """List SpiderFoot event types."""
    pyp = ensure_venv()
    result = subprocess.run(
        [pyp, str(SPIDERFOOT_DIR / "sf.py"), "-T"],
        capture_output=True, text=True
    )
    types = []
    for line in result.stdout.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            types.append((parts[0], parts[1] if len(parts) > 1 else ""))

    if args.category:
        cat = args.category.lower()
        filtered = [(n, d) for n, d in types if cat in (n + " " + d).lower()]
    else:
        filtered = types

    for name, desc in filtered:
        print(f"{name:48s} {desc}")
    print(f"\n{len(filtered)} types ({len(types)} total)")


def cmd_hx2(args):
    """Start SpiderFoot HX2 web UI in background."""
    pyp = ensure_venv()
    listen = args.listen
    print(f"[*] Starting SpiderFoot HX2 web UI on {listen}")
    print(f"[*] Open http://{listen.split(':')[0]}:{listen.split(':')[1]}")
    print(f"[*] To stop: pkill -f 'sf.py -l {listen}'")

    proc = subprocess.Popen(
        [pyp, str(SPIDERFOOT_DIR / "sf.py"), "-l", listen],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # Wait until ready
    time.sleep(3)
    if proc.poll() is None:
        print(f"[+] HX2 running with PID {proc.pid}")
        print(f"[+] Logs: stdout piped (pid preserved). Use 'pkill -f sf.py' to stop.")
        proc.terminate()  # in foreground we don't keep it alive
        # Actually, for background mode, the caller should use & or nohup
        print(f"[*] Foreground mode — to run in background:")
        print(f"    nohup {pyp} {SPIDERFOOT_DIR / 'sf.py'} -l {listen} "
              f"> ~/osint-reports/hx2.log 2>&1 &")
    else:
        print(f"[!] HX2 exited immediately: {proc.stderr.read()}")


def main():
    ap = argparse.ArgumentParser(
        description="SpiderFoot OSINT wrapper for Hermes Agent",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Run a SpiderFoot scan")
    p_scan.add_argument("-s", "--seed", required=True, help="Target seed (email/domain/username/phone/IP/BTC)")
    p_scan.add_argument("-u", "--use-case", choices=["all", "footprint", "investigate", "passive"])
    p_scan.add_argument("-o", "--output", default=str(REPORT_DIR))
    p_scan.add_argument("-t", "--types", help="Comma-separated event types (filters)")
    p_scan.add_argument("-m", "--modules", help="Comma-separated module names (overrides use_case)")
    p_scan.add_argument("--max-threads", type=int, default=10)
    p_scan.add_argument("--timeout", type=int, default=1800, help="Max seconds")
    p_scan.set_defaults(func=cmd_scan)

    p_norm = sub.add_parser("normalize", help="Convert raw SF output → entity-keyed JSON")
    p_norm.add_argument("-i", "--input", required=True)
    p_norm.add_argument("-o", "--output", required=True)
    p_norm.set_defaults(func=cmd_normalize)

    p_merge = sub.add_parser("merge", help="Merge multiple normalized JSON files")
    p_merge.add_argument("-i", "--inputs", nargs="+", required=True)
    p_merge.add_argument("-o", "--output", required=True)
    p_merge.set_defaults(func=cmd_merge)

    p_fb = sub.add_parser("fallback", help="Run no-API-key fallback OSINT pipeline")
    p_fb.add_argument("-s", "--seed", required=True)
    p_fb.add_argument("-o", "--output", default=str(REPORT_DIR))
    p_fb.set_defaults(func=cmd_fallback)

    p_mod = sub.add_parser("modules", help="List SpiderFoot modules")
    p_mod.add_argument("--filter", choices=["api-key", "email", "domain", "all"], default="all")
    p_mod.set_defaults(func=cmd_modules)

    p_evt = sub.add_parser("event-types", help="List event types")
    p_evt.add_argument("--category", default="")
    p_evt.set_defaults(func=cmd_event_types)

    p_hx2 = sub.add_parser("hx2", help="Start SpiderFoot HX2 Web UI")
    p_hx2.add_argument("-l", "--listen", default="127.0.0.1:5001")
    p_hx2.set_defaults(func=cmd_hx2)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
