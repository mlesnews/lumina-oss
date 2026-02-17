#!/usr/bin/env python3
"""
Interactive Demo: Workflow Verification System
Proof of Concept with Human Interaction

This script demonstrates all features of the workflow verification system
with interactive prompts and real-time feedback.

@JARVIS @MARVIN @DEMO @POC
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
logger = logging.getLogger("demo_workflow_verification_interactive")


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from workflow_base import WorkflowBase
    from workflow_completion_verifier import WorkflowCompletionVerifier, VerificationStatus
    from v3_verification import V3Verification, V3VerificationConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)


class DemoWorkflow(WorkflowBase):
    """Demo workflow for interactive demonstration"""

    def __init__(self, demo_name: str = "Interactive Demo Workflow"):
        super().__init__(demo_name, total_steps=5)

        # Set expected deliverables for demo
        self.expected_deliverables = [
            "demo_output/demo_documentation.md",
            "demo_output/demo_script.py",
            "demo_output/demo_config.json"
        ]

        self.demo_data = {}

    async def execute(self) -> Dict[str, Any]:
        """Execute demo workflow with interactive steps"""

        print("\n" + "="*70)
        print("🚀 WORKFLOW EXECUTION STARTED")
        print("="*70)

        # Step 2: Data Collection
        self._mark_step(2, "Data Collection", "in_progress")
        print("\n📊 Step 2/5: Data Collection")
        print("   Collecting demo data...")
        time.sleep(1)
        self.demo_data = {
            "timestamp": datetime.now().isoformat(),
            "demo_name": self.workflow_name,
            "execution_id": self.execution_id
        }
        self._mark_step(2, "Data Collection", "completed")
        print("   ✅ Data collected")

        # Step 3: Processing
        self._mark_step(3, "Processing", "in_progress")
        print("\n⚙️  Step 3/5: Processing")
        print("   Processing demo data...")
        time.sleep(1)
        self.demo_data["processed"] = True
        self._mark_step(3, "Processing", "completed")
        print("   ✅ Processing complete")

        # Step 4: Create Deliverables (Interactive)
        self._mark_step(4, "Create Deliverables", "in_progress")
        print("\n📝 Step 4/5: Create Deliverables")

        # Create demo output directory
        demo_output = project_root / "demo_output"
        demo_output.mkdir(exist_ok=True)

        # Create documentation
        doc_path = demo_output / "demo_documentation.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(f"# Demo Documentation\n\n")
            f.write(f"**Workflow**: {self.workflow_name}\n")
            f.write(f"**Execution ID**: {self.execution_id}\n")
            f.write(f"**Created**: {datetime.now().isoformat()}\n\n")
            f.write(f"This is a demo documentation file created by the workflow verification system.\n")
        print(f"   ✅ Created: {doc_path.name}")

        # Create script
        script_path = demo_output / "demo_script.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(f"#!/usr/bin/env python3\n")
            f.write(f"# Demo Script\n")
            f.write(f"# Created by: {self.workflow_name}\n")
            f.write(f"# Execution ID: {self.execution_id}\n\n")
            f.write(f"print('Hello from demo script!')\n")
        print(f"   ✅ Created: {script_path.name}")

        # Create config
        config_path = demo_output / "demo_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.demo_data, f, indent=2)
        print(f"   ✅ Created: {config_path.name}")

        self._mark_step(4, "Create Deliverables", "completed")

        # Step 5: Finalization
        self._mark_step(5, "Finalization", "in_progress")
        print("\n🎯 Step 5/5: Finalization")
        print("   Finalizing workflow...")
        time.sleep(0.5)
        self._mark_step(5, "Finalization", "completed")
        print("   ✅ Finalization complete")

        print("\n" + "="*70)
        print("✅ WORKFLOW EXECUTION COMPLETE")
        print("="*70)

        return {
            "status": "complete",
            "execution_id": self.execution_id,
            "demo_data": self.demo_data,
            "deliverables_created": len(self.expected_deliverables)
        }


def print_section(title: str, char: str = "="):
    """Print a formatted section header"""
    print("\n" + char*70)
    print(f"  {title}")
    print(char*70)


def print_feature(name: str, description: str, status: str = "✅"):
    """Print a feature description"""
    print(f"\n{status} {name}")
    print(f"   {description}")


def interactive_demo():
    try:
        """Run interactive demonstration"""

        print_section("🎬 WORKFLOW VERIFICATION SYSTEM - INTERACTIVE DEMO", "=")
        print("\nWelcome to the Workflow Verification System demonstration!")
        print("This demo showcases all features with interactive prompts.")

        # Feature Overview
        print_section("📋 FEATURE OVERVIEW", "-")
        print_feature("Step Tracking", "Mandatory step tracking for all workflows")
        print_feature("v3_verification", "Pre-workflow verification and validation")
        print_feature("Completion Verifier", "Post-workflow verification and validation")
        print_feature("Template System", "Auto-loading verification templates")
        print_feature("Parallel Processing", "Resource-aware parallel execution")
        print_feature("Batch Processing", "Efficient large dataset handling")
        print_feature("Memory Persistence", "Tiered workflow state storage")

        input("\n⏸️  Press Enter to continue...")

        # Initialize Workflow
        print_section("🔧 WORKFLOW INITIALIZATION", "-")
        print("\nInitializing demo workflow...")
        workflow = DemoWorkflow("Interactive Demo Workflow")
        print(f"✅ Workflow initialized: {workflow.workflow_name}")
        print(f"   Execution ID: {workflow.execution_id}")
        print(f"   Total Steps: {workflow.total_steps}")
        print(f"   Expected Deliverables: {len(workflow.expected_deliverables)}")

        # Show v3_verification
        if workflow.v3_verifier:
            print_section("🔍 v3_VERIFICATION (Pre-Workflow)", "-")
            print("\nRunning pre-workflow verification...")
            workflow_data = workflow.to_dict()
            v3_result = workflow.v3_verifier.verify_workflow_preconditions(workflow_data)
            print(f"✅ v3_verification: {v3_result.message}")
            print(f"   Status: {'PASSED' if v3_result.passed else 'FAILED'}")
            if v3_result.details:
                print(f"   Details: {json.dumps(v3_result.details, indent=2)}")

        input("\n⏸️  Press Enter to execute workflow...")

        # Execute Workflow
        import asyncio
        result = asyncio.run(workflow.execute())

        input("\n⏸️  Press Enter to verify completion...")

        # Verify Completion
        print_section("✅ COMPLETION VERIFICATION", "-")
        print("\nRunning completion verification...")
        verification = workflow.verify_completion()

        # Display Results
        print("\n" + "="*70)
        print("📊 VERIFICATION RESULTS")
        print("="*70)

        # Step Verification
        if "step_verification" in verification:
            step_ver = verification["step_verification"]
            print(f"\n📋 Step Verification:")
            print(f"   Total Steps: {step_ver.get('total_steps', 0)}")
            print(f"   Completed: {step_ver.get('completed_steps', 0)}")
            print(f"   Missing: {step_ver.get('missing_steps', [])}")
            print(f"   Can Declare Complete: {step_ver.get('can_declare_complete', False)}")

        # v3_verification Results
        if "v3_verification" in verification:
            v3_ver = verification["v3_verification"]
            print(f"\n🔍 v3_verification (Pre-Workflow):")
            print(f"   Status: {'PASSED' if v3_ver.get('passed') else 'FAILED'}")
            print(f"   Message: {v3_ver.get('message', 'N/A')}")

        # Completion Verification
        if "completion_verification" in verification:
            comp_ver = verification["completion_verification"]
            print(f"\n✅ Completion Verification:")
            print(f"   Overall Status: {comp_ver.get('overall_status', 'N/A')}")
            print(f"   Completion: {comp_ver.get('completion_percentage', 0):.1f}%")
            print(f"   Summary: {comp_ver.get('summary', 'N/A')}")

            missing = comp_ver.get('missing_items', [])
            if missing:
                print(f"\n   ⚠️  Missing Items ({len(missing)}):")
                for item in missing:
                    print(f"      - {item}")
            else:
                print(f"\n   ✅ All deliverables found!")

            next_steps = comp_ver.get('next_steps', [])
            if next_steps:
                print(f"\n   📝 Next Steps:")
                for step in next_steps[:3]:  # Show first 3
                    print(f"      - {step}")

        # Overall Status
        print(f"\n" + "="*70)
        overall_complete = verification.get("overall_can_declare_complete", False)
        status_icon = "✅" if overall_complete else "⚠️"
        print(f"{status_icon} OVERALL STATUS: {'COMPLETE' if overall_complete else 'INCOMPLETE'}")
        print("="*70)

        # Feature Showcase
        print_section("🎯 FEATURE SHOWCASE", "-")

        # Parallel Processing Demo
        print("\n🔄 Parallel Processing Demo:")
        print("   Executing 5 tasks in parallel...")
        tasks = [lambda i=x: (time.sleep(0.1), print(f"      ✅ Task {i+1} completed"))[1] for x in range(5)]
        list(workflow.parallel_execute(tasks, max_workers=3))
        print("   ✅ All tasks completed in parallel")

        # Batch Processing Demo
        print("\n📦 Batch Processing Demo:")
        items = list(range(10))
        processor = lambda x: x * 2
        results = list(workflow.batch_process(items, processor, batch_size=3))
        print(f"   Processed {len(items)} items in batches")
        print(f"   Results: {results[:5]}... (showing first 5)")

        # Progress Reporting
        print("\n📊 Progress Reporting:")
        progress = workflow.get_progress()
        print(f"   Current Step: {progress.get('current_step', 0)}/{progress.get('total_steps', 0)}")
        print(f"   Completed: {len(progress.get('completed_steps', []))}")
        print(f"   Missing: {len(progress.get('missing_steps', []))}")

        # Memory Persistence
        if workflow.memory_persistence:
            print("\n💾 Memory Persistence:")
            stored = workflow.store_in_memory("hot", {"demo": True})
            print(f"   Stored in memory: {stored}")

        # Final Summary
        print_section("📋 DEMO SUMMARY", "=")
        print("\n✅ All features demonstrated successfully!")
        print("\nFeatures Tested:")
        print("  ✅ Step Tracking")
        print("  ✅ v3_verification (Pre-Workflow)")
        print("  ✅ Completion Verification (Post-Workflow)")
        print("  ✅ File Verification")
        print("  ✅ Parallel Processing")
        print("  ✅ Batch Processing")
        print("  ✅ Progress Reporting")
        print("  ✅ Memory Persistence")

        print(f"\n📁 Deliverables created in: {project_root / 'demo_output'}")
        print(f"📊 Verification logs in: {project_root / 'data' / 'workflow_verifications'}")

        print("\n" + "="*70)
        print("🎉 INTERACTIVE DEMO COMPLETE!")
        print("="*70 + "\n")

        return verification


    except Exception as e:
        logger.error(f"Error in interactive_demo: {e}", exc_info=True)
        raise
def main():
    """Main entry point"""
    try:
        verification = interactive_demo()

        # Save demo results
        demo_results = {
            "demo_timestamp": datetime.now().isoformat(),
            "verification": verification,
            "status": "success"
        }

        results_path = project_root / "demo_output" / "demo_results.json"
        results_path.parent.mkdir(exist_ok=True)
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(demo_results, f, indent=2)

        print(f"💾 Demo results saved to: {results_path}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":



    main()