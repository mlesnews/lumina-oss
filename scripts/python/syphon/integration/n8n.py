#!/usr/bin/env python3
"""
n8n SYPHON Integration

Integrates SYPHON system with n8n workflows for email and SMS extraction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from syphon import SYPHONSystem, SYPHONConfig, SubscriptionTier

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


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
        """Process email from n8n workflow and syphon intelligence"""
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
        """Process SMS from n8n workflow and syphon intelligence"""
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

