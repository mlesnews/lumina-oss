#!/usr/bin/env python3
"""
Explore and Map N8N Workflows
Analyzes existing N8N workflows and maps out processes.

Tags: #N8N #WORKFLOWS #MAPPING #PROCESSES
@JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Set
from collections import defaultdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ExploreN8NWorkflows")


class N8NWorkflowExplorer:
    """Explore and map N8N workflows"""

    def __init__(self):
        """Initialize explorer"""
        self.base_path = Path(__file__).parent.parent.parent
        self.n8n_config_path = self.base_path / "config" / "n8n"
        self.workflows = {}
        self.process_map = {}
        self.integrations = defaultdict(set)

    def load_workflows(self) -> Dict[str, Any]:
        """Load all N8N workflow files"""
        logger.info("=" * 80)
        logger.info("📂 LOADING N8N WORKFLOWS")
        logger.info("=" * 80)

        if not self.n8n_config_path.exists():
            logger.warning(f"⚠️  N8N config directory not found: {self.n8n_config_path}")
            return {}

        workflow_files = list(self.n8n_config_path.glob("*.json"))
        logger.info(f"Found {len(workflow_files)} workflow files")

        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow = json.load(f)
                    workflow_name = workflow_file.stem
                    self.workflows[workflow_name] = {
                        "file": str(workflow_file),
                        "data": workflow,
                        "name": workflow.get("name", workflow_name),
                        "nodes": workflow.get("nodes", []),
                        "connections": workflow.get("connections", {})
                    }
                    logger.info(f"✅ Loaded: {workflow_name}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parsing {workflow_file}: {e}")
            except Exception as e:
                logger.error(f"❌ Error loading {workflow_file}: {e}")

        logger.info(f"✅ Loaded {len(self.workflows)} workflows")
        logger.info("")
        return self.workflows

    def analyze_workflow(self, workflow_name: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single workflow"""
        analysis = {
            "name": workflow_data.get("name", workflow_name),
            "nodes": [],
            "triggers": [],
            "integrations": set(),
            "process_flow": [],
            "webhooks": [],
            "schedules": []
        }

        nodes = workflow_data.get("nodes", [])

        for node in nodes:
            node_type = node.get("type", "unknown")
            node_name = node.get("name", "unnamed")
            parameters = node.get("parameters", {})

            analysis["nodes"].append({
                "name": node_name,
                "type": node_type,
                "parameters": parameters
            })

            # Identify triggers
            if "trigger" in node_type.lower() or "webhook" in node_type.lower():
                if "webhook" in node_type.lower():
                    webhook_path = parameters.get("path", parameters.get("path", ""))
                    analysis["webhooks"].append({
                        "node": node_name,
                        "path": webhook_path,
                        "method": parameters.get("httpMethod", "POST")
                    })
                analysis["triggers"].append({
                    "node": node_name,
                    "type": node_type
                })

            # Identify schedules
            if "schedule" in node_type.lower() or "cron" in node_type.lower():
                cron = parameters.get("cron", parameters.get("rule", ""))
                analysis["schedules"].append({
                    "node": node_name,
                    "cron": cron
                })

            # Identify integrations
            if "elevenlabs" in node_type.lower() or "11labs" in node_name.lower():
                analysis["integrations"].add("11Labs")
            if "gmail" in node_type.lower():
                analysis["integrations"].add("Gmail")
            if "proton" in node_type.lower() or "proton" in node_name.lower():
                analysis["integrations"].add("ProtonMail")
            if "syphon" in node_name.lower() or "syphon" in str(parameters).lower():
                analysis["integrations"].add("SYPHON")
            if "holocron" in node_name.lower() or "holocron" in str(parameters).lower():
                analysis["integrations"].add("Holocron")

        # Convert set to list for JSON serialization
        analysis["integrations"] = list(analysis["integrations"])

        # Build process flow from connections
        connections = workflow_data.get("connections", {})
        if connections:
            analysis["process_flow"] = self.build_process_flow(nodes, connections)

        return analysis

    def build_process_flow(self, nodes: List[Dict], connections: Dict) -> List[str]:
        """Build process flow from node connections"""
        flow = []
        node_map = {node.get("name"): node for node in nodes}

        # Find starting nodes (triggers)
        start_nodes = []
        for node in nodes:
            node_name = node.get("name")
            node_type = node.get("type", "")
            if "trigger" in node_type.lower() or "webhook" in node_type.lower() or "schedule" in node_type.lower():
                start_nodes.append(node_name)

        # Build flow from start nodes
        for start_node in start_nodes:
            flow.append(f"START: {start_node}")
            self.traverse_connections(start_node, connections, node_map, flow, visited=set())

        return flow

    def traverse_connections(self, node_name: str, connections: Dict, node_map: Dict, 
                           flow: List[str], visited: Set[str], depth: int = 0):
        """Traverse workflow connections recursively"""
        if node_name in visited or depth > 20:  # Prevent infinite loops
            return

        visited.add(node_name)
        indent = "  " * depth

        if node_name in connections:
            for output_key, outputs in connections[node_name].items():
                for output in outputs:
                    # Handle different connection formats
                    target_names = []

                    if isinstance(output, list):
                        for item in output:
                            if isinstance(item, dict):
                                # Try different ways to get node name
                                if "node" in item:
                                    node_obj = item["node"]
                                    if isinstance(node_obj, dict):
                                        target_names.append(node_obj.get("name", "unknown"))
                                    else:
                                        target_names.append(str(node_obj))
                                else:
                                    target_names.append(item.get("name", str(item)))
                            elif isinstance(item, (str, int)):
                                target_names.append(str(item))
                            else:
                                target_names.append("unknown")
                    elif isinstance(output, dict):
                        if "node" in output:
                            node_obj = output["node"]
                            if isinstance(node_obj, dict):
                                target_names.append(node_obj.get("name", "unknown"))
                            else:
                                target_names.append(str(node_obj))
                        else:
                            target_names.append(output.get("name", "unknown"))
                    else:
                        target_names.append(str(output))

                    # Process each target
                    for target_name in target_names:
                        if target_name and target_name != "unknown" and target_name not in visited:
                            flow.append(f"{indent}→ {target_name}")
                            self.traverse_connections(target_name, connections, node_map, flow, visited, depth + 1)

    def map_all_processes(self) -> Dict[str, Any]:
        """Map all processes across workflows"""
        logger.info("=" * 80)
        logger.info("🗺️  MAPPING ALL PROCESSES")
        logger.info("=" * 80)

        process_map = {
            "workflows": {},
            "integrations": defaultdict(list),
            "triggers": defaultdict(list),
            "webhooks": [],
            "schedules": [],
            "process_chains": []
        }

        for workflow_name, workflow_data in self.workflows.items():
            analysis = self.analyze_workflow(workflow_name, workflow_data)
            process_map["workflows"][workflow_name] = analysis

            # Aggregate integrations
            for integration in analysis["integrations"]:
                process_map["integrations"][integration].append(workflow_name)

            # Aggregate triggers
            for trigger in analysis["triggers"]:
                process_map["triggers"][trigger["type"]].append(workflow_name)

            # Aggregate webhooks
            process_map["webhooks"].extend(analysis["webhooks"])

            # Aggregate schedules
            process_map["schedules"].extend(analysis["schedules"])

        logger.info(f"✅ Mapped {len(process_map['workflows'])} workflows")
        logger.info(f"✅ Found {len(process_map['integrations'])} integrations")
        logger.info(f"✅ Found {len(process_map['webhooks'])} webhooks")
        logger.info("")

        return process_map

    def generate_report(self, process_map: Dict[str, Any]) -> str:
        """Generate human-readable report"""
        logger.info("=" * 80)
        logger.info("📊 GENERATING REPORT")
        logger.info("=" * 80)

        report_lines = [
            "# N8N Workflows Process Map",
            "",
            f"**Total Workflows**: {len(process_map['workflows'])}",
            "",
            "## Integrations",
            ""
        ]

        for integration, workflows in process_map["integrations"].items():
            report_lines.append(f"### {integration}")
            for workflow in workflows:
                report_lines.append(f"- {workflow}")
            report_lines.append("")

        report_lines.extend([
            "## Webhooks",
            ""
        ])

        for webhook in process_map["webhooks"]:
            report_lines.append(f"- **{webhook['node']}**: `{webhook['path']}` ({webhook['method']})")

        report_lines.extend([
            "",
            "## Workflow Details",
            ""
        ])

        for workflow_name, analysis in process_map["workflows"].items():
            report_lines.extend([
                f"### {analysis['name']}",
                f"**File**: `{workflow_name}.json`",
                "",
                f"**Nodes**: {len(analysis['nodes'])}",
                f"**Integrations**: {', '.join(analysis['integrations']) if analysis['integrations'] else 'None'}",
                ""
            ])

            if analysis["triggers"]:
                report_lines.append("**Triggers**:")
                for trigger in analysis["triggers"]:
                    report_lines.append(f"- {trigger['node']} ({trigger['type']})")
                report_lines.append("")

            if analysis["process_flow"]:
                report_lines.append("**Process Flow**:")
                for step in analysis["process_flow"][:10]:  # Limit to first 10 steps
                    report_lines.append(f"  {step}")
                if len(analysis["process_flow"]) > 10:
                    report_lines.append(f"  ... ({len(analysis['process_flow']) - 10} more steps)")
                report_lines.append("")

        report = "\n".join(report_lines)
        logger.info("✅ Report generated")
        logger.info("")
        return report

    def explore_all(self) -> Dict[str, Any]:
        try:
            """Explore all workflows and generate complete map"""
            logger.info("")
            logger.info("=" * 80)
            logger.info("🔍 EXPLORING N8N WORKFLOWS")
            logger.info("=" * 80)
            logger.info("")

            # Load workflows
            self.load_workflows()

            # Map processes
            process_map = self.map_all_processes()

            # Generate report
            report = self.generate_report(process_map)

            # Save report
            report_path = self.base_path / "docs" / "n8n" / "N8N_WORKFLOWS_PROCESS_MAP.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"✅ Saved report: {report_path}")

            # Save JSON map
            map_path = self.base_path / "data" / "n8n_workflows_map.json"
            map_path.parent.mkdir(parents=True, exist_ok=True)
            with open(map_path, 'w', encoding='utf-8') as f:
                json.dump(process_map, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved map: {map_path}")

            return {
                "workflows_found": len(self.workflows),
                "process_map": process_map,
                "report": report
            }


        except Exception as e:
            self.logger.error(f"Error in explore_all: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Explore and Map N8N Workflows")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        explorer = N8NWorkflowExplorer()
        results = explorer.explore_all()

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())