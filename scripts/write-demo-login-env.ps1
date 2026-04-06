# Merges NEXT_PUBLIC_DEMO_* from demo-account.env into .env.local (creates or updates lines).
# Usage: .\scripts\write-demo-login-env.ps1
#        .\scripts\write-demo-login-env.ps1 -Email "a@b.com" -Password "secret"

param(
    [string]$Email,
    [string]$Password
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$demoFile = Join-Path $root "demo-account.env"
$exampleFile = Join-Path $root "demo-account.env.example"
$localEnv = Join-Path $root ".env.local"

function Read-DemoAccountFile {
    param([string]$Path)
    $e = $null
    $p = $null
    foreach ($raw in Get-Content $Path) {
        $line = $raw.Trim()
        if ($line -match '^\s*#' -or $line -eq "") { continue }
        if ($line -match '^\s*NEXT_PUBLIC_DEMO_EMAIL=(.+)$') { $e = $matches[1].Trim().Trim('"') }
        if ($line -match '^\s*NEXT_PUBLIC_DEMO_PASSWORD=(.+)$') { $p = $matches[1].Trim().Trim('"') }
    }
    return @{ Email = $e; Password = $p }
}

if (-not $Email -or -not $Password) {
    if (-not (Test-Path $demoFile)) {
        Copy-Item $exampleFile $demoFile
        Write-Host "Created demo-account.env from demo-account.env.example"
        Write-Host "Edit demo-account.env with your demo email and password, then run this script again."
        exit 0
    }
    $parsed = Read-DemoAccountFile $demoFile
    if (-not $Email) { $Email = $parsed.Email }
    if (-not $Password) { $Password = $parsed.Password }
}

if (-not $Email -or -not $Password) {
    Write-Error "Missing NEXT_PUBLIC_DEMO_EMAIL or NEXT_PUBLIC_DEMO_PASSWORD. Fill demo-account.env or pass -Email and -Password."
    exit 1
}

if ($Email -eq "you@example.com" -or $Password -eq "your_password_here") {
    Write-Error "Replace placeholder values in demo-account.env with your real demo user (email + password)."
    exit 1
}

$lines = @()
if (Test-Path $localEnv) {
    $lines = @(Get-Content $localEnv | Where-Object {
        $_ -notmatch '^\s*NEXT_PUBLIC_DEMO_EMAIL=' -and $_ -notmatch '^\s*NEXT_PUBLIC_DEMO_PASSWORD='
    })
}
$merged = New-Object System.Collections.ArrayList
foreach ($l in $lines) { [void]$merged.Add($l) }
if ($merged.Count -gt 0 -and $merged[-1].Trim() -ne "") { [void]$merged.Add("") }
[void]$merged.Add("# Demo login banner (from scripts/write-demo-login-env.ps1)")
[void]$merged.Add("NEXT_PUBLIC_DEMO_EMAIL=$Email")
[void]$merged.Add("NEXT_PUBLIC_DEMO_PASSWORD=$Password")
Set-Content -Path $localEnv -Value $merged -Encoding utf8
Write-Host "Updated $localEnv with NEXT_PUBLIC_DEMO_* (restart next dev if running)."
