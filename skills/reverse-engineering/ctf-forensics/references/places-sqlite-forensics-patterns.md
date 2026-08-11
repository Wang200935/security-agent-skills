# places.sqlite Forensics Flag-Hunting Patterns

## Quick Wins (try these first — they solve 80% of CTF challenges)

### 1. Raw string grep
The flag is often embedded directly in URL strings within the database:
```bash
strings places.sqlite | grep -i 'FLAGFORMAT{' 
# e.g.: strings places.sqlite | grep 'MetaCTF{'
# Found: https://docs.google.com/document/d/MetaCTF{sqlite_1snt_4_f1gh7}
```

### 2. SQL queries on moz_places
```sql
SELECT url, title FROM moz_places WHERE url LIKE '%flag%' OR title LIKE '%flag%';
SELECT url, title FROM moz_places WHERE description LIKE '%flag%';
```

### 3. Raw byte scan in SQLite file
The flag may exist OUTSIDE the SQLite structure (in slack space, page gaps, or appended data):
```bash
grep -a 'FLAG{' places.sqlite
xxd places.sqlite | grep -i 'flag'
```

## Deeper Analysis (when quick wins fail)

### 4. Non-standard Firefox values
- **visit_type = 9**: Not a standard Firefox visit type. Custom-inserted by challenge author. Examine these rows carefully.
- **Fake timestamps**: Year 1657, 1999, etc. are clearly fabricated. Check if the timestamp differences encode ASCII.
- **frecency values**: Normally auto-computed by Firefox. Custom values may encode data.

### 5. Hidden tables and columns
```sql
-- Check extra tables for sync_json hidden data
SELECT * FROM moz_places_extra;
SELECT * FROM moz_historyvisits_extra;
SELECT * FROM moz_annos;
SELECT * FROM moz_items_annos;
SELECT * FROM moz_keywords;
```

### 6. File structure analysis
- Check file size: abnormally large files (e.g., 5MB for what should be a small DB) may hide data in null pages
- Check page count and page sizes
- Scan for data after the last valid SQLite page

### 7. The "play it" pattern (NHNC 2026 Kira-Notes)
Some challenges embed clues in external resources linked from the browser history:
- Proton Drive shared links with password
- Retro-themed archive servers
- Challenge author's GitHub repos
- YouTube video IDs/titles
- DuckDuckGo search queries

For Kira-Notes specifically: the Proton Drive file `noth*****.png` (password `do4wWWpAQ0Lw`) was a 1233x925 PNG whose filename was `nothing.png` (5 obscured characters). The Retro Archive server at 151.158.224.74:31337 served a static Astro site with fake download links. Neither yielded the flag — the solution remains undiscovered.

## SQLite Forensics Methodology (when quick wins fail)

When the flag isn't in plaintext strings or SQL queries, apply the full SQLite forensics workflow. These techniques recover deleted data, free space, and database-internal structures:

### 8. Freelist Pages
SQLite tracks freed pages in a linked list. Pages freed by DELETE/VACUUM operations may still contain old data:
```sql
PRAGMA freelist_count;  -- number of free pages
PRAGMA page_count;      -- total pages
```
Parse the freelist trunk page (found at offset 32 in the file header) to enumerate freed pages, then read their raw content. **Pitfall**: VACUUM or auto-vacuum may zero out freed pages.

### 9. Freeblock Chain (within active pages)
Deleted cells within active pages become "freeblocks" — linked lists of freed space that may retain old record data:
- Page header offset 1-2: pointer to first freeblock
- Freeblock header: [2 bytes next_offset] [2 bytes size]
- Follow the chain and extract ASCII from each freeblock body
```python
fb_off = struct.unpack('>H', page[1:3])[0]
while fb_off > 0:
    fb_size = struct.unpack('>H', page[fb_off:fb_off+2])[0]
    next_fb = struct.unpack('>H', page[fb_off+2:fb_off+4])[0]
    fb_data = page[fb_off+4:fb_off+fb_size]
    # extract strings from fb_data
    fb_off = next_fb
```
**Pitfall**: Freeblocks may contain LZ4-compressed data or Firefox internal binary formats rather than plaintext.

### 10. Unallocated Space (cell content gap)
The area between the last freeblock and cell content start may contain old records with no pointers:
- `content_start` at page header offset 5-6
- Scan bytes between the end of the freeblock chain and `content_start`
- These bytes are invisible to SQLite queries but may contain intact deleted records

### 11. WAL (Write-Ahead Log)
Uncommitted data lives in the `-wal` file:
```bash
strings places.sqlite-wal | grep -i 'flag'
xxd places.sqlite-wal | head
```
Check if WAL is non-empty. WAL pages may contain data that hasn't been checkpointed.

### 12. SHM (Shared Memory)
The `-shm` file is the WAL-index. Mostly metadata but check for unexpected data.

### 13. PRAGMA Analysis
Non-standard PRAGMA values are a common hiding place:
```sql
PRAGMA user_version;     -- Firefox normally sets specific values
PRAGMA schema_version;   -- check for unusual numbers
PRAGMA application_id;   -- should be set by Firefox
```
Challenge authors may set these to encode flag fragments.

### 14. Rowid Gap Analysis
Compare `MAX(id) - MIN(id) + 1` against `COUNT(*)`. Gaps indicate deleted rows:
```sql
SELECT MAX(id), MIN(id), COUNT(*) FROM moz_places;
-- gap = (max - min + 1) - count = number of deleted rows
```
The deleted rowids may indicate where flag data was stored before deletion.

### 15. Page-Level Raw Scan
After all structured techniques fail, scan every page's raw bytes for the flag pattern:
```python
for page_num in range(1, total_pages + 1):
    page = data[offset:offset + page_size]
    if b'FLAG{' in page or b'NHNC{' in page:
        # found
```

## Anti-AI Challenge Design
Some challenges explicitly design against AI solvers. The description "Please don't use AI to solve this question" was a meta-hint that the solution path was intentionally non-obvious to LLMs. In these cases, systematic human-style forensics workflows are more effective than mass flag-guessing.

**Pitfall**: Blindly generating 50+ flag candidates and submitting them is NOT a valid methodology. If a challenge is unsolved after applying all systematic forensic techniques, accept the limitation and move on. The challenge may require contextual knowledge (CTF Discord hints, during-CTF interactive elements, author-provided clues) that is not available post-CTF.
