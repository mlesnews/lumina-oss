#!/usr/bin/env python3
"""
Visual Desktop Check - REQUIRED

Actually checks the desktop visually to see if VAs are visible.
Uses VLM to analyze what's on screen.

Tags: #VISUAL_CHECK #REQUIRED #NO_ASSUMPTIONS @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from vlm_integration import VLMIntegration
    VLM_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False
    print("⚠️  VLM not available")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️  pyautogui not available")

def check_desktop_visually():
    """Actually check desktop visually - no assumptions"""
    print("=" * 80)
    print("🔍 VISUAL DESKTOP CHECK - NO ASSUMPTIONS")
    print("=" * 80)
    print()

    # Take screenshot
    if not PYAUTOGUI_AVAILABLE:
        print("❌ Cannot take screenshot - pyautogui not available")
        return

    print("📸 Taking screenshot of desktop...")
    try:
        screenshot = pyautogui.screenshot()
        screenshot_path = project_root / "data" / "desktop_check.png"
        screenshot.save(screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"❌ Failed to take screenshot: {e}")
        return

    # Analyze with VLM
    if VLM_AVAILABLE:
        print()
        print("🤖 Analyzing screenshot with VLM...")
        try:
            vlm = VLMIntegration(project_root=project_root)

            prompt = """Analyze this desktop screenshot and tell me:
1. Are there any small animated characters or virtual assistants visible? (like Armoury Crate VA or Iron Man character)
2. Are there any small windows (120x120px or similar) visible on screen?
3. Are there any red/orange circular or geometric shapes that could be virtual assistants?
4. What windows are visible on the desktop?
5. Are there any "Accept All Changes" or "Keep All" buttons visible?
6. Are there any voice input buttons or microphone icons visible?

Be specific about what you see - don't assume anything."""

            result = vlm.analyze_image(str(screenshot_path), prompt)
            print()
            print("=" * 80)
            print("📊 VLM ANALYSIS RESULTS:")
            print("=" * 80)
            print(result)
            print("=" * 80)
        except Exception as e:
            print(f"❌ VLM analysis failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  VLM not available - cannot analyze screenshot")

    # Also check for windows programmatically
    print()
    print("🔍 Checking for VA windows programmatically...")
    try:
        import pygetwindow as gw
        windows = gw.getAllWindows()

        kenny_windows = []
        ace_windows = []
        other_small_windows = []

        for window in windows:
            title = window.title.lower()
            width = window.width
            height = window.height

            # Check for Kenny window
            if "kenny" in title or "imva" in title or "iron man" in title:
                kenny_windows.append({
                    'title': window.title,
                    'position': (window.left, window.top),
                    'size': (width, height),
                    'visible': window.visible
                })

            # Check for Ace/ACVA window
            if "armoury" in title or "acva" in title or "virtual assistant" in title or "virtual pet" in title:
                ace_windows.append({
                    'title': window.title,
                    'position': (window.left, window.top),
                    'size': (width, height),
                    'visible': window.visible
                })

            # Check for small windows (could be VAs)
            if 80 <= width <= 150 and 80 <= height <= 150 and window.visible:
                other_small_windows.append({
                    'title': window.title,
                    'position': (window.left, window.top),
                    'size': (width, height)
                })

        print()
        print("=" * 80)
        print("🪟 WINDOW DETECTION RESULTS:")
        print("=" * 80)

        if kenny_windows:
            print(f"✅ Found {len(kenny_windows)} Kenny window(s):")
            for w in kenny_windows:
                print(f"   - {w['title']}")
                print(f"     Position: {w['position']}, Size: {w['size']}, Visible: {w['visible']}")
        else:
            print("❌ No Kenny windows found")

        print()
        if ace_windows:
            print(f"✅ Found {len(ace_windows)} Ace/ACVA window(s):")
            for w in ace_windows:
                print(f"   - {w['title']}")
                print(f"     Position: {w['position']}, Size: {w['size']}, Visible: {w['visible']}")
        else:
            print("❌ No Ace/ACVA windows found")

        print()
        if other_small_windows:
            print(f"🔍 Found {len(other_small_windows)} other small windows (possible VAs):")
            for w in other_small_windows:
                print(f"   - {w['title']}")
                print(f"     Position: {w['position']}, Size: {w['size']}")
        else:
            print("ℹ️  No other small windows found")

        print("=" * 80)

    except ImportError:
        print("⚠️  pygetwindow not available - cannot check windows")
    except Exception as e:
        print(f"❌ Window check failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_desktop_visually()
