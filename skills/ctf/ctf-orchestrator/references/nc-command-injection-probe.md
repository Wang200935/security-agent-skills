# NC-Based Command-Injection Probe Pattern

Discovered in NHNC 2026 "67 login system".

## Pattern
When an nc-based challenge presents a text-menu with input fields (username,
password, etc.), the binary may reuse the same input buffer for both menu
selection and data entry. If menu keywords are not stripped from data input,
typing a command name into a data field triggers that command instead.

## Quick Probe Script
```python
import socket, time

HOST = "target.host"
PORT = 12345

for cmd_name in ["flag", "show", "update", "delete", "register", "readflag", "admin"]:
    s = socket.socket()
    s.settimeout(3)
    s.connect((HOST, PORT))
    time.sleep(0.2)
    s.recv(4096)  # menu banner

    # Try the command in every input field
    # Field 1: username (after "3\n" for login)
    s.send(b"3\n")
    time.sleep(0.1)
    s.recv(4096)  # prompt
    s.send(f"{cmd_name}\n".encode())
    time.sleep(0.2)
    resp = s.recv(4096).decode()

    if "invalid" not in resp and cmd_name not in resp:
        print(f"'{cmd_name}' in login username: {resp[:200]}")
    s.close()
```

## Signal
Any response that deviates from the expected "invalid" or standard prompt is a
hit. Follow up by testing ALL menu keywords (register, login, show, update,
delete, flag, readflag, read, execute, help, exit, quit) in ALL input fields.

## Root Cause
The challenge binary uses the same `read()` / `fgets()` buffer for menu
selection and data entry. The parser dispatches on the first token without
segregating the input context (menu vs data field).

## NHNC 2026 "67 login system" — Detailed Flow

### Normal Usage
1. Register → gets slot N (e.g. `registered at slot 0`)
2. **Login with slot NUMBER** (not username) → `welcome!`
3. Show → `slot: ` (asks which slot)
4. Update → `slot: ` → (send slot#) → `new username: ` → (send name)
5. Update returns `username: <name>` with null padding (~59-byte buffer)

### Command Injection Results
- `flag` as login → triggers show (returns empty), then disconnect
- `show` as login → returns `slot: ` (show prompt)
- `update` as login → returns `slot: ` (update prompt)
- `delete` as login → returns `slot: ` (delete prompt)
- `register` as login → disconnects
- `exit` as login → disconnects
- `admin`, `root`, `readflag` as login → all return empty + disconnect

### Binary Structure (from "show" output)
```
username: <name>\n\n<name>\n
followed by null padding (~59 bytes total)
then: 60 e0 12 49 ca 55 00 00  (stack/heap pointer — 0x55ca4912e060)
```
Buffer overflow at >59 bytes may overwrite the pointer.
