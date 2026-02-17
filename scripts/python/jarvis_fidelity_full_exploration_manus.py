#!/usr/bin/env python3
"""
JARVIS Fidelity Full Exploration with @MANUS Control
Complete @ff exploration including keyboard shortcuts and full @MANUS control interface

Features:
- Comprehensive feature mapping (@ff exploration)
- Keyboard shortcut extraction and documentation
- Full @MANUS control interface generation
- Network API endpoint discovery
- Complete JARVIS automation control

Tags: #FIDELITY #@FF #@MANUS #KEYBOARD_SHORTCUTS #JARVIS #COMPLETE_CONTROL
"""

import sys
import json
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
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

logger = get_logger("JARVISFidelityFullExplorationMANUS")


class KeyboardShortcut:
    """Represents a keyboard shortcut"""
    def __init__(self, keys: str, action: str, description: str = "", context: str = ""):
        self.keys = keys
        self.action = action
        self.description = description
        self.context = context

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "keys": self.keys,
            "action": self.action,
            "description": self.description,
            "context": self.context
        }


class JARVISFidelityFullExplorationMANUS:
    """
    Complete Fidelity Dashboard Exploration with @MANUS Control

    Performs comprehensive @ff exploration including:
    - All UI elements and features
    - Keyboard shortcuts
    - @MANUS control interface
    - Network API endpoints
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize full exploration system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "fidelity_exploration"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Known Fidelity keyboard shortcuts (will be enhanced from exploration)
        self.known_shortcuts = self._initialize_known_shortcuts()

        logger.info("=" * 70)
        logger.info("🎮 JARVIS FIDELITY FULL EXPLORATION WITH @MANUS")
        logger.info("=" * 70)
        logger.info("   @ff exploration: ACTIVE")
        logger.info("   Keyboard shortcuts: ENABLED")
        logger.info("   @MANUS control: ENABLED")
        logger.info("")

    def _initialize_known_shortcuts(self) -> List[KeyboardShortcut]:
        """Initialize known Fidelity keyboard shortcuts"""
        shortcuts = [
            KeyboardShortcut("Ctrl+K", "Quick Search", "Open quick search dialog", "Global"),
            KeyboardShortcut("Ctrl+/", "Help", "Open help menu", "Global"),
            KeyboardShortcut("Ctrl+Shift+P", "Command Palette", "Open command palette", "Global"),
            KeyboardShortcut("F5", "Refresh", "Refresh current view", "Global"),
            KeyboardShortcut("Ctrl+R", "Refresh", "Refresh current view", "Global"),
            KeyboardShortcut("Esc", "Close/Cancel", "Close dialog or cancel action", "Global"),
            KeyboardShortcut("Enter", "Submit/Confirm", "Submit form or confirm action", "Forms"),
            KeyboardShortcut("Tab", "Navigate", "Navigate to next field", "Forms"),
            KeyboardShortcut("Shift+Tab", "Navigate Back", "Navigate to previous field", "Forms"),
            KeyboardShortcut("Ctrl+Enter", "Submit Order", "Submit trading order", "Trading"),
            KeyboardShortcut("Ctrl+B", "Buy", "Quick buy action", "Trading"),
            KeyboardShortcut("Ctrl+S", "Sell", "Quick sell action", "Trading"),
            KeyboardShortcut("Ctrl+L", "Limit Order", "Open limit order dialog", "Trading"),
            KeyboardShortcut("Ctrl+M", "Market Order", "Open market order dialog", "Trading"),
            KeyboardShortcut("Ctrl+O", "Options Chain", "Open options chain", "Trading"),
            KeyboardShortcut("Ctrl+W", "Watchlist", "Open watchlist", "Trading"),
            KeyboardShortcut("Ctrl+P", "Positions", "View positions", "Trading"),
            KeyboardShortcut("Ctrl+H", "Order History", "View order history", "Trading"),
            KeyboardShortcut("Ctrl+A", "Account Summary", "View account summary", "Account"),
            KeyboardShortcut("Ctrl+T", "Trade Ticket", "Open trade ticket", "Trading"),
            KeyboardShortcut("Ctrl+C", "Charts", "Open charts", "Charts"),
            KeyboardShortcut("Ctrl+I", "Indicators", "Open indicators menu", "Charts"),
            KeyboardShortcut("Ctrl+D", "Drawing Tools", "Open drawing tools", "Charts"),
            KeyboardShortcut("Ctrl+Shift+S", "Save Chart", "Save chart layout", "Charts"),
            KeyboardShortcut("Ctrl+Shift+L", "Load Chart", "Load chart layout", "Charts"),
            KeyboardShortcut("Ctrl+Plus", "Zoom In", "Zoom in on chart", "Charts"),
            KeyboardShortcut("Ctrl+Minus", "Zoom Out", "Zoom out on chart", "Charts"),
            KeyboardShortcut("Ctrl+0", "Reset Zoom", "Reset chart zoom", "Charts"),
            KeyboardShortcut("Arrow Keys", "Navigate", "Navigate through lists/tables", "Global"),
            KeyboardShortcut("Page Up", "Scroll Up", "Scroll up in list", "Lists"),
            KeyboardShortcut("Page Down", "Scroll Down", "Scroll down in list", "Lists"),
            KeyboardShortcut("Home", "Top", "Jump to top of list", "Lists"),
            KeyboardShortcut("End", "Bottom", "Jump to bottom of list", "Lists"),
        ]
        return shortcuts

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
            "navigation": [],
            "charts": [],
            "watchlists": [],
            "order_forms": [],
            "keyboard_shortcuts": []
        }

        # Trading feature keywords
        trading_keywords = [
            "trade", "buy", "sell", "order", "submit", "limit", "market", "stop",
            "options", "chain", "strategy", "quick", "ticket", "position", "portfolio"
        ]

        # Chart keywords
        chart_keywords = [
            "chart", "candle", "line", "bar", "indicator", "drawing", "zoom", "timeframe"
        ]

        def traverse_node(node, path="", depth=0):
            """Recursively traverse snapshot structure"""
            if isinstance(node, dict):
                role = node.get("role", "")
                name = node.get("name", "")
                ref = node.get("ref", "")
                description = node.get("description", "")
                value = node.get("value", "")

                # Extract keyboard shortcuts from aria-label, title, or description
                shortcut_keys = self._extract_shortcut_from_text(name + " " + description)

                if role:
                    element = {
                        "role": role,
                        "name": name,
                        "ref": ref,
                        "path": path,
                        "depth": depth,
                        "description": description,
                        "value": value,
                        "shortcut": shortcut_keys
                    }
                    feature_map["elements"].append(element)

                    # Categorize
                    if role == "button":
                        feature_map["buttons"].append(element)
                        name_lower = name.lower()
                        if any(kw in name_lower for kw in trading_keywords):
                            feature_map["trading_features"].append(element)
                        if any(kw in name_lower for kw in ["order", "submit", "trade"]):
                            feature_map["order_forms"].append(element)
                    elif role == "link":
                        feature_map["links"].append(element)
                    elif role == "form":
                        feature_map["forms"].append(element)
                    elif role in ["textbox", "combobox", "spinbutton"]:
                        feature_map["inputs"].append(element)
                    elif role in ["menu", "menuitem"]:
                        feature_map["menus"].append(element)
                    elif role == "dialog":
                        feature_map["dialogs"].append(element)
                    elif any(kw in name.lower() for kw in chart_keywords):
                        feature_map["charts"].append(element)
                    elif "watchlist" in name.lower():
                        feature_map["watchlists"].append(element)

                # Traverse children
                children = node.get("children", [])
                current_path = f"{path}/{role}" if role else path
                for child in children:
                    traverse_node(child, current_path, depth + 1)

            elif isinstance(node, list):
                for item in node:
                    traverse_node(item, path, depth)

        traverse_node(snapshot_data)

        # Add known shortcuts
        feature_map["keyboard_shortcuts"] = [s.to_dict() for s in self.known_shortcuts]

        return feature_map

    def _extract_shortcut_from_text(self, text: str) -> Optional[str]:
        """Extract keyboard shortcut notation from text"""
        if not text:
            return None

        # Patterns for keyboard shortcuts
        patterns = [
            r'\(([A-Za-z]\+?)+\)',  # (Ctrl+K), (Alt+F)
            r'\[([A-Za-z]\+?)+\]',  # [Ctrl+K], [Alt+F]
            r'([A-Za-z]\+)+[A-Za-z]',  # Ctrl+K, Alt+F
            r'Shortcut:\s*([A-Za-z]\+?)+',  # Shortcut: Ctrl+K
            r'Key:\s*([A-Za-z]\+?)+',  # Key: Ctrl+K
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.lastindex else match.group(0)

        return None

    def process_network_requests(self, network_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            """Process network requests to discover API endpoints"""
            logger.info(f"🌐 Processing {len(network_data)} network requests...")

            api_endpoints = {
                "trading": [],
                "market_data": [],
                "account": [],
                "positions": [],
                "orders": [],
                "watchlists": [],
                "charts": [],
                "other": []
            }

            for request in network_data:
                url = request.get("url", "")
                method = request.get("method", "GET")

                endpoint_info = {
                    "url": url,
                    "method": method,
                    "headers": request.get("headers", {}),
                    "payload": request.get("payload", {})
                }

                # Categorize endpoints
                url_lower = url.lower()
                if any(kw in url_lower for kw in ["trade", "order", "buy", "sell", "submit"]):
                    api_endpoints["trading"].append(endpoint_info)
                elif any(kw in url_lower for kw in ["quote", "price", "market", "symbol"]):
                    api_endpoints["market_data"].append(endpoint_info)
                elif any(kw in url_lower for kw in ["account", "balance", "summary"]):
                    api_endpoints["account"].append(endpoint_info)
                elif any(kw in url_lower for kw in ["position", "holdings"]):
                    api_endpoints["positions"].append(endpoint_info)
                elif any(kw in url_lower for kw in ["order", "execution"]):
                    api_endpoints["orders"].append(endpoint_info)
                elif any(kw in url_lower for kw in ["watchlist", "alert"]):
                    api_endpoints["watchlists"].append(endpoint_info)
                elif any(kw in url_lower for kw in ["chart", "candle", "history"]):
                    api_endpoints["charts"].append(endpoint_info)
                else:
                    api_endpoints["other"].append(endpoint_info)

            logger.info(f"✅ Discovered {sum(len(v) for v in api_endpoints.values())} API endpoints")
            return api_endpoints

        except Exception as e:
            self.logger.error(f"Error in process_network_requests: {e}", exc_info=True)
            raise
    def generate_manus_control_interface(self, feature_map: Dict[str, Any], 
                                        api_endpoints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete @MANUS control interface"""
        logger.info("🔧 Generating @MANUS Control Interface...")

        manus_control = {
            "generated_at": datetime.now().isoformat(),
            "dashboard_url": "https://digital.fidelity.com/ftgw/digital/trader-dashboard",
            "control_areas": {
                "trading": {},
                "charts": {},
                "account": {},
                "watchlists": {},
                "navigation": {},
                "forms": {},
                "keyboard_shortcuts": {}
            },
            "api_endpoints": api_endpoints,
            "control_methods": {}
        }

        # Generate trading controls
        for feature in feature_map.get("trading_features", []):
            name = self._sanitize_name(feature.get("name", ""))
            if name:
                manus_control["control_areas"]["trading"][name] = {
                    "type": feature.get("role"),
                    "name": feature.get("name"),
                    "ref": feature.get("ref"),
                    "control_method": f"manus_trade_{name}",
                    "mcp_command": "browser_click",
                    "keyboard_shortcut": feature.get("shortcut"),
                    "description": feature.get("description", f"Control {feature.get('name')}")
                }

        # Generate chart controls
        for feature in feature_map.get("charts", []):
            name = self._sanitize_name(feature.get("name", ""))
            if name:
                manus_control["control_areas"]["charts"][name] = {
                    "type": feature.get("role"),
                    "name": feature.get("name"),
                    "ref": feature.get("ref"),
                    "control_method": f"manus_chart_{name}",
                    "mcp_command": "browser_click",
                    "keyboard_shortcut": feature.get("shortcut"),
                    "description": feature.get("description", f"Control {feature.get('name')}")
                }

        # Generate form controls
        for form in feature_map.get("forms", []):
            form_id = form.get("ref", "").split("-")[-1] if form.get("ref") else "form"
            manus_control["control_areas"]["forms"][f"form_{form_id}"] = {
                "type": "form",
                "ref": form.get("ref"),
                "control_method": f"manus_fill_form_{form_id}",
                "mcp_command": "browser_type",
                "description": f"Fill form {form_id}"
            }

        # Generate input controls
        for input_elem in feature_map.get("inputs", []):
            name = self._sanitize_name(input_elem.get("name", ""))
            if name:
                manus_control["control_areas"]["forms"][f"input_{name}"] = {
                    "type": "input",
                    "name": input_elem.get("name"),
                    "ref": input_elem.get("ref"),
                    "control_method": f"manus_type_{name}",
                    "mcp_command": "browser_type",
                    "keyboard_shortcut": input_elem.get("shortcut"),
                    "description": f"Type into {input_elem.get('name')} field"
                }

        # Generate navigation controls
        for link in feature_map.get("links", []):
            name = self._sanitize_name(link.get("name", ""))
            if name:
                manus_control["control_areas"]["navigation"][name] = {
                    "type": "link",
                    "name": link.get("name"),
                    "ref": link.get("ref"),
                    "control_method": f"manus_navigate_{name}",
                    "mcp_command": "browser_click",
                    "description": f"Navigate to {link.get('name')}"
                }

        # Add keyboard shortcuts
        for shortcut in feature_map.get("keyboard_shortcuts", []):
            keys = shortcut.get("keys", "")
            action = shortcut.get("action", "")
            if keys and action:
                shortcut_id = self._sanitize_name(f"{keys}_{action}")
                manus_control["control_areas"]["keyboard_shortcuts"][shortcut_id] = {
                    "keys": keys,
                    "action": action,
                    "context": shortcut.get("context", ""),
                    "description": shortcut.get("description", ""),
                    "control_method": f"manus_keyboard_{shortcut_id}",
                    "mcp_command": "browser_press_key",
                    "description": f"Execute keyboard shortcut: {keys} - {action}"
                }

        # Generate unified control methods
        for area_name, area_controls in manus_control["control_areas"].items():
            for control_name, control_info in area_controls.items():
                method_name = control_info.get("control_method", "")
                if method_name:
                    manus_control["control_methods"][method_name] = control_info

        logger.info(f"✅ Generated {len(manus_control['control_methods'])} @MANUS control methods")
        logger.info(f"   Trading: {len(manus_control['control_areas']['trading'])}")
        logger.info(f"   Charts: {len(manus_control['control_areas']['charts'])}")
        logger.info(f"   Forms: {len(manus_control['control_areas']['forms'])}")
        logger.info(f"   Navigation: {len(manus_control['control_areas']['navigation'])}")
        logger.info(f"   Keyboard Shortcuts: {len(manus_control['control_areas']['keyboard_shortcuts'])}")

        return manus_control

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use in method names"""
        if not name:
            return ""
        # Remove special characters, replace spaces with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        return sanitized.lower()

    def create_comprehensive_report(self, feature_map: Dict[str, Any],
                                   manus_control: Dict[str, Any],
                                   api_endpoints: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive exploration report"""
        logger.info("📊 Creating comprehensive exploration report...")

        report = {
            "generated_at": datetime.now().isoformat(),
            "exploration_type": "@ff_full_feature_mapping_with_manus",
            "dashboard_url": "https://digital.fidelity.com/ftgw/digital/trader-dashboard",
            "summary": {
                "total_elements": len(feature_map.get("elements", [])),
                "buttons": len(feature_map.get("buttons", [])),
                "forms": len(feature_map.get("forms", [])),
                "inputs": len(feature_map.get("inputs", [])),
                "menus": len(feature_map.get("menus", [])),
                "trading_features": len(feature_map.get("trading_features", [])),
                "charts": len(feature_map.get("charts", [])),
                "watchlists": len(feature_map.get("watchlists", [])),
                "order_forms": len(feature_map.get("order_forms", [])),
                "keyboard_shortcuts": len(feature_map.get("keyboard_shortcuts", [])),
                "manus_control_methods": len(manus_control.get("control_methods", {})),
                "api_endpoints": sum(len(v) for v in api_endpoints.values())
            },
            "feature_categories": {
                "trading": feature_map.get("trading_features", []),
                "charts": feature_map.get("charts", []),
                "watchlists": feature_map.get("watchlists", []),
                "order_forms": feature_map.get("order_forms", []),
                "navigation": feature_map.get("links", []),
                "forms": feature_map.get("forms", []),
                "menus": feature_map.get("menus", [])
            },
            "keyboard_shortcuts": {
                "all_shortcuts": feature_map.get("keyboard_shortcuts", []),
                "by_context": self._organize_shortcuts_by_context(feature_map.get("keyboard_shortcuts", []))
            },
            "manus_control": manus_control,
            "api_endpoints": api_endpoints
        }

        logger.info("✅ Comprehensive report created")
        logger.info(f"   Total elements: {report['summary']['total_elements']}")
        logger.info(f"   Control methods: {report['summary']['manus_control_methods']}")
        logger.info(f"   Keyboard shortcuts: {report['summary']['keyboard_shortcuts']}")
        logger.info(f"   API endpoints: {report['summary']['api_endpoints']}")

        return report

    def _organize_shortcuts_by_context(self, shortcuts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize shortcuts by context"""
        organized = {}
        for shortcut in shortcuts:
            context = shortcut.get("context", "Global")
            if context not in organized:
                organized[context] = []
            organized[context].append(shortcut)
        return organized

    def save_exploration(self, report: Dict[str, Any]) -> Path:
        try:
            """Save complete exploration results"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"fidelity_full_exploration_manus_{timestamp}.json"

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

        parser = argparse.ArgumentParser(description="JARVIS Fidelity Full Exploration with @MANUS")
        parser.add_argument("--snapshot", type=str, help="Snapshot file path")
        parser.add_argument("--network", type=str, help="Network requests JSON file path")
        parser.add_argument("--full", action="store_true", help="Run full exploration")

        args = parser.parse_args()

        explorer = JARVISFidelityFullExplorationMANUS()

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

        # Process network requests if provided
        api_endpoints = {}
        if args.network:
            network_file = Path(args.network)
            with open(network_file, 'r', encoding='utf-8') as f:
                network_data = json.load(f)
            api_endpoints = explorer.process_network_requests(network_data)
        else:
            # Initialize empty API endpoints
            api_endpoints = {
                "trading": [],
                "market_data": [],
                "account": [],
                "positions": [],
                "orders": [],
                "watchlists": [],
                "charts": [],
                "other": []
            }

        # Generate @MANUS control interface
        manus_control = explorer.generate_manus_control_interface(feature_map, api_endpoints)

        # Create comprehensive report
        report = explorer.create_comprehensive_report(feature_map, manus_control, api_endpoints)

        # Save exploration
        output_file = explorer.save_exploration(report)
        print(f"\n✅ Full exploration with @MANUS control saved to: {output_file}")
        print(f"   Total elements: {report['summary']['total_elements']}")
        print(f"   @MANUS control methods: {report['summary']['manus_control_methods']}")
        print(f"   Keyboard shortcuts: {report['summary']['keyboard_shortcuts']}")
        print(f"   API endpoints: {report['summary']['api_endpoints']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()