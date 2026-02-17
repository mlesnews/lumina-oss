#!/usr/bin/env python3
"""
JARVIS Grammarly CLI API Integration

Full AI-driven JARVIS integration with Grammarly CLI API for data and information processing.

Tags: #GRAMMARLY #CLI_API #INTEGRATION #AI_DRIVEN @JARVIS @LUMINA
"""

import sys
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISGrammarlyCLI")
except ImportError:
    try:
        from lumina_logger import get_logger, setup_logging
        logger = get_logger("JARVISGrammarlyCLI")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISGrammarlyCLI")

# AI Identity and Delegation
try:
    from jarvis_ai_identity_self_awareness import DelegationManager, AgentRole
    DELEGATION_AVAILABLE = True
except ImportError:
    DELEGATION_AVAILABLE = False
    logger.debug("AI Identity/Delegation not available")


class GrammarlyCLIIntegration:
    """Grammarly CLI API integration for JARVIS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "grammarly_cli_config.json"
        self.data_dir = project_root / "data" / "grammarly_integration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()
        self.api_key = self.config.get("api_key")
        self.api_endpoint = self.config.get("api_endpoint", "https://api.grammarly.com")
        self.cli_available = self._check_cli_availability()

        # AI Identity and Delegation
        self.delegation_manager = None
        self.grammarly_agent = None
        if DELEGATION_AVAILABLE:
            try:
                self.delegation_manager = DelegationManager(project_root)
                # Create Grammarly specialist agent
                self.grammarly_agent = self.delegation_manager.create_delegate(
                    agent_name="GrammarlySpecialist",
                    role=AgentRole.SPECIALIST,
                    capabilities=["grammarly_cli", "text_processing", "api_integration"]
                )
            except Exception as e:
                logger.debug(f"Delegation setup failed: {e}")

    def load_config(self) -> Dict[str, Any]:
        """Load Grammarly CLI configuration"""
        default_config = {
            "api_key": None,
            "api_endpoint": "https://api.grammarly.com",
            "enabled": False,
            "auto_check": True,
            "integration_mode": "full"
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                logger.error(f"Error loading Grammarly config: {e}")

        return default_config

    def save_config(self):
        """Save Grammarly CLI configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving Grammarly config: {e}")

    def _check_cli_availability(self) -> bool:
        """Check if Grammarly CLI is available"""
        try:
            result = subprocess.run(
                ["grammarly", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get integration status with AI identity breakdown"""
        status = {
            "enabled": self.config.get("enabled", False),
            "cli_available": self.cli_available,
            "api_key_configured": self.api_key is not None,
            "api_endpoint": self.api_endpoint,
            "integration_mode": self.config.get("integration_mode", "full"),
            "last_checked": datetime.now().isoformat()
        }

        # Add AI identity breakdown if available
        if self.grammarly_agent:
            status["ai_identity"] = {
                "who_am_i": self.grammarly_agent.agent_name,
                "what_im_doing": [
                    {
                        "task_id": t.get("task_id"),
                        "description": t.get("task", {}).get("description", ""),
                        "status": t.get("status")
                    }
                    for t in self.grammarly_agent.current_tasks
                ],
                "breakdown": self.grammarly_agent.get_breakdown()
            }

        # Test API connection if configured
        if self.api_key and self.config.get("enabled"):
            try:
                # Placeholder for actual API test
                status["api_connection"] = "unknown"
                status["api_connection_note"] = "API testing not yet implemented"
            except Exception as e:
                status["api_connection"] = "error"
                status["api_error"] = str(e)
        else:
            status["api_connection"] = "not_configured"

        return status

    def check_text(self, text: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check text using Grammarly CLI API"""
        if not self.cli_available:
            return {
                "success": False,
                "error": "Grammarly CLI not available",
                "suggestion": "Install Grammarly CLI: npm install -g @grammarly/cli"
            }

        if not self.config.get("enabled"):
            return {
                "success": False,
                "error": "Grammarly integration not enabled"
            }

        try:
            # Use Grammarly CLI to check text
            # This is a placeholder - actual implementation would use the CLI
            result = subprocess.run(
                ["grammarly", "check", "--json"],
                input=text,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                try:
                    suggestions = json.loads(result.stdout)
                    return {
                        "success": True,
                        "suggestions": suggestions,
                        "checked_at": datetime.now().isoformat()
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "raw_output": result.stdout,
                        "checked_at": datetime.now().isoformat()
                    }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "returncode": result.returncode
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Grammarly CLI timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def process_file(self, file_path: Path, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a file using Grammarly CLI API"""
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result = self.check_text(content, options)

            if result.get("success"):
                # Save suggestions
                suggestions_file = self.data_dir / f"{file_path.stem}_grammarly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(suggestions_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, default=str)

                result["suggestions_file"] = str(suggestions_file)

            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def integrate_with_jarvis(self, data: Any, information: Any = None) -> Dict[str, Any]:
        """Full AI-driven JARVIS integration - process data and information"""
        logger.info("🔗 Grammarly CLI API integration with JARVIS")

        result = {
            "success": True,
            "processed_at": datetime.now().isoformat(),
            "data_processed": False,
            "information_processed": False
        }

        # Process data (text content)
        if isinstance(data, str):
            check_result = self.check_text(data)
            if check_result.get("success"):
                result["data_processed"] = True
                result["data_suggestions"] = check_result.get("suggestions", [])
            else:
                result["data_error"] = check_result.get("error")

        # Process information (metadata, context)
        if information:
            # Placeholder for information processing
            result["information_processed"] = True
            result["information_note"] = "Information processing not yet implemented"

        return result


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Grammarly CLI API Integration")
        parser.add_argument("--status", action="store_true", help="Show integration status")
        parser.add_argument("--check", type=str, help="Check text")
        parser.add_argument("--file", type=str, help="Check file")
        parser.add_argument("--enable", action="store_true", help="Enable integration")
        parser.add_argument("--disable", action="store_true", help="Disable integration")
        parser.add_argument("--who-am-i", action="store_true", help="Show AI identity breakdown")
        parser.add_argument("--breakdown", action="store_true", help="Show task breakdown")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        integration = GrammarlyCLIIntegration(project_root)

        if args.status:
            status = integration.get_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.who_am_i:
            if integration.grammarly_agent:
                identity = integration.grammarly_agent.get_identity()
                print(json.dumps(identity, indent=2, default=str))
            else:
                print(json.dumps({"error": "AI identity not available"}, indent=2))

        elif args.breakdown:
            if integration.grammarly_agent:
                breakdown = integration.grammarly_agent.get_breakdown()
                print(json.dumps(breakdown, indent=2, default=str))
            else:
                print(json.dumps({"error": "AI identity not available"}, indent=2))

        elif args.check:
            result = integration.check_text(args.check)
            print(json.dumps(result, indent=2, default=str))

        elif args.file:
            file_path = Path(args.file)
            if not file_path.is_absolute():
                file_path = project_root / file_path
            result = integration.process_file(file_path)
            print(json.dumps(result, indent=2, default=str))

        elif args.enable:
            integration.config["enabled"] = True
            integration.save_config()
            print(json.dumps({"success": True, "message": "Integration enabled"}, indent=2))

        elif args.disable:
            integration.config["enabled"] = False
            integration.save_config()
            print(json.dumps({"success": True, "message": "Integration disabled"}, indent=2))

        else:
            # Default: show status
            status = integration.get_status()
            print(json.dumps(status, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()