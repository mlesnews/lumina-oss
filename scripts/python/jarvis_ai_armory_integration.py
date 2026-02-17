#!/usr/bin/env python3
"""
JARVIS AI Armory Integration

Integrates with AI Armory virtual assistant to create
a JARVIS-themed companion that can interact with the existing system.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAIArmoryIntegration")


class JARVISAIArmoryIntegration:
    """
    Integration with AI Armory Virtual Assistant

    Allows JARVIS to interact with existing AI Armory assistant
    or create a JARVIS-themed version.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # AI Armory paths (common locations)
        self.possible_paths = [
            Path("C:/Program Files/AI Armory"),
            Path("C:/Program Files (x86)/AI Armory"),
            Path.home() / "AppData/Local/AI Armory",
            Path.home() / "AppData/Roaming/AI Armory",
        ]

        self.armory_path = self._find_armory()

        if self.armory_path:
            self.logger.info(f"✅ AI Armory found at: {self.armory_path}")
        else:
            self.logger.warning("⚠️  AI Armory not found - will use standalone JARVIS assistant")

    def _find_armory(self) -> Optional[Path]:
        """Find AI Armory installation"""
        for path in self.possible_paths:
            if path.exists():
                return path

        # Try to find via registry (Windows)
        if sys.platform == 'win32':
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\AI Armory"
                )
                install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                winreg.CloseKey(key)
                return Path(install_path)
            except:
                pass

        return None

    def detect_armory_api(self) -> Dict[str, Any]:
        """Detect AI Armory API endpoints"""
        if not self.armory_path:
            return {
                'found': False,
                'message': 'AI Armory not found'
            }

        # Look for API/config files
        config_files = [
            self.armory_path / "config.json",
            self.armory_path / "settings.json",
            self.armory_path / "api.json",
        ]

        api_info = {
            'found': True,
            'path': str(self.armory_path),
            'config_files': [],
            'api_endpoints': []
        }

        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        api_info['config_files'].append(str(config_file))
                        api_info['config'] = config
                except:
                    pass

        return api_info

    def create_jarvis_theme(self) -> Dict[str, Any]:
        try:
            """Create JARVIS-themed configuration for AI Armory"""
            theme_config = {
                'name': 'JARVIS',
                'appearance': {
                    'color': '#00FF00',  # JARVIS green
                    'size': 60,
                    'shape': 'circle',
                    'icon': 'J',
                    'glow': True
                },
                'behavior': {
                    'wander': True,
                    'speed': 2,
                    'idle_phrases': [
                        "I'm here if you need me.",
                        "Always ready to assist.",
                        "Monitoring systems.",
                        "Everything is running smoothly."
                    ],
                    'interaction_range': 200
                },
                'integration': {
                    'jarvis_agent': True,
                    'tts': True,
                    'voice': 'jarvis'
                }
            }

            # Save theme config
            theme_file = self.project_root / "data" / "jarvis_theme.json"
            theme_file.parent.mkdir(parents=True, exist_ok=True)

            with open(theme_file, 'w') as f:
                json.dump(theme_config, f, indent=2)

            self.logger.info(f"✅ JARVIS theme created: {theme_file}")

            return {
                'success': True,
                'theme_file': str(theme_file),
                'config': theme_config
            }

        except Exception as e:
            self.logger.error(f"Error in create_jarvis_theme: {e}", exc_info=True)
            raise
    def integrate_with_armory(self) -> Dict[str, Any]:
        """Integrate JARVIS with AI Armory"""
        if not self.armory_path:
            return {
                'success': False,
                'message': 'AI Armory not found - using standalone JARVIS'
            }

        # Create JARVIS theme
        theme_result = self.create_jarvis_theme()

        # Try to inject theme into AI Armory
        # This would depend on AI Armory's plugin/theme system
        armory_config = self.armory_path / "themes" / "jarvis.json"
        if armory_config.parent.exists():
            try:
                with open(armory_config, 'w') as f:
                    json.dump(theme_result['config'], f, indent=2)

                return {
                    'success': True,
                    'message': 'JARVIS theme installed in AI Armory',
                    'theme_file': str(armory_config)
                }
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Failed to install theme: {e}'
                }

        return {
            'success': True,
            'message': 'JARVIS theme created (manual installation may be required)',
            'theme_file': str(theme_result['theme_file'])
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS AI Armory Integration")
        parser.add_argument("--detect", action="store_true", help="Detect AI Armory installation")
        parser.add_argument("--create-theme", action="store_true", help="Create JARVIS theme")
        parser.add_argument("--integrate", action="store_true", help="Integrate with AI Armory")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        integration = JARVISAIArmoryIntegration(project_root)

        if args.detect:
            result = integration.detect_armory_api()
            print("\n" + "="*80)
            print("AI ARMORY DETECTION")
            print("="*80)
            if result.get('found'):
                print(f"✅ Found at: {result.get('path')}")
                if result.get('config_files'):
                    print(f"   Config files: {len(result['config_files'])}")
            else:
                print("❌ AI Armory not found")
            print("="*80)

        elif args.create_theme:
            result = integration.create_jarvis_theme()
            if result.get('success'):
                print(f"\n✅ JARVIS theme created: {result.get('theme_file')}")
            else:
                print(f"❌ Failed: {result.get('message', 'unknown')}")

        elif args.integrate:
            result = integration.integrate_with_armory()
            if result.get('success'):
                print(f"\n✅ {result.get('message')}")
                if result.get('theme_file'):
                    print(f"   Theme file: {result['theme_file']}")
            else:
                print(f"❌ {result.get('message', 'unknown')}")

        else:
            print("Usage:")
            print("  --detect       : Detect AI Armory installation")
            print("  --create-theme : Create JARVIS theme")
            print("  --integrate    : Integrate with AI Armory")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()