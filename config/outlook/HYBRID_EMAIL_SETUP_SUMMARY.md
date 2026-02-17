# Hybrid Email System Setup Summary

## Architecture Overview

```
┌─────────┐      ┌──────────────┐
│ Gmail   │─────→│              │
└─────────┘      │  NAS Mail    │      ┌──────────────┐
                 │     Hub      │─────→│   Outlook    │
┌─────────────┐  │ (<NAS_PRIMARY_IP>)│      │   Classic    │
│ ProtonMail  │─→│              │      └──────────────┘
│ (via Bridge)│  └──────────────┘
└─────────────┘
```

**Flow:**
1. Gmail emails are imported to NAS Mail Hub
2. ProtonMail emails (via Proton Bridge) are imported to NAS Mail Hub
3. Outlook Classic connects to NAS Mail Hub to receive ALL emails in one unified inbox

---

## Configuration Files Generated

### 1. Hybrid Email Configuration
**File:** `config/outlook/hybrid_email_config.json`

Contains complete configuration for:
- NAS Mail Hub settings (<NAS_PRIMARY_IP>)
- ProtonMail Bridge settings (from your screenshot)
- Gmail settings
- Outlook Classic connection settings
- Import schedules

### 2. Outlook NAS Hub Setup Instructions
**File:** `config/outlook/OUTLOOK_NAS_HUB_SETUP.md`

Step-by-step instructions for connecting Outlook Classic to NAS Mail Hub.

### 3. NAS Hub Import Configuration
**File:** `config/outlook/nas_hub_import_config.json`

Configuration for importing Gmail and ProtonMail emails to NAS Mail Hub.

---

## ProtonMail Bridge Settings (From Screenshot)

**Account:** mlesnews@protonmail.com

### IMAP Settings
- **Hostname:** 127.0.0.1
- **Port:** 1143
- **Security:** STARTTLS
- **Username:** mlesnews@protonmail.com
- **Password:** 9n5m3Hn_8PhRcG8KeXKo0w

### SMTP Settings
- **Hostname:** 127.0.0.1
- **Port:** 1025
- **Security:** STARTTLS
- **Username:** mlesnews@protonmail.com
- **Password:** 9n5m3Hn_8PhRcG8KeXKo0w

**Note:** Proton Bridge must be running on your PC for these settings to work.

---

## NAS Mail Hub Settings

**Server:** <NAS_PRIMARY_IP>  
**Domain:** <LOCAL_HOSTNAME>  
**Webmail:** https://<NAS_PRIMARY_IP>:5001/mailplus

### IMAP Settings (for Outlook Classic)
- **Server:** <NAS_PRIMARY_IP>
- **Port:** 993
- **Encryption:** SSL/TLS
- **Username:** mlesn@<LOCAL_HOSTNAME>

### SMTP Settings (for Outlook Classic)
- **Server:** <NAS_PRIMARY_IP>
- **Port:** 587
- **Encryption:** STARTTLS
- **Username:** mlesn@<LOCAL_HOSTNAME>

---

## Setup Steps

### Step 1: Verify Proton Bridge is Running
1. Check system tray for Proton Bridge icon
2. Verify account `mlesnews@protonmail.com` is connected
3. Note: Bridge must be running for email import to work

### Step 2: Set Up Email Import to NAS Hub
Run the import script to start importing emails:

```bash
# Test import (last 7 days)
python scripts/python/import_emails_to_nas_hub.py --days-back 7

# Full import (last year)
python scripts/python/import_emails_to_nas_hub.py --days-back 365
```

### Step 3: Configure Outlook Classic
Follow the detailed instructions in: `config/outlook/OUTLOOK_NAS_HUB_SETUP.md`

**Quick Summary:**
1. Open Outlook
2. File → Account Settings → Account Settings → New
3. Manual setup → POP or IMAP
4. Enter NAS Mail Hub settings:
   - Email: mlesn@<LOCAL_HOSTNAME>
   - IMAP: <NAS_PRIMARY_IP>:993 (SSL/TLS)
   - SMTP: <NAS_PRIMARY_IP>:587 (STARTTLS)
5. Test connection

### Step 4: Verify Setup
1. Check NAS Mail Hub webmail: https://<NAS_PRIMARY_IP>:5001/mailplus
2. Verify emails from Gmail and ProtonMail are present
3. Check Outlook Classic inbox for unified emails
4. Monitor import logs: `data/email_import/`

---

## Gmail Setup (If Not Already Done)

### Generate Gmail App Password
1. Go to: https://myaccount.google.com/
2. Security → 2-Step Verification (enable if needed)
3. Security → App passwords
4. Generate app password for "Mail" → "Other (Outlook)"
5. **Save the 16-character password** - you'll need it for email import

### Store Gmail Credentials (Optional)
Store in Azure Key Vault for automated import:
- `gmail-email` - Your Gmail address
- `gmail-app-password` - The 16-character app password

---

## Scheduled Import (Recommended)

Set up automatic email import every 15 minutes:

1. Review: `config/outlook/import_daemon_config.json`
2. Set up Windows Task Scheduler:
   - Program: `python`
   - Arguments: `scripts/python/import_emails_to_nas_hub.py --days-back 30`
   - Schedule: Every 15 minutes
3. Or use JARVIS daemon system

---

## Troubleshooting

### Proton Bridge Not Working
- **Issue:** Cannot connect to Proton Bridge
- **Solution:** Ensure Proton Bridge is running (check system tray)
- **Solution:** Verify Bridge password matches: `9n5m3Hn_8PhRcG8KeXKo0w`
- **Solution:** Check Bridge ports: 1143 (IMAP), 1025 (SMTP)

### Gmail Import Fails
- **Issue:** Gmail authentication fails
- **Solution:** Use Gmail App Password (not regular password)
- **Solution:** Verify 2FA is enabled on Gmail account
- **Solution:** Check Gmail IMAP is enabled in settings

### Outlook Cannot Connect to NAS Hub
- **Issue:** Cannot connect to <NAS_PRIMARY_IP>
- **Solution:** Verify NAS Mail Hub is running (check webmail)
- **Solution:** Check network connectivity to NAS
- **Solution:** Verify firewall allows ports 993 (IMAP) and 587 (SMTP)
- **Solution:** Verify username: mlesn@<LOCAL_HOSTNAME>

### No Emails in Outlook
- **Issue:** Outlook connected but no emails visible
- **Solution:** Verify email import is running and successful
- **Solution:** Check NAS Mail Hub webmail for imported emails
- **Solution:** Verify import logs show successful imports
- **Solution:** Check Outlook folder sync settings

---

## Files Reference

### Configuration Files
- `config/outlook/hybrid_email_config.json` - Complete hybrid email configuration
- `config/outlook/nas_hub_import_config.json` - NAS Hub import configuration
- `config/outlook/import_daemon_config.json` - Scheduled import daemon config

### Instructions
- `config/outlook/OUTLOOK_NAS_HUB_SETUP.md` - Outlook Classic setup guide
- `config/outlook/OUTLOOK_SETUP_INSTRUCTIONS.md` - Original Outlook setup (direct connection)

### Scripts
- `scripts/python/setup_hybrid_email_to_nas_hub.py` - Main setup script
- `scripts/python/import_emails_to_nas_hub.py` - Email import script
- `scripts/python/setup_outlook_and_nas_import.py` - Combined setup script

---

## Next Steps

1. ✅ **Configuration Complete** - All config files generated
2. ⏳ **Set Up Email Import** - Run import script to start syncing emails
3. ⏳ **Configure Outlook Classic** - Follow setup instructions
4. ⏳ **Set Up Scheduled Import** - Automate email syncing
5. ⏳ **Verify & Monitor** - Check all emails are flowing correctly

---

## Support

For issues or questions:
- Check import logs: `data/email_import/`
- Review configuration files in `config/outlook/`
- Check NAS Mail Hub webmail interface
- Monitor Proton Bridge status

**Setup Date:** 2026-01-05  
**Status:** ✅ Configuration Complete - Ready for Import Setup
