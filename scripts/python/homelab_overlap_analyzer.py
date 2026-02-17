#!/usr/bin/env python3
"""
Homelab Overlap Analyzer and Prioritization System

Analyzes all discovered systems to identify overlaps and determine:
- Best options (primary)
- Fallback options (secondary)
- Creates prioritized fallback chains

Tags: #HOMELAB #OVERLAP #PRIORITIZATION #FALLBACK @JARVIS @LUMINA
"""

import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_overlap_analyzer")


@dataclass
class OverlapGroup:
    """Group of overlapping items"""

    group_id: str
    category: str  # "command", "api", "service", "application", "framework", "software"
    items: List[Dict[str, Any]] = field(default_factory=list)
    primary: Optional[Dict[str, Any]] = None
    fallbacks: List[Dict[str, Any]] = field(default_factory=list)
    reason: str = ""


@dataclass
class PrioritizationRule:
    """Rule for prioritizing options"""

    rule_id: str
    category: str
    criteria: Dict[str, Any]  # {"prefer": "newer", "avoid": "deprecated", etc.}
    priority: int = 0  # Higher = more important


class OverlapDetector:
    """Detects overlaps across systems"""

    def detect_command_overlaps(self, control_interfaces: List[Dict]) -> List[OverlapGroup]:
        """Detect overlapping commands"""
        overlaps = []
        command_groups = defaultdict(list)

        for interface in control_interfaces:
            for cmd in interface.get("commands", []):
                # Normalize command name
                cmd_name = self._normalize_command_name(cmd.get("name", ""))
                command_groups[cmd_name].append(
                    {
                        "command": cmd,
                        "device_id": interface.get("device_id"),
                        "interface_id": interface.get("interface_id"),
                    }
                )

        for cmd_name, items in command_groups.items():
            if len(items) > 1:
                # Determine primary
                primary = self._prioritize_command(items)
                fallbacks = [item for item in items if item != primary]

                overlaps.append(
                    OverlapGroup(
                        group_id=f"cmd_overlap_{cmd_name}",
                        category="command",
                        items=items,
                        primary=primary,
                        fallbacks=fallbacks,
                        reason=self._get_prioritization_reason(items, primary, "command"),
                    )
                )

        return overlaps

    def detect_api_overlaps(self, control_interfaces: List[Dict]) -> List[OverlapGroup]:
        """Detect overlapping API endpoints"""
        overlaps = []
        api_groups = defaultdict(list)

        for interface in control_interfaces:
            for api in interface.get("api_endpoints", []):
                # Group by functionality (normalize URL)
                api_key = self._normalize_api_key(api.get("name", ""), api.get("url", ""))
                api_groups[api_key].append(
                    {
                        "api": api,
                        "device_id": interface.get("device_id"),
                        "interface_id": interface.get("interface_id"),
                    }
                )

        for api_key, items in api_groups.items():
            if len(items) > 1:
                primary = self._prioritize_api(items)
                fallbacks = [item for item in items if item != primary]

                overlaps.append(
                    OverlapGroup(
                        group_id=f"api_overlap_{api_key}",
                        category="api",
                        items=items,
                        primary=primary,
                        fallbacks=fallbacks,
                        reason=self._get_prioritization_reason(items, primary, "api"),
                    )
                )

        return overlaps

    def detect_service_overlaps(self, architecture_data: List[Dict]) -> List[OverlapGroup]:
        """Detect overlapping services"""
        overlaps = []
        service_groups = defaultdict(list)

        for device_data in architecture_data:
            for service in device_data.get("services", []):
                service_name = self._normalize_service_name(service.get("name", ""))
                service_groups[service_name].append(
                    {"service": service, "device_id": device_data.get("device_id")}
                )

        for service_name, items in service_groups.items():
            if len(items) > 1:
                primary = self._prioritize_service(items)
                fallbacks = [item for item in items if item != primary]

                overlaps.append(
                    OverlapGroup(
                        group_id=f"svc_overlap_{service_name}",
                        category="service",
                        items=items,
                        primary=primary,
                        fallbacks=fallbacks,
                        reason=self._get_prioritization_reason(items, primary, "service"),
                    )
                )

        return overlaps

    def detect_application_overlaps(self, architecture_data: List[Dict]) -> List[OverlapGroup]:
        """Detect overlapping applications"""
        overlaps = []
        app_groups = defaultdict(list)

        for device_data in architecture_data:
            for app in device_data.get("applications", []):
                app_key = self._normalize_application_key(app.get("name", ""), app.get("type", ""))
                app_groups[app_key].append(
                    {"application": app, "device_id": device_data.get("device_id")}
                )

        for app_key, items in app_groups.items():
            if len(items) > 1:
                primary = self._prioritize_application(items)
                fallbacks = [item for item in items if item != primary]

                overlaps.append(
                    OverlapGroup(
                        group_id=f"app_overlap_{app_key}",
                        category="application",
                        items=items,
                        primary=primary,
                        fallbacks=fallbacks,
                        reason=self._get_prioritization_reason(items, primary, "application"),
                    )
                )

        return overlaps

    def detect_framework_overlaps(self, architecture_data: List[Dict]) -> List[OverlapGroup]:
        """Detect overlapping frameworks"""
        overlaps = []
        framework_groups = defaultdict(list)

        for device_data in architecture_data:
            for framework in device_data.get("frameworks", []):
                framework_name = framework.get("name", "").lower()
                framework_groups[framework_name].append(
                    {"framework": framework, "device_id": device_data.get("device_id")}
                )

        for framework_name, items in framework_groups.items():
            if len(items) > 1:
                primary = self._prioritize_framework(items)
                fallbacks = [item for item in items if item != primary]

                overlaps.append(
                    OverlapGroup(
                        group_id=f"fw_overlap_{framework_name}",
                        category="framework",
                        items=items,
                        primary=primary,
                        fallbacks=fallbacks,
                        reason=self._get_prioritization_reason(items, primary, "framework"),
                    )
                )

        return overlaps

    def _normalize_command_name(self, name: str) -> str:
        """Normalize command name for comparison"""
        # Remove platform-specific prefixes
        name = re.sub(r"^(powershell|cmd|linux|dsm)_", "", name.lower())
        # Remove common suffixes
        name = re.sub(r"_[0-9]+$", "", name)
        return name.strip()

    def _normalize_api_key(self, name: str, url: str) -> str:
        """Normalize API key for comparison"""
        # Extract functionality from name or URL
        key = name.lower()
        # Remove version numbers
        key = re.sub(r"v\d+", "", key)
        # Extract path from URL
        if url:
            path_match = re.search(r"/(api/|v\d+/)?([^/?]+)", url)
            if path_match:
                key = path_match.group(2).lower()
        return key.strip()

    def _normalize_service_name(self, name: str) -> str:
        """Normalize service name"""
        return name.lower().strip()

    def _normalize_application_key(self, name: str, app_type: str) -> str:
        """Normalize application key"""
        return f"{name.lower()}_{app_type.lower()}".strip()

    def _prioritize_command(self, items: List[Dict]) -> Dict:
        """Prioritize commands"""
        # Prefer: newer, more features, local over remote, native over wrapper
        scored = []
        for item in items:
            cmd = item.get("command", {})
            score = 0

            # Prefer local
            if "localhost" in cmd.get("command", ""):
                score += 10
            elif "127.0.0.1" in cmd.get("command", ""):
                score += 10

            # Prefer native (not wrapper)
            if "powershell" in cmd.get("command", "").lower() and platform.system() == "Windows":
                score += 5
            elif "cmd" in cmd.get("command", "").lower() and platform.system() == "Windows":
                score += 3

            # Prefer more parameters
            score += len(cmd.get("parameters", []))

            scored.append((score, item))

        return max(scored, key=lambda x: x[0])[1]

    def _prioritize_api(self, items: List[Dict]) -> Dict:
        """Prioritize APIs"""
        scored = []
        for item in items:
            api = item.get("api", {})
            score = 0

            # Prefer local
            url = api.get("url", "")
            if "localhost" in url or "127.0.0.1" in url:
                score += 10

            # Prefer HTTPS
            if url.startswith("https://"):
                score += 5
            elif url.startswith("http://"):
                score += 3

            # Prefer newer APIs (v2 > v1)
            if "/v2/" in url or "/v2" in url:
                score += 5
            elif "/v1/" in url or "/v1" in url:
                score += 3

            # Prefer authenticated (more secure)
            if api.get("authentication") and api.get("authentication") != "none":
                score += 3

            scored.append((score, item))

        return max(scored, key=lambda x: x[0])[1]

    def _prioritize_service(self, items: List[Dict]) -> Dict:
        """Prioritize services"""
        scored = []
        for item in items:
            service = item.get("service", {})
            score = 0

            # Prefer running services
            if service.get("status") == "running":
                score += 10
            elif service.get("status") == "stopped":
                score += 1

            # Prefer automatic startup
            if service.get("startup_type") == "automatic":
                score += 5
            elif service.get("startup_type") == "manual":
                score += 3

            # Prefer services with process
            if service.get("process_id"):
                score += 3

            scored.append((score, item))

        return max(scored, key=lambda x: x[0])[1]

    def _prioritize_application(self, items: List[Dict]) -> Dict:
        """Prioritize applications"""
        scored = []
        for item in items:
            app = item.get("application", {})
            score = 0

            # Prefer newer frameworks
            framework = app.get("framework", "")
            if framework in ["fastapi", "express", "spring"]:
                score += 5
            elif framework in ["flask", "django"]:
                score += 3

            # Prefer applications with ports (active)
            if app.get("ports"):
                score += 5

            # Prefer applications with configuration
            if app.get("configuration_files"):
                score += 3

            scored.append((score, item))

        return max(scored, key=lambda x: x[0])[1]

    def _prioritize_framework(self, items: List[Dict]) -> Dict:
        """Prioritize frameworks"""
        scored = []
        for item in items:
            framework = item.get("framework", {})
            score = 0

            # Prefer newer frameworks
            fw_name = framework.get("name", "").lower()
            if fw_name in ["fastapi", "express", "spring"]:
                score += 5
            elif fw_name in ["flask", "django"]:
                score += 3

            # Prefer frameworks with version
            if framework.get("version"):
                score += 3

            # Prefer frameworks with applications
            if framework.get("applications"):
                score += 5

            scored.append((score, item))

        return max(scored, key=lambda x: x[0])[1]

    def _get_prioritization_reason(self, items: List[Dict], primary: Dict, category: str) -> str:
        """Get reason for prioritization"""
        reasons = []

        if category == "command":
            cmd = primary.get("command", {})
            if "localhost" in cmd.get("command", ""):
                reasons.append("local execution")
            if len(cmd.get("parameters", [])) > 0:
                reasons.append(f"{len(cmd.get('parameters', []))} parameters")

        elif category == "api":
            api = primary.get("api", {})
            if "localhost" in api.get("url", ""):
                reasons.append("local endpoint")
            if api.get("authentication") and api.get("authentication") != "none":
                reasons.append("authenticated")

        elif category == "service":
            service = primary.get("service", {})
            if service.get("status") == "running":
                reasons.append("running")
            if service.get("startup_type") == "automatic":
                reasons.append("auto-start")

        elif category == "application":
            app = primary.get("application", {})
            if app.get("framework"):
                reasons.append(f"framework: {app.get('framework')}")
            if app.get("ports"):
                reasons.append("active ports")

        elif category == "framework":
            framework = primary.get("framework", {})
            if framework.get("version"):
                reasons.append(f"version: {framework.get('version')}")
            if framework.get("applications"):
                reasons.append(f"{len(framework.get('applications', []))} applications")

        return ", ".join(reasons) if reasons else "default selection"


class FallbackChainBuilder:
    """Builds fallback chains"""

    def build_fallback_chains(self, overlaps: List[OverlapGroup]) -> Dict[str, List[Dict]]:
        """Build fallback chains from overlaps"""
        chains = {}

        for overlap in overlaps:
            chain = []

            # Add primary
            if overlap.primary:
                chain.append({"item": overlap.primary, "priority": 1, "reason": "primary"})

            # Add fallbacks in priority order
            for i, fallback in enumerate(overlap.fallbacks, start=2):
                chain.append({"item": fallback, "priority": i, "reason": "fallback"})

            chains[overlap.group_id] = {
                "category": overlap.category,
                "chain": chain,
                "reason": overlap.reason,
            }

        return chains


class HomelabOverlapAnalyzer:
    """Main overlap analysis system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.detector = OverlapDetector()
        self.chain_builder = FallbackChainBuilder()

    def analyze_all_overlaps(self) -> Dict[str, Any]:
        """Analyze all overlaps across systems"""
        # Load all data
        control_dir = project_root / "data" / "homelab_control"
        architecture_dir = project_root / "data" / "homelab_architecture"

        control_files = sorted(control_dir.glob("control_map_*.json"), reverse=True)
        architecture_files = sorted(
            architecture_dir.glob("architecture_inventory_*.json"), reverse=True
        )

        if not control_files or not architecture_files:
            logger.error("Missing required data files")
            return {}

        # Load control interfaces
        with open(control_files[0], encoding="utf-8") as f:
            control_data = json.load(f)

        # Load architecture data
        with open(architecture_files[0], encoding="utf-8") as f:
            architecture_data = json.load(f)

        # Detect overlaps
        all_overlaps = []

        # Command overlaps
        command_overlaps = self.detector.detect_command_overlaps(control_data.get("interfaces", []))
        all_overlaps.extend(command_overlaps)

        # API overlaps
        api_overlaps = self.detector.detect_api_overlaps(control_data.get("interfaces", []))
        all_overlaps.extend(api_overlaps)

        # Service overlaps
        service_overlaps = self.detector.detect_service_overlaps(
            architecture_data.get("devices", [])
        )
        all_overlaps.extend(service_overlaps)

        # Application overlaps
        app_overlaps = self.detector.detect_application_overlaps(
            architecture_data.get("devices", [])
        )
        all_overlaps.extend(app_overlaps)

        # Framework overlaps
        framework_overlaps = self.detector.detect_framework_overlaps(
            architecture_data.get("devices", [])
        )
        all_overlaps.extend(framework_overlaps)

        # Build fallback chains
        fallback_chains = self.chain_builder.build_fallback_chains(all_overlaps)

        # Create analysis report
        analysis = {
            "analysis_id": f"overlap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "overlaps": {
                "commands": len(command_overlaps),
                "apis": len(api_overlaps),
                "services": len(service_overlaps),
                "applications": len(app_overlaps),
                "frameworks": len(framework_overlaps),
                "total": len(all_overlaps),
            },
            "overlap_groups": [asdict(o) for o in all_overlaps],
            "fallback_chains": fallback_chains,
            "summary": {
                "total_overlaps": len(all_overlaps),
                "total_fallback_chains": len(fallback_chains),
                "categories": {
                    "commands": len(command_overlaps),
                    "apis": len(api_overlaps),
                    "services": len(service_overlaps),
                    "applications": len(app_overlaps),
                    "frameworks": len(framework_overlaps),
                },
            },
        }

        return analysis

    def save_analysis(self, analysis: Dict[str, Any], output_file: Path):
        """Save overlap analysis"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Overlap analysis saved: {output_file}")
        return analysis


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze overlaps and create prioritization/fallback system"
    )
    parser.add_argument("--output", help="Output file (default: overlap_analysis_<timestamp>.json)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    analyzer = HomelabOverlapAnalyzer(project_root)

    print("Analyzing overlaps and building prioritization system...")
    analysis = analyzer.analyze_all_overlaps()

    # Save analysis
    output_dir = project_root / "data" / "homelab_overlap_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = (
            output_dir / f"overlap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    analyzer.save_analysis(analysis, output_file)

    # Print summary
    print("\n" + "=" * 80)
    print("OVERLAP ANALYSIS SUMMARY")
    print("=" * 80)
    summary = analysis["summary"]
    print(f"Total Overlaps: {summary['total_overlaps']}")
    print(f"Total Fallback Chains: {summary['total_fallback_chains']}")
    print("\nBy Category:")
    for category, count in summary["categories"].items():
        print(f"  {category}: {count}")
    print(f"\nAnalysis saved: {output_file}")
    print("=" * 80)

    if args.json:
        print(json.dumps(analysis, indent=2, default=str))


if __name__ == "__main__":
    main()
