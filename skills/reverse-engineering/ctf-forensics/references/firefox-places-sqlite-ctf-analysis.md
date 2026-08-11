# Firefox places.sqlite CTF Analysis

## Quick Triage

When a CTF challenge provides a `places.sqlite` file, it's Firefox browser history. The database contains browsing history, bookmarks, annotations, and metadata.

```bash
file places.sqlite
# SQLite 3.x database
sqlite3 places.sqlite ".tables"
```

## Key Tables

| Table | Content | CTF Relevance |
|-------|---------|---------------|
| `moz_places` | URLs, titles, visit counts | Primary data source |
| `moz_historyvisits` | Timestamps, visit types | Encoded data (timestamps, types) |
| `moz_meta` | Browser metadata | Hidden base64/JSON data |
| `moz_annos` | Page annotations | Hidden content |
| `moz_bookmarks` | Bookmarks | Clues to target sites |
| `moz_inputhistory` | Form input history | User-typed values |
| `moz_origins` | Domain origins | frecency data |

## Common CTF Encoding Patterns

### 1. Fake/Manipulated Timestamps
Firefox stores timestamps as PRTime (microseconds since 1601-01-01). Challenge authors often manipulate these:
- All timestamps set to same fake year (e.g., 1657)
- Low bytes of timestamps encode flag characters
- Visit order encodes a sequence

```python
from datetime import datetime, timedelta
for row in conn.execute("SELECT visit_date FROM moz_historyvisits"):
    ts = datetime(1601, 1, 1) + timedelta(microseconds=row[0])
    # Check low byte for ASCII
    low = row[0] & 0xFF
    if 32 <= low < 127:
        chars.append(chr(low))
```

### 2. Non-Standard Visit Types
Firefox defines visit types 1-8. Type 9+ is custom/injected:
- `1` = TRANSITION_LINK
- `2` = TRANSITION_TYPED
- `9` = CUSTOM (CTF-injected, check payload)

```sql
SELECT visit_type, count(*) FROM moz_historyvisits GROUP BY visit_type;
```

### 3. Base64 in moz_meta
The `moz_meta` table stores browser metadata as key-value pairs. Values may contain base64-encoded JSON:

```python
import base64, json
for row in conn.execute("SELECT key, value FROM moz_meta"):
    if 'base64' in row[1]:
        b64 = row[1].split('base64,')[1]
        decoded = base64.b64decode(b64)
        parsed = json.loads(decoded)
```

### 4. URL Hash Encoding
Firefox stores `url_hash` (64-bit integer) for quick lookups. These may encode data:
- Low bytes as ASCII
- XOR with known values
- Differences between consecutive hashes

### 5. GUID Patterns
Firefox generates 12-char base64url GUIDs for each place. Check for:
- Repeating patterns
- Leetspeak/words in GUIDs
- Custom GUIDs vs auto-generated

## NHNC 2026 "Kira-Notes" Pattern

This challenge provided only `places.sqlite` with these characteristics:
- Browser history of a fictional user researching "Kira-Notes" CTF challenge
- Traces lead to: GitHub (UmmItKin/Kira-Notes), Proton Drive (password-protected), Retro Archive server
- `moz_meta` contains base64-encoded bookmark folder GUIDs
- Visit type 9 (custom) on key entries
- Timestamps set to year 1657 (fake)
- The challenge is OSINT/forensics: reconstruct the user's research path to find the flag

### Proton Drive Access Pattern
When browser history shows Proton Drive shared links (`drive.proton.me/urls/XXXXX`), the URL fragment after `#` is the decryption password. Download requires browser with JavaScript (curl/Wget cannot access).

### Retro/Hacker Archive Pattern
CTF authors often deploy retro-themed static sites (no JS) as part of OSINT challenges. Key areas to check:
- Page source for hidden comments
- `/robots.txt` (often returns 200 even when other paths 404)
- `/dl/` directory for downloadable files
- Footer/header for encoded clues
- Email addresses, PGP keys, visitor counters (NHNC used 00001337)

## Analysis Workflow

```python
import sqlite3
conn = sqlite3.connect('places.sqlite')

# 1. Tables and schema
for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(row[0])

# 2. moz_meta (hidden metadata)
for row in conn.execute("SELECT * FROM moz_meta"):
    print(row)

# 3. Visit type anomalies
for row in conn.execute("""
    SELECT visit_type, count(*) 
    FROM moz_historyvisits 
    GROUP BY visit_type 
    ORDER BY visit_type
"""):
    print(f"Type {row[0]}: {row[1]}")

# 4. Timestamp low bytes
from datetime import datetime, timedelta
visits = conn.execute("""
    SELECT visit_date FROM moz_historyvisits ORDER BY visit_date
""").fetchall()
chars = []
for v in visits:
    low = v[0] & 0xFF
    chars.append(chr(low) if 32 <= low < 127 else f'[{low:02x}]')
print(''.join(chars))

# 5. GUID inspection
for row in conn.execute("SELECT guid, url FROM moz_places WHERE guid GLOB '*[0-9]*'"):
    print(f"{row[0]} -> {row[1][:60]}")

conn.close()
```

## Pitfalls

- Timestamps are in MICROSECONDS, not milliseconds or seconds
- Firefox stores timestamps relative to 1601-01-01 (Windows epoch), not Unix epoch
- `url_hash` is not a cryptographic hash — it's a fast lookup hash
- `moz_annos` and `moz_items_annos` may be empty in clean exports
- Some tables use `WITHOUT ROWID` (e.g., `moz_meta`) — use `SELECT *` not `SELECT rowid`
