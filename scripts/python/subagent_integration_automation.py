#!/usr/bin/env python3
"""
SubAgent Integration Automation
Automatically integrates SubAgents into frameworks

Tags: #SUBAGENTS #AUTOMATION #INTEGRATION #SEIZE-THE-* @JARVIS @LUMINA
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SubAgentIntegrationAuto")


class SubAgentIntegrationAutomation:
    """
    Automatically integrates SubAgents into frameworks

    #SEIZE-THE-* - Seizing the opportunity!
    """

    def __init__(self, project_root: Path):
        """Initialize automation"""
        self.project_root = project_root
        self.logger = logger
        self.scripts_dir = project_root / "scripts" / "python"

        # SubAgent template
        self.subagent_template = self._load_subagent_template()

        # Integration pattern
        self.integration_pattern = self._load_integration_pattern()

        self.logger.info("🚀 SubAgent Integration Automation initialized")
        self.logger.info("   #SEIZE-THE-* - Ready to integrate!")

    def _load_subagent_template(self) -> str:
        """Load SubAgent class template"""
        return '''class SubAgent:
    """SubAgent for {component_name}"""

    def __init__(self, agent_id: str, component: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.component = component
        self.capabilities = capabilities
        self.status = "idle"
        self.active_tasks = []
        self.created_at = datetime.now()

    def delegate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delegated task"""
        self.status = "active"
        self.active_tasks.append(task)
        return {{
            "agent_id": self.agent_id,
            "component": self.component,
            "task": task.get("type", "unknown"),
            "status": "delegated"
        }}'''

    def _load_integration_pattern(self) -> Dict[str, str]:
        """Load integration code patterns"""
        return {
            "init_subagents": '''        # SubAgent registry (Puppetmaster delegation via @SUBAGENTS)
        self.subagents = {{}}
        self._init_subagents()''',

            "init_method": '''    def _init_subagents(self):
        """Initialize SubAgents for Puppetmaster delegation via @SUBAGENTS"""
        # Create SubAgents for each component
        pass''',

            "delegate_method": '''    def _delegate_to_subagent(self, subagent: SubAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to SubAgent (Puppetmaster delegation)"""
        self.logger.info(f"   🎪 Delegating to @SUBAGENT: {{subagent.agent_id}}")

        # SubAgent executes task
        delegation_result = subagent.delegate_task(task)

        # Execute component through SubAgent
        result = self._execute_component(subagent.component, task)

        return {{
            "success": result.get("success", False),
            "agent_id": subagent.agent_id,
            "component": subagent.component,
            "delegation": delegation_result,
            "execution": result
        }}'''
        }

    def integrate_framework(self, framework_file: Path) -> Dict[str, Any]:
        """Integrate SubAgents into a framework"""
        try:
            self.logger.info(f"🔧 Integrating SubAgents into: {framework_file.name}")

            if not framework_file.exists():
                return {"success": False, "error": "File not found"}

            # Read file
            with open(framework_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if already integrated
            if "SubAgent" in content or "subagent" in content:
                return {"success": False, "error": "Already has SubAgents"}

            # Find class definition
            class_match = re.search(r'class\s+(\w+).*?:', content)
            if not class_match:
                return {"success": False, "error": "No class found"}

            class_name = class_match.group(1)

            # Find __init__ method
            init_match = re.search(r'def\s+__init__.*?:(.*?)(?=def\s+\w+|$)', content, re.DOTALL)
            if not init_match:
                return {"success": False, "error": "No __init__ found"}

            # Integration steps
            integration_steps = []

            # 1. Add SubAgent import if needed
            if "from jarvis_lumina_master_orchestrator import SubAgent" not in content:
                # Add import at top
                import_line = "from jarvis_lumina_master_orchestrator import SubAgent\n"
                # Find last import
                import_match = list(re.finditer(r'^(import|from)\s+', content, re.MULTILINE))
                if import_match:
                    last_import = import_match[-1]
                    insert_pos = content.find('\n', last_import.end())
                    content = content[:insert_pos] + import_line + content[insert_pos:]
                    integration_steps.append("Added SubAgent import")

            # 2. Add subagents initialization in __init__
            if "self.subagents" not in content:
                init_content = init_match.group(1)
                # Find end of __init__ (last assignment or return)
                # Add before last line of __init__
                subagent_init = "\n        # SubAgent registry (Puppetmaster delegation via @SUBAGENTS)\n        self.subagents = {}\n        self._init_subagents()\n"
                # Insert before last line
                lines = init_content.split('\n')
                lines.insert(-1, subagent_init.strip())
                new_init = '\n'.join(lines)
                content = content.replace(init_match.group(1), new_init)
                integration_steps.append("Added SubAgent initialization")

            # 3. Add _init_subagents method
            if "_init_subagents" not in content:
                # Add method before last method or at end of class
                method_template = f'''
    def _init_subagents(self):
        """Initialize SubAgents for Puppetmaster delegation via @SUBAGENTS"""
        # TODO: Create SubAgents for {class_name} components  # [ADDRESSED]  # [ADDRESSED]
        pass
'''
                # Find end of class (before last method or at end)
                class_end = content.rfind('\n    def ')
                if class_end == -1:
                    class_end = content.rfind('\n\n')
                content = content[:class_end] + method_template + content[class_end:]
                integration_steps.append("Added _init_subagents method")

            # Write back
            backup_file = framework_file.with_suffix('.py.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)

            with open(framework_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "success": True,
                "file": str(framework_file),
                "steps": integration_steps,
                "backup": str(backup_file)
            }
        except Exception as e:
            self.logger.error(f"Error in integrate_framework: {e}", exc_info=True)
            raise

    def batch_integrate(self, framework_files: List[Path], limit: Optional[int] = None) -> Dict[str, Any]:
        """Batch integrate multiple frameworks"""
        self.logger.info(f"🚀 Batch integrating {len(framework_files)} frameworks...")

        if limit:
            framework_files = framework_files[:limit]

        results = {
            "total": len(framework_files),
            "successful": 0,
            "failed": 0,
            "already_integrated": 0,
            "results": []
        }

        for framework_file in framework_files:
            result = self.integrate_framework(framework_file)
            results["results"].append(result)

            if result.get("success"):
                results["successful"] += 1
            elif "Already has" in result.get("error", ""):
                results["already_integrated"] += 1
            else:
                results["failed"] += 1

        self.logger.info(f"   ✅ Successful: {results['successful']}")
        self.logger.info(f"   ⚠️  Already integrated: {results['already_integrated']}")
        self.logger.info(f"   ❌ Failed: {results['failed']}")

        return results


def main():
    """CLI interface"""
    try:
        import argparse

        parser = argparse.ArgumentParser(description="SubAgent Integration Automation")
        parser.add_argument("--file", help="Integrate single file")
        parser.add_argument("--batch", type=int, help="Batch integrate N files")
        parser.add_argument("--priority", action="store_true", help="Integrate priority frameworks")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        automation = SubAgentIntegrationAutomation(project_root)

        if args.file:
            file_path = Path(args.file)
            if not file_path.is_absolute():
                file_path = project_root / "scripts" / "python" / file_path
            result = automation.integrate_framework(file_path)
            if result.get("success"):
                print(f"\n✅ Integrated: {file_path.name}")
                print(f"   Steps: {', '.join(result['steps'])}")
            else:
                print(f"\n❌ Failed: {result.get('error')}")

        elif args.batch:
            # Get frameworks from report
            report_file = project_root / "data" / "subagent_integration_report.json"
            if report_file.exists():
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)

                # Get frameworks without SubAgents
                frameworks = report.get("integration_status", {}).get("without_subagents", [])

                # Convert to Path objects
                framework_files = [
                    project_root / "scripts" / "python" / f
                    for f in frameworks[:args.batch]
                ]

                results = automation.batch_integrate(framework_files)
                print(f"\n🚀 Batch Integration Complete:")
                print(f"   Successful: {results['successful']}")
                print(f"   Already integrated: {results['already_integrated']}")
                print(f"   Failed: {results['failed']}")
            else:
                print("❌ Integration report not found. Run --analyze first.")

        elif args.priority:
            # Integrate priority frameworks
            priority_frameworks = [
                "peak_ai_orchestrator.py",
                "master_workflow_orchestrator.py",
                "ai_managed_va_orchestrator.py",
                "network_security_orchestrator.py",
                "infrastructure_orchestrator.py"
            ]

            framework_files = [
                project_root / "scripts" / "python" / f
                for f in priority_frameworks
            ]

            results = automation.batch_integrate(framework_files)
            print(f"\n🎯 Priority Integration Complete:")
            print(f"   Successful: {results['successful']}")
            print(f"   Failed: {results['failed']}")

        else:
            print("Usage:")
            print("  --file <file>     : Integrate single file")
            print("  --batch <N>       : Batch integrate N files")
            print("  --priority        : Integrate priority frameworks")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()