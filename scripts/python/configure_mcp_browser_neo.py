#!/usr/bin/env python3
"""
Configure MCP Browser to Use NEO as Default with Edge Fallback

This script configures the cursor-ide-browser MCP server to use NEO browser
as the default, with Edge as fallback.

Tags: #MCP_BROWSER #NEO #EDGE #FALLBACK @JARVIS @LUMINA
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConfigureMCPBrowserNEO")


def find_cursor_mcp_config() -> Optional[Path]:
    try:
        """
        Find Cursor MCP configuration file

        Returns:
            Path to MCP config file or None
        """
        # Common locations for Cursor MCP config
        possible_locations = [
            Path(os.path.expanduser("~")) / ".cursor" / "mcp.json",
            Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "mcp.json",
            Path(os.path.expanduser("~")) / ".config" / "cursor" / "mcp.json",
            project_root / ".cursor" / "mcp_config.json",
        ]

        for location in possible_locations:
            if location.exists():
                logger.info(f"   ✅ Found MCP config: {location}")
                return location

        logger.warning("   ⚠️  MCP config file not found in common locations")
        return None


    except Exception as e:
        logger.error(f"Error in find_cursor_mcp_config: {e}", exc_info=True)
        raise
def get_neo_browser_path() -> Optional[str]:
    try:
        """Get NEO browser path"""
        neo_paths = [
            "C:\\Users\\mlesn\\AppData\\Local\\Neo\\Application\\neo.exe",
            "D:\\Program Files\\Neo\\Application\\neo.exe",
            Path(os.path.expanduser("~")) / "AppData" / "Local" / "Neo" / "Application" / "neo.exe",
        ]

        for path_str in neo_paths:
            path = Path(path_str) if isinstance(path_str, str) else path_str
            if path.exists():
                logger.info(f"   ✅ Found NEO browser: {path}")
                return str(path)

        logger.warning("   ⚠️  NEO browser not found")
        return None


    except Exception as e:
        logger.error(f"Error in get_neo_browser_path: {e}", exc_info=True)
        raise
def get_edge_browser_path() -> Optional[str]:
    try:
        """Get Edge browser path as fallback"""
        edge_paths = [
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        ]

        for path_str in edge_paths:
            path = Path(path_str)
            if path.exists():
                logger.info(f"   ✅ Found Edge browser: {path}")
                return str(path)

        logger.warning("   ⚠️  Edge browser not found (will use system default)")
        return None


    except Exception as e:
        logger.error(f"Error in get_edge_browser_path: {e}", exc_info=True)
        raise
def configure_mcp_browser_neo() -> Dict[str, Any]:
    """
    Configure MCP browser to use NEO as default with Edge fallback

    Returns:
        Configuration result dictionary
    """
    logger.info("=" * 80)
    logger.info("🔧 CONFIGURING MCP BROWSER FOR NEO (DEFAULT) + EDGE (FALLBACK)")
    logger.info("=" * 80)
    logger.info("")

    neo_path = get_neo_browser_path()
    edge_path = get_edge_browser_path()

    # Load browser config
    browser_config_path = project_root / "config" / "browser_config.json"
    if browser_config_path.exists():
        with open(browser_config_path, 'r', encoding='utf-8') as f:
            browser_config = json.load(f)
    else:
        browser_config = {}

    # Update MCP browser config
    if "mcp_browser_config" not in browser_config:
        browser_config["mcp_browser_config"] = {}

    mcp_config = browser_config["mcp_browser_config"]
    mcp_config.update({
        "preferred_browser": "NEO",
        "use_default_browser": True,
        "default_browser_path": neo_path,
        "fallback_browser": "Edge",
        "fallback_browser_path": edge_path,
        "fallback_to_default": True,
        "configuration_note": "Use default browser (NEO) with Edge as fallback. Previously configured setting."
    })

    # Save updated config
    with open(browser_config_path, 'w', encoding='utf-8') as f:
        json.dump(browser_config, f, indent=2, ensure_ascii=False)

    logger.info("   ✅ Updated browser_config.json")
    logger.info("")

    # Try to find and update MCP config file
    mcp_config_file = find_cursor_mcp_config()

    result = {
        "status": "configured",
        "neo_path": neo_path,
        "edge_path": edge_path,
        "browser_config_updated": True,
        "mcp_config_file": str(mcp_config_file) if mcp_config_file else None,
        "configuration": {
            "preferred_browser": "NEO",
            "use_default_browser": True,
            "fallback_browser": "Edge",
            "fallback_to_default": True
        }
    }

    if mcp_config_file:
        try:
            with open(mcp_config_file, 'r', encoding='utf-8') as f:
                mcp_data = json.load(f)

            # Check if cursor-ide-browser server exists
            if "mcpServers" in mcp_data:
                if "cursor-ide-browser" in mcp_data["mcpServers"]:
                    server_config = mcp_data["mcpServers"]["cursor-ide-browser"]

                    # Update browser configuration
                    if "env" not in server_config:
                        server_config["env"] = {}

                    server_config["env"]["BROWSER_PATH"] = neo_path or ""
                    server_config["env"]["FALLBACK_BROWSER_PATH"] = edge_path or ""
                    server_config["env"]["USE_DEFAULT_BROWSER"] = "true"
                    server_config["env"]["FALLBACK_TO_EDGE"] = "true"

                    # Save updated MCP config
                    with open(mcp_config_file, 'w', encoding='utf-8') as f:
                        json.dump(mcp_data, f, indent=2, ensure_ascii=False)

                    logger.info(f"   ✅ Updated MCP config: {mcp_config_file}")
                    result["mcp_config_updated"] = True
                else:
                    logger.info("   ℹ️  cursor-ide-browser not in MCP config (may be auto-configured)")
                    result["mcp_config_updated"] = False
                    result["note"] = "cursor-ide-browser server not found in MCP config - may need manual configuration"
        except Exception as e:
            logger.warning(f"   ⚠️  Could not update MCP config: {e}")
            result["mcp_config_updated"] = False
            result["error"] = str(e)
    else:
        logger.info("   ℹ️  MCP config file not found - configuration saved to browser_config.json")
        logger.info("   💡 You may need to manually configure MCP browser in Cursor settings")
        result["mcp_config_updated"] = False
        result["note"] = "MCP config file not found - manual configuration may be required"

    logger.info("")
    logger.info("=" * 80)
    logger.info("📋 CONFIGURATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Preferred Browser: NEO")
    logger.info(f"  Path: {neo_path or 'Not found'}")
    logger.info(f"Fallback Browser: Edge")
    logger.info(f"  Path: {edge_path or 'Not found'}")
    logger.info(f"Browser Config: ✅ Updated")
    logger.info(f"MCP Config: {'✅ Updated' if result.get('mcp_config_updated') else '⚠️  Manual config may be needed'}")
    logger.info("")
    logger.info("💡 Note: MCP browser server may need to be restarted for changes to take effect")
    logger.info("=" * 80)

    return result


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Configure MCP Browser for NEO (Default) + Edge (Fallback)")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        result = configure_mcp_browser_neo()

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            # Results already logged
            pass

        return 0 if result.get("status") == "configured" else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())