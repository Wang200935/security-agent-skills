# Forensics CTF Playbook

## Universal File Triage

```bash
file artifact
sha256sum artifact
xxd -l 256 artifact
strings -a artifact | head -100
binwalk artifact
exiftool artifact
```

Look for:
- magic-byte mismatch
- appended data after EOF markers
- embedded archives/files
- high entropy encrypted/compressed regions
- metadata comments, author, software, timestamps
- flag-like strings and base encodings

## Images

- EXIF/comments/thumbnails.
- PNG chunks: `pngcheck -v`, unusual ancillary chunks, trailing bytes.
- LSB stego: inspect bit planes/channels.
- Palette/alpha channel messages.
- QR/barcode hidden in contrast/levels.

## Audio/Video

- Metadata and attached images/subtitles.
- Spectrogram for text/images.
- Channels difference, reversed audio, speed changes.
- Individual frames for QR/hidden text.

## Archives

- Nested archives and misleading extensions.
- Password hints from metadata/strings/challenge text.
- Corrupt header recovery.
- Zip comments and extra fields.
- Known-plaintext only in CTF scope.

## Documents

- PDF hidden text/layers/attachments/metadata.
- Office macros and embedded objects.
- OLE streams with `oletools`.

## Disk Images

- Partition table and filesystem type.
- Deleted files, slack space, unallocated space.
- Browser/app artifacts, shell history, config files.
- **Firefox places.sqlite**: See `references/places-sqlite-forensics-patterns.md` for systematic flag-hunting workflow. Quick win: `strings places.sqlite | grep -i 'FLAG{'` before deep analysis.
- Chrome history, cookies, and login data are also SQLite databases — same approach.

## Solve Discipline

Work from least destructive and most general to format-specific. Keep original read-only and store extracted files in a separate directory.
