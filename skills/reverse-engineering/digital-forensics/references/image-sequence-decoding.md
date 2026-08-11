# Image Sequence Decoding — Fallback When Tool Unavailable

## When to Use
When you have a sequence of numbered image frames (BMP, PNG, TIFF) from an oscilloscope/scan capture, and the companion binary tool cannot be executed (wrong architecture, missing deps, no Linux environment). The frames themselves may encode the flag through trace position dynamics.

## Core Principle
**Each frame = one time sample. The trace position (X/Y) in each frame encodes one symbol.**

## Extraction Pipeline

### 1. Frame Structure Verification
```python
# Verify all frames share identical structure
for idx in range(N):
    with open(f'cap_{idx:03d}.bmp', 'rb') as f:
        header = f.read(54)
        # Check magic, width, height, bit depth
```

### 2. Trace Extraction (Per Frame)
```python
def extract_trace(frame, left_margin, right_margin, threshold=100):
    """Return list of (x, y) for the trace in this frame."""
    trace = []
    for x in range(left_margin, right_margin):
        col = frame[:, x]
        dark = np.where(col < threshold)[0]
        if len(dark) > 0:
            y = frame.height - 1 - dark[0]  # image coords
            trace.append((x, y))
    return trace
```

### 3. Signal Sampling Strategies

| Strategy | Description | Use When |
|----------|-------------|----------|
| **Fixed X sampling** | Y-position at specific X columns | Trace is vertical function |
| **Centroid** | Mean (X, Y) of all trace pixels | Trace is compact blob |
| **Leftmost/rightmost X** | Horizontal extent at fixed Y | Trace is horizontal |
| **Peak detection** | Local maxima/minima in trace | Multiple peaks per frame |

### 4. Quantization & Encoding

| Quantization | Bits/frame | 151 frames = | Best for |
|--------------|------------|--------------|----------|
| Binary (high/low) | 1 bit | 151 bits ≈ 19 chars | High/low oscillation |
| 3-level | ~1.58 bits | 239 bits ≈ 30 chars | Low/mid/high |
| 5-level (oscilloscope grid) | ~2.32 bits | 350 bits ≈ 43 chars | Oscilloscope |
| 6-level | ~2.58 bits | 390 bits ≈ 48 chars | Fine grid |
| 8-level | 3 bits | 453 bits ≈ 56 chars | Fine detail |

### 5. Decoding Attempts (In Order)

```python
# 1. Direct ASCII from quantized values
# 2. Base-N decoding (base-5, base-6, base-8)
# 3. Binary → ASCII (7-bit or 8-bit)
# 4. Differential (delta between frames)
# 5. XOR with previous frame
# 6. ROT13 / Caesar on decoded text
# 6. Base64 decode
# 7. XOR with constant
```

### 6. Validation Heuristics
```python
def is_printable_ascii(data):
    return all(32 <= b < 127 for b in data)

def looks_like_flag(text):
    return any(kw in text.lower() for kw in ['flag', 'ctf', 'echo', 'axis', 'easy', 'peasy', 'lemon'])
```

## When to Give Up on Direct Decoding

**Stop if:**
- More than 3 quantization schemes tried with no printable output
- No recognisable words after 5 decoding strategies
- The signal is clearly the raw waveform needing the tool's transform

**Then:** You MUST run the companion tool. No amount of statistical analysis replaces the inverse transform.

## Real-World Example (This Session)

**Challenge**: Hackerverse June 2026 "Easy Peasy Lemon Squeezy"
- 151 × 541×541 8-bit BMP frames
- Trace Y at X=270: 24 distinct values, 5 clusters
- Quantization attempts (binary, base-5, base-6, base-8, frequency-rank) → all garbage
- **Cause**: imgconv `--swirl` applies coordinate transformation (lookup table at 0x4b8b1c)
- **Solution**: Must run `imgconv --swirl` on Linux

## Tooling

```bash
# Quick extract all frames
for i in {000..150}; do
    python3 extract_trace.py cap_${i}.bmp >> traces.txt
done

# Python deps
pip install numpy pillow scipy
```

## Key Lesson
**Direct trace decoding is a fallback, not the primary path.** The primary path is **always** running the provided tool. Only spend ~5 tool calls on image analysis before confirming the tool can/cannot be run. If it can't be run, document why and what environment is needed.

## References
- `references/oscilloscope-bmp-analysis.md` — analysis patterns
- `references/scope-trace-bmp-stego.md` — full workflow
- `references/hackerverse-june2026-easy-peasy-lemon-squeezy.md` — worked example
- `references/encrypted-archive-recovery.md` — get the tool first