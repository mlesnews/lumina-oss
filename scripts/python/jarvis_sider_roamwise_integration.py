#!/usr/bin/env python3
"""
JARVIS Sider.AI and ROAMWISE.AI Integration

Full JARVIS control over Sider.AI (WiseBase) and ROAMWISE.AI (Web Portal/Gateway).
Integrates with JARVIS Desktop Full Control for complete AI <=> AI bidirectional communication.

Tags: #JARVIS #SIDER #ROAMWISE #WISEBASE #INTEGRATION #AI_TO_AI @JARVIS @LUMINA
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

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

logger = get_logger("JARVISSiderRoamwiseIntegration")


class JARVISSiderAIIntegration:
    """
    JARVIS Integration with Sider.AI (WiseBase features)

    Primary importance - provides WiseBase functionality
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Sider.AI integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.sider_config = self.config_dir / "sider_ai_config.json"
        self.sider_endpoint = None
        self.wisebase_available = False

        self._load_config()
        self._discover_sider()

        logger.info("✅ JARVIS Sider.AI Integration initialized")
        logger.info("   ⭐ PRIMARY IMPORTANCE - WiseBase features")

    def _load_config(self):
        """Load Sider.AI configuration"""
        default_config = {
            "endpoints": [
                "http://localhost:3000",
                "http://localhost:8080",
                "http://127.0.0.1:3000"
            ],
            "wisebase_enabled": True,
            "api_key": None
        }

        if self.sider_config.exists():
            try:
                with open(self.sider_config, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                pass

        with open(self.sider_config, 'w') as f:
            json.dump(default_config, f, indent=2)

    def _discover_sider(self):
        """Discover Sider.AI installation"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if 'sider' in proc.info['name'].lower():
                        logger.info(f"   ✅ Sider.AI process found: {proc.info['name']}")
                        self.wisebase_available = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check API endpoints
        with open(self.sider_config, 'r') as f:
            config = json.load(f)

        for endpoint in config.get("endpoints", []):
            try:
                response = requests.get(f"{endpoint}/health", timeout=2)
                if response.status_code == 200:
                    self.sider_endpoint = endpoint
                    self.wisebase_available = True
                    logger.info(f"   ✅ Sider.AI API found: {endpoint}")
                    break
            except Exception:
                pass

    def wisebase_query(self, query: str) -> Dict[str, Any]:
        """Query WiseBase via Sider.AI"""
        if not self.wisebase_available:
            return {"error": "Sider.AI WiseBase not available"}

        try:
            if self.sider_endpoint:
                response = requests.post(
                    f"{self.sider_endpoint}/api/wisebase/query",
                    json={"query": query},
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.debug(f"   WiseBase query error: {e}")

        return {"error": "WiseBase query failed"}


class JARVISRoamwiseAIIntegration:
    """
    JARVIS Integration with ROAMWISE.AI

    Web frontend portal/gateway (.local network only)
    Half: Sider.AI (WiseBase)
    Half: RoamResearch (Lifetime Account - Personal)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ROAMWISE.AI integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"

        self.roamwise_endpoint = "http://roamwise.ai"  # Discovered as reachable
        self.available = False
        self.sider_component = False
        self.roamresearch_component = False

        self._discover_roamwise()

        logger.info("✅ JARVIS ROAMWISE.AI Integration initialized")
        logger.info("   🌐 Web Portal/Gateway (.local network only)")

    def _discover_roamwise(self):
        """Discover ROAMWISE.AI"""
        try:
            response = requests.get(self.roamwise_endpoint, timeout=5)
            if response.status_code < 500:
                self.available = True
                logger.info(f"   ✅ ROAMWISE.AI reachable: {self.roamwise_endpoint}")

                # Check for Sider.AI component
                if "sider" in response.text.lower() or "wisebase" in response.text.lower():
                    self.sider_component = True
                    logger.info("   ✅ Sider.AI component detected")

                # Check for RoamResearch component
                if "roam" in response.text.lower() or "roamresearch" in response.text.lower():
                    self.roamresearch_component = True
                    logger.info("   ✅ RoamResearch component detected")
        except Exception as e:
            logger.debug(f"   ROAMWISE.AI discovery error: {e}")

    def send_to_roamwise(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send action to ROAMWISE.AI"""
        if not self.available:
            return {"error": "ROAMWISE.AI not available"}

        try:
            response = requests.post(
                f"{self.roamwise_endpoint}/api/action",
                json={"action": action, "data": data},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"   ROAMWISE.AI action error: {e}")

        return {"error": "ROAMWISE.AI action failed"}


class JARVISRoamResearchIntegration:
    """
    JARVIS Integration with RoamResearch

    Lifetime Account - Personal
    Part of ROAMWISE.AI (other half)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize RoamResearch integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"

        self.roamresearch_config = self.config_dir / "roamresearch_config.json"
        self.lifetime_account = False
        self.api_key = None

        self._load_config()

        logger.info("✅ JARVIS RoamResearch Integration initialized")
        logger.info("   📚 Lifetime Account - Personal")

    def _load_config(self):
        """Load RoamResearch configuration"""
        default_config = {
            "lifetime_account": False,
            "api_key": None,
            "graph_name": "Personal",
            "endpoint": "https://roamresearch.com"
        }

        if self.roamresearch_config.exists():
            try:
                with open(self.roamresearch_config, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                pass

        self.lifetime_account = default_config.get("lifetime_account", False)
        self.api_key = default_config.get("api_key")

        if self.lifetime_account:
            logger.info("   ✅ RoamResearch Lifetime Account configured")

        # Save config
        with open(self.roamresearch_config, 'w') as f:
            json.dump(default_config, f, indent=2)

    def query_graph(self, query: str) -> Dict[str, Any]:
        """Query RoamResearch knowledge graph"""
        if not self.lifetime_account:
            return {"error": "RoamResearch Lifetime Account not configured"}

        # RoamResearch API integration would go here
        return {"error": "RoamResearch API integration not yet implemented"}


def main():
    try:
        """Test integrations"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Sider.AI and ROAMWISE.AI Integration")
        parser.add_argument("--test-sider", action="store_true", help="Test Sider.AI")
        parser.add_argument("--test-roamwise", action="store_true", help="Test ROAMWISE.AI")
        parser.add_argument("--test-roamresearch", action="store_true", help="Test RoamResearch")

        args = parser.parse_args()

        if args.test_sider:
            sider = JARVISSiderAIIntegration()
            result = sider.wisebase_query("test query")
            print(json.dumps(result, indent=2))

        if args.test_roamwise:
            roamwise = JARVISRoamwiseAIIntegration()
            result = roamwise.send_to_roamwise("test", {})
            print(json.dumps(result, indent=2))

        if args.test_roamresearch:
            roamresearch = JARVISRoamResearchIntegration()
            print(f"Lifetime Account: {roamresearch.lifetime_account}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()