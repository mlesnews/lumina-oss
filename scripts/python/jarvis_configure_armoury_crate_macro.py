#!/usr/bin/env python3
"""
JARVIS - Configure Armoury Crate Macro for Right Alt Key
Attempts to programmatically configure the macro or provides automated setup
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_ArmouryCrateMacro")

class JARVISArmouryCrateMacroConfig:
    """JARVIS system for configuring Armoury Crate macros"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Armoury Crate macro configuration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.batch_file = self.project_root / "scripts" / "python" / "trigger_retry_and_voice.bat"
        self.config_file = self.project_root / "config" / "armoury_crate_macro_config.json"

        logger.info("✅ JARVIS Armoury Crate Macro Config initialized")

    def check_armoury_crate_running(self) -> bool:
        """Check if Armoury Crate is running"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq ArmouryCrate.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "ArmouryCrate.exe" in result.stdout
        except Exception as e:
            logger.warning(f"Could not check Armoury Crate status: {e}")
            return False

    def open_armoury_crate(self) -> bool:
        """Open Armoury Crate application"""
        try:
            # Try multiple possible paths
            paths = [
                r"C:\Program Files\ASUS\ARMOURY CRATE Service\ArmouryCrate.exe",
                r"C:\Program Files (x86)\ASUS\ARMOURY CRATE Service\ArmouryCrate.exe",
                r"%LOCALAPPDATA%\Programs\ASUS\ARMOURY CRATE\ArmouryCrate.exe",
            ]

            for path in paths:
                expanded_path = Path(path).expanduser()
                if expanded_path.exists():
                    logger.info(f"Opening Armoury Crate: {expanded_path}")
                    subprocess.Popen([str(expanded_path)], shell=True)
                    return True

            # Try to open via Start Menu
            logger.info("Opening Armoury Crate via Start Menu...")
            subprocess.Popen(["start", "armoury"], shell=True)
            return True

        except Exception as e:
            logger.error(f"Failed to open Armoury Crate: {e}")
            return False

    def create_macro_config(self) -> Dict[str, Any]:
        try:
            """Create macro configuration file"""
            config = {
                "macro_name": "Right Alt - Retry + Voice Input",
                "assigned_key": "RightAlt",
                "action_type": "Execute Program",
                "program_path": str(self.batch_file),
                "description": "Executes @RETRY_MANAGER processing and triggers voice input in Cursor IDE",
                "tags": ["#RETRY_MANAGER", "#VOICE_INPUT", "@JARVIS", "@LUMINA"],
                "setup_instructions": {
                    "step_1": "Open Armoury Crate",
                    "step_2": "Navigate to Device → Keyboard → Macro",
                    "step_3": "Click 'Create New Macro' or '+'",
                    "step_4": f"Set Name: 'Right Alt - Retry + Voice Input'",
                    "step_5": "Assign to Right Alt key",
                    "step_6": f"Add Action: Execute Program → {self.batch_file}",
                    "step_7": "Save macro"
                }
            }

            # Save config
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Macro configuration saved: {self.config_file}")
            return config

        except Exception as e:
            self.logger.error(f"Error in create_macro_config: {e}", exc_info=True)
            raise
    def create_automated_setup_script(self) -> Path:
        """Create a script that automates the setup process"""
        script_content = f'''@echo off
REM JARVIS Automated Armoury Crate Macro Setup
REM This script opens Armoury Crate and provides setup instructions

echo ======================================================================
echo JARVIS - Armoury Crate Macro Setup
echo ======================================================================
echo.
echo Opening Armoury Crate...
echo.

REM Try to open Armoury Crate
start "" "C:\\Program Files\\ASUS\\ARMOURY CRATE Service\\ArmouryCrate.exe" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo ======================================================================
echo SETUP INSTRUCTIONS
echo ======================================================================
echo.
echo 1. In Armoury Crate, navigate to: Device ^> Keyboard ^> Macro
echo.
echo 2. Click "Create New Macro" or "+" button
echo.
echo 3. Configure the macro:
echo    - Name: Right Alt - Retry + Voice Input
echo    - Assign Key: Right Alt (click on keyboard diagram)
echo    - Action Type: Execute Program
echo    - Program: {self.batch_file}
echo.
echo 4. Click "Save" or "OK"
echo.
echo ======================================================================
echo.
echo Press any key to close this window after configuring the macro...
pause >nul
'''

        script_path = self.project_root / "scripts" / "python" / "jarvis_armoury_crate_setup.bat"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"✅ Automated setup script created: {script_path}")
        return script_path

    def execute_setup(self) -> Dict[str, Any]:
        try:
            """Execute the complete setup process"""
            logger.info("=" * 70)
            logger.info("JARVIS - CONFIGURING ARMOURY CRATE MACRO")
            logger.info("=" * 70)
            logger.info("")

            result = {
                "status": "success",
                "steps_completed": [],
                "files_created": [],
                "next_steps": []
            }

            # Step 1: Verify batch file exists
            logger.info("STEP 1: Verifying batch file...")
            if not self.batch_file.exists():
                logger.error(f"❌ Batch file not found: {self.batch_file}")
                result["status"] = "error"
                result["error"] = f"Batch file not found: {self.batch_file}"
                return result

            logger.info(f"✅ Batch file found: {self.batch_file}")
            result["steps_completed"].append("batch_file_verified")
            result["files_created"].append(str(self.batch_file))

            # Step 2: Create macro configuration
            logger.info("")
            logger.info("STEP 2: Creating macro configuration...")
            config = self.create_macro_config()
            result["steps_completed"].append("config_created")
            result["files_created"].append(str(self.config_file))

            # Step 3: Create automated setup script
            logger.info("")
            logger.info("STEP 3: Creating automated setup script...")
            setup_script = self.create_automated_setup_script()
            result["steps_completed"].append("setup_script_created")
            result["files_created"].append(str(setup_script))

            # Step 4: Check if Armoury Crate is running
            logger.info("")
            logger.info("STEP 4: Checking Armoury Crate status...")
            if self.check_armoury_crate_running():
                logger.info("✅ Armoury Crate is running")
                result["steps_completed"].append("armoury_crate_running")
            else:
                logger.info("⚠️  Armoury Crate is not running")
                result["next_steps"].append("Open Armoury Crate manually or run setup script")

            # Step 5: Open Armoury Crate
            logger.info("")
            logger.info("STEP 5: Opening Armoury Crate...")
            if self.open_armoury_crate():
                logger.info("✅ Armoury Crate opened")
                result["steps_completed"].append("armoury_crate_opened")
            else:
                logger.warning("⚠️  Could not open Armoury Crate automatically")
                result["next_steps"].append("Open Armoury Crate manually")

            # Step 6: Provide instructions
            logger.info("")
            logger.info("=" * 70)
            logger.info("SETUP COMPLETE - NEXT STEPS")
            logger.info("=" * 70)
            logger.info("")
            logger.info("1. In Armoury Crate, navigate to: Device → Keyboard → Macro")
            logger.info("2. Click 'Create New Macro' or '+' button")
            logger.info("3. Configure:")
            logger.info(f"   - Name: {config['macro_name']}")
            logger.info(f"   - Assign Key: {config['assigned_key']}")
            logger.info(f"   - Action: {config['action_type']}")
            logger.info(f"   - Program: {config['program_path']}")
            logger.info("4. Click 'Save' or 'OK'")
            logger.info("")
            logger.info("=" * 70)
            logger.info("")

            result["next_steps"] = [
                "Navigate to Device → Keyboard → Macro in Armoury Crate",
                "Create new macro with the configuration above",
                "Test by pressing Right Alt in Cursor IDE"
            ]

            return result


        except Exception as e:
            self.logger.error(f"Error in execute_setup: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    configurator = JARVISArmouryCrateMacroConfig()
    result = configurator.execute_setup()

    # Print summary
    print("")
    print("=" * 70)
    print("JARVIS SETUP SUMMARY")
    print("=" * 70)
    print(f"Status: {result['status']}")
    print(f"Steps Completed: {len(result['steps_completed'])}")
    print(f"Files Created: {len(result['files_created'])}")
    print("")
    print("Files Created:")
    for file in result['files_created']:
        print(f"  ✅ {file}")
    print("")
    print("Next Steps:")
    for step in result['next_steps']:
        print(f"  • {step}")
    print("")
    print("=" * 70)

    return result


if __name__ == "__main__":


    main()