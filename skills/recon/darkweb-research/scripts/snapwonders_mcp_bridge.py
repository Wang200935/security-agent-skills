#!/usr/bin/env python3
"""
snapwonders_mcp_bridge.py — stdio MCP bridge (Hermes → Tor → snapWONDERS .onion)

為什麼需要這個 bridge:
- Hermes 內建 MCP HTTP client (mcp.client.streamable_http) 用 httpx,不主動走
  Tor SOCKS5。snapWONDERS 在 .onion,需要 Tor 才能連。
- 這個腳本在本地 spawn 成 stdio MCP server (Hermes 用 stdio transport 接它),
  本身內部用 socks5h 連 snapWONDERS /api/mcp,這樣流量才會走 Tor。
- Hermes 啟動時透過 `python3 snapwonders_mcp_bridge.py` spawn 此 subprocess,
  透過 stdin/stdout 做 JSON-RPC 2.0 通訊。

規格 (MCP 2.x):
- 緩衝: stdin/stdout line-buffered (buffering=1), log 走 stderr
- 一個 JSON-RPC 訊息一行 (newline-separated)
- handshake: initialize -> Initialized notification
- tools/list -> 回 tools (透過 forwarded POST /api/mcp)

用法 (與 Hermes config):
  mcp_servers:
    snapwonders:
      command: "python3"
      args: ["${DARKWEB_HOME:-./darkweb-research}/tools/snapwonders_mcp_bridge.py"]
      timeout: 180
      connect_timeout: 60

測試 (本地直接手測 handshake):
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}' | python3 snapwonders_mcp_bridge.py
"""
import json
import os
import sys
import socks
import urllib.request
import urllib.error
from typing import Any, Dict, Optional, Union

# 至關重要: line-buffered stdout (MCP 規格 - 每行一個 JSON-RPC 訊息)
try:
    sys.stdout.reconfigure(line_buffering=True)  # py3.7+: TextIOWrapper.reconfigure
except Exception:
    pass
try:
    sys.stdin.reconfigure(line_buffering=True)
except Exception:
    pass

# Tor SOCKS5 settings
TOR_HOST = "127.0.0.1"
TOR_PORT = 9050

# snapWONDERS onion MCP endpoint
SW_ONION_HOST = "swonders2xcif3yv2rsn54ics35rkfvugydk7xcwb2s3xntdc5zu7gid.onion"
SW_MCP_URL = f"http://{SW_ONION_HOST}/api/mcp"
SW_STATUS_URL = f"http://{SW_ONION_HOST}/api/status"

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

# Monkey-patch socket.create_connection 走 Tor
import socket
_orig_create = socket.create_connection
_socks = socks

def _tor_create(addr, *a, **kw):
    timeout = kw.get("timeout", 60) or (a[0] if a else 60)
    s = _socks.socksocket()
    s.set_proxy(_socks.SOCKS5, TOR_HOST, TOR_PORT, rdns=True)
    s.settimeout(timeout)
    s.connect(addr)
    return s

socket.create_connection = _tor_create


def log(msg: str):
    # 永遠 stderr (stdout 是 JSON-RPC channel)
    print(msg, file=sys.stderr, flush=True)


# API key (從環境變數讀, 由 Hermes config.yaml 的 mcp_servers[].env 注入)
# 沒填的話 bridge 仍可跑, status 等 no-auth endpoint 仍可用; forward 到需 auth
# 的 /api/mcp 會回 401/403 (server 會給明確訊息告訴你要 X-Api-Key)
SW_API_KEY = os.environ.get("SW_API_KEY") or os.environ.get("SNAPWONDERS_API_KEY", "")
if SW_API_KEY:
    log(f"[bridge] SW_API_KEY: loaded (len {len(SW_API_KEY)})")
else:
    log("[bridge] WARNING no SW_API_KEY; .onion 後端只 /api/status 可用,"
        " /api/mcp 會回 401/403. 取 key: 註冊 snapwonders.com 帳號 → profile → API key")


def http_post_json(url: str, body: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    """透 Tor 把 JSON-RPC POST 到 snapWONDERS /api/mcp"""
    data = json.dumps(body).encode("utf-8")
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",  # MCP spec 允許 SSE
        "MCP-Protocol-Version": "2024-11-05",
    }
    if SW_API_KEY:
        headers["X-Api-Key"] = SW_API_KEY
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(2_000_000)
            ct = r.headers.get("Content-Type", "")
            log(f"[bridge] POST {url} -> HTTP {r.status} content-type={ct}")
            # Streamable HTTP 可能回 SSE event 或 JSON
            if "text/event-stream" in ct:
                # 解析 data: chunks
                events = []
                for line in raw.decode("utf-8", "replace").splitlines():
                    if line.startswith("data:"):
                        events.append(line[5:].strip())
                if events:
                    return json.loads(events[-1])
                return {"error": "empty SSE stream"}
            return json.loads(raw.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read()[:1000].decode("utf-8", "replace")
        log(f"[bridge] HTTPError {e.code}: {body}")
        return {"error": f"HTTP {e.code}: {body}"}
    except Exception as e:
        log(f"[bridge] {type(e).__name__}: {e}")
        return {"error": f"{type(e).__name__}: {e}"}


# === JSON-RPC handlers ===
PROTOCOL = "2024-11-05"
SERVER_INFO = {"name": "snapwonders-bridge", "version": "1.0.0"}


def handle(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """回 JSON-RPC response (or None if notification)"""
    method = req.get("method")
    rid = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        # 不 forward 給 snapWONDERS - 先回我們自己 capability,
        # 然後實際上 init 通常只宣告 client <-> bridge,
        # bridge <-> server init 是私事我們自己處理
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": PROTOCOL,
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": SERVER_INFO,
            },
        }

    if method == "notifications/initialized":
        # 戳一下 snapWONDERS /api/status 確認活著
        try:
            reqw = urllib.request.Request(SW_STATUS_URL, headers={"User-Agent": UA})
            with urllib.request.urlopen(reqw, timeout=20) as r:
                status = json.loads(r.read(500))
                log(f"[bridge] snapWONDERS /api/status: {status}")
        except Exception as e:
            log(f"[bridge] status probe failed: {e}")
        return None  # notification -> no response

    if method == "tools/list":
        # 我們啟用的 tool 清單 (`mcp_snapwonders_*` 會在 Hermes 命名為此)
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "tools": [
                    {
                        "name": "status",
                        "description": "查 snapWONDERS 服務健康 (GET /api/status).",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "forward_rpc",
                        "description":
                            "把 JSON-RPC request (無 id) 直接 forward 到 snapWONDERS "
                            "/api/mcp (POST). 已知 available methods: initialize / "
                            "tools/list / resources/list / 等 (依 server 回應).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "method": {"type": "string"},
                                "params": {"type": "object", "default": {}},
                            },
                            "required": ["method"],
                        },
                    },
                ],
            },
        }

    if method == "tools/call":
        # Hermes 用 stdio call 我們的 (大寫) tools:[status, forward_rpc]
        tool = params.get("name")
        args = params.get("arguments", {})
        if tool == "status":
            try:
                reqw = urllib.request.Request(SW_STATUS_URL, headers={"User-Agent": UA})
                with urllib.request.urlopen(reqw, timeout=20) as r:
                    status = json.loads(r.read(500))
                return {
                    "jsonrpc": "2.0", "id": rid,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(status)}],
                    },
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32000, "message": str(e)},
                }
        if tool == "forward_rpc":
            sub_method = args.get("method")
            sub_params = args.get("params", {})
            fw_body = {"jsonrpc": "2.0", "id": 999, "method": sub_method,
                       "params": sub_params}
            resp = http_post_json(SW_MCP_URL, fw_body, timeout=60)
            return {
                "jsonrpc": "2.0", "id": rid,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(resp)}],
                },
            }
        return {
            "jsonrpc": "2.0", "id": rid,
            "error": {"code": -32601, "message": f"unknown tool: {tool}"},
        }

    # 未支援 method 直接 forward 給 snapWONDERS (best effort)
    if rid is not None:
        if isinstance(params, dict):
            fw = {"jsonrpc": "2.0", "id": rid, "method": method, "params": params}
        else:
            fw = {"jsonrpc": "2.0", "id": rid, "method": method}
        resp = http_post_json(SW_MCP_URL, fw, timeout=60)
        return {"jsonrpc": "2.0", "id": rid, "result": resp}

    return None


def main():
    log("[bridge] snapwonders_mcp_bridge starting (stdio)")
    log(f"[bridge] forwarding POST to {SW_MCP_URL}")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            log(f"[bridge] parse line failed: {e}")
            continue
        try:
            resp = handle(req)
        except Exception as e:
            rid = req.get("id") if isinstance(req, dict) else None
            resp = {"jsonrpc": "2.0", "id": rid,
                    "error": {"code": -32000, "message": str(e)}}
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
    log("[bridge] stdin EOF, exiting")


if __name__ == "__main__":
    main()
