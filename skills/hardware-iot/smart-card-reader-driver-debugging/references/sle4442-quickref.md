# SLE4442 Quick Reference Card — Campus AC Card Operations

## 🚨 SAFETY FIRST (READ BEFORE ANY OPERATION)

| Rule | Why |
|------|-----|
| **Always read Security Memory first** | Check EC — if 0xF3 or lower, STOP (locked) |
| **Never blind guess PSC** | 3 strikes = permanent lock |
| **Correct PSC resets EC** | Successful Verify = EC → 0xFF (no attempt consumed) |
| **Stop at EC = 1 remaining** | Preserve last attempt for real PSC |

---

## 🔍 Phase 1: Recon (Zero Risk)

```python
# 1. Read Security Memory (EC + PSC[3])
cmd = bytes([0xFF, 0xB4, 0x00, 0x00, 0x04])

# 2. Read all Main Memory (256 bytes, free read)
cmd = bytes([0xFF, 0xB0, 0x00, 0x00, 0xFF])

# 3. Read Protection Memory (32 bits)
cmd = bytes([0xFF, 0xB8, 0x00, 0x00, 0x04])
```

---

## 📊 EC Decision Matrix

| EC Hex | Binary | Attempts Left | Action |
|--------|--------|---------------|--------|
| `FF` | 111 | 3 | **Safe** — try defaults |
| `FB` | 110 | 2 | **Cautious** — try FF FF FF only |
| `F7` | 101 | 1 | **STOP** — no more guessing |
| `F3` or lower | 011+ | 0 | **LOCKED** — clone only |

---

## 🎯 Phase 2: PSC Recovery (If EC ≥ 2)

### Default PSC Priority Order

| PSC | Source | Try? |
|-----|--------|------|
| `FF FF FF` | Factory blank cards | ✅ Always first (60-70%) |
| `B2 B2 B2` | Chinese suppliers | ⚠️ If FF fails, EC=2 left |
| `55 55 55` | Indian/ME vendors | ⚠️ If B2 fails, EC=1 — STOP |
| `00 00 00` | Lazy vendors | ❌ Never (wastes attempts) |

### Verify Command (ACR38/ACR39 / CT-API)
```python
# 3-byte PSC (CT-API / Bus Pirate)
verify = bytes([0xFF, 0x20, 0x00, 0x00, 0x03, p1, p2, p3])

# ACR38 Pseudo-APDU (2-byte CODE, reader handles EC)
verify = bytes([0xFF, 0x20, 0x00, 0x00, 0x02, p1, p2])
# SW1=90, SW2=EC_value
```

### Verify Success Check
- Response SW1=90 / CT-API rc=0 → **SUCCESS**
- EC resets to 0xFF automatically
- Now you have full write access until power-off

---

## 📋 Phase 3: If PSC Recovered

```python
# Write any data to Main Memory
write = bytes([0xFF, 0xD0, 0x00, offset, 0x01, value])

# Change PSC (optional, after verify)
change_psc = bytes([0xFF, 0xD2, 0x00, 0x00, 0x03, np1, np2, np3])

# Permanently protect first 32 bytes (OTP — IRREVERSIBLE)
protect = bytes([0xFF, 0x8E, 0x00, byte_addr, 0x01, 0x00])
```

---

## 🔄 Phase 4: If PSC Unknown (Clone Path)

**Read → Write to blank card. No PSC needed.**

```python
# 1. Dump target card (already done in Phase 1)
dump = read_all_256_bytes()

# 2. Buy blank SLE4442/SLE5542 (PSC = FF FF FF guaranteed)

# 3. Write dump to blank card
for i in range(256):
    write_byte(i, dump[i])
    
# 4. Done — perfect functional clone
```

---

## 🛠️ Required Hardware

| Item | Model | Price | Notes |
|------|-------|-------|-------|
| **Reader** | **ACS ACR38U** | NT$300-800 | WHQL driver, 100% SLE4442 support |
| **Reader** | ACS ACR39U | NT$400-1000 | Upgraded ACR38U |
| **Reader** | Alcor AU9540 (VID 058F) | NT$150-350 | Same chip as Pincop, original VID |
| **Blank Cards** | SLE4442 / SLE5542 | NT$5-10/張 | 10張一包 |

### ❌ Don't Buy
- Kinyo KCR-6250 (only SD/SIM, no SLE4442)
- GF607 (Win98 era, no driver)
- Any reader only mentioning "CPU卡" / "ISO 7816"

### 🔍 Shopee Search Keywords
```
ACR38U
SLE4442 讀卡機
冷氣卡 讀卡機
AU9540 讀卡機
IC卡讀卡器 4442
```

---

## 🎮 Bus Pirate Quick Commands

```bash
# Setup
m 2wire
20          # 20kHz
W 5         # 5V
P           # Pull-up enable (x2!)
L           # LSB first

# ATR (should get A2 13 10 91)
} { ^ } r:4

# Read Security Memory
{ 0x31 0x01 r:4 }

# Verify PSC (FF FF FF)
{ 0x33 0xFF 0xFF 0xFF }

# Read Main Memory at N, length L
{ 0x30 N r:L }
```

---

## ⚡ Advanced: If Card Locked (EC = 0)

| Method | Difficulty | Cost | Success |
|--------|------------|------|---------|
| **Clone to blank card** | Easy | $5 | 100% (if read works) |
| **Voltage glitching** | Medium | $300 (ChipWhisperer) | High (bypass EC) |
| **Clock glitching** | Medium | $300 | High |
| **Decap + microprobe** | Hard | $50K+ | Near 100% |

**For campus cards**: Clone path is usually sufficient — you just want the same value on another card.

---

## 📞 Emergency Contacts

- **Skill reference**: `smart-card-reader-driver-debugging` → `references/sle4442-security-attacks.md`
- **Test script**: `scripts/test_ctapi_sle4442.py` (needs 32-bit Python)
- **Force bind script**: `scripts/force_bind_szccid.ps1` (if reader binds to MS CCID)

---

## 💡 Pro Tips

1. **Photo the card** before any operation (UID, printed number)
2. **Log every command** and response with timestamp
3. **Test on a blank card first** — verify your reader/commands work
4. **Work in a clean environment** — static kills cards
5. **Never rush** — one wrong write = bricked card