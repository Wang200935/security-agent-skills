# Oscilloscope BMP Sequence Analysis — Pattern Reference

## Pattern Description
A sequence of numbered 8-bit grayscale BMP files (e.g., `cap_000.bmp` through `cap_NNN.bmp`) with identical dimensions, representing consecutive frames of an oscilloscope/oscillogram capture. Each frame shows:
- Left and right vertical ruler strips (tick marks)
- Central sparse waveform trace (oscilloscope trace)
- 8-bit grayscale palette (linear 0-255)

## Characteristics
- **Resolution**: Typically 541×541 or similar square
- **Color depth**: 8-bit (256 grayscale levels)
- **Palette**: Linear grayscale (0=black, 255=white) — not indexed with hidden data
- **Frame count**: Often 150-200 frames
- **Trace**: Sparse dark pixels on white background forming a continuous waveform

## Analysis Workflow

### 1. Verify Uniformity
```python
# All frames should have identical structure
for f in frames:
    assert f.width == W and f.height == H
    assert f.mode == 'L'  # 8-bit grayscale
```

### 2. Trace Extraction (Per Frame)
```python
def extract_trace(frame, left_margin=50, right_margin=500, threshold=100):
    """Extract trace Y-position per X column."""
    trace = []
    for x in range(left_margin, right_margin):
        col = frame[:, x]
        dark = np.where(col < threshold)[0]
        if len(dark) > 0:
            y = frame.height - 1 - dark[0]  # convert to image coordinates
            trace.append((x, y))
    return trace
```

### 3. Overlay Analysis (All Frames Combined)
```python
# Sum all frames to find persistent elements
overlay = np.sum([frame < threshold for frame in frames], axis=0)
# High values = ruler ticks, grid lines, static text
# Low values = moving trace
```

### 4. Trace Dynamics Analysis
The moving trace across frames often encodes the hidden message:

| Method | What it captures | Typical result |
|--------|------------------|----------------|
| Centroid (mean X/Y of trace) | Overall trace position | Often noisy, 20-30 distinct values |
| Y at fixed X (e.g., center) | Single-point position | 20-30 distinct Y levels |
| Leftmost/rightmost trace X | Trace horizontal extent | Often static |
| Trace Y quantized to 5 levels | Oscilloscope grid levels | 5-6 distinct bands |

### 5. Signal Reconstruction
- **151 frames** ≈ 21 characters × 7 bits/char (for `echo XXXX XXXXX XXXXX axis` format)
- Quantize Y into 5-6 levels → 3 bits per frame → 453 bits ≈ 56 chars
- Quantize Y into 2 levels (high/low) → 1 bit per frame → 151 bits ≈ 19 chars

## Common Pitfalls (Learned the Hard Way)

1. **Don't assume overlay reveals text directly** — the static overlay shows rulers/grid; the MOVING trace is the signal.

2. **Don't use LSB steganography** — palette is linear grayscale (0=black, 255=white), no room for LSB hiding.

3. **Don't expect literal text in pixel values** — the waveform POSITION encodes data, not pixel values themselves.

4. **Don't burn 20+ tool calls on pixel statistics** before checking the companion tool. The trace IS varying, but with 100s of unknowns (which column? which threshold? which property?), you cannot decode without the tool's reverse mapping.

5. **Overlay max count > 100 means trace overlaps** — use median Y per column instead of raw sum.

## Decoding Strategy (When Tool Unavailable)

1. Extract trace Y at fixed X (e.g., column 270) for all 151 frames
2. Normalize Y values to 0-5 range (6 quantization levels)
3. Try encodings:
   - Base-6: 151 frames × 2.58 bits = 390 bits
   - Base-5: 151 × 2.32 bits = 350 bits
   - Binary threshold (high/low): 151 bits
4. Check for ASCII, base64, ROT, XOR patterns

## Key Patterns Observed
- **5-level quantization** in trace Y (matches oscilloscope grid)
- **151 frames** ≈ 21 chars × 7 bits/char for `echo XXXX XXXXX XXXXX axis`
- Left/right rulers are STATIC (good for alignment)
- Center trace movement encodes data
- Right edge "text" = ruler tick marks, not flag

## Related Files
- `references/scope-trace-bmp-stego.md` — full challenge workflow
- `references/hackerverse-june2026-easy-peasy-lemon-squeezy.md` — specific challenge
- `scripts/artifact_triage.py` — quick triage script

---
*Pattern observed in: Hackerverse June 2026 "Easy Peasy Lemon Squeezy", similar oscilloscope CTF challenges*