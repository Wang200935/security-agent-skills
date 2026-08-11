# nc Command Injection Pattern (CTF Misc)

## Pattern

When an nc-based CTF challenge presents a menu-driven interface (register, login, show, update, delete, etc.), the "login" or username field may be vulnerable to **command injection** — entering a menu command name as a username triggers that action instead of a normal login.

## Example (67 login system, NHNC 2026)

```
1. register
2. show
3. login
4. update
5. delete
6. exit
> 3          (choose login)
slot:        (prompt for username/slot)
```

### Behavior
- Entering a slot **number** → normal login ("welcome!" or "invalid")
- Entering `flag`, `show`, `update`, `delete`, `exit`, `register` → triggers the **corresponding menu command** directly
- Empty input or garbage input → returns empty response

### Exploitation

1. **Register first** to establish a session
2. **Login with slot number** to authenticate
3. **Try command names as usernames** to discover which ones trigger unintended actions
4. The "show" command triggered by entering `flag` as username may reveal hidden data

## Detection Checklist

- Does the server echo a prompt like "slot:" or "username:" after choosing login?
- Does entering known command names produce different behavior than random strings?
- Does the response length change for special inputs?
- Try: `flag`, `show`, `admin`, `readflag`, `/readflag`, `cat flag*`, shell metacharacters (`;`, `|`, `$(,)`, backticks)

## Tools

Use raw Python sockets for testing — pwntools often fails to install on macOS due to unicorn cmake dependency:

```python
import socket, time
s = socket.socket(); s.settimeout(5)
s.connect(("host", port))
time.sleep(0.2); s.recv(4096)  # menu
s.send(b"3\n")                  # login command
time.sleep(0.15); s.recv(4096)  # prompt
s.send(b"flag\n")               # try command name
time.sleep(0.3)
resp = s.recv(4096).decode()
print(resp)
```

## Pitfalls
- Connection drops after ~5-10 operations — keep sessions short
- Server state resets between TCP connections
- macOS `nc` may not work well for interactive protocols; use Python sockets
- pwntools `unicorn` dependency fails on macOS ARM64 (cmake not found); fall back to raw sockets
