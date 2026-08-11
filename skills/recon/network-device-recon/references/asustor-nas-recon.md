# ASUSTOR NAS Reconnaissance Notes

Example from real session (2026-05-02) — ASUSTOR NAS at `192.168.68.104`.

## Identification

- **Web UI fingerprint**: `<!-- Copyright (c) 2022 Asustor Inc. All rights reserved. -->`, `<title>Ready to Serve!</title>`, `Server: Apache`
- **Admin UI ports**: 8000 (HTTP), 8001 (HTTPS) — these were firewalled/closed in this case
- **Web server on 80/443** runs Apache and serves the "Ready to Serve!" landing page
- **MAC OUI**: `78:72:64` (Asustor)

## Open Ports

```
21    FTP
22    SSH (accepts TCP, but shell login may still be disallowed for some users)
80    HTTP (Apache landing page)
139   NetBIOS
443   HTTPS
445   SMB
548   AFP (Apple Filing Protocol)
631   IPP (print server feature)
1723  Additional service observed open
2049  NFS
32400 Plex Media Server
9001  UMS web UI (not ADM)
```

## SMB / FTP / Authenticated Access Notes

Guest listing (`smbutil view -g smb://IP`) revealed **19 shares without authentication**:

| Share | Type | Notes |
|---|---|---|
| Surveillance | Disk | Surveillance default shared folder |
| RD | Disk | 研發部 |
| 行政部 | Disk | |
| User Homes | Disk | All users' home directories |
| Media | Disk | Media default shared folder |
| 財務部 | Disk | 財務部 |
| Web | Disk | Web default shared folder |
| PM | Disk | 專案部 |
| 採購部 | Disk | 採購部 |
| Download | Disk | Download default shared folder |
| Plex | Disk | Default location for Plex library |
| Music | Disk | Default Music shared folder |
| Comics | Disk | 漫畫庫 |
| Photos | Disk | Photo Gallery default shared folder |
| Video | Disk | |
| IPC$ | Pipe | IPC Service |
| Public | Disk | System default share |
| Docker | Disk | Data and files directory for Docker Apps |
| Home | Disk | Home directory |

Key observation: all 19 shares were **guest-listable** — no password needed to see the share names. Actual mount may require credentials depending on share configuration.

Additional authenticated findings from a later session on the same NAS:
- `ellis` / provided password worked for SMB mounts and FTP login.
- FTP root listing confirmed `Docker`, `User Homes`, `Home`, `Plex`, and `Web` shares exist even when ADM web login was unavailable.
- The same `ellis` credentials did NOT produce an SSH shell; SSH accepted the TCP connection and prompted for a password, then re-prompted/closed. This strongly suggests SSH permission/account-scope differences rather than a universally wrong password.
- `32400` responded as Plex (`/identity` returned Plex XML) while Jellyfin ports were closed.
- `9001` served a UMS media UI and should not be confused with the ASUSTOR ADM management interface.

## Comparison: Synology vs QNAP vs ASUSTOR

| Feature | ASUSTOR | Synology | QNAP |
|---|---|---|---|
| Admin UI port | 8000/8001 | 5000/5001 | 8080/8443 |
| Web landing page | "Ready to Serve!" + Apache footer | DSM branded | QTS branded |
| SMB guest listing | Often works | Usually blocked | Usually blocked |
| Copyright in HTML | `Asustor Inc.` | Not typically | Not typically |
| Web server | Apache | nginx | Apache/nginx |
