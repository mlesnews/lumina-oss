#!/usr/bin/env python3
"""
@AC Force Enable Lighting
=========================
Forces keyboard lighting to be enabled via multiple methods to ensure it actually turns on.

This script ensures lighting is enabled even if Armoury Crate shows "not connected"
for certain features (like AniMe Vision).

@AC @LIGHTING @FORCE_ENABLE
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from lumina_unified_logger import LuminaUnifiedLogger

    logger = LuminaUnifiedLogger("System", "ACForceLighting")
    _logger = logger.get_logger()
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    _logger = logging.getLogger("ACForceLighting")


async def force_enable_keyboard_lighting(brightness: int = 100) -> Dict[str, Any]:
    """
    Force enable keyboard lighting via multiple methods

    Args:
        brightness: 0-100 (default: 100 for daylight)
    """
    _logger.info(f"Force enabling keyboard lighting at {brightness}%")

    result = {"success": False, "methods_used": [], "errors": []}

    # Method 1: Direct registry (most reliable)
    try:
        script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)

$brightness = {brightness}
$enabled = 1

$updated = 0
foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }}
        if (Test-Path $path) {{
            Set-ItemProperty -Path $path -Name 'Brightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enable' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enabled' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingEnabled' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue
            $updated++
        }}
    }} catch {{
    }}
}}

if ($updated -gt 0) {{
    Write-Output "OK:$updated"
}} else {{
    Write-Output "Failed"
}}
"""
        ps_result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if ps_result.returncode == 0 and "OK:" in ps_result.stdout:
            result["success"] = True
            result["methods_used"].append("registry")
            _logger.info(f"✅ Registry method: {ps_result.stdout.strip()}")
        else:
            result["errors"].append(f"Registry: {ps_result.stderr or ps_result.stdout}")
    except Exception as e:
        result["errors"].append(f"Registry error: {e}")

    # Method 2: @MANUS time-based lighting
    try:
        from manus_lighting_time_based import set_lighting_via_manus

        manus_result = await set_lighting_via_manus(brightness, False)
        if manus_result.get("success"):
            result["success"] = True
            result["methods_used"].append("manus")
            _logger.info(f"✅ @MANUS method: {manus_result.get('method', 'unknown')}")
        else:
            result["errors"].append(f"@MANUS: {manus_result.get('errors', 'Unknown')}")
    except ImportError:
        _logger.debug("@MANUS not available")
    except Exception as e:
        result["errors"].append(f"@MANUS error: {e}")

    # Method 3: Toggle keyboard lighting script (no console window)
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        toggle_result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "python" / "toggle_keyboard_lighting.py"),
                "--on",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            creationflags=creationflags,
        )
        if toggle_result.returncode == 0:
            result["methods_used"].append("toggle_script")
            _logger.info("✅ Toggle script method")
        else:
            result["errors"].append(f"Toggle script: {toggle_result.stderr}")
    except Exception as e:
        result["errors"].append(f"Toggle script error: {e}")

    return result


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="@AC Force Enable Lighting - Ensures keyboard lighting is actually on",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
@AC = API & CLI (consistent results)

This script forces keyboard lighting to be enabled via multiple methods,
ensuring it actually turns on even if Armoury Crate shows "not connected"
for certain features.

Examples:
  %(prog)s              Force enable at 100 percent (daylight)
  %(prog)s --brightness 50  Force enable at 50 percent
        """,
    )

    parser.add_argument(
        "--brightness", type=int, default=100, help="Brightness level (0-100, default: 100)"
    )

    args = parser.parse_args()

    async def run():
        result = await force_enable_keyboard_lighting(args.brightness)

        if result.get("success"):
            methods = ", ".join(result.get("methods_used", []))
            print(f"✅ Keyboard lighting force-enabled via: {methods}")
            print(f"   Brightness: {args.brightness}%")
            return 0
        else:
            errors = result.get("errors", ["Unknown error"])
            print("❌ Failed to force enable lighting:")
            for error in errors:
                print(f"   - {error}")
            return 1

    exit_code = asyncio.run(run())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
