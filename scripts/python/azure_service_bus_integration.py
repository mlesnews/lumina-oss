#!/usr/bin/env python3
"""
Azure Service Bus Integration for Lumina | JARVIS Extension
All async communication must use Azure Service Bus
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum

try:
    from azure.servicebus import ServiceBusClient
    from azure.servicebus import ServiceBusMessage as AzureServiceBusMessage
    from azure.servicebus.exceptions import ServiceBusError
    from azure.identity import DefaultAzureCredential
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False
    AzureServiceBusMessage = None
    logging.warning("Azure Service Bus SDK not installed. Install with: pip install azure-servicebus azure-identity")

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    logging.warning("Azure Key Vault SDK not installed. Install with: pip install azure-keyvault-secrets azure-identity")

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AzureServiceBus")
else:
    logger = get_logger("AzureServiceBus")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class MessageType(Enum):
    """Message types for Service Bus"""
    WORKFLOW = "workflow"
    ESCALATION = "escalation"
    INTELLIGENCE = "intelligence"
    RESPONSE = "response"
    VERIFICATION = "verification"
    KNOWLEDGE = "knowledge"
    COORDINATION = "coordination"


@dataclass
class ServiceBusMessage:
    """Service Bus message structure"""
    message_id: str
    message_type: MessageType
    timestamp: datetime
    source: str
    destination: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_azure_message(self) -> 'AzureServiceBusMessage':
        try:
            """Convert to Azure Service Bus message"""
            if not SERVICE_BUS_AVAILABLE or AzureServiceBusMessage is None:
                raise ImportError("Azure Service Bus SDK not installed")

            body = {
                "message_id": self.message_id,
                "message_type": self.message_type.value,
                "timestamp": self.timestamp.isoformat(),
                "source": self.source,
                "destination": self.destination,
                "payload": self.payload,
                "correlation_id": self.correlation_id,
                "reply_to": self.reply_to,
                "metadata": self.metadata
            }

            message = AzureServiceBusMessage(
                body=json.dumps(body).encode('utf-8'),
                message_id=self.message_id,
                correlation_id=self.correlation_id,
                subject=self.message_type.value
            )

            if self.reply_to:
                message.reply_to = self.reply_to

            return message
        except Exception as e:
            self.logger.error(f"Error in to_azure_message: {e}", exc_info=True)
            raise
class AzureServiceBusClient:
    """
    Azure Service Bus client for async communication

    All components must use this for async message communication
    """

    def __init__(
        self,
        namespace: str,
        credential: Optional[Any] = None,
        key_vault_client: Optional['AzureKeyVaultClient'] = None
    ):
        """
        Initialize Service Bus client

        Args:
            namespace: Service Bus namespace (e.g., "jarvis-lumina-bus.servicebus.windows.net")
            credential: Azure credential (defaults to DefaultAzureCredential)
            key_vault_client: Optional Key Vault client for retrieving connection string
        """
        if not SERVICE_BUS_AVAILABLE:
            raise ImportError("Azure Service Bus SDK not installed")

        self.namespace = namespace
        self.credential = credential or DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                )

        # Get connection string from Key Vault if available
        if key_vault_client:
            try:
                connection_string = key_vault_client.get_secret("service-bus-connection-string")
                self.client = ServiceBusClient.from_connection_string(connection_string)
            except Exception as e:
                logger.warning(f"Failed to get connection string from Key Vault: {e}")
                # Fallback to namespace + credential
                self.client = ServiceBusClient(fully_qualified_namespace=namespace, credential=self.credential)
        else:
            self.client = ServiceBusClient(fully_qualified_namespace=namespace, credential=self.credential)

        logger.info(f"Azure Service Bus client initialized: {namespace}")

    async def publish_to_topic_async(
        self,
        topic_name: str,
        message: ServiceBusMessage,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Publish message to Service Bus topic (async)

        Args:
            topic_name: Name of the topic
            message: ServiceBusMessage to publish
            session_id: Optional session ID for ordered delivery

        Returns:
            True if published successfully
        """
        try:
            sb_message = message.to_azure_message()
            if session_id:
                sb_message.session_id = session_id

            async with self.client:
                sender = self.client.get_topic_sender(topic_name=topic_name)
                await sender.send_messages(sb_message)

            logger.info(f"Published message {message.message_id} to topic {topic_name}")
            return True

        except ServiceBusError as e:
            logger.error(f"Failed to publish message to topic {topic_name}: {e}")
            return False

    async def send_to_queue_async(
        self,
        queue_name: str,
        message: ServiceBusMessage,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Send message to Service Bus queue (async)

        Args:
            queue_name: Name of the queue
            message: ServiceBusMessage to send
            session_id: Optional session ID for ordered delivery

        Returns:
            True if sent successfully
        """
        try:
            sb_message = message.to_azure_message()
            if session_id:
                sb_message.session_id = session_id

            async with self.client:
                sender = self.client.get_queue_sender(queue_name=queue_name)
                await sender.send_messages(sb_message)

            logger.info(f"Sent message {message.message_id} to queue {queue_name}")
            return True

        except ServiceBusError as e:
            logger.error(f"Failed to send message to queue {queue_name}: {e}")
            return False

    async def subscribe_to_topic_async(
        self,
        topic_name: str,
        subscription_name: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
        max_wait_time: int = 5
    ):
        """
        Subscribe to Service Bus topic (async)

        Args:
            topic_name: Name of the topic
            subscription_name: Name of the subscription
            handler: Async function to handle received messages
            max_wait_time: Maximum wait time for messages (seconds)
        """
        try:
            async with self.client:
                receiver = self.client.get_subscription_receiver(
                    topic_name=topic_name,
                    subscription_name=subscription_name
                )

                async with receiver:
                    received_messages = await receiver.receive_messages(max_wait_time=max_wait_time)

                    for msg in received_messages:
                        try:
                            body = json.loads(str(msg))
                            await handler(body)
                            await receiver.complete_message(msg)
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            await receiver.dead_letter_message(msg)

        except ServiceBusError as e:
            logger.error(f"Error subscribing to topic {topic_name}: {e}")

    async def receive_from_queue_async(
        self,
        queue_name: str,
        handler: Callable[[Dict[str, Any]], Awaitable[None]],
        max_wait_time: int = 5
    ):
        """
        Receive messages from Service Bus queue (async)

        Args:
            queue_name: Name of the queue
            handler: Async function to handle received messages
            max_wait_time: Maximum wait time for messages (seconds)
        """
        try:
            async with self.client:
                receiver = self.client.get_queue_receiver(queue_name=queue_name)

                async with receiver:
                    received_messages = await receiver.receive_messages(max_wait_time=max_wait_time)

                    for msg in received_messages:
                        try:
                            body = json.loads(str(msg))
                            await handler(body)
                            await receiver.complete_message(msg)
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            await receiver.dead_letter_message(msg)

        except ServiceBusError as e:
            logger.error(f"Error receiving from queue {queue_name}: {e}")

    def publish_to_topic(
        self,
        topic_name: str,
        message: ServiceBusMessage,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Publish message to Service Bus topic

        Args:
            topic_name: Name of the topic
            message: ServiceBusMessage to publish
            session_id: Optional session ID for ordered delivery

        Returns:
            True if published successfully
        """
        try:
            sb_message = message.to_azure_message()
            if session_id:
                sb_message.session_id = session_id

            with self.client:
                sender = self.client.get_topic_sender(topic_name=topic_name)
                sender.send_messages(sb_message)

            logger.info(f"Published message {message.message_id} to topic {topic_name}")
            return True

        except ServiceBusError as e:
            logger.error(f"Failed to publish message to topic {topic_name}: {e}")
            return False

    def send_to_queue(
        self,
        queue_name: str,
        message: ServiceBusMessage,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Send message to Service Bus queue

        Args:
            queue_name: Name of the queue
            message: ServiceBusMessage to send
            session_id: Optional session ID for ordered delivery

        Returns:
            True if sent successfully
        """
        try:
            sb_message = message.to_azure_message()
            if session_id:
                sb_message.session_id = session_id

            with self.client:
                sender = self.client.get_queue_sender(queue_name=queue_name)
                sender.send_messages(sb_message)

            logger.info(f"Sent message {message.message_id} to queue {queue_name}")
            return True

        except ServiceBusError as e:
            logger.error(f"Failed to send message to queue {queue_name}: {e}")
            return False

    def subscribe_to_topic(
        self,
        topic_name: str,
        subscription_name: str,
        handler: Callable[[Dict[str, Any]], None],
        max_wait_time: int = 5
    ):
        """
        Subscribe to Service Bus topic

        Args:
            topic_name: Name of the topic
            subscription_name: Name of the subscription
            handler: Function to handle received messages
            max_wait_time: Maximum wait time for messages (seconds)
        """
        try:
            with self.client:
                receiver = self.client.get_subscription_receiver(
                    topic_name=topic_name,
                    subscription_name=subscription_name
                )

                with receiver:
                    received_messages = receiver.receive_messages(max_wait_time=max_wait_time)

                    for msg in received_messages:
                        try:
                            body = json.loads(str(msg))
                            handler(body)
                            receiver.complete_message(msg)
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            receiver.dead_letter_message(msg)

        except ServiceBusError as e:
            logger.error(f"Error subscribing to topic {topic_name}: {e}")

    def receive_from_queue(
        self,
        queue_name: str,
        handler: Callable[[Dict[str, Any]], None],
        max_wait_time: int = 5
    ):
        """
        Receive messages from Service Bus queue

        Args:
            queue_name: Name of the queue
            handler: Function to handle received messages
            max_wait_time: Maximum wait time for messages (seconds)
        """
        try:
            with self.client:
                receiver = self.client.get_queue_receiver(queue_name=queue_name)

                with receiver:
                    received_messages = receiver.receive_messages(max_wait_time=max_wait_time)

                    for msg in received_messages:
                        try:
                            body = json.loads(str(msg))
                            handler(body)
                            receiver.complete_message(msg)
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            receiver.dead_letter_message(msg)

        except ServiceBusError as e:
            logger.error(f"Error receiving from queue {queue_name}: {e}")


class AzureKeyVaultClient:
    """
    Azure Key Vault client for secrets management

    ALL company secrets MUST be stored in Azure Key Vault
    """

    def __init__(
        self,
        vault_url: str,
        credential: Optional[Any] = None
    ):
        """
        Initialize Key Vault client

        Args:
            vault_url: Key Vault URL (e.g., "https://jarvis-lumina.vault.azure.net/")
            credential: Azure credential (defaults to DefaultAzureCredential)
        """
        if not KEY_VAULT_AVAILABLE:
            raise ImportError("Azure Key Vault SDK not installed")

        self.vault_url = vault_url
        self.credential = credential or DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                )
        self.client = SecretClient(vault_url=vault_url, credential=self.credential)

        logger.info(f"Azure Key Vault client initialized: {vault_url}")

    def get_secret(self, secret_name: str, version: Optional[str] = None) -> str:
        """
        Get secret from Key Vault

        Args:
            secret_name: Name of the secret
            version: Optional version of the secret (defaults to latest)

        Returns:
            Secret value
        """
        try:
            if version:
                secret = self.client.get_secret(secret_name, version=version)
            else:
                secret = self.client.get_secret(secret_name)

            logger.debug(f"Retrieved secret: {secret_name}")
            return secret.value

        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise

    def set_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Set secret in Key Vault

        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret

        Returns:
            True if set successfully
        """
        try:
            self.client.set_secret(secret_name, secret_value)
            logger.info(f"Set secret: {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to set secret {secret_name}: {e}")
            return False

    def list_secrets(self) -> list:
        """List all secrets in Key Vault"""
        try:
            secrets = []
            for secret_properties in self.client.list_properties_of_secrets():
                secrets.append(secret_properties.name)
            return secrets
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []


def get_service_bus_client(
    namespace: Optional[str] = None,
    key_vault_client: Optional[AzureKeyVaultClient] = None
) -> AzureServiceBusClient:
    """
    Get Service Bus client (retrieves namespace from Key Vault if needed)

    Args:
        namespace: Service Bus namespace (or retrieved from Key Vault)
        key_vault_client: Key Vault client for retrieving connection string

    Returns:
        AzureServiceBusClient instance
    """
    if not namespace and key_vault_client:
        namespace = key_vault_client.get_secret("service-bus-namespace")

    if not namespace:
        raise ValueError("Service Bus namespace required")

    return AzureServiceBusClient(namespace, key_vault_client=key_vault_client)


def get_key_vault_client(vault_url: Optional[str] = None) -> AzureKeyVaultClient:
    """
    Get Key Vault client

    Args:
        vault_url: Key Vault URL (or retrieved from environment/config)

    Returns:
        AzureKeyVaultClient instance
    """
    if not vault_url:
        # Try to get from environment or config
        import os
        vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

    return AzureKeyVaultClient(vault_url)


if __name__ == "__main__":
    # Example usage
    print("Azure Service Bus and Key Vault Integration")
    print("=" * 60)

    # Initialize Key Vault client
    try:
        kv_client = get_key_vault_client()
        print(f"[SUCCESS] Key Vault client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Key Vault: {e}")

    # Initialize Service Bus client
    try:
        sb_client = get_service_bus_client(key_vault_client=kv_client)
        print(f"[SUCCESS] Service Bus client initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Service Bus: {e}")
