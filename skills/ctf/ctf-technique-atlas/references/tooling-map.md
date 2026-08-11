# CTF Tooling Map

Prefer reproducible CLI/scripts. GUI tools are useful for inspection but final solves should be scriptable where possible.

## Universal

- `file`, `stat`, `sha256sum`, `xxd`, `strings`
- `python3`, `ipython`, `jq`
- `Docker` for challenge-provided environments
- `~/homebrew/bin/brew` on Wang's macOS when installing tools

## Web

- `curl` for exact HTTP
- Python `requests`, `beautifulsoup4`
- Browser devtools / CUA browser automation for JS-heavy apps
- `sqlmap` only when allowed and after manual understanding
- `jwt_tool`, `pyjwt`, `flask-unsign`, `itsdangerous`
- Local webhook receiver for XSS/admin-bot labs

## Crypto

- Python: `pycryptodome`, `gmpy2`, `sympy`, `z3-solver`, `pwntools`
- SageMath for lattices, ECC, polynomial rings, Coppersmith-style attacks
- `openssl asn1parse` for cert/PEM/ASN.1
- Factordb-like lookups only for CTF/public moduli, not real secrets

## Forensics

- `exiftool`, `binwalk`, `foremost`, `7z`
- Images: `pngcheck`, Pillow, `zbar`, `stego-lsb`
- PCAP: Wireshark/tshark, Scapy
- Memory: `volatility3`
- Disk: Sleuth Kit tools where available
- Docs: `oletools`, `pdfimages`, `qpdf`, `mutool`
- Audio: spectrogram tooling, `ffmpeg`, Python scipy/matplotlib

## Reverse engineering

- `Ghidra`, `radare2`/`rizin`, `objdump`, `nm`, `otool`
- `jadx`, `apktool` for APK
- `wasm2wat` / wabt for WASM
- Python: `z3-solver`, `angr`, `capstone`, `unicorn`, `lief`
- `lldb` on macOS; Linux container/VM when binary behavior depends on glibc

## Pwn

- Python `pwntools`
- `checksec`, `ROPgadget`, `ropper`, `one_gadget`
- Linux/Docker for faithful exploitation
- `gdb` + gef/pwndbg where available
- `seccomp-tools` for syscall filters
- `patchelf` to bind libc/ld in Linux environments

## Misc/Jail

- Python `pwntools`, `z3-solver`, `requests`, Pillow, `pyzbar`
- `jq`, `zbar`, `ffmpeg`
- Custom scripts for encodings, parser states, game solvers

## OSINT

- Web search/browser
- Metadata tools: `exiftool`
- Maps/geocoding skills/tools
- DNS/cert transparency/archives where relevant

## Mobile

- `jadx`, `apktool`, `adb` where an Android environment exists
- Frida/objection for dynamic labs when needed
- SQLite tools for local stores
- Ghidra for native libraries

## Cloud

- Provider CLIs only in isolated/authorized lab contexts
- `jq` for policy JSON
- SSRF metadata tests only against CTF/lab targets
- Kubernetes tools (`kubectl`) only if a lab kubeconfig/context is provided

## Blockchain

- Foundry (`cast`, `forge`) or Hardhat/ethers.js
- ABI decoders
- Python web3 where convenient
- Storage slot calculators and event log decoders

## Hardware/RF/ICS

- `binwalk`, `strings`, filesystem extractors for firmware
- Sigrok/PulseView for logic traces
- GNU Radio/inspectrum-style tooling for RF where available
- Wireshark dissectors for Modbus/CAN/ICS protocols

## AI/ML

- Python safe loaders/inspectors for ONNX/Torch state dicts
- Never blindly `pickle.load` untrusted files; inspect with safer static methods first
- Gradient-free search scripts for black-box classifiers
