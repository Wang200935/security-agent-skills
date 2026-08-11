# Pyjail and Sandbox Playbook

Use only in CTF/lab environments.

## Inventory

- Python version.
- Input filter: blocked chars, words, length, encoding.
- Execution primitive: `eval`, `exec`, `input`, template, AST evaluator.
- Available builtins/globals/locals.
- Output channel and exception leakage.

## Escape Themes

- Recover builtins through object graph traversal.
- Use dunder attribute construction when underscores are blocked.
- Abuse format strings, decorators, comprehensions, exceptions.
- Import alternatives through existing modules/classes.
- Encoding tricks: Unicode normalization, escapes, bytes construction.
- Shell jails: globbing, variable expansion, IFS, command substitution, builtins.

## Workflow

1. Recreate the jail locally from source or observed behavior.
2. Write a payload tester that records accepted/rejected syntax.
3. Build payload in layers: syntax allowed → object access → file/read/command primitive → flag.
4. Minimize payload for remote reliability.

## Notes

Do not memorize one payload. Most jails are filter-specific; solve by inventorying constraints and available object paths.
