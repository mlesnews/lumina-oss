#!/usr/bin/env python3
"""
JARVIS Cloud Failover Protocol
Forces the system to use Azure OpenAI model resources when standard connections stall.

Tags: #FAILOVER #AZURE #OPENAI #STABILITY @AUTO @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from auto_mode_model_selector import AutoModeModelSelector, ModelSpectrum, RequestAnalysis, ModelProvider
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    AutoModeModelSelector = None

logger = get_logger("JARVISCloudFailover")

class JARVISCloudFailover:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.config_file = self.project_root / "config" / "llm_routing_override.json"

    def activate_azure_failover(self) -> bool:
        """Force Azure OpenAI as the primary cloud provider"""
        self.logger.info("⚡ Activating Azure OpenAI Failover Protocol...")

        override = {
            "primary_cloud_provider": "azure_openai",
            "force_azure": True,
            "activated_at": datetime.now().isoformat(),
            "reason": "Operator requested stability fix for stalled session"
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(override, f, indent=2)
            self.logger.info("✅ Azure OpenAI is now the preferred cloud provider.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to set failover: {e}")
            return False

    def check_status(self) -> Dict[str, Any]:
        try:
            """Check if failover is active"""
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {"force_azure": False}

        except Exception as e:
            self.logger.error(f"Error in check_status: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    from datetime import datetime
    failover = JARVISCloudFailover()

    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        print(json.dumps(failover.check_status(), indent=2))
    else:
        failover.activate_azure_failover()
