#!/usr/bin/env python3
"""
JARVIS Vacuum Integration with Unified API

Integrates vacuum control with JARVIS unified API for remote administration
and coordination with other JARVIS systems.

Tags: #JARVIS #VACUUM #INTEGRATION #API @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_unified_api import JARVISUnifiedAPI, RequestType, APIRequest, APIResponse
    from jarvis_vacuum_control import JARVISVacuumControl, CleaningMode
    UNIFIED_API_AVAILABLE = True
except ImportError as e:
    UNIFIED_API_AVAILABLE = False
    logger = get_logger("JARVISVacuumIntegration")
    logger.warning(f"⚠️  Integration modules not available: {e}")

logger = get_logger("JARVISVacuumIntegration")


class JARVISVacuumIntegration:
    """
    JARVIS Vacuum Integration

    Integrates vacuum control with JARVIS unified API
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.vacuum_control = JARVISVacuumControl(project_root=project_root)

        if UNIFIED_API_AVAILABLE:
            self.unified_api = JARVISUnifiedAPI(project_root=project_root)
            self._register_handlers()
        else:
            self.unified_api = None
            logger.warning("⚠️  Unified API not available - integration limited")

        logger.info("🔗 JARVIS Vacuum Integration initialized")

    def _register_handlers(self):
        """Register API handlers with unified API"""
        if not self.unified_api:
            return

        # Register vacuum system with unified API
        self.unified_api.register_system(
            system_id="jarvis_vacuum_control",
            system_name="JARVIS Vacuum Control System",
            capabilities=[
                "vacuum_discovery",
                "vacuum_status",
                "vacuum_control",
                "cleaning_scheduling",
                "remote_administration"
            ],
            endpoint="vacuum"
        )

        # Store reference for request processing
        # The unified API will route requests to this system via target="jarvis_vacuum_control"
        # We'll process them in the handler methods
        self._api_handlers = {
            "discover": self._handle_discover,
            "status": self._handle_status,
            "start": self._handle_start,
            "stop": self._handle_stop,
            "dock": self._handle_dock
        }

        logger.info("✅ Registered vacuum API handlers")

    def process_api_request(self, request: APIRequest) -> Optional[APIResponse]:
        """
        Process API request for vacuum system

        Called by unified API when request target is "jarvis_vacuum_control"
        """
        if not request.target or request.target != "jarvis_vacuum_control":
            return None

        action = request.payload.get("action", "")
        handler = self._api_handlers.get(action)

        if handler:
            return handler(request)
        else:
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=f"Unknown action: {action}"
            )

    def _handle_discover(self, request: APIRequest) -> APIResponse:
        """Handle discover request"""
        try:
            devices = self.vacuum_control.discover_and_register()
            return APIResponse(
                request_id=request.request_id,
                success=True,
                data={
                    "devices_found": len(devices),
                    "devices": [device.to_dict() for device in devices]
                }
            )
        except Exception as e:
            logger.error(f"❌ Discover failed: {e}", exc_info=True)
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )

    def _handle_status(self, request: APIRequest) -> APIResponse:
        """Handle status request"""
        try:
            device_id = request.payload.get("device_id")
            if not device_id:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="device_id is required"
                )

            status = self.vacuum_control.get_status(device_id)
            return APIResponse(
                request_id=request.request_id,
                success=True,
                data=status
            )
        except Exception as e:
            logger.error(f"❌ Status request failed: {e}", exc_info=True)
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )

    def _handle_start(self, request: APIRequest) -> APIResponse:
        """Handle start cleaning request"""
        try:
            device_id = request.payload.get("device_id")
            if not device_id:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="device_id is required"
                )

            mode_str = request.payload.get("mode", "standard")
            try:
                mode = CleaningMode(mode_str)
            except ValueError:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error=f"Invalid mode: {mode_str}. Valid modes: {[m.value for m in CleaningMode]}"
                )

            result = self.vacuum_control.start_cleaning(device_id, mode)
            return APIResponse(
                request_id=request.request_id,
                success=result.get("success", False),
                data=result
            )
        except Exception as e:
            logger.error(f"❌ Start cleaning failed: {e}", exc_info=True)
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )

    def _handle_stop(self, request: APIRequest) -> APIResponse:
        """Handle stop cleaning request"""
        try:
            device_id = request.payload.get("device_id")
            if not device_id:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="device_id is required"
                )

            result = self.vacuum_control.stop_cleaning(device_id)
            return APIResponse(
                request_id=request.request_id,
                success=result.get("success", False),
                data=result
            )
        except Exception as e:
            logger.error(f"❌ Stop cleaning failed: {e}", exc_info=True)
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )

    def _handle_dock(self, request: APIRequest) -> APIResponse:
        """Handle return to dock request"""
        try:
            device_id = request.payload.get("device_id")
            if not device_id:
                return APIResponse(
                    request_id=request.request_id,
                    success=False,
                    error="device_id is required"
                )

            result = self.vacuum_control.return_to_dock(device_id)
            return APIResponse(
                request_id=request.request_id,
                success=result.get("success", False),
                data=result
            )
        except Exception as e:
            logger.error(f"❌ Return to dock failed: {e}", exc_info=True)
            return APIResponse(
                request_id=request.request_id,
                success=False,
                error=str(e)
            )


def main():
    """CLI entry point"""
    integration = JARVISVacuumIntegration()
    logger.info("✅ JARVIS Vacuum Integration ready")
    logger.info("   Use JARVIS unified API to control vacuums remotely")


if __name__ == "__main__":


    main()