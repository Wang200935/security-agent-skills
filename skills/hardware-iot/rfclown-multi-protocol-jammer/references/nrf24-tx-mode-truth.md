# nRF24L01+ TX Mode Truth — Why startConstCarrier Works and startShockBurst Doesn't

## Empirical Discovery (2026-07-26)

Built a diagnostic firmware that initialized Radio A in different TX modes and
passively polled STATUS + OBSERVE_TX + FIFO_STATUS every 200ms for 5 seconds.
**No ISR clearing** — pure observation of what the nRF24 hardware does on its own.

### Test 1: startShockBurst (old code — pure ShockBurst TX)

Config: auto-ack off, retries=0, EN_DYN_ACK, W_TX_PAYLOAD 32×0xAA, CE HIGH.
No CONT_WAVE, no REUSE_TX_PL.

```
T+10ms:   STATUS=0x2e (TX_DS=1)  FIFO=0x11 (TX_EMPTY=1)  OBS=0x00
T+200ms:  STATUS=0x0e (TX_DS=0)  FIFO=0x11 (TX_EMPTY=1)  OBS=0x00
T+400ms:  STATUS=0x0e (TX_DS=0)  FIFO=0x11 (TX_EMPTY=1)  OBS=0x00
...5s:    all identical to T+200ms — RADIO IS IDLE
```

**Conclusion**: ShockBurst TX with auto-ack off + 0 retries fires exactly ONE
packet. TX_DS is set once, FIFO empties, radio returns to Standby-I. No further
transmission occurs. ARC_CNT stays 0 (no retransmits). The radio is silent for
the remaining 4.98 seconds.

### Test 2: startConstCarrier (new code — CONT_WAVE + REUSE_TX_PL)

Config: RF_SETUP=0x9F (CONT_WAVE bit7 + PLL_LOCK bit4 + 2Mbps + PA max),
flush_tx, W_TX_PAYLOAD_NOACK (0xB0) 32×0xFF, CE HIGH, delay 1ms,
REUSE_TX_PL (0xE3): CE LOW → STATUS clear → transfer(0xE3) → CE HIGH.

```
T+200ms:  STATUS=0x0e (TX_DS=0)  FIFO=0x41 (TX_EMPTY=0 TX_FULL=1)  OBS=0x00
T+400ms:  STATUS=0x0e (TX_DS=0)  FIFO=0x41 (TX_EMPTY=0 TX_FULL=1)  OBS=0x00
...5s:   all identical — FIFO STAYS FULL, CARRIER RUNNING
```

**Conclusion**: CONT_WAVE + REUSE_TX_PL keeps the FIFO full and the carrier
continuously transmitting. TX_EMPTY=0 means the payload is always available
for re-transmit. OBSERVE_TX ARC_CNT=0 because REUSE_TX_PL retransmits are
internal hardware re-sends, not auto-ack retransmits (which would increment
ARC_CNT). This is the CORRECT continuous interference pattern.

## Register Values After startConstCarrier

| Register    | Value  | Meaning |
|-------------|--------|---------|
| RF_SETUP    | 0x9F   | CONT_WAVE(7) + PLL_LOCK(4) + RF_DR_HIGH(3) + RF_PWR max(2:1) + LNA(0) |
| CONFIG      | 0x02   | PWR_UP(1) + PRIM_RX=0(TX) + CRC off |
| STATUS      | 0x0E   | TX_FIFO_FULL(0) set, no IRQ flags |
| FIFO_STATUS | 0x41   | TX_FULL=1, TX_EMPTY=0 — FIFO has payload |
| EN_AA       | 0x00   | Auto-ack disabled |
| SETUP_RETR  | 0x00   | No auto-retries |

**Runtime health check**: If RF_SETUP != 0x9F on any radio, call `reloadP()`:
FLUSH_TX → W_TX_PAYLOAD_NOACK 32×0xFF → sendReuseTXPL.

## RF24 Library startConstCarrier() — Reverse-Engineered Steps

Source: `RF24.cpp` (nRF24/RF24 GitHub repo, master branch)

```cpp
void RF24::startConstCarrier(rf24_pa_dbm_e level, uint8_t channel) {
    stopListening();
    // 1. Set CONT_WAVE + PLL_LOCK in RF_SETUP
    write_register(RF_SETUP, read(RF_SETUP) | _BV(CONT_WAVE) | _BV(PLL_LOCK));
    if (isPVariant()) {
        setAutoAck(0);        // EN_AA = 0
        setRetries(0, 0);     // SETUP_RETR = 0
        uint8_t dummy_buf[32];
        for (uint8_t i = 0; i < 32; ++i) dummy_buf[i] = 0xFF;
        // 2. TX_ADDR = 5 bytes 0xFF (bypass address truncation)
        write_register(TX_ADDR, dummy_buf, 5);
        flush_tx();            // 3. Clear TX FIFO
        // 4. W_TX_PAYLOAD 32 bytes 0xFF
        write_register(W_TX_PAYLOAD, dummy_buf, 32);
        disableCRC();
    }
    setPALevel(level);
    setChannel(channel);
    ce(HIGH);                 // 5. Launch const carrier
    if (isPVariant()) {
        delay(1);
        reUseTX();             // 6. CE LOW → clear MAX_RT → REUSE_TX_PL → CE HIGH
    }
}
```

```cpp
void RF24::reUseTX() {
    ce(LOW);
    write_register(STATUS, RF24_TX_DF);  // clear MAX_RT flag
    read_register(REUSE_TX_PL, nullptr, 0);  // send 0xE3 command
    ce(HIGH);
}
```

## Datasheet Warning (And Why RF24 Library Ignores It)

> "Do not use REUSE_TX_PL together with CONT_WAVE=1. When both these registers
> are set the chip does not react when setting CE low."

The RF24 library sets BOTH. This is intentional — the combination produces
continuous carrier modulated with payload data. The tradeoff: CE LOW cannot
stop transmission. To stop, you must `powerDown()` (PWR_UP=0), which forces
the chip to Standby-I regardless of CE state. The library's `stopConstCarrier()`
calls `powerDown()` first, then clears CONT_WAVE + PLL_LOCK bits, then `flush_tx()`.

## Why Pure CW (CONT_WAVE Without Payload) Fails for WiFi

WiFi CCA (Clear Channel Assessment) uses TWO mechanisms:
1. **Energy detect** — carrier above threshold → channel busy
2. **Preamble correlation** — 802.11 preamble pattern detected → channel busy

Pure CW (CONT_WAVE alone, no payload in FIFO) produces an unmodulated carrier.
Some WiFi chips' CCA energy detect triggers on this, but many don't — the
detection threshold depends on modulation characteristics. More importantly,
preamble correlation never fires on pure CW, so WiFi receivers configured for
preamble-detect CCA will NOT defer.

The RF24 `startConstCarrier()` with payload + REUSE_TX_PL produces a carrier
that IS modulated (the 0xFF payload bits are transmitted as GFSK modulation).
This triggers BOTH CCA mechanisms — energy detect sees the carrier, and
preamble correlation sees modulated data that looks like 802.11 traffic.

## SPI Commands Used (All are commands, NOT register writes)

| Command | Code | Function |
|---------|------|----------|
| W_TX_PAYLOAD | 0xA0 | Write TX payload (with auto-ack) |
| W_TX_PAYLOAD_NOACK | 0xB0 | Write TX payload (no auto-ack, requires EN_DYN_ACK) |
| FLUSH_TX | 0xE1 | Clear TX FIFO |
| REUSE_TX_PL | 0xE3 | Re-send last payload (goes in CSN-low transaction, not a register) |

**Common mistake**: Trying to write REUSE_TX_PL as a register:
`writeReg(0x1D, 0x04)` does NOT enable REUSE_TX_PL. 0x1D is the FEATURE
register and 0x04 is EN_DPL (dynamic payload length), not REUSE_TX_PL.
REUSE_TX_PL is a standalone SPI command — pull CSN LOW, transfer(0xE3),
CSN HIGH.
