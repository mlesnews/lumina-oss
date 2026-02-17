# Lumina Voice Actor Service Startup Script
# Start the unified voice synthesis/recognition service

$ErrorActionPreference = "Stop"
$ServiceDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting Lumina Voice Actor Service..." -ForegroundColor Cyan

# Check if virtual environment exists
$VenvPath = Join-Path $ServiceDir "venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvPath
}

# Activate venv and install dependencies
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
. $ActivateScript

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r (Join-Path $ServiceDir "requirements.txt") -q

# Load environment variables from .env if exists
$EnvFile = Join-Path $ServiceDir ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Also check project-level .env
$ProjectEnv = Join-Path $ServiceDir "..\..\..\.env"
if (Test-Path $ProjectEnv) {
    Get-Content $ProjectEnv | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Start the service
Write-Host "Starting Voice Actor service on http://127.0.0.1:11436" -ForegroundColor Green
python (Join-Path $ServiceDir "voice_actor_service.py")
