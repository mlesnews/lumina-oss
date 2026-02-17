"""
Register All Systems with Lumina Extension
Updates Lumina extension configuration to include all new systems.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("register_with_lumina")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def register_all_systems_with_lumina(project_root: Optional[Path] = None) -> Dict[str, Any]:
    try:
        """
        Register all systems with Lumina extension.

        Args:
            project_root: Project root directory

        Returns:
            Registration result
        """
        if project_root is None:
            project_root = Path("D:/Dropbox/my_projects")
        else:
            project_root = Path(project_root)

        # Load existing registration
        registration_path = project_root / "config" / "lumina_extensions_integration.json"

        if registration_path.exists():
            with open(registration_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        else:
            existing = {"extensions": {}}

        # Update with all systems
        extensions = {
            "r5_system": {
                "name": "R5 Living Context Matrix",
                "type": "knowledge_aggregation",
                "enabled": True,
                "api_endpoint": "http://localhost:8000/r5",
                "integrations": ["n8n", "jupyter"],
                "module": "scripts/python/r5_living_context_matrix.py",
                "api_server": "scripts/python/r5_api_server.py",
                "config": "config/r5/r5_config.json"
            },
            "droid_actor_system": {
                "name": "Droid Actor System",
                "type": "workflow_verification",
                "enabled": True,
                "location": "@helpdesk",
                "coordinator": "C-3PO",
                "droids": ["c3po", "r2d2", "k2so", "2-1b", "ig88", "mousedroid", "r5", "marvin"],
                "module": "scripts/python/droid_actor_system.py",
                "routing_config": "config/droid_actor_routing.json"
            },
            "v3_verification": {
                "name": "@v3 Verification Logic",
                "type": "verification",
                "enabled": True,
                "all_droids": True,
                "verification_logic": "scripts/python/v3_verification.py",
                "class": "V3Verification",
                "auto_verify": True,
                "verification_required": True
            },
            "helpdesk": {
                "name": "@helpdesk",
                "type": "coordination",
                "enabled": True,
                "location": "@helpdesk",
                "coordinator": "C-3PO",
                "escalation_path": "C-3PO → JARVIS",
                "structure_config": "config/helpdesk/helpdesk_structure.json",
                "droids_config": "config/helpdesk/droids.json"
            },
            "jarvis_helpdesk_integration": {
                "name": "JARVIS Helpdesk Integration",
                "type": "workflow_integration",
                "enabled": True,
                "module": "scripts/python/jarvis_helpdesk_integration.py",
                "class": "JARVISHelpdeskIntegration",
                "features": [
                    "workflow_verification",
                    "droid_actor_routing",
                    "r5_ingestion",
                    "jarvis_escalation"
                ],
                "integration_points": {
                    "pre_execution": "droid_actor_verification",
                    "post_execution": "r5_knowledge_ingestion",
                    "escalation": "c3po_to_jarvis"
                }
            },
            "syphon_system": {
                "name": "SYPHON Intelligence Extraction System",
                "type": "intelligence_extraction",
                "enabled": True,
                "module": "scripts/python/syphon",
                "class": "SYPHONSystem",
                "version": "1.0.0",
                "features": [
                    "email_extraction",
                    "sms_extraction",
                    "banking_extraction",
                    "self_healing",
                    "health_monitoring",
                    "basic_budgeting",
                    "premium_analytics"
                ],
                "subscription_tiers": ["basic", "premium", "enterprise"],
                "integration_points": {
                    "n8n": "scripts/python/syphon/integration/n8n.py",
                    "email_webhook": "/webhook/syphon/email",
                    "sms_webhook": "/webhook/syphon/sms",
                    "banking_api": "scripts/python/syphon/extractors.py::BankingExtractor"
                },
                "config": {
                    "enable_self_healing": True,
                    "health_check_interval": 60,
                    "enable_banking": True,
                    "storage_backend": "json"
                }
            }
        }

        # Merge with existing (preserve any custom settings)
        for key, value in extensions.items():
            if key in existing.get("extensions", {}):
                # Merge, keeping existing custom fields
                existing["extensions"][key].update(value)
            else:
                existing["extensions"][key] = value

        # Update metadata
        existing["updated_at"] = datetime.now().isoformat()
        existing["version"] = "6.0.0"
        existing["registered_systems"] = list(extensions.keys())

        # Save updated registration
        registration_path.parent.mkdir(parents=True, exist_ok=True)
        with open(registration_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2)

        print(f"[SUCCESS] Registered {len(extensions)} systems with Lumina extension")
        print(f"  - R5 System")
        print(f"  - Droid Actor System")
        print(f"  - @v3 Verification")
        print(f"  - @helpdesk")
        print(f"  - JARVIS Helpdesk Integration")
        print(f"  - SYPHON Intelligence Extraction System")

        return existing


    except Exception as e:
        logger.error(f"Error in register_all_systems_with_lumina: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    registration = register_all_systems_with_lumina()
    print(f"\n[SUCCESS] Registration complete: {registration['updated_at']}")

