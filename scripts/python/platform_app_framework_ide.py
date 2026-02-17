#!/usr/bin/env python3
"""
IDE Chat Interface Framework
Framework for creating IDE extensions (Cursor, VS Code, Abacus)

Provides foundation for IDE extension development.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

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

logger = get_logger("IDEExtensionFramework")


class IDEExtensionFramework:
    """Framework for IDE extensions"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.api_base_url = "https://api.jarvis.local"
        self.ide_extensions_dir = self.project_root / "platform_apps" / "ide_extensions"
        self.ide_extensions_dir.mkdir(parents=True, exist_ok=True)

    def create_extension_structure(self, ide: str) -> Dict[str, Any]:
        try:
            """Create IDE extension structure"""
            extension_structure = {
                "ide": ide,
                "api_base_url": self.api_base_url,
                "features": [
                    "Direct Chat with JARVIS",
                    "Code Generation",
                    "Workflow Orchestration",
                    "Knowledge Query",
                    "Escalation",
                    "Context-Aware Assistance"
                ],
                "endpoints": {
                    "auth": "/api/v1/auth",
                    "chat": "/api/v1/chat",
                    "workflows": "/api/v1/workflows",
                    "r5": "/api/v1/r5/knowledge/search",
                    "helpdesk": "/api/v1/helpdesk/tickets"
                },
                "websocket": {
                    "url": "ws://api.jarvis.local/api/v1/ws",
                    "reconnect_interval": 5
                },
                "created_at": datetime.now().isoformat()
            }

            ide_dir = self.ide_extensions_dir / ide
            ide_dir.mkdir(parents=True, exist_ok=True)

            config_file = ide_dir / "extension_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(extension_structure, f, indent=2)

            logger.info(f"IDE extension structure created for {ide}: {config_file}")
            return extension_structure

        except Exception as e:
            self.logger.error(f"Error in create_extension_structure: {e}", exc_info=True)
            raise
    def create_vscode_extension(self) -> Dict[str, Any]:
        try:
            """Create VS Code extension configuration"""
            vscode_config = {
                "name": "jarvis-chat",
                "displayName": "JARVIS Chat",
                "description": "Chat with JARVIS directly from VS Code",
                "version": "1.0.0",
                "publisher": "jarvis",
                "engines": {
                    "vscode": "^1.80.0"
                },
                "categories": ["Other"],
                "activationEvents": [
                    "onCommand:jarvis.chat",
                    "onView:jarvisChat"
                ],
                "main": "./out/extension.js",
                "contributes": {
                    "commands": [
                        {
                            "command": "jarvis.chat",
                            "title": "Chat with JARVIS"
                        }
                    ],
                    "views": {
                        "explorer": [
                            {
                                "id": "jarvisChat",
                                "name": "JARVIS Chat"
                            }
                        ]
                    }
                }
            }

            vscode_dir = self.ide_extensions_dir / "vscode"
            package_file = vscode_dir / "package.json"
            with open(package_file, 'w', encoding='utf-8') as f:
                json.dump(vscode_config, f, indent=2)

            logger.info(f"VS Code extension config created: {package_file}")
            return vscode_config

        except Exception as e:
            self.logger.error(f"Error in create_vscode_extension: {e}", exc_info=True)
            raise
    def create_cursor_extension(self) -> Dict[str, Any]:
        """Create Cursor extension configuration"""
        # Cursor uses similar structure to VS Code
        return self.create_vscode_extension()

    def create_all_extensions(self) -> Dict[str, Any]:
        """Create frameworks for all IDEs"""
        ides = ["vscode", "cursor", "abacus"]
        results = {}

        for ide in ides:
            results[ide] = {
                "extension_structure": self.create_extension_structure(ide),
                "config": self.create_vscode_extension() if ide in ["vscode", "cursor"] else {}
            }

        logger.info(f"Created IDE extension frameworks for {len(ides)} IDEs")
        return results


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    framework = IDEExtensionFramework(project_root)

    print("=" * 60)
    print("IDE Extension Framework")
    print("=" * 60)

    extensions = framework.create_all_extensions()

    print(f"\nCreated frameworks for {len(extensions)} IDEs:")
    for ide, config in extensions.items():
        print(f"  ✅ {ide.upper()}")

    print("=" * 60)
