# Chess Board PNG → FEN OCR

CTF challenges frequently ship a series of chess-board screenshots (e.g. `board_01.png` … `board_28.png`) and hide the flag in some aggregate property of the positions (check / checkmate state, side to move, piece counts, etc.). This file documents a pixel-analysis pipeline that recovers a valid FEN per board so you can reason about game state with `python-chess`.

## Detection Signal

- Multiple PNGs named `board_NN.png` (28 boards = 28 ASCII chars is common)
- All same resolution (e.g. `360×360`, `8×8` grid of 45×45 squares)
- Two background colors only — light squares `(255, 206, 158)`, dark squares `(209, 139, 71)`
- Pieces drawn as outlined glyphs — black pieces = `(0, 0, 0)` silhouette; white pieces = `(255, 255, 255)` fill on dark outline

## Step 1 — Extract Piece Silhouette per Square

For each 45×45 square, classify pixels as "piece" or "background" using the **minimum distance to either background color**:

```python
import numpy as np

def silhouette(arr, y, x, sq=45):
    sq_img = arr[y*sq:(y+1)*sq, x*sq:(x+1)*sq]
    bg_light = np.array([255, 206, 158])
    bg_dark  = np.array([209, 139, 71])
    d1 = np.linalg.norm(sq_img.astype(float) - bg_light, axis=2)
    d2 = np.linalg.norm(sq_img.astype(float) - bg_dark,  axis=2)
    return np.minimum(d1, d2) > 30   # threshold tuned per dataset
```

If `silhouette.sum() < 30` the square is empty.

## Step 2 — Determine Color

Count pure-bright pixels (`>220` in all channels) inside the silhouette. If they exceed ~25% of the silhouette area, the piece is white; otherwise black. (White pieces show their bright interior; black pieces are pure dark fill.)

## Step 3 — Classify by Silhouette Area

For chess.com / lichess style renderings, each piece type occupies a consistent silhouette area. The bins below were validated against `python-chess`'s `is_valid()`:

| Area (pixels) | Piece | Notes |
|---|---|---|
| 540 – 554 | Pawn | smallest, no top decoration |
| 555 – 600 | **Rook** | wide symmetrical silhouette, small knob on top |
| 700 – 749 | **Queen** | 3 distinct prongs at top |
| 750 – 810 | **King**   | taller silhouette with cross / single spike + 2 flanking bumps |
| 820 – 849 | Knight | asymmetric — unique silhouette, easy to ID |
| 850 – 890 | **Bishop** | 5-prong elaborate crown, tallest |

### CRITICAL pitfall — King vs Queen vs Bishop identification

Looking at thumbnail silhouettes, the **3-prong crown at top is QUEEN, not King**. The King silhouette is taller with a single spike + two flanking ears (cross design). Bishops show the most elaborate 5-point crown and the largest area. From the silhouette alone this is **not obvious** — always validate.

## Step 4 — Brute-Force K / Q / B Labels via python-chess

Pawn, Rook, Knight are unambiguous by area. The remaining three bins (700-749, 750-810, 850-890) need to be assigned to {K, Q, B} in some order. **Exhaustively try all six permutations** and keep the assignment that makes the FEN valid:

```python
import chess, itertools

def build_fen(arr, mapping):
    """mapping: {(low, high): piece_letter}; other bins fixed."""
    rows = [[] for _ in range(8)]
    for y in range(8):
        for x in range(8):
            sil = silhouette(arr, y, x)
            if sil.sum() < 30:
                continue
            area = sil.sum()
            is_white = (arr[y*45:(y+1)*45, x*45:(x+1)*45][sil] > 220).all(axis=1).sum() > 200
            if   area < 555: piece = 'P'
            elif area < 600: piece = 'R'
            elif 820 <= area < 850: piece = 'N'
            else:
                piece = None
                for (lo, hi), p in mapping.items():
                    if lo <= area < hi:
                        piece = p; break
                if piece is None:
                    continue
            rows[y].append((x, piece if is_white else piece.lower()))

    out = []
    for r in range(8):
        last_x, s = -1, ''
        for x, p in sorted(rows[r]):
            gap = x - last_x - 1
            if gap > 0: s += str(gap)
            s += p
            last_x = x
        if last_x < 7: s += str(7 - last_x)
        out.append(s)
    return "/".join(out) + " w - - 0 1"

bins = [(700, 750), (750, 810), (850, 1000)]
for perm in itertools.permutations(['Q', 'K', 'B']):
    mapping = dict(zip(bins, perm))
    fen = build_fen(arr, mapping)
    try:
        b = chess.Board(fen)
        if b.is_valid():
            # try black-to-move as fallback
            fen_b = fen[:-11] + ' b - - 0 1'
            if chess.Board(fen_b).is_valid():
                pass  # both moves accept the same labels — labels correct
            print("MATCH", perm, fen)
    except Exception:
        pass
```

A FEN is invalid if there are multiple kings per side, pawns on rank 1 or 8, or kings too close.

## Step 5 — Extract the Hidden Signal

Once every board has a valid FEN, the flag is usually hidden in a single per-board property. Encode each board as 0/1 (or one of several symbols), then concatenate:

```python
states = []
for bn in range(1, 29):
    b = chess.Board(fens[bn])
    states.append(1 if b.is_check() else 0)  # or is_checkmate(), stalemate, etc.

bits = ''.join(str(s) for s in states)
flag = ''.join(chr(int(bits[i:i+7], 2)) for i in range(0, len(bits), 7))
```

Other useful properties: `is_checkmate()`, `is_stalemate()`, `is_valid()`, `len(list(legal_moves))`, whose turn it is, piece-type counts.

## Common Errors

- **Color / row flip**: in the image, `row 0` is BLACK's home rank (top), `row 7` is WHITE's home rank (bottom). FEN rank 8 corresponds to image row 0. Don't flip when emitting the FEN.
- **Missing trailing empty squares in FEN**: a FEN row must sum to 8 columns. Always append `str(7 - last_x)` after the last piece.
- **Pawn on home rank**: any "pawn" silhouette on row 0 or row 7 means your classifier is wrong — it is not actually a pawn.
- **Skipping unknown labels**: if `mapping` misses an area bin, the piece silently disappears. Always check that the per-board piece count matches your expected total.
- **Vision tools failing on CTF imagery**: auth-protected vision APIs (FAL, vision_analyze with provider keys) may 401 in your environment. Falling back to pixel analysis via PIL/numpy is faster and works offline.

## Install

```bash
pip install pillow numpy python-chess
```
