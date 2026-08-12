# AI-Assisted CTF Solving: MCP + LLM Workflow (DEF CON 33 Field Report)

### What happened at DEF CON 33 (August 2025)

**"All You Need Is MCP"** — A team used IDA Pro MCP + GPT-5 to solve a DEF CON CTF Finals RE challenge in **12 minutes**. The LLM:
1. Read IDA decompilation via MCP tool calls (`list_functions`, `decompile_function`, `rename_function`, `set_comment`)
2. Identified protocol, function purposes, and flag exfil path from decompilation
3. Wrote a pwntools exploit script from scratch
4. Ran the script, analyzed output, discovered the "Author" field was an MD5 hash of the flag
5. Updated IDA decompilation with findings (renamed functions, added comments)
6. Iterated: `gather knowledge (from IDA) → formulate hypothesis → create exploit script → analyze script output → apply new findings to IDA`
7. Final exploit: 10-byte payload (`\x10\x22\x32\x01\x11`) to extract flag from PNG tEXt chunk

**Blue Water** won LiveCTF tournament using autonomous AI agents (Devin-based, 10 parallel agents). AI independently solved 3/5 challenges including binary exploitation. Human player was working on a challenge the agent had already solved.

**DARPA AIxCC** — $4M prize. Team Atlanta (1st), Trail of Bits Buttercup (2nd), Theori (3rd). AI systems found 54 vulnerabilities and patched 68%.

**Google GenSec CTF** — 85% of participants found AI useful for security workflows.

### Practical AI-Assisted RE Workflow for Hermes

```
install IDA MCP or GhidraMCP → load challenge binary → 
LLM reads decompilation via MCP → renames functions → 
identifies protocol/vulnerability → writes exploit script → 
runs script → analyzes output → updates decompilation → iterate
```

**Key success factors** (from DEF CON 33):
- LLM needs access to the actual decompilation (not just disassembly)
- Explicitly update decompilation with findings after each iteration
- Give the LLM the flag format and any constraints upfront
- Allow the LLM to run Python scripts to check its own work
- Simple exploit paths (no tricks, just reversing) work best
- Works on straightforward RE; complex challenges with anti-LLM techniques resist

**Tools to install**:
- **IDA Pro MCP**: `github.com/mrexodia/ida-pro-mcp` — MCP server exposing IDA's decompiler
- **GhidraMCP / ReVa**: `github.com/cyberkaida/reverse-engineering-assistant` — 110 tools for Ghidra
- **OGhidra**: `github.com/LLNL/OGhidra` — AI-powered Ghidra with LLM + RAG + malware pattern detection

**Limitations observed**:
- Only solved 1/5 LiveCTF challenges and 1 Finals challenge — not a silver bullet
- Complex challenges with unusual obfuscation or multi-step logic resist LLM solving
- "Vibe-reversing" works for straightforward protocol reversing, not for creative exploitation
- Authors are now designing LLM-resistant challenges (KalmarCTF 2026: only 2 and 1 solves)
