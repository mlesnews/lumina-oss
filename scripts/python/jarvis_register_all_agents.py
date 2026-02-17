#!/usr/bin/env python3
"""
JARVIS Register All Agents - Auto-Discovery and Registration

Auto-discovers all agents/subagents and registers them with JARVIS @PEAK management.
Uses @PEAK tool selection to determine best framework for each agent.

Tags: #JARVIS #AGENTS #AUTODISCOVERY #PEAK @JARVIS @TEAM
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

logger = get_logger("JARVISRegisterAllAgents")

try:
    from jarvis_peak_agent_management import JARVISPeakAgentManagement
    PEAK_MANAGEMENT_AVAILABLE = True
except ImportError:
    PEAK_MANAGEMENT_AVAILABLE = False
    logger.error("JARVIS @PEAK Agent Management not available")


def discover_va_agents(project_root: Path) -> List[Dict[str, Any]]:
    """Discover Virtual Assistant agents"""
    agents = []

    # IMVA (Iron Man Virtual Assistant)
    agents.append({
        "agent_id": "imva",
        "agent_name": "Iron Man Virtual Assistant",
        "task": "Desktop companion with TTS, voice recognition, and visual interface",
        "requirements": {
            "tts": True,
            "isolation": False,
            "cpu": 5.0,
            "memory": 200.0  # MB
        },
        "command": f"python {project_root}/scripts/python/ironman_virtual_assistant.py",
        "dependencies": []
    })

    # ACVA (Anakin/Vader Combat Virtual Assistant)
    agents.append({
        "agent_id": "acva",
        "agent_name": "Anakin/Vader Combat Virtual Assistant",
        "task": "Combat VA with lightsaber animations and Jedi abilities",
        "requirements": {
            "isolation": False,
            "cpu": 3.0,
            "memory": 150.0
        },
        "command": f"python {project_root}/scripts/python/jarvis_acva_combat_demo.py",
        "dependencies": []
    })

    # JARVIS_VA (JARVIS Virtual Assistant)
    agents.append({
        "agent_id": "jarvis_va",
        "agent_name": "JARVIS Virtual Assistant",
        "task": "Background coordinator and supervisor",
        "requirements": {
            "isolation": False,
            "cpu": 2.0,
            "memory": 100.0
        },
        "command": f"python {project_root}/scripts/python/jarvis_fulltime_super_agent.py",
        "dependencies": []
    })

    return agents


def discover_mcp_agents(project_root: Path) -> List[Dict[str, Any]]:
    """Discover MCP server agents"""
    agents = []

    # Check MCP config
    mcp_config_file = project_root / ".cursor" / "mcp_config.json"
    if mcp_config_file.exists():
        try:
            import json
            with open(mcp_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                mcp_servers = config.get("mcpServers", {})

                for server_name, server_config in mcp_servers.items():
                    agents.append({
                        "agent_id": f"mcp_{server_name.lower()}",
                        "agent_name": f"MCP Server: {server_name}",
                        "task": f"MCP server integration: {server_name}",
                        "requirements": {
                            "mcp": True,
                            "cpu": 1.0,
                            "memory": 50.0
                        },
                        "mcp_server": server_name,
                        "dependencies": []
                    })
        except Exception as e:
            logger.debug(f"Could not read MCP config: {e}")

    return agents


def discover_docker_agents(project_root: Path) -> List[Dict[str, Any]]:
    try:
        """Discover Docker container agents"""
        agents = []

        # Check for docker-compose files
        docker_compose_dir = project_root / "containerization"
        if docker_compose_dir.exists():
            for compose_file in docker_compose_dir.rglob("docker-compose.yml"):
                service_name = compose_file.parent.name
                agents.append({
                    "agent_id": f"docker_{service_name}",
                    "agent_name": f"Docker Service: {service_name}",
                    "task": f"Docker containerized service: {service_name}",
                    "requirements": {
                        "isolation": True,
                        "scaling": True,
                        "cpu": 10.0,
                        "memory": 500.0
                    },
                    "docker_compose_file": str(compose_file.relative_to(project_root)),
                    "dependencies": []
                })

        return agents


    except Exception as e:
        logger.error(f"Error in discover_docker_agents: {e}", exc_info=True)
        raise
def register_all_agents(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """Register all discovered agents with JARVIS @PEAK management"""
    if not PEAK_MANAGEMENT_AVAILABLE:
        logger.error("❌ JARVIS @PEAK Agent Management not available")
        return {"success": False, "error": "Management system not available"}

    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    project_root = Path(project_root)

    logger.info("="*80)
    logger.info("🔍 Auto-Discovering All Agents for JARVIS @PEAK Management")
    logger.info("="*80)

    manager = JARVISPeakAgentManagement(project_root=project_root)

    result = {
        "success": True,
        "agents_discovered": 0,
        "agents_registered": 0,
        "agents_failed": [],
        "by_type": {}
    }

    # Discover all agent types
    all_agents = []

    logger.info("\n🔍 Discovering Virtual Assistant agents...")
    va_agents = discover_va_agents(project_root)
    all_agents.extend(va_agents)
    result["by_type"]["virtual_assistants"] = len(va_agents)
    logger.info(f"   ✅ Found {len(va_agents)} VA agents")

    logger.info("\n🔍 Discovering MCP server agents...")
    mcp_agents = discover_mcp_agents(project_root)
    all_agents.extend(mcp_agents)
    result["by_type"]["mcp_servers"] = len(mcp_agents)
    logger.info(f"   ✅ Found {len(mcp_agents)} MCP server agents")

    logger.info("\n🔍 Discovering Docker container agents...")
    docker_agents = discover_docker_agents(project_root)
    all_agents.extend(docker_agents)
    result["by_type"]["docker_containers"] = len(docker_agents)
    logger.info(f"   ✅ Found {len(docker_agents)} Docker container agents")

    result["agents_discovered"] = len(all_agents)

    # Register all agents
    logger.info("\n📝 Registering agents with JARVIS @PEAK management...")
    for agent_config in all_agents:
        try:
            agent = manager.register_agent(**agent_config)
            result["agents_registered"] += 1
            logger.info(f"   ✅ Registered: {agent.agent_id} ({agent.framework})")
        except Exception as e:
            result["agents_failed"].append({
                "agent_id": agent_config.get("agent_id", "unknown"),
                "error": str(e)
            })
            logger.warning(f"   ⚠️  Failed to register {agent_config.get('agent_id', 'unknown')}: {e}")

    logger.info("="*80)
    logger.info("✅ Agent Registration Complete")
    logger.info(f"   Discovered: {result['agents_discovered']}")
    logger.info(f"   Registered: {result['agents_registered']}")
    logger.info(f"   Failed: {len(result['agents_failed'])}")
    logger.info("="*80)

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Register All Agents")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--start-all", action="store_true", help="Start all registered agents after registration")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🤖 JARVIS Register All Agents - Auto-Discovery")
    print("   Using @PEAK tool selection: 'Measure twice, cut once, the first time, every time!'")
    print("="*80 + "\n")

    result = register_all_agents(project_root=args.project_root)

    print("\n" + "="*80)
    print("📊 REGISTRATION RESULTS")
    print("="*80)
    print(f"Agents Discovered: {result['agents_discovered']}")
    print(f"Agents Registered: {result['agents_registered']}")
    print(f"Agents Failed: {len(result['agents_failed'])}")
    print()

    if result.get("by_type"):
        print("By Type:")
        for agent_type, count in result["by_type"].items():
            print(f"   {agent_type}: {count}")
        print()

    if result.get("agents_failed"):
        print("Failed Registrations:")
        for failure in result["agents_failed"]:
            print(f"   ❌ {failure['agent_id']}: {failure['error']}")
        print()

    if args.start_all and result["success"]:
        print("🚀 Starting all registered agents...")
        manager = JARVISPeakAgentManagement(project_root=args.project_root)
        for agent_id in manager.agent_definitions.keys():
            success = manager.start_agent(agent_id)
            if success:
                print(f"   ✅ Started: {agent_id}")
            else:
                print(f"   ❌ Failed to start: {agent_id}")
        print()

    print("✅ Complete")
    print("="*80 + "\n")
