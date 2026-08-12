# 2025-2026 CTF Landscape Update: AI-Assisted Solving & New Trends

### AI-Assisted CTF Solving (Game-Changing Trend)

**At DEF CON 33 (August 2025), AI-assisted CTF solving crossed a historic threshold**:
- **Blue Water team** won LiveCTF tournament using autonomous AI agents (Devin-based, 10 parallel agents). The AI independently solved 3 out of 5 challenges, including binary exploitation. The human player was still working on a challenge the agent had already solved and submitted.
- **"All You Need Is MCP"** — A team used IDA MCP + GPT-5 to solve a DEF CON Finals reverse engineering challenge in **12 minutes**. The LLM read decompilation via MCP, renamed functions, identified protocol, wrote exploit script, analyzed output, iteratively refined.
- **DARPA AIxCC** — $4M prize for autonomous AI vulnerability discovery. Winners: Team Atlanta (1st, $4M), Trail of Bits Buttercup (2nd, $3M), Theori (3rd, $1.5M). AI systems found 54 vulnerabilities and patched 68% in critical open-source software.
- **Google GenSec CTF** at DEF CON 33 — Dedicated AI-human collaboration CTF. 85% of participants found AI useful. Sec-Gemini (Google's cyber AI) rated "very helpful" or "extremely helpful" by 77%.
- **CSAW Agentic Automated CTF** — Build AI agents to solve CTF challenges autonomously.
- **UNbreakable Romania 2026** — AI agent ran entire CTF autonomously for $26.74 in ~1 hour, only human action was clicking start.

### Practical AI-Assisted Solving Workflow for Hermes

1. **Binary analysis**: Use GhidraMCP/OGhidra or IDA MCP + LLM to accelerate decompilation review
2. **Protocol RE**: Feed decompilation to LLM, ask it to identify protocol structure, flag exfil paths
3. **Exploit generation**: LLM can write pwntools exploit scripts from decompilation + vulnerability pattern
4. **Output analysis**: LLM analyzes exploit output, updates decompilation with findings, iterates
5. **Loop**: `gather knowledge (from IDA) → formulate hypothesis → create exploit script → analyze output → apply findings to IDA`
6. **Parallel agents**: Run multiple AI agents in parallel on different challenges (Blue Water used 10)

### Top CTF Competition Trends 2025-2026

| Competition | Key Themes | New Techniques |
|---|---|---|
| **DEF CON 33 CTF** | A/D + KotH + LiveCTF | AI agents, Rust binary RE, audio modulation exploitation |
| **HITCON CTF 2025** | AArch64 pwn, Python jail | PAC/BTI/relative vtables bypass, Python 3.13 setattr jail, multiprocessing pickle pipe injection |
| **Google CTF 2025** | Browser exploitation, crypto | SafeContentFrame race condition, Math.random prediction, AES shift_rows backdoor, bcrypt collision |
| **snakeCTF 2025** | Heap pwn | GLIBC_TUNABLES tcache disable → fastbin dup → mp_ overwrite → tcache re-enable |
| **KalmarCTF 2026** | ZK/crypto | SageMath PRNG state recovery, LLM-resistant challenge design |
| **DiceCTF 2026** | Pyjail | pickle/cpickle divergence in py3.15+, COPY opcode OOB |

### Top CTF Archives & Resources (2025-2026)

- **DEF CON CTF Finals 2025 source**: `github.com/Nautilus-Institute/finals-2025`
- **CTF archives**: `github.com/sajjadium/ctf-archives` — comprehensive challenge archive
- **pyjail collection**: `github.com/jailctf/pyjail-collection` — 113 challenges across 20+ CTFs
- **CTFtime**: `ctftime.org` — event calendar, writeups, team rankings
- **CTF writeups aggregator**: `ctftime.org/writeups`
- **how2heap**: `github.com/shellphish/how2heap` — updated for glibc 2.41/2.42
- **7Rocky/CTF-scripts**: `github.com/7Rocky/CTF-scripts` — SageMath/Python CTF solvers

### New Competition Formats

- **Attack/Defense resurgence**: DEF CON 33 still premier A/D CTF; Nautilus Institute stepping down, new organizers "Benevolent Bureau of Birds" for DEF CON 34
- **LiveCTF**: 1v1 tournament format, livestreamed on YouTube, AI agents now competitive
- **King of the Hill**: Optimize solutions per round, challenge changes every round
- **AI CTF**: Dedicated AI-human collaboration or AI-only competitions (GenSec, AIxCC, Agentic CTF)
- **LLM-resistant challenges**: Top CTFs now design challenges specifically resistant to LLM solving
