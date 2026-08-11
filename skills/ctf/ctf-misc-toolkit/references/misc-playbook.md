# Misc CTF Playbook

## Category Split

- If there is a service prompt, script interaction after manual exploration.
- If there is source for a jail/sandbox, enumerate allowed syntax and objects.
- If there is text, try encodings, alphabets, transposition, compression, and structured formats.
- If there is an image-like puzzle, switch to forensics/stego if hidden data appears.
- If there is a math/programming constraint, write a solver rather than brute-forcing blindly.

## Common Families

### Encoding and Puzzle

- Base encodings, hex, URL, HTML entities, binary/octal/decimal ASCII.
- Morse, Bacon, braille, semaphore, tap code, rail fence.
- Esolangs: Brainfuck, Piet, Whitespace, Ook.
- QR/barcode variants and damaged symbols.

### Jails and Sandboxes

- Python/JS/shell restricted eval.
- Character blacklist bypass, object graph traversal, format string attribute access.
- Unicode confusables and normalization.
- Environment/function leakage.

### Protocol/Game

- TCP line protocol state machine.
- Maze/pathfinding, chess, word games, proof-of-work.
- Automate with `pwntools` or sockets.

### OSINT

- Reverse image search manually when allowed.
- EXIF/geolocation clues.
- Username reuse, archived pages, DNS/history.
- Timezone/weather shadows only if challenge intended.

## Solver Habit

Represent the puzzle as data. Build validators and generate candidates; keep assumptions explicit.
