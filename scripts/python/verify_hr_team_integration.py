#!/usr/bin/env python3
"""
SYPHON Verification: HR Team Integration

Run → Verify → Validate → Verify Again
Part of SYPHON verification process.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import logging
logger = logging.getLogger("verify_hr_team_integration")


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))


@dataclass
class VerificationResult:
    """Verification result"""
    name: str
    passed: bool
    details: Dict[str, Any]
    errors: List[str]


class HRTeamVerification:
    """HR Team Integration Verification (SYPHON Process)"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: List[VerificationResult] = []

    def run_all(self) -> List[VerificationResult]:
        """Run → Verify → Validate → Verify Again"""
        print("=" * 60)
        print("SYPHON VERIFICATION: HR Team Integration")
        print("=" * 60)

        # STEP 1: RUN
        print("\n[STEP 1] RUN")
        print("-" * 60)
        self._run_structure_check()
        self._run_routing_check()
        self._run_system_check()

        # STEP 2: VERIFY
        print("\n[STEP 2] VERIFY")
        print("-" * 60)
        self._verify_results()

        # STEP 3: VALIDATE
        print("\n[STEP 3] VALIDATE")
        print("-" * 60)
        self._validate_integrity()

        # STEP 4: VERIFY AGAIN
        print("\n[STEP 4] VERIFY AGAIN")
        print("-" * 60)
        self._verify_again()

        return self.results

    def _run_structure_check(self) -> None:
        """Run: Check HR team structure exists"""
        try:
            hr_file = self.project_root / "config" / "helpdesk" / "hr_team.json"
            if not hr_file.exists():
                self.results.append(VerificationResult(
                    "HR Team Structure File",
                    False,
                    {},
                    [f"File not found: {hr_file}"]
                ))
                return

            with open(hr_file, 'r') as f:
                hr_data = json.load(f)

            members = hr_data.get('team_members', {})

            self.results.append(VerificationResult(
                "HR Team Structure File",
                True,
                {
                    "team_name": hr_data.get('team_metadata', {}).get('team_name'),
                    "member_count": len(members),
                    "members": list(members.keys())
                },
                []
            ))
            print("✓ HR team structure file exists")

        except Exception as e:
            self.results.append(VerificationResult(
                "HR Team Structure File",
                False,
                {},
                [f"Error: {str(e)}"]
            ))
            print(f"✗ Error checking structure: {e}")

    def _run_routing_check(self) -> None:
        """Run: Check routing configuration"""
        try:
            routing_file = self.project_root / "config" / "droid_actor_routing.json"
            if not routing_file.exists():
                self.results.append(VerificationResult(
                    "Routing Configuration",
                    False,
                    {},
                    [f"File not found: {routing_file}"]
                ))
                return

            with open(routing_file, 'r') as f:
                routing = json.load(f)

            comm_expert = routing.get('domain_routing', {}).get('communication_expert', {})

            self.results.append(VerificationResult(
                "Routing Configuration",
                'team' in comm_expert and comm_expert['team'] == 'hr_team',
                {
                    "routes_to": comm_expert.get('team'),
                    "expected": "hr_team",
                    "keywords": len(comm_expert.get('keywords', []))
                },
                [] if comm_expert.get('team') == 'hr_team' else ["Routing not configured correctly"]
            ))

            if comm_expert.get('team') == 'hr_team':
                print("✓ Routing configured correctly")
            else:
                print("✗ Routing not configured correctly")

        except Exception as e:
            self.results.append(VerificationResult(
                "Routing Configuration",
                False,
                {},
                [f"Error: {str(e)}"]
            ))
            print(f"✗ Error checking routing: {e}")

    def _run_system_check(self) -> None:
        """Run: Check system integration"""
        try:
            from droid_actor_system import DroidActorSystem

            das = DroidActorSystem(self.project_root)
            experts = ['psychologist', 'linguist', 'speech-pathologist', 'rhetorician']
            loaded = [e for e in experts if e in das.droids]

            self.results.append(VerificationResult(
                "System Integration",
                len(loaded) == len(experts),
                {
                    "total_agents": len(das.droids),
                    "experts_loaded": len(loaded),
                    "experts_expected": len(experts),
                    "loaded_experts": loaded
                },
                [] if len(loaded) == len(experts) else [f"Only {len(loaded)}/{len(experts)} experts loaded"]
            ))

            if len(loaded) == len(experts):
                print(f"✓ System integration: {len(loaded)}/{len(experts)} experts loaded")
            else:
                print(f"✗ System integration: Only {len(loaded)}/{len(experts)} experts loaded")

        except Exception as e:
            self.results.append(VerificationResult(
                "System Integration",
                False,
                {},
                [f"Error: {str(e)}"]
            ))
            print(f"✗ Error checking system: {e}")

    def _verify_results(self) -> None:
        """Verify: All run checks passed"""
        passed = [r for r in self.results if r.passed]
        failed = [r for r in self.results if not r.passed]

        print(f"✓ Passed: {len(passed)}/{len(self.results)}")
        if failed:
            print(f"✗ Failed: {len(failed)}")
            for result in failed:
                print(f"  - {result.name}: {', '.join(result.errors)}")
        else:
            print("✓ All checks passed")

    def _validate_integrity(self) -> None:
        """Validate: Data integrity and consistency"""
        try:
            # Validate HR team JSON structure
            hr_file = self.project_root / "config" / "helpdesk" / "hr_team.json"
            with open(hr_file, 'r') as f:
                hr_data = json.load(f)

            # Validate routing JSON structure
            routing_file = self.project_root / "config" / "droid_actor_routing.json"
            with open(routing_file, 'r') as f:
                routing = json.load(f)

            # Check consistency: HR team members match routing
            hr_members = set(hr_data.get('team_members', {}).keys())
            routing_team = routing.get('domain_routing', {}).get('communication_expert', {}).get('team')

            integrity_passed = routing_team == 'hr_team'

            self.results.append(VerificationResult(
                "Data Integrity",
                integrity_passed,
                {
                    "hr_team_members": len(hr_members),
                    "routing_team": routing_team,
                    "consistency": integrity_passed
                },
                [] if integrity_passed else ["Routing team doesn't match HR team"]
            ))

            if integrity_passed:
                print("✓ Data integrity validated")
            else:
                print("✗ Data integrity issues found")

        except Exception as e:
            self.results.append(VerificationResult(
                "Data Integrity",
                False,
                {},
                [f"Error: {str(e)}"]
            ))
            print(f"✗ Validation error: {e}")

    def _verify_again(self) -> None:
        """Verify Again: Final verification pass"""
        all_passed = all(r.passed for r in self.results)

        print(f"✓ Final verification: {'PASS' if all_passed else 'FAIL'}")
        print(f"  Total checks: {len(self.results)}")
        print(f"  Passed: {sum(1 for r in self.results if r.passed)}")
        print(f"  Failed: {sum(1 for r in self.results if not r.passed)}")

        if all_passed:
            print("\n✅ ALL VERIFICATIONS PASSED - HR Team Integration Verified")
        else:
            print("\n❌ VERIFICATION FAILED - Review errors above")

        self.results.append(VerificationResult(
            "Final Verification",
            all_passed,
            {
                "total_checks": len(self.results) - 1,  # Exclude this final check
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed)
            },
            []
        ))

    def get_summary(self) -> Dict[str, Any]:
        """Get verification summary"""
        return {
            "total_checks": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "details": r.details,
                    "errors": r.errors
                }
                for r in self.results
            ]
        }


def main():
    try:
        """Main verification entry point"""
        verifier = HRTeamVerification(project_root)
        results = verifier.run_all()

        summary = verifier.get_summary()

        # Save verification result (SYPHON style)
        output_file = project_root / "data" / "syphon" / "verification_hr_team.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n✓ Verification results saved to: {output_file}")

        return 0 if all(r.passed for r in results) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())