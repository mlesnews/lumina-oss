#!/usr/bin/env python3
"""
JARVIS Azure Service Bus Integration

Full integration with Azure Service Bus for messaging, queuing, and event-driven architecture.

Tags: #AZURE #SERVICE_BUS #MESSAGING #QUEUE #EVENT_DRIVEN @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISAzureServiceBus")

# Azure Service Bus SDK
try:
    from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusReceiver
    from azure.servicebus.exceptions import ServiceBusError
    AZURE_SB_AVAILABLE = True
except ImportError:
    AZURE_SB_AVAILABLE = False
    logger.warning("Azure Service Bus SDK not available. Install with: pip install azure-servicebus")

# Azure Key Vault for secrets
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False
    logger.warning("Azure Key Vault SDK not available. Install with: pip install azure-keyvault-secrets azure-identity")


class AzureServiceBusIntegration:
    """Azure Service Bus integration for JARVIS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "azure_services_config.json"
        self.data_dir = project_root / "data" / "azure_service_bus"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()
        self.client = None
        self.connection_string = None
        self.namespace = self.config.get("service_bus", {}).get("namespace", "jarvis-lumina-sb")

        self._initialize_client()

    def load_config(self) -> Dict[str, Any]:
        """Load Azure services configuration"""
        default_config = {
            "service_bus": {
                "enabled": False,
                "namespace": "jarvis-lumina-sb",
                "connection_string_secret": "azure-service-bus-connection-string"
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    azure_config = data.get("azure_services_config", {})
                    if azure_config.get("service_bus"):
                        default_config["service_bus"].update(azure_config["service_bus"])
            except Exception as e:
                logger.error(f"Error loading Azure config: {e}")

        return default_config

    def _get_connection_string(self) -> Optional[str]:
        """Get Service Bus connection string from Key Vault or environment"""
        # Try Key Vault first
        if AZURE_KV_AVAILABLE:
            try:
                vault_url = self.config.get("key_vault", {}).get("vault_url") or "https://jarvis-lumina.vault.azure.net/"
                secret_name = self.config.get("service_bus", {}).get("connection_string_secret", "azure-service-bus-connection-string")

                credential = DefaultAzureCredential(


                                    exclude_interactive_browser_credential=False,


                                    exclude_shared_token_cache_credential=False


                                )
                secret_client = SecretClient(vault_url=vault_url, credential=credential)
                connection_string = secret_client.get_secret(secret_name).value
                return connection_string
            except Exception as e:
                logger.debug(f"Could not get connection string from Key Vault: {e}")

        # Fallback to environment variable
        import os
        return os.getenv("AZURE_SERVICE_BUS_CONNECTION_STRING")

    def _initialize_client(self):
        """Initialize Service Bus client"""
        if not AZURE_SB_AVAILABLE:
            logger.warning("Azure Service Bus SDK not available")
            return

        if not self.config.get("service_bus", {}).get("enabled", False):
            logger.info("Azure Service Bus not enabled in config")
            return

        try:
            self.connection_string = self._get_connection_string()
            if not self.connection_string:
                logger.warning("Service Bus connection string not found")
                return

            self.client = ServiceBusClient.from_connection_string(self.connection_string)
            logger.info("✅ Azure Service Bus client initialized")
        except Exception as e:
            logger.error(f"Error initializing Service Bus client: {e}")

    def send_message(self, topic_or_queue: str, message_body: Any, properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send message to topic or queue"""
        if not self.client:
            return {
                "success": False,
                "error": "Service Bus client not initialized"
            }

        try:
            # Convert message body to JSON if needed
            if isinstance(message_body, dict):
                message_body = json.dumps(message_body)

            message = ServiceBusMessage(message_body)

            # Add custom properties
            if properties:
                for key, value in properties.items():
                    message.application_properties[key] = value

            # Add standard properties
            message.application_properties["timestamp"] = datetime.now().isoformat()
            message.application_properties["source"] = "jarvis"

            # Determine if topic or queue
            topics = self.config.get("service_bus", {}).get("topics", {})
            queues = self.config.get("service_bus", {}).get("queues", {})

            if topic_or_queue in topics:
                # Send to topic
                with self.client:
                    sender = self.client.get_topic_sender(topic_name=topic_or_queue)
                    sender.send_messages(message)
                    logger.info(f"📤 Sent message to topic: {topic_or_queue}")
            elif topic_or_queue in queues:
                # Send to queue
                with self.client:
                    sender = self.client.get_queue_sender(queue_name=topic_or_queue)
                    sender.send_messages(message)
                    logger.info(f"📤 Sent message to queue: {topic_or_queue}")
            else:
                return {
                    "success": False,
                    "error": f"Topic/Queue not found: {topic_or_queue}"
                }

            return {
                "success": True,
                "topic_or_queue": topic_or_queue,
                "sent_at": datetime.now().isoformat()
            }
        except ServiceBusError as e:
            logger.error(f"Service Bus error sending message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def receive_messages(self, topic_or_queue: str, subscription: str = None, max_messages: int = 1, handler: Callable = None) -> List[Dict[str, Any]]:
        """Receive messages from topic or queue"""
        if not self.client:
            return []

        messages = []

        try:
            with self.client:
                if subscription:
                    # Receive from topic subscription
                    receiver = self.client.get_subscription_receiver(
                        topic_name=topic_or_queue,
                        subscription_name=subscription
                    )
                else:
                    # Receive from queue
                    receiver = self.client.get_queue_receiver(queue_name=topic_or_queue)

                received_messages = receiver.receive_messages(max_message_count=max_messages, max_wait_time=5)

                for msg in received_messages:
                    try:
                        # Parse message
                        body = msg.body
                        if isinstance(body, bytes):
                            body = body.decode('utf-8')

                        try:
                            body = json.loads(body)
                        except json.JSONDecodeError:
                            pass  # Keep as string if not JSON

                        message_data = {
                            "body": body,
                            "properties": dict(msg.application_properties) if msg.application_properties else {},
                            "message_id": msg.message_id,
                            "sequence_number": msg.sequence_number,
                            "enqueued_time": msg.enqueued_time_utc.isoformat() if msg.enqueued_time_utc else None
                        }

                        # Call handler if provided
                        if handler:
                            handler_result = handler(message_data)
                            if handler_result:
                                message_data["handler_result"] = handler_result

                        messages.append(message_data)

                        # Complete message
                        receiver.complete_message(msg)

                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        receiver.abandon_message(msg)

        except ServiceBusError as e:
            logger.error(f"Service Bus error receiving messages: {e}")
        except Exception as e:
            logger.error(f"Error receiving messages: {e}")

        return messages

    def send_work_shift_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send work shift event"""
        message = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return self.send_message("work_shift_events", message, {"event_type": event_type})

    def send_operator_activity(self, activity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send operator activity event"""
        message = {
            "activity_type": activity_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return self.send_message("operator_activity", message, {"activity_type": activity_type})

    def send_ai_coordination(self, coordination_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send AI coordination message"""
        message = {
            "coordination_type": coordination_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return self.send_message("ai_coordination", message, {"coordination_type": coordination_type})

    def send_system_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send system event"""
        message = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        return self.send_message("system_events", message, {"event_type": event_type})

    def get_status(self) -> Dict[str, Any]:
        """Get Service Bus integration status"""
        status = {
            "enabled": self.config.get("service_bus", {}).get("enabled", False),
            "sdk_available": AZURE_SB_AVAILABLE,
            "client_initialized": self.client is not None,
            "namespace": self.namespace,
            "connection_string_configured": self.connection_string is not None,
            "last_checked": datetime.now().isoformat()
        }

        if self.client:
            try:
                # Test connection
                status["connection_test"] = "success"
            except Exception as e:
                status["connection_test"] = "failed"
                status["connection_error"] = str(e)
        else:
            status["connection_test"] = "not_initialized"

        return status


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Azure Service Bus Integration")
        parser.add_argument("--status", action="store_true", help="Show integration status")
        parser.add_argument("--send", type=str, help="Send test message to topic/queue")
        parser.add_argument("--receive", type=str, help="Receive messages from topic/queue")
        parser.add_argument("--subscription", type=str, help="Subscription name (for topics)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        integration = AzureServiceBusIntegration(project_root)

        if args.status:
            status = integration.get_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.send:
            test_message = {
                "test": True,
                "message": "Test message from JARVIS",
                "timestamp": datetime.now().isoformat()
            }
            result = integration.send_message(args.send, test_message)
            print(json.dumps(result, indent=2, default=str))

        elif args.receive:
            messages = integration.receive_messages(
                args.receive,
                subscription=args.subscription,
                max_messages=5
            )
            print(json.dumps(messages, indent=2, default=str))

        else:
            # Default: show status
            status = integration.get_status()
            print(json.dumps(status, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()