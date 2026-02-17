#!/usr/bin/env python3
"""
Dummy Test Fixtures
Test data, mocks, and fixtures for sandbox testing

@JARVIS @MARVIN @FIXTURES @MOCKS @TEST_DATA
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
logger = logging.getLogger("dummy_test_fixtures")



class DummyFixtures:
    """Test fixtures and dummy data"""

    @staticmethod
    def create_test_template() -> Dict[str, Any]:
        """Create a dummy verification template"""
        return {
            "workflow_id": "dummy_workflow_001",
            "workflow_name": "Dummy Test Workflow",
            "expected_tasks": [
                {
                    "task_id": "task_1",
                    "description": "Setup test environment",
                    "verification_notes": [
                        "File exists: test_output/setup.md",
                        "Configuration created"
                    ]
                },
                {
                    "task_id": "task_2",
                    "description": "Execute test operations",
                    "verification_notes": [
                        "Operations completed",
                        "Log file exists: test_output/operations.log"
                    ]
                },
                {
                    "task_id": "task_3",
                    "description": "Generate test results",
                    "verification_notes": [
                        "File exists: test_output/results.json",
                        "Summary document created: test_output/summary.md"
                    ]
                }
            ],
            "deliverables": [
                "test_output/setup.md",
                "test_output/operations.log",
                "test_output/results.json",
                "test_output/summary.md"
            ],
            "workflow_context": {
                "test_type": "dummy",
                "environment": "sandbox",
                "timestamp": datetime.now().isoformat()
            }
        }

    @staticmethod
    def create_mock_workflow_data() -> Dict[str, Any]:
        """Create mock workflow data structure"""
        return {
            "workflow_id": "mock_workflow_001",
            "workflow_name": "Mock Test Workflow",
            "execution_id": f"mock_{int(datetime.now().timestamp())}",
            "total_steps": 5,
            "steps": [
                {"step": 1, "name": "Issue Received", "status": "completed"},
                {"step": 2, "name": "Analysis", "status": "completed"},
                {"step": 3, "name": "Execution", "status": "completed"},
                {"step": 4, "name": "Verification", "status": "completed"},
                {"step": 5, "name": "Completion", "status": "completed"}
            ],
            "expected_deliverables": [
                "mock_output/document.md",
                "mock_output/script.py"
            ],
            "metadata": {
                "created": datetime.now().isoformat(),
                "environment": "sandbox"
            }
        }

    @staticmethod
    def create_test_files(project_root: Path, file_list: List[str]):
        try:
            """Create dummy test files"""
            for file_path in file_list:
                full_path = project_root / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                if file_path.endswith('.md'):
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Dummy Test File\n\n")
                        f.write(f"**Path**: {file_path}\n")
                        f.write(f"**Created**: {datetime.now().isoformat()}\n\n")
                        f.write(f"This is a dummy test file for sandbox testing.\n")

                elif file_path.endswith('.py'):
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write("#!/usr/bin/env python3\n")
                        f.write("# Dummy Test Script\n")
                        f.write(f"# Created: {datetime.now().isoformat()}\n\n")
                        f.write("print('Dummy test script')\n")

                elif file_path.endswith('.json'):
                    with open(full_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            "test": True,
                            "file_path": file_path,
                            "created": datetime.now().isoformat()
                        }, f, indent=2)

                else:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(f"Dummy test file: {file_path}\n")

        except Exception as e:
            logger.error(f"Error in create_test_files: {e}", exc_info=True)
            raise
    @staticmethod
    def get_test_scenarios() -> List[Dict[str, Any]]:
        """Get list of test scenarios"""
        return [
            {
                "name": "basic_complete",
                "description": "Basic workflow with all deliverables",
                "steps": 5,
                "deliverables": 3,
                "should_complete": True
            },
            {
                "name": "incomplete",
                "description": "Workflow with missing deliverables",
                "steps": 5,
                "deliverables": 3,
                "create_all": False,
                "should_complete": False
            },
            {
                "name": "many_steps",
                "description": "Workflow with many steps",
                "steps": 20,
                "deliverables": 5,
                "should_complete": True
            },
            {
                "name": "many_deliverables",
                "description": "Workflow with many deliverables",
                "steps": 5,
                "deliverables": 20,
                "should_complete": True
            },
            {
                "name": "minimal",
                "description": "Minimal workflow",
                "steps": 2,
                "deliverables": 1,
                "should_complete": True
            }
        ]


def main():
    try:
        """Generate dummy test fixtures"""
        project_root = Path(__file__).parent.parent.parent

        fixtures = DummyFixtures()

        # Create test template
        template = fixtures.create_test_template()
        template_path = project_root / "templates" / "dummy_test_template.json"
        template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        print(f"✅ Created test template: {template_path}")

        # Create mock workflow data
        mock_data = fixtures.create_mock_workflow_data()
        mock_path = project_root / "sandbox_output" / "mock_workflow_data.json"
        mock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(mock_path, 'w', encoding='utf-8') as f:
            json.dump(mock_data, f, indent=2)
        print(f"✅ Created mock workflow data: {mock_path}")

        # Create test scenarios file
        scenarios = fixtures.get_test_scenarios()
        scenarios_path = project_root / "sandbox_output" / "test_scenarios.json"
        with open(scenarios_path, 'w', encoding='utf-8') as f:
            json.dump(scenarios, f, indent=2)
        print(f"✅ Created test scenarios: {scenarios_path}")

        print("\n✅ All dummy fixtures created!")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()