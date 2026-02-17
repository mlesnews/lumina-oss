#!/usr/bin/env python3
"""
JARVIS Fidelity Dashboard Feature Mapper
Processes browser snapshots and creates comprehensive feature map

Tags: #FIDELITY #FEATURE_MAPPING #@FF #JARVIS
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

logger = get_logger("JARVISFidelityFeatureMapper")


class FidelityFeatureMapper:
    """
    Maps Fidelity Dashboard features from browser snapshots
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize mapper"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "fidelity_exploration"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Fidelity Feature Mapper initialized")

    def process_snapshot(self, snapshot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process browser snapshot and extract features"""
        logger.info("Processing browser snapshot...")

        feature_map = {
            "processed_at": datetime.now().isoformat(),
            "url": snapshot_data.get("page_url", ""),
            "title": snapshot_data.get("page_title", ""),
            "elements": [],
            "buttons": [],
            "links": [],
            "forms": [],
            "menus": [],
            "inputs": [],
            "dialogs": []
        }

        # Parse snapshot YAML structure
        snapshot = snapshot_data.get("page_snapshot", "")
        if snapshot:
            # Extract elements by role
            elements = self._parse_snapshot_yaml(snapshot)
            feature_map["elements"] = elements

            # Categorize elements
            for elem in elements:
                role = elem.get("role", "")
                if role == "button":
                    feature_map["buttons"].append(elem)
                elif role == "link":
                    feature_map["links"].append(elem)
                elif role == "form":
                    feature_map["forms"].append(elem)
                elif role in ["menu", "menuitem"]:
                    feature_map["menus"].append(elem)
                elif role == "textbox" or role == "combobox":
                    feature_map["inputs"].append(elem)
                elif role == "dialog":
                    feature_map["dialogs"].append(elem)

        logger.info(f"✅ Processed snapshot: {len(feature_map['elements'])} elements found")
        logger.info(f"   Buttons: {len(feature_map['buttons'])}")
        logger.info(f"   Links: {len(feature_map['links'])}")
        logger.info(f"   Forms: {len(feature_map['forms'])}")
        logger.info(f"   Menus: {len(feature_map['menus'])}")
        logger.info(f"   Inputs: {len(feature_map['inputs'])}")
        logger.info(f"   Dialogs: {len(feature_map['dialogs'])}")

        return feature_map

    def _parse_snapshot_yaml(self, snapshot_yaml: str) -> List[Dict[str, Any]]:
        """Parse snapshot YAML and extract elements"""
        elements = []

        try:
            # Parse YAML structure
            data = yaml.safe_load(snapshot_yaml)

            def extract_elements(node, parent_path=""):
                """Recursively extract elements from YAML structure"""
                if isinstance(node, dict):
                    role = node.get("role", "")
                    name = node.get("name", "")
                    ref = node.get("ref", "")

                    if role:
                        elem = {
                            "role": role,
                            "name": name,
                            "ref": ref,
                            "path": parent_path
                        }
                        elements.append(elem)

                    children = node.get("children", [])
                    current_path = f"{parent_path}/{role}" if role else parent_path
                    for child in children:
                        extract_elements(child, current_path)
                elif isinstance(node, list):
                    for item in node:
                        extract_elements(item, parent_path)

            extract_elements(data)

        except Exception as e:
            logger.warning(f"Could not parse YAML snapshot: {e}")

        return elements

    def generate_control_map(self, feature_map: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JARVIS control map from feature map"""
        logger.info("Generating JARVIS control map...")

        control_map = {
            "generated_at": datetime.now().isoformat(),
            "dashboard_url": feature_map.get("url", ""),
            "control_methods": {},
            "feature_controls": {}
        }

        # Map buttons to control methods
        for button in feature_map.get("buttons", []):
            name = button.get("name", "").lower().replace(" ", "_")
            if name:
                control_map["feature_controls"][name] = {
                    "type": "button",
                    "name": button.get("name"),
                    "ref": button.get("ref"),
                    "control_method": f"click_{name}",
                    "action": "browser_click"
                }

        # Map forms to control methods
        for form in feature_map.get("forms", []):
            form_id = form.get("ref", "").split("-")[-1] if form.get("ref") else "form"
            control_map["feature_controls"][f"form_{form_id}"] = {
                "type": "form",
                "ref": form.get("ref"),
                "control_method": f"fill_form_{form_id}",
                "action": "browser_type"
            }

        # Map inputs to control methods
        for input_elem in feature_map.get("inputs", []):
            name = input_elem.get("name", "").lower().replace(" ", "_")
            if name:
                control_map["feature_controls"][f"input_{name}"] = {
                    "type": "input",
                    "name": input_elem.get("name"),
                    "ref": input_elem.get("ref"),
                    "control_method": f"type_{name}",
                    "action": "browser_type"
                }

        logger.info(f"✅ Generated control map: {len(control_map['feature_controls'])} controls")

        return control_map

    def save_feature_map(self, feature_map: Dict[str, Any], filename: Optional[str] = None) -> Path:
        try:
            """Save feature map to JSON"""
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fidelity_feature_map_{timestamp}.json"

            output_file = self.output_dir / filename

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(feature_map, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Feature map saved to: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in save_feature_map: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Fidelity Feature Mapper")
        parser.add_argument("--snapshot", type=str, help="Snapshot YAML file or data")
        parser.add_argument("--control", action="store_true", help="Generate control map")

        args = parser.parse_args()

        mapper = FidelityFeatureMapper()

        # For now, create a template feature map
        # In production, this would process actual browser snapshots
        template_map = {
            "processed_at": datetime.now().isoformat(),
            "url": "https://digital.fidelity.com/ftgw/digital/trader-dashboard",
            "title": "Fidelity Trader Dashboard",
            "note": "This is a template. Run with browser snapshots for live mapping."
        }

        feature_map = mapper.process_snapshot(template_map)

        if args.control:
            control_map = mapper.generate_control_map(feature_map)
            control_file = mapper.output_dir / "control_map.json"
            with open(control_file, 'w', encoding='utf-8') as f:
                json.dump(control_map, f, indent=2, ensure_ascii=False)
            print(f"✅ Control map saved to: {control_file}")

        output_file = mapper.save_feature_map(feature_map)
        print(f"✅ Feature map saved to: {output_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()