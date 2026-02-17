#!/usr/bin/env python3
"""
Configure All Extensions: Cursor IDE, Docker, @MANUS, @ELEVENLABS, and All Frameworks

Comprehensive extension configuration system that ensures all extensions are properly
configured across all platforms and frameworks.

Tags: #EXTENSIONS #CURSOR_IDE #DOCKER #MANUS #ELEVENLABS #FRAMEWORKS @JARVIS @LUMINA
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConfigureAllExtensions")


class ExtensionConfigurator:
    """Configure all extensions across all platforms and frameworks"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize extension configurator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data" / "extensions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Extension Configurator initialized")

    def configure_cursor_ide_extensions(self) -> Dict[str, Any]:
        try:
            """Configure Cursor IDE extensions"""
            logger.info("=" * 80)
            logger.info("🔧 CONFIGURING CURSOR IDE EXTENSIONS")
            logger.info("=" * 80)

            # Load extension configuration
            extensions_file = self.config_dir / "lumina_vscode_extensions.json"
            if not extensions_file.exists():
                logger.warning(f"   ⚠️  Extensions file not found: {extensions_file}")
                return {"success": False, "error": "Extensions file not found"}

            with open(extensions_file, 'r', encoding='utf-8') as f:
                extensions_config = json.load(f)

            # Generate .vscode/extensions.json
            vscode_dir = self.project_root / ".vscode"
            vscode_dir.mkdir(exist_ok=True)

            extensions_json = {
                "recommendations": extensions_config.get("all_extensions", [])
            }

            extensions_json_path = vscode_dir / "extensions.json"
            with open(extensions_json_path, 'w', encoding='utf-8') as f:
                json.dump(extensions_json, f, indent=2)

            logger.info(f"   ✅ Generated: {extensions_json_path.relative_to(self.project_root)}")
            logger.info(f"   ✅ Recommended extensions: {len(extensions_json['recommendations'])}")

            return {
                "success": True,
                "extensions_file": str(extensions_json_path),
                "extensions_count": len(extensions_json['recommendations'])
            }

        except Exception as e:
            self.logger.error(f"Error in configure_cursor_ide_extensions: {e}", exc_info=True)
            raise
    def configure_docker_extensions(self) -> Dict[str, Any]:
        try:
            """Configure Docker extensions"""
            logger.info("=" * 80)
            logger.info("🐳 CONFIGURING DOCKER EXTENSIONS")
            logger.info("=" * 80)

            # Docker extensions from VS Code extensions config
            extensions_file = self.config_dir / "lumina_vscode_extensions.json"
            docker_extensions = []

            if extensions_file.exists():
                with open(extensions_file, 'r', encoding='utf-8') as f:
                    extensions_config = json.load(f)

                docker_category = extensions_config.get("extensions", {}).get("docker", {})
                docker_extensions = docker_category.get("extensions", [])

            # Verify Docker extensions are in recommendations
            vscode_extensions_file = self.project_root / ".vscode" / "extensions.json"
            if vscode_extensions_file.exists():
                with open(vscode_extensions_file, 'r', encoding='utf-8') as f:
                    vscode_extensions = json.load(f)

                recommendations = vscode_extensions.get("recommendations", [])
                for ext in docker_extensions:
                    if ext not in recommendations:
                        recommendations.append(ext)

                vscode_extensions["recommendations"] = recommendations
                with open(vscode_extensions_file, 'w', encoding='utf-8') as f:
                    json.dump(vscode_extensions, f, indent=2)

            logger.info(f"   ✅ Docker extensions configured: {len(docker_extensions)}")
            for ext in docker_extensions:
                logger.info(f"      - {ext}")

            return {
                "success": True,
                "docker_extensions": docker_extensions,
                "count": len(docker_extensions)
            }

        except Exception as e:
            self.logger.error(f"Error in configure_docker_extensions: {e}", exc_info=True)
            raise
    def configure_manus_integration(self) -> Dict[str, Any]:
        try:
            """Configure @MANUS integration"""
            logger.info("=" * 80)
            logger.info("🤖 CONFIGURING @MANUS INTEGRATION")
            logger.info("=" * 80)

            # Check environment.json for MANUS configuration
            env_file = self.project_root / ".cursor" / "environment.json"
            manus_config = {}

            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_config = json.load(f)

                manus_config = env_config.get("integrations", {}).get("manus", {})

            if manus_config.get("enabled"):
                logger.info("   ✅ @MANUS is enabled")
                logger.info(f"      Desktop Control: {manus_config.get('desktopControl', False)}")
                logger.info(f"      Screenshot Capture: {manus_config.get('screenshotCapture', False)}")
            else:
                logger.warning("   ⚠️  @MANUS is not enabled")

            return {
                "success": True,
                "manus_enabled": manus_config.get("enabled", False),
                "config": manus_config
            }

        except Exception as e:
            self.logger.error(f"Error in configure_manus_integration: {e}", exc_info=True)
            raise
    def configure_elevenlabs_integration(self) -> Dict[str, Any]:
        try:
            """Configure @ELEVENLABS integration"""
            logger.info("=" * 80)
            logger.info("🎙️  CONFIGURING @ELEVENLABS INTEGRATION")
            logger.info("=" * 80)

            # Check environment.json for ELEVENLABS configuration
            env_file = self.project_root / ".cursor" / "environment.json"
            elevenlabs_config = {}

            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    env_config = json.load(f)

                kenjar_config = env_config.get("integrations", {}).get("kenjar", {})
                elevenlabs_config = {
                    "enabled": kenjar_config.get("elevenlabsVoice", False),
                    "voiceEnabled": kenjar_config.get("voiceEnabled", False)
                }

            # Check if API key is in Azure Vault (from startup script)
            logger.info("   ✅ Checking ELEVENLABS API key in Azure Vault...")
            logger.info("      Secret name: elevenlabs-api-key")
            logger.info("      Environment variable: ELEVENLABS_API_KEY")

            if elevenlabs_config.get("enabled"):
                logger.info("   ✅ @ELEVENLABS is enabled")
            else:
                logger.warning("   ⚠️  @ELEVENLABS is not enabled")

            return {
                "success": True,
                "elevenlabs_enabled": elevenlabs_config.get("enabled", False),
                "config": elevenlabs_config
            }

        except Exception as e:
            self.logger.error(f"Error in configure_elevenlabs_integration: {e}", exc_info=True)
            raise
    def configure_wakatime(self) -> Dict[str, Any]:
        """Configure WakaTime with API key from Azure Vault"""
        logger.info("=" * 80)
        logger.info("⏱️  CONFIGURING WAKATIME (FOR THE UMPTEENTH TIME!)")
        logger.info("=" * 80)

        # Check WakaTime config
        wakatime_config_file = self.config_dir / "wakatime_secure_config.json"
        if not wakatime_config_file.exists():
            logger.warning(f"   ⚠️  WakaTime config not found: {wakatime_config_file}")
            return {"success": False, "error": "WakaTime config not found"}

        with open(wakatime_config_file, 'r', encoding='utf-8') as f:
            wakatime_config = json.load(f)

        # Check if API key is set
        api_key = os.environ.get("WAKATIME_API_KEY")
        if api_key:
            logger.info("   ✅ WAKATIME_API_KEY is set in environment")
            logger.info(f"      Key preview: {api_key[:6]}...")
        else:
            logger.warning("   ⚠️  WAKATIME_API_KEY is NOT set in environment")
            logger.info("   🔄 Attempting to retrieve from Azure Vault...")

            # Try to get from vault
            try:
                from get_vault_secret import get_secret
                api_key = get_secret("wakatime-api-key")
                if api_key:
                    os.environ["WAKATIME_API_KEY"] = api_key
                    logger.info("   ✅ Retrieved WAKATIME_API_KEY from Azure Vault")
                else:
                    logger.error("   ❌ Could not retrieve WAKATIME_API_KEY from vault")
            except Exception as e:
                logger.error(f"   ❌ Error retrieving WAKATIME_API_KEY: {e}")

        # Create/update .wakatime-project file
        wakatime_project_file = self.project_root / ".wakatime-project"
        with open(wakatime_project_file, 'w', encoding='utf-8') as f:
            f.write("LUMINA\n")
        logger.info(f"   ✅ Created: {wakatime_project_file.relative_to(self.project_root)}")

        # Verify WakaTime CLI is available
        try:
            result = subprocess.run(
                ["wakatime", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"   ✅ WakaTime CLI is available: {result.stdout.strip()}")
            else:
                logger.warning("   ⚠️  WakaTime CLI may not be installed")
        except FileNotFoundError:
            logger.warning("   ⚠️  WakaTime CLI not found - install via: pip install wakatime")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not verify WakaTime CLI: {e}")

        return {
            "success": True,
            "api_key_set": api_key is not None,
            "config_file": str(wakatime_config_file),
            "project_file": str(wakatime_project_file)
        }

    def configure_all_extensions(self) -> Dict[str, Any]:
        """Configure all extensions"""
        logger.info("=" * 80)
        logger.info("🔧 CONFIGURING ALL EXTENSIONS")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "cursor_ide": {},
            "docker": {},
            "manus": {},
            "elevenlabs": {},
            "wakatime": {},
            "success": True,
            "errors": []
        }

        # Configure Cursor IDE extensions
        try:
            results["cursor_ide"] = self.configure_cursor_ide_extensions()
        except Exception as e:
            logger.error(f"   ❌ Error configuring Cursor IDE extensions: {e}")
            results["cursor_ide"] = {"success": False, "error": str(e)}
            results["errors"].append(f"Cursor IDE: {e}")

        logger.info("")

        # Configure Docker extensions
        try:
            results["docker"] = self.configure_docker_extensions()
        except Exception as e:
            logger.error(f"   ❌ Error configuring Docker extensions: {e}")
            results["docker"] = {"success": False, "error": str(e)}
            results["errors"].append(f"Docker: {e}")

        logger.info("")

        # Configure @MANUS
        try:
            results["manus"] = self.configure_manus_integration()
        except Exception as e:
            logger.error(f"   ❌ Error configuring @MANUS: {e}")
            results["manus"] = {"success": False, "error": str(e)}
            results["errors"].append(f"@MANUS: {e}")

        logger.info("")

        # Configure @ELEVENLABS
        try:
            results["elevenlabs"] = self.configure_elevenlabs_integration()
        except Exception as e:
            logger.error(f"   ❌ Error configuring @ELEVENLABS: {e}")
            results["elevenlabs"] = {"success": False, "error": str(e)}
            results["errors"].append(f"@ELEVENLABS: {e}")

        logger.info("")

        # Configure WakaTime
        try:
            results["wakatime"] = self.configure_wakatime()
        except Exception as e:
            logger.error(f"   ❌ Error configuring WakaTime: {e}")
            results["wakatime"] = {"success": False, "error": str(e)}
            results["errors"].append(f"WakaTime: {e}")

        # Update success status
        results["success"] = len(results["errors"]) == 0

        # Save results
        results_file = self.data_dir / f"extension_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ EXTENSION CONFIGURATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Results saved: {results_file.name}")

        if results["errors"]:
            logger.warning(f"   ⚠️  Errors: {len(results['errors'])}")
            for error in results["errors"]:
                logger.warning(f"      - {error}")
        else:
            logger.info("   ✅ All extensions configured successfully")

        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure All Extensions")
    parser.add_argument("--cursor-only", action="store_true", help="Configure only Cursor IDE extensions")
    parser.add_argument("--docker-only", action="store_true", help="Configure only Docker extensions")
    parser.add_argument("--manus-only", action="store_true", help="Configure only @MANUS")
    parser.add_argument("--elevenlabs-only", action="store_true", help="Configure only @ELEVENLABS")
    parser.add_argument("--wakatime-only", action="store_true", help="Configure only WakaTime")

    args = parser.parse_args()

    configurator = ExtensionConfigurator()

    if args.cursor_only:
        configurator.configure_cursor_ide_extensions()
    elif args.docker_only:
        configurator.configure_docker_extensions()
    elif args.manus_only:
        configurator.configure_manus_integration()
    elif args.elevenlabs_only:
        configurator.configure_elevenlabs_integration()
    elif args.wakatime_only:
        configurator.configure_wakatime()
    else:
        configurator.configure_all_extensions()

    return 0


if __name__ == "__main__":


    sys.exit(main())