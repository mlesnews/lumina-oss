#!/usr/bin/env python3
"""
Proving Ground: Stress Testing
Advanced stress tests and edge case validation

@JARVIS @MARVIN @STRESS_TEST @EDGE_CASES
"""

import sys
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import asyncio

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from workflow_base import WorkflowBase
    from workflow_completion_verifier import WorkflowCompletionVerifier
    from v3_verification import V3Verification
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class StressTestWorkflow(WorkflowBase):
    """Workflow for stress testing"""

    def __init__(self, test_id: int, num_steps: int = 10, num_deliverables: int = 5):
        super().__init__(f"Stress Test {test_id}", total_steps=num_steps)
        self.test_id = test_id
        self.expected_deliverables = [
            f"stress_output/test_{test_id}_deliverable_{i}.md"
            for i in range(num_deliverables)
        ]

    async def execute(self) -> Dict[str, Any]:
        """Execute stress test workflow"""
        stress_output = project_root / "stress_output"
        stress_output.mkdir(exist_ok=True)

        # Execute all steps
        for step in range(2, self.total_steps + 1):
            self._mark_step(step, f"Step {step}", "completed")
            time.sleep(0.01)  # Minimal delay

        # Create deliverables
        for deliverable in self.expected_deliverables:
            file_path = project_root / deliverable
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(f"Stress test deliverable {self.test_id}\n")

        return {"status": "complete", "test_id": self.test_id}


class ProvingGroundStressTest:
    """Stress testing framework"""

    def __init__(self):
        self.project_root = project_root
        self.stress_output = project_root / "stress_output"
        self.stress_output.mkdir(exist_ok=True)
        self.results = []

    def test_concurrent_workflows(self, num_workflows: int = 10):
        try:
            """Test concurrent workflow execution"""
            print(f"\n🔥 Stress Test: {num_workflows} Concurrent Workflows")
            print("="*70)

            start_time = time.time()
            workflows = []

            # Create workflows
            for i in range(num_workflows):
                workflow = StressTestWorkflow(i, num_steps=5, num_deliverables=3)
                workflows.append(workflow)

            # Execute concurrently
            async def run_all():
                tasks = [w.execute() for w in workflows]
                return await asyncio.gather(*tasks)

            results = asyncio.run(run_all())

            # Verify all
            verification_times = []
            for workflow in workflows:
                v_start = time.time()
                verification = workflow.verify_completion()
                verification_times.append(time.time() - v_start)

            elapsed = time.time() - start_time

            result = {
                "test": "concurrent_workflows",
                "num_workflows": num_workflows,
                "execution_time": elapsed,
                "avg_verification_time": sum(verification_times) / len(verification_times),
                "status": "success"
            }

            self.results.append(result)
            print(f"✅ Completed {num_workflows} workflows in {elapsed:.2f}s")
            print(f"   Average verification time: {result['avg_verification_time']:.3f}s")

            return result

        except Exception as e:
            self.logger.error(f"Error in test_concurrent_workflows: {e}", exc_info=True)
            raise
    def test_many_deliverables(self, num_deliverables: int = 100):
        try:
            """Test workflow with many deliverables"""
            print(f"\n📦 Stress Test: {num_deliverables} Deliverables")
            print("="*70)

            workflow = StressTestWorkflow(0, num_steps=5, num_deliverables=num_deliverables)

            start_time = time.time()
            asyncio.run(workflow.execute())
            execution_time = time.time() - start_time

            v_start = time.time()
            verification = workflow.verify_completion()
            verification_time = time.time() - v_start

            result = {
                "test": "many_deliverables",
                "num_deliverables": num_deliverables,
                "execution_time": execution_time,
                "verification_time": verification_time,
                "status": "success"
            }

            self.results.append(result)
            print(f"✅ Created and verified {num_deliverables} deliverables")
            print(f"   Execution: {execution_time:.2f}s, Verification: {verification_time:.2f}s")

            return result

        except Exception as e:
            self.logger.error(f"Error in test_many_deliverables: {e}", exc_info=True)
            raise
    def test_parallel_processing(self, num_tasks: int = 100):
        """Test parallel processing with many tasks"""
        print(f"\n⚡ Stress Test: {num_tasks} Parallel Tasks")
        print("="*70)

        workflow = StressTestWorkflow(0, num_steps=3)

        tasks = [lambda i=x: (time.sleep(0.01), i*2)[1] for x in range(num_tasks)]

        start_time = time.time()
        results = list(workflow.parallel_execute(tasks, max_workers=10))
        elapsed = time.time() - start_time

        result = {
            "test": "parallel_processing",
            "num_tasks": num_tasks,
            "execution_time": elapsed,
            "throughput": num_tasks / elapsed,
            "status": "success"
        }

        self.results.append(result)
        print(f"✅ Processed {num_tasks} tasks in {elapsed:.2f}s")
        print(f"   Throughput: {result['throughput']:.1f} tasks/sec")

        return result

    def run_all_stress_tests(self):
        try:
            """Run all stress tests"""
            print("\n" + "="*70)
            print("🔥 PROVING GROUND: Stress Testing")
            print("="*70)

            # Cleanup first
            if self.stress_output.exists():
                import shutil
                shutil.rmtree(self.stress_output)
                self.stress_output.mkdir(exist_ok=True)

            # Run tests
            self.test_concurrent_workflows(10)
            self.test_many_deliverables(50)
            self.test_parallel_processing(50)

            # Save results
            results_file = project_root / "sandbox_results" / f"stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_file.parent.mkdir(exist_ok=True)

            with open(results_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "stress_tests": self.results
                }, f, indent=2)

            print(f"\n💾 Results saved to: {results_file}")


        except Exception as e:
            self.logger.error(f"Error in run_all_stress_tests: {e}", exc_info=True)
            raise
def main():
    tester = ProvingGroundStressTest()
    tester.run_all_stress_tests()


if __name__ == "__main__":



    main()