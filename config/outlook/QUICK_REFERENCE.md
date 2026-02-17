# Hybrid Email System - Quick Reference

## 🎯 Architecture
```
Gmail + ProtonMail → NAS Mail Hub → Outlook Classic
```

---

## 📧 Outlook Classic Settings (Connect to NAS Mail Hub)

**Account Type:** IMAP

### Incoming Mail (IMAP)
- **Server:** <NAS_PRIMARY_IP>
- **Port:** 993
- **Encryption:** SSL/TLS
- **Username:** mlesn@<LOCAL_HOSTNAME>

### Outgoing Mail (SMTP)
- **Server:** <NAS_PRIMARY_IP>
- **Port:** 587
- **Encryption:** STARTTLS
- **Username:** mlesn@<LOCAL_HOSTNAME>

---

## 🔐 ProtonMail Bridge Settings

**Account:** mlesnews@protonmail.com  
**Bridge Password:** 9n5m3Hn_8PhRcG8KeXKo0w

### IMAP (via Bridge)
- **Server:** 127.0.0.1
- **Port:** 1143
- **Security:** STARTTLS
- **Username:** mlesnews@protonmail.com
- **Password:** 9n5m3Hn_8PhRcG8KeXKo0w

### SMTP (via Bridge)
- **Server:** 127.0.0.1
- **Port:** 1025
- **Security:** STARTTLS
- **Username:** mlesnews@protonmail.com
- **Password:** 9n5m3Hn_8PhRcG8KeXKo0w

**⚠️ Note:** Proton Bridge must be running!

---

## 📬 NAS Mail Hub

- **Server:** <NAS_PRIMARY_IP>
- **Domain:** <LOCAL_HOSTNAME>
- **Webmail:** https://<NAS_PRIMARY_IP>:5001/mailplus
- **Account:** mlesn@<LOCAL_HOSTNAME>

---

## 📥 Gmail Settings (for Import)

### IMAP
- **Server:** imap.gmail.com
- **Port:** 993
- **Security:** SSL
- **Requires:** App Password (16-char)

### SMTP
- **Server:** smtp.gmail.com
- **Port:** 587
- **Security:** STARTTLS
- **Requires:** App Password (16-char)

**Generate App Password:** https://myaccount.google.com/apppasswords

---

## 🚀 Quick Commands

### Run Email Import
```bash
# Test (7 days)
python scripts/python/import_emails_to_nas_hub.py --days-back 7

# Full (1 year)
python scripts/python/import_emails_to_nas_hub.py --days-back 365
```

### Check Setup
```bash
python scripts/python/setup_hybrid_email_to_nas_hub.py
```

---

## 📁 Key Files

- **Setup Instructions:** `config/outlook/OUTLOOK_NAS_HUB_SETUP.md`
- **Full Summary:** `config/outlook/HYBRID_EMAIL_SETUP_SUMMARY.md`
- **Configuration:** `config/outlook/hybrid_email_config.json`

---

## ✅ Verification Checklist

- [ ] Proton Bridge running and connected
- [ ] Gmail App Password generated
- [ ] Email import script tested
- [ ] NAS Mail Hub accessible (webmail)
- [ ] Outlook Classic connected to NAS Mail Hub
- [ ] Emails visible in Outlook inbox
- [ ] Scheduled import configured (optional)

---

**Last Updated:** 2026-01-05
