#!/usr/bin/env python3
"""
Test Auto-Accept "Keep All" Button - Diagnostic Tool

Run this to test if auto-accept is working and diagnose issues.

Tags: #TESTING #DIAGNOSTICS #AUTO_ACCEPT #LUMINA_CORE
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger("TestAutoAccept")


def test_auto_accept():
    """Test auto-accept functionality"""
    print("\n" + "="*80)
    print("🧪 Testing Auto-Accept 'Keep All' Button Functionality")
    print("="*80 + "\n")

    try:
        from cursor_ide_auto_accept import CursorIDEAutoAccept
        auto_accept = CursorIDEAutoAccept()

        # Test 1: Check if Cursor IDE is running
        print("1. Checking if Cursor IDE is running...")
        is_running = auto_accept._is_cursor_running()
        if is_running:
            print("   ✅ Cursor IDE is running")
        else:
            print("   ⚠️  Cursor IDE not detected")
            print("   💡 Make sure Cursor IDE is open")
            return False

        # Test 2: Check UI libraries
        print("\n2. Checking UI automation libraries...")
        if auto_accept.ui_available:
            print("   ✅ pyautogui and pywinauto available")
        else:
            print("   ⚠️  UI libraries not available")
            print("   💡 Install: pip install pyautogui pywinauto")
            print("   ⚠️  Will only use keyboard shortcuts")

        # Test 3: Check keyboard library
        print("\n3. Checking keyboard library...")
        try:
            import keyboard
            print("   ✅ keyboard library available")
        except ImportError:
            print("   ⚠️  keyboard library not available")
            print("   💡 Install: pip install keyboard")
            return False

        # Test 4: Test cooldown/rate limiting
        print("\n4. Testing cooldown and rate limiting...")
        should_accept = auto_accept._should_accept()
        if should_accept:
            print("   ✅ Can accept (no cooldown active)")
        else:
            print("   ⚠️  Cooldown active - will wait")

        # Test 5: Try to detect and accept (verbose mode)
        print("\n5. Attempting to detect 'Keep All' dialog...")
        print("   💡 If a 'Keep All' / 'Accept All Changes' dialog is open, it should be detected now")
        print("   💡 This will try keyboard shortcuts and UI automation")
        print()

        accepted = auto_accept.detect_and_accept_changes(verbose=True)

        if accepted:
            print("\n   ✅ SUCCESS: Changes were accepted automatically!")
            print(f"   📊 Acceptance count: {auto_accept.acceptance_count}")
            return True
        else:
            print("\n   ⚠️  No dialog detected or acceptance failed")
            print("   💡 Make sure:")
            print("      - A 'Keep All' / 'Accept All Changes' dialog is open in Cursor IDE")
            print("      - Cursor IDE window is focused/active")
            print("      - The dialog is visible")
            return False

    except ImportError as e:
        print(f"\n   ❌ Failed to import auto-accept module: {e}")
        return False
    except Exception as e:
        print(f"\n   ❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_keyboard_shortcuts():
    """Test keyboard shortcuts directly"""
    print("\n" + "="*80)
    print("⌨️  Testing Keyboard Shortcuts")
    print("="*80 + "\n")

    try:
        import keyboard
        print("✅ keyboard library available")

        shortcuts = [
            'ctrl+alt+enter',
            'ctrl+shift+enter',
            'alt+enter'
        ]

        print("\n💡 Testing keyboard shortcuts...")
        print("   These will be sent to the active window (Cursor IDE should be focused)")
        print("   Press Ctrl+C to cancel\n")

        for i, shortcut in enumerate(shortcuts, 1):
            print(f"{i}. Sending {shortcut}...")
            try:
                keyboard.press_and_release(shortcut)
                time.sleep(0.5)
                print(f"   ✅ Sent {shortcut}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")

        print("\n✅ Keyboard shortcut test complete")
        return True

    except ImportError:
        print("❌ keyboard library not available")
        print("💡 Install: pip install keyboard")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Auto-Accept 'Keep All' Button")
    parser.add_argument("--keyboard-only", action="store_true", 
                       help="Test keyboard shortcuts only")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    if args.keyboard_only:
        success = test_keyboard_shortcuts()
    else:
        success = test_auto_accept()

    print("\n" + "="*80)
    if success:
        print("✅ Test completed successfully")
    else:
        print("⚠️  Test completed with issues - check output above")
    print("="*80 + "\n")

    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())