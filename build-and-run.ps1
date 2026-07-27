# CareerForge AI — Build & Launch
# Run this script from the project root, or double-click it.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "=== CareerForge AI — Build & Launch ===" -ForegroundColor Cyan
Write-Host ""

# ---- 1. Node / npm check ----
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: node is not installed or not in PATH." -ForegroundColor Red
    exit 1
}
Write-Host "[1/4] node $(node --version) found" -ForegroundColor Gray

# ---- 2. Rust / Cargo check ----
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Rust toolchain is not installed." -ForegroundColor Red
    Write-Host "Install it from https://rustup.rs/" -ForegroundColor Yellow
    exit 1
}
Write-Host "[2/4] cargo $(cargo --version) found" -ForegroundColor Gray

# ---- 3. Install npm deps & build frontend ----
Write-Host "[3/4] Installing npm dependencies..." -ForegroundColor Gray
npm install --no-audit 2>$null | Out-Null

Write-Host "       Building frontend (vite)..." -ForegroundColor Gray
npm run build 2>$null | Out-Null

if (-not (Test-Path "dist\index.html")) {
    Write-Host "ERROR: dist/index.html not found after npm run build." -ForegroundColor Red
    exit 1
}
Write-Host "       Frontend build OK" -ForegroundColor Gray

# ---- 4. Build & launch via Tauri CLI ----
Write-Host "[4/4] Building Tauri app (npx tauri build)..." -ForegroundColor Gray
Write-Host "       This may take several minutes on first run." -ForegroundColor Gray
Write-Host ""

# Prefer npx tauri (uses @tauri-apps/cli already in devDependencies).
# Fall back to cargo tauri if cargo-tauri subcommand is installed.
$tauriCmd = $null
if (Get-Command cargo -ErrorAction SilentlyContinue) {
    cargo tauri --version 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $tauriCmd = "cargo tauri"
    }
}
if (-not $tauriCmd) {
    $tauriCmd = "npx tauri"
}

Write-Host "       Using: $tauriCmd" -ForegroundColor DarkGray
Invoke-Expression "$tauriCmd build" 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed (exit code $exitCode)." -ForegroundColor Red
    Write-Host "Check the error output above for details." -ForegroundColor Yellow
    exit $exitCode
}

# ---- 5. Locate & launch the built exe ----
$exePath = Join-Path $PSScriptRoot "src-tauri\target\release\careerforge-ai.exe"

if (-not (Test-Path $exePath)) {
    Write-Host ""
    Write-Host "Build completed but exe not found at expected path:" -ForegroundColor Yellow
    Write-Host "  $exePath" -ForegroundColor Yellow
    Write-Host ""
    # Try to find it
    $found = Get-ChildItem "src-tauri\target\release\*.exe" -ErrorAction SilentlyContinue |
             Where-Object { $_.Name -ne "careerforge-ai.pdb" } |
             Select-Object -First 1
    if ($found) {
        $exePath = $found.FullName
        Write-Host "Found: $exePath" -ForegroundColor Green
    } else {
        Write-Host "No exe found in src-tauri\target\release\" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Launching CareerForge AI..." -ForegroundColor Cyan
Start-Process $exePath
Write-Host "Done — the app window should appear shortly." -ForegroundColor Green
