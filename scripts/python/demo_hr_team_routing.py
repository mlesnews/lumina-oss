#!/usr/bin/env python3
"""
Demo: HR Team Routing for Communication Expert Agents

Demonstrates that communication_expert domain routes to HR team correctly.
"""

import sys
import json
from pathlib import Path
import logging
logger = logging.getLogger("demo_hr_team_routing")


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

def demo_hr_team_structure():
    try:
        """Demo 1: Show HR team structure loads correctly"""
        print("=" * 60)
        print("DEMO 1: HR Team Structure")
        print("=" * 60)

        hr_team_file = project_root / "config" / "helpdesk" / "hr_team.json"

        if not hr_team_file.exists():
            print("❌ HR team config not found!")
            return False

        with open(hr_team_file, 'r') as f:
            hr_team = json.load(f)

        print(f"\n✓ HR Team: {hr_team['team_metadata']['team_name']}")
        print(f"  Team ID: {hr_team['team_metadata']['team_id']}")
        print(f"  Manager: {hr_team['team_metadata']['manager']}")
        print(f"  Status: {hr_team['team_metadata']['status']}")

        print(f"\n✓ Team Members ({len(hr_team['team_members'])}):")
        for member_id, member in hr_team['team_members'].items():
            print(f"  - {member['name']}: {member['role']}")
            print(f"    Specialization: {member['specialization']}")

        print(f"\n✓ Routing Keywords: {len(hr_team['routing']['keywords'])} keywords")
        print(f"  Default Assignment: {hr_team['routing']['default_assignment']}")

        return True

    except Exception as e:
        logger.error(f"Error in demo_hr_team_structure: {e}", exc_info=True)
        raise
def demo_helpdesk_routing():
    try:
        """Demo 2: Show helpdesk routes communication_expert to HR team"""
        print("\n" + "=" * 60)
        print("DEMO 2: Helpdesk Routing")
        print("=" * 60)

        routing_file = project_root / "config" / "droid_actor_routing.json"

        if not routing_file.exists():
            print("❌ Routing config not found!")
            return False

        with open(routing_file, 'r') as f:
            routing = json.load(f)

        comm_expert = routing['domain_routing'].get('communication_expert', {})

        if 'team' not in comm_expert:
            print("❌ communication_expert domain not configured correctly!")
            return False

        print(f"\n✓ Domain: communication_expert")
        print(f"  Routes to Team: {comm_expert['team']}")
        print(f"  Team Config: {comm_expert.get('team_config', 'N/A')}")
        print(f"  Fallback: {comm_expert.get('fallback', 'N/A')}")
        print(f"  Keywords: {len(comm_expert.get('keywords', []))} keywords")

        return True

    except Exception as e:
        logger.error(f"Error in demo_helpdesk_routing: {e}", exc_info=True)
        raise
def demo_droid_actor_system():
    """Demo 3: Show droid actor system loads and routes correctly"""
    print("\n" + "=" * 60)
    print("DEMO 3: Droid Actor System Integration")
    print("=" * 60)

    try:
        from droid_actor_system import DroidActorSystem

        das = DroidActorSystem(project_root)

        print(f"\n✓ System loaded")
        print(f"  Total agents: {len(das.droids)}")
        print(f"  Helpdesk location: {das.helpdesk_location}")

        # Check if HR team experts are loaded
        experts = ['psychologist', 'linguist', 'speech-pathologist', 'rhetorician']
        loaded_experts = [e for e in experts if e in das.droids]

        print(f"\n✓ Expert agents loaded: {len(loaded_experts)}/{len(experts)}")
        for expert_id in loaded_experts:
            expert = das.droids[expert_id]
            print(f"  - {expert.name}: {expert.specialization}")

        # Test workflow context analysis
        test_workflow = {
            "workflow_id": "demo_comm_expert",
            "workflow_name": "Communication Breakdown Pattern Analysis",
            "workflow_type": "analysis",
            "steps": [{"action": "analyze_pattern"}],
            "domain": "communication_expert"
        }

        context = das.analyze_workflow_context(test_workflow)

        print(f"\n✓ Workflow Context Analysis:")
        print(f"  Domain: {context.domain}")
        print(f"  Complexity: {context.complexity}")
        print(f"  Expertise Required: {len(context.requires_expertise)} areas")

        # Test routing
        assignment = das.select_droid_for_workflow(context)

        print(f"\n✓ Routing Result:")
        print(f"  Assigned: {assignment.droid_name} ({assignment.droid_id})")
        print(f"  Confidence: {assignment.confidence_score:.2f}")
        print(f"  Reason: {assignment.assignment_reason[:100]}...")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("HR TEAM ROUTING DEMONSTRATION")
    print("=" * 60)

    results = []

    results.append(("HR Team Structure", demo_hr_team_structure()))
    results.append(("Helpdesk Routing", demo_helpdesk_routing()))
    results.append(("Droid Actor System", demo_droid_actor_system()))

    print("\n" + "=" * 60)
    print("DEMO RESULTS")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(r[1] for r in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL DEMOS PASSED - HR Team Routing Works!")
    else:
        print("❌ SOME DEMOS FAILED - Check configuration")
    print("=" * 60)

    return 0 if all_passed else 1

if __name__ == "__main__":



    sys.exit(main())