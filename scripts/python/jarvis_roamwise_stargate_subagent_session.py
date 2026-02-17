#!/usr/bin/env python3
"""
JARVIS RoamWise.ai Stargate Portal Subagent Session
Create and manage agent chat session for RoamWise.ai web portal/gateway
Inspired by "Stargate" - the gateway to knowledge

@JARVIS @ROAMWISE @STARGATE @PORTAL @GATEWAY @SUBAGENT @SESSION
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRoamWiseStargate")


class RoamWiseStargateSubagentSession:
    """
    RoamWise.ai Stargate Portal Subagent Session Manager

    Creates and manages agent chat sessions for RoamWise.ai web portal/gateway,
    inspired by "Stargate" - the gateway to knowledge and exploration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize RoamWise Stargate subagent session manager"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Session directory
        self.session_dir = self.project_root / "data" / "agent_chat_sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Subagent directory
        self.subagent_dir = self.project_root / "data" / "subagent_spawner" / "active_agents"
        self.subagent_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ RoamWise Stargate Subagent Session Manager initialized")
        logger.info("   'Chevron encoded!' - Gateway to knowledge")

    def check_existing_session(self) -> Optional[Dict[str, Any]]:
        """Check if a RoamWise Stargate subagent session already exists"""
        logger.info("🔍 Checking for existing RoamWise Stargate subagent session...")

        # Check agent chat sessions
        sessions = sorted(self.session_dir.glob("session_*.json"))
        sessions.extend(sorted(self.session_dir.glob("*roamwise*stargate*.json")))

        for session_file in reversed(sessions):  # Check most recent first
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                # Check if this is a RoamWise Stargate session
                metadata = session_data.get("metadata", {})
                issues = session_data.get("issues_tracked", [])
                session_id = session_data.get("session_id", "")

                is_roamwise_stargate = (
                    "roamwise" in str(session_data).lower() and "stargate" in str(session_data).lower()
                ) or (
                    any("roamwise" in str(issue).lower() and "stargate" in str(issue).lower() for issue in issues)
                ) or (
                    metadata.get("workflow_type") == "roamwise_stargate" or
                    metadata.get("portal_type") == "stargate" or
                    "roamwise" in session_id.lower() and "stargate" in session_id.lower()
                )

                if is_roamwise_stargate:
                    logger.info(f"  ✓ Found existing session: {session_file.name}")
                    return {
                        "exists": True,
                        "session_file": str(session_file),
                        "session_data": session_data
                    }
            except Exception as e:
                logger.warning(f"  ⚠️  Error reading {session_file.name}: {e}")

        logger.info("  ✗ No existing RoamWise Stargate subagent session found")
        return None

    def create_subagent_session(self, workflow_name: str = "roamwise_stargate_portal") -> Dict[str, Any]:
        """Create a new agent chat session for RoamWise.ai Stargate portal"""
        logger.info("=" * 70)
        logger.info("🚪 CREATING ROAMWISE STARGATE SUBAGENT SESSION")
        logger.info("   'Chevron encoded!' - Gateway to knowledge")
        logger.info("=" * 70)
        logger.info("")

        session_id = f"roamwise_stargate_subagent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session_data = {
            "session_id": session_id,
            "inception_time": datetime.now().isoformat(),
            "workflow_type": "roamwise_stargate_portal",
            "portal_type": "stargate_gateway",
            "portal_url": "<LOCAL_HOSTNAME>",
            "agents_involved": [
                "JARVIS",
                "ROAMWISE_STARGATE_SUBAGENT",
                "STARGATE_GATEWAY",
                "KNOWLEDGE_NAVIGATOR",
                "R5",
                "WOW_ATLAS"
            ],
            "messages": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "agent": "JARVIS",
                    "message": f"RoamWise.ai Stargate portal subagent workflow session created: {workflow_name}",
                    "type": "system"
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "agent": "STARGATE_GATEWAY",
                    "message": "Chevron encoded! Gateway to knowledge activated.",
                    "type": "system"
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "agent": "JARVIS",
                    "message": "Stargate portal initialized for RoamWise.ai web gateway",
                    "type": "system"
                }
            ],
            "issues_tracked": [
                f"RoamWise.ai Stargate Portal: {workflow_name}",
                "Stargate gateway coordination",
                "Knowledge navigation",
                "Portal/gateway development",
                "Web portal integration"
            ],
            "resolutions": [],
            "archived": False,
            "archive_time": None,
            "metadata": {
                "workflow_type": "roamwise_stargate_portal",
                "portal_type": "stargate_gateway",
                "workflow_name": workflow_name,
                "portal_url": "<LOCAL_HOSTNAME>",
                "inspiration": "Stargate (movie/TV series)",
                "gateway_concept": "Gateway to knowledge and exploration",
                "features": [
                    "RoamWise.ai Web Portal",
                    "Stargate Gateway Interface",
                    "Knowledge Graph Navigation",
                    "RoamResearch Integration",
                    "SiderAI Wisebase Integration",
                    "Wow Atlas Oracle Integration",
                    "Jedi Archives Integration",
                    "Holocron System",
                    "Marketing Frontend",
                    "Customer Portal"
                ],
                "stargate_references": [
                    "Chevron encoding",
                    "Gate activation",
                    "Wormhole travel (knowledge navigation)",
                    "Address system (knowledge paths)",
                    "Dial Home Device (DHD) - search/navigation"
                ],
                "integrations": [
                    "Lumina Core",
                    "R5 Living Context Matrix",
                    "Wow Atlas Oracle",
                    "Jedi Archives",
                    "Holocron System"
                ],
                "tags": [
                    "@roamwise",
                    "@stargate",
                    "@portal",
                    "@gateway",
                    "@subagent",
                    "@lumina",
                    "@premium"
                ]
            }
        }

        # Save session
        session_file = self.session_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, default=str)

        logger.info(f"Session ID: {session_id}")
        logger.info(f"Workflow: {workflow_name}")
        logger.info(f"Portal URL: {session_data['portal_url']}")
        logger.info(f"Agents: {', '.join(session_data['agents_involved'])}")
        logger.info(f"Session file: {session_file}")
        logger.info("")

        # Create subagent entry
        subagent_entry = {
            "agent_id": f"roamwise_stargate_subagent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "agent_type": "roamwise_stargate_subagent",
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "workflow": workflow_name,
            "portal_url": "<LOCAL_HOSTNAME>",
            "capabilities": [
                "stargate_gateway_management",
                "knowledge_navigation",
                "roamwise_integration",
                "portal_development",
                "gateway_coordination"
            ],
            "stargate_references": session_data["metadata"]["stargate_references"],
            "metadata": session_data["metadata"]
        }

        subagent_file = self.subagent_dir / f"{subagent_entry['agent_id']}.json"
        with open(subagent_file, 'w', encoding='utf-8') as f:
            json.dump(subagent_entry, f, indent=2, default=str)

        logger.info(f"Subagent entry: {subagent_file}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ ROAMWISE STARGATE SUBAGENT SESSION CREATED")
        logger.info("   'Chevron encoded!' - Gateway activated")
        logger.info("=" * 70)

        return {
            "success": True,
            "session_id": session_id,
            "session_file": str(session_file),
            "subagent_file": str(subagent_file),
            "session_data": session_data,
            "subagent_entry": subagent_entry
        }

    def ensure_session_exists(self) -> Dict[str, Any]:
        """Ensure a RoamWise Stargate subagent session exists, create if needed"""
        logger.info("=" * 70)
        logger.info("🔍 ENSURING ROAMWISE STARGATE SUBAGENT SESSION EXISTS")
        logger.info("=" * 70)
        logger.info("")

        # Check for existing session
        existing = self.check_existing_session()

        if existing:
            logger.info("✅ Existing session found - no need to create new one")
            logger.info(f"   Session: {existing['session_file']}")
            logger.info("")
            logger.info("=" * 70)
            logger.info("✅ SESSION VERIFIED")
            logger.info("=" * 70)

            return {
                "success": True,
                "action": "existing_session_found",
                "session_file": existing["session_file"],
                "session_data": existing["session_data"]
            }
        else:
            logger.info("⚠️  No existing session found - creating new one")
            logger.info("")
            return self.create_subagent_session()


def main():
    """Main execution"""
    print("=" * 70)
    print("🚪 ROAMWISE STARGATE SUBAGENT SESSION MANAGER")
    print("   'Chevron encoded!' - Gateway to knowledge")
    print("=" * 70)
    print()

    manager = RoamWiseStargateSubagentSession()
    result = manager.ensure_session_exists()

    print()
    print("=" * 70)
    print("✅ SESSION STATUS")
    print("=" * 70)
    print(f"Action: {result.get('action', 'created')}")
    print(f"Session ID: {result.get('session_id', 'N/A')}")
    print(f"Portal URL: {result.get('session_data', {}).get('portal_url', '<LOCAL_HOSTNAME>')}")
    print(f"Session File: {result.get('session_file', 'N/A')}")
    print("=" * 70)
    print()
    print("🚪 Stargate Gateway Status: ACTIVE")
    print("   'Chevron encoded!' - Ready for knowledge navigation")
    print("=" * 70)


if __name__ == "__main__":


    main()