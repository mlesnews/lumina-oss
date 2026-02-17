#!/usr/bin/env python3
"""
Actually Setup New Outlook - Remove Gmail, Add NAS Email

Connects to EXISTING Outlook instance only - NO NEW LAUNCHES.
Uses UI automation to actually perform the setup.
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupNewOutlookActual")

NAS_MAIL_SERVER = "<NAS_PRIMARY_IP>"
NAS_IMAP_PORT = 993
NAS_SMTP_PORT = 587
COMPANY_EMAIL = "mlesn@<LOCAL_HOSTNAME>"

def get_password():
    """Get password from Azure Vault"""
    try:
        vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
        return vault.get_secret("n8n-password")
    except:
        return None

def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("📧 SETTING UP NEW OUTLOOK - REMOVE GMAIL, ADD NAS EMAIL")
    logger.info("="*80)
    logger.info("")
    logger.info("⚠️  IMPORTANT: This script connects to EXISTING Outlook")
    logger.info("   It will NOT launch new Outlook instances")
    logger.info("")

    password = get_password()

    # Check for UI automation
    try:
        import pywinauto
        from pywinauto import Application
        import pyautogui
        UI_AVAILABLE = True
    except ImportError:
        UI_AVAILABLE = False
        logger.error("   ❌ UI automation libraries not installed")
        logger.info("   💡 Installing now...")
        import subprocess
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pywinauto", "pyautogui"], 
                         check=True, capture_output=True)
            logger.info("   ✅ Libraries installed - please run script again")
            return 1
        except:
            logger.error("   ❌ Failed to install libraries")
            logger.info("   💡 Please install manually: pip install pywinauto pyautogui")
            return 1

    logger.info("   ✅ UI automation libraries available")
    logger.info("")
    logger.info("🔍 Connecting to existing New Outlook instance...")
    logger.info("   (Please ensure New Outlook is already open)")
    logger.info("")

    time.sleep(2)

    try:
        # Connect to EXISTING Outlook (connect, don't start)
        # Handle multiple Outlook windows - find the main one
        app = Application(backend="uia")
        try:
            app.connect(title_re=".*Outlook.*", timeout=10)
        except Exception as e:
            if "6 elements" in str(e) or "multiple" in str(e).lower():
                # Multiple windows found - get all and find main window
                logger.info("   ⚠️  Multiple Outlook windows found - finding main window...")
                app = Application(backend="uia")
                # Try to connect by process name instead
                import psutil
                outlook_pids = []
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'outlook' in proc.info['name'].lower() or 'olk' in proc.info['name'].lower():
                        outlook_pids.append(proc.info['pid'])

                if outlook_pids:
                    # Connect to the first Outlook process
                    app.connect(process=outlook_pids[0])
                    logger.info(f"   ✅ Connected to Outlook process: {outlook_pids[0]}")
                else:
                    raise Exception("Could not find Outlook process")
            else:
                raise

        # Get main window (not dialogs)
        windows = app.windows()
        main_window = None
        for window in windows:
            title = window.window_text().lower()
            # Main window is usually the largest or doesn't have "dialog" in title
            if "dialog" not in title and "settings" not in title and "add" not in title:
                if not main_window or window.rectangle().width() > main_window.rectangle().width():
                    main_window = window

        if not main_window:
            main_window = app.top_window()

        logger.info(f"   ✅ Connected to: {main_window.window_text()}")

        # Bring to front
        main_window.set_focus()
        time.sleep(1)

        # STEP 1: Remove Gmail
        logger.info("")
        logger.info("🗑️  STEP 1: Removing Gmail Account")
        logger.info("")

        logger.info("   Opening Account Settings (Ctrl+Shift+A)...")
        pyautogui.hotkey('ctrl', 'shift', 'a')
        time.sleep(4)

        # Find Account Settings dialog
        try:
            account_dialog = None
            # Wait a bit for dialog to appear
            time.sleep(1)
            windows = app.windows()
            logger.info(f"   📊 Checking {len(windows)} windows for Account Settings...")
            for window in windows:
                try:
                    title = window.window_text().lower()
                    logger.debug(f"   Window: {title[:50]}")
                    if "account" in title and "settings" in title:
                        account_dialog = window
                        logger.info(f"   ✅ Found Account Settings: {window.window_text()}")
                        window.set_focus()
                        break
                except:
                    continue

            # If not found, try looking for any dialog that appeared
            if not account_dialog:
                logger.info("   🔍 Account Settings dialog not found by title, searching all dialogs...")
                for window in windows:
                    try:
                        # Check if it's a dialog (not main window)
                        if window != main_window and window.is_visible():
                            title = window.window_text()
                            logger.info(f"   📋 Found dialog: {title}")
                            # If it has account-related controls, use it
                            controls = list(window.descendants())
                            for ctrl in controls[:20]:
                                try:
                                    ctrl_text = ctrl.window_text().lower()
                                    if "account" in ctrl_text or "email" in ctrl_text:
                                        account_dialog = window
                                        logger.info(f"   ✅ Using dialog: {title}")
                                        window.set_focus()
                                        break
                                except:
                                    continue
                            if account_dialog:
                                break
                    except:
                        continue

            if account_dialog:
                logger.info("   🔍 Searching for Gmail account...")
                time.sleep(2)

                # Search all controls for Gmail
                all_controls = account_dialog.descendants()
                for control in all_controls:
                    try:
                        text = control.window_text().lower()
                        if "gmail" in text or "@gmail.com" in text:
                            logger.info(f"   ✅ Found Gmail: {control.window_text()}")
                            control.click_input()
                            time.sleep(1)

                            # Find Remove button
                            buttons = account_dialog.descendants(control_type="Button")
                            for btn in buttons:
                                btn_text = btn.window_text().lower()
                                if "remove" in btn_text or "delete" in btn_text:
                                    logger.info(f"   ✅ Found Remove: {btn.window_text()}")
                                    btn.click_input()
                                    time.sleep(2)
                                    logger.info("   ✅ Clicked Remove")

                                    # Look for confirmation dialog
                                    time.sleep(1)
                                    for confirm_dialog in app.windows():
                                        confirm_title = confirm_dialog.window_text().lower()
                                        if "confirm" in confirm_title or "remove" in confirm_title:
                                            logger.info(f"   ✅ Found confirmation: {confirm_dialog.window_text()}")
                                            # Look for Yes/OK button
                                            confirm_buttons = confirm_dialog.descendants(control_type="Button")
                                            for confirm_btn in confirm_buttons:
                                                confirm_text = confirm_btn.window_text().lower()
                                                if "yes" in confirm_text or "ok" in confirm_text or "remove" in confirm_text:
                                                    logger.info(f"   ✅ Clicking: {confirm_btn.window_text()}")
                                                    confirm_btn.click_input()
                                                    time.sleep(2)
                                                    logger.info("   ✅ Gmail account removed")
                                                    break
                                            break
                                    break
                            break
                    except:
                        continue

                # Close Account Settings
                time.sleep(2)
                try:
                    close_btn = account_dialog.child_window(title="Close", control_type="Button")
                    if close_btn.exists():
                        close_btn.click_input()
                        time.sleep(1)
                except:
                    pyautogui.press('escape')

        except Exception as e:
            logger.debug(f"   Gmail removal: {e}")
            logger.info("   💡 Please manually remove Gmail account")

        logger.info("")
        logger.info("   ⏳ Waiting 3 seconds...")
        time.sleep(3)

        # STEP 2: Add NAS email
        logger.info("")
        logger.info("➕ STEP 2: Adding NAS Company Email")
        logger.info("")

        logger.info("   Opening Add Account (File menu)...")
        pyautogui.hotkey('alt', 'f')
        time.sleep(1)

        # Navigate to Add Account
        pyautogui.press('a')  # Add Account
        time.sleep(4)
        logger.info("   ✅ Add Account dialog should be open")

        # Find Add Account dialog
        try:
            add_dialog = None
            for window in app.windows():
                title = window.window_text().lower()
                if ("add" in title and "account" in title) or "email" in title or "setup" in title:
                    add_dialog = window
                    logger.info(f"   ✅ Found: {window.window_text()}")
                    window.set_focus()
                    break

            if add_dialog:
                # Look for Advanced/Manual setup button
                time.sleep(1)
                buttons = add_dialog.descendants(control_type="Button")
                for btn in buttons:
                    btn_text = btn.window_text().lower()
                    if "advanced" in btn_text or "manual" in btn_text:
                        logger.info(f"   ✅ Found: {btn.window_text()}")
                        btn.click_input()
                        time.sleep(2)
                        break

                # Look for IMAP option (radio button or button)
                time.sleep(1)
                options = add_dialog.descendants()
                for opt in options:
                    opt_text = opt.window_text().lower()
                    if "imap" in opt_text:
                        logger.info(f"   ✅ Found IMAP")
                        opt.click_input()
                        time.sleep(1)
                        break

                # Fill email field
                time.sleep(1)
                pyautogui.write(COMPANY_EMAIL, interval=0.1)
                time.sleep(1)
                logger.info(f"   ✅ Entered email: {COMPANY_EMAIL}")

                # Tab to password and enter
                if password:
                    pyautogui.press('tab')
                    time.sleep(0.5)
                    pyautogui.write(password, interval=0.05)
                    time.sleep(1)
                    logger.info("   ✅ Entered password")

                # Look for Advanced Options/More Settings
                time.sleep(1)
                advanced_buttons = add_dialog.descendants(control_type="Button")
                for btn in advanced_buttons:
                    btn_text = btn.window_text().lower()
                    if "advanced" in btn_text or "more" in btn_text:
                        logger.info(f"   ✅ Found: {btn.window_text()}")
                        btn.click_input()
                        time.sleep(2)
                        break

                # Fill IMAP server settings
                time.sleep(1)
                # Navigate to IMAP server field (may need multiple tabs)
                for _ in range(4):
                    pyautogui.press('tab')
                    time.sleep(0.2)

                pyautogui.write(NAS_MAIL_SERVER, interval=0.1)
                time.sleep(0.5)
                pyautogui.press('tab')
                pyautogui.write(str(NAS_IMAP_PORT), interval=0.1)
                logger.info(f"   ✅ Entered IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT}")

                # Navigate to SMTP settings
                time.sleep(1)
                for _ in range(2):
                    pyautogui.press('tab')
                    time.sleep(0.2)

                pyautogui.write(NAS_MAIL_SERVER, interval=0.1)
                time.sleep(0.5)
                pyautogui.press('tab')
                pyautogui.write(str(NAS_SMTP_PORT), interval=0.1)
                logger.info(f"   ✅ Entered SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT}")

                # Look for Connect/Finish button
                time.sleep(1)
                connect_buttons = add_dialog.descendants(control_type="Button")
                for btn in connect_buttons:
                    btn_text = btn.window_text().lower()
                    if "connect" in btn_text or "finish" in btn_text or "next" in btn_text:
                        logger.info(f"   ✅ Found: {btn.window_text()}")
                        btn.click_input()
                        time.sleep(3)
                        logger.info("   ✅ Clicked Connect/Finish")
                        break

        except Exception as e:
            logger.debug(f"   Add Account: {e}")
            logger.info("   💡 Please complete setup manually")

        logger.info("")
        logger.info("="*80)
        logger.info("✅ SETUP ATTEMPTED")
        logger.info("="*80)
        logger.info("")
        logger.info("💡 Please verify:")
        logger.info("   • Gmail account removed")
        logger.info(f"   • NAS email ({COMPANY_EMAIL}) added")
        logger.info("")

    except Exception as e:
        logger.error(f"   ❌ Could not connect to Outlook: {e}")
        logger.info("   💡 Please ensure New Outlook is open")
        logger.info("   💡 Then run this script again")
        return 1

    return 0

if __name__ == "__main__":


    exit(main())