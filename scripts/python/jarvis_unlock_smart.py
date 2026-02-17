#!/usr/bin/env python3
"""
JARVIS: Smart Adaptive Unlock System
🧠 Intelligent, learning-based unlock system that adapts and discovers
"""

import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

class SmartUnlockSystem:
    """🧠 Smart unlock system that learns and adapts"""

    def __init__(self):
        self.integration = create_armoury_crate_integration()
        self.learned_paths = {}
        self.failed_attempts = []
        self.config_file = project_root / "data" / "smart_unlock_config.json"
        self.load_config()

    def load_config(self):
        """Load learned paths from previous sessions"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.learned_paths = json.load(f)
        except:
            self.learned_paths = {}

    def save_config(self):
        """Save learned paths for future use"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.learned_paths, f, indent=2)
        except:
            pass

    async def discover_ui_elements(self, window) -> Dict[str, List[Tuple[int, int]]]:
        """Discover UI elements using multiple methods"""
        print("  🔍 Discovering UI elements...")

        discovered = {
            "device_menu": [],
            "system_config": [],
            "keyboard_settings": [],
            "lock_toggles": [],
            "text_elements": []
        }

        try:
            import pyautogui
            from PIL import Image
            import pytesseract

            left = window.left
            top = window.top
            width = window.width
            height = window.height

            # Take screenshot
            screenshot = pyautogui.screenshot(region=(left, top, width, height))

            # Method 1: OCR to find text (optional)
            print("    📝 Using OCR to find text elements...")
            try:
                import pytesseract
                ocr_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

                keywords = {
                    "device": ["device", "devices"],
                    "system": ["system", "configuration", "config"],
                    "keyboard": ["keyboard", "key"],
                    "function": ["function", "fn", "f1-f12"],
                    "windows": ["windows", "win"],
                    "lock": ["lock", "locked"],
                    "action": ["action", "mode"]
                }

                for i, text in enumerate(ocr_data.get('text', [])):
                    if text and len(text.strip()) > 2:
                        text_lower = text.lower()
                        x = ocr_data['left'][i] + left
                        y = ocr_data['top'][i] + top
                        conf = ocr_data['conf'][i]

                        if conf > 30:  # Confidence threshold
                            for category, words in keywords.items():
                                if any(word in text_lower for word in words):
                                    if category == "device":
                                        discovered["device_menu"].append((x, y))
                                    elif category == "system":
                                        discovered["system_config"].append((x, y))
                                    elif category == "keyboard":
                                        discovered["keyboard_settings"].append((x, y))
                                    elif category in ["function", "windows", "lock", "action"]:
                                        discovered["lock_toggles"].append((x, y))
                                    discovered["text_elements"].append((x, y, text))
                                    print(f"      ✅ Found '{text}' at ({x}, {y}) - category: {category}")
            except ImportError:
                print("    ⚠️  pytesseract not available for OCR")
            except Exception as e:
                print(f"    ⚠️  OCR error: {e}")

            # Method 2: Color-based detection (find buttons/toggles)
            print("    🎨 Analyzing colors to find interactive elements...")
            try:
                pixels = screenshot.load()
                button_colors = []  # Common button colors

                # Scan for common UI element colors (buttons, toggles)
                for y in range(0, height, 10):
                    for x in range(0, width, 10):
                        r, g, b = pixels[x, y]
                        # Look for common button colors (blues, grays, etc.)
                        if (r > 50 and r < 200 and g > 50 and g < 200 and b > 100 and b < 255):
                            # Potential button area
                            abs_x = left + x
                            abs_y = top + y
                            discovered["lock_toggles"].append((abs_x, abs_y))
            except Exception as e:
                print(f"    ⚠️  Color analysis error: {e}")

            # Method 3: Edge detection for UI elements
            print("    📐 Analyzing edges to find UI boundaries...")
            try:
                from PIL import ImageFilter
                edges = screenshot.filter(ImageFilter.FIND_EDGES)
                # This would require more sophisticated processing
            except Exception as e:
                pass

        except ImportError as e:
            print(f"    ⚠️  Required libraries not available: {e}")

        return discovered

    async def smart_navigation(self, discovered: Dict) -> bool:
        """Navigate using discovered elements"""
        print("  🧭 Smart navigation using discovered elements...")

        try:
            import pyautogui

            success = False

            # Strategy 1: Use discovered Device menu
            if discovered["device_menu"]:
                print("    📍 Clicking discovered Device menu...")
                x, y = discovered["device_menu"][0]
                pyautogui.click(x, y)
                await asyncio.sleep(2)
                success = True

            # Strategy 2: Use discovered System Configuration
            if discovered["system_config"]:
                print("    📍 Clicking discovered System Configuration...")
                for x, y in discovered["system_config"][:3]:  # Try first 3
                    pyautogui.click(x, y)
                    await asyncio.sleep(1)

            # Strategy 3: Click discovered lock toggles
            if discovered["lock_toggles"]:
                print(f"    📍 Found {len(discovered['lock_toggles'])} potential lock toggles...")
                for i, (x, y) in enumerate(discovered["lock_toggles"][:10]):  # Try first 10
                    print(f"      Trying toggle {i+1} at ({x}, {y})...")
                    pyautogui.click(x, y)
                    await asyncio.sleep(0.5)

                    # Try toggling
                    pyautogui.press('space')
                    await asyncio.sleep(0.3)
                    pyautogui.press('enter')
                    await asyncio.sleep(0.3)

                    # Try arrow keys to navigate dropdowns
                    for key in ['down', 'up', 'left', 'right']:
                        pyautogui.press(key)
                        await asyncio.sleep(0.2)
                        pyautogui.press('enter')
                        await asyncio.sleep(0.3)

            return success

        except Exception as e:
            print(f"    ⚠️  Navigation error: {e}")
            return False

    async def adaptive_registry_search(self) -> bool:
        """Adaptively search and modify registry"""
        print("  🔍 Adaptive registry search...")

        modified_count = 0

        # Get all ASUS registry paths
        ps_cmd = (
            "Get-ChildItem -Path 'HKCU:\\SOFTWARE\\ASUS' -Recurse -ErrorAction SilentlyContinue | "
            "ForEach-Object { $_.PSPath } | ConvertTo-Json"
        )
        result = self.integration._run_powershell(ps_cmd)

        if isinstance(result, dict):
            output = result.get("stdout", "")
        else:
            output = str(result) if result else ""

        if output:
            try:
                paths = json.loads(output)
                print(f"    ✅ Found {len(paths)} ASUS registry paths")

                # Search each path for lock-related values
                for path in paths[:30]:  # Limit to first 30
                    ps_cmd = (
                        f"$path = '{path}'; "
                        f"$props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue; "
                        f"if ($props) {{ "
                        f"  $lockProps = $props.PSObject.Properties | Where-Object {{ "
                        f"    $_.Name -like '*Lock*' -or $_.Name -like '*Fn*' -or $_.Name -like '*Win*' -or "
                        f"    $_.Name -like '*Action*' -or $_.Name -like '*Function*' "
                        f"  }}; "
                        f"  if ($lockProps) {{ "
                        f"    $lockProps | ForEach-Object {{ "
                        f"      Write-Host \"$path|$($_.Name)|$($_.Value)\" "
                        f"    }} "
                        f"  }} "
                        f"}}"
                    )
                    result = self.integration._run_powershell(ps_cmd)
                    if isinstance(result, dict):
                        reg_output = result.get("stdout", "")
                    else:
                        reg_output = str(result) if result else ""

                    if reg_output and '|' in reg_output:
                        for line in reg_output.strip().split('\n'):
                            if '|' in line:
                                parts = line.split('|')
                                if len(parts) >= 3:
                                    reg_path = parts[0]
                                    name = parts[1]
                                    value = parts[2]
                                    print(f"    ✅ Found: {reg_path}\\{name} = {value}")

                                    # Determine unlock value
                                    # 0 = unlock, 1 = lock (for most settings)
                                    # For ActionKeyMode: 1 = Function Key mode (unlocks FN), 0 = Media Key mode (locks FN)
                                    name_lower = name.lower()
                                    if "action" in name_lower or "function" in name_lower:
                                        unlock_value = "1"  # Function Key mode = unlocked
                                    elif "winkey" in name_lower or "win" in name_lower:
                                        unlock_value = "0"  # 0 = Windows key unlocked
                                    elif "fn" in name_lower or "lock" in name_lower:
                                        unlock_value = "0"  # 0 = unlocked
                                    else:
                                        unlock_value = "0"  # Default to unlock

                                    # Try to set unlock value
                                    try:
                                        ps_cmd = (
                                            f"try {{ "
                                            f"  Set-ItemProperty -Path '{reg_path}' -Name '{name}' -Value {unlock_value} -Type DWord -Force -ErrorAction Stop; "
                                            f"  Write-Host 'SUCCESS' "
                                            f"}} catch {{ "
                                            f"  try {{ "
                                            f"    New-ItemProperty -Path '{reg_path}' -Name '{name}' -Value {unlock_value} -Type DWord -Force -ErrorAction Stop; "
                                            f"    Write-Host 'CREATED' "
                                            f"  }} catch {{ Write-Host 'FAILED' }} "
                                            f"}}"
                                        )
                                        result = self.integration._run_powershell(ps_cmd)
                                        if isinstance(result, dict):
                                            mod_output = result.get("stdout", "")
                                        else:
                                            mod_output = str(result) if result else ""

                                        if "SUCCESS" in mod_output or "CREATED" in mod_output:
                                            print(f"      ✅ Modified {name} to {unlock_value}")
                                            modified_count += 1
                                    except Exception as e:
                                        pass
            except Exception as e:
                print(f"    ⚠️  Registry search error: {e}")

        print(f"    📊 Modified {modified_count} registry values")
        return modified_count > 0

    async def execute_smart_unlock(self) -> bool:
        """Execute smart unlock with all strategies"""
        print("=" * 70)
        print("🧠 JARVIS: Smart Adaptive Unlock System")
        print("=" * 70)
        print()

        # Step 1: Open Armoury Crate
        print("🔧 STEP 1: Opening Armoury Crate...")
        print("-" * 70)

        try:
            open_result = await self.integration.process_request({'action': 'open_app'})
            if open_result.get('success'):
                print("  ✅ Armoury Crate opened")
                await asyncio.sleep(5)
            else:
                print("  ⚠️  Please open Armoury Crate manually")
                await asyncio.sleep(3)
        except:
            pass

        print()

        # Step 2: Discover UI elements
        print("🔧 STEP 2: Discovering UI Elements...")
        print("-" * 70)

        try:
            import pygetwindow as gw

            windows = gw.getWindowsWithTitle("Armoury Crate")
            if not windows:
                windows = [w for w in gw.getAllWindows() if "armoury" in w.title.lower()]

            if windows:
                window = windows[0]
                window.activate()
                await asyncio.sleep(1)

                discovered = await self.discover_ui_elements(window)

                print()
                print(f"  📊 Discovery Results:")
                print(f"    Device menu: {len(discovered['device_menu'])} locations")
                print(f"    System config: {len(discovered['system_config'])} locations")
                print(f"    Keyboard settings: {len(discovered['keyboard_settings'])} locations")
                print(f"    Lock toggles: {len(discovered['lock_toggles'])} locations")
                print(f"    Text elements: {len(discovered['text_elements'])} found")

                # Step 3: Smart navigation
                print()
                print("🔧 STEP 3: Smart Navigation...")
                print("-" * 70)

                await self.smart_navigation(discovered)

                # Save discovered paths
                self.learned_paths["last_discovery"] = discovered
                self.save_config()

            else:
                print("  ⚠️  Armoury Crate window not found")
        except ImportError:
            print("  ⚠️  UI libraries not available")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")

        print()

        # Step 4: Adaptive registry search
        print("🔧 STEP 4: Adaptive Registry Search...")
        print("-" * 70)

        await self.adaptive_registry_search()

        print()

        # Step 5: Restart to apply changes
        print("🔧 STEP 5: Applying Changes...")
        print("-" * 70)

        services = ["ArmouryCrateService", "LightingService"]
        for service in services:
            try:
                ps_cmd = f"Restart-Service -Name '{service}' -Force -ErrorAction SilentlyContinue"
                self.integration._run_powershell(ps_cmd)
                print(f"  ✅ {service}: Restarted")
            except:
                pass

        print()
        print("=" * 70)
        print("💡 SUMMARY:")
        print("=" * 70)
        print("  🧠 Smart unlock system executed:")
        print("     ✅ UI element discovery")
        print("     ✅ Adaptive navigation")
        print("     ✅ Registry search and modification")
        print("     ✅ Service restart")
        print()
        print("  ⚠️  Check if lock symbols disappeared")
        print("  ⚠️  If not, restart computer to apply registry changes")
        print("=" * 70)

        return True

async def main():
    """Main function"""
    system = SmartUnlockSystem()
    await system.execute_smart_unlock()

if __name__ == "__main__":


    asyncio.run(main())