# Printing to Network Printers via CUPS / IPP

How to go from "found a printer on the network" to "printed a test page." Covers diagnosis of supported formats and CUPS integration.

## Workflow

### Step 1: Diagnose supported formats via IPP

Do NOT assume PostScript. Most consumer inkjets and many office printers don't support it.

```bash
# Query what document formats the printer actually supports
ipptool -tv http://$PRINTER_IP:631/ipp/print get-printer-attributes.test 2>&1 | grep "document-format"
```

Example output from Brother MFC-J4340DW:
```
document-format-supported = application/octet-stream,image/urf,image/jpeg,image/pwg-raster,application/vnd.brother-hbp
document-format-default = application/octet-stream
document-format-preferred = image/urf
```

**No PostScript in the list → do not send PS/PCL test pages.** The first test page attempt with raw PostScript via JetDirect produced nothing.

Also query general attributes for DPI, duplex, color mode:
```bash
ipptool -tv http://$PRINTER_IP:631/ipp/print get-printer-attributes.test 2>&1 | grep -E "resolution|color|sides|media-default"
```

### Step 2: Add printer to CUPS

```bash
# Add via IPP everywhere driver (auto-discovers capabilities)
lpadmin -p PrinterName -v ipp://$PRINTER_IP/ipp/print -E -m everywhere
```

### Step 3: Generate a test page in a supported format

**If `image/jpeg` is supported (most common for consumer printers):**

Generate a BMP with Python (no dependencies needed), then convert to JPEG via macOS native `sips`:

```python
# Pixel function creates: title bar, CMYK color bars, grayscale ramp, resolution lines
# Width/height: 1275x1650 (~US Letter at 150dpi)
# Write BMP, then:
import subprocess
subprocess.run(['sips', '-s', 'format', 'jpeg', '/tmp/testpage.bmp', '--out', '/tmp/testpage.jpg'])
```

Full BMP generation script: see `scripts/generate-testpage-bmp.py`.

**If `application/octet-stream` is the default:** Plain text via `lp` may work (CUPS filter chain handles it), but the result depends on the printer's text rendering capability. A JPEG test page is more reliable.

### Step 4: Print

```bash
lp -d PrinterName /tmp/testpage.jpg
```

Then monitor:
```bash
lpstat -p PrinterName     # printer status
lpq -P PrinterName        # job queue
lpstat -W completed -p PrinterName  # job history
```

### Step 5: Verify

The printer's web UI on port 80 usually shows a status page. Check for "Ready" after printing:
```bash
curl -sk http://$PRINTER_IP/ 2>&1 | grep -oE 'moni[A-Za-z]+'
# moniOk = ready
```

## CUPS troubleshooting

- Job stuck on "waiting for printer to become available": printer may be in deep sleep. Wake it by sending a small PJL command via port 9100:
  ```bash
  echo -ne "\x1B%-12345X@PJL INFO STATUS\r\n\x1B%-12345X" | nc -w 3 $PRINTER_IP 9100
  ```
- `lpadmin` fails with "Unable to connect": check that IPP port 631 is actually open
- Text test page prints but JPEG doesn't: verify `document-format-supported` includes `image/jpeg`

## Printer-specific notes

### Brother MFC-J4340DW (inkjet, 2026 session)
- IPP endpoint: `ipp://192.168.68.103/ipp/print`
- Formats: JPEG, URF, PWG-Raster, Brother-HBP, octet-stream
- **No PostScript support**
- MAC OUI `c8:94:02` (HP/Aruba) — misleading, ignore OUI for Brother printers
- Resolution: 600dpi, Duplex supported, Color: auto
- Ports: 80 (web UI), 515 (LPR), 631 (IPP), 9100 (JetDirect)
- Web UI shows ink levels (M/C/Y/BK) and page yields
