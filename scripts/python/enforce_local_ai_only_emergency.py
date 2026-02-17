#!/usr/bin/env python3
"""
Emergency Local AI Only Enforcement
Preserve Cloud Tokens - Route ALL AI to Local Resources

CRITICAL: Cloud tokens will be exhausted by 15th at current rate.
This script enforces local-only AI routing to preserve cloud tokens.

Local Resources:
- ULTRON: localhost:11434 (laptop local AI)
- KAIJU Number Eight: <NAS_IP>:11434 (Desktop PC - 7 models, NOT NAS)
- NAS (DS2118+): <NAS_PRIMARY_IP> (storage/email, NOT Ollama)
- ULTRON Virtual Hybrid Cluster: Combines ULTRON + KAIJU

Tags: #EMERGENCY #LOCAL_AI #TOKEN_PRESERVATION #ULTRON #IRON_LEGION
@JARVIS @MARVIN @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List
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

logger = get_logger("EnforceLocalAIOnly")

def enforce_cursor_local_only(project_root: Path) -> bool:
    """Enforce Cursor IDE to use local AI only"""
    settings_file = project_root / ".cursor" / "settings.json"

    if not settings_file.exists():
        logger.error(f"❌ Cursor settings not found: {settings_file}")
        return False

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Ensure all models are local-only
        local_models = []

        # ULTRON (localhost)
        ultron_model = {
            "title": "ULTRON",
            "name": "ULTRON",
            "provider": "ollama",
            "model": "qwen2.5:72b",
            "apiBase": "http://localhost:11434",
            "contextLength": 32768,
            "description": "ULTRON - Local laptop AI (LOCAL ONLY - NO CLOUD)",
            "localOnly": True,
            "skipProviderSelection": True
        }
        local_models.append(ultron_model)

        # KAIJU Number Eight (Desktop PC, NOT NAS)
        kaiju_model = {
            "title": "KAIJU (Iron Legion)",
            "name": "KAIJU",
            "provider": "ollama",
            "model": "llama3.2:3b",
            "apiBase": "http://<NAS_IP>:11434",
            "contextLength": 8192,
            "description": "KAIJU Number Eight - Desktop PC (NOT NAS) - 7 models (LOCAL ONLY - NO CLOUD)",
            "localOnly": True,
            "skipProviderSelection": True
        }
        local_models.append(kaiju_model)

        # ULTRON Virtual Hybrid Cluster
        ultron_cluster = {
            "title": "ULTRON",
            "name": "ULTRON",
            "provider": "ollama",
            "model": "qwen2.5:72b",
            "apiBase": "http://localhost:11434",
            "contextLength": 32768,
            "description": "ULTRON Virtual Hybrid Cluster - Laptop + KAIJU (LOCAL ONLY)",
            "localOnly": True,
            "skipProviderSelection": True,
            "cluster": {
                "type": "virtual_hybrid",
                "nodes": [
                    {
                        "name": "ULTRON Local",
                        "endpoint": "http://localhost:11434",
                        "priority": 1
                    },
                    {
                        "name": "KAIJU",
                        "endpoint": "http://<NAS_IP>:11434",  # KAIJU Number Eight (Desktop PC)
                        "priority": 2
                    }
                ],
                "routing": "load_balanced"
            }
        }

        # Update all model arrays
        if "cursor.model" in settings:
            settings["cursor.model"]["customModels"] = local_models

        if "cursor.chat" in settings:
            settings["cursor.chat"]["customModels"] = [ultron_cluster, kaiju_model]
            settings["cursor.chat"]["defaultModel"] = "ULTRON"

        if "cursor.composer" in settings:
            settings["cursor.composer"]["customModels"] = [ultron_cluster, kaiju_model]
            settings["cursor.composer"]["defaultModel"] = "ULTRON"

        if "cursor.inlineCompletion" in settings:
            settings["cursor.inlineCompletion"]["defaultModel"] = "ULTRON"

        if "cursor.agent" in settings:
            if "customModels" in settings["cursor.agent"]:
                settings["cursor.agent"]["customModels"] = [ultron_cluster, kaiju_model]
            settings["cursor.agent"]["defaultModel"] = "ULTRON"

        # Add emergency comment
        settings["_emergency_local_only"] = {
            "enabled": True,
            "timestamp": datetime.now().isoformat(),
            "reason": "Cloud tokens exhausted by 15th - FORCE LOCAL ONLY",
            "cloud_models_blocked": True,
            "local_resources": {
                "ultron": "http://localhost:11434",
                "kaiju_iron_legion": "http://<NAS_IP>:11434"  # KAIJU Number Eight (Desktop PC)
            }
        }

        # Write back
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        logger.info("✅ Cursor settings updated - LOCAL ONLY enforced")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to update Cursor settings: {e}")
        return False

def verify_local_resources() -> Dict[str, bool]:
    """Verify local AI resources are available"""
    import requests

    results = {}

    # Check ULTRON (localhost)
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        results["ultron_local"] = response.status_code == 200
        if results["ultron_local"]:
            logger.info("✅ ULTRON (localhost:11434) - Available")
        else:
            logger.warning("⚠️  ULTRON (localhost:11434) - Not responding")
    except Exception as e:
        results["ultron_local"] = False
        logger.warning(f"⚠️  ULTRON (localhost:11434) - Error: {e}")

    # Check KAIJU Number Eight (Desktop PC, NOT NAS)
    try:
        response = requests.get("http://<NAS_IP>:11434/api/tags", timeout=2)
        results["kaiju_iron_legion"] = response.status_code == 200
        if results["kaiju_iron_legion"]:
            logger.info("✅ KAIJU Number Eight (<NAS_IP>:11434) - Available")
        else:
            logger.warning("⚠️  KAIJU Number Eight (<NAS_IP>:11434) - Not responding")
    except Exception as e:
        results["kaiju_iron_legion"] = False
        logger.warning(f"⚠️  KAIJU Number Eight (<NAS_IP>:11434) - Error: {e}")

    return results

def main():
    """Main enforcement function"""
    logger.info("=" * 80)
    logger.info("🚨 EMERGENCY: ENFORCING LOCAL AI ONLY")
    logger.info("   Preserving cloud tokens (exhausted by 15th at current rate)")
    logger.info("=" * 80)

    # Verify local resources
    logger.info("\n📡 Verifying local AI resources...")
    resources = verify_local_resources()

    if not any(resources.values()):
        logger.error("❌ NO LOCAL AI RESOURCES AVAILABLE!")
        logger.error("   Please start Ollama on localhost or KAIJU Number Eight (<NAS_IP>)")
        return False

    # Enforce Cursor settings
    logger.info("\n🔧 Enforcing Cursor IDE local-only mode...")
    if enforce_cursor_local_only(project_root):
        logger.info("✅ Cursor configured for LOCAL ONLY")
    else:
        logger.error("❌ Failed to configure Cursor")
        return False

    logger.info("\n" + "=" * 80)
    logger.info("✅ LOCAL AI ONLY ENFORCEMENT COMPLETE")
    logger.info("=" * 80)
    logger.info("\n📋 Next Steps:")
    logger.info("   1. Restart Cursor IDE")
    logger.info("   2. Verify model selector shows 'ULTRON' (not cloud models)")
    logger.info("   3. Check Cursor Settings > Features > Chat/Composer/Agent")
    logger.info("   4. Ensure all defaults are set to 'ULTRON'")
    logger.info("\n💡 Local Resources:")
    if resources.get("ultron_local"):
        logger.info("   ✅ ULTRON: http://localhost:11434")
    if resources.get("kaiju_iron_legion"):
        logger.info("   ✅ KAIJU Number Eight: http://<NAS_IP>:11434 (7 models)")

    return True

if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = main()