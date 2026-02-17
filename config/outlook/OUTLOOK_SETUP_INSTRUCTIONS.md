# Classic Outlook Setup Guide: Gmail + ProtonMail

## Prerequisites

1. **Microsoft Outlook** (Classic/Desktop version) installed
2. **Proton Bridge** installed and configured (for ProtonMail)
3. **Gmail account** with 2-Factor Authentication enabled (for Gmail)

---

## Part 1: Install and Configure Proton Bridge

### Step 1: Download and Install Proton Bridge

1. Go to: https://proton.me/mail/bridge
2. Download Proton Bridge for Windows
3. Install the application
4. Launch Proton Bridge

### Step 2: Add Your ProtonMail Account to Bridge

1. Open Proton Bridge
2. Click "Add Account" or "Sign In"
3. Enter your ProtonMail email address
4. Enter your ProtonMail password
5. Complete any 2FA verification if enabled
6. Bridge will generate a **Bridge Password** - **SAVE THIS SECURELY**

### Step 3: Verify Bridge is Running

1. Check system tray for Proton Bridge icon
2. Bridge must be running for Outlook to connect to ProtonMail
3. Default ports:
   - **IMAP**: 127.0.0.1:1143 (SSL)
   - **SMTP**: 127.0.0.1:1025 (SSL)

---

## Part 2: Configure Gmail in Outlook

### Step 1: Enable Gmail IMAP Access

1. Go to: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Go to **Security** → **App passwords**
4. Generate a new app password:
   - Select "Mail" as app type
   - Select "Other (Custom name)" as device
   - Enter "Outlook" as name
   - Click "Generate"
   - **COPY THE 16-CHARACTER PASSWORD** (you'll need this)

### Step 2: Add Gmail Account to Outlook

1. Open Outlook
2. Go to **File** → **Account Settings** → **Account Settings**
3. Click **New...**
4. Select **Manual setup or additional server types**
5. Click **Next**
6. Select **POP or IMAP**
7. Click **Next**
8. Fill in the account information:
   - **Your Name**: Your display name
   - **Email Address**: your-email@gmail.com
   - **Account Type**: IMAP
   - **Incoming mail server**: imap.gmail.com
   - **Outgoing mail server (SMTP)**: smtp.gmail.com
   - **User Name**: your-email@gmail.com
   - **Password**: [Use the 16-character App Password from Step 1]
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

## Part 3: Configure ProtonMail in Outlook (via Proton Bridge)

### Step 1: Ensure Proton Bridge is Running

1. Check system tray for Proton Bridge icon
2. If not running, launch Proton Bridge
3. Verify your ProtonMail account is added and active

### Step 2: Get Bridge Connection Details

1. Open Proton Bridge
2. Click on your account
3. Note the connection details:
   - **IMAP Port**: Usually 1143
   - **SMTP Port**: Usually 1025
   - **Username**: Your ProtonMail email address
   - **Password**: Your ProtonMail password (NOT the Bridge password)

### Step 3: Add ProtonMail Account to Outlook

1. Open Outlook
2. Go to **File** → **Account Settings** → **Account Settings**
3. Click **New...**
4. Select **Manual setup or additional server types**
5. Click **Next**
6. Select **POP or IMAP**
7. Click **Next**
8. Fill in the account information:
   - **Your Name**: Your display name
   - **Email Address**: your-email@protonmail.com (or @proton.me)
   - **Account Type**: IMAP
   - **Incoming mail server**: 127.0.0.1
   - **Outgoing mail server (SMTP)**: 127.0.0.1
   - **User Name**: your-email@protonmail.com
   - **Password**: Your ProtonMail password (NOT Bridge password)
9. Click **More Settings...**
10. Go to **Outgoing Server** tab:
    - Check "My outgoing server (SMTP) requires authentication"
    - Select "Use same settings as my incoming mail server"
11. Go to **Advanced** tab:
    - **Incoming server (IMAP)**: 1143 (or port shown in Bridge)
    - **Use the following type of encrypted connection**: SSL/TLS
    - **Outgoing server (SMTP)**: 1025 (or port shown in Bridge)
    - **Use the following type of encrypted connection**: SSL/TLS
12. Click **OK**
13. Click **Next**
14. Outlook will test the connection
15. Click **Finish** when successful

---

## Part 4: Verification and Troubleshooting

### Verify Both Accounts

1. In Outlook, go to **File** → **Account Settings** → **Account Settings**
2. You should see both accounts listed:
   - Gmail (IMAP)
   - ProtonMail (IMAP)
3. Test sending/receiving from both accounts

### Common Issues

#### Gmail Connection Fails
- **Issue**: "Username and password not accepted"
  - **Solution**: Make sure you're using the 16-character App Password, not your regular Gmail password
- **Issue**: "Cannot connect to server"
  - **Solution**: Check internet connection, verify IMAP is enabled in Gmail settings

#### ProtonMail Connection Fails
- **Issue**: "Cannot connect to server"
  - **Solution**: Ensure Proton Bridge is running (check system tray)
  - **Solution**: Verify Bridge ports match Outlook settings (1143 for IMAP, 1025 for SMTP)
- **Issue**: "Username and password not accepted"
  - **Solution**: Use your ProtonMail password, NOT the Bridge password
  - **Solution**: Verify account is properly added in Proton Bridge

#### Outlook Can't Send Emails
- **Gmail**: Verify SMTP port is 587 with STARTTLS
- **ProtonMail**: Verify SMTP port matches Bridge (usually 1025) with SSL/TLS
- Both: Ensure "My outgoing server requires authentication" is checked

---

## Security Notes

1. **Gmail App Passwords**: Store securely, never share
2. **Proton Bridge Password**: Different from ProtonMail password, used only for Bridge app
3. **ProtonMail Password**: Used in Outlook, different from Bridge password
4. **Local Connection**: ProtonMail connects via localhost (127.0.0.1), so Bridge must always be running

---

## Configuration Summary

### Gmail Settings
- **IMAP Server**: imap.gmail.com:993 (SSL)
- **SMTP Server**: smtp.gmail.com:587 (STARTTLS)
- **Authentication**: App Password required

### ProtonMail Settings (via Bridge)
- **IMAP Server**: 127.0.0.1:1143 (SSL)
- **SMTP Server**: 127.0.0.1:1025 (SSL)
- **Authentication**: ProtonMail password (not Bridge password)
- **Requires**: Proton Bridge running

---

## Next Steps

After setup:
1. Test sending emails from both accounts
2. Test receiving emails in both accounts
3. Configure email rules/folders as needed
4. Set default account for sending (if desired)

For automated email management, see: `scripts/python/unified_email_service.py`
