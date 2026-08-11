<#>
.SYNOPSIS
    Force bind a USB smart card reader to the Alcor SZCCID driver
    Use when Windows binds reader to Microsoft CCID (WUDFRd) instead

.NOTES
    Requires: Administrator PowerShell
    Target: Pincop ICU02 (VID_2CE3 PID_9563) or similar rebranded Alcor readers
    Pre-requisite: Alcor SZCCID driver already installed (oem58.inf)

    SECURE BOOT NOTE:
    If Secure Boot is enabled, this script WILL NOT WORK because
    Windows PnP will always prefer the signed Microsoft CCID driver.
    Solution: Disable Secure Boot in UEFI/BIOS, OR buy a reader with
    native WHQL driver (ACS ACR38U).
#>

param(
    [string]$VID = "2CE3",
    [string]$PID = "9563",
    [string]$InstanceID = "5&3639e268&0&4"  # Find with: pnputil /enum-devices | findstr 2CE3
)

Write-Host "=== Force Bind to SZCCID Driver ===" -ForegroundColor Cyan
Write-Host "Target: VID=$VID PID=$PID Instance=$InstanceID" -ForegroundColor Yellow

# 1. Find the device
$devicePath = "HKLM:\SYSTEM\CurrentControlSet\Enum\USB\VID_$VID&PID_$PID\$InstanceID"
if (-not (Test-Path $devicePath)) {
    Write-Host "ERROR: Device not found at $devicePath" -ForegroundColor Red
    Write-Host "Run: pnputil /enum-devices | findstr $VID" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found device: $devicePath" -ForegroundColor Green

# 2. Check current binding
$currentService = (Get-ItemProperty $devicePath).Service
Write-Host "Current Service: $currentService" -ForegroundColor Yellow

if ($currentService -eq "SzCCID") {
    Write-Host "Already bound to SZCCID!" -ForegroundColor Green
    exit 0
}

# 3. Get SZCCID driver key
$szccidClass = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{50DD5230-BA8A-11D1-BF5D-0000F805F530}"
$driverKey = Get-ChildItem $szccidClass | Where-Object {
    (Get-ItemProperty $_.PSPath).ProviderName -like "*AlcorMicro*"
}
if (-not $driverKey) {
    Write-Host "ERROR: Alcor SZCCID driver not found in class {50DD5230-BA8A-11D1-BF5D-0000F805F530}" -ForegroundColor Red
    Write-Host "Run: pnputil /enum-drivers /class {50DD5230-BA8A-11D1-BF5D-0000F805F530}" -ForegroundColor Yellow
    exit 1
}

$driverDesc = (Get-ItemProperty $driverKey.PSPath).DriverDesc
$driverVersion = (Get-ItemProperty $driverKey.PSPath).DriverVersion
Write-Host "SZCCID Driver: $driverDesc v$driverVersion" -ForegroundColor Green

# 4. Disable device (prevents PnP re-enumeration override)
Write-Host "Disabling device..." -ForegroundColor Yellow
pnputil /disable-device "USB\VID_$VID&PID_$PID\$InstanceID" 2>&1 | Out-Null
Start-Sleep -Seconds 2

# 5. Modify registry to point to SZCCID
Write-Host "Setting Service=SzCCID..." -ForegroundColor Yellow
Set-ItemProperty -Path $devicePath -Name "Service" -Value "SzCCID" -Force

# Remove WUDF lower filters if present
$lowerFilters = (Get-ItemProperty $devicePath -Name "LowerFilters" -ErrorAction SilentlyContinue).LowerFilters
if ($lowerFilters -and $lowerFilters -contains "WUDFRd") {
    $newFilters = $lowerFilters | Where-Object { $_ -ne "WUDFRd" }
    if ($newFilters.Count -eq 0) {
        Remove-ItemProperty -Path $devicePath -Name "LowerFilters" -ErrorAction SilentlyContinue
    } else {
        Set-ItemProperty -Path $devicePath -Name "LowerFilters" -Value $newFilters -Force
    }
    Write-Host "Removed WUDFRd from LowerFilters" -ForegroundColor Green
}

# Remove WUDF Device Parameters (cleanup)
$wudfPath = "$devicePath\Device Parameters\WUDF"
if (Test-Path $wudfPath) {
    Remove-Item $wudfPath -Recurse -Force
    Write-Host "Removed WUDF Device Parameters" -ForegroundColor Green
}

# 6. Re-enable device
Write-Host "Re-enabling device..." -ForegroundColor Yellow
pnputil /enable-device "USB\VID_$VID&PID_$PID\$InstanceID" 2>&1 | Out-Null
Start-Sleep -Seconds 3

# 7. Verify
$newService = (Get-ItemProperty $devicePath).Service
Write-Host "New Service: $newService" -ForegroundColor Yellow

if ($newService -eq "SzCCID") {
    Write-Host "SUCCESS: Device bound to SZCCID!" -ForegroundColor Green
    
    # Restart smart card service
    Write-Host "Restarting Smart Card service..." -ForegroundColor Yellow
    Restart-Service -Name SCardSvr -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    Write-Host "`nNow test with 32-bit Python + CTAlc001.dll:" -ForegroundColor Cyan
    Write-Host "  C:\Python311-32\python.exe test_ctapi_sle4442.py" -ForegroundColor Gray
} else {
    Write-Host "FAILED: PnP re-bound to $newService" -ForegroundColor Red
    Write-Host "This is expected with Secure Boot enabled." -ForegroundColor Yellow
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  1. Disable Secure Boot in BIOS -> reboot -> run this script again" -ForegroundColor Gray
    Write-Host "  2. Buy ACS ACR38U (VID_072B:021C) - native WHQL driver" -ForegroundColor Gray
    Write-Host "  3. Buy Alcor AU9540 with original VID (058F:9540)" -ForegroundColor Gray
}

Write-Host "`nCurrent device status:"
pnputil /enum-devices /instanceid "USB\VID_$VID&PID_$PID\$InstanceID" 2>&1