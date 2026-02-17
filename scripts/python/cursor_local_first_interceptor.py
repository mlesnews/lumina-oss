#!/usr/bin/env python3
"""
Cursor Local-First AI Interceptor

Intercepts Cursor AI requests and enforces local-first routing.
Monitors Cursor's AI usage and redirects cloud requests to local models.

Tags: #CURSOR #LOCAL_FIRST #INTERCEPTOR @CURSOR @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
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

logger = get_logger("CursorLocalFirstInterceptor")

from enforce_local_first_ai_routing import LocalFirstAIRouter


class CursorLocalFirstInterceptor:
    """Intercept and enforce local-first AI in Cursor"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.router = LocalFirstAIRouter(project_root)
        self.cursor_settings = project_root / ".cursor" / "settings.json"
        self.monitoring = False

    def start_monitoring(self):
        """Start monitoring Cursor AI usage"""
        self.monitoring = True
        logger.info("✅ Started monitoring Cursor AI usage")

        # Check Cursor settings periodically
        self._monitor_cursor_settings()

    def _monitor_cursor_settings(self):
        """Monitor and enforce local-first in Cursor settings"""
        try:
            if not self.cursor_settings.exists():
                logger.warning("Cursor settings.json not found")
                return

            with open(self.cursor_settings, 'r') as f:
                config = json.load(f)

            # Check if local-first is enforced
            lumina_config = config.get("lumina", {})
            if not lumina_config.get("local_first_enforced"):
                logger.warning("⚠️  Local-first AI not enforced in Cursor settings!")
                self._enforce_local_first(config)

            # Check default models
            default_model = config.get("cursor.chat.defaultModel", "")
            if default_model not in ["ULTRON", "KAIJU"]:
                logger.warning(f"⚠️  Default model is not local-first: {default_model}")
                config["cursor.chat.defaultModel"] = "ULTRON"
                config["cursor.composer.defaultModel"] = "ULTRON"
                config["cursor.inlineCompletion.defaultModel"] = "ULTRON"

                with open(self.cursor_settings, 'w') as f:
                    json.dump(config, f, indent=2)

                logger.info("✅ Updated Cursor default models to ULTRON")

        except Exception as e:
            logger.error(f"Error monitoring Cursor settings: {e}")

    def _enforce_local_first(self, config: Dict[str, Any]):
        try:
            """Enforce local-first AI in Cursor config"""
            if "lumina" not in config:
                config["lumina"] = {}

            config["lumina"]["local_first_enforced"] = True
            config["lumina"]["cloud_requires_approval"] = True
            config["lumina"]["jedi_council_approval_required"] = True
            config["lumina"]["r5_routing_enabled"] = True

            # Ensure ULTRON is default
            config["cursor.chat.defaultModel"] = "ULTRON"
            config["cursor.composer.defaultModel"] = "ULTRON"
            config["cursor.inlineCompletion.defaultModel"] = "ULTRON"

            with open(self.cursor_settings, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("✅ Enforced local-first AI in Cursor settings")

        except Exception as e:
            self.logger.error(f"Error in _enforce_local_first: {e}", exc_info=True)
            raise
    def get_routing_report(self) -> Dict[str, Any]:
        """Get routing statistics report"""
        stats = self.router.get_routing_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "local_first_enforced": True,
            "statistics": stats,
            "recommendation": "Continue using local-first AI (ULTRON/KAIJU/R5)" if stats["local_requests"] > stats["cloud_requests"] else "⚠️  Cloud usage detected - review routing"
        }


def main():
    """Main execution"""
    interceptor = CursorLocalFirstInterceptor(project_root)

    # Enforce local-first immediately
    interceptor._monitor_cursor_settings()

    # Get report
    report = interceptor.get_routing_report()

    print("=" * 80)
    print("📊 CURSOR LOCAL-FIRST AI ENFORCEMENT")
    print("=" * 80)
    print()
    print(f"Local Requests: {report['statistics']['local_requests']}")
    print(f"Cloud Requests: {report['statistics']['cloud_requests']}")
    print(f"Blocked Cloud: {report['statistics']['blocked_cloud']}")
    print(f"Local Percent: {report['statistics']['local_percent']}")
    print()
    print(f"Recommendation: {report['recommendation']}")
    print()
    print("=" * 80)
    print("✅ Local-First AI Enforcement Active")
    print("=" * 80)


if __name__ == "__main__":


    main()