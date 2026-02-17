#!/usr/bin/env python3
"""
JARVIS Voice Button Macro - Right Alt to Control+Shift+Space

Maps Right Alt button to Control+Shift+Space (voice activation)
Using PowerToys or custom macro solution

Tags: #VOICE_BUTTON #MACRO #POWERTOYS #RIGHT_ALT @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISVoiceButtonMacro")

# Try to import keyboard library for custom macro
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.warning("⚠️  keyboard library not available - install: pip install keyboard")


class VoiceButtonMacro:
    """Voice button macro system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config" / "macros"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "voice_button_macro.json"
        self.powertoys_config = None
        self.macro_active = False

        self.load_config()

    def load_config(self):
        """Load macro configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.powertoys_config = data.get("powertoys", {})
            except:
                self.powertoys_config = {}
        else:
            self.powertoys_config = {
                "mapping": {
                    "trigger": "Right Alt",
                    "action": "Control+Shift+Space",
                    "description": "Voice activation button"
                },
                "powertoys_path": None,
                "custom_macro": True
            }
            self.save_config()

    def save_config(self):
        try:
            """Save macro configuration"""
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "powertoys": self.powertoys_config,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in save_config: {e}", exc_info=True)
            raise
    def generate_powertoys_config(self) -> Dict[str, Any]:
        try:
            """Generate PowerToys Keyboard Manager configuration"""
            logger.info("🔧 Generating PowerToys Keyboard Manager configuration...")

            # PowerToys Keyboard Manager JSON format
            powertoys_config = {
                "remapKeys": [
                    {
                        "inVK": "VK_RMENU",  # Right Alt (Right Menu key)
                        "outVK": "VK_LCONTROL",  # Start with Control
                        "outVK2": "VK_LSHIFT",  # Then Shift
                        "outVK3": "VK_SPACE"  # Then Space
                    }
                ],
                "remapShortcuts": [
                    {
                        "originalKeys": "Right Alt",
                        "newRemapKeys": [
                            {
                                "key": "Ctrl",
                                "modifiers": ["Shift"],
                                "target": "Space"
                            }
                        ]
                    }
                ]
            }

            # Alternative: Simple remap to shortcut
            simple_config = {
                "remapShortcuts": [
                    {
                        "originalKeys": "Right Alt",
                        "newRemapKeys": "Ctrl+Shift+Space"
                    }
                ]
            }

            config_path = self.config_dir / "powertoys_keyboard_manager.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(simple_config, f, indent=2, default=str)

            logger.info(f"✅ PowerToys config generated: {config_path}")
            logger.info("")
            logger.info("📋 To apply:")
            logger.info("   1. Open PowerToys")
            logger.info("   2. Go to Keyboard Manager")
            logger.info("   3. Import or manually add:")
            logger.info("      Right Alt → Ctrl+Shift+Space")
            logger.info("")

            return simple_config

        except Exception as e:
            self.logger.error(f"Error in generate_powertoys_config: {e}", exc_info=True)
            raise
    def create_custom_macro(self) -> bool:
        """Create custom macro using keyboard library"""
        if not KEYBOARD_AVAILABLE:
            logger.error("❌ keyboard library not available")
            logger.info("   Install: pip install keyboard")
            logger.info("   Note: Requires administrator privileges on Windows")
            return False

        logger.info("🔧 Creating custom macro...")
        logger.info("   Right Alt → Control+Shift+Space")
        logger.info("")
        logger.info("⚠️  This will run in the background")
        logger.info("   Press Ctrl+C to stop")
        logger.info("")

        try:
            def on_right_alt():
                """Handle Right Alt press"""
                keyboard.press_and_release('ctrl+shift+space')
                logger.debug("🎤 Voice activation triggered")

            # Hook Right Alt key
            keyboard.on_press_key('right alt', lambda _: on_right_alt())

            logger.info("✅ Custom macro active")
            logger.info("   Press Right Alt to trigger voice activation")
            logger.info("   Press Ctrl+C to stop")
            logger.info("")

            # Keep running
            keyboard.wait()

            return True

        except Exception as e:
            logger.error(f"❌ Error creating custom macro: {e}")
            return False

    def create_autohotkey_script(self) -> Path:
        """Create AutoHotkey script for macro"""
        logger.info("🔧 Creating AutoHotkey script...")

        ahk_script = self.config_dir / "voice_button_macro.ahk"

        script_content = """#NoEnv
#SingleInstance Force
#Persistent

; JARVIS Voice Button Macro
; Right Alt → Control+Shift+Space (Voice Activation)

RAlt::
    Send, ^{Shift}{Space}
    Return

; Alternative: Right Alt only (not Left Alt)
; RAlt & Space::
;     Send, ^{Shift}{Space}
;     Return
"""

        with open(ahk_script, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"✅ AutoHotkey script created: {ahk_script}")
        logger.info("")
        logger.info("📋 To use:")
        logger.info("   1. Install AutoHotkey: https://www.autohotkey.com/")
        logger.info(f"   2. Run: {ahk_script}")
        logger.info("   3. Right Alt will trigger Control+Shift+Space")
        logger.info("")

        return ahk_script

    def create_powertoys_instructions(self) -> Path:
        """Create PowerToys setup instructions"""
        logger.info("🔧 Creating PowerToys setup instructions...")

        instructions_file = self.config_dir / "POWERTOYS_SETUP_INSTRUCTIONS.md"

        instructions = """# PowerToys Voice Button Macro Setup

## Objective
Map **Right Alt** button to **Control+Shift+Space** (Voice Activation)

## Method 1: PowerToys Keyboard Manager (Recommended)

### Steps:
1. **Install PowerToys** (if not already installed)
   - Download from: https://github.com/microsoft/PowerToys
   - Or install from Microsoft Store

2. **Open PowerToys**
   - Launch PowerToys from Start Menu
   - Go to **Keyboard Manager**

3. **Add Remap**
   - Click **"Remap a shortcut"**
   - In **"Shortcut"** field, press **Right Alt**
   - In **"Mapped to"** field, press **Control+Shift+Space**
   - Click **OK**

4. **Apply**
   - The remap is active immediately
   - Right Alt will now trigger Control+Shift+Space

### Alternative: Remap a key
- Click **"Remap a key"**
- Select **Right Alt** → **Remap to** → **Custom shortcut**
- Enter: **Ctrl+Shift+Space**

## Method 2: AutoHotkey Script

1. **Install AutoHotkey**
   - Download from: https://www.autohotkey.com/
   - Install the application

2. **Run Script**
   - Double-click `voice_button_macro.ahk`
   - Script runs in background
   - Right Alt triggers Control+Shift+Space

3. **Auto-Start** (Optional)
   - Copy script to Windows Startup folder:
     `%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup`

## Method 3: Custom Python Macro

1. **Install keyboard library**
   ```bash
   pip install keyboard
   ```

2. **Run macro**
   ```bash
   python scripts/python/jarvis_voice_button_macro.py --custom
   ```

   **Note**: Requires administrator privileges on Windows

## Verification

1. Press **Right Alt**
2. Should trigger voice activation (Control+Shift+Space)
3. Check if voice interface activates

## Troubleshooting

- **Right Alt not working**: Check if PowerToys is running
- **Requires admin**: Some methods require administrator privileges
- **Conflicts**: Check for other software using Right Alt
- **PowerToys not found**: Install from Microsoft Store or GitHub

## Current Configuration

- **Trigger**: Right Alt
- **Action**: Control+Shift+Space
- **Purpose**: Voice activation button
- **Status**: Ready to configure

@JARVIS @LUMINA #VOICE_BUTTON #MACRO #POWERTOYS
"""

        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        logger.info(f"✅ Instructions created: {instructions_file}")

        return instructions_file

    def setup_macro(self, method: str = "powertoys") -> Dict[str, Any]:
        """Setup voice button macro"""
        logger.info("=" * 80)
        logger.info("🎤 JARVIS VOICE BUTTON MACRO SETUP")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Mapping: Right Alt → Control+Shift+Space")
        logger.info("")

        setup_result = {
            "timestamp": datetime.now().isoformat(),
            "trigger": "Right Alt",
            "action": "Control+Shift+Space",
            "method": method,
            "files_created": [],
            "status": "READY"
        }

        if method == "powertoys":
            # Generate PowerToys config
            config = self.generate_powertoys_config()
            setup_result["files_created"].append(str(self.config_dir / "powertoys_keyboard_manager.json"))

            # Create instructions
            instructions = self.create_powertoys_instructions()
            setup_result["files_created"].append(str(instructions))

            logger.info("✅ PowerToys configuration ready")
            logger.info("   Follow instructions in: POWERTOYS_SETUP_INSTRUCTIONS.md")

        elif method == "autohotkey":
            # Create AutoHotkey script
            ahk_script = self.create_autohotkey_script()
            setup_result["files_created"].append(str(ahk_script))

            logger.info("✅ AutoHotkey script ready")
            logger.info(f"   Run: {ahk_script}")

        elif method == "custom":
            # Create custom macro
            if self.create_custom_macro():
                setup_result["status"] = "ACTIVE"
                logger.info("✅ Custom macro active")
            else:
                setup_result["status"] = "FAILED"
                logger.error("❌ Custom macro failed")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ MACRO SETUP COMPLETE")
        logger.info("=" * 80)

        return setup_result


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Voice Button Macro")
        parser.add_argument("--setup", action="store_true", help="Setup macro")
        parser.add_argument("--method", type=str, choices=["powertoys", "autohotkey", "custom"], 
                           default="powertoys", help="Macro method")
        parser.add_argument("--powertoys", action="store_true", help="Generate PowerToys config")
        parser.add_argument("--autohotkey", action="store_true", help="Create AutoHotkey script")
        parser.add_argument("--custom", action="store_true", help="Run custom Python macro")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        macro = VoiceButtonMacro(project_root)

        if args.setup or (not args.powertoys and not args.autohotkey and not args.custom):
            # Full setup
            result = macro.setup_macro(args.method)
            print(json.dumps(result, indent=2, default=str))

        elif args.powertoys:
            config = macro.generate_powertoys_config()
            instructions = macro.create_powertoys_instructions()
            print(json.dumps({"config": config, "instructions": str(instructions)}, indent=2, default=str))

        elif args.autohotkey:
            script = macro.create_autohotkey_script()
            print(json.dumps({"script": str(script)}, indent=2, default=str))

        elif args.custom:
            macro.create_custom_macro()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()