#!/usr/bin/env python3
"""
JARVIS Unified API

Central API for all JARVIS systems to communicate, coordinate, and share resources.
Provides a unified interface for all JARVIS capabilities.

MCU JARVIS Capability: Unified system communication and coordination.

@JARVIS @UNIFIED_API @MCU_FEATURE @INTEGRATION
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import threading
import time
from collections import defaultdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISUnifiedAPI")


class APIVersion(Enum):
    """API Version"""
    V1 = "v1"
    V2 = "v2"


class RequestType(Enum):
    """Request types"""
    QUERY = "query"
    COMMAND = "command"
    STATUS = "status"
    NOTIFICATION = "notification"
    DATA = "data"
    COORDINATION = "coordination"


@dataclass
class APIRequest:
    """API Request"""
    request_id: str
    request_type: RequestType
    source: str
    target: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 5  # 1-10, higher is more urgent

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['request_type'] = self.request_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class APIResponse:
    """API Response"""
    request_id: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


# Import AI Actions
try:
    from jarvis_synology_ai_actions import JARVISSynologyAIActions
    SYNOLOGY_AI_AVAILABLE = True
except ImportError:
    SYNOLOGY_AI_AVAILABLE = False

try:
    from jarvis_unified_ai_actions import JARVISUnifiedAIActions
    UNIFIED_AI_AVAILABLE = True
except ImportError:
    UNIFIED_AI_AVAILABLE = False

class JARVISUnifiedAPI:
    """
    JARVIS Unified API

    Central API for all JARVIS systems to communicate and coordinate.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Unified API"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISUnifiedAPI")

        # API Registry - registered JARVIS systems
        self.registered_systems: Dict[str, Dict[str, Any]] = {}

        # Request queue
        self.request_queue: List[APIRequest] = []
        self.request_lock = threading.Lock()

        # Response cache
        self.response_cache: Dict[str, APIResponse] = {}
        self.cache_ttl = timedelta(minutes=5)

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Request history
        self.request_history: List[APIRequest] = []
        self.max_history = 1000

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis" / "api"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load state
        self._load_state()

        # Start request processor
        self.processing_active = False
        self.processor_thread: Optional[threading.Thread] = None

        # Initialize AI Actions if available
        self.synology_ai: Optional[JARVISSynologyAIActions] = None
        self.unified_ai: Optional[JARVISUnifiedAIActions] = None

        if SYNOLOGY_AI_AVAILABLE:
            try:
                self.synology_ai = JARVISSynologyAIActions()
                self.register_system(
                    system_id="jarvis_synology_ai",
                    system_name="JARVIS Synology AI Actions",
                    capabilities=["task_scheduling", "system_info", "storage_info", "package_management"],
                    endpoint="synology_ai"
                )
                self.logger.info("✅ Synology AI Actions registered")
            except Exception as e:
                self.logger.warning(f"⚠️  Synology AI Actions not available: {e}")

        if UNIFIED_AI_AVAILABLE:
            try:
                self.unified_ai = JARVISUnifiedAIActions()
                self.register_system(
                    system_id="jarvis_unified_ai",
                    system_name="JARVIS Unified AI Actions",
                    capabilities=["llm_routing", "ai_coordination", "model_management", "health_monitoring"],
                    endpoint="unified_ai"
                )
                self.logger.info("✅ Unified AI Actions registered")
            except Exception as e:
                self.logger.warning(f"⚠️  Unified AI Actions not available: {e}")

        # Register Grammarly Desktop CLI API
        try:
            from jarvis_grammarly_desktop_integration import JARVISGrammarlyDesktopBridge
            self.grammarly_bridge = JARVISGrammarlyDesktopBridge()
            self.register_system(
                system_id="jarvis_grammarly_desktop",
                system_name="JARVIS Grammarly Desktop Integration",
                capabilities=["grammar_checking", "text_correction", "auto_improvement", "jarvis_output_enhancement"],
                endpoint="grammarly_desktop"
            )
            self.logger.info("✅ Grammarly Desktop CLI API registered")
        except Exception as e:
            self.logger.warning(f"⚠️  Grammarly Desktop integration not available: {e}")
            self.grammarly_bridge = None

        self.logger.info("🌐 JARVIS Unified API initialized")
        self.logger.info(f"   Registered systems: {len(self.registered_systems)}")

    def register_system(self, system_id: str, system_name: str, 
                       capabilities: List[str], endpoint: Optional[str] = None):
        """
        Register a JARVIS system with the API

        Args:
            system_id: Unique system identifier
            system_name: Human-readable system name
            capabilities: List of capabilities this system provides
            endpoint: Optional endpoint URL or path
        """
        self.registered_systems[system_id] = {
            "system_id": system_id,
            "system_name": system_name,
            "capabilities": capabilities,
            "endpoint": endpoint,
            "registered_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "status": "active"
        }

        self.logger.info(f"📝 Registered system: {system_name} ({system_id})")
        self._save_state()

    def unregister_system(self, system_id: str):
        """Unregister a JARVIS system"""
        if system_id in self.registered_systems:
            system_name = self.registered_systems[system_id]["system_name"]
            del self.registered_systems[system_id]
            self.logger.info(f"🗑️ Unregistered system: {system_name} ({system_id})")
            self._save_state()

    def send_request(self, request_type: RequestType, source: str,
                    target: Optional[str] = None, payload: Dict[str, Any] = None,
                    priority: int = 5) -> str:
        """
        Send an API request

        Returns:
            Request ID
        """
        request_id = f"req_{int(datetime.now().timestamp())}_{len(self.request_queue)}"

        request = APIRequest(
            request_id=request_id,
            request_type=request_type,
            source=source,
            target=target,
            payload=payload or {},
            priority=priority
        )

        with self.request_lock:
            # Insert by priority (higher priority first)
            inserted = False
            for i, existing_req in enumerate(self.request_queue):
                if existing_req.priority < priority:
                    self.request_queue.insert(i, request)
                    inserted = True
                    break

            if not inserted:
                self.request_queue.append(request)

        self.logger.debug(f"📤 Request queued: {request_type.value} from {source} to {target or 'broadcast'}")

        return request_id

    def get_response(self, request_id: str, timeout: float = 30.0) -> Optional[APIResponse]:
        """
        Get response for a request

        Args:
            request_id: Request ID
            timeout: Timeout in seconds

        Returns:
            APIResponse or None if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if request_id in self.response_cache:
                response = self.response_cache[request_id]
                # Check if cache is still valid
                age = datetime.now() - response.timestamp
                if age < self.cache_ttl:
                    return response
                else:
                    # Cache expired
                    del self.response_cache[request_id]

            time.sleep(0.1)

        return None

    def process_request(self, request: APIRequest) -> APIResponse:
        """
        Process an API request

        This routes the request to the appropriate system handler
        """
        try:
            # Update target system activity
            if request.target and request.target in self.registered_systems:
                self.registered_systems[request.target]["last_activity"] = datetime.now().isoformat()

            # Route based on request type
            if request.request_type == RequestType.QUERY:
                return self._handle_query(request)
            elif request.request_type == RequestType.COMMAND:
                return self._handle_command(request)
            elif request.request_type == RequestType.STATUS:
                return self._handle_status(request)
            elif request.request_type == RequestType.NOTIFICATION:
                return self._handle_notification(request)
            elif request.request_type == RequestType.DATA:
                return self._handle_data(request)
            elif request.request_type == RequestType.COORDINATION:
                return self._handle_coordination(request)
            else:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Unknown request type: {request.request_type}"
                )

        except Exception as e:
            self.logger.error(f"Error processing request {request.request_id}: {e}", exc_info=True)
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )

    def _handle_query(self, request: APIRequest) -> APIResponse:
        """Handle query request"""
        query = request.payload.get("query", "")
        target = request.target

        # If target specified, route to that system
        if target and target in self.registered_systems:
            # Would call actual system handler here
            return APIResponse(
                request_id=request.request_id,
                success=True,
                data={"result": f"Query processed by {target}", "query": query}
            )

        # Broadcast query to all systems
        results = {}
        for system_id, system_info in self.registered_systems.items():
            if "query" in system_info.get("capabilities", []):
                results[system_id] = f"Response from {system_info['system_name']}"

        return APIResponse(
            request_id=request.request_id,
            success=True,
            data={"results": results}
        )

    def _handle_command(self, request: APIRequest) -> APIResponse:
        """Handle command request"""
        command = request.payload.get("command", "")
        target = request.target

        # Handle AI Actions commands
        if target == "synology_ai" or target == "jarvis_synology_ai":
            if self.synology_ai:
                action = request.payload.get("action", "")
                kwargs = request.payload.get("kwargs", {})
                try:
                    result = self.synology_ai.execute_action(action, **kwargs)
                    return APIResponse(
                        request_id=request.request_id,
                        success=result.get("success", False),
                        data=result,
                        error=result.get("error")
                    )
                except Exception as e:
                    self.logger.error(f"Error executing Synology AI action: {e}")
                    return APIResponse(
                        request_id=request.request_id,
                        success=False,
                        error=str(e)
                    )
            else:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="Synology AI Actions not available"
                )

        # Handle Unified AI commands
        if target == "unified_ai" or target == "jarvis_unified_ai":
            if self.unified_ai:
                action = request.payload.get("action", "")
                kwargs = request.payload.get("kwargs", {})
                try:
                    result = self.unified_ai.execute_action(action, **kwargs)
                    return APIResponse(
                        request_id=request.request_id,
                        success=result.get("success", False),
                        data=result,
                        error=result.get("error")
                    )
                except Exception as e:
                    self.logger.error(f"Error executing Unified AI action: {e}")
                    return APIResponse(
                        request_id=request.request_id,
                        success=False,
                        error=str(e)
                    )
            else:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="Unified AI Actions not available"
                )

        # Handle Vacuum Control commands
        if target == "vacuum" or target == "jarvis_vacuum_control":
            try:
                from jarvis_vacuum_integration import JARVISVacuumIntegration
                # Get or create vacuum integration instance
                if not hasattr(self, '_vacuum_integration'):
                    self._vacuum_integration = JARVISVacuumIntegration(project_root=self.project_root)

                # Process request through vacuum integration
                response = self._vacuum_integration.process_api_request(request)
                if response:
                    return response
                else:
                    return APIResponse(
                        request_id=request.request_id,
                        success=False,
                        error="Vacuum integration did not process request"
                    )
            except ImportError:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="Vacuum integration not available"
                )
            except Exception as e:
                self.logger.error(f"Error executing vacuum command: {e}")
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error=str(e)
                )

        # Handle Grammarly Desktop commands
        if target == "grammarly_desktop" or target == "jarvis_grammarly_desktop":
            if self.grammarly_bridge:
                action = request.payload.get("action", "check_text")
                text = request.payload.get("text", "")

                try:
                    if action == "check_text":
                        result = self.grammarly_bridge.integration.check_text(text)
                    elif action == "check_jarvis_output":
                        result = self.grammarly_bridge.check_jarvis_output(text)
                    elif action == "check_user_input":
                        result = self.grammarly_bridge.check_user_input(text)
                    elif action == "improve_jarvis_response":
                        result_text = self.grammarly_bridge.improve_jarvis_response(text)
                        result = {"success": True, "original": text, "improved": result_text}
                    elif action == "get_status":
                        result = self.grammarly_bridge.get_integration_status()
                    else:
                        result = {"success": False, "error": f"Unknown action: {action}"}

                    return APIResponse(
                        request_id=request.request_id,
                        success=result.get("success", True),
                        data=result,
                        error=result.get("error")
                    )
                except Exception as e:
                    self.logger.error(f"Error executing Grammarly action: {e}")
                    return APIResponse(
                        request_id=request.request_id,
                        success=False,
                        error=str(e)
                    )
            else:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="Grammarly Desktop integration not available"
                )

        if target and target in self.registered_systems:
            # Would execute command on target system
            return APIResponse(
                request_id=request.request_id,
                success=True,
                data={"result": f"Command executed on {target}", "command": command}
            )

        return APIResponse(
            request_id=request.request_id,
            success=False,
            error="Command requires target system"
        )

    def _handle_status(self, request: APIRequest) -> APIResponse:
        """Handle status request"""
        target = request.target

        if target:
            # Get status of specific system
            if target in self.registered_systems:
                system_info = self.registered_systems[target]
                return APIResponse(
                    request_id=request.request_id,
                    success=True,
                    data={"status": system_info}
                )
            else:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"System not found: {target}"
                )

        # Return status of all systems
        return APIResponse(
            request_id=request.request_id,
            success=True,
            data={"systems": list(self.registered_systems.values())}
        )

    def _handle_notification(self, request: APIRequest) -> APIResponse:
        """Handle notification request"""
        notification = request.payload.get("notification", {})

        # Broadcast notification to all systems
        notified = []
        for system_id in self.registered_systems.keys():
            # Would send notification to system
            notified.append(system_id)

        return APIResponse(
            request_id=request.request_id,
            success=True,
            data={"notified": notified, "notification": notification}
        )

    def _handle_data(self, request: APIRequest) -> APIResponse:
        """Handle data request"""
        action = request.payload.get("action", "get")  # get, set, update, delete
        data_key = request.payload.get("key", "")
        data_value = request.payload.get("value")

        # Would implement actual data storage/retrieval
        return APIResponse(
            request_id=request.request_id,
            success=True,
            data={"action": action, "key": data_key, "value": data_value}
        )

    def _handle_coordination(self, request: APIRequest) -> APIResponse:
        """Handle coordination request"""
        coordination_type = request.payload.get("type", "sync")

        # Would coordinate between systems
        return APIResponse(
            request_id=request.request_id,
            success=True,
            data={"coordination": coordination_type, "status": "coordinated"}
        )

    def start_processing(self):
        """Start request processing thread"""
        if self.processing_active:
            return

        self.processing_active = True
        self.processor_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processor_thread.start()
        self.logger.info("🔄 Request processing started")

    def stop_processing(self):
        """Stop request processing"""
        self.processing_active = False
        if self.processor_thread:
            self.processor_thread.join(timeout=5)
        self.logger.info("🛑 Request processing stopped")

    def _processing_loop(self):
        """Request processing loop"""
        while self.processing_active:
            try:
                with self.request_lock:
                    if not self.request_queue:
                        time.sleep(0.1)
                        continue

                    request = self.request_queue.pop(0)

                # Process request
                response = self.process_request(request)

                # Cache response
                self.response_cache[request.request_id] = response

                # Add to history
                self.request_history.append(request)
                if len(self.request_history) > self.max_history:
                    self.request_history = self.request_history[-self.max_history:]

                # Trigger event handlers
                event_key = f"{request.request_type.value}_{request.target or 'broadcast'}"
                for handler in self.event_handlers.get(event_key, []):
                    try:
                        handler(request, response)
                    except Exception as e:
                        self.logger.error(f"Event handler error: {e}")

            except Exception as e:
                self.logger.error(f"Processing loop error: {e}")
                time.sleep(1)

    def register_event_handler(self, event_pattern: str, handler: Callable):
        """
        Register an event handler

        Args:
            event_pattern: Event pattern (e.g., "query_broadcast", "command_jarvis_core")
            handler: Handler function(request, response)
        """
        self.event_handlers[event_pattern].append(handler)
        self.logger.debug(f"📋 Registered event handler: {event_pattern}")

    def get_api_status(self) -> Dict[str, Any]:
        """Get API status report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "registered_systems": len(self.registered_systems),
            "queued_requests": len(self.request_queue),
            "cached_responses": len(self.response_cache),
            "request_history_size": len(self.request_history),
            "processing_active": self.processing_active,
            "systems": list(self.registered_systems.keys())
        }

    def _save_state(self):
        """Save API state"""
        try:
            state_file = self.data_dir / "api_state.json"
            state = {
                "registered_systems": self.registered_systems,
                "last_updated": datetime.now().isoformat()
            }

            # Atomic write
            temp_file = state_file.parent / f".{state_file.name}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            if state_file.exists():
                state_file.unlink()
            temp_file.replace(state_file)

        except Exception as e:
            self.logger.error(f"Error saving API state: {e}")

    def _load_state(self):
        """Load API state"""
        try:
            state_file = self.data_dir / "api_state.json"
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.registered_systems = state.get("registered_systems", {})
                    self.logger.info(f"   Loaded {len(self.registered_systems)} registered systems")
        except Exception as e:
            self.logger.error(f"Error loading API state: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Unified API")
    parser.add_argument("--status", action="store_true", help="Get API status")
    parser.add_argument("--register", nargs=3, metavar=("ID", "NAME", "CAPABILITIES"), 
                       help="Register a system (capabilities comma-separated)")
    parser.add_argument("--start", action="store_true", help="Start request processing")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    api = JARVISUnifiedAPI()

    if args.status:
        status = api.get_api_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🌐 JARVIS Unified API Status")
            print("="*60)
            print(f"Registered Systems: {status['registered_systems']}")
            print(f"Queued Requests: {status['queued_requests']}")
            print(f"Cached Responses: {status['cached_responses']}")
            print(f"Processing Active: {status['processing_active']}")

    elif args.register:
        system_id, system_name, capabilities_str = args.register
        capabilities = [c.strip() for c in capabilities_str.split(",")]
        api.register_system(system_id, system_name, capabilities)
        print(f"✅ Registered: {system_name} ({system_id})")

    elif args.start:
        print("\n🌐 Starting JARVIS Unified API...")
        api.start_processing()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            api.stop_processing()

    else:
        parser.print_help()


if __name__ == "__main__":


    main()