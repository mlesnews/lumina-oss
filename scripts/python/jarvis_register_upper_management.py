#!/usr/bin/env python3
"""
JARVIS Register Upper Management - MACE, TONY, GANDALF

Registers MACE, TONY, and GANDALF as upper management and Jedi Council members
(both normal and high councils).

Tags: #JARVIS #UPPERMANAGEMENT #JEDICOUNCIL #JEDIHIGHCOUNCIL #MACE #TONY #GANDALF @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRegisterUpperManagement")

try:
    from jarvis_peak_agent_management import JARVISPeakAgentManagement
    PEAK_MANAGEMENT_AVAILABLE = True
except ImportError:
    PEAK_MANAGEMENT_AVAILABLE = False
    logger.error("JARVIS @PEAK Agent Management not available")


def register_upper_management_agents(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Register MACE, TONY, and GANDALF as upper management and Jedi Council members"""
    if not PEAK_MANAGEMENT_AVAILABLE:
        logger.error("❌ JARVIS @PEAK Agent Management not available")
        return {"success": False, "error": "Management system not available"}

    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    project_root = Path(project_root)

    logger.info("="*80)
    logger.info("👑 Registering Upper Management & Jedi Council Members")
    logger.info("   MACE, TONY, GANDALF - Both Normal & High Councils")
    logger.info("="*80)

    manager = JARVISPeakAgentManagement(project_root=project_root)

    result = {
        "success": True,
        "agents_registered": 0,
        "agents_failed": [],
        "upper_management": [],
        "jedi_council_members": []
    }

    # MACE WINDU - Upper Management, Jedi Council (Normal & High)
    logger.info("\n👑 Registering MACE WINDU...")
    try:
        mace = manager.register_agent(
            agent_id="mace_windu",
            agent_name="MACE WINDU - Upper Management & Jedi Council",
            task="Upper management oversight, Jedi Council (normal & high) decision-making, strategic planning",
            requirements={
                "isolation": False,  # Upper management - direct access
                "cpu": 15.0,  # High-level decision making
                "memory": 500.0,  # Strategic planning requires memory
                "authority": "upper_management",
                "council_levels": ["jedi_council", "jedi_high_council"],
                "force_local": True  # Force local for upper management
            },
            command=None,  # MACE is a decision-making agent, not a process
            dependencies=[],
            peak_tool_selection={
                "framework": "local",
                "rationale": "Upper management requires direct access - Local is @PEAK tool for authority",
                "alternatives_considered": ["docker", "mcp"]
            }
        )
        result["agents_registered"] += 1
        result["upper_management"].append("mace_windu")
        result["jedi_council_members"].append("mace_windu")
        logger.info(f"   ✅ Registered: {mace.agent_id}")
        logger.info(f"      Role: Upper Management & Jedi Council (Normal & High)")
        logger.info(f"      Framework: {mace.framework}")
    except Exception as e:
        result["agents_failed"].append({"agent_id": "mace_windu", "error": str(e)})
        logger.error(f"   ❌ Failed to register MACE: {e}")

    # TONY STARK - Upper Management, Jedi Council (Normal & High)
    logger.info("\n👑 Registering TONY STARK...")
    try:
        tony = manager.register_agent(
            agent_id="tony_stark",
            agent_name="TONY STARK - Upper Management & Jedi Council",
            task="Upper management oversight, Jedi Council (normal & high) decision-making, innovation leadership",
            requirements={
                "isolation": False,  # Upper management - direct access
                "cpu": 20.0,  # Innovation and strategic thinking
                "memory": 600.0,  # Extensive knowledge base
                "authority": "upper_management",
                "council_levels": ["jedi_council", "jedi_high_council"],
                "force_local": True  # Force local for upper management
            },
            command=None,  # TONY is a decision-making agent
            dependencies=[],
            peak_tool_selection={
                "framework": "local",
                "rationale": "Upper management requires direct access - Local is @PEAK tool for authority",
                "alternatives_considered": ["docker", "mcp"]
            }
        )
        result["agents_registered"] += 1
        result["upper_management"].append("tony_stark")
        result["jedi_council_members"].append("tony_stark")
        logger.info(f"   ✅ Registered: {tony.agent_id}")
        logger.info(f"      Role: Upper Management & Jedi Council (Normal & High)")
        logger.info(f"      Framework: {tony.framework}")
    except Exception as e:
        result["agents_failed"].append({"agent_id": "tony_stark", "error": str(e)})
        logger.error(f"   ❌ Failed to register TONY: {e}")

    # GANDALF - Upper Management, Jedi Council (Normal & High)
    logger.info("\n👑 Registering GANDALF...")
    try:
        gandalf = manager.register_agent(
            agent_id="gandalf",
            agent_name="GANDALF - Upper Management & Jedi Council",
            task="Upper management oversight, Jedi Council (normal & high) decision-making, wisdom and guidance",
            requirements={
                "isolation": False,  # Upper management - direct access
                "cpu": 18.0,  # Wisdom and deep thinking
                "memory": 700.0,  # Extensive knowledge and experience
                "authority": "upper_management",
                "council_levels": ["jedi_council", "jedi_high_council"],
                "force_local": True  # Force local for upper management
            },
            command=None,  # GANDALF is a decision-making agent
            dependencies=[],
            peak_tool_selection={
                "framework": "local",
                "rationale": "Upper management requires direct access - Local is @PEAK tool for authority",
                "alternatives_considered": ["docker", "mcp"]
            }
        )
        result["agents_registered"] += 1
        result["upper_management"].append("gandalf")
        result["jedi_council_members"].append("gandalf")
        logger.info(f"   ✅ Registered: {gandalf.agent_id}")
        logger.info(f"      Role: Upper Management & Jedi Council (Normal & High)")
        logger.info(f"      Framework: {gandalf.framework}")
    except Exception as e:
        result["agents_failed"].append({"agent_id": "gandalf", "error": str(e)})
        logger.error(f"   ❌ Failed to register GANDALF: {e}")

    logger.info("="*80)
    logger.info("✅ Upper Management Registration Complete")
    logger.info(f"   Registered: {result['agents_registered']}")
    logger.info(f"   Upper Management: {len(result['upper_management'])}")
    logger.info(f"   Jedi Council Members: {len(result['jedi_council_members'])}")
    logger.info("="*80)

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Register Upper Management")
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("👑 JARVIS Register Upper Management")
    print("   MACE, TONY, GANDALF - Both Normal & High Jedi Councils")
    print("="*80 + "\n")

    result = register_upper_management_agents(project_root=args.project_root)

    print("\n" + "="*80)
    print("📊 REGISTRATION RESULTS")
    print("="*80)
    print(f"Success: {'✅' if result['success'] else '❌'}")
    print(f"Agents Registered: {result['agents_registered']}")
    print()

    if result.get("upper_management"):
        print("👑 Upper Management:")
        for agent_id in result["upper_management"]:
            print(f"   ✅ {agent_id}")
        print()

    if result.get("jedi_council_members"):
        print("⚔️  Jedi Council Members (Normal & High):")
        for agent_id in result["jedi_council_members"]:
            print(f"   ✅ {agent_id}")
        print()

    if result.get("agents_failed"):
        print("❌ Failed Registrations:")
        for failure in result["agents_failed"]:
            print(f"   ❌ {failure['agent_id']}: {failure['error']}")
        print()

    print("✅ Complete")
    print("="*80 + "\n")
