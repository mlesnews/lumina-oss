#!/usr/bin/env python3
"""
MCPToolkit Health Check and Failover Manager
Implements Option B: NAS Primary, Localhost Fallback

This script monitors MCPToolkit endpoints and automatically fails over
to localhost if NAS becomes unavailable.
"""

import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "homelab_mcp_hybrid_config.json"
STATUS_PATH = PROJECT_ROOT / "data" / "mcp_routing" / "routing_status.json"


class MCPHealthChecker:
    """Health check manager for MCPToolkit endpoints"""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()
        self.status = self._load_status()
        self.timeout = self.config.get("health_checks", {}).get("timeout", 5)
        self.interval = self.config.get("health_checks", {}).get("interval", 30)

    def _load_config(self) -> Dict:
        """Load MCP configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def _load_status(self) -> Dict:
        """Load current routing status"""
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            if STATUS_PATH.exists():
                with open(STATUS_PATH, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load status: {e}")

        # Default status
        return {
            "current_primary": "nas",
            "nas_healthy": True,
            "localhost_healthy": True,
            "last_check": None,
            "failover_count": 0,
            "failover_history": []
        }

    def _save_status(self):
        """Save current routing status"""
        try:
            STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(STATUS_PATH, 'w') as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")

    def check_endpoint(self, url: str) -> Tuple[bool, Optional[str]]:
        """Check health of a single endpoint"""
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return True, None
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except Exception as e:
            return False, str(e)

    def check_nas_health(self) -> bool:
        """Check NAS MCPToolkit health"""
        endpoints = self.config.get("health_checks", {}).get("endpoints", {})
        nas_endpoints = [
            endpoints.get("nas_manus"),
            endpoints.get("nas_n8n"),
            "http://<NAS_PRIMARY_IP>:8080/health"  # MCPToolkit health endpoint
        ]

        # Check at least one NAS endpoint
        for endpoint in nas_endpoints:
            if endpoint:
                healthy, error = self.check_endpoint(endpoint)
                if healthy:
                    logger.debug(f"NAS endpoint {endpoint} is healthy")
                    return True
                else:
                    logger.debug(f"NAS endpoint {endpoint} failed: {error}")

        return False

    def check_localhost_health(self) -> bool:
        """Check localhost MCPToolkit health"""
        endpoints = self.config.get("health_checks", {}).get("endpoints", {})
        localhost_endpoints = [
            endpoints.get("localhost_mcp_toolkit"),
            endpoints.get("localhost_iron_legion"),
            "http://localhost:8080/health"  # MCPToolkit health endpoint
        ]

        # Check at least one localhost endpoint
        for endpoint in localhost_endpoints:
            if endpoint:
                healthy, error = self.check_endpoint(endpoint)
                if healthy:
                    logger.debug(f"Localhost endpoint {endpoint} is healthy")
                    return True
                else:
                    logger.debug(f"Localhost endpoint {endpoint} failed: {error}")

        return False

    def perform_health_check(self) -> Dict:
        """Perform health check on both NAS and localhost"""
        logger.info("Performing health check...")

        nas_healthy = self.check_nas_health()
        localhost_healthy = self.check_localhost_health()

        # Update status
        self.status["nas_healthy"] = nas_healthy
        self.status["localhost_healthy"] = localhost_healthy
        self.status["last_check"] = datetime.now().isoformat()

        # Determine current primary
        if nas_healthy:
            # NAS is healthy, use as primary
            if self.status["current_primary"] != "nas":
                logger.info("✅ NAS recovered, switching back to NAS primary")
                self.status["current_primary"] = "nas"
        elif localhost_healthy:
            # NAS is down, failover to localhost
            if self.status["current_primary"] != "localhost":
                logger.warning("⚠️ NAS unavailable, failing over to localhost")
                self.status["current_primary"] = "localhost"
                self.status["failover_count"] += 1
                self.status["failover_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "from": "nas",
                    "to": "localhost",
                    "reason": "NAS health check failed"
                })
                # Keep only last 10 failover events
                if len(self.status["failover_history"]) > 10:
                    self.status["failover_history"] = self.status["failover_history"][-10:]
        else:
            # Both are down
            logger.error("❌ Both NAS and localhost are unavailable!")
            if self.status["current_primary"] == "nas":
                # Try to failover to localhost anyway (might be transient)
                logger.warning("Attempting failover to localhost despite health check failure")
                self.status["current_primary"] = "localhost"

        self._save_status()

        return {
            "nas_healthy": nas_healthy,
            "localhost_healthy": localhost_healthy,
            "current_primary": self.status["current_primary"],
            "recommendation": self.get_routing_recommendation()
        }

    def get_routing_recommendation(self) -> str:
        """Get current routing recommendation"""
        if self.status["nas_healthy"]:
            return "Use NAS as primary endpoint"
        elif self.status["localhost_healthy"]:
            return "Use localhost as fallback (NAS unavailable)"
        else:
            return "Both endpoints unavailable - manual intervention required"

    def run_continuous_monitoring(self):
        """Run continuous health monitoring"""
        logger.info("Starting continuous MCPToolkit health monitoring...")
        logger.info(f"Check interval: {self.interval} seconds")
        logger.info(f"Timeout: {self.timeout} seconds")

        try:
            while True:
                result = self.perform_health_check()
                logger.info(
                    f"Status - NAS: {'✅' if result['nas_healthy'] else '❌'}, "
                    f"Localhost: {'✅' if result['localhost_healthy'] else '❌'}, "
                    f"Primary: {result['current_primary']}"
                )
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}", exc_info=True)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="MCPToolkit Health Check and Failover Manager")
        parser.add_argument(
            "action",
            choices=["check", "monitor", "status"],
            help="Action to perform"
        )
        parser.add_argument(
            "--config",
            type=Path,
            default=CONFIG_PATH,
            help="Path to MCP configuration file"
        )

        args = parser.parse_args()

        checker = MCPHealthChecker(config_path=args.config)

        if args.action == "check":
            result = checker.perform_health_check()
            print(json.dumps(result, indent=2))
        elif args.action == "monitor":
            checker.run_continuous_monitoring()
        elif args.action == "status":
            print(json.dumps(checker.status, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()