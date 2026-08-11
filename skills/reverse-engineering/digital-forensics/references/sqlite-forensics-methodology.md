# SQLite Forensics Methodology for CTF

Comprehensive checklist for analyzing SQLite databases in CTF forensics challenges. Based on NHNC 2026 "Kira-Notes" (places.sqlite) session learnings.

## Systematic Analysis Order

### 1. Quick Triage
```bash
file database.db                    # confirm it's SQLite
strings database.db | grep -iE 'flag|ctf|NHNC|FLAG'  # flag in plaintext?
xxd database.db | head -20          # check header
sqlite3 database.db ".tables"       # list all tables
```

### 2. Full Schema + Row Count
```sql
SELECT type, name, sql FROM sqlite_master ORDER BY type, name;
SELECT name FROM sqlite_master WHERE type='table';
-- For each table: SELECT COUNT(*) FROM <table>;
```

### 3. PRAGMA Analysis (Encoded Values)
```sql
PRAGMA integrity_check;     -- database health
PRAGMA page_count;          -- total pages
PRAGMA freelist_count;      -- freed pages (deleted data may be here)
PRAGMA page_size;           -- page size (usually 4096 or 32768)
PRAGMA user_version;        -- can hold encoded data
PRAGMA schema_version;      -- can hold encoded data
PRAGMA application_id;      -- can hold encoded data
```

### 4. Deleted Record Recovery
- **Freelist pages**: Check PRAGMA freelist_count. If > 0, dump freed pages
  ```python
  # Read freelist trunk page from header offset 32
  freelist_trunk = struct.unpack('>I', data[32:36])[0]
  # Walk the freelist linked list, dump leaf pages
  ```
- **Freeblock chain**: Within active pages, check freeblock linked list
  - Page header offset 1: first freeblock offset (2 bytes)
  - Freeblock header: [next_offset:2][size:2]
- **Unallocated space**: Between cell content area start and end of page
- **WAL file**: Check for `database.db-wal` (Write-Ahead Log)
- **SHM file**: Check for `database.db-shm` (Shared Memory index)
- **Journal file**: Check for `database.db-journal` (Rollback Journal)

### 5. Rowid Gap Analysis
```sql
SELECT name FROM sqlite_sequence;  -- track max rowids
-- Compare MAX(id) vs COUNT(*) per table to find deleted rows
```

### 6. Column-by-Column Deep Scan
For EVERY table, check EVERY column for:
- Encoded strings (base64, hex, leetspeak)
- Unusual values (non-zero in typically-zero columns)
- Non-standard visit_type values (Firefox uses 1-8; type 9+ is custom)
- Frecency values (can be manipulated to encode data)
- GUID values (12-char base64url, decode for hidden bytes)
- Timestamps in unusual epochs (e.g., year 1657 = fake)

### 7. Raw Hex Analysis
```python
# Search for flag pattern in raw bytes
import re
for m in re.finditer(rb'NHNC\{[^}]+\}', data):
    print(f"Found at offset {m.start()}: {m.group()}")

# Check for data AFTER SQLite EOF (pages * page_size)
expected_size = total_pages * page_size
if len(data) > expected_size:
    print(f"Hidden data after EOF: {len(data) - expected_size} bytes")
```

### 8. Firefox places.sqlite Specifics
- `moz_places`: URLs, titles, visit_count, frecency, GUIDs
- `moz_historyvisits`: visit_date (PRTime = µs since 1601-01-01), visit_type
- `moz_bookmarks`: bookmark hierarchy (parent column)
- `moz_meta`: key-value metadata (check for base64 encoded JSON)
- `moz_places_metadata`: typing_time, key_presses, scrolling data
- `moz_annos` / `moz_items_annos`: annotations (hidden text)
- `moz_origins`: frecency values (check for encoded patterns)

### 9. Custom Visit Types
Non-standard `visit_type` values (e.g., type=9) indicate CUSTOM INSERTIONS by the challenge author. These are first-class clues. Extract the URLs, titles, and timestamps of all custom-type visits.

### 10. Common Flag Locations (by difficulty)
| Difficulty | Location | Example |
|-----------|----------|---------|
| Easy | Plaintext in URL/title | `strings db | grep FLAG{` |
| Medium | Encoded in PRAGMA values | `PRAGMA user_version` |
| Medium | Deleted row in freelist | Walk freeblock chain |
| Medium | Custom visit_type entries | Check type != 1-8 |
| Hard | Encoded in timestamp diffs | Difference between visit_dates |
| Hard | Browser fingerprinting | Correlation of multiple columns |
| Anti-AI | Requires external context | Proton Drive download, live server |

## Pitfalls
- **97% null bytes** in a 5MB database: Not corruption — the DB was padded. Check 1% non-null area only.
- **Fake timestamps**: Year 1657 = clearly fabricated. Look for patterns in the fake values.
- **All freelist pages zeroed**: Challenge author may have VACUUMed. Check freeblocks within active pages instead.
- **Base64 in moz_meta**: Firefox stores bookmark folder GUIDs encoded. Decode and check.
- **`strings | grep FLAG` returns empty**: Flag may be encoded, not plaintext.
