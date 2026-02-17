#!/usr/bin/env python3
"""
JARVIS DEFCON Streetlight Poller - NAS KronScheduler Event

Listens for Azure Service Bus confirmation that PC is fully live and online with all LUMINA startup sequences,
then starts persistent live polling of DEFCON streetlight system.

Polling frequency balanced for ecosystem utilization:
- High frequency when active events detected
- Normal frequency (hourly) during normal operations
- Adaptive based on system load

Tags: #DEFCON #STREETLIGHT #NAS #KRONSCHEDULER #AZBUS #POLLING #LIVE @JARVIS @LUMINA @WOPR
"""

import sys
import json
import time
import threading
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISDEFCONPOLLER")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISDEFCONPOLLER")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISDEFCONPOLLER")

# Import Azure Service Bus
try:
    from jarvis_azure_service_bus_integration import AzureServiceBusIntegration
    AZBUS_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.jarvis_azure_service_bus_integration import AzureServiceBusIntegration
        AZBUS_AVAILABLE = True
    except ImportError:
        AZBUS_AVAILABLE = False
        logger.warning("Azure Service Bus integration not available")

# Import DEFCON Streetlight
try:
    from jarvis_defcon_streetlight import DEFCONStreetlight, DEFCONLevel, SensorType
    DEFCON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.jarvis_defcon_streetlight import DEFCONStreetlight, DEFCONLevel, SensorType
        DEFCON_AVAILABLE = True
    except ImportError:
        DEFCON_AVAILABLE = False
        logger.error("DEFCON Streetlight system not available")


class DEFCONStreetlightPoller:
    """DEFCON Streetlight Poller - NAS KronScheduler Event"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "defcon_streetlight_poller"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.data_dir / "poller_state.json"
        self.polling_log_file = self.data_dir / "polling_log.jsonl"

        # Initialize Azure Service Bus
        if AZBUS_AVAILABLE:
            try:
                self.azbus = AzureServiceBusIntegration(project_root)
                logger.info("✅ Azure Service Bus integration initialized")
            except Exception as e:
                logger.warning(f"Azure Service Bus initialization failed: {e}")
                self.azbus = None
        else:
            self.azbus = None

        # Initialize DEFCON Streetlight
        if DEFCON_AVAILABLE:
            try:
                self.streetlight = DEFCONStreetlight(project_root)
                logger.info("✅ DEFCON Streetlight system initialized")
            except Exception as e:
                logger.error(f"DEFCON Streetlight initialization failed: {e}")
                self.streetlight = None
        else:
            self.streetlight = None

        # Polling state
        self.polling_active = False
        self.startup_confirmed = False
        self.confirmation_received_at = None
        self.polling_thread = None
        self.listener_thread = None

        # Resource balancing
        self.base_poll_interval_seconds = 3600  # 1 hour base interval
        self.active_event_poll_interval_seconds = 300  # 5 minutes when active events
        self.max_cpu_percent = 80.0  # Don't poll if CPU > 80%
        self.max_memory_percent = 85.0  # Don't poll if memory > 85%

        # Load state
        self._load_state()

    def _load_state(self):
        """Load polling state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.startup_confirmed = state.get("startup_confirmed", False)
                    self.confirmation_received_at = state.get("confirmation_received_at")
                    self.polling_active = state.get("polling_active", False)
            except Exception as e:
                logger.error(f"Error loading state: {e}")

    def _save_state(self):
        """Save polling state"""
        state = {
            "startup_confirmed": self.startup_confirmed,
            "confirmation_received_at": self.confirmation_received_at,
            "polling_active": self.polling_active,
            "updated_at": datetime.now().isoformat()
        }
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def _log_polling_event(self, event_type: str, data: Dict[str, Any]):
        """Log polling event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        try:
            with open(self.polling_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error logging polling event: {e}")

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources for balancing"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "can_poll": cpu_percent < self.max_cpu_percent and memory_percent < self.max_memory_percent,
                "reason": None if (cpu_percent < self.max_cpu_percent and memory_percent < self.max_memory_percent) else (
                    f"CPU: {cpu_percent:.1f}% > {self.max_cpu_percent}%" if cpu_percent >= self.max_cpu_percent
                    else f"Memory: {memory_percent:.1f}% > {self.max_memory_percent}%"
                )
            }
        except Exception as e:
            logger.warning(f"Error checking system resources: {e}")
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "can_poll": True,  # Default to allowing poll if check fails
                "reason": None
            }

    def _calculate_poll_interval(self) -> int:
        """Calculate adaptive poll interval based on system state"""
        # Check if there are active events
        if self.streetlight:
            active_events_count = len(self.streetlight.active_events)
            if active_events_count > 0:
                # Active events detected - poll more frequently
                return self.active_event_poll_interval_seconds

        # Normal operations - use base interval
        return self.base_poll_interval_seconds

    def _perform_poll(self) -> Dict[str, Any]:
        """Perform a single polling cycle"""
        if not self.streetlight:
            return {
                "success": False,
                "error": "DEFCON Streetlight system not available"
            }

        # Check system resources
        resources = self._check_system_resources()
        if not resources["can_poll"]:
            logger.warning(f"⏸️  Polling skipped due to resource constraints: {resources['reason']}")
            self._log_polling_event("poll_skipped_resource", resources)
            return {
                "success": False,
                "skipped": True,
                "reason": resources["reason"],
                "resources": resources
            }

        # Perform hourly sweep
        try:
            sweep_result = self.streetlight.perform_hourly_sweep()

            self._log_polling_event("poll_completed", {
                "defcon_before": sweep_result.get("defcon_before"),
                "defcon_after": sweep_result.get("defcon_after"),
                "new_intelligence": sweep_result.get("new_intelligence_total"),
                "updates": sweep_result.get("updates_total"),
                "duplicates_skipped": sweep_result.get("duplicates_skipped_total"),
                "resources": resources
            })

            logger.info(f"🔍 Poll completed: DEFCON {sweep_result.get('defcon_before')} → {sweep_result.get('defcon_after')}")

            return {
                "success": True,
                "sweep_result": sweep_result,
                "resources": resources
            }
        except Exception as e:
            logger.error(f"Error performing poll: {e}")
            self._log_polling_event("poll_error", {"error": str(e)})
            return {
                "success": False,
                "error": str(e)
            }

    def _polling_loop(self):
        """Main polling loop - runs continuously after startup confirmation"""
        logger.info("=" * 80)
        logger.info("🔍 DEFCON STREETLIGHT POLLING LOOP STARTED")
        logger.info("=" * 80)

        while self.polling_active and self.startup_confirmed:
            try:
                # Calculate adaptive interval
                poll_interval = self._calculate_poll_interval()

                logger.info(f"⏰ Next poll in {poll_interval} seconds ({poll_interval / 60:.1f} minutes)")

                # Perform poll
                poll_result = self._perform_poll()

                if poll_result.get("success"):
                    logger.info("✅ Poll completed successfully")
                elif poll_result.get("skipped"):
                    logger.info(f"⏭️  Poll skipped: {poll_result.get('reason')}")
                else:
                    logger.warning(f"⚠️  Poll failed: {poll_result.get('error')}")

                # Wait for next poll interval
                time.sleep(poll_interval)

            except KeyboardInterrupt:
                logger.info("🛑 Polling loop interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                # Wait before retrying
                time.sleep(60)

        logger.info("=" * 80)
        logger.info("🔍 DEFCON STREETLIGHT POLLING LOOP STOPPED")
        logger.info("=" * 80)

    def _listen_for_startup_confirmation(self):
        """Listen for Azure Service Bus startup confirmation message"""
        logger.info("=" * 80)
        logger.info("👂 LISTENING FOR AZURE SERVICE BUS STARTUP CONFIRMATION")
        logger.info("=" * 80)

        if not self.azbus or not self.azbus.client:
            logger.warning("⚠️  Azure Service Bus not available - will start polling immediately")
            self._confirm_startup()
            return

        # Queue/topic names for startup confirmation
        confirmation_queue = "lumina_startup_confirmation"
        confirmation_topic = "system_events"
        confirmation_subscription = "defcon_poller"

        while not self.startup_confirmed:
            try:
                # Try to receive from queue first
                messages = self.azbus.receive_messages(
                    confirmation_queue,
                    max_messages=1,
                    handler=self._handle_startup_confirmation_message
                )

                # If no messages from queue, try topic subscription
                if not messages:
                    messages = self.azbus.receive_messages(
                        confirmation_topic,
                        subscription=confirmation_subscription,
                        max_messages=1,
                        handler=self._handle_startup_confirmation_message
                    )

                # Check if confirmation received
                if self.startup_confirmed:
                    break

                # Wait before next check
                time.sleep(5)  # Check every 5 seconds

            except KeyboardInterrupt:
                logger.info("🛑 Listener interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error listening for confirmation: {e}")
                time.sleep(10)  # Wait longer on error

        if self.startup_confirmed:
            logger.info("=" * 80)
            logger.info("✅ STARTUP CONFIRMATION RECEIVED - STARTING POLLING")
            logger.info("=" * 80)
            self._start_polling()
        else:
            logger.warning("⚠️  Startup confirmation not received - polling not started")

    def _handle_startup_confirmation_message(self, message_data: Dict[str, Any]) -> bool:
        """Handle startup confirmation message from Azure Service Bus"""
        try:
            body = message_data.get("body", {})
            properties = message_data.get("properties", {})

            # Check if this is a startup confirmation message
            event_type = properties.get("event_type") or body.get("event_type")
            message_type = properties.get("message_type") or body.get("message_type")

            # Look for confirmation indicators
            is_confirmation = (
                event_type == "startup_complete" or
                event_type == "lumina_online" or
                event_type == "system_ready" or
                message_type == "startup_confirmation" or
                "fully live" in str(body).lower() or
                "startup sequences" in str(body).lower() or
                "online" in str(body).lower()
            )

            if is_confirmation:
                logger.info("=" * 80)
                logger.info("📨 STARTUP CONFIRMATION MESSAGE RECEIVED")
                logger.info("=" * 80)
                logger.info(f"Event Type: {event_type}")
                logger.info(f"Message Type: {message_type}")
                logger.info(f"Body: {json.dumps(body, indent=2, default=str)}")
                logger.info("=" * 80)

                self._confirm_startup()
                return True  # Message processed successfully

            return False  # Not a confirmation message
        except Exception as e:
            logger.error(f"Error handling confirmation message: {e}")
            return False

    def _confirm_startup(self):
        """Confirm startup and start polling"""
        self.startup_confirmed = True
        self.confirmation_received_at = datetime.now().isoformat()
        self._save_state()

        logger.info("=" * 80)
        logger.info("✅ STARTUP CONFIRMED - READY TO START POLLING")
        logger.info("=" * 80)
        logger.info(f"Confirmation received at: {self.confirmation_received_at}")
        logger.info("=" * 80)

    def _start_polling(self):
        """Start the polling loop"""
        if not self.startup_confirmed:
            logger.warning("⚠️  Cannot start polling - startup not confirmed")
            return

        if self.polling_active:
            logger.warning("⚠️  Polling already active")
            return

        self.polling_active = True
        self._save_state()

        # Start polling thread
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()

        logger.info("✅ Polling thread started")

    def start(self, wait_for_confirmation: bool = True):
        """Start the poller - listen for confirmation then start polling"""
        if wait_for_confirmation and not self.startup_confirmed:
            # Start listener thread
            self.listener_thread = threading.Thread(target=self._listen_for_startup_confirmation, daemon=True)
            self.listener_thread.start()
            logger.info("✅ Listener thread started - waiting for startup confirmation")
        else:
            # Start immediately
            if not self.startup_confirmed:
                self._confirm_startup()
            self._start_polling()
            logger.info("✅ Polling started immediately")

    def stop(self):
        """Stop the poller"""
        self.polling_active = False
        self._save_state()
        logger.info("🛑 Poller stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get poller status"""
        status = {
            "startup_confirmed": self.startup_confirmed,
            "confirmation_received_at": self.confirmation_received_at,
            "polling_active": self.polling_active,
            "polling_thread_alive": self.polling_thread.is_alive() if self.polling_thread else False,
            "listener_thread_alive": self.listener_thread.is_alive() if self.listener_thread else False,
            "azbus_available": self.azbus is not None and self.azbus.client is not None,
            "streetlight_available": self.streetlight is not None,
            "current_defcon": self.streetlight.current_defcon.value if self.streetlight else None,
            "active_events": len(self.streetlight.active_events) if self.streetlight else 0,
            "poll_interval": self._calculate_poll_interval(),
            "resources": self._check_system_resources(),
            "updated_at": datetime.now().isoformat()
        }

        return status


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS DEFCON Streetlight Poller - NAS KronScheduler Event")
    parser.add_argument("--start", action="store_true", help="Start poller (wait for confirmation)")
    parser.add_argument("--start-immediate", action="store_true", help="Start poller immediately (skip confirmation)")
    parser.add_argument("--stop", action="store_true", help="Stop poller")
    parser.add_argument("--status", action="store_true", help="Get poller status")
    parser.add_argument("--poll-now", action="store_true", help="Perform immediate poll (one-time)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    poller = DEFCONStreetlightPoller(project_root)

    if args.start:
        poller.start(wait_for_confirmation=True)
        # Keep running
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping poller...")
            poller.stop()

    elif args.start_immediate:
        poller.start(wait_for_confirmation=False)
        # Keep running
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping poller...")
            poller.stop()

    elif args.stop:
        poller.stop()
        print("✅ Poller stopped")

    elif args.poll_now:
        result = poller._perform_poll()
        print("=" * 80)
        print("🔍 IMMEDIATE POLL RESULT")
        print("=" * 80)
        print(json.dumps(result, indent=2, default=str))

    elif args.status:
        status = poller.get_status()
        print("=" * 80)
        print("📊 DEFCON STREETLIGHT POLLER STATUS")
        print("=" * 80)
        print(f"Startup Confirmed: {status['startup_confirmed']}")
        print(f"Polling Active: {status['polling_active']}")
        print(f"Current DEFCON: {status['current_defcon']}")
        print(f"Active Events: {status['active_events']}")
        print(f"Poll Interval: {status['poll_interval']} seconds ({status['poll_interval'] / 60:.1f} minutes)")
        print(f"CPU: {status['resources']['cpu_percent']:.1f}%")
        print(f"Memory: {status['resources']['memory_percent']:.1f}%")
        print(f"Can Poll: {status['resources']['can_poll']}")
        print("=" * 80)
        print(json.dumps(status, indent=2, default=str))

    else:
        # Default: show status
        status = poller.get_status()
        print("=" * 80)
        print("📊 DEFCON STREETLIGHT POLLER")
        print("=" * 80)
        print(f"Startup Confirmed: {status['startup_confirmed']}")
        print(f"Polling Active: {status['polling_active']}")
        print(f"Current DEFCON: {status['current_defcon']}")
        print("=" * 80)


if __name__ == "__main__":


    main()