# Windows VPN Removal (Tailscale + WireGuard)

Step-by-step procedure for removing Tailscale (complete uninstall) and disabling WireGuard (stop + disable) on a Windows machine via SSH from macOS.

## Prerequisites

- SSH to Windows configured in `~/.ssh/config` (e.g. `Host win → 192.168.68.x, User ellis`)
- Windows OpenSSH Server running
- Commands use CMD syntax (not PowerShell) where possible — PowerShell output encoding over SSH is unreliable for Traditional Chinese Windows

## Tailscale Complete Removal

### Step 1: Stop services + kill processes

```bash
ssh win "net stop Tailscale 2>&1 & sc config Tailscale start= disabled 2>&1 & sc query Tailscale 2>&1"
```

Also stop `TailscaleIPN` if it exists (service name may vary — check with `sc query type= service state= all | findstr /I tailscale`):

```bash
ssh win "sc query type= service state= all | findstr /I tailscale 2>&1"
```

Kill the GUI process:

```bash
ssh win "taskkill /F /IM tailscale-ipn.exe 2>&1 & taskkill /F /IM tailscaled.exe 2>&1"
```

### Step 2: MSI silent uninstall

Find the MSI product GUID from registry:

```bash
ssh win "powershell -Command \"Get-ItemProperty 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' -ErrorAction SilentlyContinue | Where-Object { \$_.DisplayName -match 'Tailscale' } | Select-Object DisplayName,UninstallString | Format-List\""
```

Example output:
```
DisplayName     : Tailscale
UninstallString : MsiExec.exe /X{F4BE7A91-41C3-512C-85BF-CC0A4A2A8791}
```

Execute silent uninstall:

```bash
ssh win "msiexec /x {F4BE7A91-41C3-512C-85BF-CC0A4A2A8791} /qn /norestart 2>&1"
# Exit code 0 = success
```

### Step 3: Clean residual files + registry

```bash
ssh win "rmdir /s /q \"C:\Program Files\Tailscale\" & rmdir /s /q \"C:\ProgramData\Tailscale\" & rmdir /s /q \"%LOCALAPPDATA%\Tailscale\" & rmdir /s /q \"%APPDATA%\Tailscale\" & reg delete HKLM\SOFTWARE\Tailscale /f & reg delete HKCU\SOFTWARE\Tailscale /f & reg delete \"HKLM\SYSTEM\CurrentControlSet\Services\Tailscale\" /f & reg delete \"HKLM\SYSTEM\CurrentControlSet\Services\TailscaleIPN\" /f & echo CLEANUP_DONE"
```

Running it twice confirms removal (second run says "system cannot find the file specified").

### Step 4: Verify

```bash
# No service
ssh win "sc query Tailscale 2>&1"
# Expected: "The specified service does not exist as an installed service" (error 1060)

# No process
ssh win "tasklist | findstr /I tailscale 2>&1"
# Expected: empty output

# No uninstall entry
ssh win "powershell -Command \"Get-ItemProperty 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' | Where-Object { \$_.DisplayName -match 'Tailscale' }\""
# Expected: empty output

# No network adapter
ssh win "powershell -Command \"Get-NetAdapter | Where-Object { \$_.InterfaceDescription -match 'Tailscale' }\""
# Expected: empty output
```

## WireGuard Disable (not full uninstall)

WireGuard on Windows runs as a service called `WireGuardManager`. To stop it:

```bash
ssh win "net stop WireGuardManager 2>&1 & sc config WireGuardManager start= disabled 2>&1 & sc query WireGuardManager 2>&1"
```

Kill the GUI process:

```bash
ssh win "taskkill /F /IM wireguard.exe 2>&1"
```

**To re-enable later** (if user wants WireGuard back):
```bash
ssh win "sc config WireGuardManager start= auto & net start WireGuardManager"
```

**For full uninstall**: WireGuard Manager has its own uninstaller in Add/Remove Programs — find it the same way as Tailscale (registry uninstall entry → `msiexec /x {GUID} /qn`).

## Pitfalls

- **PowerShell output over SSH to macOS is unreliable for CJK Windows** — `chcp 65001` helps but doesn't fix all encoding issues. Prefer CMD (`net stop`, `sc config`, `taskkill`) over PowerShell cmdlets when the output matters. Use PowerShell only for queries (`Get-Process`, `Get-NetAdapter`) where you're parsing structured output.
- **Tailscale service name may be just `Tailscale` not `TailscaleService`** — always check with `sc query type= service state= all | findstr /I tailscale` first.
- **`net stop` returns exit code 36 even on success** — the Chinese localization of Windows returns non-standard exit codes. Don't rely on `$?` — check `sc query` output for `STATE : 1 STOPPED`.
- **`tailscaled.exe` may not be running as a separate process** — on Windows, Tailscale runs as a system service, not a user process. `taskkill /F /IM tailscaled.exe` may return "process not found" — that's fine, the service stop already killed it.
- **VMware/WSL virtual adapters remain after VPN removal** — these also contribute to interface count and jitter. Disable them separately:
  ```bash
  ssh win "powershell -Command \"Disable-NetAdapter -Name 'VMware Network Adapter VMnet1' -Confirm:\$false; Disable-NetAdapter -Name 'VMware Network Adapter VMnet8' -Confirm:\$false\""
  ```
- **After VPN removal, the first few pings may be 200-400ms** — this is the network stack resetting. Wait 10-20 seconds and re-ping for steady-state numbers.
