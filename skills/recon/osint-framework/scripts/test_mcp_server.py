#!/usr/bin/env python3
"""
OpenOSINT MCP Server Test Client
Tests the OpenOSINT MCP server by listing available tools.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Path to OpenOSINT installation
OPENOSINT_PATH = Path("${HERMES_PY:-python3}")
MCP_SERVER = Path("/tmp/OpenOSINT/openosint/mcp_server.py")


async def test_mcp_server():
    """Test the MCP server by connecting via stdio and listing tools."""
    # Start the MCP server as a subprocess
    proc = await asyncio.create_subprocess_exec(
        str(OPENOSINT_PATH), str(MCP_SERVER),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hermes-test", "version": "1.0.0"}
            }
        }
        proc.stdin.write((json.dumps(init_request) + "\n").encode())
        await proc.stdin.drain()

        # Read response
        response_line = await proc.stdout.readline()
        print(f"Initialize response: {response_line.decode().strip()}")

        # Send initialized notification
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        proc.stdin.write((json.dumps(initialized) + "\n").encode())
        await proc.stdin.drain()

        # Send list_tools request
        list_tools = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        proc.stdin.write((json.dumps(list_tools) + "\n").encode())
        await proc.stdin.drain()

        # Read tools response
        response_line = await proc.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"\n✅ MCP Server started successfully!")
            print(f"📋 Available tools ({len(tools)}):\n")
            for tool in tools:
                print(f"  🔧 {tool['name']}")
                print(f"     {tool['description'][:80]}...")
                print()
        else:
            print(f"❌ Error: {response}")

    finally:
        proc.terminate()
        await proc.wait()


async def test_tool_call(tool_name: str, arguments: dict):
    """Test calling a specific MCP tool."""
    proc = await asyncio.create_subprocess_exec(
        str(OPENOSINT_PATH), str(MCP_SERVER),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hermes-test", "version": "1.0.0"}
            }
        }
        proc.stdin.write((json.dumps(init_request) + "\n").encode())
        await proc.stdin.drain()
        await proc.stdout.readline()  # consume init response

        # Initialized notification
        proc.stdin.write((json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }) + "\n").encode())
        await proc.stdin.drain()

        # Call tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        proc.stdin.write((json.dumps(call_request) + "\n").encode())
        await proc.stdin.drain()

        # Read response (with timeout)
        try:
            response_line = await asyncio.wait_for(proc.stdout.readline(), timeout=60.0)
            response = json.loads(response_line.decode().strip())
            
            if "result" in response:
                content = response["result"].get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        print(item.get("text", ""))
            elif "error" in response:
                print(f"❌ Tool error: {response['error']}")
            else:
                print(f"Response: {response}")

        except asyncio.TimeoutError:
            print("❌ Tool call timed out (60s)")

    finally:
        proc.terminate()
        await proc.wait()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test OpenOSINT MCP Server")
    parser.add_argument("--list-tools", action="store_true", help="List all available tools")
    parser.add_argument("--call", help="Call a specific tool by name")
    parser.add_argument("--args", help="JSON arguments for tool call")

    args = parser.parse_args()

    if args.list_tools:
        asyncio.run(test_mcp_server())
    elif args.call:
        tool_args = json.loads(args.args) if args.args else {}
        asyncio.run(test_tool_call(args.call, tool_args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()