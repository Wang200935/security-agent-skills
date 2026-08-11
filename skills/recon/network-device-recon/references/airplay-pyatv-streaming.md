# AirPlay / pyatv Streaming Reference

How to discover AirPlay-capable devices and attempt streaming. Covers `pyatv` installation, scan results interpretation, and common failure modes.

## Installation

```bash
pip3 install pyatv
export PATH="$HOME/Library/Python/3.9/bin:$PATH"
```

## Discovery

```bash
atvremote scan
```

### Interpreting scan output

Key fields:
- **Deep Sleep** — `True` means the device won't accept connections. It must be woken first (app, physical button, or playing from already-paired device). Deep Sleep devices fail at RTSP metadata exchange with `ConnectionLostError`.
- **Pairing** — `NotNeeded`, `Mandatory`, or `Unsupported`. `Mandatory` means a PIN is required (Samsung TVs show it on screen). `NotNeeded` is ideal but Deep Sleep can still block.
- **Protocols** — `AirPlay` (video/audio), `RAOP` (Remote Audio Output Protocol — Apple's audio streaming), `Companion` (remote control)
- **Credentials** — `None` means no password required (separate from pairing)

### Real session devices (2026-05-02, 192.168.68.0/24)

| Device | IP | MAC | Deep Sleep | Pairing | Protocols |
|---|---|---|---|---|---|
| Bose Smart Soundbar 900 "客廳" | .101 | ac:bf:71 (Apple) | **True** | NotNeeded | AirPlay, RAOP |
| Samsung QN95BA 65 | .111 | 10:2b:41 (Google) | False | **Mandatory** | AirPlay |
| Mac mini "王池川的Mac mini" | .110 | 14:98:77 (Apple) | False | NotNeeded | AirPlay, RAOP, Companion |

## Streaming via pyatv

### Local file
```bash
atvremote --id <DEVICE_ID> stream_file=/tmp/test_tone.wav
```

Use the shorter identifier (e.g., `ACBF71593E11`) from the scan output.

### URL
```bash
atvremote --id <DEVICE_ID> stream_file=https://example.com/audio.mp3
```

**Note:** `stream_file` with URLs requires `miniaudio` to decode the remote stream. Some MP3 encodings may fail with `DecodeError: failed to init decoder` — use local WAV files as fallback.

### Multiple devices error
If the network has >1 AirPlay device, `atvremote` will error "Found more than one Apple TV; specify one using --id". Always pass `--id` with the target device's identifier.

## Failure modes

### Deep Sleep (Bose Soundbar)
```
pyatv.exceptions.ConnectionLostError: connection was lost
RuntimeError: not connected to remote
```
Symptoms: `pyatv scan` shows `Deep Sleep: True`. The RTSP connection drops during metadata exchange (`SET_PARAMETER` phase). **Cannot be fixed from the network side** — the device must be physically woken.

### Pairing Mandatory (Samsung TV)
```
pyatv.exceptions.PairingError: pairing is required
```
The TV displays a PIN on screen. Use `atvremote --id <ID> pair` to initiate pairing, then enter the PIN.

### Decode errors (remote MP3)
```
miniaudio.DecodeError: ('failed to init decoder', -1)
```
The `miniaudio` library couldn't decode the remote stream. Use a locally-generated WAV file instead (see `scripts/generate-tone-wav.py` in `network-device-recon` for a 440Hz test tone generator).

## Raw AirPlay RTSP (fallback, no pyatv)

```bash
# OPTIONS probe
printf "OPTIONS * RTSP/1.0\r\nCSeq: 1\r\n\r\n" | nc -w 2 $IP 7000
# Response: RTSP/1.0 200 OK + Public: methods list + Server: AirTunes/xxx.xx

# Device info (binary plist — pipe through strings)
curl -sk http://$IP:7000/info 2>&1 | strings | head -20
# Shows: model name, firmware version, manufacturer (e.g., "Bose Smart Soundbar 900")
# But is a binary plist, not human-readable without `strings`

# SETUP attempt (will fail if Deep Sleep)
printf "SETUP rtsp://$IP/1 RTSP/1.0\r\nCSeq: 1\r\nTransport: RTP/AVP/UDP;unicast;interleaved=0-1;mode=record\r\n\r\n" | nc -w 2 $IP 7000
# Deep Sleep response: "455 Method Not Valid In This State"
```
