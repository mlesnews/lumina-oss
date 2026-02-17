#!/usr/bin/env python3
"""
Service Bus Backward Compatibility Layer
Provides file-based interface for systems still using file-based communication

This layer subscribes to Service Bus topics/queues and writes messages to files
for backward compatibility with systems that haven't migrated yet.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import threading
import time

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

logger = get_logger("ServiceBusBackwardCompatibility")

try:
    from azure_service_bus_integration import (
        AzureServiceBusClient,
        get_service_bus_client,
        get_key_vault_client
    )
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False
    logger.error("Azure Service Bus integration not available")


class ServiceBusBackwardCompatibility:
    """
    Backward compatibility layer that bridges Service Bus to file-based communication

    Subscribes to Service Bus topics/queues and writes messages to files
    for systems that still expect file-based communication.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.jarvis_intelligence_dir = self.project_root / "data" / "jarvis_intelligence"
        self.jarvis_intelligence_dir.mkdir(parents=True, exist_ok=True)

        self.running = False
        self.threads = []

        # Initialize Service Bus client
        if SERVICE_BUS_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                self.sb_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=kv_client
                )
                logger.info("Service Bus backward compatibility layer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Service Bus client: {e}")
                self.sb_client = None
        else:
            self.sb_client = None

    def handle_escalation_message(self, message_body: Dict[str, Any]):
        """Handle escalation message from Service Bus and write to file"""
        try:
            payload = message_body.get("payload", {})
            message_id = message_body.get("message_id", payload.get("message_id", f"escalation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"))

            # Write to file for backward compatibility
            message_file = self.jarvis_intelligence_dir / f"{message_id}.json"
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "message_id": message_id,
                    "source": "service_bus",
                    "timestamp": datetime.now().isoformat(),
                    **payload
                }, f, indent=2, ensure_ascii=False)

            logger.debug(f"Wrote escalation message to file: {message_file.name}")

        except Exception as e:
            logger.error(f"Error handling escalation message: {e}")

    def handle_intelligence_message(self, message_body: Dict[str, Any]):
        """Handle intelligence message from Service Bus and write to file"""
        try:
            payload = message_body.get("payload", {})
            message_id = message_body.get("message_id", payload.get("id", f"intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}"))

            # Write to file for backward compatibility
            message_file = self.jarvis_intelligence_dir / f"{message_id}.json"
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "message_id": message_id,
                    "source": "service_bus",
                    "timestamp": datetime.now().isoformat(),
                    **payload
                }, f, indent=2, ensure_ascii=False)

            logger.debug(f"Wrote intelligence message to file: {message_file.name}")

        except Exception as e:
            logger.error(f"Error handling intelligence message: {e}")

    def start_escalation_listener(self):
        """Start listening to escalation queue and writing to files"""
        if not self.sb_client:
            return

        def listen():
            while self.running:
                try:
                    self.sb_client.receive_from_queue(
                        queue_name="jarvis-escalation-queue",
                        handler=self.handle_escalation_message,
                        max_wait_time=5
                    )
                except Exception as e:
                    logger.error(f"Error in escalation listener: {e}")
                    time.sleep(5)

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        self.threads.append(thread)
        logger.info("Started escalation listener")

    def start_intelligence_listener(self):
        """Start listening to intelligence topic and writing to files"""
        if not self.sb_client:
            return

        def listen():
            while self.running:
                try:
                    self.sb_client.subscribe_to_topic(
                        topic_name="jarvis.intelligence",
                        subscription_name="intelligence-feed",
                        handler=self.handle_intelligence_message,
                        max_wait_time=5
                    )
                except Exception as e:
                    logger.error(f"Error in intelligence listener: {e}")
                    time.sleep(5)

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        self.threads.append(thread)
        logger.info("Started intelligence listener")

    def start(self):
        """Start all backward compatibility listeners"""
        if not self.sb_client:
            logger.error("Service Bus client not available")
            return

        self.running = True
        self.start_escalation_listener()
        self.start_intelligence_listener()
        logger.info("Backward compatibility layer started")

    def stop(self):
        """Stop all backward compatibility listeners"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=5)
        logger.info("Backward compatibility layer stopped")


def main():
    """Run backward compatibility layer"""
    project_root = Path(__file__).parent.parent.parent
    compatibility = ServiceBusBackwardCompatibility(project_root)

    try:
        compatibility.start()
        print("Backward compatibility layer running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping backward compatibility layer...")
        compatibility.stop()


if __name__ == "__main__":


    main()