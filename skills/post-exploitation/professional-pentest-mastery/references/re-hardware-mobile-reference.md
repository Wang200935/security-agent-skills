# Phase 1: Reverse Engineering + Hardware/IoT Hacking + Firmware Analysis + Mobile Security
## Comprehensive Research Reference Document

---

## Table of Contents
1. [Ghidra Workflows](#ghidra-workflows)
2. [IDA Pro Techniques](#ida-pro-techniques)
3. [radare2 & angr for Symbolic Execution](#radare2--angr-for-symbolic-execution)
4. [Firmware Extraction & Analysis](#firmware-extraction--analysis)
5. [Hardware Debugging (UART/JTAG/SPI/I2C)](#hardware-debugging-uartjtagspii2c)
6. [SDR/RFID/NFC/BLE/Zigbee Attacks](#sdfrfidnfcblezigbee-attacks)
7. [Android Security (Frida, Objection, APK Reversing)](#android-security)
8. [iOS Jailbreaking & Mobile Pentesting](#ios-jailbreaking--mobile-pentesting)
9. [Mobile Pentesting Methodology](#mobile-pentesting-methodology)

---

## Ghidra Workflows

### Core Ghidra Features
- **Decompiler**: Built-in decompiler supporting multiple architectures (x86, x64, ARM, ARM64, MIPS, PowerPC, etc.)
- **Scripting**: Java-based scripting API + Python via Pyhidra
- **Headless Mode**: Batch processing via `analyzeHeadless` command
- **Project Management**: Multi-user repositories, versioning
- **Extension System**: Ghidra extensions (GhidraDev for Eclipse)

### Decompilation Workflow
```bash
# Headless analysis
./analyzeHeadless <project_dir> <project_name> -import <binary> -postScript <script.java>

# GUI analysis
./ghidraRun
```

### Script Writing (Java API)
```java
// Example: Find all functions calling a specific API
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class FindCallers extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String targetFunc = "strcpy";
        Function target = getFunction(targetFunc);
        if (target == null) return;
        
        ReferenceIterator refs = target.getEntryPoint().getReferencesTo();
        while (refs.hasNext()) {
            Reference ref = refs.next();
            if (ref.getReferenceType().isCall()) {
                Function caller = getFunctionContaining(ref.getFromAddress());
                println(caller.getName() + " at " + ref.getFromAddress());
            }
        }
    }
}
```

### Pyhidra (Python API)
```python
# Install: pip install pyhidra
import pyhidra
pyhidra.start()

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

# Open program
from ghidra.program.flatapi import FlatProgramAPI
from ghidra.program.model.listing import Program

# Decompile function
def decompile_function(program, func_addr):
    iface = DecompInterface()
    iface.openProgram(program)
    func = program.getFunctionManager().getFunctionAt(func_addr)
    result = iface.decompileFunction(func, 30, ConsoleTaskMonitor())
    return result.getDecompiledFunction().getC()
```

### Useful Ghidra Scripts & Resources
- **GhidraScripts** (built-in): `FindCrypto`, `FunctionID`, `ExportSymbols`
- **Pyhidra notebooks**: Jupyter integration for interactive analysis
- **GhidraMCP**: MCP server for LLM integration
- **GhidraDocs**: https://github.com/NationalSecurityAgency/ghidra/tree/master/GhidraDocs

---

## IDA Pro Techniques

### Core Capabilities
- **Decompiler**: Hex-Rays decompiler (x86, x64, ARM, ARM64, MIPS, PPC)
- **IDAPython**: Python 3 API for automation
- **IDA Pro SDK**: C++ plugin development
- **Lumina**: Cloud-based function recognition
- **FLIRT**: Fast Library Identification and Recognition Technology

### IDAPython Essentials
```python
import idaapi
import idautils
import idc

# Iterate all functions
for func_ea in idautils.Functions():
    func_name = idc.get_func_name(func_ea)
    print(f"{func_name} @ 0x{func_ea:x}")

# Find cross-references to address
for xref in idautils.XrefsTo(0x401000):
    print(f"From: 0x{xref.frm:x} Type: {xref.type}")

# Decompile function
import ida_hexrays
if ida_hexrays.init_hexrays_plugin():
    cfunc = ida_hexrays.decompile(func_ea)
    print(str(cfunc))

# Rename function
idc.set_name(func_ea, "my_new_name", idaapi.SN_FORCE)

# Patch bytes
ida_bytes.patch_byte(ea, 0x90)  # NOP
```

### IDA Pro Plugins & Resources
- **IDA Pro Book** by Chris Eagle (No Starch Press)
- **Hex-Rays Decompiler SDK**: https://hex-rays.com/products/ida/support/sdk/
- **IDAPython docs**: https://hex-rays.com/products/ida/support/idapython_docs/
- **Lumina server**: Function signature sharing
- **FLIRT signatures**: Custom library recognition

---

## radare2 & angr for Symbolic Execution

### radare2 (r2) - UNIX-like RE Framework
**Key Resources**:
- Official book: https://book.rada.re/
- GitHub: https://github.com/radareorg/radare2
- r2pipe: Python/JS/Go bindings for scripting

#### Core Commands
```bash
# Start analysis
r2 -A binary          # Auto-analyze
r2 -d binary          # Debug mode
r2 -w binary          # Write mode

# Analysis commands
aaa                   # Analyze all (functions, refs, etc.)
afl                   # List functions
aflj                  # JSON output
pdf @ sym.main        # Disassemble function
pdd @ sym.main        # Decompile (r2dec/pseudo)
agf                   # Graph functions
afb                   # Basic blocks
afv                   # Function variables
```

#### Visual Mode
```
V                     # Visual mode
p/P                   # Cycle print modes (disasm, hex, etc.)
d/f                   # Define function/data
;                     # Add comment
:                     # Command mode
```

#### ESIL Emulation
```bash
aeim                  # Initialize ESIL VM
aeip                  # Set IP to current address
aesu 0x401000         # Emulate until address
aer                   # Show registers
aem                   # Show memory
```

#### r2pipe Scripting (Python)
```python
import r2pipe

r2 = r2pipe.open("./binary")
r2.cmd("aaa")  # Analyze all

# Get functions as JSON
funcs = r2.cmdj("aflj")
for f in funcs:
    print(f"{f['name']} @ 0x{f['offset']:x}")

# Decompile function
dec = r2.cmdj(f"pdj 50 @ {funcs[0]['offset']}")
```

#### R2Frida Integration
```bash
r2 frida://0          # Attach to PID 0 (system)
r2 frida://com.app    # Spawn/attach to Android app
r2 frida://usb//com.app  # USB device
```
Commands: `dm`, `dmi`, `db`, `ic`, `icj` (classes), `im` (methods)

---

### angr - Symbolic Execution Platform
**Documentation**: https://docs.angr.io/
**GitHub**: https://github.com/angr/angr

#### Core Concepts
- **Project**: Binary loading (CLE loader)
- **State**: CPU registers, memory, symbolic variables
- **SimulationManager**: Manages symbolic execution paths
- **Analyses**: CFG, VSA, Identifier, Decompiler

#### Installation
```bash
pip install angr
# Or via docker: docker run -it angr/angr
```

#### Basic Symbolic Execution
```python
import angr

proj = angr.Project("./binary", auto_load_libs=False)

# Create entry state
state = proj.factory.entry_state()

# Symbolic argument
argv1 = state.solver.BVS("argv1", 8 * 32)  # 32-byte symbolic arg
state.regs.rdi = argv1

# Simulation manager
simgr = proj.factory.simulation_manager(state)

# Explore to find target
simgr.explore(find=0x401234, avoid=0x401300)

if simgr.found:
    found = simgr.found[0]
    solution = found.solver.eval(argv1, cast_to=bytes)
    print(f"Input: {solution}")
```

#### CFG Recovery
```python
# Fast CFG
cfg = proj.analyses.CFGFast()

# Emulated CFG (more accurate)
cfg = proj.analyses.CFGEmulated()

# Visualize
import networkx as nx
nx.write_graphml(cfg.graph, "cfg.graphml")
```

#### Symbolic Memory & Constraints
```python
# Symbolic memory write
state.memory.store(state.regs.rsp, state.solver.BVS("stack_var", 64))

# Add constraints
state.solver.add(state.regs.rax == 0x1337)

# Check satisfiability
if state.satisfiable():
    print("Path is reachable")
    val = state.solver.eval(state.regs.rbx)
```

#### angr Analyses
```python
# Backward slicing
bs = proj.analyses.BackwardSlice(targets=[(target_addr, -1)])

# Identifier (library function recognition)
idfer = proj.analyses.Identifier()
print(idfer.run())

# Calling convention analysis
cc = proj.analyses.CallingConvention()
```

#### Cheatsheet Reference
- https://docs.angr.io/appendix/cheatsheet.html
- https://github.com/angr/angr-doc

---

## Firmware Extraction & Analysis

### binwalk - Firmware Analysis Tool
**GitHub**: https://github.com/ReFirmLabs/binwalk

#### Installation
```bash
# Ubuntu/Debian
sudo apt install binwalk

# From source
git clone https://github.com/ReFirmLabs/binwalk
cd binwalk
sudo python3 setup.py install

# Dependencies
sudo apt install squashfs-tools mtd-utils gzip bzip2 tar arj lhasa p7zip p7zip-full \
  cabextract cramfsprogs cramfsswap squashfs-tools-ng
```

#### Usage
```bash
# Scan for signatures
binwalk firmware.bin

# Extract all files
binwalk -e firmware.bin

# Extract specific filesystem
binwalk -e --run-as=root firmware.bin

# Verbose with offsets
binwalk -v firmware.bin

# Entropy analysis
binwalk -E firmware.bin

# Extract with custom signatures
binwalk --signature custom.sig -e firmware.bin
```

#### binwalk Modules
- **Signature scanning**: Magic bytes, filesystem headers, compression
- **Extraction**: Automatic filesystem extraction (squashfs, cramfs, jffs2, ubifs, yaffs2)
- **Entropy analysis**: Detect encryption/compression
- **Raw extraction**: `dd` carve files by offset

### flashrom - SPI/Flash Programming
**Website**: https://www.flashrom.org/Flashrom

#### Supported Programmers
```bash
# List programmers
flashrom -L

# Common programmers
flashrom -p ch341a_spi      # CH341A programmer
flashrom -p ft2232_spi      # FTDI FT2232
flashrom -p rayer_spi       # RayeR SPI
flashrom -p linux_spi       # Linux SPI kernel module
flashrom -p dummy           # Test mode
```

#### Reading/Writing Flash
```bash
# Read flash
flashrom -p ch341a_spi -r firmware_backup.bin

# Write flash
flashrom -p ch341a_spi -w firmware_new.bin

# Verify
flashrom -p ch341a_spi -v firmware_new.bin

# Erase
flashrom -p ch341a_spi -E
```

#### Chip Detection
```bash
flashrom -p ch341a_spi -c "MX25L6405"  # Specify chip
```

---

## Hardware Debugging (UART/JTAG/SPI/I2C)

### UART (Universal Asynchronous Receiver-Transmitter)
**Finding UART**:
- 3-4 pins: VCC, GND, TX, RX
- Use multimeter: GND=0V, VCC=3.3V/5V, TX=idle high, RX=floating
- Logic analyzer / oscilloscope for baud rate detection

**Tools**:
```bash
# Screen
screen /dev/ttyUSB0 115200

# Picocom
picocom -b 115200 /dev/ttyUSB0

# Minicom
minicom -D /dev/ttyUSB0 -b 115200

# Python
import serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
```

**Baud Rate Detection**:
- Common: 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600
- Use `baudrate.py` or logic analyzer

### JTAG (Joint Test Action Group)
**Finding JTAG**:
- 4-5 pins: TCK, TMS, TDI, TDO, (TRST)
- Use JTAGulator or manual probing

**Tools**:
```bash
# OpenOCD
openocd -f interface/ftdi/olimex-arm-usb-ocd-h.cfg \
        -f target/stm32f4x.cfg

# Connect via GDB
arm-none-eabi-gdb firmware.elf
(gdb) target remote localhost:3333
(gdb) monitor reset halt
(gdb) load
(gdb) continue
```

**JTAGenum / JTAGulator**: Automated pin discovery

### SWD (Serial Wire Debug)
- 2 pins: SWCLK, SWDIO
- ARM Cortex-M standard
- Same tools as JTAG (OpenOCD, J-Link, ST-Link)

### SPI (Serial Peripheral Interface) Flash
**Reading SPI Flash**:
```bash
# With flashrom
flashrom -p ch341a_spi -r dump.bin

# With Bus Pirate
# Flashrom supports buspirate_spi programmer
```

**In-Circuit Reading**:
- Power target OFF (or use 3.3V from programmer)
- Clip onto SOIC-8/SOIC-16 package
- Use SOIC clip or solder wires

### I2C
**Tools**:
```bash
# i2cdetect (Linux)
i2cdetect -y 1

# i2cdump
i2cdump -y 1 0x50

# Python
import smbus
bus = smbus.SMBus(1)
data = bus.read_i2c_block_data(0x50, 0, 256)
```

### Hardware Debugging Toolkit
| Tool | Purpose | Cost |
|------|---------|------|
| Bus Pirate | UART/SPI/I2C/JTAG | ~$30 |
| Shikra | High-speed SPI/I2C/JTAG | ~$60 |
| FT2232H Mini Module | USB to serial/JTAG | ~$15 |
| CH341A Programmer | SPI flash programming | ~$15 |
| Logic Analyzer (Saleae/DSLogic) | Protocol analysis | $100-500 |
| Oscilloscope | Signal analysis | $300+ |
| JTAGulator | JTAG/UART discovery | ~$100 |
| GreatFET One | USB/USB host/SPI/I2C | ~$60 |
| HydraBus | Multi-protocol tool | ~$60 |

---

## SDR/RFID/NFC/BLE/Zigbee Attacks

### SDR (Software Defined Radio)
**Hardware**:
- RTL-SDR (RTL2832U) - $25, 24-1766 MHz
- HackRF One - $300, 1 MHz - 6 GHz, TX/RX
- bladeRF - $400+, full duplex
- USRP (Ettus) - Professional grade

**Software**:
```bash
# GNU Radio Companion
gnuradio-companion

# GQRX (GUI spectrum analyzer)
gqrx

# rtl_433 (decode 433MHz devices)
rtl_433 -f 433.92M

# inspectrum (analyze recordings)
inspectrum capture.cfile

# Universal Radio Hacker
urh
```

### RFID/NFC
**Tools**:
```bash
# Proxmark3 (LF/HF RFID)
# Commands
lf search          # Find LF tags
hf search          # Find HF tags (NFC)
hf mf autopwn      # Mifare Classic attack
hf 14a list        # ISO14443-A tags

# libnfc / nfc-tools
nfc-list           # List tags
nfc-mfclassic      # Mifare Classic tools

# ChameleonMini / Flipper Zero
# Emulate tags, clone cards
```

**Attacks**:
- **Mifare Classic**: Nested authentication, darkside attack, static nested
- **Mifare Ultralight**: Password cracking, tear-off attack
- **NFC Relay**: Proxy attack between reader and card
- **UID Spoofing**: Clone UID on magic cards (Gen1a/Gen2)

### BLE (Bluetooth Low Energy)
**Tools**:
```bash
# gatttool (deprecated)
gatttool -b AA:BB:CC:DD:EE:FF -I

# bluetoothctl
bluetoothctl
[bluetooth]# scan on
[bluetooth]# connect AA:BB:CC:DD:EE:FF

# bettercap
bettercap -eval "ble.recon on; ble.enum AA:BB:CC:DD:EE:FF"

# btsnoop (Android)
# Wireshark with btusb/BT Snoop

# Nordic nRF Sniffer
# Wireshark plugin for BLE sniffing

# BlueZ DBus API (Python)
import dbus
bus = dbus.SystemBus()
```

**Attacks**:
- **Passive sniffing**: nRF Sniffer, Ubertooth One
- **Active MITM**: GATTacker, bleah
- **Pairing attacks**: Just Works, numeric comparison bypass
- **Key recovery**: CrackLE, btlejack
- **Fuzzing**: Bluff, BLEFuzz

### Zigbee / 802.15.4
**Hardware**:
- CC2531 USB dongle (flashed with sniffer firmware)
- TI CC2530/CC2538 dev kits
- KillerBee framework hardware

**Tools**:
```bash
# KillerBee
zbw_replay          # Replay captures
zbw_inject          # Inject packets
zbdsniff            # Sniff Zigbee

# Zigbee2MQTT (CC2531 coordinator)
# For sniffing: flash sniffer firmware

# Wireshark with Zigbee dissector
# Set encryption key in preferences
```

**Attacks**:
- **Key extraction**: Transport key, install codes
- **Replay attacks**: Command replay
- **Network join**: Permit join exploitation
- **Touchlink**: ZLL commissioning attack

---

## Android Security

### Frida - Dynamic Instrumentation
**Website**: https://frida.re/docs/home/
**GitHub**: https://github.com/frida/frida

#### Installation
```bash
# Host (Python)
pip install frida-tools

# Device
# 1. Root device / emulator
# 2. Push frida-server
adb push frida-server /data/local/tmp/
adb shell chmod +x /data/local/tmp/frida-server
adb shell /data/local/tmp/frida-server &

# Or use Magisk module: frida-server
```

#### Basic Usage
```bash
# List processes
frida-ps -U

# Spawn and attach
frida -U -f com.target.app -l script.js

# Attach to running
frida -U -n com.target.app -l script.js

# REPL
frida -U -n com.target.app
```

#### JavaScript API
```javascript
// Hook Java method
Java.perform(function() {
    var String = Java.use("java.lang.String");
    String.$init.overload("[C").implementation = function(c) {
        console.log("String created: " + this.toString());
        return this.$init(c);
    };
});

// Hook native function
Interceptor.attach(Module.findExportByName("libc.so", "strcpy"), {
    onEnter: function(args) {
        this.dst = args[0];
        this.src = args[1];
        console.log("strcpy(" + this.dst + ", " + Memory.readUtf8String(this.src) + ")");
    },
    onLeave: function(retval) {
        console.log("strcpy returned: " + retval);
    }
});

// Enum classes
Java.enumerateLoadedClasses({
    onMatch: function(className) {
        if (className.indexOf("crypto") !== -1) console.log(className);
    },
    onComplete: function() {}
});

// Call static method
Java.perform(function() {
    var Crypto = Java.use("javax.crypto.Cipher");
    var instance = Crypto.getInstance("AES/ECB/PKCS5Padding");
    console.log(instance.getAlgorithm());
});

// Bypass SSL pinning
Java.perform(function() {
    var TrustManager = Java.use("javax.net.ssl.TrustManager");
    var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    
    var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
    TrustManagerImpl.checkTrustedRecursive.implementation = function() {
        return;
    };
});
```

#### Frida Tools
```bash
# frida-trace - Auto-generate tracing scripts
frida-trace -U -f com.app -i "open*"

# frida-discover - Find interesting APIs
frida-discover -U com.app

# frida-ls-devices
frida-ls-devices
```

### Objection - Runtime Mobile Exploration
**GitHub**: https://github.com/sensepost/objection

#### Installation & Usage
```bash
pip install objection

# Connect to app
objection -g com.target.app explore

# Or with Frida gadget injection
objection --gadget="com.target.app" explore
```

#### Key Commands
```bash
# Storage
env                    # Show environment
ls                     # List files
cat <file>             # Read file
download <file>        # Download file

# Keystore/Keychain
ios_keychain_dump      # iOS
android_keystore_dump  # Android

# Hooking
hook_method -c "com.app.Class" -m "methodName"
watch_method -c "com.app.Class" -m "methodName"

# SSL Pinning Bypass
android sslpinning disable

# Crypto
android hooking watch class javax.crypto.Cipher

# Filesystem
android fs ls /
android fs cat /data/data/com.app/shared_prefs/prefs.xml

# Memory
memory dump 0x7b123000 1024
memory find "password"

# IPC
android intent send --action android.intent.action.VIEW --data "http://evil.com"
```

### APK Reversing

#### Tools
```bash
# apktool - Decode/rebuild APK
apktool d app.apk -o out_dir
apktool b out_dir -o new.apk

# jadx - Decompile to Java
jadx -d out_dir app.apk
jadx-gui app.apk

# dex2jar + JD-GUI
d2j-dex2jar.sh app.apk
# Open app-dex2jar.jar in JD-GUI

# smali/baksmali - Assembly
baksmali d classes.dex -o smali_out
smali a smali_out -o classes.dex

# Ghidra - Analyze native libs
# Import lib/arm64-v8a/libnative.so

# Android Studio - Debug
# Attach debugger to debuggable app
```

#### APK Structure
```
app.apk
├── AndroidManifest.xml (binary XML)
├── classes.dex (Dalvik bytecode)
├── classes2.dex (multidex)
├── resources.arsc (compiled resources)
├── res/ (resources)
├── assets/ (raw assets)
├── lib/
│   ├── arm64-v8a/libnative.so
│   ├── armeabi-v7a/libnative.so
│   └── x86_64/libnative.so
├── META-INF/
│   ├── MANIFEST.MF
│   ├── CERT.RSA
│   └── CERT.SF
```

#### Manifest Analysis
```bash
# aapt2
aapt2 dump badging app.apk

# apktool manifest
cat out_dir/AndroidManifest.xml
```

#### Native Library Analysis
```bash
# Find JNI functions
strings libnative.so | grep Java_

# Ghidra: Import .so, analyze JNI_OnLoad
# Look for RegisterNatives calls

# frida-trace native
frida-trace -U -f com.app -I "libnative.so" -i "*"
```

### Android Kernel Security
- **SELinux**: Enforcing mode, policies in `/sys/fs/selinux/policy`
- **Seccomp**: Syscall filtering
- **KASLR/KPTI**: Kernel address space layout randomization
- **Hardening**: `CONFIG_DEBUG_RODATA`, `CONFIG_DEBUG_SET_MODULE_RONX`
- **Root detection**: MagiskHide, Zygisk, Shamiko

---

## iOS Jailbreaking & Mobile Pentesting

### iOS Jailbreak Status (2024-2025)
| iOS Version | Jailbreak Tool | Type |
|-------------|----------------|------|
| 15.0-15.4.1 | palera1n | Semi-tethered (checkm8) |
| 15.0-16.5 | Dopamine | Semi-untethered |
| 16.0-16.6.1 | palera1n | Semi-tethered |
| 17.0-17.x | palera1n (rootless) | Semi-tethered |
| 18.x | TBD | Research ongoing |

**Key Tools**:
- **palera1n**: checkm8-based, supports A8-A11 (iPhone 6s-X)
- **Dopamine**: Semi-untethered, A12+ devices
- **Bootstrap**: SSH, apt, basic tools
- **Sileo/Zebra**: Package managers

### Frida on iOS
```bash
# With jailbreak
# Install Frida via Cydia/Sileo
# Or inject Frida gadget

# Frida gadget injection
objection --gadget="com.target.app" explore

# Or use frida-ios-dump for decrypted IPA
```

### iOS Reverse Engineering Tools
```bash
# class-dump - Objective-C headers
class-dump -H /Applications/App.app/App

# Hopper Disassembler - Commercial, great for iOS
# IDA Pro - With iOS SDK signatures

# otool - Object file tools
otool -l App              # Load commands
otool -ov App             # Objective-C info
otool -arch arm64 -V App  # Disassemble

# dyld_shared_cache_extractor
# Extract libraries from shared cache

# ipsw - Download/extract iOS firmware
go install github.com/blacktop/ipsw@latest
ipsw download 17.0 --device iPhone15,2
ipsw extract kernel.ipsw
```

### iOS App Analysis
```bash
# Decrypt App Store binary (requires jailbreak)
frida-ios-dump -U com.target.app

# Class dump
class-dump decrypted_app -H headers/

# Cycript - Runtime manipulation (deprecated, use Frida)
# cycript -p SpringBoard

# Passionfruit - iOS app analysis GUI
# https://github.com/chenan/passionfruit
```

### iOS Security Mechanisms
- **Code Signing**: All binaries must be signed
- **Entitlements**: Capabilities (keychain, push, etc.)
- **App Sandbox**: Container at `/var/mobile/Containers/Data/Application/`
- **Keychain**: Hardware-backed (Secure Enclave)
- **Face ID/Touch ID**: LocalAuthentication framework
- **App Transport Security (ATS)**: Enforced HTTPS
- **Pointer Authentication (PAC)**: ARMv8.3+ (A12+)

---

## Mobile Pentesting Methodology

### 1. Reconnaissance
```bash
# App info
aapt2 dump badging app.apk
# Bundle ID, version, permissions, activities, services, receivers, providers

# Network traffic
# Burp Suite + ProxyDroid / Proxy settings
# mitmproxy
mitmweb --mode transparent --showhost

# Static analysis
jadx-gui app.apk
# Look for: hardcoded keys, API endpoints, crypto constants
```

### 2. Static Analysis Checklist
- [ ] **Manifest**: Exported components, permissions, debuggable flag, backup allow
- [ ] **Network**: HTTP vs HTTPS, certificate pinning, cleartext traffic
- [ ] **Storage**: SharedPreferences, SQLite, files, keystore usage
- [ ] **Crypto**: Hardcoded keys, weak algorithms (ECB, DES, MD5), IV reuse
- [ ] **Native**: JNI functions, stripped symbols, anti-debug
- [ ] **IPC**: Intent filters, content providers, exported services
- [ ] **WebViews**: JS enabled, file access, universal links
- [ ] **Logging**: Sensitive data in logs

### 3. Dynamic Analysis
```bash
# Frida scripts for common checks
# SSL pinning bypass
frida -U -f com.app -l bypass_ssl.js

# Root detection bypass
frida -U -f com.app -l bypass_root.js

# Crypto tracing
frida -U -f com.app -l trace_crypto.js

# File access monitoring
frida -U -f com.app -l trace_file.js
```

### 4. Network Testing
- **MITM**: Burp Suite, mitmproxy, OWASP ZAP
- **Certificate Pinning**: Frida/Objection bypass
- **API Testing**: Swagger/OpenAPI spec extraction, fuzzing
- **Traffic Analysis**: PCAP capture, protocol reverse engineering

### 5. Platform-Specific Tests

#### Android
- **Intent/Activity hijacking**: Exported activities with malicious data
- **Content Provider SQLi**: Query injection via content:// URIs
- **Broadcast Receiver**: Ordered broadcasts, permission bypass
- **Service Hijacking**: Exported services
- **Parcelable/Serializable**: Deserialization attacks
- **WebView**: File:// access, JS interfaces, universal links
- **Backup**: `adb backup` extraction
- **Keystore**: Key extraction (if weak)

#### iOS
- **Keychain**: Data protection classes, accessibility
- **Pasteboard**: Sensitive data leakage
- **URL Schemes**: Custom scheme handling, openURL
- **Universal Links**: Associated domains, apple-app-site-association
- **App Groups**: Shared container data
- **Background Snapshots**: Sensitive UI in app switcher
- **Analytics/Crash Reporting**: PII leakage

### 6. Reporting
- **CVSS Scoring**: For each finding
- **POC**: Frida scripts, curl commands, screenshots
- **Remediation**: Code snippets, config changes
- **Retest**: Verification steps

---

## Key Resources & References

### Books
- "Practical Reverse Engineering" - Dang, Gazet, Bachaalany
- "The IDA Pro Book" - Chris Eagle
- "Practical Binary Analysis" - Dennis Andriesse
- "Android Security Internals" - Nikolay Elenkov
- "iOS Application Security" - David Thiel
- "The Hardware Hacker" - Andrew "bunnie" Huang
- "Practical Hardware Pentesting" - Fotios Chantzis

### Training Platforms
- **Pwn.college** - ASU systems security
- **HackTheBox** - RE, Hardware, Mobile tracks
- **TryHackMe** - Mobile security rooms
- **OverTheWire** - Microcorruption (embedded)
- **Damn Vulnerable iOS App (DVIA)**
- **OWASP MASVS/MASTG** - Mobile security testing guide

### CTF Practice
- **Pwnable.kr** - Binary exploitation
- **IO.smashthestack.org** - Wargames
- **Microcorruption** - Embedded (MSP430)
- **Reversing.kr** - Windows/Reverse engineering

### Conferences & Communities
- **REcon** - Reverse engineering
- **Black Hat / DEFCON** - Security research
- **r2con** - radare2 conference
- **Frida.re** - Frida community
- **/r/ReverseEngineering**, **/r/pwned**, **/r/netsec**

### Essential GitHub Repos
```
Ghidra:          https://github.com/NationalSecurityAgency/ghidra
radare2:         https://github.com/radareorg/radare2
angr:            https://github.com/angr/angr
Frida:           https://github.com/frida/frida
Objection:       https://github.com/sensepost/objection
binwalk:         https://github.com/ReFirmLabs/binwalk
flashrom:        https://github.com/flashrom/flashrom
Proxmark3:       https://github.com/RfidResearchGroup/proxmark3
KillerBee:       https://github.com/riverloopsec/killerbee
Ubertooth:       https://github.com/greatscottgadgets/ubertooth
rtl_433:         https://github.com/merbanan/rtl_433
MobileSecurity:  https://github.com/OWASP/owasp-mastg
```

---

*Document compiled: July 2025*
*Target path: /Users/wang/security-research/phase1-re-hardware-mobile.md*