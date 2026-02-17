#!/usr/bin/env python3
"""
JARVIS Cursor Agent Integration

Integrates Cursor Agent API with JARVIS and ElevenLabs:
- Agent management
- Voice integration
- Workflow coordination
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorAgentIntegration")


class JARVISCursorAgentIntegration:
    """
    Cursor Agent API integration
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.api_key = self._get_api_key()
        self.api_base = "https://api.cursor.com"

    def _get_api_key(self) -> Optional[str]:
        """Get Cursor Agent API key"""
        # Try environment variable first
        api_key = os.getenv("CURSOR_AGENT_API_KEY")
        if api_key:
            return api_key

        # Try config file
        config_file = self.project_root / "config" / "cursor_agent" / "cursor_agent_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get("cursor_agent_api_key")
                    if api_key:
                        return api_key
            except Exception as e:
                self.logger.error(f"Error reading config file: {e}")

        # Try Azure Key Vault
        try:
            from azure_service_bus_integration import get_key_vault_client
            vault_client = get_key_vault_client()
            api_key = vault_client.get_secret("cursor-agent-api-key")
            if api_key:
                return api_key
        except Exception as e:
            self.logger.debug(f"Key Vault not available: {e}")

        return None

    def test_connection(self) -> Dict[str, Any]:
        """Test Cursor Agent API connection"""
        if not self.api_key:
            return {
                "success": False,
                "error": "API key not configured"
            }

        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Test endpoint (adjust based on actual API)
            response = requests.get(
                f"{self.api_base}/agents",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Connection successful",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "response": response.text
                }

        except ImportError:
            return {
                "success": False,
                "error": "requests library not installed - install: pip install requests"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def integrate_with_elevenlabs(self) -> Dict[str, Any]:
        """Integrate Cursor Agent with ElevenLabs"""
        try:
            from jarvis_elevenlabs_integration import JARVISElevenLabsTTS

            # Initialize ElevenLabs TTS
            tts = JARVISElevenLabsTTS(project_root=self.project_root)

            if not tts.api_key:
                return {
                    "success": False,
                    "error": "ElevenLabs API key not configured"
                }

            # Test TTS
            test_message = "Cursor Agent integration with ElevenLabs is active."
            tts.speak(test_message)

            return {
                "success": True,
                "message": "ElevenLabs integration active",
                "tts_available": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor Agent Integration")
        parser.add_argument("--test", action="store_true", help="Test API connection")
        parser.add_argument("--elevenlabs", action="store_true", help="Test ElevenLabs integration")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        integration = JARVISCursorAgentIntegration(project_root)

        if args.test or not args:
            result = integration.test_connection()
            if result.get("success"):
                print("✅ Cursor Agent API connection successful")
            else:
                print(f"❌ Connection failed: {result.get('error', 'Unknown error')}")

        if args.elevenlabs:
            result = integration.integrate_with_elevenlabs()
            if result.get("success"):
                print("✅ ElevenLabs integration active")
            else:
                print(f"❌ Integration failed: {result.get('error', 'Unknown error')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()