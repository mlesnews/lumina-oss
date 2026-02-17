#!/usr/bin/env python3
"""
n8n SYPHON Integration

Integrates SYPHON system with n8n workflows for email and SMS extraction.

Author: <COMPANY_NAME> LLC
Date: 2025-01-24
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from syphon import SYPHONSystem, SYPHONConfig, SubscriptionTier, DataSourceType
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class N8NSyphonIntegration:
    """Integration between n8n workflows and SYPHON system"""

    def __init__(
        self,
        project_root: Path,
        n8n_config_path: Optional[Path] = None,
        subscription_tier: SubscriptionTier = SubscriptionTier.BASIC
    ) -> None:
        """
        Initialize n8n SYPHON integration.

        Args:
            project_root: Root path of the project
            n8n_config_path: Path to n8n config file
            subscription_tier: Subscription tier for features
        """
        self.project_root = Path(project_root)
        self.n8n_config_path = n8n_config_path or (self.project_root / "config" / "n8n" / "unified_communications_config.json")

        # Initialize SYPHON with config
        config = SYPHONConfig(
            project_root=self.project_root,
            subscription_tier=subscription_tier,
            enable_self_healing=True,
            enable_banking=True
        )
        self.syphon = SYPHONSystem(config)
        self.logger = get_logger("N8NSyphonIntegration")

    def process_email_from_n8n(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process email from n8n workflow and syphon intelligence.

        Args:
            email_data: Email data from n8n workflow
                {
                    "email_id": "...",
                    "subject": "...",
                    "body": "...",
                    "from": "...",
                    "to": "...",
                    "metadata": {...}
                }

        Returns:
            Syphoned data as dictionary
        """
        try:
            result = self.syphon.extract_email(
                email_id=email_data.get("email_id", ""),
                subject=email_data.get("subject", ""),
                body=email_data.get("body", ""),
                from_address=email_data.get("from", ""),
                to_address=email_data.get("to", ""),
                metadata=email_data.get("metadata")
            )

            if result.success and result.data:
                return {
                    "success": True,
                    "syphon_data": result.data.to_dict(),
                    "actionable_items_count": len(result.data.actionable_items),
                    "tasks_count": len(result.data.tasks),
                    "decisions_count": len(result.data.decisions),
                    "intelligence_count": len(result.data.intelligence)
                }
            else:
                return {
                    "success": False,
                    "error": result.error or "Extraction failed"
                }
        except Exception as e:
            self.logger.error(f"Error processing email from n8n: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def process_sms_from_n8n(self, sms_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process SMS from n8n workflow and syphon intelligence.

        Args:
            sms_data: SMS data from n8n workflow
                {
                    "sms_id": "...",
                    "message": "...",
                    "from": "...",
                    "to": "...",
                    "metadata": {...}
                }

        Returns:
            Syphoned data as dictionary
        """
        try:
            result = self.syphon.extract_sms(
                sms_id=sms_data.get("sms_id", ""),
                message=sms_data.get("message", ""),
                from_number=sms_data.get("from", ""),
                to_number=sms_data.get("to", ""),
                metadata=sms_data.get("metadata")
            )

            if result.success and result.data:
                return {
                    "success": True,
                    "syphon_data": result.data.to_dict(),
                    "actionable_items_count": len(result.data.actionable_items),
                    "tasks_count": len(result.data.tasks),
                    "decisions_count": len(result.data.decisions),
                    "intelligence_count": len(result.data.intelligence)
                }
            else:
                return {
                    "success": False,
                    "error": result.error or "Extraction failed"
                }
        except Exception as e:
            self.logger.error(f"Error processing SMS from n8n: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_syphon_webhook_endpoint(self, source_type: str) -> str:
        """
        Get webhook endpoint for syphon processing.

        Args:
            source_type: "email" or "sms"

        Returns:
            Webhook endpoint path
        """
        return f"/webhook/syphon/{source_type}"

    def create_n8n_syphon_workflow_config(self) -> Dict[str, Any]:
        try:
            """Create n8n workflow configuration with syphon integration"""
            return {
                "email_syphon": {
                    "workflow_id": "email_syphon",
                    "name": "Email SYPHON Extraction",
                    "webhook_path": "/webhook/syphon/email",
                    "trigger_type": "webhook",
                    "nodes": [
                        {
                            "type": "webhook",
                            "name": "Receive Email",
                            "settings": {
                                "path": "syphon/email",
                                "httpMethod": "POST"
                            }
                        },
                        {
                            "type": "function",
                            "name": "Process with SYPHON",
                            "settings": {
                                "functionCode": """
                                // Call SYPHON system
                                const syphonResult = await $http.post('http://localhost:8000/api/syphon/email', {
                                    body: $json
                                });
                                return syphonResult;
                                """
                            }
                        },
                        {
                            "type": "function",
                            "name": "Extract Actionable Items",
                            "settings": {
                                "functionCode": """
                                // Extract actionable items from syphon result
                                const actionable = $json.syphon_data.actionable_items || [];
                                return { actionable_items: actionable };
                                """
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Notify System",
                            "settings": {
                                "url": "http://localhost:8000/api/intelligence/actionable",
                                "method": "POST"
                            }
                        }
                    ],
                    "enabled": True
                },
                "sms_syphon": {
                    "workflow_id": "sms_syphon",
                    "name": "SMS SYPHON Extraction",
                    "webhook_path": "/webhook/syphon/sms",
                    "trigger_type": "webhook",
                    "nodes": [
                        {
                            "type": "webhook",
                            "name": "Receive SMS",
                            "settings": {
                                "path": "syphon/sms",
                                "httpMethod": "POST"
                            }
                        },
                        {
                            "type": "function",
                            "name": "Process with SYPHON",
                            "settings": {
                                "functionCode": """
                                // Call SYPHON system
                                const syphonResult = await $http.post('http://localhost:8000/api/syphon/sms', {
                                    body: $json
                                });
                                return syphonResult;
                                """
                            }
                        },
                        {
                            "type": "function",
                            "name": "Extract Actionable Items",
                            "settings": {
                                "functionCode": """
                                // Extract actionable items from syphon result
                                const actionable = $json.syphon_data.actionable_items || [];
                                return { actionable_items: actionable };
                                """
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Notify System",
                            "settings": {
                                "url": "http://localhost:8000/api/intelligence/actionable",
                                "method": "POST"
                            }
                        }
                    ],
                    "enabled": True
                }
            }


        except Exception as e:
            self.logger.error(f"Error in create_n8n_syphon_workflow_config: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    # Test integration
    project_root = Path(__file__).parent.parent.parent
    integration = N8NSyphonIntegration(project_root)

    # Test email processing
    test_email = {
        "email_id": "test_n8n_001",
        "subject": "Action Required: Complete Blueprint",
        "body": "We need to complete the blueprint. Please follow up by Friday.",
        "from": "team@example.com",
        "to": "dev@example.com"
    }

    result = integration.process_email_from_n8n(test_email)
    print(f"Email syphon result: {json.dumps(result, indent=2)}")

    # Test SMS processing
    test_sms = {
        "sms_id": "test_n8n_002",
        "message": "Urgent: Deploy P0 containment ASAP",
        "from": "+1234567890",
        "to": "+0987654321"
    }

    result = integration.process_sms_from_n8n(test_sms)
    print(f"\nSMS syphon result: {json.dumps(result, indent=2)}")

