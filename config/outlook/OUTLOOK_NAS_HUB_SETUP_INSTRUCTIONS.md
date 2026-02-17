# Outlook Classic Setup: Connect to NAS Mail Hub

## Overview
Outlook Classic connects to **NAS Mail Hub** which aggregates emails from:
- Gmail (synced automatically)
- ProtonMail via Proton Bridge (synced automatically)

You do NOT configure Gmail or ProtonMail directly in Outlook - only the NAS Mail Hub account.

---

## Step 1: Add NAS Mail Hub Account to Outlook

1. Open Outlook Classic
2. Go to **File** → **Account Settings** → **Account Settings**
3. Click **New...**
4. Select **Manual setup or additional server types**
5. Click **Next**
6. Select **POP or IMAP**
7. Click **Next**
8. Fill in account information:
   - **Your Name**: Your display name (e.g., "mlesn")
   - **Email Address**: `mlesn@<LOCAL_HOSTNAME>`
   - **Account Type**: IMAP
   - **Incoming mail server**: `<NAS_PRIMARY_IP>`
   - **Outgoing mail server (SMTP)**: `<NAS_PRIMARY_IP>`
   - **User Name**: `mlesn`
   - **Password**: [Your NAS MailPlus account password]
9. Click **More Settings...**
10. Go to **Outgoing Server** tab:
    - ✅ Check "My outgoing server (SMTP) requires authentication"
    - Select "Use same settings as my incoming mail server"
11. Go to **Advanced** tab:
    - **Incoming server (IMAP)**: `993`
    - **Use the following type of encrypted connection**: SSL/TLS
    - **Outgoing server (SMTP)**: `587`
    - **Use the following type of encrypted connection**: STARTTLS
12. Click **OK**
13. Click **Next**
14. Outlook will test the connection
15. Click **Finish** when successful

---

## Step 2: Verify Email Sync

After setup, you should see:
- Emails from Gmail (synced to NAS Mail Hub)
- Emails from ProtonMail (synced to NAS Mail Hub)
- All emails in one unified inbox

---

## Step 3: Sending Emails

When sending emails from Outlook:
- Emails are sent via NAS Mail Hub SMTP
- You can send from: `mlesn@<LOCAL_HOSTNAME>`
- Replies will appear to come from your company email address

---

## Troubleshooting

### Cannot Connect to NAS Mail Hub
- Verify NAS MailPlus is running: https://<NAS_PRIMARY_IP>:5001/mailplus
- Check network connectivity to <NAS_PRIMARY_IP>
- Verify IMAP/SMTP ports are open (993, 587)
- Check username and password are correct

### Not Receiving Gmail/ProtonMail Emails
- Verify email sync daemon is running
- Check sync configuration: `config/outlook/email_sync_to_nas_config.json`
- Verify Gmail App Password is configured
- Verify Proton Bridge is running and connected

### Sending Emails Fails
- Verify SMTP authentication is enabled
- Check SMTP port is 587 with STARTTLS
- Verify NAS MailPlus SMTP service is running

---

## Configuration Files

- Outlook NAS Hub Config: `config/outlook/outlook_nas_hub_config.json`
- Email Sync Config: `config/outlook/email_sync_to_nas_config.json`
- Import Config: `config/outlook/nas_import_config.json`

---

## Next Steps

1. ✅ Outlook is now connected to NAS Mail Hub
2. ✅ Gmail emails are syncing to NAS Mail Hub automatically
3. ✅ ProtonMail emails are syncing to NAS Mail Hub automatically
4. ✅ All emails appear in Outlook from NAS Mail Hub

For email sync status, check: `data/email_import/sync_status.json`
