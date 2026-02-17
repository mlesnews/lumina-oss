# BitNet API Server Startup Script
# This script is run by Windows Task Scheduler at startup
# Tags: @PEAK @CLUSTER @BITNET #automation

param(
    [int]$Port = 11435,
    [int]$Threads = 16
)

$ErrorActionPreference = "Continue"

# Configuration
$BitNetDir = "$env:USERPROFILE\bitnet"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServerScript = Join-Path $ScriptDir "bitnet_api_server.py"
$LogFile = Join-Path $ScriptDir "bitnet_service.log"

# Set environment
$env:BITNET_DIR = $BitNetDir

# Log function
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -Append -FilePath $LogFile
    Write-Host "$timestamp - $Message"
}

Write-Log "Starting BitNet API Server..."
Write-Log "BitNet Dir: $BitNetDir"
Write-Log "Server Script: $ServerScript"
Write-Log "Port: $Port, Threads: $Threads"

# Check if already running
$existingProcess = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-Log "Port $Port already in use. BitNet may already be running."
    exit 0
}

# Start the server
try {
    Write-Log "Launching BitNet API Server..."
    python $ServerScript --port $Port --threads $Threads
} catch {
    Write-Log "Error: $_"
    exit 1
}
