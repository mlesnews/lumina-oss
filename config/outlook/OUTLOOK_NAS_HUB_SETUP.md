# Outlook Classic Setup: Connect to NAS Mail Hub

## Overview

This setup connects Outlook Classic to your **NAS Mail Hub** (not directly to Gmail/ProtonMail).
All emails from Gmail and ProtonMail are imported to the NAS Mail Hub, and Outlook Classic
receives all emails from the hub.

## Architecture

```
Gmail ──┐
        ├──→ NAS Mail Hub ──→ Outlook Classic
ProtonMail ──┘
```

## Prerequisites

1. **Microsoft Outlook** (Classic/Desktop version) installed
2. **NAS Mail Hub** configured and running (<NAS_PRIMARY_IP>)
3. **Gmail and ProtonMail** emails being imported to NAS Mail Hub
4. **Company email account** on NAS Mail Hub (mlesn@<LOCAL_HOSTNAME>)

---

## Step 1: Verify NAS Mail Hub Access

1. Open web browser
2. Navigate to: https://<NAS_PRIMARY_IP>:5001/mailplus
3. Log in with your company email account
4. Verify you can see emails from Gmail and ProtonMail

---

## Step 2: Add NAS Mail Hub Account to Outlook

1. Open Outlook
2. Go to **File** → **Account Settings** → **Account Settings**
3. Click **New...**
4. Select **Manual setup or additional server types**
5. Click **Next**
6. Select **POP or IMAP**
7. Click **Next**
8. Fill in the account information:
   - **Your Name**: Your display name
   - **Email Address**: mlesn@<LOCAL_HOSTNAME>
   - **Account Type**: IMAP
   - **Incoming mail server**: <NAS_PRIMARY_IP>
   - **Outgoing mail server (SMTP)**: <NAS_PRIMARY_IP>
   - **User Name**: mlesn@<LOCAL_HOSTNAME>
   - **Password**: [Your NAS Mail Hub password]
9. Click **More Settings...**
10. Go to **Outgoing Server** tab:
    - Check "My outgoing server (SMTP) requires authentication"
    - Select "Use same settings as my incoming mail server"
11. Go to **Advanced** tab:
    - **Incoming server (IMAP)**: 993
    - **Use the following type of encrypted connection**: SSL/TLS
    - **Outgoing server (SMTP)**: 587
    - **Use the following type of encrypted connection**: STARTTLS
12. Click **OK**
13. Click **Next**
14. Outlook will test the connection
15. Click **Finish** when successful

---

## Step 3: Verify Email Reception

1. In Outlook, check your inbox
2. You should see emails from:
   - Gmail (imported to NAS Mail Hub)
   - ProtonMail (imported to NAS Mail Hub)
   - Company email (direct to NAS Mail Hub)
3. All emails are now in one unified inbox

---

## Step 4: Configure Email Folders (Optional)

1. In Outlook, organize emails by creating folders:
   - Gmail
   - ProtonMail
   - Company
2. Set up rules to automatically organize emails by source

---

## Troubleshooting

### Cannot Connect to NAS Mail Hub
- **Issue**: "Cannot connect to server"
  - **Solution**: Verify NAS Mail Hub is running (check webmail interface)
  - **Solution**: Check network connectivity to <NAS_PRIMARY_IP>
  - **Solution**: Verify firewall allows connections on ports 993 (IMAP) and 587 (SMTP)

### Authentication Fails
- **Issue**: "Username and password not accepted"
  - **Solution**: Verify username is: mlesn@<LOCAL_HOSTNAME>
  - **Solution**: Verify password is correct for NAS Mail Hub account
  - **Solution**: Check if account exists in NAS Mail Hub

### No Emails from Gmail/ProtonMail
- **Issue**: Only seeing company emails, not Gmail/ProtonMail
  - **Solution**: Verify email import system is running
  - **Solution**: Check import logs: data/email_import/
  - **Solution**: Verify Gmail and ProtonMail are configured in import system

---

## Configuration Summary

### NAS Mail Hub Settings
- **IMAP Server**: <NAS_PRIMARY_IP>:993 (SSL/TLS)
- **SMTP Server**: <NAS_PRIMARY_IP>:587 (STARTTLS)
- **Username**: mlesn@<LOCAL_HOSTNAME>
- **Webmail**: https://<NAS_PRIMARY_IP>:5001/mailplus

### Email Sources (Imported to NAS Mail Hub)
- **Gmail**: Imported via IMAP every 15 minutes
- **ProtonMail**: Imported via Proton Bridge every 15 minutes

---

## Next Steps

1. Set up email import daemon to continuously sync Gmail/ProtonMail to NAS Mail Hub
2. Configure email rules in Outlook for organization
3. Set up email archiving and backup
4. Monitor import logs for any issues

For email import setup, see: `scripts/python/import_emails_to_nas_hub.py`
