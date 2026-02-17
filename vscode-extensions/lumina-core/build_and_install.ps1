# Lumina Core - BDA: Build, Deploy, Activate
# #automation: single entry point. Run from repo root or from vscode-extensions/lumina-core.
# Circle back: docs/system/LUMINA_EXTENSION_BDA.md
# cspell:ignore LASTEXITCODE

param(
    [switch]$NoVersionBump  # Set to skip incrementing version (e.g. for dry run)
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Smart bump: don't bump if last bump was within this many seconds (e.g. two tiny changes in quick succession).
$BumpCooldownSeconds = 600   # 10 minutes

$pkgPath = Join-Path $ScriptDir "package.json"
$bumpStatePath = Join-Path $ScriptDir ".last_bda_bump.json"
$pkg = Get-Content $pkgPath -Raw | ConvertFrom-Json

# --- VERSION BUMP (smart: bump only if last bump was > 10 min ago, else keep version) ---
$nowUtc = [DateTime]::UtcNow
$doBump = $false
if ($NoVersionBump) {
    $doBump = $false
} else {
    if (Test-Path $bumpStatePath) {
        try {
            $state = Get-Content $bumpStatePath -Raw | ConvertFrom-Json
            $lastUtc = [DateTime]::Parse($state.timestamp_utc, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind)
            $elapsed = ($nowUtc - $lastUtc).TotalSeconds
            if ($elapsed -ge $BumpCooldownSeconds) {
                $doBump = $true
            } else {
                Write-Host "[BDA] VERSION: keeping $($pkg.version) (last bump was $([math]::Floor($elapsed))s ago; cooldown ${BumpCooldownSeconds}s)" -ForegroundColor Yellow
            }
        } catch {
            $doBump = $true
        }
    } else {
        $doBump = $true
    }
}

if ($doBump) {
    $parts = $pkg.version -split '\.'
    $patch = [int]$parts[2] + 1
    $newVer = "$($parts[0]).$($parts[1]).$patch"
    $oldVer = $pkg.version
    $pattern = '"version"\s*:\s*"' + [regex]::Escape($oldVer) + '"'
    $replacement = '"version": "' + $newVer + '"'
    (Get-Content $pkgPath -Raw) -replace $pattern, $replacement | Set-Content $pkgPath -NoNewline
    Write-Host "[BDA] VERSION: $oldVer -> $newVer (bumped patch)" -ForegroundColor Cyan
    $pkg = Get-Content $pkgPath -Raw | ConvertFrom-Json
    # Remember when we bumped so rapid BDAs within 10 min don't bump again
    @{ version = $pkg.version; timestamp_utc = $nowUtc.ToString("o") } | ConvertTo-Json | Set-Content $bumpStatePath -NoNewline
}

$ver = $pkg.version

# --- BUILD ---
# Version = package.json. Each BDA increments patch unless -NoVersionBump. See docs/system/VERSION_CONTROL_POLICY.md
Write-Host "[BDA] BUILD: compile + package VSIX (version $ver)" -ForegroundColor Cyan
npm run compile
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
npx vsce package
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$name = $pkg.name
$vsix = Join-Path $ScriptDir "$name-$ver.vsix"
if (-not (Test-Path $vsix)) {
    $fallback = Get-ChildItem -Path $ScriptDir -Filter "*.vsix" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($fallback) {
        $vsix = $fallback.FullName
        Write-Host "[BDA] Using latest VSIX: $vsix" -ForegroundColor Yellow
    } else {
        Write-Error "VSIX not found: $vsix (and no *.vsix in directory)"
        exit 1
    }
}

# --- DEPLOY ---
$cursorCmd = "C:\Program Files\cursor\resources\app\bin\cursor.cmd"
if (-not (Test-Path $cursorCmd)) {
    Write-Host "[BDA] DEPLOY: Cursor CLI not found. Install manually: cursor --install-extension `"$vsix`" --force" -ForegroundColor Yellow
    exit 0
}
Write-Host "[BDA] DEPLOY: install extension into Cursor" -ForegroundColor Cyan
& $cursorCmd --install-extension $vsix --force
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# --- ACTIVATE ---
Write-Host "[BDA] ACTIVATE: Reload Cursor window (Developer: Reload Window) to activate." -ForegroundColor Green
