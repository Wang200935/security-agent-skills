---
name: digital-forensics
description: 'Comprehensive CTF forensics workflows covering file type identification,
  image/audio steganography, PCAP/memory/disk forensics, archive cracking, document
  analysis, and common flag-hunting patterns. Use when the challenge involves unknown
  files, data recovery, hidden data, or forensic artifacts.

  '
version: 2.1.0
license: MIT
metadata:
  hermes:
    tags:
    - ctf
    - forensics
    - steganography
    - pcap
    - memory
    - disk
    - reversing
    related_skills: []
    origin: import
---

# CTF Forensics Skill

## 1. RECONNAISSANCE: Identify What You Have

### 1.1 File Type Identification
Never trust extensions. Always check the actual type:

```bash
# Primary: look at magic bytes
file suspicious.bin
file -i suspicious.bin          # MIME type
file --keep-going suspicious.bin

# Hex dump first 512 bytes
xxd suspicious.bin | head -32
hexdump -C suspicious.bin | head -32

# Deeper inspection
binwalk -Me suspicious.bin      # extract embedded files recursively
foremost -i suspicious.bin -o output/
strings suspicious.bin | head -100
```

### 1.2 Common Magic Bytes (First 8 bytes, hex)

```
FF D8 FF E0/JFIF  = JPEG image
89 50 4E 47       = PNG image
47 49 46 38       = GIF image (GIF8)
42 4D             = BMP image
49 49 2A 00       = TIFF (little-endian)
4D 4D 00 2A       = TIFF (big-endian)
52 49 46 46       = RIFF (WAV, AVI, WebP sibling)
50 4B 03 04       = ZIP / DOCX / XLSX / JAR / APK
1F 8B 08          = GZIP
FD 37 7A 58 5A    = XZ / LZMA
42 5A 68          = BZ2
37 7A BC AF       = 7-Zip
52 61 72 21       = RAR
25 50 44 46       = PDF
D0 CF 11 E0       = OLE2 / MS Office (DOC, XLS, PPT)
7B 5C 72 74       = RTF
0A 0D 0D 0A       = PCAP
D4 C3 B2 A1       = PCAP (swapped endian)
4D 5A             = PE / EXE / DLL
7F 45 4C 46       = ELF
CA FE BA BE       = Mach-O (universal binary)
CF FA ED FE       = Mach-O 64-bit
49 44 33          = MP3 (ID3 tag)
4F 67 67 53       = OGG / OGA / OGV
1A 45 DF A3       = Matroska (MKV/MKA/WebM)
45 56 46 32       = EWF / Expert Witness (E01)
53 51 4C 69       = SQLite 3
```

### 1.3 Quick Enumeration Script
```bash
# Dump magic + strings + embedded files in one pass
for f in *.bin *.unknown *; do
  echo "=== $f ==="
  file "$f"
  strings "$f" | grep -iE 'flag|ctf|pico|hack|key|secret' || true
  echo "---"
done

# Bulk binwalk extraction
for f in *.bin; do
  binwalk -Me "$f" 2>/dev/null
done
```

---

## 2. IMAGE FORENSICS

### 2.1 General Inspection
## 2. IMAGE FORENSICS

### 2.1 General Inspection
```bash
exiftool image.png                # all metadata
identify -verbose image.png       # ImageMagick deep info
pngcheck -v image.png             # chunk-level PNG validation
mediainfo image.jpg
```

### 2.2 LSB Steganography

**Detection:**
```bash
# zsteg — best all-in-one tool for PNG/BMP
zsteg image.png                   # all methods
zsteg -a image.png                # aggressive, try all
zsteg -E b1,rgb,lsb image.png     # specific: bit 1, RGB, LSB
```

**Extraction:**
```bash
# steghide (password-protected)
steghide extract -sf image.jpg -p password
stegseek image.jpg                # bruteforce steghide passwords
stegseek image.jpg /usr/share/wordlists/rockyou.txt

# Custom Python LSB extraction from specific plane
python3 -c "
from PIL import Image
img = Image.open('image.png')
pixels = list(img.getdata())
bits = ''.join(str(p[i] & 1) for p in pixels for i in range(3))
data = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits)//8*8, 8))
print(data[:200])
"
```

### 2.3 PNG Chunk Analysis

### 2.3a RAW PNG CHUNK EXIF EXTRACTION (no exiftool needed)

When `exiftool` is unavailable (macOS without brew-installed tools) and
`PIL` is broken in the venv, extract EXIF metadata directly from PNG
chunks using Python's `struct` module. Many phone-camera PNGs store
`DateTimeOriginal`, GPS direction, and camera info in `tEXt` chunks.

```python
import struct

with open('photo.png', 'rb') as f:
    f.read(8)  # PNG signature
    while True:
        length = struct.unpack('>I', f.read(4))[0]
        chunk_type = f.read(4)
        data = f.read(length)
        f.read(4)  # CRC

        if chunk_type == b'tEXt':
            null_idx = data.index(0)
            keyword = data[:null_idx].decode('ascii')
            value = data[null_idx+1:].decode('latin-1')
            if keyword.startswith('exif:'):
                print(f'{keyword}: {value}')

        if chunk_type == b'IEND':
            break
```

**Key EXIF tags found in tEXt chunks**: `exif:DateTimeOriginal`,
`exif:Make`, `exif:Model`, `exif:GPSImgDirection`,
`exif:GPSImgDirectionRef`, `exif:OffsetTime`,
`exif:LensMake`, `exif:LensModel`, `exif:Software`.

**PNG text chunk types**:
- `tEXt` — uncompressed key=value (null-separated)
- `zTXt` — zlib-compressed key=value
- `iTXt` — UTF-8 international text (can be compressed)

**Pitfalls**:
- `sips -g all` on macOS does NOT show EXIF data embedded in PNG
  chunks — it only reports file-level creation/modification timestamps.
- `mdls` shows Spotlight metadata which typically lacks EXIF fields.
- GPS coordinates (lat/lon) are stored in the EXIF IFD at the offset
  given by `exif:GPSInfo`, requiring full EXIF IFD parsing — but
  `DateTimeOriginal` and GPS direction are directly accessible in
  tEXt chunks.
- For OSINT challenges (NHNC 2026 "Final Boarding"), the
  DateTimeOriginal directly yields the date portion of the flag.

### 2.3b FIREFOX/CHROME HISTORY SQLITE ANALYSIS

When a CTF forensics challenge provides a `places.sqlite` file (Firefox)
or `History` file (Chrome), extract the browsing history to reconstruct
the challenge author's research path. See **`references/sqlite-forensics-methodology.md`** for the full systematic checklist including freelist recovery, freeblock chain walking, PRAGMA analysis, rowid gaps, custom visit types, and raw hex carving.

```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('places.sqlite')

# All visited URLs
for row in conn.execute(
    "SELECT id, url, title, description FROM moz_places"
):
    print(f"{row[1][:100]}")

# History visits with timestamps (PRTime = µs since 1601-01-01)
for row in conn.execute("""
    SELECT v.id, p.url, v.visit_date, v.visit_type
    FROM moz_historyvisits v JOIN moz_places p ON v.place_id = p.id
"""):
    ts = datetime(1601, 1, 1) + timedelta(microseconds=row[2])
    print(f"  {row[1][:80]} @ {ts}")
```

Common sources of flag clues in browser history:
- Proton Drive / cloud storage shared links
- Challenge author's GitHub repos
- Retro-themed archive sites used as challenge servers
- CTFtime event pages with challenge descriptions

### 2.4 Multi-Frame / Time-Series BMP Analysis (NEW)

When a challenge provides a sequence of numbered BMP files (e.g., `cap_000.bmp` through `cap_150.bmp`), they often represent time-series frames of an oscilloscope/oscillogram capture. The hidden message is typically revealed by analyzing the combined frames.

#### BMP Frame Analysis Workflow:

1. **Extract frame structure:** All frames typically share identical dimensions, palette, and header.
2. **Overlay all frames:** Sum pixel-wise — pixels appearing in many frames indicate stable UI elements (axes, rulers); pixels appearing in few frames are the variable trace.
3. **Extract trace per frame:** For each column in the trace area (between left/right axes), find the darkest pixel Y-position. This gives 151 × N trace points.
4. **Analyze trace dynamics:** Variable Y-positions across frames often encode the message (one value per frame = one symbol/bit per frame).
5. **Ruler analysis:** Left/right vertical strips often contain tick marks. If the ruler pattern varies across frames, it may encode data; if identical, it's a fixed UI element (not the message).

**BMP Frame Analysis Pitfall (learned the hard way):**
- Don't burn 20+ tool calls on pixel statistics, centroid hunting, ruler-shape comparison, LSB checks, Hough circles, contour analysis **without first confirming the companion tool can be cracked**.
- Each pixel analysis reveals the trace IS varying — but with 100s of unknowns (which column? which threshold? which property?), you cannot decode without the tool's reverse mapping.
- The user sees only "tried centroid, tried LSB, tried Hough" and concludes you're stuck.

**Correct order for this pattern:**
1. Triage bundle (~3 calls)
2. Confirm ZipCrypto (~1 call)
3. Password guess loop (~10s)
4. **bkcrack with zlib header as immediate next move** — don't defer it
5. Only attempt trace decoding if bkcrack genuinely fails (rare)

**BMP Frame Analysis Workflow:**

1. **Extract frame structure:** All frames typically share identical dimensions, palette, and header structure. Verify with:
   ```bash
   for f in cap_*.bmp; do file "$f"; done
   ```

2. **Trace extraction:** For each frame, find the trace (waveform) by scanning columns for the darkest pixel (lowest value in 8-bit grayscale):
   ```python
   # Per-frame trace extraction
   for x in range(left_margin, right_margin):
       col = image[:, x]
       dark_pixels = np.where(col < threshold)[0]
       if len(dark_pixels) > 0:
           y = height - 1 - dark_pixels[0]  # convert to image coords
           trace.append((x, y))
   ```

3. **Overlay analysis:** Sum all frames to see persistent patterns (grid, axes, static labels):
   ```python
   overlay = np.sum([frame < threshold for frame in frames], axis=0)
   ```

4. **Per-frame signal extraction:** The "moving" trace often encodes data. At each frame, measure:
   - Centroid X/Y of the trace
   - Leftmost/rightmost trace position
   - Y-position at fixed X coordinates (e.g., center column)
   - Number of dark pixels per column

5. **Signal reconstruction:** 151 frames × N samples per frame = time-series. The trace position sequence may encode:
   - ASCII/UTF-8 characters (one byte per frame)
   - Binary data (high/low threshold per frame)
   - Amplitude/frequency modulation

**Key patterns observed:**
- Left/right ruler tick marks are static (good for alignment)
- Center trace movement encodes data
- 5-level quantization in trace Y-position (common in oscilloscopes)
- 151 frames ≈ 21 chars × 7 bits/char (for `echo XXXX XXXXX XXXXX axis` format)

**Pitfalls:**
- DO NOT assume overlay reveals text directly — the trace is the signal, not the static overlay
- DO NOT use LSB steganography on these BMPs — palette is linear grayscale (0-255)
- DO NOT expect literal text in pixel values — the waveform POSITION encodes data
- Overlay max count > 100 means trace overlaps; use median Y per column instead of raw sum

**Reference: `references/oscilloscope-bmp-analysis.md`** (to be created)
```bash
# List all chunks with offsets
pngcheck -v image.png

# Look for data after IEND chunk:
python3 -c "
with open('image.png','rb') as f:
    data = f.read()
    iend = data.find(b'IEND') + 8
    if iend < len(data):
        print('Data after IEND:', data[iend:])
"
# Common stego chunks: tEXt, zTXt, iTXt, tIME (odd timestamps)
```

### 2.4 JPEG Forensics
```bash
# DCT coefficient analysis
jsteg reveal image.jpg            # JSteg detection
stegdetect image.jpg              # detect JSteg/JPHide/OutGuess/F5

# JPEG comment fields
exiftool -Comment image.jpg
strings image.jpg | grep -iE 'flag|ctf|comment'

# Error Level Analysis (ELA) — reveals spliced regions
python3 -c "
from PIL import Image, ImageFilter, ImageChops
img = Image.open('image.jpg')
img.save('/tmp/tmp_ela_q90.jpg', quality=90)
ela = ImageChops.difference(img, Image.open('/tmp/tmp_ela_q90.jpg'))
ela = ImageChops.multiply(ela, Image.new('RGB', img.size, (20,20,20)))
ela.save('ela_output.png')
"

# JPEG EXIF GPS / thumbnail extraction
exiftool -GPS* image.jpg
exiftool -ThumbnailImage -b image.jpg > thumb.jpg
```

### 2.5 QR Code & Barcode Recovery
```bash
zbarimg image.png                 # QR + barcodes
python3 -c "
from PIL import Image
# Try contrast enhancement for damaged QR codes
img = Image.open('qr.png').convert('L')
img.point(lambda x: 0 if x < 128 else 255).save('qr_binary.png')
"
```

---

## 3. AUDIO FORENSICS

### 3.1 Spectrogram Analysis
```bash
# sox spectrogram
sox audio.wav -n spectrogram -Y 300 -l -r -o spectrogram.png
sox audio.wav -n spectrogram -Y 200 -X 50 -m -r -o spec_highres.png

# Audacity: File → Import → Audio, then click track dropdown → Spectrogram
# Sonic Visualiser — powerful standalone spectrogram tool
```

### 3.2 SSTV Decoding (Slow-Scan TV, common in CTF)
```bash
# qsstv (GUI, Linux) or decode from WAV file:
sstv -d audio.wav -o output.png
```

### 3.3 DTMF Decoding
```bash
# multimon-ng
multimon-ng -t wav audio.wav
multimon-ng -a DTMF audio.wav
```

### 3.4 WAV LSB Steganography
```bash
# wav-stego tools
stegolsb wavsteg -r -i audio.wav -o output.txt -n 1   # 1 LSB
stegolsb wavsteg -r -i audio.wav -o output.txt -n 2   # 2 LSBs
```

---

## 4. NETWORK FORENSICS (PCAP ANALYSIS)

### 4.1 Essential tshark Filters
```bash
# HTTP traffic
tshark -r capture.pcap -Y "http" -T fields -e http.host -e http.request.uri
tshark -r capture.pcap -Y "http.request" -T fields -e http.request.full_uri

# Extract all HTTP objects (files transferred)
tshark -r capture.pcap --export-objects http,./http_objects/

# DNS queries
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name | sort -u

# DNS exfiltration (long subdomain queries)
tshark -r capture.pcap -Y "dns.qry.name matches \".{30,}\""

# DNS TXT exfil
tshark -r capture.pcap -Y "dns.txt" -T fields -e dns.txt

# ICMP exfil (data in ICMP payload)
tshark -r capture.pcap -Y "icmp" -T fields -e data

# USB traffic
tshark -r capture.pcap -Y "usb.capdata" -T fields -e usb.capdata

# HTTP POST with credentials
tshark -r capture.pcap -Y "http.request.method == POST" -T fields -e http.file_data

# Follow TCP stream
tshark -r capture.pcap -z follow,tcp,ascii,0
```

### 4.2 USB HID Keystroke Reconstruction
Extract HID data and decode with Python using the HID usage ID mapping table.

### 4.3 TLS Decryption
```bash
# If you have the key log file:
# Wireshark: Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename
tshark -r capture.pcap -o tls.keylog_file:keylog.txt
```

### 4.4 Wireshark Display Filters Cookbook
```
http.request.method == "POST"
dns.qry.name contains "flag"
tcp.port == 4444 or udp.port == 4444   # common reverse shell ports
tcp.flags.syn == 1 and tcp.flags.ack == 0  # SYN scan
frame contains "password"
```

---

## 5. MEMORY FORENSICS

### 5.1 Volatility 3 Quick Reference
```bash
# Image identification
vol -f memory.dump windows.info

# Process listing
vol -f memory.dump windows.pslist
vol -f memory.dump windows.pstree          # process tree
vol -f memory.dump windows.cmdline         # command-line arguments

# Malware detection
vol -f memory.dump windows.malfind         # injected code detection
vol -f memory.dump windows.netscan         # network connections

# Credential harvesting
vol -f memory.dump windows.hashdump        # NTLM hashes
vol -f memory.dump windows.lsadump

# File recovery
vol -f memory.dump windows.filescan        # list all files
vol -f memory.dump windows.dumpfiles --pid <PID>

# Process memory dump for string search
vol -f memory.dump windows.memmap --pid <PID> --dump
strings pid.<PID>.dmp | grep -iE 'flag|ctf|key|password'

# Linux memory
vol -f memory.lime linux.pslist
vol -f memory.lime linux.bash              # bash history
```

### 5.2 Common CTF Memory Scenario Workflow
```bash
# 1. Identify profile
vol -f mem.dump windows.info

# 2. Look for suspicious processes
vol -f mem.dump windows.pstree | grep -iE 'cmd|powershell|nc|shell|backdoor'

# 3. Check network for C2
vol -f mem.dump windows.netscan | grep ESTABLISHED

# 4. Dump suspicious process
PID=1234
vol -f mem.dump windows.memmap --pid $PID --dump

# 5. Extract strings and grep for flags
strings -n 8 pid.$PID.dmp | grep -E '(picoCTF|HTB|flag|FLAG)'
```

---

## 6. DISK FORENSICS

### 6.1 General Workflow
```bash
# Mount read-only
losetup -r /dev/loop0 disk.img
mount -o ro /dev/loop0p1 /mnt/forensic

# Or use autopsy/sleuthkit
mmls disk.img                   # partition layout
fsstat -o $OFFSET disk.img      # filesystem info
fls -r -o $OFFSET disk.img      # list all files
icat -o $OFFSET disk.img $INODE > recovered_file
tsk_recover -o $OFFSET disk.img output_dir/
```

### 6.2 NTFS Specifics
```bash
# MFT (Master File Table) dump and parse
icat -o $OFFSET disk.img 0 > mft.raw
analyzeMFT.py -f mft.raw -o mft.csv

# Alternate Data Streams (ADS)
fls -r -o $OFFSET disk.img | grep ":"     # streams show as file:stream
icat -o $OFFSET disk.img INODE-NTFS-ADS > stream_data

# Deleted file recovery
fls -r -o $OFFSET disk.img | grep deleted
```

### 6.3 EXT4 Specifics
```bash
# Journal recovery
debugfs -R "logdump -a" disk.img | less

# Superblock and inode inspection
debugfs -R "stats" disk.img
debugfs -R "ls -l /" disk.img

# Deleted inode recovery
extundelete disk.img --restore-all
ext4magic disk.img -r -d recovered/
```

### 6.4 Partition Table Recovery
```bash
# If partition table is missing:
testdisk disk.img                 # interactive recovery
gdisk -l disk.img                 # GPT inspection
```

---

## 7. ARCHIVE FORENSICS

### 7.1 ZIP Attacks
```bash
# Plaintext attack: if you have one original file from the archive:
bkcrack -C encrypted.zip -c known_file.txt -p known_file.txt.plain
bkcrack -C encrypted.zip -c known_file.txt -k <keys> -d decrypted.zip

# Password cracking
zip2john encrypted.zip > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# 7z
7z2john archive.7z > hash.txt

# RAR
rar2john archive.rar > hash.txt
```

### 7.2 Nested Archive Extraction
```bash
# Recursive extraction script with depth safety (max 50 levels)
python3 << 'EOF'
import os, subprocess, magic, shutil
def extract_recursive(path, depth=0):
    if depth > 50: return  # safety limit
    mime = magic.from_file(path, mime=True)
    if 'gzip' in mime:
        subprocess.run(['gunzip', '-k', path], check=False)
        base = path.replace('.gz','')
        if os.path.exists(base): extract_recursive(base, depth+1)
    elif 'zip' in mime:
        subprocess.run(['7z', 'x', f'-o{path}_extracted', path, '-y'], check=False)
        for root, dirs, files in os.walk(f'{path}_extracted'):
            for f in files: extract_recursive(os.path.join(root,f), depth+1)
    else:
        subprocess.run(['binwalk', '-Me', path], check=False)

extract_recursive('challenge.bin')
EOF
```

---

## 8. DOCUMENT FORENSICS

### 8.1 OOXML (DOCX, XLSX, PPTX)
```bash
# OOXML is a ZIP — unzip and inspect
unzip -l document.docx
unzip document.docx -d docx_contents/

# Check for hidden content
find docx_contents/ -type f | xargs strings | grep -iE 'flag|ctf|hidden'

# Key internals:
#   word/document.xml     — main content
#   word/comments.xml     — comments (CTF flags in comments!)
#   word/footnotes.xml    — footnotes
#   docProps/custom.xml   — custom properties
#   word/media/           — embedded images (check for stego)
```

### 8.2 PDF Analysis
```bash
# qpdf — structural analysis and decompression
qpdf --qdf --object-streams=disable suspicious.pdf expanded.pdf
grep -iE 'flag|ctf|hidden' expanded.pdf

# peepdf — interactive PDF analysis
peepdf -i suspicious.pdf

# PDF stream extraction
pdf-parser.py suspicious.pdf
pdf-parser.py -o 5 suspicious.pdf    # extract object 5

# Check for: /EmbeddedFiles, /OpenAction, /AA, /JS, /JavaScript

# pdfimages extracts all images
pdfimages -all suspicious.pdf pdf_img_
```

### 8.3 VBA Macro Extraction & Deobfuscation
```bash
# oletools suite
olevba document.docm                  # extract + analyze VBA
olevba -c document.docm               # show only code
olevba --deobf document.docm          # attempt deobfuscation

# Common hidden VBA techniques:
#   - UserForm labels/captions
#   - Document variables
#   - Custom document properties
#   - Hidden worksheets in XLSM
```

---

## 9. FLAG HUNTING PATTERNS

### 9.1 Common Flag Formats
```bash
# Standard CTF flag regex patterns:
grep -aEo 'picoCTF\{[^}]+\}'
grep -aEo 'HTB\{[^}]+\}'
grep -aEo 'flag\{[^}]+\}'
grep -aEo 'FLAG\{[^}]+\}'
grep -aEo 'ctf\{[^}]+\}'
grep -aEo 'thm\{[^}]+\}'         # TryHackMe
grep -aEo 'KCTF\{[^}]+\}'
grep -aEo 'inctf\{[^}]+\}'
grep -aEo 'amateursCTF\{[^}]+\}'
grep -aEo 'idek\{[^}]+\}'
grep -aEo 'dice\{[^}]+\}'
grep -aEo 'utflag\{[^}]+\}'

# Generic brace-flag pattern
grep -aEo '[A-Za-z0-9_]+\{[A-Za-z0-9_!@#$%^&*()\-+=.,;:\[\]{}| ]{5,80}\}'

# Base64-encoded flags
grep -aEo '[A-Za-z0-9+/]{20,}={0,2}' | while read b64; do echo "$b64" | base64 -d 2>/dev/null; done

# ROT13 / Caesar
grep -a . suspicious.txt | tr 'A-Za-z' 'N-ZA-Mn-za-m' | grep -i flag
```

---

## 10. FORENSICS PLAYBOOK: Quick Decision Tree

```
Unknown file
├── file says "data" → binwalk -Me, inspect hex
├── file says "PNG/JPEG/GIF" → zsteg, exiftool, stegsolve
├── file says "WAV/MP3/OGG"  → spectrogram, LSB, DTMF, SSTV
├── file says "PCAP"         → tshark HTTP/DNS/USB/follow
├── file says "ZIP/RAR/7z"   → zipinfo, zip2john, bkcrack
├── file says "PE/EXE/ELF"   → strings, volatility (if memory)
├── file says "data" + contains "PK" → rename to .zip & extract
├── file says "data" + has JFIF/PNG magic at offset → carve with foremost
└── Still unknown → strings | grep flag, OR binwalk -Me --dd='.*'
```

---

## 10.5. SCOPE-TRACE BMP SERIES + ENCRYPTED TOOL (oscilloscope captures + bkcrack)

When the artifact bundle is `images.zip` of `cap_NNN.bmp` (541×541 8-bit grayscale with left/right axis strips + sparse trace) + a password-protected `tool.zip` containing an `imgconv`-style binary, this is a recurring CTF class. See `references/scope-trace-bmp-stego.md` for the full workflow: ZipCrypto identification, bkcrack with zlib header (`78 9C`/`78 DA`), and trace extraction when you can't get the tool.

**Always try `fcrackzip -D -p /tmp/rockyou.txt -u tool.zip` BEFORE writing custom C brute-forcers.** Wordlist wins in the majority of CTFs in under a second. See `references/encrypted-archive-recovery.md` for the full password-cracking discipline (rockyou → short brute → mask → bkcrack) and the false-positive pitfalls when brute-forcing ZipCrypto with only a CRC check.

When you cannot run the recovered `imgconv` (e.g., macOS Intel cannot execute Linux ELF), fall back to **image-sequence decoding** — concatenating the trace Y-positions across frames often produces a printable byte stream. See `references/image-sequence-decoding.md`.

### Discipline Pitfall (learned the hard way)

When this pattern shows up, **spend at most ~5 tool calls on image inspection before pivoting to the encrypted tool.** The single highest-leverage action is `bkcrack -C tool.zip -c imgconv -p <zlib-header.bin>` — that one call often unlocks everything. The pitfall is:

1. Burning 20+ tool calls doing pixel-statistics, centroid hunting, ruler-shape comparison, LSB checks, Hough circles, contour analysis on the BMPS **without first confirming the tool can be cracked**.
2. Each pixel analysis call reveals that the trace IS varying — but with 100s of unknowns (which column? which threshold? which property?), you cannot decode without the tool's reverse mapping.
3. The user sees only "tried centroid, tried LSB, tried Hough" and concludes you're stuck.

**Correct order:** (1) Triage bundle (~3 calls); (2) Confirm ZipCrypto (~1 call); (3) Password guess loop (~10s); (4) **bkcrack with zlib header as immediate next move** — don't defer it; (5) Only attempt trace decoding if bkcrack genuinely fails (which is rare for these challenges).

If after bkcrack you still don't have the tool, that's when direct trace extraction earns its budget — and even then, set a hard iteration cap and surface the partial result rather than burning the user's patience.

When the user says "你自己處理 / 全部做完再跟我講 / 好了" — they want a one-shot push to the answer, not a slow statistical archaeology. **Default to the action that maximizes expected flag recovery per tool call.**

## 11. CHESS-BOARD PNG SERIES (multi-frame OCR puzzles)

When the archive contains N PNGs of chess boards at uniform resolution, the flag is usually hidden in a per-board game-state property (check / checkmate / stalemate / side-to-move / legal move count). Recover a valid FEN per board and aggregate.

- Standard chess.com / lichess piece renderings cluster by silhouette **area**: Pawn ~545, Rook ~580, Queen ~712, King ~762, Knight ~824, Bishop ~875. The K/Q/B trio is hard to distinguish from thumbnails — **always brute-force the 6 permutations through `python-chess.Board.is_valid()`**.
- White vs Black: count `(R,G,B) > 220` pixels inside the silhouette. White pieces show bright interior; black pieces are pure dark fill.
- Once every FEN is valid, encode each board as a bit / symbol by `is_check()`, `is_checkmate()`, `is_stalemate()`, side-to-move, etc., then concatenate to form the flag.

Full reproducible pipeline: see `references/chess-board-ocr.md`.

## 12. KEY TOOLS INSTALL ONE-LINER
```bash
# Essential forensics toolkit (Debian/Ubuntu)
sudo apt install -y binwalk foremost exiftool pngcheck steghide zsteg stegseek \
  tshark volatility3 sleuthkit testdisk audacity sox multimon-ng qpdf \
  oletools bkcrack john hashcat poppler-utils pdfimages zbar-tools

# Python tools
pip install stegoveritas stegolsb oletools peepdf
```

---

## 13. 2025-2026 FORENSICS TRENDS & NEW TOOLS

### 13.1 Memory Forensics: Volatility 3 + MemProcFS Dominance
**Volatility 2 is deprecated (April 2025).** Volatility 3 is now the standard with full feature parity + Linux/macOS support. Key 2025 updates:
- **No `--profile` required** — symbol tables (JSON) auto-downloaded or built from `vmlinuz`/`kernel.dwarf`
- **macOS support matured** — `mac.pslist`, `mac.netscan`, `mac.malfind`, `mac.bash` plugins working on Sequoia (24.x kernels)
- **Linux kernel 6.x support** — `linux.pslist`, `linux.bash`, `linux.malfind`, `linux.lsmod`, `linux.check_modules`
- **New 2024-2025 plugins**: `windows.etw`, `windows.etw_providers`, `windows.handle`, `windows.privileges`, `windows.sessions`, `linux.proc_maps`, `mac.vminfo`
- **Plugin contest winners (2024)**: `windows.ghost` (ghost processes), `linux.hidden_modules`, `mac.kextstat`

**MemProcFS** (by Ulf Frisk) is now the preferred **interactive** memory analysis tool:
```bash
# Mount memory as virtual filesystem — browse with ls/cat/grep
./MemProcFS -device mem.dmp -mount /mnt/mem
ls /mnt/mem/processes/    # each PID is a directory
cat /mnt/mem/processes/1234/cmdline
cat /mnt/mem/files/       # all file handles
cat /mnt/mem/registry/    # full registry hive
cat /mnt/mem/network/     # connections, sockets
```
- Extracts **more artifacts** than Volatility alone (handles, VAD, heap, registry)
- Works on live systems + dumps (raw, lime, vmem, crash dump)
- Combine with Volatility: `vol -f /mnt/mem/vmem windows.pslist`

**13Cubed 2025 Challenge workflow**: MemProcFS mount → browse processes → dump suspicious → Volatility plugins for deep dive.

---

### 13.2 Network Forensics: Zeek + Arkime + Malcolm Stack
**Zeek (ex-Bro)** and **Arkime (ex-Moloch)** are now standard for large-scale PCAP analysis in CTFs:
```bash
# Zeek: protocol analysis, file extraction, anomaly detection
zeek -r capture.pcap local
# Output: conn.log, http.log, dns.log, files.log, ssl.log, weird.log

# Arkime: full packet capture + web UI for session search
docker run -d --name arkime -p 8005:8005 -v $(pwd)/pcap:/data/pcap \
  -v $(pwd)/arkime:/data/arkime  arkime/arkime:latest capture

# Malcolm (Idaho Lab): Docker compose stack = Zeek + Arkime + Suricata + OpenSearch + dashboards
git clone https://github.com/idaholab/Malcolm
cd Malcolm && ./scripts/configure && docker compose up -d
# Web UI: https://localhost — upload PCAP, get full protocol parse + file carve + threat intel
```
**CTF workflow**: Drop PCAP into Malcolm → auto-extracts files, parses TLS JA3, maps DNS exfil, shows HTTP objects, runs Suricata rules.

---

### 13.3 AI-Powered Steganalysis: Aletheia + Deep Learning
**Aletheia** (daniellerch/aletheia) — open-source deep-learning steganalysis toolbox (JOSS 2024):
```bash
pip install aletheia
aletheia detect image.png          # CNN-based detection (HUGO, UNIWARD, WOW, S-UNIWARD)
aletheia train --dataset BOSSBase  # train custom models
```
- Detects **adaptive steganography** (HUGO, UNIWARD, WOW, MiPOD) that defeats classical chi-square/RS analysis
- Pre-trained models on BOSSBase / ALASKA2 datasets
- Use as **triage**: if Aletheia says "clean", skip deep LSB analysis

**2025-2026 Trend**: GAN-based steganography (adversarial embedding against CNN detectors) → CTF challenges now use **SteganoGAN**, **SSGAN**, **Coverless Steganography** (hiding in generated images). Detection requires **ensemble steganalysis** (Aletheia + StegExpose + custom CNNs).

**New stego tools for CTF**:
- **stegoveritas** — all-in-one image stego analysis (LSB, palette, metadata, transform, AI)
- **stegoVeritas** Docker: `docker run -v $(pwd):/data dominicbreuker/stego-toolkit`
- **CloakedPixel** — new LSB tool for PNG with password protection

---

### 13.4 Archive Forensics: bkcrack + Known-Plaintext Discipline
**bkcrack** (2024-2025 updates): ZIP known-plaintext attack for ZipCrypto (legacy encryption).
```bash
# Minimum 12 CONTIGUOUS known plaintext bytes from compressed stream
# Best source: zlib header (78 9C / 78 DA / 78 01) + file magic
printf '\x78\x9C' > zlib_header.bin
bkcrack -C archive.zip -c target_file -p zlib_header.bin -o 0

# If you have a known file (even partial):
bkcrack -C archive.zip -c target_file -k <keys> -d decrypted.zip
```
**Critical discipline (from 2026 CTFs)**:
1. **Wordlist first** (rockyou) — wins >90% of CTF ZIPs in <1s (`fcrackzip -D -p rockyou.txt -u`)
2. **Short brute** (1-5 chars) — 2 min max
3. **bkcrack with zlib header** — immediate next move if wordlist fails
4. **Full brute / GPU** — almost never needed in CTF

**False positive trap**: CRC-only checks give 1/65536 false hits. **Always verify by full zlib decompression**.

---

### 13.5 New File Format Challenges (2025-2026)
| Format | Tools | CTF Patterns |
|--------|-------|--------------|
| **Minidump (.dmp)** | `minidump-stackwalk` (Rust, JSON output), `cdb`/`windbg` | Crash dump forensics, stack trace flag, heap grooming |
| **SIF / Singularity / Apptainer** | `singularity exec`, `unsquashfs` | Container image forensics, hidden layers |
| **SquashFS** | `unsquashfs -l`, `unsquashfs -d out image.sqsh` | Embedded firmware, router FS |
| **EWF / E01** | `ewfmount`, `libewf` | Expert Witness forensic images |
| **VHDX / VMDK** | `qemu-nbd`, `nbd-client`, `guestmount` | VM disk forensics |
| **BitLocker** | `dislocker`, Autopsy 4.22+ | Encrypted volume analysis |
| **OCR / PDF** | `pymupdf`, `pdfplumber`, `ocrmypdf` | Scanned docs, hidden text layers |

---

### 13.6 Disk Forensics: Autopsy 4.22+ + TSK Updates
- **Autopsy 4.22** (2024): BitLocker native support (enter recovery key), Cyber Triage sidecar, GStreamer 1.20, Tesseract 4.10
- **Sleuth Kit (TSK) 4.12+**: Better EXT4/XFS/APFS support, `fsstat` JSON output (`-j`), `fls` bodyfile v3
- **APFS forensics**: `apfs-fuse` for mounting, `apfsck` for analysis

---

### 13.7 Quick-Reference: 2025-2026 CTF Forensics Tool Matrix

| Category | Primary (2025+) | Fallback / Legacy | New / AI-Enhanced |
|----------|----------------|-------------------|-------------------|
| **Memory** | Volatility 3, MemProcFS | Volatility 2 (deprecated) | Volatility 3 macOS/Linux plugins |
| **Network** | Zeek + Arkime (Malcolm stack) | Wireshark/tshark only | Suricata rules + JA3 TLS fingerprinting |
| **Stego (images)** | zsteg, stegoveritas, Aletheia (DL) | steghide, stegsolve, stegdetect | SteganoGAN detection, ensemble CNNs |
| **Stego (audio)** | sox + spectrogram, stegolsb | audacity manual | SSTV auto-decode, DTMF ML |
| **Archives** | bkcrack (known-plaintext), fcrackzip | john/hashcat | ZipCrypto CRC false-positive verification |
| **Disk** | Autopsy 4.22+, TSK 4.12+, dislocker | autopsy 4.19 | BitLocker native, APFS support |
| **Documents** | oletools, pymupdf, pdfplumber | peepdf, pdf-parser | VBA deobfuscation ML, OCR pipeline |
| **Containers** | singularity, unsquashfs, crane | docker save | SIF/Apptainer layer analysis |

---

### 13.8 Emerging CTF Challenge Patterns (2025-2026)
1. **Memory + Network correlation** — memdump + PCAP from same incident; correlate Volatility `netscan` with Zeek `conn.log`
2. **AI-generated stego covers** — flag hidden in Midjourney/Stable Diffusion output; detect with Aletheia + noise analysis
3. **Container escape forensics** — analyze container runtime (containerd/cri-o) memory + disk for breakout artifacts
4. **Firmware/embedded forensics** — SquashFS/UBIFS/JFFS2 from router/IoT dumps; `binwalk -Me` + `unsquashfs`
5. **Cloud forensics** — AWS/GCP/Azure log analysis (CloudTrail, VPC flow logs) + memory from compromised instances
6. **Minidump crash forensics** — Windows minidump with flag in stack/heap; `minidump-stackwalk --json`
7. **Coverless steganography** — no cover modification; flag encoded in *generation parameters* of AI image (prompt, seed, steps)

---

*This skill is maintained by Nous Research. Pull requests with additional techniques, tool references, or CTF challenge patterns are welcome.*
