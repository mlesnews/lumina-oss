#!/usr/bin/env python3
"""
Homelab Unified Interface with Automatic Fallback

Unified interface that automatically:
- Chooses the best option from overlaps
- Falls back to alternatives if primary fails
- Provides seamless access to all homelab resources

Tags: #HOMELAB #UNIFIED #FALLBACK #PRIORITIZATION @JARVIS @LUMINA
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.homelab_control_explorer import HomelabControlExplorer

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_unified_interface")


class FallbackExecutor:
    """Executes operations with automatic fallback"""

    def __init__(self, fallback_chains: Dict[str, Dict]):
        self.fallback_chains = fallback_chains

    def execute_with_fallback(
        self, operation_type: str, operation_key: str, executor_func: Callable, *args, **kwargs
    ) -> Dict[str, Any]:
        """Execute operation with automatic fallback"""
        # Find fallback chain
        chain_key = None
        for key, chain_data in self.fallback_chains.items():
            if chain_data["category"] == operation_type:
                # Check if operation_key matches
                if operation_key.lower() in key.lower():
                    chain_key = key
                    break

        if not chain_key:
            # No fallback chain, try direct execution
            try:
                result = executor_func(*args, **kwargs)
                return {"success": True, "result": result, "used": "direct", "attempts": 1}
            except Exception as e:
                return {"success": False, "error": str(e), "attempts": 1}

        chain = self.fallback_chains[chain_key]["chain"]
        last_error = None

        # Try each option in priority order
        for i, option in enumerate(chain, 1):
            try:
                logger.info(
                    f"Attempting {operation_type} with option {i}/{len(chain)}: {option.get('reason')}"
                )
                result = executor_func(option["item"], *args, **kwargs)
                return {
                    "success": True,
                    "result": result,
                    "used": f"fallback_chain_option_{i}",
                    "priority": option["priority"],
                    "attempts": i,
                    "fallback_chain": chain_key,
                }
            except Exception as e:
                last_error = e
                logger.warning(f"Option {i} failed: {e}, trying next...")
                continue

        # All options failed
        return {
            "success": False,
            "error": str(last_error) if last_error else "All options failed",
            "attempts": len(chain),
            "fallback_chain": chain_key,
        }


class UnifiedHomelabInterface:
    """Unified interface with automatic fallback"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.control_explorer = HomelabControlExplorer()
        self.fallback_chains: Dict[str, Dict] = {}
        self.fallback_executor: Optional[FallbackExecutor] = None
        self._load_fallback_chains()

    def _load_fallback_chains(self):
        """Load fallback chains"""
        overlap_dir = project_root / "data" / "homelab_overlap_analysis"
        overlap_files = sorted(overlap_dir.glob("overlap_analysis_*.json"), reverse=True)

        if overlap_files:
            with open(overlap_files[0], encoding="utf-8") as f:
                analysis = json.load(f)
                self.fallback_chains = analysis.get("fallback_chains", {})
                self.fallback_executor = FallbackExecutor(self.fallback_chains)
                logger.info(f"Loaded {len(self.fallback_chains)} fallback chains")

    def execute_command(
        self, command_name: str, device_id: str = None, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute command with fallback"""
        if not self.fallback_executor:
            # No fallback chains, use direct execution
            return self.control_explorer.execute_command_by_name(
                device_id or "local_Millennium-Falcon", command_name, parameters
            )

        def executor(item):
            cmd = item.get("command", {})
            cmd_id = cmd.get("command_id")
            return self.control_explorer.execute_command(cmd_id, parameters)

        return self.fallback_executor.execute_with_fallback("command", command_name, executor)

    def call_api(
        self, api_name: str, device_id: str = None, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Call API with fallback"""
        if not self.fallback_executor:
            return self.control_explorer.call_api_by_name(
                device_id or "local_Millennium-Falcon", api_name, parameters
            )

        def executor(item):
            api = item.get("api", {})
            endpoint_id = api.get("endpoint_id")
            return self.control_explorer.test_api_endpoint(endpoint_id, parameters)

        return self.fallback_executor.execute_with_fallback("api", api_name, executor)

    def get_best_option(self, category: str, operation_key: str) -> Optional[Dict[str, Any]]:
        """Get the best option for an operation"""
        for key, chain_data in self.fallback_chains.items():
            if chain_data["category"] == category:
                if operation_key.lower() in key.lower():
                    chain = chain_data["chain"]
                    if chain:
                        return chain[0]["item"]  # Primary option

        return None

    def get_fallback_options(self, category: str, operation_key: str) -> List[Dict[str, Any]]:
        """Get fallback options for an operation"""
        for key, chain_data in self.fallback_chains.items():
            if chain_data["category"] == category:
                if operation_key.lower() in key.lower():
                    chain = chain_data["chain"]
                    if len(chain) > 1:
                        return [item["item"] for item in chain[1:]]  # Skip primary

        return []

    def list_prioritized_resources(self, category: str = None) -> Dict[str, Any]:
        """List all resources with prioritization"""
        resources = {
            "commands": [],
            "apis": [],
            "services": [],
            "applications": [],
            "frameworks": [],
        }

        for key, chain_data in self.fallback_chains.items():
            cat = chain_data["category"]
            if category and cat != category:
                continue

            chain = chain_data["chain"]
            if chain:
                primary = chain[0]["item"]
                fallbacks = [item["item"] for item in chain[1:]]

                resources[cat].append(
                    {
                        "key": key,
                        "primary": primary,
                        "fallbacks": fallbacks,
                        "reason": chain_data.get("reason", ""),
                    }
                )

        return resources

    def generate_prioritization_report(self) -> str:
        """Generate prioritization report"""
        report = []
        report.append("=" * 80)
        report.append("HOMELAB PRIORITIZATION AND FALLBACK REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total Fallback Chains: {len(self.fallback_chains)}")
        report.append("")

        # Group by category
        by_category = {}
        for key, chain_data in self.fallback_chains.items():
            cat = chain_data["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((key, chain_data))

        for category, items in sorted(by_category.items()):
            report.append(f"{category.upper()} ({len(items)} overlaps)")
            report.append("-" * 80)

            for key, chain_data in items[:10]:  # Show first 10
                chain = chain_data["chain"]
                if chain:
                    primary = chain[0]["item"]
                    report.append(f"  {key}")
                    report.append(f"    Primary: {self._get_item_name(primary, category)}")
                    report.append(f"    Reason: {chain_data.get('reason', 'N/A')}")
                    if len(chain) > 1:
                        report.append(f"    Fallbacks: {len(chain) - 1}")
                        for i, fallback in enumerate(chain[1:3], 1):  # Show first 2 fallbacks
                            report.append(
                                f"      {i}. {self._get_item_name(fallback['item'], category)}"
                            )
                    report.append("")

            if len(items) > 10:
                report.append(f"    ... and {len(items) - 10} more")
                report.append("")

        report.append("=" * 80)
        return "\n".join(report)

    def _get_item_name(self, item: Dict, category: str) -> str:
        """Get display name for item"""
        if category == "command":
            return item.get("command", {}).get("name", "Unknown")
        elif category == "api":
            return item.get("api", {}).get("name", "Unknown")
        elif category == "service":
            return item.get("service", {}).get("name", "Unknown")
        elif category == "application":
            return item.get("application", {}).get("name", "Unknown")
        elif category == "framework":
            return item.get("framework", {}).get("name", "Unknown")
        return "Unknown"


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified Homelab Interface with Automatic Fallback"
    )
    parser.add_argument(
        "--execute-command", metavar="COMMAND", help="Execute command with fallback"
    )
    parser.add_argument("--call-api", metavar="API", help="Call API with fallback")
    parser.add_argument(
        "--get-best", metavar="CATEGORY:KEY", help="Get best option (format: category:key)"
    )
    parser.add_argument(
        "--list-prioritized",
        metavar="CATEGORY",
        nargs="?",
        const="all",
        help="List prioritized resources",
    )
    parser.add_argument("--report", action="store_true", help="Generate prioritization report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    interface = UnifiedHomelabInterface(project_root)

    if args.execute_command:
        result = interface.execute_command(args.execute_command)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print(f"✅ Command executed (attempt {result.get('attempts', 1)})")
                print(result.get("result", {}).get("stdout", ""))
            else:
                print(f"❌ Command failed after {result.get('attempts', 1)} attempts")
                print(result.get("error", ""))

    elif args.call_api:
        result = interface.call_api(args.call_api)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print(f"✅ API called (attempt {result.get('attempts', 1)})")
                print(f"Status: {result.get('result', {}).get('status_code', 'N/A')}")
            else:
                print(f"❌ API call failed after {result.get('attempts', 1)} attempts")
                print(result.get("error", ""))

    elif args.get_best:
        category, key = args.get_best.split(":", 1)
        best = interface.get_best_option(category, key)
        if args.json:
            print(json.dumps(best, indent=2, default=str))
        else:
            if best:
                print(f"Best option for {category}:{key}:")
                print(json.dumps(best, indent=2, default=str))
            else:
                print(f"No best option found for {category}:{key}")

    elif args.list_prioritized:
        resources = interface.list_prioritized_resources(
            category=None if args.list_prioritized == "all" else args.list_prioritized
        )
        if args.json:
            print(json.dumps(resources, indent=2, default=str))
        else:
            for category, items in resources.items():
                if items:
                    print(f"\n{category.upper()} ({len(items)}):")
                    for item in items[:5]:
                        print(f"  {item['key']}: {len(item['fallbacks'])} fallbacks")

    elif args.report:
        report = interface.generate_prioritization_report()
        print(report)

    else:
        # Default: show report
        report = interface.generate_prioritization_report()
        print(report)


if __name__ == "__main__":
    main()
