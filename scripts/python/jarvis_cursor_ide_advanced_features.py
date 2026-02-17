#!/usr/bin/env python3
"""
JARVIS Cursor IDE Advanced Features

Implements advanced Cursor IDE features and optimizations for peak performance.

Tags: #CURSOR-IDE #ADVANCED #PRODUCTIVITY @CURSOR-ENGINEER
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("JARVISCursorAdvanced")


class JARVISCursorIDEAdvancedFeatures:
    """
    JARVIS Cursor IDE Advanced Features

    Implements advanced features for peak Cursor IDE performance.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.cursor_dir = project_root / ".cursor"
        self.config_dir = project_root / "config"

        self.logger.info("✅ JARVIS Cursor IDE Advanced Features initialized")

    def create_snippets(self) -> Dict[str, Any]:
        """Create LUMINA-specific code snippets"""
        self.logger.info("📝 Creating LUMINA code snippets...")

        snippets = {
            "LUMINA Module Header": {
                "prefix": "lummod",
                "body": [
                    "#!/usr/bin/env python3",
                    "\"\"\"",
                    "${1:Module Description}",
                    "",
                    "Tags: ${2:#JARVIS} ${3:@TEAM}",
                    "\"\"\"",
                    "",
                    "import sys",
                    "from pathlib import Path",
                    "from typing import Dict, Any, List, Optional",
                    "from datetime import datetime",
                    "import logging",
                    "",
                    "script_dir = Path(__file__).parent",
                    "if str(script_dir) not in sys.path:",
                    "    sys.path.insert(0, str(script_dir))",
                    "",
                    "try:",
                    "    from lumina_logger import get_logger",
                    "except ImportError:",
                    "    logging.basicConfig(level=logging.INFO)",
                    "    get_logger = lambda name: logging.getLogger(name)",
                    "",
                    "logger = get_logger(\"${4:ModuleName}\")",
                    "",
                    "${5:# Code here}"
                ],
                "description": "LUMINA Python module template"
            },
            "JARVIS System Class": {
                "prefix": "jarclass",
                "body": [
                    "class ${1:ClassName}:",
                    "    \"\"\"",
                    "    ${2:Class Description}",
                    "    \"\"\"",
                    "    ",
                    "    def __init__(self, project_root: Path):",
                    "        self.project_root = project_root",
                    "        self.logger = logger",
                    "        self.logger.info(\"✅ ${1:ClassName} initialized\")",
                    "    ",
                    "    ${3:# Methods here}"
                ],
                "description": "JARVIS system class template"
            },
            "CLI Interface": {
                "prefix": "cli",
                "body": [
                    "def main():",
                    "    \"\"\"CLI interface\"\"\"",
                    "    import argparse",
                    "    ",
                    "    parser = argparse.ArgumentParser(description=\"${1:Description}\")",
                    "    parser.add_argument(\"${2:--arg}\", action=\"store_true\", help=\"${3:Help text}\")",
                    "    ",
                    "    args = parser.parse_args()",
                    "    ",
                    "    project_root = Path(__file__).parent.parent.parent",
                    "    ${4:instance} = ${5:ClassName}(project_root)",
                    "    ",
                    "    ${6:# CLI logic here}",
                    "",
                    "",
                    "if __name__ == \"__main__\":",
                    "    main()"
                ],
                "description": "CLI interface template"
            },
            "Error Handling": {
                "prefix": "tryex",
                "body": [
                    "try:",
                    "    ${1:# Code here}",
                    "except ${2:Exception} as e:",
                    "    self.logger.error(f\"❌ ${3:Error message}: {e}\", exc_info=True)",
                    "    return {\"success\": False, \"error\": str(e)}"
                ],
                "description": "Error handling template"
            },
            "Git Commit": {
                "prefix": "gitcommit",
                "body": [
                    "[${1:CATEGORY}] ${2:Description}"
                ],
                "description": "Git commit message template"
            }
        }

        snippets_path = self.cursor_dir / "snippets" / "python.json"
        snippets_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(snippets_path, 'w', encoding='utf-8') as f:
                json.dump(snippets, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Created snippets at {snippets_path}")
            return {"success": True, "path": str(snippets_path), "snippets": len(snippets)}
        except Exception as e:
            self.logger.error(f"❌ Failed to create snippets: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def create_tasks_config(self) -> Dict[str, Any]:
        """Create tasks.json for Cursor IDE"""
        self.logger.info("⚙️  Creating tasks.json configuration...")

        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "JARVIS: Auto Git Commit",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "scripts/python/jarvis_auto_git_manager.py",
                        "--auto-commit",
                        "--message",
                        "[AUTO] Auto-commit changes"
                    ],
                    "problemMatcher": [],
                    "presentation": {
                        "reveal": "silent",
                        "panel": "shared"
                    }
                },
                {
                    "label": "JARVIS: Health Check",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "scripts/python/jarvis_health_check.py"
                    ],
                    "problemMatcher": [],
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated"
                    }
                },
                {
                    "label": "JARVIS: Cursor IDE Optimization",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "scripts/python/jarvis_cursor_ide_engineer.py",
                        "--optimize"
                    ],
                    "problemMatcher": [],
                    "presentation": {
                        "reveal": "always",
                        "panel": "dedicated"
                    }
                }
            ]
        }

        tasks_path = self.cursor_dir / "tasks.json"
        try:
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Created tasks.json at {tasks_path}")
            return {"success": True, "path": str(tasks_path), "tasks": len(tasks["tasks"])}
        except Exception as e:
            self.logger.error(f"❌ Failed to create tasks.json: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def create_launch_config(self) -> Dict[str, Any]:
        """Create launch.json for debugging"""
        self.logger.info("🐛 Creating launch.json for debugging...")

        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: Current File",
                    "type": "debugpy",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "justMyCode": True,
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                },
                {
                    "name": "Python: JARVIS Script",
                    "type": "debugpy",
                    "request": "launch",
                    "program": "${workspaceFolder}/scripts/python/${input:scriptName}.py",
                    "console": "integratedTerminal",
                    "justMyCode": True,
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                },
                {
                    "name": "Python: Cursor IDE Engineer",
                    "type": "debugpy",
                    "request": "launch",
                    "program": "${workspaceFolder}/scripts/python/jarvis_cursor_ide_engineer.py",
                    "args": ["--optimize"],
                    "console": "integratedTerminal",
                    "justMyCode": True,
                    "env": {
                        "PYTHONPATH": "${workspaceFolder}"
                    }
                }
            ],
            "inputs": [
                {
                    "id": "scriptName",
                    "type": "promptString",
                    "description": "Enter script name (without .py)"
                }
            ]
        }

        launch_path = self.cursor_dir / "launch.json"
        try:
            with open(launch_path, 'w', encoding='utf-8') as f:
                json.dump(launch_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Created launch.json at {launch_path}")
            return {"success": True, "path": str(launch_path), "configurations": len(launch_config["configurations"])}
        except Exception as e:
            self.logger.error(f"❌ Failed to create launch.json: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def create_extensions_recommendations(self) -> Dict[str, Any]:
        """Create extensions.json with recommended extensions"""
        self.logger.info("🔌 Creating extensions recommendations...")

        extensions = {
            "recommendations": [
                "eamodio.gitlens",
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "ms-python.flake8",
                "ms-python.debugpy",
                "ms-python.isort",
                "charliermarsh.ruff",
                "ms-vscode.powershell",
                "redhat.vscode-yaml",
                "ms-vscode.vscode-json",
                "esbenp.prettier-vscode",
                "dbaeumer.vscode-eslint",
                "bradlc.vscode-tailwindcss",
                "formulahendry.auto-rename-tag",
                "christian-kohler.path-intellisense",
                "usernamehw.errorlens",
                "gruntfuggly.todo-tree",
                "wayou.vscode-todo-highlight",
                "aaron-bond.better-comments",
                "streetsidesoftware.code-spell-checker",
                "ms-vscode.remote-repositories",
                "github.copilot",
                "github.copilot-chat"
            ]
        }

        extensions_path = self.cursor_dir / "extensions.json"
        try:
            with open(extensions_path, 'w', encoding='utf-8') as f:
                json.dump(extensions, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Created extensions.json at {extensions_path}")
            return {"success": True, "path": str(extensions_path), "extensions": len(extensions["recommendations"])}
        except Exception as e:
            self.logger.error(f"❌ Failed to create extensions.json: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def full_advanced_setup(self) -> Dict[str, Any]:
        """Perform full advanced setup"""
        self.logger.info("🚀 Performing full advanced Cursor IDE setup...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "snippets": self.create_snippets(),
            "tasks": self.create_tasks_config(),
            "launch": self.create_launch_config(),
            "extensions": self.create_extensions_recommendations()
        }

        results["summary"] = {
            "snippets_created": results["snippets"]["success"],
            "tasks_created": results["tasks"]["success"],
            "launch_created": results["launch"]["success"],
            "extensions_created": results["extensions"]["success"],
            "total_features": sum([
                results["snippets"]["success"],
                results["tasks"]["success"],
                results["launch"]["success"],
                results["extensions"]["success"]
            ])
        }

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor IDE Advanced Features")
        parser.add_argument("--setup", action="store_true", help="Perform full advanced setup")
        parser.add_argument("--snippets", action="store_true", help="Create code snippets")
        parser.add_argument("--tasks", action="store_true", help="Create tasks.json")
        parser.add_argument("--launch", action="store_true", help="Create launch.json")
        parser.add_argument("--extensions", action="store_true", help="Create extensions.json")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        features = JARVISCursorIDEAdvancedFeatures(project_root)

        if args.snippets:
            result = features.create_snippets()
            print(json.dumps(result, indent=2, default=str))

        elif args.tasks:
            result = features.create_tasks_config()
            print(json.dumps(result, indent=2, default=str))

        elif args.launch:
            result = features.create_launch_config()
            print(json.dumps(result, indent=2, default=str))

        elif args.extensions:
            result = features.create_extensions_recommendations()
            print(json.dumps(result, indent=2, default=str))

        elif args.setup:
            result = features.full_advanced_setup()
            print(json.dumps(result, indent=2, default=str))

        else:
            # Default: full setup
            result = features.full_advanced_setup()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()