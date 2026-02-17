# Lumina AI Gateway Startup Script
# Start the unified AI gateway service

$ErrorActionPreference = "Stop"
$GatewayDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting Lumina AI Gateway..." -ForegroundColor Cyan

# Check if virtual environment exists
$VenvPath = Join-Path $GatewayDir "venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvPath
}

# Activate venv and install dependencies
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
. $ActivateScript

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r (Join-Path $GatewayDir "requirements.txt") -q

# Load environment variables from .env if exists
$EnvFile = Join-Path $GatewayDir ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Start the gateway
Write-Host "Starting gateway on http://127.0.0.1:11435" -ForegroundColor Green
python (Join-Path $GatewayDir "gateway.py")
