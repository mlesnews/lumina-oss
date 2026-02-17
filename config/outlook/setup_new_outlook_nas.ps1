
# New Outlook Configuration Script for NAS Mail Hub
# Run this in PowerShell as Administrator if needed

$email = "mlesn@homelab.lesnewski.local"
$imapServer = "10.17.17.32"
$imapPort = 993
$smtpServer = "10.17.17.32"
$smtpPort = 587

Write-Host "========================================"
Write-Host "New Outlook - NAS Mail Hub Configuration"
Write-Host "========================================"
Write-Host ""
Write-Host "Email Account: $email"
Write-Host "IMAP Server: $imapServer:$imapPort"
Write-Host "SMTP Server: $smtpServer:$smtpPort"
Write-Host ""
Write-Host "Note: New Outlook requires manual account setup through the UI."
Write-Host "This script provides the configuration details."
Write-Host ""
Write-Host "Configuration Details:"
Write-Host "  - Account Type: IMAP"
Write-Host "  - Incoming: $imapServer : $imapPort (SSL/TLS)"
Write-Host "  - Outgoing: $smtpServer : $smtpPort (STARTTLS)"
Write-Host ""
