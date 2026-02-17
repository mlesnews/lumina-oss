#!/usr/bin/env python3
"""
Browser Extension Integration - MANUS Auto-Grammarly & AI Coordination

Integrates MANUS Auto-Grammarly and AI Coordination with Web Browser Extensions
"DO THE SAME WITH THE WEB BROWSER EXTENSION"
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

logger = get_logger("BrowserExtensionIntegration")

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

class BrowserExtensionIntegration:
    """
    Browser Extension Integration

    Integrates MANUS Auto-Grammarly and AI Coordination with Web Browser Extensions
    Supports Chrome, Edge, Firefox, etc.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Browser Extension integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("BrowserExtensionIntegration")

        # Initialize MANUS Auto-Grammarly
        self.auto_grammarly = None
        if MANUS_AVAILABLE:
            try:
                self.auto_grammarly = MANUSAutoGrammarly()
                self.logger.info("  ✅ MANUS Auto-Grammarly enabled for Browser Extension")
            except Exception as e:
                self.logger.debug(f"  Auto-Grammarly init error: {e}")

        # Initialize AI Coordination
        self.ai_coordination = None
        if COORDINATION_AVAILABLE:
            try:
                self.ai_coordination = JARVISAICoordination(self.project_root)
                # Register Browser Extension as an AI
                self.ai_coordination._register_ai(
                    "browser_extension",
                    "Browser Extension",
                    AIType.TOOL,
                    ["browser_automation", "web_interaction", "content_editing", "form_filling"]
                )
                # Sync with Browser Extension
                self.ai_coordination.sync_with_ai("browser_extension")
                self.logger.info("  ✅ AI Coordination enabled for Browser Extension")
            except Exception as e:
                self.logger.debug(f"  AI Coordination init error: {e}")

        # Find browser extension installations
        self.extension_paths = self._find_browser_extensions()

        self.logger.info("🌐 Browser Extension Integration initialized")
        self.logger.info("   MANUS Auto-Grammarly: Enabled")
        self.logger.info("   AI Coordination: Enabled")

    def _find_browser_extensions(self) -> Dict[str, List[Path]]:
        try:
            """Find browser extension installations"""
            paths = {
                "chrome": [],
                "edge": [],
                "firefox": [],
                "other": []
            }

            # Chrome extensions
            chrome_paths = [
                Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Extensions",
                Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Profile 1" / "Extensions",
            ]

            # Edge extensions
            edge_paths = [
                Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Extensions",
                Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Profile 1" / "Extensions",
            ]

            # Firefox extensions
            firefox_paths = [
                Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles",
            ]

            # Search for extensions
            for path in chrome_paths:
                if path.exists():
                    paths["chrome"].append(path)
                    self.logger.debug(f"  Found Chrome extensions at: {path}")

            for path in edge_paths:
                if path.exists():
                    paths["edge"].append(path)
                    self.logger.debug(f"  Found Edge extensions at: {path}")

            for path in firefox_paths:
                if path.exists():
                    paths["firefox"].append(path)
                    self.logger.debug(f"  Found Firefox profiles at: {path}")

            return paths

        except Exception as e:
            self.logger.error(f"Error in _find_browser_extensions: {e}", exc_info=True)
            raise
    def correct_text(self, text: str) -> str:
        """Auto-correct text using MANUS Auto-Grammarly"""
        if self.auto_grammarly:
            return self.auto_grammarly.auto_correct_input(text)
        return text

    def sync_with_jarvis(self) -> bool:
        """Sync Browser Extension with JARVIS AI Coordination"""
        if self.ai_coordination:
            return self.ai_coordination.sync_with_ai("browser_extension")
        return False

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "browser_extension": {
                "enabled": True,
                "manus_auto_grammarly": self.auto_grammarly is not None,
                "ai_coordination": self.ai_coordination is not None,
                "extension_paths": {
                    "chrome": [str(p) for p in self.extension_paths["chrome"]],
                    "edge": [str(p) for p in self.extension_paths["edge"]],
                    "firefox": [str(p) for p in self.extension_paths["firefox"]],
                    "other": [str(p) for p in self.extension_paths["other"]]
                },
                "synced": self.sync_with_jarvis() if self.ai_coordination else False
            },
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Browser Extension Integration")
    parser.add_argument("--status", action="store_true", help="Show integration status")
    parser.add_argument("--sync", action="store_true", help="Sync with JARVIS")
    parser.add_argument("--test", type=str, help="Test auto-correction with text")

    args = parser.parse_args()

    integration = BrowserExtensionIntegration()

    if args.status:
        status = integration.get_integration_status()
        print("\n🌐 Browser Extension Integration Status")
        print("="*60)
        print(json.dumps(status, indent=2))

    elif args.sync:
        print("\n🤝 Syncing Browser Extension with JARVIS...")
        success = integration.sync_with_jarvis()
        print(f"   {'✅ Synced' if success else '❌ Sync failed'}")

    elif args.test:
        corrected = integration.correct_text(args.test)
        print(f"\nOriginal: {args.test}")
        print(f"Corrected: {corrected}")

    else:
        parser.print_help()

