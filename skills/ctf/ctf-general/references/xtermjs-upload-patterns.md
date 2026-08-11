# xterm.js WebSocket Terminal Upload Patterns

For CTF challenges that use xterm.js over WebSocket (AIS3, CTFd web terminals).

## Problem
Uploading large exploit binaries (~1.3MB) through a WebSocket terminal to a QEMU VM. The VM has a ~300s timeout. Uploading too fast causes PTY buffer overflow → silent disconnect (0 chars on `recv()`, `WebSocketConnectionClosedException` on `send()`).

## Pattern 1: Delayed Echo Chunks (most reliable)

```python
import websocket, base64, gzip, time

# Compress first: 1.3MB -> 370KB -> 500KB b64
with open("exploit", "rb") as f:
    raw = f.read()
gz = gzip.compress(raw, compresslevel=9)
b64 = base64.b64encode(gz).decode()

# Upload with controlled delays
CHUNK = 200       # small chunks reduce PTY pressure
DELAY = 0.020     # 20ms = ~10KB/s, validated working (50s upload for 500KB)
# 30ms also works (75s upload) — both fit within 300s VM timeout

for i in range(0, len(b64), CHUNK):
    ws.send(f'echo -n "{b64[i:i+CHUNK]}" >> /tmp/e.gz.b64\r\n')
    time.sleep(DELAY)

# Decode (busybox: use gzip -d not gunzip)
ws.send("base64 -d /tmp/e.gz.b64 | gzip -d > /tmp/e; chmod +x /tmp/e\r\n")
```

Total upload: ~50-75 seconds for 500KB. Fits within 300s VM timeout.

## Pattern 2: Heredoc (NOT recommended — rarely works)

Heredoc approach sends data as one logical shell input, avoiding command flood.
However, this almost never works in practice — the PTY buffer invariably drops the terminator line.
Tested over 99 attempts with various markers (EOF, ENDOFFILE, ENDOFDATA), line endings (\n, \r\n),
and controlled pacing (50ms pauses every 50 lines). Never successfully terminated. Skip to Pattern 1.

```python
ws.send("cat > /tmp/e.gz.b64 << 'ENDOFFILE'\r\n")
for i in range(0, len(b64), 76):
    ws.send(b64[i:i+76] + "\r\n")
ws.send("ENDOFFILE\r\n")
# Then decode as above
```

**Symptom of failure**: output shows `>` PS2 prompts with base64 content, but `ENDOFFILE` never terminates — PTY dropped the terminator line. Fall back to Pattern 1.

**Marker pitfall**: short markers like `'EOF'` CAN appear in base64 data. Use ≥10-char markers. Base64 alphabet = `A-Za-z0-9+/=`.

## Drain-Then-Command Pattern (recommended)

After uploading with delayed echo chunks, the shell echoes back all upload data (~300K chars).
You MUST drain this before sending decode/run commands, or their output will be buried.

```python
# ... upload complete (85s for 500KB at 20ms/chunk) ...

# DRAIN: read and discard echo output until we see a shell prompt
ws.settimeout(30)
drained = ""
t0 = time.time()
while time.time() - t0 < 30:
    try:
        d = ws.recv()
        drained += d if isinstance(d, str) else d.decode('latin-1', errors='replace')
        if drained.rstrip().endswith('$ ') or drained.rstrip().endswith('# '):
            if len(drained) > 100:  # real prompt, not boot artifact
                break
    except:
        break
print(f"  drained {len(drained)} chars")

# NOW send decode + run + flag commands
ws.send("echo U1;base64 -d /tmp/e.gz.b64|gzip -d>/tmp/e 2>&1;chmod +x /tmp/e;ls -la /tmp/e;echo U2\r\n")
time.sleep(2)
ws.send("/tmp/e 2>&1;echo U3\r\n")
time.sleep(5)
ws.send("cat /flag /tmp/flag_out 2>/dev/null;echo ===F===\r\n")

# Read clean output (only command results, not upload echo)
ws.settimeout(60)
all_out = ""
while time.time() - t0 < 60:
    try:
        d = ws.recv()
        all_out += d if isinstance(d, str) else d.decode('latin-1', errors='replace')
        if "===F===" in all_out: break
    except: break
```

Without the drain step: receive 300K chars of upload echo, but decode/run output is at the end.
With a 60s read timeout, those 300K chars may not all arrive in time, causing the exploit output to be missed.
The drain step consumes the echo data first, leaving a clean channel for command results.

## Fire-and-Forget Read Pattern (legacy, less reliable)

Send all commands without draining, then read at the end. Risky because upload echo
can consume the read timeout, hiding command output.

```python
# ... upload ...
ws.send("echo U1; base64 -d /tmp/e.gz.b64 | gzip -d > /tmp/e; chmod +x /tmp/e; echo U2\r\n")
time.sleep(2)
ws.send("/tmp/e 2>&1; echo U3\r\n")
time.sleep(5)
ws.send("cat /flag /tmp/flag_out 2>/dev/null; echo ===F===\r\n")

# Read all output
ws.settimeout(60)
all_out = ""
while time.time() - t0 < 60:
    try:
        all_out += ws.recv()
        if "===F===" in all_out: break
    except: break
```

Intermediate reads risk capturing stale terminal echoes instead of command output.

## Session Flow

```python
# 1. PoW
resp = urlopen(URL + "/pow/challenge")
data = json.loads(resp.read())
nonce = solve_pow(data["challenge"], data["difficulty"])
pow_token = verify_pow(data["challenge"], nonce)

# 2. Connect WebSocket
ws = create_connection(f"ws://host/ws?token={token}&pow_token={pow_token}")

# 3. Wait for READY (handles queue/status/error messages)
ws.settimeout(300)
while True:
    msg = json.loads(ws.recv())
    if msg["type"] == "ready": break
    if msg["type"] == "error": raise ...

# 4. Wait for VM boot (15s), then upload + run
time.sleep(15)
# ... upload + decode + run + flag ...
```

## Key Pitfalls

- **WebSocket close detection**: `ws.recv()` returns 0 chars, `ws.send()` raises `WebSocketConnectionClosedException`. Retry the entire chain.
- **Busybox decompression**: `gzip -d`, NOT `gunzip`. Fallback: `zcat`.
- **PoW format**: `sha256(challenge + ':' + nonce)`, note the COLON.
- **Session timeout**: ~300s from VM boot. The full chain must complete within this.
- **Shell prompt**: after `{"type":"ready"}`, VM is still booting. Wait for prompt or use fixed 15s delay.
- **Background process output**: the process tool only shows output after exit. Use `notify_on_complete` and check the final log.
- **DRAIN ECHO BEFORE COMMANDS** (critical): after uploading with echo chunks, the shell echoes everything back (~300K chars for 500KB upload). You MUST drain this echo output (read until shell prompt appears) before sending decode/run/flag commands, or their output will be buried in the upload echo and missed by the read timeout.
- **Heredoc doesn't work**: tested across 99+ attempts with various markers and line endings. The PTY buffer drops the terminator line. Use Pattern 1 (delayed echo chunks) + drain instead.
