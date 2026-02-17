#!/usr/bin/env python3
"""
Sandbox/Proving Ground: Workflow Verification System
"The Dummy" - Safe Testing Environment

This is a comprehensive sandbox for testing, experimentation, and validation
of the workflow verification system without affecting production data.

@JARVIS @MARVIN @SANDBOX @PROVING_GROUND @TESTING
"""

import sys
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from workflow_base import WorkflowBase
    from workflow_completion_verifier import WorkflowCompletionVerifier, VerificationStatus
    from v3_verification import V3Verification, V3VerificationConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class TestScenario(Enum):
    """Test scenarios for sandbox testing"""
    BASIC = "basic"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    PARALLEL = "parallel"
    BATCH = "batch"
    TEMPLATE = "template"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE = "performance"
    EDGE_CASES = "edge_cases"
    STRESS = "stress"


class SandboxWorkflow(WorkflowBase):
    """Sandbox workflow for testing and experimentation"""

    def __init__(self, test_name: str = "Sandbox Test", scenario: TestScenario = TestScenario.BASIC):
        super().__init__(test_name, total_steps=5)
        self.scenario = scenario
        self.test_data = {}
        self.created_files = []

        # Set expected deliverables based on scenario
        if scenario == TestScenario.INCOMPLETE:
            # Missing some deliverables for testing incomplete workflows
            self.expected_deliverables = [
                "sandbox_output/complete_file.md",
                "sandbox_output/missing_file.md"  # This will be missing
            ]
        else:
            self.expected_deliverables = [
                "sandbox_output/test_document.md",
                "sandbox_output/test_script.py",
                "sandbox_output/test_config.json"
            ]

    async def execute(self) -> Dict[str, Any]:
        """Execute sandbox workflow based on scenario"""
        sandbox_output = project_root / "sandbox_output"
        sandbox_output.mkdir(exist_ok=True)

        # Step 2: Setup
        self._mark_step(2, "Setup", "completed")
        self.test_data["setup"] = datetime.now().isoformat()
        time.sleep(0.1)

        # Step 3: Processing
        self._mark_step(3, "Processing", "completed")

        if self.scenario == TestScenario.PARALLEL:
            # Test parallel processing
            tasks = [lambda i=x: (time.sleep(0.05), i*2)[1] for x in range(5)]
            results = list(self.parallel_execute(tasks, max_workers=3))
            self.test_data["parallel_results"] = results

        elif self.scenario == TestScenario.BATCH:
            # Test batch processing
            items = list(range(10))
            processor = lambda x: x * 2
            results = list(self.batch_process(items, processor, batch_size=3))
            self.test_data["batch_results"] = results

        elif self.scenario == TestScenario.ERROR_HANDLING:
            # Simulate error scenario
            self.test_data["error_simulated"] = True

        elif self.scenario == TestScenario.PERFORMANCE:
            # Performance test
            start_time = time.time()
            # Simulate work
            time.sleep(0.1)
            self.test_data["execution_time"] = time.time() - start_time

        time.sleep(0.1)

        # Step 4: Create Deliverables (unless incomplete scenario)
        self._mark_step(4, "Create Deliverables", "completed")

        if self.scenario != TestScenario.INCOMPLETE:
            # Create all deliverables
            doc_path = sandbox_output / "test_document.md"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(f"# Sandbox Test Document\n\n")
                f.write(f"**Scenario**: {self.scenario.value}\n")
                f.write(f"**Created**: {datetime.now().isoformat()}\n\n")
                f.write(f"This is a sandbox test file.\n")
            self.created_files.append(str(doc_path))

            script_path = sandbox_output / "test_script.py"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write("#!/usr/bin/env python3\n")
                f.write("# Sandbox Test Script\n")
                f.write(f"# Scenario: {self.scenario.value}\n\n")
                f.write("print('Sandbox test script')\n")
            self.created_files.append(str(script_path))

            config_path = sandbox_output / "test_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.test_data, f, indent=2)
            self.created_files.append(str(config_path))
        else:
            # Only create one file for incomplete scenario
            doc_path = sandbox_output / "complete_file.md"
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write("# Complete File\n\nThis file exists.\n")
            self.created_files.append(str(doc_path))
            # Missing file is intentionally not created

        # Step 5: Finalization
        self._mark_step(5, "Finalization", "completed")
        self.test_data["finalized"] = True

        return {
            "status": "complete",
            "scenario": self.scenario.value,
            "test_data": self.test_data,
            "created_files": self.created_files
        }


class SandboxTester:
    """Sandbox testing and experimentation framework"""

    def __init__(self):
        self.project_root = project_root
        self.sandbox_dir = project_root / "sandbox_output"
        self.results_dir = project_root / "sandbox_results"
        self.sandbox_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        self.test_results = []
        self.scenarios_run = []

    def cleanup(self):
        try:
            """Clean up sandbox directory"""
            if self.sandbox_dir.exists():
                shutil.rmtree(self.sandbox_dir)
                self.sandbox_dir.mkdir(exist_ok=True)
                print(f"🧹 Cleaned sandbox directory: {self.sandbox_dir}")

        except Exception as e:
            self.logger.error(f"Error in cleanup: {e}", exc_info=True)
            raise
    def run_scenario(self, scenario: TestScenario, cleanup_before: bool = True) -> Dict[str, Any]:
        """Run a specific test scenario"""
        print(f"\n{'='*70}")
        print(f"🧪 Running Scenario: {scenario.value.upper()}")
        print(f"{'='*70}")

        if cleanup_before:
            self.cleanup()

        try:
            # Create workflow
            workflow = SandboxWorkflow(f"Sandbox {scenario.value.title()}", scenario)

            # Execute workflow
            import asyncio
            result = asyncio.run(workflow.execute())

            # Verify completion
            verification = workflow.verify_completion()

            # Store results
            scenario_result = {
                "scenario": scenario.value,
                "timestamp": datetime.now().isoformat(),
                "workflow_result": result,
                "verification": verification,
                "status": "success"
            }

            self.test_results.append(scenario_result)
            self.scenarios_run.append(scenario.value)

            # Display results
            self._display_results(scenario_result)

            return scenario_result

        except Exception as e:
            error_result = {
                "scenario": scenario.value,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
            self.test_results.append(error_result)
            print(f"\n❌ Error in scenario {scenario.value}: {e}")
            import traceback
            traceback.print_exc()
            return error_result

    def _display_results(self, result: Dict[str, Any]):
        """Display test results"""
        verification = result.get("verification", {})

        print(f"\n📊 Results for {result['scenario']}:")

        # Step verification
        if "step_verification" in verification:
            step_ver = verification["step_verification"]
            print(f"   Steps: {step_ver.get('completed_steps', [])} completed")

        # Completion verification
        if "completion_verification" in verification:
            comp_ver = verification["completion_verification"]
            print(f"   Completion: {comp_ver.get('completion_percentage', 0):.1f}%")
            print(f"   Status: {comp_ver.get('overall_status', 'N/A')}")

            missing = comp_ver.get('missing_items', [])
            if missing:
                print(f"   ⚠️  Missing: {len(missing)} items")
            else:
                print(f"   ✅ All deliverables found")

        # Overall status
        overall_complete = verification.get("overall_can_declare_complete", False)
        status_icon = "✅" if overall_complete else "⚠️"
        print(f"   {status_icon} Overall: {'COMPLETE' if overall_complete else 'INCOMPLETE'}")

    def run_all_scenarios(self, cleanup_before: bool = True):
        """Run all test scenarios"""
        print("\n" + "="*70)
        print("🚀 SANDBOX: Running All Test Scenarios")
        print("="*70)

        if cleanup_before:
            self.cleanup()

        scenarios = [
            TestScenario.BASIC,
            TestScenario.COMPLETE,
            TestScenario.INCOMPLETE,
            TestScenario.PARALLEL,
            TestScenario.BATCH,
            TestScenario.ERROR_HANDLING,
            TestScenario.PERFORMANCE
        ]

        for scenario in scenarios:
            self.run_scenario(scenario, cleanup_before=False)
            time.sleep(0.5)  # Brief pause between scenarios

        # Save all results
        self.save_results()

    def save_results(self):
        try:
            """Save all test results to file"""
            results_file = self.results_dir / f"sandbox_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_scenarios": len(self.scenarios_run),
                "scenarios_run": self.scenarios_run,
                "test_results": self.test_results,
                "summary": {
                    "successful": len([r for r in self.test_results if r.get("status") == "success"]),
                    "failed": len([r for r in self.test_results if r.get("status") == "error"]),
                    "total": len(self.test_results)
                }
            }

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            print(f"\n💾 Results saved to: {results_file}")
            return results_file

        except Exception as e:
            self.logger.error(f"Error in save_results: {e}", exc_info=True)
            raise
    def run_interactive(self):
        """Run interactive sandbox mode"""
        print("\n" + "="*70)
        print("🎮 SANDBOX: Interactive Mode")
        print("="*70)

        print("\nAvailable scenarios:")
        for i, scenario in enumerate(TestScenario, 1):
            print(f"  {i}. {scenario.value}")
        print("  a. Run all scenarios")
        print("  c. Cleanup sandbox")
        print("  q. Quit")

        while True:
            try:
                choice = input("\nSelect scenario (1-10, a, c, q): ").strip().lower()

                if choice == 'q':
                    break
                elif choice == 'c':
                    self.cleanup()
                    print("✅ Sandbox cleaned")
                elif choice == 'a':
                    self.run_all_scenarios()
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(TestScenario):
                        scenario = list(TestScenario)[idx]
                        self.run_scenario(scenario)
                    else:
                        print("❌ Invalid choice")
                else:
                    print("❌ Invalid choice")
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Sandbox/Proving Ground for Workflow Verification")
    parser.add_argument("--scenario", choices=[s.value for s in TestScenario],
                       help="Run specific scenario")
    parser.add_argument("--all", action="store_true",
                       help="Run all scenarios")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--cleanup", action="store_true",
                       help="Cleanup sandbox before running")

    args = parser.parse_args()

    tester = SandboxTester()

    if args.cleanup:
        tester.cleanup()

    if args.interactive:
        tester.run_interactive()
    elif args.all:
        tester.run_all_scenarios(cleanup_before=not args.cleanup)
    elif args.scenario:
        scenario = TestScenario(args.scenario)
        tester.run_scenario(scenario, cleanup_before=not args.cleanup)
    else:
        # Default: interactive mode
        tester.run_interactive()


if __name__ == "__main__":



    main()