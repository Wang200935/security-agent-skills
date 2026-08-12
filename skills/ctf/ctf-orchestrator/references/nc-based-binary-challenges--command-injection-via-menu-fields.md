# NC-Based Binary Challenges — Command-Injection via Menu Fields

When an nc challenge presents a menu with text input fields (e.g.,
username, password), **test every input field for command-name injection**.
Discovered in NHNC 2026 "67 login system": typing `flag`, `show`,
`update`, `delete`, or `register` as the login username triggered the
corresponding menu command instead of attempting authentication. This
pattern arises when the binary reuses the same input buffer / parser
for both menu selection and data entry, and the data-entry parser doesn't
strip or escape the menu keywords.

**Quick probe** (Python socket):
```python
for cmd_name in ["flag", "show", "update", "delete", "register", "readflag", "admin"]:
    s = socket.socket(); s.settimeout(3); s.connect((host, port))
    s.recv(4096)  # menu
    s.send(b"3\n")        # login command
    s.recv(4096)          # username prompt
    s.send(f"{cmd_name}\n".encode())
    resp = s.recv(4096).decode()[:200]
    print(f"{cmd_name}: {resp}")
    s.close()
```

**Signals**: if any response deviates from the expected "invalid" or
standard prompt, that input name is a command-injection target. Follow up
by testing ALL menu keywords in ALL input fields.
