# FORENSICS

### File Analysis

```bash
# Identify file type
file unknown
binwalk unknown        # find embedded files
xxd unknown | head     # hex dump

# Extract embedded files
binwalk -e unknown     # auto-extract
foremost unknown       # file carving

# Search for flags
strings unknown | grep -i 'flag{'
strings unknown | grep -i 'ctf{'
strings -e l unknown   # 16-bit little-endian
strings -e b unknown   # 16-bit big-endian
```

### Memory Forensics (Volatility)

```bash
# Identify profile
volatility -f memory.dmp imageinfo

# Process list
volatility -f memory.dmp --profile=Win7SP1x64 pslist
volatility -f memory.dmp --profile=Win7SP1x64 pstree

# Command history
volatility -f memory.dmp --profile=Win7SP1x64 cmdscan
volatility -f memory.dmp --profile=Win7SP1x64 consoles

# Dump process memory
volatility -f memory.dmp --profile=Win7SP1x64 memdump -p <PID> -D out/

# Find strings in memory dump
strings out/<PID>.dmp | grep -i flag

# Network connections
volatility -f memory.dmp --profile=Win7SP1x64 netscan

# Registry
volatility -f memory.dmp --profile=Win7SP1x64 hivelist
volatility -f memory.dmp --profile=Win7SP1x64 printkey -K "SAM\\Domains\\Account\\Users"
```

### PCAP / Network Forensics

```bash
# Wireshark / tshark analysis
tshark -r capture.pcap -Y "http" -T fields -e http.host -e http.request.uri
tshark -r capture.pcap -Y "dns" -T fields -e dns.qry.name
tshark -r capture.pcap -Y "ftp" -T fields -e ftp.request.command -e ftp.request.arg

# Extract files from HTTP
tshark -r capture.pcap --export-objects http,/tmp/extracted/

# Follow TCP stream
tshark -r capture.pcap -q -z follow,tcp,ascii,0

# Extract data from ICMP
tshark -r capture.pcap -Y "icmp" -T fields -e data.data
```

### Disk Forensics

```bash
# Mount disk image
mount -o ro,loop disk.img /mnt/analysis

# Deleted file recovery
testdisk disk.img
photorec disk.img

# NTFS analysis
fls -r disk.img
icat disk.img <inode>

# EXT4 analysis
debugfs disk.img
  ls -la /
  cat /path/to/file

# Find hidden files
find /mnt/analysis -name ".*" -type f
getfattr -d -m - /mnt/analysis/*
```

---
