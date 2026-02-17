# ULTRON Cluster Router - Startup Script
# Presents ULTRON + Iron Legion as a unified Ollama-compatible endpoint
#
# Usage: .\start_cluster_router.ps1
# Endpoint: http://localhost:8080

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Get-Item $ScriptDir).Parent.Parent.FullName

Write-Host "=== ULTRON Cluster Router ===" -ForegroundColor Cyan
Write-Host "Starting unified cluster on port 8080..." -ForegroundColor Yellow

# Check if already running
$existing = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Port 8080 already in use. Checking if it's the cluster router..." -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8080/health" -TimeoutSec 5
        if ($health.status) {
            Write-Host "Cluster router already running!" -ForegroundColor Green
            Write-Host "Health: $($health.status), Nodes: $($health.healthy_nodes)/$($health.total_nodes)" -ForegroundColor Green
            exit 0
        }
    } catch {
        Write-Host "Port 8080 in use by another process. Cannot start." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment if exists
$venvPath = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    . $venvPath
}

# Install dependencies if needed
$aiohttp = python -c "import aiohttp" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing aiohttp..." -ForegroundColor Yellow
    pip install aiohttp
}

# Start the router
$routerScript = Join-Path $ScriptDir "cluster_router.py"
Write-Host "Launching: $routerScript" -ForegroundColor Cyan
python $routerScript
