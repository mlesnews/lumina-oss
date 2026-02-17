# ╔══════════════════════════════════════════════════════════════════╗
# ║  J.A.R.V.I.S. — PowerShell Environment                        ║
# ║  Stark Industries // Millennium Falcon                         ║
# ║  Cedarbrook Financial Services, LLC                            ║
# ╚══════════════════════════════════════════════════════════════════╝

# ── JARVIS Color Palette ──────────────────────────────────────────
$script:E = [char]27
$script:cCyan    = "$([char]27)[96m"
$script:cBlue    = "$([char]27)[94m"
$script:cDim     = "$([char]27)[2m"
$script:cBold    = "$([char]27)[1m"
$script:cGreen   = "$([char]27)[92m"
$script:cYellow  = "$([char]27)[93m"
$script:cRed     = "$([char]27)[91m"
$script:cRst     = "$([char]27)[0m"

$Host.UI.RawUI.WindowTitle = "J.A.R.V.I.S. // Stark Industries"

# ── JARVIS Prompt ──────────────────────────────────────────────────
function prompt {
    $lastOk = $?

    if ($lastOk) { $dot = "$($script:cGreen)◉$($script:cRst)" }
    else         { $dot = "$($script:cRed)◉$($script:cRst)" }

    $pathParts = (Get-Location).Path -split '\\'
    if ($pathParts.Count -gt 2) { $sp = "$($pathParts[-2])\$($pathParts[-1])" }
    else                        { $sp = (Get-Location).Path }

    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    $atag = ""; if ($isAdmin) { $atag = "$($script:cRed)[ADMIN]$($script:cRst) " }

    $gb = ""
    try {
        $br = git rev-parse --abbrev-ref HEAD 2>$null
        if ($br) { $gb = " $($script:cDim)on$($script:cRst) $($script:cYellow)$br$($script:cRst)" }
    } catch {}

    $tm = Get-Date -Format "HH:mm"
    Write-Host ""
    Write-Host "$($script:cDim)$tm$($script:cRst) $dot ${atag}$($script:cCyan)JARVIS$($script:cRst)$($script:cDim)://$($script:cRst)$($script:cBold)$sp$($script:cRst)$gb" -NoNewline
    Write-Host ""
    return "$($script:cCyan)>$($script:cRst) "
}

# ── JARVIS Greeting ────────────────────────────────────────────────
function Show-JarvisGreeting {
    $hour = (Get-Date).Hour
    if     ($hour -lt 6)  { $g = "Burning the midnight oil, sir?" }
    elseif ($hour -lt 12) { $g = "Good morning, sir." }
    elseif ($hour -lt 17) { $g = "Good afternoon, sir." }
    elseif ($hour -lt 21) { $g = "Good evening, sir." }
    else                  { $g = "Working late again, sir?" }

    Write-Host ""
    Write-Host "  $($script:cCyan)$([char]9678) $($script:cBold)J.A.R.V.I.S.$($script:cRst)$($script:cDim) - Just A Rather Very Intelligent System$($script:cRst)"
    Write-Host "  $($script:cDim)  Stark Industries // Millennium Falcon$($script:cRst)"
    Write-Host ""
    Write-Host "    $($script:cDim)$g$($script:cRst)"
    Write-Host "    $($script:cDim)All systems operational.$($script:cRst)"
    Write-Host ""
}

# ── Aliases ────────────────────────────────────────────────────────
Set-Alias -Name which -Value Get-Command

function lumina { Set-Location "\\10.17.17.32\docker\lumina" }
function proj   { Set-Location "\\10.17.17.32\homes\mlesn\projects" }
function nas    { Set-Location "\\10.17.17.32\homes" }

# ── System Status ──────────────────────────────────────────────────
function Get-SystemStatus {
    Write-Host ""
    Write-Host "  $($script:cCyan)$([char]9678) SYSTEM STATUS$($script:cRst)"
    Write-Host "  $($script:cDim)$([string][char]0x2500 * 37)$($script:cRst)"

    $cpu = (Get-CimInstance Win32_Processor).LoadPercentage
    if     ($cpu -gt 80) { $cc = $script:cRed }
    elseif ($cpu -gt 50) { $cc = $script:cYellow }
    else                 { $cc = $script:cGreen }
    Write-Host "    CPU:    ${cc}${cpu}%$($script:cRst)"

    $os = Get-CimInstance Win32_OperatingSystem
    $mu = [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB, 1)
    $mt = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
    $mp = [math]::Round($mu / $mt * 100)
    if     ($mp -gt 80) { $mc = $script:cRed }
    elseif ($mp -gt 60) { $mc = $script:cYellow }
    else                { $mc = $script:cGreen }
    Write-Host "    Memory: ${mc}${mu}/${mt} GB (${mp}%)$($script:cRst)"

    $up = (Get-Date) - $os.LastBootUpTime
    Write-Host "    Uptime: $($script:cDim)$([math]::Floor($up.TotalDays))d $($up.Hours)h $($up.Minutes)m$($script:cRst)"

    try {
        $gpu = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notmatch 'Virtual|Basic' } | Select-Object -First 1
        if ($gpu) { Write-Host "    GPU:    $($script:cDim)$($gpu.Name)$($script:cRst)" }
    } catch {}
    Write-Host ""
}
Set-Alias -Name status -Value Get-SystemStatus

# ── PSReadLine ────────────────────────────────────────────────────
if (Get-Module -ListAvailable PSReadLine) {
    if ($PSVersionTable.PSVersion.Major -ge 7) {
        try { Set-PSReadLineOption -PredictionSource History } catch {}
        try {
            Set-PSReadLineOption -Colors @{
                Command   = "$([char]27)[96m"
                Parameter = "$([char]27)[94m"
                Operator  = "$([char]27)[93m"
                Variable  = "$([char]27)[92m"
                String    = "$([char]27)[33m"
                Number    = "$([char]27)[35m"
                Comment   = "$([char]27)[2m"
                Error     = "$([char]27)[91m"
            }
        } catch {}
    } else {
        try {
            Set-PSReadLineOption -Colors @{
                Command   = "Cyan"
                Parameter = "DarkCyan"
                Operator  = "Yellow"
                Variable  = "Green"
                String    = "DarkYellow"
                Number    = "Magenta"
                Comment   = "DarkGray"
                Error     = "Red"
            }
        } catch {}
    }
    try { Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete } catch {}
}

# ── Startup ───────────────────────────────────────────────────────
Show-JarvisGreeting
