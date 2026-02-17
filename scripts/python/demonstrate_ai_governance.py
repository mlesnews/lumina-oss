#!/usr/bin/env python3
"""
AI Governance Hierarchy Demonstration

Demonstrates the three-tier AI governance system with clear examples
of how Entry Level, Middle Management, and Senior Management tiers
work together in consensus decision-making.

Shows both micro-level (task decisions) and macro-level (project decisions)
governance in action.
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from three_tier_ai_system import ThreeTierAISystem, AITier, GovernanceDecision
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def demonstrate_governance_hierarchy():
    """Comprehensive demonstration of AI governance hierarchy"""
    print("🤖 AI GOVERNANCE HIERARCHY DEMONSTRATION")
    print("="*80)
    print("This demonstrates how the three-tier AI system works as a governance hierarchy")
    print("similar to corporate management structures.")
    print()

    # Initialize the system
    system = ThreeTierAISystem()

    print("🏗️  ESTABLISHED TIER HIERARCHY:")
    print("-" * 50)
    for tier in AITier:
        config = system.governance_config["tier_hierarchy"][tier]
        print(f"\n🎯 {tier.name} TIER")
        print(f"   Role: {config['level']}")
        print(f"   Authority: {config['authority']}")
        print(f"   Consensus Required: {config['consensus_required']}")
        print(f"   Decision Power: {config['decision_power']}")
    print()

    # Demonstrate decision categories
    print("📋 DECISION CATEGORIES BY TIER:")
    print("-" * 50)
    categories = system.governance_config["decision_categories"]
    for category, tier in categories.items():
        print(f"   {category.upper()}: {tier.name} Tier")
    print()

    # SCENARIO 1: Routine Task (Entry Level)
    print("🎬 SCENARIO 1: ROUTINE CODE GENERATION TASK")
    print("-" * 50)
    print("Task: Generate a simple Python function to calculate fibonacci numbers")
    print("Expected: Entry Level (LOCAL tier) handles this independently")
    print()

    # Simulate the decision process
    task_complexity = "routine"
    required_tier = system.governance_config["decision_categories"][task_complexity]

    print(f"🤖 AI System Analysis:")
    print(f"   Task Complexity: {task_complexity}")
    print(f"   Required Tier: {required_tier.name}")
    print(f"   Consensus Required: {required_tier.consensus_required()}")
    print(f"   Decision Authority: {required_tier.decision_authority()}")
    print()
    print("✅ DECISION: Entry Level can proceed independently")
    print("   No consensus required for routine tasks")
    print()

    # SCENARIO 2: Complex Coordination (Middle Management)
    print("🎬 SCENARIO 2: COMPLEX MULTI-SYSTEM COORDINATION")
    print("-" * 50)
    print("Task: Refactor entire codebase with multiple AI systems working together")
    print("Expected: Middle Management (FREE tier) coordinates with consensus")
    print()

    task_complexity = "oversight"
    required_tier = system.governance_config["decision_categories"][task_complexity]

    print(f"🤖 AI System Analysis:")
    print(f"   Task Complexity: {task_complexity}")
    print(f"   Required Tier: {required_tier.name}")
    print(f"   Consensus Required: {required_tier.consensus_required()}")
    print(f"   Decision Authority: {required_tier.decision_authority()}")
    print()

    # Initiate governance decision
    decision_id = system.initiate_governance_decision(
        title="Major Codebase Refactoring Initiative",
        description="Coordinate multiple AI systems to refactor the entire codebase following new architectural patterns",
        decision_type="proceed",
        governance_level="macro",
        required_tier=AITier.FREE,
        stakeholders=["EntryLevelAI", "MiddleManagerAI", "SeniorExecAI"],
        deadline_hours=12
    )

    print(f"📝 Governance Decision Initiated: {decision_id}")
    print("   Middle Management consensus required")
    print("   Stakeholders notified: EntryLevelAI, MiddleManagerAI, SeniorExecAI")
    print()

    # Simulate voting process
    print("🗳️  CONSENSUS VOTING PROCESS:")
    print("-" * 30)

    votes = [
        ("EntryLevelAI", AITier.LOCAL, "approve", "Task is within my execution capabilities", 0.8),
        ("MiddleManagerAI", AITier.FREE, "approve", "Coordinated approach will ensure quality", 0.9),
        ("SeniorExecAI", AITier.PREMIUM, "approve", "Strategic value justifies the coordination effort", 0.95),
    ]

    for voter_id, voter_tier, decision, reasoning, confidence in votes:
        success = system.submit_consensus_vote(
            decision_id=decision_id,
            voter_id=voter_id,
            voter_tier=voter_tier,
            vote_decision=decision,
            reasoning=reasoning,
            confidence_score=confidence
        )
        print(f"   ✅ {voter_id} ({voter_tier.name}): {decision.upper()} ({confidence:.2f} confidence)")

    print()
    print("📊 CONSENSUS RESULT:")
    status = system.get_governance_status()
    for decision in status['recent_decisions']:
        if decision['id'] == decision_id:
            print(f"   Decision: {decision['title']}")
            print(f"   Resolution: {decision['resolution'].upper()}")
            print("   ✅ CONSENSUS ACHIEVED - PROCEED WITH INITIATIVE")
    print()

    # SCENARIO 3: Strategic Decision (Senior Management)
    print("🎬 SCENARIO 3: STRATEGIC ARCHITECTURE DECISION")
    print("-" * 50)
    print("Decision: Whether to adopt a new AI framework that will affect the entire organization")
    print("Expected: Senior Management (PREMIUM tier) with high consensus threshold")
    print()

    task_complexity = "strategic"
    required_tier = system.governance_config["decision_categories"][task_complexity]

    print(f"🤖 AI System Analysis:")
    print(f"   Decision Type: {task_complexity}")
    print(f"   Required Tier: {required_tier.name}")
    print(f"   Consensus Required: {required_tier.consensus_required()}")
    print(f"   Decision Authority: {required_tier.decision_authority()}")
    print(f"   Consensus Threshold: {system.governance_config['consensus_thresholds'][required_tier]*100:.0f}%")
    print()

    # Initiate strategic decision
    strategic_decision_id = system.initiate_governance_decision(
        title="Adopt Revolutionary AI Framework",
        description="Decision to adopt a new AI framework that will replace current architecture and affect all systems",
        decision_type="proceed",
        governance_level="enterprise",
        required_tier=AITier.PREMIUM,
        stakeholders=["CTO_AI", "Architecture_AI", "Security_AI", "Operations_AI"],
        deadline_hours=48
    )

    print(f"📝 Strategic Decision Initiated: {strategic_decision_id}")
    print("   Senior Management consensus required (80% threshold)")
    print("   Enterprise-level governance")
    print("   48-hour decision deadline")
    print()

    # Simulate complex voting with mixed opinions
    print("🗳️  STRATEGIC VOTING PROCESS:")
    print("-" * 30)

    strategic_votes = [
        ("EntryLevelAI", AITier.LOCAL, "approve", "Technically feasible to implement", 0.7),
        ("MiddleManagerAI", AITier.FREE, "modify", "Approve with modifications to integration plan", 0.8),
        ("Architecture_AI", AITier.PREMIUM, "approve", "Architecturally sound and future-proof", 0.95),
        ("Security_AI", AITier.PREMIUM, "deny", "Security concerns with new framework dependencies", 0.85),
        ("Operations_AI", AITier.PREMIUM, "approve", "Operational benefits outweigh migration costs", 0.9),
        ("CTO_AI", AITier.PREMIUM, "approve", "Strategic advantage justifies the transition", 0.98),
    ]

    for voter_id, voter_tier, decision, reasoning, confidence in strategic_votes:
        success = system.submit_consensus_vote(
            decision_id=strategic_decision_id,
            voter_id=voter_id,
            voter_tier=voter_tier,
            vote_decision=decision,
            reasoning=reasoning,
            confidence_score=confidence
        )
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {voter_id} ({voter_tier.name}): {decision.upper()} ({confidence:.2f})")

    print()
    print("📊 STRATEGIC CONSENSUS ANALYSIS:")
    strategic_status = system.get_governance_status()
    for decision in strategic_status['recent_decisions']:
        if decision['id'] == strategic_decision_id:
            print(f"   Decision: {decision['title']}")
            print(f"   Resolution: {decision['resolution'].upper()}")
            break

    # Show voting breakdown
    if strategic_decision_id in system.decision_history:
        final_decision = system.decision_history[-1]  # Most recent
        vote_breakdown = {}
        for vote_data in final_decision.votes.values():
            vote_type = vote_data["vote"]
            vote_breakdown[vote_type] = vote_breakdown.get(vote_type, 0) + 1

        print("   Vote Breakdown:")
        for vote_type, count in vote_breakdown.items():
            print(f"      {vote_type.upper()}: {count} votes")

        threshold = system.governance_config["consensus_thresholds"][AITier.PREMIUM]
        total_votes = len(final_decision.votes)
        consensus_ratio = vote_breakdown.get(final_decision.resolution, 0) / total_votes
        print(f"      Consensus Ratio: {consensus_ratio:.2f}")
        print(f"      Required Threshold: {threshold:.2f}")
        print(f"      Consensus: {'✅ ACHIEVED' if consensus_ratio >= threshold else '❌ FAILED'}")

    print()

    # SUMMARY
    print("🎯 GOVERNANCE HIERARCHY SUMMARY")
    print("="*80)
    print("✅ Entry Level (LOCAL): Handles routine tasks independently")
    print("✅ Middle Management (FREE): Coordinates complex tasks with consensus")
    print("✅ Senior Management (PREMIUM): Makes strategic decisions with high consensus")
    print()
    print("🔄 Escalation Flow:")
    print("   Entry Level → Middle Management → Senior Management")
    print("   (as task complexity and stakes increase)")
    print()
    print("⚖️  Consensus Requirements:")
    print("   Entry Level: No consensus required (fast execution)")
    print("   Middle Management: 70% consensus required")
    print("   Senior Management: 80% consensus required")
    print()
    print("🎭 Governance Levels:")
    print("   Micro: Individual task decisions")
    print("   Macro: Project/initiative decisions")
    print("   Enterprise: Organization-wide strategic decisions")
    print()

    # Final status
    final_status = system.get_governance_status()
    print("📈 FINAL SYSTEM STATUS:")
    print(f"   Active Governance Decisions: {final_status['active_decisions']}")
    print(f"   Completed Decisions: {final_status['completed_decisions']}")
    print(f"   Governance Hierarchy: ✅ Established")
    print(f"   Consensus Engine: ✅ Operational")

    print("\n" + "="*80)
    print("🎉 AI GOVERNANCE HIERARCHY DEMONSTRATION COMPLETE!")
    print("   The three-tier system is ready for both micro and macro governance.")
    print("="*80)


if __name__ == "__main__":
    demonstrate_governance_hierarchy()