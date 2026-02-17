#!/usr/bin/env python3
"""
Azure Authentication Helper
Helps troubleshoot Azure sign-in and two-step verification issues
"""
import webbrowser
from pathlib import Path

print("=" * 80)
print("🔐 Azure Authentication Helper")
print("=" * 80)

print("\n📋 Common Solutions for Two-Step Verification Issues:")
print("\n1. Not receiving verification codes:")
print("   - Check junk/spam folder for @accountprotection.microsoft.com")
print("   - Verify phone number is correct (not VOIP)")
print("   - Try alternate verification method")
print("   - Wait if you've made excessive requests (may be temporarily blocked)")

print("\n2. 'Try another verification method' message:")
print("   - Switch verification method (SMS → Email or vice versa)")
print("   - Try different network (Wi-Fi vs cellular)")
print("   - Wait 24 hours if blocked due to unusual activity")

print("\n3. Lost access to security info:")
print("   - Sign in to: https://mysignins.microsoft.com/security-info")
print("   - Add new verification method")
print("   - Remove old one (don't remove all at once)")

print("\n4. Account locked or restricted:")
print("   - Contact IT administrator")
print("   - Check Microsoft Entra sign-in logs")
print("   - Wait for automatic resolution (can take up to 1 week)")

print("\n🌐 Opening Azure Portal...")
try:
    webbrowser.open("https://portal.azure.com")
    print("✅ Azure Portal opened")
except:
    print("⚠️  Could not open browser - go to: https://portal.azure.com")

print("\n🔗 Useful Links:")
print("   Security Info: https://mysignins.microsoft.com/security-info")
print("   Account Recovery: https://account.live.com/acsr")
print("   Azure Portal: https://portal.azure.com")

print("\n💡 Tip: Use Microsoft Authenticator app for easier verification")
