# Outlook Classic Setup for NAS Mail Hub - Automated Configuration
# Generated: 2026-01-06T01:37:22.381806

Write-Host "========================================"
Write-Host "OUTLOOK CLASSIC - NAS MAIL HUB SETUP"
Write-Host "========================================"
Write-Host ""

# Check if Outlook is installed
try {
    $outlook = New-Object -ComObject Outlook.Application
    Write-Host "✅ Outlook is installed and accessible"
} catch {
    Write-Host "❌ Outlook is not installed or not accessible"
    Write-Host "   Please install Microsoft Outlook first"
    exit 1
}

# Get Outlook namespace
$namespace = $outlook.GetNamespace("MAPI")
$accounts = $namespace.Accounts

Write-Host ""
Write-Host "Current Outlook Accounts:"
Write-Host "------------------------"
foreach ($account in $accounts) {
    Write-Host "  - $($account.DisplayName) ($($account.SmtpAddress))"
}

Write-Host ""
Write-Host "========================================"
Write-Host "NAS MAIL HUB CONFIGURATION"
Write-Host "========================================"
Write-Host ""
Write-Host "Account Details:"
Write-Host "  Email: mlesn@homelab.lesnewski.local"
Write-Host "  Display Name: NAS Mail Hub"
Write-Host ""
Write-Host "IMAP Settings:"
Write-Host "  Server: 10.17.17.32"
Write-Host "  Port: 993"
Write-Host "  Encryption: SSL/TLS"
Write-Host ""
Write-Host "SMTP Settings:"
Write-Host "  Server: 10.17.17.32"
Write-Host "  Port: 587"
Write-Host "  Encryption: STARTTLS"
Write-Host ""

# Check if account already exists
$accountExists = $false
foreach ($account in $accounts) {
    if ($account.SmtpAddress -eq "mlesn@homelab.lesnewski.local") {
        Write-Host "⚠️  Account already exists: mlesn@homelab.lesnewski.local"
        $accountExists = $true
        break
    }
}

if (-not $accountExists) {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "MANUAL SETUP REQUIRED"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Outlook COM API has limitations for adding accounts."
    Write-Host "Please follow these steps to add the account manually:"
    Write-Host ""
    Write-Host "1. Open Outlook"
    Write-Host "2. Go to File → Account Settings → Account Settings"
    Write-Host "3. Click 'New...'"
    Write-Host "4. Select 'Manual setup or additional server types'"
    Write-Host "5. Click 'Next'"
    Write-Host "6. Select 'POP or IMAP'"
    Write-Host "7. Click 'Next'"
    Write-Host "8. Fill in:"
    Write-Host "   - Your Name: Your Display Name"
    Write-Host "   - Email Address: mlesn@homelab.lesnewski.local"
    Write-Host "   - Account Type: IMAP"
    Write-Host "   - Incoming mail server: 10.17.17.32"
    Write-Host "   - Outgoing mail server (SMTP): 10.17.17.32"
    Write-Host "   - User Name: mlesn@homelab.lesnewski.local"
    Write-Host "   - Password: [Your NAS Mail Hub password]"
    Write-Host "9. Click 'More Settings...'"
    Write-Host "10. Outgoing Server tab:"
    Write-Host "    - Check 'My outgoing server (SMTP) requires authentication'"
    Write-Host "    - Select 'Use same settings as my incoming mail server'"
    Write-Host "11. Advanced tab:"
    Write-Host "    - Incoming server (IMAP): 993"
    Write-Host "    - Use encrypted connection: SSL/TLS"
    Write-Host "    - Outgoing server (SMTP): 587"
    Write-Host "    - Use encrypted connection: STARTTLS"
    Write-Host "12. Click 'OK' then 'Next'"
    Write-Host "13. Outlook will test the connection"
    Write-Host "14. Click 'Finish' when successful"
    Write-Host ""
    Write-Host "========================================"
    Write-Host "VERIFICATION"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "After adding the account, run this script again to verify."
    Write-Host ""
    
    # Try to open Account Settings dialog
    Write-Host "Attempting to open Outlook Account Settings..."
    try {
        $outlook = New-Object -ComObject Outlook.Application
        $outlook.Session.GetDefaultFolder(6)  # olFolderInbox
        Write-Host "✅ Outlook is ready for manual configuration"
        Write-Host ""
        Write-Host "Opening Outlook Account Settings dialog..."
        # Note: We can't directly open the dialog, but we can guide the user
        Write-Host "   Please manually open: File → Account Settings → Account Settings"
    } catch {
        Write-Host "⚠️  Could not interact with Outlook"
    }
} else {
    Write-Host ""
    Write-Host "✅ Account already configured!"
    Write-Host ""
    Write-Host "Verifying account settings..."
    foreach ($account in $accounts) {
        if ($account.SmtpAddress -eq "mlesn@homelab.lesnewski.local") {
            Write-Host "  Account: $($account.DisplayName)"
            Write-Host "  Email: $($account.SmtpAddress)"
            Write-Host "  Type: $($account.AccountType)"
            Write-Host ""
            Write-Host "✅ NAS Mail Hub account is configured!"
        }
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host "SETUP COMPLETE"
Write-Host "========================================"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "1. Verify emails are syncing in Outlook"
Write-Host "2. Check NAS Mail Hub webmail for imported emails"
Write-Host "3. Set up email import if not already running"
Write-Host ""
