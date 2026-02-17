#!/usr/bin/env python3
"""
Centralized Logging Setup for Lumina Project

Configures L: drive mapping for centralized logging with NAS/DSM integration.
Includes log aggregation, monitoring, and archival systems.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger("setup_centralized_logging")


# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class CentralizedLoggingSetup:
    """
    Comprehensive centralized logging system for Lumina project.

    Features:
    - L: drive mapping for log storage
    - Log aggregation from multiple hosts
    - DSM integration for log management
    - Log rotation and archival
    - Real-time monitoring and alerting
    """

    def __init__(self):
        self.log_config = self._define_log_configuration()
        self.l_drive_config = self._define_l_drive_mapping()

    def _define_log_configuration(self) -> Dict[str, Any]:
        """Define comprehensive logging configuration"""

        return {
            "log_types": {
                "system": {
                    "path": "L:/Logs/System",
                    "retention": "90 days",
                    "rotation": "daily",
                    "compression": True
                },
                "application": {
                    "path": "L:/Logs/Application",
                    "retention": "180 days",
                    "rotation": "weekly",
                    "compression": True
                },
                "security": {
                    "path": "L:/Logs/Security",
                    "retention": "365 days",
                    "rotation": "daily",
                    "compression": True,
                    "encryption": True
                },
                "ai_models": {
                    "path": "L:/Logs/AI",
                    "retention": "90 days",
                    "rotation": "daily",
                    "compression": True
                },
                "network": {
                    "path": "L:/Logs/Network",
                    "retention": "60 days",
                    "rotation": "hourly",
                    "compression": True
                },
                "performance": {
                    "path": "L:/Logs/Performance",
                    "retention": "30 days",
                    "rotation": "daily",
                    "compression": False  # Keep uncompressed for analysis
                }
            },
            "hosts": {
                "RTX5090-Laptop": {
                    "hostname": "lumina-rtx5090",
                    "ip": "<NAS_IP>",
                    "log_sources": ["system", "application", "ai_models", "performance"]
                },
                "RTX3090-Desktop": {
                    "hostname": "lumina-rtx3090",
                    "ip": "<NAS_PRIMARY_IP>",
                    "log_sources": ["system", "application", "network", "security"]
                },
                "NAS-DS2118plus": {
                    "hostname": "ds2118plus",
                    "ip": "<NAS_PRIMARY_IP>",
                    "log_sources": ["system", "network", "storage"]
                }
            },
            "aggregation": {
                "interval": "5 minutes",
                "batch_size": "100MB",
                "compression": "gzip",
                "encryption": "AES256"
            },
            "monitoring": {
                "alert_thresholds": {
                    "error_rate": 10,  # errors per minute
                    "disk_usage": 85,  # percentage
                    "log_size": "10GB"  # per log type
                },
                "notifications": {
                    "email": "admin@lumina-project.local",
                    "slack": "#logging-alerts",
                    "sms": "+1-555-LUMINA"
                }
            }
        }

    def _define_l_drive_mapping(self) -> Dict[str, Any]:
        """Define L: drive mapping for centralized logging"""

        return {
            "drive_letter": "L:",
            "description": "Centralized Logging Storage",
            "path": r"\\DS2118PLUS\Logs",
            "username": "backupadm",
            "purpose": "Centralized log storage and aggregation",
            "capacity": "500GB+",
            "backup": "Real-time replication",
            "subdirs": [
                "Logs/System",
                "Logs/Application",
                "Logs/Security",
                "Logs/AI",
                "Logs/Network",
                "Logs/Performance",
                "Archives",
                "Analytics",
                "Reports"
            ],
            "permissions": {
                "administrators": "Full Control",
                "users": "Read & Execute",
                "services": "Write"
            }
        }

    def add_l_drive_to_registry(self) -> Dict[str, Any]:
        """Add L: drive to Windows Registry for permanent mapping"""

        print("🔧 ADDING L: DRIVE TO REGISTRY FOR LOGGING")
        print("=" * 50)

        try:
            import winreg as reg

            # Open the Network key in HKEY_CURRENT_USER
            key_path = r"Network"
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)

            drive_key = "L"

            try:
                # Create subkey for L drive
                drive_subkey = reg.CreateKey(key, drive_key)

                # Set connection type and provider
                reg.SetValueEx(drive_subkey, "ConnectionType", 0, reg.REG_DWORD, 1)
                reg.SetValueEx(drive_subkey, "DeferFlags", 0, reg.REG_DWORD, 4)
                reg.SetValueEx(drive_subkey, "ProviderName", 0, reg.REG_SZ, "Microsoft Windows Network")
                reg.SetValueEx(drive_subkey, "ProviderType", 0, reg.REG_DWORD, 0x20000)
                reg.SetValueEx(drive_subkey, "RemotePath", 0, reg.REG_SZ, self.l_drive_config['path'])
                reg.SetValueEx(drive_subkey, "UserName", 0, reg.REG_SZ, self.l_drive_config['username'])

                reg.CloseKey(drive_subkey)

                print("✅ L: drive registry entry created for centralized logging")
                return {"status": "created", "method": "registry"}

            except Exception as e:
                print(f"❌ Failed to create L: drive registry entry: {e}")
                return {"status": "failed", "error": str(e)}

            reg.CloseKey(key)

        except Exception as e:
            print(f"❌ Failed to access registry: {e}")
            return {"error": f"Registry access failed: {e}"}

    def create_log_shipper_config(self) -> str:
        """Create log shipper configuration for forwarding logs to NAS"""

        config_content = f'''# Lumina Project Log Shipper Configuration
# Forwards local logs to centralized NAS storage

[general]
hostname = {platform.node()}
log_level = INFO
batch_size = 100MB
flush_interval = 30s
compression = gzip

[outputs]
central_nas = {{
    type = "file"
    path = "{self.l_drive_config['path']}/Logs/{{{{.Hostname}}}}/{{{{.LogType}}}}/"
    rotation = "daily"
    retention = "90d"
    compression = true
}}

[inputs]
system_logs = {{
    type = "file"
    paths = [
        "/var/log/syslog",
        "/var/log/messages",
        "/var/log/system.log",
        "C:\\Windows\\System32\\winevt\\Logs\\System.evtx"
    ]
    tags = ["system"]
}}

application_logs = {{
    type = "file"
    paths = [
        "/var/log/application/*.log",
        "C:\\ProgramData\\ApplicationLogs\\*.log",
        "/opt/lumina/logs/*.log"
    ]
    tags = ["application"]
}}

ai_logs = {{
    type = "file"
    paths = [
        "/opt/ollama/logs/*.log",
        "/opt/stable-diffusion/logs/*.log",
        "M:\\AI\\logs\\*.log"
    ]
    tags = ["ai", "ml"]
}}

security_logs = {{
    type = "file"
    paths = [
        "/var/log/auth.log",
        "/var/log/secure",
        "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx"
    ]
    tags = ["security"]
}}

performance_logs = {{
    type = "metrics"
    interval = "30s"
    metrics = [
        "cpu.usage",
        "memory.usage",
        "disk.usage",
        "network.traffic"
    ]
    tags = ["performance", "monitoring"]
}}

[processing]
filters = [
    {{
        type = "drop"
        condition = "level == 'debug' && size > 100MB"
    }},
    {{
        type = "anonymize"
        fields = ["password", "token", "key"]
    }},
    {{
        type = "enrich"
        add_fields = {{
            "environment" = "lumina"
            "project" = "ai-workstation"
            "host_role" = "workstation"
        }}
    }}
]

[monitoring]
alerts = [
    {{
        name = "High Error Rate"
        condition = "rate(errors) > 10 per minute"
        action = "email"
    }},
    {{
        name = "Disk Usage High"
        condition = "disk.usage > 85%"
        action = "slack"
    }}
]
'''

        config_path = project_root / "log-shipper-config.toml"
        with open(config_path, 'w') as f:
            f.write(config_content)

        return str(config_path)

    def create_dsm_log_config(self) -> str:
        """Create DSM (Synology) log configuration for log aggregation"""

        dsm_config = '''# DSM Log Center Configuration for Lumina Project
# Configure log aggregation and monitoring on DS2118+

[log_center]
enabled = true
retention_days = 365
compression = true
encryption = true

[log_sources]
rtx5090_laptop = {
    type = "syslog"
    protocol = "tcp"
    port = 514
    source_ip = "<NAS_IP>"
    facility = "local0"
    severity = "info"
}

rtx3090_desktop = {
    type = "syslog"
    protocol = "tcp"
    port = 514
    source_ip = "<NAS_PRIMARY_IP>"
    facility = "local1"
    severity = "info"
}

[log_rules]
security_events = {
    filter = "facility == 'auth' || facility == 'authpriv'"
    action = "alert"
    email = "security@lumina-project.local"
}

ai_errors = {
    filter = "program == 'ollama' || program == 'stable-diffusion'"
    action = "notify"
    slack = "#ai-alerts"
}

system_errors = {
    filter = "severity >= 'error'"
    action = "log"
    archive = true
}

[log_storage]
primary = "/volume1/Logs"
secondary = "/volume2/Logs-Backup"
archive = "/volume1/Archives/Logs"

[log_rotation]
daily = {
    enabled = true
    time = "02:00"
    compression = "gzip"
    retention = 90
}

weekly = {
    enabled = true
    day = "sunday"
    time = "03:00"
    compression = "xz"
    retention = 365
}

[monitoring]
enabled = true
check_interval = "5m"
alert_thresholds = {
    disk_usage = 85
    log_size = "50GB"
    error_rate = 100
}

[reports]
daily_report = {
    enabled = true
    time = "08:00"
    recipients = ["admin@lumina-project.local"]
    include = ["error_summary", "disk_usage", "top_sources"]
}

weekly_report = {
    enabled = true
    day = "monday"
    time = "09:00"
    recipients = ["team@lumina-project.local"]
    include = ["security_summary", "performance_trends", "anomaly_detection"]
}
'''

        dsm_config_path = project_root / "dsm-log-center-config.json"
        with open(dsm_config_path, 'w') as f:
            f.write(dsm_config)

        return str(dsm_config_path)

    def create_log_monitoring_script(self) -> str:
        """Create log monitoring and alerting script"""

        monitoring_script = '''# Lumina Project Log Monitoring Script
# Monitors centralized logs and sends alerts

param(
    [switch]$Continuous,
    [int]$IntervalSeconds = 300,
    [switch]$Quiet
)

$ErrorActionPreference = "Continue"

# Configuration
$LogPath = "L:\\Logs"
$AlertThresholds = @{
    ErrorRate = 10  # errors per 5 minutes
    DiskUsagePercent = 85
    LogSizeGB = 10
}

$NotificationSettings = @{
    Email = "admin@lumina-project.local"
    SlackWebhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    SMTP = "smtp.lumina-project.local"
}

function Get-LogStats {
    param([string]$LogType)

    $logDir = Join-Path $LogPath $LogType
    if (-not (Test-Path $logDir)) {
        return $null
    }

    $files = Get-ChildItem $logDir -File -Recurse
    $totalSize = ($files | Measure-Object -Property Length -Sum).Sum
    $errorCount = ($files | Select-String -Pattern "ERROR|CRITICAL|FATAL" -CaseSensitive:$false).Count
    $recentFiles = $files | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) }

    return @{
        TotalSizeGB = [math]::Round($totalSize / 1GB, 2)
        FileCount = $files.Count
        ErrorCount = $errorCount
        RecentActivity = $recentFiles.Count
    }
}

function Send-Alert {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Severity = "warning"
    )

    if (-not $Quiet) {
        Write-Host "🚨 ALERT: $Title" -ForegroundColor Red
        Write-Host "   $Message" -ForegroundColor Yellow
    }

    # Email alert
    try {
        $emailBody = @"
LUMINA LOG ALERT

Title: $Title
Severity: $Severity
Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

$Message

--
Lumina Log Monitoring System
"@

        Send-MailMessage -To $NotificationSettings.Email -Subject "LUMINA ALERT: $Title" -Body $emailBody -SmtpServer $NotificationSettings.SMTP
    } catch {
        if (-not $Quiet) {
            Write-Host "Failed to send email alert: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    # Slack alert (if webhook configured)
    if ($NotificationSettings.SlackWebhook -and $NotificationSettings.SlackWebhook -notlike "*YOUR*") {
        try {
            $slackMessage = @{
                text = ":warning: *LUMINA ALERT*\\n*$Title*\\n$Message"
                username = "Lumina Log Monitor"
                icon_emoji = ":notebook:"
            } | ConvertTo-Json

            Invoke-RestMethod -Uri $NotificationSettings.SlackWebhook -Method Post -Body $slackMessage -ContentType 'application/json'
        } catch {
            if (-not $Quiet) {
                Write-Host "Failed to send Slack alert: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }
}

function Monitor-Logs {
    if (-not $Quiet) {
        Write-Host "📊 Starting Lumina Log Monitoring..." -ForegroundColor Cyan
        Write-Host "   Monitoring path: $LogPath" -ForegroundColor Gray
        Write-Host "   Check interval: $IntervalSeconds seconds" -ForegroundColor Gray
        Write-Host ""
    }

    $iteration = 0
    do {
        $iteration++
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

        if (-not $Quiet) {
            Write-Host "[$timestamp] Checking logs (iteration $iteration)..." -NoNewline
        }

        # Check disk usage
        try {
            $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='L:'"
            $diskUsagePercent = [math]::Round(($disk.Size - $disk.FreeSpace) / $disk.Size * 100, 1)

            if ($diskUsagePercent -gt $AlertThresholds.DiskUsagePercent) {
                Send-Alert -Title "High Disk Usage on L: Drive" -Message "Disk usage is at ${diskUsagePercent}% (threshold: $($AlertThresholds.DiskUsagePercent)%)" -Severity "critical"
            }
        } catch {
            if (-not $Quiet) {
                Write-Host " (disk check failed)" -ForegroundColor Yellow
            }
        }

        # Check each log type
        $logTypes = @("System", "Application", "Security", "AI", "Network", "Performance")

        foreach ($logType in $logTypes) {
            $stats = Get-LogStats -LogType $logType

            if ($stats) {
                # Check log size
                if ($stats.TotalSizeGB -gt $AlertThresholds.LogSizeGB) {
                    Send-Alert -Title "Large Log Size: $logType" -Message "$logType logs are $($stats.TotalSizeGB)GB (threshold: $($AlertThresholds.LogSizeGB)GB)" -Severity "warning"
                }

                # Check error rate (simplified - would need more sophisticated analysis in production)
                if ($stats.ErrorCount -gt $AlertThresholds.ErrorRate) {
                    Send-Alert -Title "High Error Rate: $logType" -Message "Found $($stats.ErrorCount) errors in $logType logs (threshold: $($AlertThresholds.ErrorRate)))" -Severity "warning"
                }

                if (-not $Quiet -and $Verbose) {
                    Write-Host "  $logType`: $($stats.FileCount) files, $($stats.TotalSizeGB)GB, $($stats.ErrorCount) errors, $($stats.RecentActivity) recent" -ForegroundColor Gray
                }
            }
        }

        if (-not $Quiet) {
            Write-Host " ✓" -ForegroundColor Green
        }

        if ($Continuous) {
            Start-Sleep -Seconds $IntervalSeconds
        }

    } while ($Continuous)
}

# Main execution
if ($Continuous) {
    Monitor-Logs
} else {
    Monitor-Logs
    if (-not $Quiet) {
        Write-Host "`nMonitoring complete. Use -Continuous for ongoing monitoring." -ForegroundColor Cyan
    }
}
'''

        monitoring_script_path = project_root / "LuminaLogMonitor.ps1"
        with open(monitoring_script_path, 'w', encoding='utf-8') as f:
            f.write(monitoring_script)

        return str(monitoring_script_path)

    def create_log_analysis_tools(self) -> Dict[str, str]:
        """Create log analysis and reporting tools"""

        # Log analysis PowerShell script
        analysis_script = '''# Lumina Log Analysis Tool

param(
    [string]$LogType = "All",
    [DateTime]$StartDate = (Get-Date).AddDays(-7),
    [DateTime]$EndDate = (Get-Date),
    [switch]$GenerateReport,
    [string]$OutputPath = "L:\\Reports"
)

$LogPath = "L:/Logs"

function Analyze-LogFiles {
    param([string]$LogType, [DateTime]$StartDate, [DateTime]$EndDate)

    $logDir = Join-Path $LogPath $LogType
    if (-not (Test-Path $logDir)) {
        Write-Warning "Log directory not found: $logDir"
        return $null
    }

    $files = Get-ChildItem $logDir -File -Recurse | Where-Object {
        $_.LastWriteTime -ge $StartDate -and $_.LastWriteTime -le $EndDate
    }

    $analysis = @{
        TotalFiles = $files.Count
        TotalSizeMB = [math]::Round(($files | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
        DateRange = "$($StartDate.ToString('yyyy-MM-dd')) to $($EndDate.ToString('yyyy-MM-dd'))"
        ErrorCount = 0
        WarningCount = 0
        InfoCount = 0
        TopErrorMessages = @()
        HourlyDistribution = @{}
    }

    foreach ($file in $files) {
        try {
            $content = Get-Content $file.FullName -Raw
            $lines = $content -split "`n"

            foreach ($line in $lines) {
                if ($line -match "ERROR|CRITICAL|FATAL") {
                    $analysis.ErrorCount++
                    # Extract error message (simplified)
                    if ($line -match "ERROR[:\\s]+(.+)$") {
                        $errorMsg = $matches[1].Trim()
                        $analysis.TopErrorMessages += $errorMsg
                    }
                } elseif ($line -match "WARNING|WARN") {
                    $analysis.WarningCount++
                } elseif ($line -match "INFO") {
                    $analysis.InfoCount++
                }

                # Extract timestamp for hourly distribution (simplified)
                if ($line -match "(\\d{4}-\\d{2}-\\d{2}\\s\\d{2}):") {
                    $hour = $matches[1]
                    if (-not $analysis.HourlyDistribution.ContainsKey($hour)) {
                        $analysis.HourlyDistribution[$hour] = 0
                    }
                    $analysis.HourlyDistribution[$hour]++
                }
            }
        } catch {
            Write-Warning "Failed to analyze file: $($file.FullName)"
        }
    }

    # Get top error messages
    $analysis.TopErrorMessages = $analysis.TopErrorMessages | Group-Object | Sort-Object -Property Count -Descending | Select-Object -First 10 -ExpandProperty Name

    return $analysis
}

function Generate-Report {
    param([object]$Analysis, [string]$LogType, [string]$OutputPath)

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportFile = Join-Path $OutputPath "LogAnalysis_${LogType}_${timestamp}.html"

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Lumina Log Analysis Report - $LogType</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .metric {{ background: #ecf0f1; padding: 10px; margin: 10px 0; }}
        .error {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        .success {{ color: #27ae60; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #2c3e50; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Lumina Log Analysis Report</h1>
        <h2>$LogType Logs</h2>
        <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
    </div>

    <div class="metric">
        <h3>Summary</h3>
        <p><strong>Date Range:</strong> $($Analysis.DateRange)</p>
        <p><strong>Total Files:</strong> $($Analysis.TotalFiles)</p>
        <p><strong>Total Size:</strong> $($Analysis.TotalSizeMB) MB</p>
    </div>

    <div class="metric">
        <h3>Log Levels</h3>
        <p class="error"><strong>Errors:</strong> $($Analysis.ErrorCount)</p>
        <p class="warning"><strong>Warnings:</strong> $($Analysis.WarningCount)</p>
        <p class="success"><strong>Info:</strong> $($Analysis.InfoCount)</p>
    </div>

    <div class="metric">
        <h3>Top Error Messages</h3>
        <ul>
"@

    foreach ($error in $Analysis.TopErrorMessages | Select-Object -First 10) {
        $html += "            <li>$error</li>`n"
    }

    $html += @"
        </ul>
    </div>

    <div class="metric">
        <h3>Hourly Distribution</h3>
        <table>
            <tr><th>Hour</th><th>Log Entries</th></tr>
"@

    foreach ($hour in $Analysis.HourlyDistribution.GetEnumerator() | Sort-Object -Property Name) {
        $html += "            <tr><td>$($hour.Key)</td><td>$($hour.Value)</td></tr>`n"
    }

    $html += @"
        </table>
    </div>
</body>
</html>
"@

    $null = New-Item -ItemType Directory -Path $OutputPath -Force
    $html | Out-File -FilePath $reportFile -Encoding UTF8

    Write-Host "Report generated: $reportFile" -ForegroundColor Green
}

# Main execution
$logTypes = if ($LogType -eq "All") {
    @("System", "Application", "Security", "AI", "Network", "Performance")
} else {
    @($LogType)
}

foreach ($type in $logTypes) {
    Write-Host "Analyzing $type logs..." -ForegroundColor Cyan
    $analysis = Analyze-LogFiles -LogType $type -StartDate $StartDate -EndDate $EndDate

    if ($analysis) {
        Write-Host "  Files: $($analysis.TotalFiles)" -ForegroundColor Gray
        Write-Host "  Size: $($analysis.TotalSizeMB) MB" -ForegroundColor Gray
        Write-Host "  Errors: $($analysis.ErrorCount)" -ForegroundColor $(if ($analysis.ErrorCount -gt 0) { "Red" } else { "Green" })

        if ($GenerateReport) {
            Generate-Report -Analysis $analysis -LogType $type -OutputPath $OutputPath
        }
    }
}
'''

        analysis_script_path = project_root / "LuminaLogAnalysis.ps1"
        with open(analysis_script_path, 'w', encoding='utf-8') as f:
            f.write(analysis_script)

        # Log cleanup script
        cleanup_script = '''# Lumina Log Cleanup Script

param(
    [switch]$DryRun,
    [int]$RetentionDays = 90,
    [string]$LogPath = "L:/Logs",
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$cutoffDate = (Get-Date).AddDays(-$RetentionDays)

if (-not $Quiet) {
    Write-Host "🧹 Lumina Log Cleanup" -ForegroundColor Cyan
    Write-Host "   Path: $LogPath" -ForegroundColor Gray
    Write-Host "   Retention: $RetentionDays days (before $($cutoffDate.ToString('yyyy-MM-dd')))" -ForegroundColor Gray
    if ($DryRun) {
        Write-Host "   Mode: DRY RUN (no files will be deleted)" -ForegroundColor Yellow
    }
    Write-Host ""
}

$stats = @{
    TotalFiles = 0
    FilesToDelete = 0
    SpaceToReclaim = 0
    DeletedFiles = 0
    ReclaimedSpace = 0
}

# Function to process directory
function Process-Directory {
    param([string]$Directory)

    if (-not (Test-Path $Directory)) {
        return
    }

    $files = Get-ChildItem $Directory -File -Recurse

    foreach ($file in $files) {
        $stats.TotalFiles++

        if ($file.LastWriteTime -lt $cutoffDate) {
            $stats.FilesToDelete++
            $stats.SpaceToReclaim += $file.Length

            if (-not $DryRun) {
                try {
                    Remove-Item $file.FullName -Force
                    $stats.DeletedFiles++
                    $stats.ReclaimedSpace += $file.Length
                } catch {
                    if (-not $Quiet) {
                        Write-Warning "Failed to delete: $($file.FullName)"
                    }
                }
            }

            if (-not $Quiet -and -not $DryRun) {
                Write-Host "  Deleted: $($file.Name)" -ForegroundColor Gray
            }
        }
    }
}

# Process each log type
$logTypes = @("System", "Application", "Security", "AI", "Network", "Performance")

foreach ($logType in $logTypes) {
    $logDir = Join-Path $LogPath $logType
    if (-not $Quiet) {
        Write-Host "Processing $logType logs..." -NoNewline
    }

    Process-Directory -Directory $logDir

    if (-not $Quiet) {
        Write-Host " ✓" -ForegroundColor Green
    }
}

# Summary
$reclaimGB = [math]::Round($stats.SpaceToReclaim / 1GB, 2)
$reclaimedGB = [math]::Round($stats.ReclaimedSpace / 1GB, 2)

if (-not $Quiet) {
    Write-Host "`n📊 CLEANUP SUMMARY" -ForegroundColor Cyan
    Write-Host "=" * 30 -ForegroundColor Cyan
    Write-Host "Total files scanned: $($stats.TotalFiles.ToString('N0'))" -ForegroundColor Gray
    Write-Host "Files eligible for deletion: $($stats.FilesToDelete.ToString('N0'))" -ForegroundColor Gray
    Write-Host "Space to be reclaimed: $reclaimGB GB" -ForegroundColor Gray

    if (-not $DryRun) {
        Write-Host "Files actually deleted: $($stats.DeletedFiles.ToString('N0'))" -ForegroundColor $(if ($stats.DeletedFiles -gt 0) { "Red" } else { "Green" })
        Write-Host "Space actually reclaimed: $reclaimedGB GB" -ForegroundColor $(if ($stats.ReclaimedSpace -gt 0) { "Red" } else { "Green" })
    }
}

# Return stats
@{
    TotalFiles = $stats.TotalFiles
    FilesToDelete = $stats.FilesToDelete
    SpaceToReclaimGB = $reclaimGB
    DeletedFiles = $stats.DeletedFiles
    ReclaimedSpaceGB = $reclaimedGB
    DryRun = $DryRun
}
'''

        cleanup_script_path = project_root / "LuminaLogCleanup.ps1"
        with open(cleanup_script_path, 'w', encoding='utf-8') as f:
            f.write(cleanup_script)

        return {
            "analysis": str(analysis_script_path),
            "cleanup": str(cleanup_script_path)
        }

    def run_complete_setup(self) -> Dict[str, Any]:
        """Run the complete centralized logging setup"""

        print("📋 CENTRALIZED LOGGING SETUP FOR LUMINA PROJECT")
        print("=" * 60)
        print("Setting up L: drive and comprehensive logging infrastructure...")

        results = {
            "timestamp": "2026-01-20T18:33:00Z",
            "components": []
        }

        # 1. Add L: drive to registry
        registry_result = self.add_l_drive_to_registry()
        results["components"].append({
            "component": "l_drive_registry",
            "description": "L: drive registry entry for logging",
            "status": "completed" if registry_result.get("status") == "created" else "failed",
            "details": registry_result
        })

        # 2. Create log shipper configuration
        shipper_config = self.create_log_shipper_config()
        results["components"].append({
            "component": "log_shipper_config",
            "description": "Log forwarding configuration",
            "status": "created",
            "path": shipper_config
        })

        # 3. Create DSM log configuration
        dsm_config = self.create_dsm_log_config()
        results["components"].append({
            "component": "dsm_log_config",
            "description": "Synology DSM log center configuration",
            "status": "created",
            "path": dsm_config
        })

        # 4. Create log monitoring script
        monitoring_script = self.create_log_monitoring_script()
        results["components"].append({
            "component": "log_monitoring_script",
            "description": "Log monitoring and alerting script",
            "status": "created",
            "path": monitoring_script
        })

        # 5. Create log analysis tools
        analysis_tools = self.create_log_analysis_tools()
        results["components"].extend([
            {
                "component": "log_analysis_script",
                "description": "Log analysis and reporting tool",
                "status": "created",
                "path": analysis_tools["analysis"]
            },
            {
                "component": "log_cleanup_script",
                "description": "Log cleanup and rotation tool",
                "status": "created",
                "path": analysis_tools["cleanup"]
            }
        ])

        # Summary
        print("\n🎉 CENTRALIZED LOGGING SETUP COMPLETE")
        print("=" * 60)

        successful_components = sum(1 for comp in results["components"] if comp["status"] in ["created", "completed"])
        total_components = len(results["components"])

        print(f"✅ Components configured: {successful_components}/{total_components}")

        print("\n🔄 IMPLEMENTATION STEPS:")
        print("1. Apply L: drive registry settings (restart may be required)")
        print("2. Configure DSM Log Center using dsm-log-center-config.json")
        print("3. Install log shipper on each host using log-shipper-config.toml")
        print("4. Set up scheduled tasks for monitoring and cleanup")
        print("5. Configure email/Slack notifications")

        print("\n📍 LOG STORAGE STRUCTURE:")
        print("L:\\Logs\\")
        print("├── System\\")
        print("├── Application\\")
        print("├── Security\\")
        print("├── AI\\")
        print("├── Network\\")
        print("└── Performance\\")

        print("\n🛠️  MANAGEMENT SCRIPTS:")
        print("• LuminaLogMonitor.ps1    - Real-time monitoring")
        print("• LuminaLogAnalysis.ps1   - Analysis and reporting")
        print("• LuminaLogCleanup.ps1    - Rotation and cleanup")

        print("\n⚡ AUTOMATION:")
        print("• Registry: L: drive permanently mapped")
        print("• DSM: Centralized aggregation and alerting")
        print("• Monitoring: Real-time error detection")
        print("• Rotation: Automatic cleanup and archival")

        return results


def main():
    try:
        """Main setup function"""
        if platform.system() != 'Windows':
            print("❌ Centralized logging setup is Windows-specific")
            return

        logging_setup = CentralizedLoggingSetup()
        results = logging_setup.run_complete_setup()

        # Save results
        output_file = project_root / "CENTRALIZED_LOGGING_SETUP_RESULTS.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📄 Detailed results saved to: {output_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    main()