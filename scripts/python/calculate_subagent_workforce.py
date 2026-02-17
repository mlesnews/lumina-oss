#!/usr/bin/env python3
"""
Calculate SubAgent Workforce
#FACTS #JUST-THE-FACTS

Calculate total SubAgent "employees" across all frameworks.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import logging
logger = logging.getLogger("calculate_subagent_workforce")


def calculate_workforce(project_root: Path) -> Dict[str, Any]:
    try:
        """Calculate total SubAgent workforce"""

        # Load integration report
        report_file = project_root / "data" / "subagent_integration_report.json"
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)

        # Master orchestrator already has 17 SubAgents
        master_orchestrator_subagents = 17

        # Estimate SubAgents per framework type
        estimates = {
            "orchestrators": 5,  # Average 5 components per orchestrator
            "managers": 3,        # Average 3 capabilities per manager
            "systems": 2,         # Average 2 components per system
            "controllers": 2,     # Average 2 capabilities per controller
            "coordinators": 3    # Average 3 components per coordinator
        }

        # Count frameworks by type (without SubAgents)
        without_subagents = report["integration_status"]["without_subagents"]

        orchestrators = [f for f in without_subagents if "orchestrator" in f]
        managers = [f for f in without_subagents if "manager" in f]
        systems = [f for f in without_subagents if "system" in f]
        controllers = [f for f in without_subagents if "controller" in f]
        coordinators = [f for f in without_subagents if "coordinator" in f]

        # Calculate projected workforce
        projected = {
            "master_orchestrator": master_orchestrator_subagents,
            "orchestrators": len(orchestrators) * estimates["orchestrators"],
            "managers": len(managers) * estimates["managers"],
            "systems": len(systems) * estimates["systems"],
            "controllers": len(controllers) * estimates["controllers"],
            "coordinators": len(coordinators) * estimates["coordinators"]
        }

        total_projected = sum(projected.values())

        # Already integrated frameworks
        with_subagents = report["integration_status"]["with_subagents"]

        # Conservative estimate (minimum)
        conservative_estimate = total_projected

        # Realistic estimate (average)
        realistic_estimate = int(total_projected * 1.2)  # 20% overhead

        # Maximum estimate (if frameworks are complex)
        maximum_estimate = int(total_projected * 1.5)  # 50% overhead

        return {
            "current_workforce": {
                "master_orchestrator_subagents": master_orchestrator_subagents,
                "integrated_frameworks": len(with_subagents),
                "total_current": master_orchestrator_subagents  # Only master has SubAgents currently
            },
            "projected_workforce": {
                "breakdown": projected,
                "total_projected": total_projected,
                "conservative": conservative_estimate,
                "realistic": realistic_estimate,
                "maximum": maximum_estimate
            },
            "frameworks": {
                "orchestrators": len(orchestrators),
                "managers": len(managers),
                "systems": len(systems),
                "controllers": len(controllers),
                "coordinators": len(coordinators),
                "total_to_integrate": len(without_subagents)
            },
            "facts": {
                "frameworks_to_integrate": len(without_subagents),
                "current_subagents": master_orchestrator_subagents,
                "projected_subagents": realistic_estimate,
                "scale_factor": f"{realistic_estimate / master_orchestrator_subagents:.1f}x"
            }
        }


    except Exception as e:
        logger.error(f"Error in calculate_workforce: {e}", exc_info=True)
        raise
def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent
        workforce = calculate_workforce(project_root)

        print("\n" + "="*60)
        print("SUBAGENT WORKFORCE CALCULATION")
        print("#FACTS #JUST-THE-FACTS")
        print("="*60)
        print()

        print("CURRENT WORKFORCE:")
        print(f"  Master Orchestrator SubAgents: {workforce['current_workforce']['master_orchestrator_subagents']}")
        print(f"  Integrated Frameworks: {workforce['current_workforce']['integrated_frameworks']}")
        print(f"  Total Current SubAgents: {workforce['current_workforce']['total_current']}")
        print()

        print("PROJECTED WORKFORCE (After Full Integration):")
        print(f"  Orchestrators: {workforce['projected_workforce']['breakdown']['orchestrators']} SubAgents")
        print(f"  Managers: {workforce['projected_workforce']['breakdown']['managers']} SubAgents")
        print(f"  Systems: {workforce['projected_workforce']['breakdown']['systems']} SubAgents")
        print(f"  Controllers: {workforce['projected_workforce']['breakdown']['controllers']} SubAgents")
        print(f"  Coordinators: {workforce['projected_workforce']['breakdown']['coordinators']} SubAgents")
        print()
        print(f"  Total Projected: {workforce['projected_workforce']['total_projected']} SubAgents")
        print(f"  Realistic Estimate: {workforce['projected_workforce']['realistic']} SubAgents")
        print(f"  Maximum Estimate: {workforce['projected_workforce']['maximum']} SubAgents")
        print()

        print("THE FACTS:")
        print(f"  Frameworks to Integrate: {workforce['facts']['frameworks_to_integrate']}")
        print(f"  Current SubAgents: {workforce['facts']['current_subagents']}")
        print(f"  Projected SubAgents: {workforce['facts']['projected_subagents']}")
        print(f"  Scale Factor: {workforce['facts']['scale_factor']}")
        print()

        print("="*60)
        print(f"ANSWER: ~{workforce['projected_workforce']['realistic']} SubAgents")
        print("="*60)
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()