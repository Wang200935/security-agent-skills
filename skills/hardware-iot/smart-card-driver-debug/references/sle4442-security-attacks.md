# SLE4442 Security Attack Surface — Complete Reference

## Chip Identification

| Chip | Manufacturer | Notes |
|------|-------------|-------|
| SLE4442 | Infineon/Siemens | Original, 1995 design |
| SLE5542 | Infineon | 100% compatible upgrade |
| IS23SC4442 | ISSI | Taiwan's most common clone |
| FM4442 | Fudan Microelectronics | China mainland staple |
| ISSI4442 | ISSI | Another variant |

Clone chips may have **weaker security logic** (easier to glitch).

---

## Memory Map

| Region | Size | Read | Write |
|--------|------|------|-------|
| Main Memory | 256 bytes (0x00–0xFF) | Free | Requires PSC |
| Protection Memory | 32 bits (protects 0x00–0x1F) | Free | Requires PSC + OTP |
| Security Memory | 4 bytes: EC[1] + PSC[3] | Free | Requires PSC |

- **EC (Error Counter)**: Byte 0 of security memory, bits 0-2 = 3 attempts
- **PSC (reference data)**: Bytes 1-3 of security memory
- Some clone chips **mask PSC** on read (return 00 00 00), but EC is always readable

### EC Values

| EC Value | Binary | Remaining Attempts | Meaning |
|----------|--------|-------------------|---------|
| 0xFF | 111xxxxx | 3 | Fresh, never attempted |
| 0xFB | 110xxxxx | 2 | 1 failed attempt |
| 0xF7 | 101xxxxx | 1 | Last chance — STOP |
| 0xF3 or lower | 011 or less | 0 | **PERMANENTLY LOCKED** |

---

## Attack Vectors (Ranked by Feasibility)

### 1. Logic Analyzer / Protocol Sniffing ⭐⭐⭐⭐⭐

**Severity: FATAL** — PSC transmitted in cleartext

- PSC sent as plaintext over I/O line during `Compare Verification Data`
- Anyone with logic analyzer on CLK+I/O lines captures PSC directly
- **Strom Carlson DEFCON 14**: Demonstrated on FedEx Kinko's ExpressPay
- **Tools**: Bus Pirate, Saleae, Open Bench Logic Analyzer, any USB sniffer
- **Cost**: $30–$200 | **Time**: Minutes | **Non-invasive**

Protocol details for decoding:
- 2-wire synchronous, LSB-first
- Data changes on falling clock edge
- ATR response: `A2 13 10 91` confirms SLE4442
- PSC visible in Compare Verification Data command bytes

### 2. Default PSC Attempt ⭐⭐⭐⭐⭐

**Most common PSC values:**

| PSC | Source | Probability |
|-----|--------|-------------|
| `FF FF FF` | Factory default (blank cards) | ~60-70% for campus cards |
| `B2 B2 B2` | Chinese suppliers | ~15-20% |
| `55 55 55` | Indian/Middle East vendors | ~5% |
| `00 00 00` | Lazy vendors | ~2% |

**Procedure** (ZERO RISK if PSC correct — EC resets on success):
```
1. Read Security Memory → confirm EC = 0xFF (3 attempts)
2. Try FF FF FF → if EC = 0xFF after = SUCCESS
3. If failed → EC = 0xFB (2 left), try B2 B2 B2
4. If failed → EC = 0xF7 (1 left), STOP
```

### 3. Clone Attack (No PSC Needed) ⭐⭐⭐⭐⭐

**SLE4442 has NO anti-cloning mechanism.**

Full attack:
1. Read all 256 bytes from target card (free, no PSC)
2. Buy blank SLE4442/SLE5542 (PSC = FF FF FF, guaranteed)
3. Write dumped data to blank card
4. Result: perfect clone, no PSC knowledge required

**Implication**: Read access = Full compromise. The PSC only protects writes,
not reads. Any system relying on SLE4442 for value storage is broken by design.

### 4. Timing Attack on PSC Verification ⭐⭐☆☆☆

**Theory**: Compare Verification Data does byte-by-byte comparison with early exit.
- Wrong byte 1 → fails fast (short execution time)
- Correct byte 1 + wrong byte 2 → fails slower
- **Reduces search space**: 2²⁴ → 3 × 2⁸ = 768 attempts

**Blocker**: EC only allows 3 attempts. Cannot observe enough timing differences.

**Becomes viable IF**: EC bypass achieved (glitching) → unlimited attempts
→ timing attack to recover PSC byte-by-byte in ≤768 attempts.

### 5. Power Analysis (SPA/DPA/CPA) ⭐⭐⭐⭐☆

**SLE4442 has NO countermeasures against power analysis.**

- **SPA (Simple Power Analysis)**: Visual identification of byte comparison loops
  - Current spikes per byte compared → count = which byte failed
  - Single trace may reveal PSC length and structure
  
- **DPA/CPA**: Statistical correlation across multiple traces
  - Hamming weight model on PSC bytes
  - 2⁸ hypotheses per byte × 3 bytes = 768 total hypotheses
  - Typical: 100-1000 traces per byte to recover

- **Equipment**: ChipWhisperer-Lite ($300), CW308 UFO board, shunt resistor
- **Time**: Hours to days

### 6. EM Emanation Analysis ⭐⭐⭐☆☆

Same principle as power analysis, non-contact:
- EM probe near chip during PSC verification
- Reference: NCC Group "Low Cost Attacks on Smart Cards"

### 7. Fault Injection — EC Bypass ⭐⭐⭐⭐☆

**THE key attack for locked/unknown-PSC cards.**

#### 7a. Voltage Glitching
Attack flow:
```
1. Send Compare Verification Data with candidate PSC
2. Precisely drop VCC during EC write cycle (~5ms window)
3. EC bit not decremented → attempt not consumed
4. Try next candidate
5. With unlimited attempts: brute force 2²⁴ or timing attack
```

Equipment options:
| Tool | Cost | Precision |
|------|------|-----------|
| ChipWhisperer-Lite | $300 | High |
| PicoGlitcher | $50 | Medium |
| DIY MOSFET + MCU | $20 | Low (but functional) |
| FPGA glitcher | $200-500 | High |

#### 7b. Clock Glitching
- Insert extra/fast clock cycles during EC comparison
- Target: Skip EC decrement instruction
- Same equipment as voltage glitching

#### 7c. IOActive Confirmation
IOActive states: *"if you try to guess it, you have 3 tries before being permanently
locked out forever (well forever for some, we can always perform magic on the part)"*
— This implies fault injection bypass is confirmed.

### 8. Silicon-Level Attacks ⭐⭐☆☆☆

**Chris Tarnovsky (Flylogic Engineering) — Toorcon 2006**
- Decapped SLE4442, photographed die
- Found security enable line loopback structure
- Suggested **shorting a trace** could defeat security measures
- Die photos: http://www.flylogic.net/blog/?p=17

| Attack | Cost | Time | Invasiveness |
|--------|------|------|-------------|
| UV light erasure of EC | High | Days | Destructive |
| Microprobing EC bits | $5K-50K | Days | Destructive |
| FIB circuit modification | $50K+ | Weeks | Destructive |

---

## Attack Feasibility Matrix

| Attack | Feasibility | Cost | Time | Invasive? | Success Rate |
|--------|-------------|------|------|-----------|--------------|
| Logic Analyzer Sniffing | ★★★★★ | $50-200 | Minutes | No | 100% (if transaction captured) |
| Default PSC (FF FF FF) | ★★★★★ | $0 | Seconds | No | 60-70% (Taiwan campus) |
| Full Clone (read+write new) | ★★★★★ | $5 (blank card) | Minutes | No | 100% |
| Timing Attack (standalone) | ★★☆☆☆ | $0 | Hours | No | BLOCKED by EC |
| Power Analysis (SPA) | ★★★★☆ | $500+ | Hours-Days | No | High |
| Voltage Glitching (EC bypass) | ★★★★☆ | $300+ | Days-Weeks | No | High with practice |
| Clock Glitching (EC bypass) | ★★★★☆ | $300+ | Days-Weeks | No | High with practice |
| Full Invasive (FIB/UV) | ★★☆☆☆ | $50K+ | Weeks | Yes | Near 100% |
| Online Brute Force | ★☆☆☆☆ | $0 | N/A | No | **IMPOSSIBLE** (3 attempts) |
| Offline Brute Force (EC bypass) | ★★★★★ | $300+ | Hours | No | 100% (once EC bypassed) |

---

## PSC Verification Protocol (Datasheet §2.3.7, §2.4)

### Compare Verification Data Command
```
Control byte: 0x33
Data: 3 bytes (PSC candidate)
```

### Verification Flow
```
Step 1: Write EC bit from 1→0 (EEPROM write, ~5ms)
Step 2: Compare 3-byte candidate with stored PSC (byte-by-byte)
Step 3: If MATCH → Reset EC to 111, enable write access until power-off
Step 4: If MISMATCH → EC bit stays 0, continue to next bit
```

After all 3 bits consumed → permanent write lock.

### ACR38/ACR39 Pseudo-APDU Interface
```
# Read Security Memory (EC + PSC[3])
FF B4 00 00 04 → returns 4 bytes

# Verify PSC (ACR38 sends 2-byte CODE internally)
FF 20 00 00 02 <CODE> → SW1=90, SW2=EC_value

# Read Main Memory
FF B0 00 <addr> <len> → returns data

# Write Main Memory
FF D0 00 <addr> 01 <value> → requires PSC verified

# Change PSC (after successful verify)
FF D2 00 00 03 <new_p1> <new_p2> <new_p3>
```

### Bus Pirate 2-WIRE Commands
```
m 2wire      # Set mode
20           # 20kHz clock
W 5          # 5V power
P P          # Enable pull-ups (MANDATORY)
L            # LSB first

# ATR
} { ^ } r:4   # Should return A2 13 10 91

# Read Security Memory
{ 0x31 0x01 r:4 }  # Command 0x31, address 0x01, read 4 bytes
# Returns: EC PSC1 PSC2 PSC3 (PSC may be masked on clones)

# Compare Verification Data
{ 0x33 PSC1 PSC2 PSC3 }

# Read Main Memory at address N, length L
{ 0x30 N r:L }
```

---

## Practical Attack Procedure (for Campus AC Cards)

### Phase 1: Reconnaissance (Zero Risk)
```
1. Insert card into ACR38/ACR39/SLE4442-capable reader
2. Read Security Memory → check EC
3. Read Main Memory → dump all 256 bytes
4. Read Protection Memory → identify protected bytes
5. Document everything
```

### Phase 2: PSC Recovery
If EC = 0xFF (3 full attempts):
```
Priority 1: Try FF FF FF (60-70% success rate)
Priority 2: Try B2 B2 B2 (if Chinese supplier)
Priority 3: Try 55 55 55
STOP if EC reaches 1 remaining
```

If EC < 0xFF (partial attempts already consumed):
```
更保守 — 只試 FF FF FF
STOP if EC = 1
```

If EC = 0 (locked):
```
Clone path: Read all memory → write to blank card (PSC = FF FF FF)
Or: Fault injection to bypass EC (requires hardware lab)
```

### Phase 3: If PSC Recovered
```
1. Change PSC to known value (FF 20 00 00 02 <CODE>)
2. Write any desired data to Main Memory
3. Set Protection Bits if needed
```

### Phase 4: If PSC Unknown + Clone Sufficient
```
1. Full memory dump (already done in Phase 1)
2. Buy blank SLE4442/SLE5542 card
3. Write dump to blank card (PSC = FF FF FF, guaranteed)
4. Done — perfect functional clone
```

---

## ACR38 Application Note Pseudo-APDU Reference

### Memory Card Type Selection
```
FF A4 00 00 01 05   # Select SLE4442 (type 5)
```

### SLE44xx Series Commands
| APDU | Description | Notes |
|------|-------------|-------|
| `FF B0 00 AA LL` | Read Main Memory | AA=address, LL=length |
| `FF D0 00 AA LL DD` | Write Main Memory | Requires PSC verified |
| `FF B4 00 00 04` | Read Security Memory | Returns EC+PSC[3] |
| `FF B2 00 00 04` | Read Presentation Error Counter | SLE4428/5528 |
| `FF 20 00 00 02 CC` | Present Code (PSC) | CC=2-byte code, SW2=EC |
| `FF D2 00 00 03 PP QQ RR` | Update Security Memory | Change PSC (after verify) |
| `FF B8 00 00 04` | Read Protection Bits | First 32 bytes' protection state |
| `FF 8E 00 AA 01 DD` | Write Protection | Permanently protect byte at AA |

---

## Key Security Failures in SLE4442 Design

| Defect | Impact |
|--------|--------|
| PSC transmitted in cleartext | Logic analyzer = instant PSC recovery |
| Main memory freely readable | Zero-cost cloning |
| No cryptographic engine | No challenge-response possible |
| No unique chip ID | Cannot bind card identity |
| EC only 3 bits | Too few for any recovery strategy |
| No glitch/fault countermeasures | 1995 design, vulnerable to fault injection |
| No power analysis countermeasures | SPA/DPA trivially applicable |

**Bottom line**: SLE4442 security = PSC secrecy + 3-attempt limit.
Both are broken (cleartext + fault injection).

---

## References

1. Infineon/Siemens SLE4432/SLE4442 Datasheet (07.95)
2. ISSI IS23SC4442 Datasheet — clearer Compare Verification Data description
3. IOActive "Infineon SLE4442" — silicon analysis, fault injection confirmation
4. Strom Carlson DEFCON 14 — FedEx Kinko's ExpressPay hack, logic analyzer capture
5. Bus Pirate SLE4442 Documentation — practical 2-WIRE protocol guide
6. ACR38 CCID Application Note — Pseudo-APDU command reference
7. Hackaday 2008 — Bus Pirate readout tutorial
8. NCC Group "Low Cost Attacks on Smart Cards" — EM side-channel methodology
9. GitHub: luu176/SLE4442-Card-Manager — Python PC/SC tool
10. GitHub: sonovice/sle4442 — AVR emulator (accepts any PSC)
11. Chris Tarnovsky / Flylogic — die photos, silicon analysis
