#!/usr/bin/env python3
"""
JARVIS Fidelity Complete @ff Exploration & Control
Complete exploration and mapping of Fidelity Trader Dashboard with JARVIS full control

Uses @ff exploration techniques to:
- Map all UI elements and features
- Extract all functionality
- Generate JARVIS control interface
- Enable automated control of all features

Tags: #FIDELITY #@FF #EXPLORATION #JARVIS #TRIAD #COMPLETE_CONTROL
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFidelityCompleteExploration")


class JARVISFidelityCompleteExploration:
    """
    Complete @ff Exploration System for Fidelity Dashboard

    Performs comprehensive feature mapping and enables JARVIS full control
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize complete exploration system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "fidelity_exploration"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ JARVIS Fidelity Complete Exploration initialized")
        logger.info("   @ff exploration mode: ACTIVE")
        logger.info("   @TRIAD protocol: ENABLED")

    def process_snapshot_file(self, snapshot_file: Path) -> Dict[str, Any]:
        """Process snapshot file and extract all features"""
        logger.info(f"📄 Processing snapshot file: {snapshot_file}")

        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_content = f.read()

            # Parse YAML snapshot
            snapshot_data = yaml.safe_load(snapshot_content)

            feature_map = self._extract_features_from_snapshot(snapshot_data)

            logger.info(f"✅ Extracted {len(feature_map['elements'])} elements from snapshot")
            return feature_map

        except Exception as e:
            logger.error(f"❌ Failed to process snapshot: {e}", exc_info=True)
            return {}

    def _extract_features_from_snapshot(self, snapshot_data: Any) -> Dict[str, Any]:
        """Extract all features from snapshot YAML structure"""
        feature_map = {
            "extracted_at": datetime.now().isoformat(),
            "elements": [],
            "buttons": [],
            "links": [],
            "forms": [],
            "inputs": [],
            "menus": [],
            "dialogs": [],
            "trading_features": [],
            "navigation": []
        }

        def traverse_node(node, path="", depth=0):
            """Recursively traverse snapshot structure"""
            if isinstance(node, dict):
                role = node.get("role", "")
                name = node.get("name", "")
                ref = node.get("ref", "")

                if role:
                    element = {
                        "role": role,
                        "name": name,
                        "ref": ref,
                        "path": path,
                        "depth": depth
                    }
                    feature_map["elements"].append(element)

                    # Categorize
                    if role == "button":
                        feature_map["buttons"].append(element)
                        if any(kw in name.lower() for kw in ["trade", "buy", "sell", "order", "submit", "login"]):
                            feature_map["trading_features"].append(element)
                    elif role == "link":
                        feature_map["links"].append(element)
                    elif role == "form":
                        feature_map["forms"].append(element)
                    elif role in ["textbox", "combobox"]:
                        feature_map["inputs"].append(element)
                    elif role in ["menu", "menuitem"]:
                        feature_map["menus"].append(element)
                    elif role == "dialog":
                        feature_map["dialogs"].append(element)

                # Traverse children
                children = node.get("children", [])
                current_path = f"{path}/{role}" if role else path
                for child in children:
                    traverse_node(child, current_path, depth + 1)

            elif isinstance(node, list):
                for item in node:
                    traverse_node(item, path, depth)

        traverse_node(snapshot_data)

        return feature_map

    def generate_jarvis_control_interface(self, feature_map: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete JARVIS control interface"""
        logger.info("🔧 Generating JARVIS Control Interface...")

        control_interface = {
            "generated_at": datetime.now().isoformat(),
            "dashboard_url": "https://digital.fidelity.com/ftgw/digital/trader-dashboard",
            "control_methods": {},
            "feature_controls": {},
            "mcp_commands": []
        }

        # Generate controls for all buttons
        for button in feature_map.get("buttons", []):
            name = button.get("name", "").lower().replace(" ", "_").replace("-", "_")
            if name:
                control_interface["feature_controls"][name] = {
                    "type": "button",
                    "name": button.get("name"),
                    "ref": button.get("ref"),
                    "control_method": f"jarvis_click_{name}",
                    "mcp_command": "browser_click",
                    "description": f"Click {button.get('name')} button"
                }

                control_interface["mcp_commands"].append({
                    "command": "browser_click",
                    "element": button.get("name"),
                    "ref": button.get("ref"),
                    "description": f"Click {button.get('name')}"
                })

        # Generate controls for forms
        for form in feature_map.get("forms", []):
            form_id = form.get("ref", "").split("-")[-1] if form.get("ref") else "form"
            control_interface["feature_controls"][f"form_{form_id}"] = {
                "type": "form",
                "ref": form.get("ref"),
                "control_method": f"jarvis_fill_form_{form_id}",
                "mcp_command": "browser_type",
                "description": f"Fill form {form_id}"
            }

        # Generate controls for inputs
        for input_elem in feature_map.get("inputs", []):
            name = input_elem.get("name", "").lower().replace(" ", "_")
            if name:
                control_interface["feature_controls"][f"input_{name}"] = {
                    "type": "input",
                    "name": input_elem.get("name"),
                    "ref": input_elem.get("ref"),
                    "control_method": f"jarvis_type_{name}",
                    "mcp_command": "browser_type",
                    "description": f"Type into {input_elem.get('name')} field"
                }

        logger.info(f"✅ Generated {len(control_interface['feature_controls'])} control methods")
        logger.info(f"   MCP commands: {len(control_interface['mcp_commands'])}")

        return control_interface

    def create_exploration_report(self, feature_map: Dict[str, Any], 
                                 control_interface: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive exploration report"""
        logger.info("📊 Creating exploration report...")

        report = {
            "generated_at": datetime.now().isoformat(),
            "exploration_type": "@ff_full_feature_mapping",
            "dashboard_url": "https://digital.fidelity.com/ftgw/digital/trader-dashboard",
            "summary": {
                "total_elements": len(feature_map.get("elements", [])),
                "buttons": len(feature_map.get("buttons", [])),
                "forms": len(feature_map.get("forms", [])),
                "inputs": len(feature_map.get("inputs", [])),
                "menus": len(feature_map.get("menus", [])),
                "trading_features": len(feature_map.get("trading_features", [])),
                "control_methods": len(control_interface.get("feature_controls", {}))
            },
            "feature_categories": {
                "trading": feature_map.get("trading_features", []),
                "navigation": feature_map.get("links", []),
                "forms": feature_map.get("forms", []),
                "menus": feature_map.get("menus", [])
            },
            "jarvis_control": control_interface,
            "network_analysis": {
                "api_endpoints": [],
                "data_endpoints": []
            }
        }

        logger.info("✅ Exploration report created")
        logger.info(f"   Total elements: {report['summary']['total_elements']}")
        logger.info(f"   Control methods: {report['summary']['control_methods']}")

        return report

    def save_exploration(self, report: Dict[str, Any]) -> Path:
        try:
            """Save complete exploration results"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"fidelity_complete_exploration_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Complete exploration saved to: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in save_exploration: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Fidelity Complete Exploration")
        parser.add_argument("--snapshot", type=str, help="Snapshot file path")
        parser.add_argument("--control", action="store_true", help="Generate control interface")
        parser.add_argument("--report", action="store_true", help="Generate exploration report")

        args = parser.parse_args()

        explorer = JARVISFidelityCompleteExploration()

        # Process snapshot if provided
        feature_map = {}
        if args.snapshot:
            snapshot_file = Path(args.snapshot)
            feature_map = explorer.process_snapshot_file(snapshot_file)
        else:
            # Use latest snapshot from browser logs
            browser_logs = Path.home() / ".cursor" / "browser-logs"
            snapshot_files = sorted(browser_logs.glob("snapshot-*.log"), reverse=True)
            if snapshot_files:
                logger.info(f"Using latest snapshot: {snapshot_files[0]}")
                feature_map = explorer.process_snapshot_file(snapshot_files[0])
            else:
                logger.warning("No snapshot file found. Capture one with browser_snapshot() first.")
                return

        if args.control or args.report:
            control_interface = explorer.generate_jarvis_control_interface(feature_map)

            if args.report:
                report = explorer.create_exploration_report(feature_map, control_interface)
                output_file = explorer.save_exploration(report)
                print(f"\n✅ Complete exploration report saved to: {output_file}")
            else:
                control_file = explorer.output_dir / "jarvis_control_interface.json"
                with open(control_file, 'w', encoding='utf-8') as f:
                    json.dump(control_interface, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Control interface saved to: {control_file}")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()