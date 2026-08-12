---
name: reverse-engineering
description: Complete Reverse Engineering skill — Ghidra, IDA, radare2, Binary Ninja,
  angr symbolic execution, deobfuscation, unpacking, anti-debug bypass, Go/Rust/.NET/Java/Android/iOS/WebAssembly
  reversing, malware analysis, game hacking, and binary triage automation.
version: 1.0.0
category: red-teaming
license: MIT
metadata:
  hermes_origin: import
tags:
- reverse-engineering
- ghidra
- angr
- ida
- radare2
- malware
- deobfuscation
- binary-analysis
- firmware
- mobile
related_skills:
- ctf-playbook
- security-orchestrator
- network-pentest
---

# Reverse Engineering — Complete Framework

## Tool Ecosystem (2025-2026)

| Tool | Type | Best For | Platform | 2025-2026 Updates |
|:-----|:-----|:---------|:---------|:------------------|
| **Ghidra 11.3+** | SRE framework | Decompilation, scripting, headless | All (Java) | VS Code integration, source mapping, PCode emulation improvements |
| **IDA Pro 9.0** | Interactive disassembler | Deep manual analysis, FLIRT | Win/Linux/Mac | Lumina server, cloud decompiler, Rust/Go improved type recovery |
| **Binary Ninja 4.x** | Modern RE platform | Speed, Python API, MLIL/IL | Win/Linux/Mac | ML-powered function detection, WASM improvements |
| **radare2/rizin** | CLI framework | Quick triage, CTF, scripting | All | ESIL improvements, better ESIL emulation |
| **x64dbg / x32dbg** | Windows debugger | Dynamic Windows analysis | Windows | ScyllaHide integration, better anti-debug |
| **GDB/pwndbg/gef** | Linux debugger | Dynamic Linux analysis | Linux | GDB 14+ Python API improvements |
| **angr 9.2+** | Symbolic execution | Automated CTF, vuln finding | Python | dAngr (GDB-like), LIFT (LLM-optimized IR), Veritesting improvements |
| **Frida 16+** | Dynamic instrumentation | Runtime hooking (all platforms) | All | Better WASM support, early instrumentation |
| **RevEng.AI** | AI binary intelligence | Function similarity, malware classification | Cloud/API | Foundational models for binary similarity, function ID |
| **Triton / Miasm** | Symbolic/DSE | Deobfuscation, VM lifting | Python | Improved CFF deobfuscation, VM lifting |
| **WASM Tools** | WASM RE | wasm2wat, wasm-decompile, wasm-rev | All | WasmRev (multi-modal LLM), wasm-stats, kotlinc/wasm |
| **Rust/Go tools** | Modern RE | GoReSym, GoStringExtractor, RIFT, alphaGolang | All | REcon 2026 training, JPCERT Rust research, alphaGolang updates |

---

## Ghidra — Complete Reference (11.3+, 2025)

### Headless Analysis

```bash
# Auto-analyze
~/ghidra/support/analyzeHeadless /tmp/proj ProjName -import binary -postScript AutoAnalysis.java

# With Python script
~/ghidra/support/analyzeHeadless /tmp/proj ProjName -import binary -postScript myscript.py

# Parallel headless (11.3+)
~/ghidra/support/analyzeHeadless /tmp/proj ProjName -import binary1 binary2 binary3 -parallel -postScript batch.py
```

### Python Scripting (PyGhidra / Pyhidra)

```python
# pip install pyghidra  (external, Jython-based, legacy)
# OR use built-in Pyhidra (Ghidra 11.3+): no pip needed, use ghidra-python

import pyghidra

with pyghidra.open_program("binary") as flat_api:
    program = flat_api.getCurrentProgram()
    listing = program.getListing()
    fm = program.getFunctionManager()
    
    for func in fm.getFunctions(True):
        print(f"0x{func.getEntryPoint():x}: {func.getName()}")
    
    for instr in listing.getInstructions(True):
        print(f"0x{instr.getAddress()}: {instr}")

# Decompiler access
from ghidra.app.decompiler import DecompInterface
decomp = DecompInterface()
decomp.openProgram(program)
for func in fm.getFunctions(True):
    result = decomp.decompileFunction(func, 30, monitor)
    if result.decompileCompleted():
        print(result.getDecompiledFunction().getC())

# Ghidra 11.3+ Pyhidra (built-in, Python 3)
# Use ghidra-python command instead of python3
# ghidra-python -c "import ghidra; print('Pyhidra works')"

# Headless with Pyhidra
# analyzeHeadless ... -postScript script.py  # script runs in Pyhidra context
```

### Ghidra 11.3+ New Features (2025)

```python
GHIDRA_113_NEW = {
    'vscode_integration': 'Tools → Create VSCode Module Project… — scaffold Ghidra extensions in VS Code with debugging launchers and Gradle export. Edit Script with Visual Studio Code — opens scripts in VS Code workspace with autocomplete/navigation. Configure via Edit → Tool Options → Visual Studio Code Integration.',
    'source_mapping': 'Enhanced source code mapping via Program SourceFileManager. New "View Source…" action opens source files at correct line in Eclipse or VS Code. Configurable via "Source Files and Transforms" tool option.',
    'pcode_improvements': 'PCode emulator enhancements for better snippet emulation and semantic analysis.',
    'performance': 'Significant analysis speed improvements and memory optimization for large binaries.',
    'decompiler': 'Improved C decompilation quality, better type recovery, enhanced control flow reconstruction.',
    'headless': 'Better headless scripting API, improved parallel analysis support.',
    'pyhidra_builtin': 'Built-in Python 3 support via Pyhidra — no more Jython 2.7 limitation. Use Python 3 scripts directly with full stdlib access.',
    'ghidra_mcp': 'GhidraMCP plugin (github.com/LaurieWired/GhidraMCP) — LLM-guided RE via MCP protocol. Allows AI assistants to interact with Ghidra: list functions, decompile, rename, add comments, search strings, get cross-references.',
}

# PCode Emulation (Enhanced in 11.3)
from ghidra.app.emulator import EmulatorHelper
from ghidra.program.model.address import AddressSet

def emulate_snippet(program, start, end):
    emu = EmulatorHelper(program)
    emu.writeRegister('RAX', 0x1000)
    emu.writeRegister('RDI', 0xdeadbeef)
    addr_set = AddressSet(start, end)
    emu.setBreakpoints(addr_set)
    if emu.run(start, None, monitor):
        return {'rax': emu.readRegister('RAX')}

# GhidraMCP — AI-Assisted RE Workflow (2025+)
# Install: copy GhidraMCP extension to ~/.ghidra/extensions/ → restart Ghidra → Tools → GhidraMCP → Start Server
# Connect via MCP client (Claude Code, Hermes, etc.)
GHIDRA_MCP_WORKFLOW = """
# 1. Load binary in Ghidra, run full analysis
# 2. Start GhidraMCP server (default port 9876)
# 3. Connect MCP client (e.g., Claude Code with mcp.json config)
# 4. Ask AI to:
#    - "List all functions with 'check' or 'validate' in name"
#    - "Decompile function at 0x401234 and explain the logic"
#    - "Find all strings referencing 'flag', 'key', 'password'"
#    - "Get cross-references to strcmp at 0x400500"
#    - "Rename function 0x401100 to 'verify_flag' and add comment"
#    - "Search for crypto constants (0x61707865, 0x3320646e, etc.)"
# 5. AI can iterate: decompile → analyze → suggest angr harness → run symbolic execution
"""

# Practical Pyhidra Script Templates (Python 3)
PYHIDRA_TEMPLATES = {
    'find_crypto_constants': '''
import pyghidra
from ghidra.program.model.scalar import Scalar

CRYPTO_CONSTANTS = {
    # S-boxes, magic numbers, rotation constants
    0x61707865: "expand 32-byte k (ChaCha20)",
    0x3320646e: "ndo 3 (ChaCha20)",
    0x79622d32: "2-by (ChaCha20)",
    0x6b206574: "te k (ChaCha20)",
    0x67452301: "MD5 init A",
    0xefcdab89: "MD5 init B",
    0x98badcfe: "MD5 init C",
    0x10325476: "MD5 init D",
    0x5a827999: "SHA-1 K1",
    0x6ed9eba1: "SHA-1 K2",
    0x8f1bbcdc: "SHA-1 K3",
    0xca62c1d6: "SHA-1 K4",
    0x428a2f98: "SHA-256 K[0]",
    0x637f0a1: "AES S-box[0]",
}

with pyghidra.open_program("binary") as flat_api:
    program = flat_api.getCurrentProgram()
    listing = program.getListing()
    mem = program.getMemory()
    
    for block in mem.getBlocks():
        if block.isExecute() or block.isReadOnly():
            data = bytearray(block.getSize())
            mem.getBytes(block.getStart(), data)
            for i in range(len(data) - 3):
                val = int.from_bytes(data[i:i+4], 'little')
                if val in CRYPTO_CONSTANTS:
                    addr = block.getStart().add(i)
                    print(f"0x{addr}: {CRYPTO_CONSTANTS[val]} (0x{val:08x})")
''',

    'extract_all_strings_with_xrefs': '''
import pyghidra

with pyghidra.open_program("binary") as flat_api:
    program = flat_api.getCurrentProgram()
    string_manager = program.getStringManager()
    
    for s in string_manager.getAllStrings():
        addr = s.getAddress()
        refs = list(flat_api.getReferencesTo(addr))
        if refs:
            print(f"0x{addr}: \"{s}\"")
            for ref in refs:
                func = flat_api.getFunctionContaining(ref.getFromAddress())
                if func:
                    print(f"  → XREF from {func.getName()} at 0x{ref.getFromAddress()}")
''',

    'auto_rename_functions_by_strings': '''
import pyghidra

with pyghidra.open_program("binary") as flat_api:
    program = flat_api.getCurrentProgram()
    fm = program.getFunctionManager()
    string_manager = program.getStringManager()
    
    for func in fm.getFunctions(True):
        body = func.getBody()
        strings_in_func = []
        for s in string_manager.getAllStrings():
            if body.contains(s.getAddress()):
                strings_in_func.append(str(s))
        
        # Heuristic: rename based on interesting strings
        for s in strings_in_func:
            if 'flag' in s.lower() and 'check' not in func.getName().lower():
                new_name = f"check_flag_{func.getEntryPoint().getOffset():x}"
                func.setName(new_name, ghidra.program.model.symbol.SourceType.USER_DEFINED)
                print(f"Renamed 0x{func.getEntryPoint()} → {new_name}")
                break
            elif 'password' in s.lower() and 'verify' not in func.getName().lower():
                new_name = f"verify_password_{func.getEntryPoint().getOffset():x}"
                func.setName(new_name, ghidra.program.model.symbol.SourceType.USER_DEFINED)
                print(f"Renamed 0x{func.getEntryPoint()} → {new_name}")
                break
''',

    'decompile_all_functions': '''
import pyghidra
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

with pyghidra.open_program("binary") as flat_api:
    program = flat_api.getCurrentProgram()
    fm = program.getFunctionManager()
    
    decomp = DecompInterface()
    decomp.openProgram(program)
    monitor = ConsoleTaskMonitor()
    
    for func in fm.getFunctions(True):
        if func.isThunk(): continue
        result = decomp.decompileFunction(func, 60, monitor)
        if result.decompileCompleted():
            c_code = result.getDecompiledFunction().getC()
            # Save to file or process
            with open(f"decomp_{func.getName()}_{func.getEntryPoint().getOffset():x}.c", "w") as f:
                f.write(c_code)
        else:
            print(f"Failed to decompile {func.getName()}")
''',

    'find_switch_cases_flattened': '''
import pyghidra
from ghidra.program.model.pcode import PcodeOp

# Detect OLLVM Control Flow Flattening: look for switch(state) pattern
with pyghidra.open_program("binary") as flat_api:
    program = flat_api.getCurrentProgram()
    listing = program.getListing()
    fm = program.getFunctionManager()
    
    for func in fm.getFunctions(True):
        if func.isThunk(): continue
        body = func.getBody()
        instrs = list(listing.getInstructions(body, True))
        
        # Look for indirect jump via table (switch)
        state_var = None
        jump_table = None
        for i, instr in enumerate(instrs):
            # Pattern: load state → shift → add base → jump [rax]
            if "MOV" in str(instr) and "DWORD PTR" in str(instr):
                # Potential state variable load
                pass
            # Simplified: look for JMP [reg*8 + offset]
            if "JMP" in str(instr) and "[" in str(instr) and "*" in str(instr):
                print(f"0x{func.getEntryPoint()}: Possible CFF at {instr.getAddress()}")
                break
''',
}
```

### Key Ghidra Features

```python
GHIDRA_CTF = {
    'auto_analysis': 'Run full auto-analysis for cross-references, function boundaries',
    'data_types': 'Right-click → Data → Choose Data Type to fix misidentified types',
    'function_sig': 'Edit Function Signature to set proper prototypes',
    'string_xrefs': 'Window → Defined Strings → trace XREFs to usage',
    'graph_view': 'Space for Function Call Graph',
    'search_memory': 'Find byte patterns or constants',
    'patch': 'Right-click → Patch Instruction for CTF patches',
    'rename': 'L key → rename functions/variables',
    'bookmark': 'Ctrl+D to bookmark locations',
    'pcode_emu': 'Emulate snippets using PCode emulator',
}
```

---

## radare2/rizin — Quick Triage

```bash
r2 -A binary          # Analyze all
r2 -d binary          # Debug mode

# Analysis
aaaa                  # Full auto analysis
afl | sort -k3 -n -r  # Functions by size
afn new_name addr     # Rename function

# Disassembly
s main; pdf           # Seek + disassemble
pdf @ 0x401234        # Disassemble function at addr

# Search
/ flag                # String search
/w \x55\x48\x89\xe5   # Hex pattern
/e /bin/sh            # Wide string

# Cross-refs
axt @ 0x400123        # What references this?

# Strings
izz | grep flag       # All strings with flag

# Visual
VV @ main             # Visual graph

# Debugger
doo binary            # Reopen in debug
dr rip=0x400123       # Set register
db 0x400123           # Breakpoint
dc                    # Continue

# Patching
wx 9090 @ 0x400123    # Write hex NOP
wa nop @ 0x400123     # Write assembly NOP
```

---

## angr — Symbolic Execution (2025+)

### Core Patterns

```python
import angr
import claripy

# Pattern 1: Find input to reach success address
proj = angr.Project('./challenge', auto_load_libs=False)
state = proj.factory.entry_state()
simgr = proj.factory.simulation_manager(state)
simgr.explore(find=0x401234)
if simgr.found:
    print(simgr.found[0].posix.dumps(0))

# Pattern 2: Symbolic stdin
flag = claripy.BVS('flag', 8 * 40)
state = proj.factory.entry_state(stdin=angr.SimFile('/dev/stdin', content=flag))
for c in flag.chop(8):
    state.solver.add(c >= 0x20); state.solver.add(c <= 0x7e)

# Pattern 3: Find input avoiding failure
simgr.explore(find=0x401000, avoid=[0x402000, 0x403000])

# Pattern 4: argv[1]
state = proj.factory.entry_state(args=['./challenge', claripy.BVS('arg', 8*30)])

# Pattern 5: Hook functions
proj.hook(0x400500, angr.SIM_PROCEDURES['libc']['strlen']())

# Pattern 6: Constraint solving
state.solver.eval(sym_expr)        # One solution
state.solver.min(sym_val)          # Minimum value
state.solver.is_true(condition)    # Must be true?
state.solver.satisfiable()         # Check satisfiability

# Advanced: Veritesting (static+dynamic)
simgr = proj.factory.simulation_manager(state, veritesting=True)

# Advanced: Unicorn engine for speed
state = proj.factory.entry_state(add_options=angr.options.unicorn)

# Advanced: Custom exploration strategy
class MyExplorer(angr.exploration_techniques.ExplorationTechnique):
    def step(self, simgr):
        simgr.step()
        return simgr

# Advanced: SimProcedure for library functions
class my_strcmp(angr.SimProcedure):
    def run(self, s1, s2): return 0  # Always match

# Advanced: CFG + backward slicing
cfg = proj.analyses.CFGFast()
ddg = proj.analyses.DDG(cfg)  # Data dependency graph
```

### angr 2025+ New Features & Integrations
### angr 2025+ New Features & Integrations

```python
ANGR_2025_NEW = {
    'dangr': 'dAngr — GDB-like CLI debugger built on angr (NDSS 2025). Enables interactive symbolic debugging with GDB commands (break, step, continue, info registers) while leveraging full symbolic execution power. `pip install dangr`',
    'lift_llm': 'LIFT (Large-language-model Integrated Functional-equivalent-IR Transformation) — Uses LLMs to optimize IR blocks for symbolic execution. 53.5% reduction in execution time for big tests, 10.24% for random. arXiv:2507.04931.',
    'veritesting_improved': 'Enhanced veritesting with better static/dynamic hybrid analysis for complex binaries.',
    'angr_ghidra': 'angryGhidra plugin — Leverage angr symbolic execution from within Ghidra. Combine Ghidra decompilation with angr path exploration.',
    'angrop': 'ROP chain generation and analysis. `project.analyses.ROP()` for automated gadget finding and chain building.',
    'claripy_improvements': 'Better constraint solving performance, improved floating-point support, new backend solvers.',
    'simuvex_v2': 'Updated symbolic execution engine (SimuVEX) with better memory modeling and syscall handling.',
}

# angr + GhidraMCP + AI Combined Workflow (2025+)
ANGR_GHIDRA_MCP_AI = """
# Complete AI-Assisted RE Pipeline:

# Phase 1: Ghidra + GhidraMCP (Static Analysis)
# - Load binary in Ghidra, run full auto-analysis
# - Start GhidraMCP server
# - AI queries: "Find all functions handling user input"
# - AI queries: "Decompile function at 0x401234 and identify constraints"
# - AI queries: "Find crypto constants and string comparisons"
# - AI renames functions, adds comments, marks interesting addresses

# Phase 2: AI Generates angr Harness
# Based on Ghidra findings, AI writes targeted angr script:
#   - Entry state at vulnerable function (not program entry)
#   - Symbolic input with constraints from decompiled code
#   - Find/avoid addresses from control flow analysis
#   - Hook library functions (strcmp, strlen, crypto)

# Phase 3: LIFT Optimization (if available)
# - AI uses LIFT to optimize IR blocks before symbolic execution
# - 50%+ speedup on complex functions

# Phase 4: dAngr Interactive Debugging
# - If symbolic execution gets stuck, drop into dAngr
# - GDB-like commands with symbolic state inspection
# - Step through symbolically, examine constraints

# Phase 5: Solution Extraction & Verification
# - Extract concrete input from solver
# - Verify against original binary
# - Generate exploit/flag
"""

# Practical angr Script Templates (2025)
ANGR_TEMPLATES = {
    'ctf_flag_finder': '''
import angr
import claripy

# Template: Find flag input that reaches success address
proj = angr.Project('./challenge', auto_load_libs=False)

# 1. Identify target function from Ghidra (e.g., check_flag at 0x401234)
# 2. Create call state at function entry
target_addr = 0x401234  # From Ghidra analysis
state = proj.factory.call_state(target_addr)

# 3. Make argv[1] or stdin symbolic
flag_len = 64  # From string analysis
flag = claripy.BVS('flag', 8 * flag_len)

# Option A: stdin
state = proj.factory.call_state(target_addr, 
    stdin=angr.SimFile('/dev/stdin', content=flag, has_end=False))

# Option B: argv[1]
# state = proj.factory.call_state(target_addr, 
#     args=['./challenge', flag])

# 4. Add constraints from decompiled code (e.g., printable ASCII)
for c in flag.chop(8):
    state.solver.add(c >= 0x20)
    state.solver.add(c <= 0x7e)

# 5. Additional constraints from Ghidra (e.g., flag format)
# state.solver.add(flag[0:4] == claripy.BVV(b'flag', 32))
# state.solver.add(flag[4] == claripy.BVV(ord('{'), 8))

# 6. Explore with veritesting for complex paths
simgr = proj.factory.simulation_manager(state, veritesting=True)

# 7. Find success, avoid failure
success_addr = 0x401350  # From Ghidra: "Correct!" branch
fail_addrs = [0x401380, 0x401390]  # "Wrong!" branches
simgr.explore(find=success_addr, avoid=fail_addrs)

if simgr.found:
    solution = simgr.found[0].solver.eval(flag, cast_to=bytes)
    print(f"Flag: {solution.decode()}")
else:
    print("Not found - try different constraints or entry point")
''',

    'angrop_rop_chain': '''
import angr

# Template: Auto-generate ROP chain
proj = angr.Project('./vuln_binary', auto_load_libs=False)

# 1. Analyze for ROP
rop = proj.analyses.ROP()

# 2. Find gadgets
rop.find_gadgets()

# 3. Build chain for specific goal
# Example: execve("/bin/sh", 0, 0)
chain = rop.execve('/bin/sh', 0, 0)

# 4. Or build custom chain
chain = rop.chain()
chain.write(0xdeadbeef, b'/bin/sh\\x00')  # Write string
chain.rax = constants.SYS_execve
chain.rdi = 0xdeadbeef
chain.rsi = 0
chain.rdx = 0
chain.syscall()

# 5. Print payload
print(chain.payload_str())
''',

    'symbolic_exploration_with_hooks': '''
import angr
import claripy

# Template: Hook library functions for cleaner exploration
proj = angr.Project('./challenge', auto_load_libs=False)

# Custom SimProcedure for strcmp that returns symbolic result
class SymbolicStrcmp(angr.SimProcedure):
    def run(self, s1, s2):
        # Make return value symbolic
        retval = claripy.BVS('strcmp_result', self.arch.bits)
        # Add constraint: if strings equal, return 0
        # This helps explorer find path where strcmp matches
        self.state.add_constraints(
            claripy.If(
                claripy.And(*[self.state.memory.load(s1+i, 1) == self.state.memory.load(s2+i, 1) 
                             for i in range(32)]),
                retval == 0,
                retval != 0
            )
        )
        return retval

# Hook strcmp
proj.hook_symbol('strcmp', SymbolicStrcmp())

# Hook other libc functions
proj.hook_symbol('strlen', angr.SIM_PROCEDURES['libc']['strlen']())
proj.hook_symbol('memcmp', angr.SIM_PROCEDURES['libc']['memcmp']())
proj.hook_symbol('printf', angr.SIM_PROCEDURES['libc']['printf']())

# Now explore - strcmp won't constrain path unexpectedly
state = proj.factory.entry_state()
simgr = proj.factory.simulation_manager(state)
simgr.explore(find=0x401234)
''',

    'cfg_ddg_backward_slicing': '''
import angr

# Template: Backward slicing from target to input
proj = angr.Project('./challenge', auto_load_libs=False)

# 1. Build CFG
cfg = proj.analyses.CFGFast()

# 2. Build Data Dependency Graph (DDG)
ddg = proj.analyses.DDG(cfg)

# 3. Find target statement (e.g., flag comparison at 0x401250)
target_addr = 0x401250
target_node = None
for node in ddg.graph.nodes():
    if node.ins_addr == target_addr:
        target_node = node
        break

# 4. Backward slice to find input dependencies
if target_node:
    from angr.analyses import BackwardSlice
    bs = proj.analyses.BackwardSlice(
        cfg, ddg, target_node,
        control_flow_slice=False,  # Only data dependencies
        max_iter=1000
    )
    
    print("Instructions affecting target:")
    for stmt in bs.sliced_nodes:
        print(f"  0x{stmt.ins_addr}: {stmt.statement}")
'''
}
```

---

## Deobfuscation & Unpacking

### Packer Detection

```python
PACKERS = {
    'UPX': 'UPX0+UPX1 sections, "UPX!" string, upx -d to unpack',
    'ASPack': '".aspack" + ".adata" sections',
    'themida': 'High entropy, anti-debug, WinLicense API',
    'VMProtect': '".vmp0" + ".vmp1" sections, custom VM',
    'MPRESS': '".MPRESS1" + ".MPRESS2" sections',
    'PECompact': '"PEC2" section, renamed .text',
}

# Tool: Detect It Easy (DIE) — best packer detector
# Tool: PEiD for classic signature matching
# Tool: binwalk -E binary — entropy analysis

# UPX unpacking
"""
upx -d packed_binary  # standard
# If modified: find tail jump → OEP → dump memory → fix imports (Scylla)
"""

# Generic unpacking
"""
1. Run under debugger
2. BP on VirtualAlloc/VirtualProtect (common unpack APIs)
3. Find OEP (jump from unpacking stub to original code)
4. Dump process memory at OEP
5. Fix IAT (Scylla / ImportREC)
"""
```

### OLLVM Deobfuscation

```python
# OLLVM techniques:
# - Control Flow Flattening (CFF): A→B→C→D becomes switch(v){case0:B;v=1;case1:C;v=2;...}
# - Bogus Control Flow: fake opaque predicates added
# - Instruction Substitution: simple ops → complex equivalents
# - String Encryption: XOR/RC4 encrypted strings

# CFF deobfuscation:
# 1. Find state variable
# 2. Map all blocks + transitions
# 3. Reconstruct original CFG
# 4. Patch binary

# Tools: ollvm-unflattener (Miasm), D-810 (Binary Ninja), deflat (angr-based)

# Miasm-based CFF deobfuscation (headless)
MIASM_CFF = """
from miasm.analysis.machine import Machine
from miasm.analysis.simplifier import *
from miasm.analysis.interval import *
from miasm.core.locationdb import LocationDB

# Load binary
loc_db = LocationDB()
machine = Machine('x86_64')
container = machine.loader.load('binary')
bin_stream = container.bin_stream
lifter = machine.lifter_model_call(loc_db)
ira = lifter.ira

# Find function with CFF (large switch dispatch)
# Use miasm's cff_unflattener or custom script
# Reference: https://github.com/airbus-seclab/ollvm_unflattener
"""

# Generic unflattener approach
CFF_DEOBFUSCATION_STEPS = """
1. Identify dispatcher block (indirect jump via jump table)
2. Identify state variable (loaded at function entry, updated in each block)
3. Trace all basic blocks reachable from dispatcher
4. For each block: find next state value written before jump back to dispatcher
5. Build state→block mapping
6. Reconstruct original CFG by ordering blocks by state sequence
7. Patch binary: replace dispatcher with direct jumps
"""
```

### VM-Based Obfuscation

```python
VM_DEOBFUSCATION = """
VMProtect/Themida compile x86 → custom bytecode → embedded VM interpreter.

Approach:
1. Identify VM entry (push vm_eip, jump to dispatcher)
2. Trace VM: find fetch/decode/execute/dispatch handlers
3. Map bytecodes → original semantics
4. Symbolic execution (Triton/angr) to lift VM code
5. Reconstruct x86 from lifted semantics

Tools:
- DragonSlayer (DEF CON 33, 2025) — automated multi-layer VM unpacking
- SATURN (Quarkslab) — Triton-based  
- VMUnprotect — open source VMProtect devirtualizer
"""

# VM Analysis with Triton (2025 approach)
TRITON_VM_ANALYSIS = """
from triton import *
from triton.arch import ARCH.X86_64

# Initialize Triton
ctx = TritonContext()
ctx.setArchitecture(ARCH.X86_64)

# Load binary and find VM entry point
# Set initial registers (VM context pointer, bytecode pointer)
# Symbolically execute VM interpreter loop
# For each bytecode handler:
#   - Concretize bytecode operand
#   - Symbolically execute handler
#   - Record semantic effect (e.g., ADD: stack[-2] = stack[-1] + stack[-2])
# Build bytecode→semantics map
# Lift full VM program to IR
# Use Triton's simplification passes to clean up
# Convert back to x86 assembly
"""
```

### 2025-2026 Deobfuscation & Unpacking (NEW)

```python
DEOBFUSCATION_2025 = {
    'dragonslayer': 'DragonSlayer (DEF CON 33, 2025) — Automated multi-layer VM unpacking. Handles VMProtect + Themida nested layers. Outputs lifted x86 from custom bytecode. GitHub: anonymized/DragonSlayer',
    'saturn': 'SATURN (Quarkslab) — Triton-based deobfuscation. Symbolic execution for VM lifting. Handles OLLVM control flow flattening.',
    'vmunprotect': 'VMUnprotect — Open source VMProtect devirtualizer. Works on simpler VMProtect configurations.',
    'deflat': 'deflat (angr-based) — Control flow flattening deobfuscation using symbolic execution and pattern matching.',
    'miasm_cff': 'Miasm ollvm_unflattener — Structural analysis of flattened CFG to recover original flow.',
    'synthesis': 'Program synthesis approach (Souper, SMT-based) — Learn semantic equivalences for instruction substitution reversal.',
}

# AI-Assisted Deobfuscation (2025-2026)
AI_DEOBFUSCATION = """
# GhidraMCP + AI Deobfuscation Workflow:

# 1. Load obfuscated binary in Ghidra
# 2. AI via GhidraMCP:
#    - "Identify VM entry point and dispatcher"
#    - "Find all bytecode handlers in function 0x401000"
#    - "Decompile handler at 0x401200 and describe semantics"
#    - "Search for state variable updates in CFF pattern"
# 3. AI generates Triton/angr lifting script for each handler
# 4. AI reconstructs original CFG from bytecode trace
# 5. AI generates Ghidra script to patch binary with deobfuscated code

# Example AI prompts for GhidraMCP:
# "This function at 0x401000 looks like a VM dispatcher. List all basic blocks that jump back to it."
# "For each handler function, decompile and tell me what x86 instruction it implements."
# "The state variable is at [rbp-0x10]. Trace all writes to it and build state->block mapping."
# "Generate a Python script to patch the binary replacing the CFF dispatcher with direct jumps."
"""
```

---

## Anti-Debugging & Bypass

### Linux Anti-Debug

```python
LINUX_ANTI_DEBUG = {
    'ptrace': 'ptrace(PTRACE_TRACEME)→-1 if traced. Bypass: LD_PRELOAD hook, NOP check',
    'proc_status': '/proc/self/status→TracerPid≠0. Bypass: hook fopen/read',
    'timing': 'rdtsc/clock_gettime delta > threshold. Bypass: skip timing code',
    'parent': 'getppid() ≠ expected. Bypass: set $ppid in gdb',
    'SIGTRAP': 'Intentional → if caught. Bypass: gdb handle SIGTRAP',
    'self_modifying': 'Code overwrites itself (breakpoints erased). Use HW breakpoints',
}
```

### Windows Anti-Debug

```python
WINDOWS_ANTI_DEBUG = {
    'IsDebuggerPresent': 'PEB->BeingDebugged. Patch PEB or return 0',
    'NtGlobalFlag': 'PEB+0x68(32b)/PEB+0xBC(64b): flags by debugger. Set to 0',
    'NtQueryInfoProcess': 'ProcessDebugPort(0x7)≠0. Hook/patch',
    'TLS callback': 'Code BEFORE entry point! Set BP after TLS',
    'CloseHandle_exc': 'CloseHandle(invalid) raises → debugged',
    'INT3_scan': 'Scans for 0xCC bytes in code → BP detected',
}

# Universal bypass: ScyllaHide (Windows), NOP checks, hook functions
```

---

## Multi-Platform Reversing

### Go (GoLang)

```python
"""
Challenges: statically linked (2MB+), custom calling convention,
stack-based args, unique string storage.

Tools: GoReSym (Mandiant), GoStringExtractor (Volexity),
IDA Pro 8.3+ (built-in), alphaGolang (SentinelLabs)

Quick: strings binary | grep 'go1\.'  → identify Go binary
Find main.main via "main.main" string reference
"""
```

### Rust

```python
"""
Challenges: monomorphization produces many copies, mangled names,
string slices (ptr+len not null-term), Option/Result variants.

Key patterns:
- main via lang_start_internal call
- Strings: .rodata referenced as (ptr, len) pair
- Vec<T>: (pointer, length, capacity) triple
- Box<T>: single pointer to heap
- Demangle: rust-demangle or c++filt -p
"""
```

### .NET / C#

```python
"""
.NET = IL bytecode → easily decompiled!

Tools: dnSpy/dnSpyEx, ILSpy, de4dot, JustDecompile
Workflow: de4dot binary.exe → dnSpy → decompile to C# → debug

Unity IL2CPP: C#→C++→native
Tools: Il2CppDumper, Cpp2IL, Il2CppInspector
"""
```

### Java

```python
"""
Tools: JD-GUI, CFR (best modern), Procyon, Fernflower
Obfuscators: ProGuard, Zelix KlassMaster, Stringer, Allatori
Deobfuscation: java-deobfuscator, manual string + constant pool
"""
```

### WebAssembly

```python
"""
Tools: wabt (wasm2wat, wasm-decompile), Ghidra WASM plugin
Workflow: wasm-objdump -x → wasm2wat → wasm-decompile (C-like)
Stack machine: i32.add/sub/mul, call $func, br_if $label
"""
```

### Android APK

```python
"""
Static: unzip APK → jadx-gui (decompile DEX→Java)
        apktool (decode resources + Smali disassembly)
        Native .so → Ghidra/IDA (ARM64)

Dynamic: Frida (frida -U -l script.js com.app)
         objection (-g com.app explore → android hooking list classes)
         adb logcat | grep flag

Smali Patching: apktool d → edit .smali → apktool b → sign → install
"""
```

### iOS

```python
"""
Tools: Hopper, Ghidra (ARM64), Frida, objection, class-dump
Decrypt: App Store = FairPlay encrypted → frida-ios-dump or Clutch

Common targets:
- Jailbreak detection: hook +[NSFileManager fileExistsAtPath:]
- SSL pinning: hook SecTrustEvaluate
- Keychain: hook SecItemCopyMatching
"""
```

---

## Malware Analysis

### Pipeline

```python
MALWARE_PIPELINE = """
Phase 1: Static
  file → strings → DIE (packer ID) → capa (capability detection) → YARA

Phase 2: Dynamic (Sandbox)
  Run in isolated VM → Process Monitor → Wireshark/FakeNet → RegShot → API Monitor → memory dump

Phase 3: Deep
  Debug (x64dbg/GDB) → unpack memory (Scylla/pe-sieve) → extract C2 configs → find crypto constants

Phase 4: Report
  YARA rules → IOCs (CSV/STIX) → MITRE ATT&CK mapping
"""
```

### YARA Rules

```python
YARA_TEMPLATE = '''
rule Malware_Name {
    meta:
        description = "Detects Malware X"
        author = "analyst"
        hash = "md5_hash"
    strings:
        $s1 = "malicious_string" ascii wide
        $hex = { 55 8B EC 83 EC 10 6A 00 }
    condition:
        uint16(0) == 0x5A4D and (any of ($s*) or $hex)
}
'''
```

### Suspicious APIs

```python
SUSPICIOUS_APIS = {
    'VirtualAlloc/Ex': 'Memory allocation (unpacking)',
    'VirtualProtect': 'Change protection (RWX)',
    'WriteProcessMemory': 'Cross-process write',
    'CreateRemoteThread': 'Remote injection',
    'NtUnmapViewOfSection': 'Process hollowing',
    'SetWindowsHookEx': 'Keyboard/message hooking',
    'OpenProcess/ReadProcessMemory': 'LSASS dumping',
    'InternetConnect': 'C2 communication',
    'CryptEncrypt/Decrypt': 'Ransomware encryption',
    'RegSetValueEx/CreateService': 'Persistence',
}
```

---

## File Format Quick Reference

### ELF (Linux)

```bash
file binary; readelf -S binary; readelf -l binary
readelf -s binary 2>/dev/null | head -50  # symbols
readelf -d binary  # dynamic entries
ldd binary 2>/dev/null  # dependencies
```

### PE (Windows)

```python
"""
DOS: 'MZ', e_lfanew→PE offset
PE Sig: 'PE\\0\\0'
COFF: Machine, NumberOfSections, TimeDateStamp
Optional: EntryPoint, ImageBase, DataDirectory[16]
Key DataDir: [0]EXPORT [1]IMPORT [2]RESOURCE [5]RELOC [9]TLS [12]IAT
"""
```

### Mach-O (macOS/iOS)

```python
"""
magic: 0xFEEDFACE(32b) 0xFEEDFACF(64b) 0xCAFEBABE(fat)
cputype: 7(x86) 0x01000007(x86_64) 12(ARM) 0x0100000C(ARM64)
Key LC: LC_SEGMENT_64, LC_SYMTAB, LC_MAIN, LC_CODE_SIGNATURE
"""
```

---

## Automated Triage Script

```python
#!/usr/bin/env python3
"""Quick binary triage for CTF."""
import subprocess, sys, os

def triage(binary):
    print(f"\n{'='*60}\nBinary Triage: {binary}\n{'='*60}")
    r = subprocess.run(['file', binary], capture_output=True, text=True)
    print(f"Type: {r.stdout.strip()}")
    print(f"Size: {os.path.getsize(binary):,} bytes")
    
    r = subprocess.run(['strings', binary], capture_output=True, text=True)
    # Packer check
    for p in ['UPX', 'ASPack', 'themida', 'VMProtect']:
        if p.lower() in r.stdout.lower(): print(f"[!] Packed: {p}")
    
    # Arch
    out = r.stdout.lower()
    if 'x86-64' in out: print("Arch: x86_64")
    elif 'arm' in out: print("Arch: ARM")
    
    # Go?
    if b'go1.' in r.stdout.encode(): print("[!] Go binary")
    
    # Interesting strings
    keywords = ['flag','ctf','key','password','secret','correct','wrong','/bin/sh']
    found = [s.strip() for s in r.stdout.split('\n') if any(k in s.lower() for k in keywords)]
    if found:
        print(f"\nInteresting ({len(found)}):")
        for s in found[:20]: print(f"  {s[:100]}")
    
    print("\nNext: Load in Ghidra/IDA or r2 -A binary")

if __name__ == '__main__':
    triage(sys.argv[1]) if len(sys.argv) > 1 else print("Usage: triage.py <binary>")
```

---

## Deep Knowledge References

- **references/re-hardware-mobile-reference.md** — Comprehensive reverse engineering reference for hardware and mobile (1019 lines) covering Ghidra/Frida/binwalk/UART/JTAG/SPI/I2C analysis, Android/iOS reversing, firmware extraction, side-channel analysis, and radio protocol reversing (BLE, Zigbee, LoRa).

---

## Pitfalls

- **Stripped binaries**: No function names → recovery tools (FLIRT, GoReSym, Ghidra auto-analysis)
- **Heavily obfuscated**: VM-based protectors need specialized tools and significant time
- **Anti-debug traps**: Always identify and bypass before debugging
- **Packed binaries**: Unpack before static analysis — packed code looks like random data
- **Cross-architecture**: ARM/MIPS/RISC-V have different calling conventions and instruction sets
- **Time estimation**: Simple CTF: 30min, packed malware: hours, VM-protected: days
- **Legal**: Only analyze binaries you own or have explicit permission to reverse
