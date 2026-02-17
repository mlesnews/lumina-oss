#!/usr/bin/env python3
"""
JARVIS Agent Collaboration Demo - @COLAB with JARVIS Oversight
Demonstrates agents and subagents collaborating with JARVIS supervision

@JARVIS @TEAM @COLAB #COLLABORATION #AGENTS #SUBAGENTS
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.agent_collaboration import (
    AgentCollaborationSystem,
    AgentRole
)

def main():
    """Demo agent collaboration with JARVIS oversight"""
    print("=" * 70)
    print("🤝 JARVIS Agent Collaboration System - @COLAB")
    print("=" * 70)
    print()

    # Initialize collaboration system
    colab = AgentCollaborationSystem(project_root=project_root, jarvis_oversight=True)

    # Register some agents/subagents
    print("📝 Registering agents...")
    print("-" * 70)

    colab.register_agent(
        agent_id="r2d2",
        name="R2-D2",
        role=AgentRole.SUBAGENT,
        capabilities=["technical_operations", "diagnostics", "system_access"]
    )

    colab.register_agent(
        agent_id="c3po",
        name="C-3PO",
        role=AgentRole.SUBAGENT,
        capabilities=["protocol", "coordination", "communication"]
    )

    colab.register_agent(
        agent_id="k2so",
        name="K-2SO",
        role=AgentRole.SUBAGENT,
        capabilities=["security", "analysis", "tactical"]
    )

    print()
    print("✅ Agents registered:")
    for agent in colab.list_agents():
        print(f"  - {agent['name']} ({agent['role']}): {', '.join(agent['capabilities'])}")

    print()
    print("=" * 70)
    print("🤝 Starting Collaboration Session")
    print("=" * 70)
    print()

    # Start collaboration
    session = colab.start_collaboration(
        task_description="Analyze system performance and provide recommendations",
        agent_ids=["r2d2", "c3po", "k2so"],
        jarvis_oversight=True,
        oversight_level="standard"
    )

    print(f"✅ Session started: {session.session_id}")
    print(f"   Task: {session.task.description}")
    print(f"   Participants: {', '.join([colab.agents[aid].name for aid in session.participants])}")
    print(f"   JARVIS Oversight: {'ENABLED' if session.jarvis_oversight_enabled else 'DISABLED'}")
    print()

    # Simulate agent communication
    print("💬 Agent Communication:")
    print("-" * 70)

    colab.agent_communicate(
        session_id=session.session_id,
        from_agent_id="c3po",
        to_agent_id="r2d2",
        message="R2-D2, please analyze CPU utilization",
        data={"metric": "cpu_utilization"}
    )

    time.sleep(0.5)

    colab.agent_communicate(
        session_id=session.session_id,
        from_agent_id="r2d2",
        to_agent_id="c3po",
        message="CPU utilization is at 65%. All systems nominal.",
        data={"cpu_percent": 65.0, "status": "nominal"}
    )

    time.sleep(0.5)

    colab.agent_communicate(
        session_id=session.session_id,
        from_agent_id="k2so",
        to_agent_id="c3po",
        message="Security analysis complete. No threats detected.",
        data={"threats": 0, "status": "secure"}
    )

    print()

    # Agents complete tasks
    print("✅ Task Completion:")
    print("-" * 70)

    colab.agent_complete_task(
        session_id=session.session_id,
        agent_id="r2d2",
        result={"cpu_analysis": "65% utilization", "recommendation": "System healthy"}
    )

    colab.agent_complete_task(
        session_id=session.session_id,
        agent_id="k2so",
        result={"security_analysis": "No threats", "recommendation": "System secure"}
    )

    print()

    # Complete collaboration
    print("🏁 Completing Collaboration:")
    print("-" * 70)

    final_result = {
        "status": "success",
        "recommendations": [
            "System performance is optimal",
            "No security threats detected",
            "Continue current operations"
        ],
        "participants": [colab.agents[aid].name for aid in session.task.assigned_agents]
    }

    colab.complete_collaboration(
        session_id=session.session_id,
        final_result=final_result,
        success=True
    )

    print()
    print("=" * 70)
    print("👁️  JARVIS Oversight Report")
    print("=" * 70)

    report = colab.get_oversight_report(session_id=session.session_id)
    print(f"   Total Actions: {report['total_oversight_actions']}")
    print(f"   Sessions Monitored: {report['sessions_monitored']}")
    print()
    print("   Recent Actions:")
    for action in report["actions"]:
        print(f"     - {action['action']}: {action['message']}")

    print()
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)

if __name__ == "__main__":


    main()