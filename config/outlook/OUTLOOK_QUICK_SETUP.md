# Outlook Classic - Quick Setup Card

## 🎯 Goal
Connect Outlook Classic to NAS Mail Hub to receive all emails (Gmail + ProtonMail + Company)

---

## ⚡ Quick Setup Steps

### 1. Open Outlook Account Settings
- **File** → **Account Settings** → **Account Settings**

### 2. Add New Account
- Click **New...**
- Select **Manual setup or additional server types**
- Click **Next**
- Select **POP or IMAP**
- Click **Next**

### 3. Enter These Exact Settings

**User Information:**
- **Your Name:** [Your Name]
- **Email Address:** `mlesn@<LOCAL_HOSTNAME>`

**Server Information:**
- **Account Type:** `IMAP` (select from dropdown)
- **Incoming mail server:** `<NAS_PRIMARY_IP>`
- **Outgoing mail server (SMTP):** `<NAS_PRIMARY_IP>`

**Logon Information:**
- **User Name:** `mlesn@<LOCAL_HOSTNAME>`
- **Password:** [Your NAS Mail Hub password]

### 4. Advanced Settings

Click **More Settings...**

**Outgoing Server Tab:**
- ☑️ Check **"My outgoing server (SMTP) requires authentication"**
- Select **"Use same settings as my incoming mail server"**

**Advanced Tab:**
- **Incoming server (IMAP):**
  - Port: `993`
  - ☑️ **"This server requires an encrypted connection (SSL/TLS)"**
  - Encryption: `SSL/TLS`
- **Outgoing server (SMTP):**
  - Port: `587`
  - ☑️ **"This server requires an encrypted connection"**
  - Encryption: `STARTTLS`
- Click **OK**

### 5. Test & Finish
- Click **Next** (Outlook will test connection)
- If successful, click **Finish**

---

## ✅ Verification

1. Check Account Settings:
   - Should see: `mlesn@<LOCAL_HOSTNAME>`
   - Type: IMAP

2. Check Inbox:
   - Should see emails from Gmail, ProtonMail, and Company

3. Test Send/Receive:
   - Press **F9** to sync
   - Check for new emails

---

## 🔧 Settings Summary

| Setting | Value |
|---------|-------|
| Email | mlesn@<LOCAL_HOSTNAME> |
| Account Type | IMAP |
| Incoming Server | <NAS_PRIMARY_IP> |
| Incoming Port | 993 |
| Incoming Encryption | SSL/TLS |
| Outgoing Server | <NAS_PRIMARY_IP> |
| Outgoing Port | 587 |
| Outgoing Encryption | STARTTLS |
| Username | mlesn@<LOCAL_HOSTNAME> |
| Authentication | Required (same as incoming) |

---

## 🚨 Troubleshooting

**Can't connect?**
- Verify NAS Mail Hub is running: https://<NAS_PRIMARY_IP>:5001/mailplus
- Check network: `ping <NAS_PRIMARY_IP>`
- Verify firewall allows ports 993 and 587

**Wrong password?**
- Verify password in NAS Mail Hub webmail
- Check username: `mlesn@<LOCAL_HOSTNAME>`

**No emails?**
- Run email import: `python scripts/python/import_emails_to_nas_hub.py --days-back 365`
- Check NAS Mail Hub webmail for emails
- Press F9 in Outlook to sync

---

**For detailed instructions:** See `OUTLOOK_DETAILED_SETUP_GUIDE.md`
