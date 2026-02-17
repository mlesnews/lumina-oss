#!/usr/bin/env python3
"""
Verify VS Code Extensions Installation
Checks if all required Lumina extensions are installed
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("verify_vscode_extensions")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def get_vscode_extensions() -> List[str]:
    """Get list of installed VS Code extensions"""
    try:
        result = subprocess.run(
            ["code", "--list-extensions"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return []
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"⚠ Warning: Could not list VS Code extensions: {e}")
        return []

def load_required_extensions(project_root: Path) -> List[Dict[str, Any]]:
    """Load required extensions from configuration"""
    extensions_file = project_root / "config" / "lumina_required_apps.json"

    if not extensions_file.exists():
        print(f"⚠ Warning: Required extensions file not found: {extensions_file}")
        return []

    try:
        with open(extensions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("vscode_extensions", [])
    except Exception as e:
        print(f"⚠ Warning: Could not load extensions file: {e}")
        return []

def verify_extensions(project_root: Path) -> Dict[str, Any]:
    """Verify VS Code extensions installation"""
    print("=" * 60)
    print("VS CODE EXTENSIONS VERIFICATION")
    print("=" * 60)
    print()

    installed = get_vscode_extensions()
    required = load_required_extensions(project_root)

    if not installed:
        print("❌ VS Code CLI not available or no extensions found")
        print("  Install VS Code and ensure 'code' command is in PATH")
        print("  Or manually check extensions in VS Code")
        return {
            "vscode_available": False,
            "installed_count": 0,
            "required_count": len(required),
            "matches": []
        }

    print(f"Found {len(installed)} installed extensions")
    print(f"Required {len(required)} extensions")
    print()

    matches = []
    missing = []

    for ext in required:
        ext_id = ext.get("id") or ext.get("name", "")
        ext_name = ext.get("name", ext_id)

        # Check if installed (by ID or name)
        found = False
        for installed_ext in installed:
            if ext_id.lower() in installed_ext.lower() or installed_ext.lower() in ext_id.lower():
                matches.append({
                    "required": ext_name,
                    "id": ext_id,
                    "installed": installed_ext,
                    "status": "✓"
                })
                found = True
                break

        if not found:
            missing.append({
                "required": ext_name,
                "id": ext_id,
                "status": "❌"
            })

    # Print results
    print("INSTALLED EXTENSIONS:")
    for match in matches:
        print(f"  ✓ {match['required']} ({match['installed']})")

    print()
    print("MISSING EXTENSIONS:")
    for miss in missing:
        print(f"  ❌ {miss['required']} ({miss['id']})")

    print()
    print(f"Summary: {len(matches)}/{len(required)} extensions installed")

    return {
        "vscode_available": True,
        "installed_count": len(installed),
        "required_count": len(required),
        "matches": matches,
        "missing": missing,
        "completion_rate": len(matches) / len(required) if required else 0
    }

def main():
    try:
        """Main verification function"""
        project_root = Path(__file__).parent.parent.parent

        result = verify_extensions(project_root)

        print("=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print()

        if not result["vscode_available"]:
            print("❌ VS Code CLI not available")
            print("  Please install VS Code and ensure 'code' is in PATH")
            return 1

        if result["completion_rate"] == 1.0:
            print("✓ ALL REQUIRED EXTENSIONS INSTALLED")
            return 0
        elif result["completion_rate"] > 0:
            print(f"⚠ PARTIAL: {len(result['matches'])}/{result['required_count']} extensions installed")
            print("  Install missing extensions to complete setup")
            return 1
        else:
            print("❌ NO REQUIRED EXTENSIONS INSTALLED")
            print("  Please install required extensions")
            return 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())