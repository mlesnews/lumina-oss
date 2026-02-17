#!/usr/bin/env python3
"""
SiderAI Extension Integration - MANUS Auto-Grammarly & AI Coordination

Integrates MANUS Auto-Grammarly and AI Coordination with SiderAI Extension
"DO THE SAME WITH THE SIDERAI EXTENSION"
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SiderAIExtensionIntegration")

# Import MANUS Auto-Grammarly and AI Coordination
try:
    from manus_auto_grammarly import MANUSAutoGrammarly
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    logger.debug("MANUS Auto-Grammarly not available")

try:
    from jarvis_ai_coordination import JARVISAICoordination, AIType
    COORDINATION_AVAILABLE = True
except ImportError:
    COORDINATION_AVAILABLE = False
    logger.debug("AI Coordination not available")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SiderAIExtensionIntegration:
    """
    SiderAI Extension Integration

    Integrates MANUS Auto-Grammarly and AI Coordination with SiderAI Extension
    Works with VS Code, Cursor, and other IDEs
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SiderAI Extension integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SiderAIExtensionIntegration")

        # Initialize MANUS Auto-Grammarly
        self.auto_grammarly = None
        if MANUS_AVAILABLE:
            try:
                self.auto_grammarly = MANUSAutoGrammarly()
                self.logger.info("  ✅ MANUS Auto-Grammarly enabled for SiderAI Extension")
            except Exception as e:
                self.logger.debug(f"  Auto-Grammarly init error: {e}")

        # Initialize AI Coordination
        self.ai_coordination = None
        if COORDINATION_AVAILABLE:
            try:
                self.ai_coordination = JARVISAICoordination(self.project_root)
                # Register SiderAI Extension as an AI
                self.ai_coordination._register_ai(
                    "siderai_extension",
                    "SiderAI Extension",
                    AIType.ASSISTANT,
                    ["ide_extension", "coding_assistant", "vscode_integration", "cursor_integration"]
                )
                # Sync with SiderAI Extension
                self.ai_coordination.sync_with_ai("siderai_extension")
                self.logger.info("  ✅ AI Coordination enabled for SiderAI Extension")
            except Exception as e:
                self.logger.debug(f"  AI Coordination init error: {e}")

        # Find SiderAI Extension installations
        self.extension_paths = self._find_siderai_extension()

        self.logger.info("🔌 SiderAI Extension Integration initialized")
        self.logger.info("   MANUS Auto-Grammarly: Enabled")
        self.logger.info("   AI Coordination: Enabled")

    def _find_siderai_extension(self) -> Dict[str, List[Path]]:
        try:
            """Find SiderAI Extension installations"""
            paths = {
                "vscode": [],
                "cursor": [],
                "other": []
            }

            # VS Code extensions
            vscode_paths = [
                Path.home() / ".vscode" / "extensions",
                Path.home() / "AppData" / "Roaming" / "Code" / "User" / "extensions",
            ]

            # Cursor extensions
            cursor_paths = [
                Path.home() / ".cursor" / "extensions",
                Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "extensions",
            ]

            # Search for SiderAI extension
            for path in vscode_paths:
                if path.exists():
                    siderai_ext = path / "siderai" / "siderai-*"
                    if list(path.glob("siderai*")):
                        paths["vscode"].append(path)
                        self.logger.debug(f"  Found SiderAI Extension in VS Code: {path}")

            for path in cursor_paths:
                if path.exists():
                    if list(path.glob("siderai*")):
                        paths["cursor"].append(path)
                        self.logger.debug(f"  Found SiderAI Extension in Cursor: {path}")

            return paths

        except Exception as e:
            self.logger.error(f"Error in _find_siderai_extension: {e}", exc_info=True)
            raise
    def correct_text(self, text: str) -> str:
        """Auto-correct text using MANUS Auto-Grammarly"""
        if self.auto_grammarly:
            return self.auto_grammarly.auto_correct_input(text)
        return text

    def sync_with_jarvis(self) -> bool:
        """Sync SiderAI Extension with JARVIS AI Coordination"""
        if self.ai_coordination:
            return self.ai_coordination.sync_with_ai("siderai_extension")
        return False

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "siderai_extension": {
                "enabled": True,
                "manus_auto_grammarly": self.auto_grammarly is not None,
                "ai_coordination": self.ai_coordination is not None,
                "extension_paths": {
                    "vscode": [str(p) for p in self.extension_paths["vscode"]],
                    "cursor": [str(p) for p in self.extension_paths["cursor"]],
                    "other": [str(p) for p in self.extension_paths["other"]]
                },
                "synced": self.sync_with_jarvis() if self.ai_coordination else False
            },
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SiderAI Extension Integration")
    parser.add_argument("--status", action="store_true", help="Show integration status")
    parser.add_argument("--sync", action="store_true", help="Sync with JARVIS")
    parser.add_argument("--test", type=str, help="Test auto-correction with text")

    args = parser.parse_args()

    integration = SiderAIExtensionIntegration()

    if args.status:
        status = integration.get_integration_status()
        print("\n🔌 SiderAI Extension Integration Status")
        print("="*60)
        print(json.dumps(status, indent=2))

    elif args.sync:
        print("\n🤝 Syncing SiderAI Extension with JARVIS...")
        success = integration.sync_with_jarvis()
        print(f"   {'✅ Synced' if success else '❌ Sync failed'}")

    elif args.test:
        corrected = integration.correct_text(args.test)
        print(f"\nOriginal: {args.test}")
        print(f"Corrected: {corrected}")

    else:
        parser.print_help()

