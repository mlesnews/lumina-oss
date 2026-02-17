#!/usr/bin/env python3
"""
Secret Rotation Service
Automated secret rotation for Azure Key Vault

Rotates secrets according to rotation schedules defined in configuration.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

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

logger = get_logger("SecretRotation")

try:
    from azure_service_bus_integration import (
        AzureKeyVaultClient,
        get_key_vault_client
    )
    from azure.servicebus import ServiceBusClient, ServiceBusMessage
    from azure.identity import DefaultAzureCredential
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    logger.error("Azure Key Vault integration not available")


class SecretRotationService:
    """Automated secret rotation service"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "azure" / "key_vault_config.json"
        self.rotation_log_dir = self.project_root / "data" / "secret_rotations"
        self.rotation_log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Key Vault client
        if KEY_VAULT_AVAILABLE:
            try:
                self.kv_client = get_key_vault_client()
                logger.info("Key Vault client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Key Vault client: {e}")
                self.kv_client = None
        else:
            self.kv_client = None

        # Load rotation schedules
        self.rotation_schedules = self._load_rotation_schedules()

    def _load_rotation_schedules(self) -> Dict[str, Any]:
        """Load rotation schedules from config"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("key_vault_config", {}).get("rotation_schedules", {})
        except Exception as e:
            logger.error(f"Error loading rotation schedules: {e}")
            return {}

    def generate_new_secret(self, secret_type: str) -> str:
        """
        Generate new secret value based on type

        Args:
            secret_type: Type of secret (jwt, api_key, password, etc.)

        Returns:
            New secret value
        """
        import secrets
        import string

        if secret_type in ["jwt", "api_key", "token"]:
            # Generate random string for API keys/tokens
            return secrets.token_urlsafe(64)
        elif secret_type == "password":
            # Generate strong password
            alphabet = string.ascii_letters + string.digits + string.punctuation
            return ''.join(secrets.choice(alphabet) for _ in range(32))
        else:
            # Default: random string
            return secrets.token_urlsafe(32)

    def rotate_secret(self, secret_name: str, secret_type: str) -> bool:
        """
        Rotate a secret in Key Vault

        Args:
            secret_name: Name of secret to rotate
            secret_type: Type of secret

        Returns:
            True if rotated successfully
        """
        if not self.kv_client:
            logger.error("Key Vault client not available")
            return False

        try:
            # Generate new secret
            new_secret = self.generate_new_secret(secret_type)

            # Set new secret version in Key Vault
            self.kv_client.set_secret(secret_name, new_secret)

            # Publish rotation notification to Service Bus
            self._notify_rotation(secret_name)

            logger.info(f"Rotated secret: {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Error rotating secret {secret_name}: {e}")
            return False

    def _notify_rotation(self, secret_name: str):
        """Notify services of secret rotation via Service Bus"""
        try:
            # Initialize Service Bus client
            kv_client = get_key_vault_client()
            from azure_service_bus_integration import get_service_bus_client
            sb_client = get_service_bus_client(key_vault_client=kv_client)

            # Create rotation notification message
            from azure_service_bus_integration import ServiceBusMessage, MessageType
            message = ServiceBusMessage(
                message_id=str(uuid.uuid4()),
                message_type=MessageType.INTELLIGENCE,
                timestamp=datetime.now(),
                source="secret-rotation-service",
                destination="all-services",
                payload={
                    "event_type": "secret_rotation",
                    "secret_name": secret_name,
                    "action": "new_version_created",
                    "rotation_date": datetime.now().isoformat()
                }
            )

            # Publish to intelligence topic (services subscribe to get notifications)
            sb_client.publish_to_topic("jarvis.intelligence", message)

        except Exception as e:
            logger.warning(f"Failed to send rotation notification: {e}")

    def check_rotation_schedule(self) -> List[Dict[str, Any]]:
        """
        Check which secrets are due for rotation

        Returns:
            List of secrets due for rotation
        """
        secrets_due = []

        # This would check last rotation date and compare to schedule
        # For now, return empty list (requires tracking last rotation dates)

        return secrets_due

    def rotate_scheduled_secrets(self) -> Dict[str, Any]:
        try:
            """
            Rotate all secrets due according to schedule

            Returns:
                Rotation report
            """
            report = {
                "rotation_started": datetime.now().isoformat(),
                "secrets_rotated": 0,
                "secrets_failed": 0,
                "errors": []
            }

            secrets_due = self.check_rotation_schedule()

            for secret_info in secrets_due:
                if self.rotate_secret(secret_info["name"], secret_info["type"]):
                    report["secrets_rotated"] += 1
                else:
                    report["secrets_failed"] += 1
                    report["errors"].append(f"Failed to rotate: {secret_info['name']}")

            report["rotation_completed"] = datetime.now().isoformat()
            report["success"] = report["secrets_failed"] == 0

            # Save rotation report
            report_file = self.rotation_log_dir / f"rotation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            return report


        except Exception as e:
            self.logger.error(f"Error in rotate_scheduled_secrets: {e}", exc_info=True)
            raise
def main():
    try:
        """Main rotation function"""
        import uuid
        project_root = Path(__file__).parent.parent.parent
        rotation_service = SecretRotationService(project_root)

        print("\n" + "=" * 60)
        print("Secret Rotation Service")
        print("=" * 60)

        # Check for secrets due for rotation
        secrets_due = rotation_service.check_rotation_schedule()

        if secrets_due:
            print(f"\nFound {len(secrets_due)} secrets due for rotation")
            report = rotation_service.rotate_scheduled_secrets()
            print(f"Rotated: {report['secrets_rotated']}")
            print(f"Failed: {report['secrets_failed']}")
        else:
            print("\nNo secrets due for rotation")

        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import uuid


    main()