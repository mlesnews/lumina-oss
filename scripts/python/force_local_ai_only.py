#!/usr/bin/env python3
"""
Force Local AI Only - Emergency Cost Control
<COMPANY_NAME> LLC

IMMEDIATE ACTION: Disable all cloud AI, force local only

@JARVIS @MARVIN @TONY @MACE @GANDALF
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("force_local_ai_only")


script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def force_local_ai_only(project_root: Path):
    try:
        """Force local AI only - disable all cloud services"""

        print("🚨 FORCING LOCAL AI ONLY - DISABLING CLOUD SERVICES")
        print("=" * 60)

        config_dir = project_root / "config"

        # 1. Update local_ai_config.json to force local
        local_ai_config = config_dir / "local_ai_config.json"
        if local_ai_config.exists():
            with open(local_ai_config, 'r') as f:
                config = json.load(f)

            # Force local only
            config["enabled"] = True
            config["use_iron_legion"] = True
            config["force_local_only"] = True
            config["block_cloud_apis"] = True
            config["emergency_cost_control"] = True

            with open(local_ai_config, 'w') as f:
                json.dump(config, f, indent=2)

            print("✅ Updated local_ai_config.json - FORCED LOCAL ONLY")

        # 2. Create cloud API blocker config
        blocker_config = {
            "version": "1.0.0",
            "name": "Cloud API Blocker - Emergency Cost Control",
            "enabled": True,
            "blocked_providers": [
                "openai",
                "anthropic",
                "azure_openai",
                "google_ai",
                "cohere"
            ],
            "allowed_providers": [
                "local_ollama",
                "llama3.2:3b",
                "kaiju_iron_legion"
            ],
            "emergency_mode": True,
            "reason": "Cost control - local AI only",
            "timestamp": "2025-01-27"
        }

        blocker_file = config_dir / "cloud_api_blocker.json"
        with open(blocker_file, 'w') as f:
            json.dump(blocker_config, f, indent=2)

        print("✅ Created cloud_api_blocker.json - BLOCKING ALL CLOUD APIs")

        # 3. Update token tracker to show local-only mode
        token_tracker = config_dir / "ai_token_request_tracker.json"
        if token_tracker.exists():
            with open(token_tracker, 'r') as f:
                tracker = json.load(f)

            tracker["emergency_mode"] = True
            tracker["local_ai_only"] = True
            tracker["cloud_apis_blocked"] = True
            tracker["cost_control_active"] = True

            with open(token_tracker, 'w') as f:
                json.dump(tracker, f, indent=2)

            print("✅ Updated token tracker - EMERGENCY MODE ACTIVE")

        print("\n" + "=" * 60)
        print("✅ LOCAL AI ONLY MODE ACTIVATED")
        print("   • All cloud APIs blocked")
        print("   • Only local resources allowed")
        print("   • Cost control active")
        print("=" * 60 + "\n")


    except Exception as e:
        logger.error(f"Error in force_local_ai_only: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    force_local_ai_only(project_root)

