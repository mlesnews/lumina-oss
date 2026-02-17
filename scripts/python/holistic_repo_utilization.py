#!/usr/bin/env python3
"""
Holistic Repository Utilization

Manages holistic utilization of public/private repositories across
all development cycles with intelligent content routing.

Tags: #HOLISTIC #REPO_UTILIZATION #CONTENT_ROUTING @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HolisticRepoUtilization")


class ContentRouter:
    """Routes content to appropriate repositories"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "repository_structure.json"
        self.config = self._load_config()

        # Content classification rules
        self.public_content = [
            "docs/",
            "examples/",
            "templates/",
            "public_scripts/",
            "*.md",
            "LICENSE",
            "README.md"
        ]

        self.private_content = [
            "config/private/",
            "credentials/",
            "enterprise/",
            "internal/",
            "*.key",
            "*.secret",
            ".env"
        ]

        self.local_content = [
            "nas_configs/",
            "local_network/",
            "local_ai/",
            "enterprise_deployments/"
        ]

    def _load_config(self) -> Dict[str, Any]:
        try:
            """Load repository configuration"""
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def classify_content(self, file_path: Path) -> str:
        """Classify content as public, private, or local"""
        path_str = str(file_path)

        # Check for private content
        for pattern in self.private_content:
            if pattern in path_str or file_path.match(pattern):
                return "private"

        # Check for local content
        for pattern in self.local_content:
            if pattern in path_str or file_path.match(pattern):
                return "local_enterprise"

        # Default to public
        return "public"

    def route_content(self, file_path: Path, target_repo: str = None) -> Dict[str, Any]:
        """Route content to appropriate repository"""
        classification = self.classify_content(file_path)

        if target_repo:
            classification = target_repo

        routing = {
            "file": str(file_path),
            "classification": classification,
            "target_repository": classification,
            "timestamp": datetime.now().isoformat()
        }

        # Get repository config
        repo_config = self.config.get("repository_strategy", {}).get(classification, {})
        routing["repository_url"] = repo_config.get("url", "")
        routing["repository_path"] = repo_config.get("path", "")

        return routing

    def batch_route(self, file_paths: List[Path]) -> Dict[str, List[Dict[str, Any]]]:
        """Route multiple files at once"""
        routes = {
            "public": [],
            "private": [],
            "local_enterprise": []
        }

        for file_path in file_paths:
            routing = self.route_content(file_path)
            target = routing["target_repository"]
            routes[target].append(routing)

        return routes


class RepositoryUtilizationManager:
    """Manages holistic repository utilization"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.router = ContentRouter(project_root)
        self.config_file = project_root / "config" / "repository_structure.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            """Load configuration"""
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def analyze_repository_utilization(self) -> Dict[str, Any]:
        """Analyze current repository utilization"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "repositories": {},
            "content_distribution": {},
            "recommendations": []
        }

        # Analyze each repository type
        repo_strategy = self.config.get("repository_strategy", {})
        for repo_type, repo_config in repo_strategy.items():
            content_types = repo_config.get("content_types", [])
            analysis["repositories"][repo_type] = {
                "content_types": content_types,
                "purpose": repo_config.get("purpose", ""),
                "visibility": repo_config.get("visibility", "")
            }

        # Analyze content distribution
        all_files = list(self.project_root.rglob("*"))
        file_paths = [f for f in all_files if f.is_file()]

        routes = self.router.batch_route(file_paths)
        analysis["content_distribution"] = {
            "public": len(routes["public"]),
            "private": len(routes["private"]),
            "local_enterprise": len(routes["local_enterprise"])
        }

        # Generate recommendations
        total = sum(analysis["content_distribution"].values())
        if total > 0:
            public_pct = (analysis["content_distribution"]["public"] / total) * 100
            private_pct = (analysis["content_distribution"]["private"] / total) * 100
            local_pct = (analysis["content_distribution"]["local_enterprise"] / total) * 100

            if public_pct < 20:
                analysis["recommendations"].append("Consider moving more content to public repository")
            if private_pct > 60:
                analysis["recommendations"].append("High percentage of private content - review classification")
            if local_pct > 30:
                analysis["recommendations"].append("Significant local content - ensure proper NAS sync")

        return analysis

    def optimize_repository_structure(self) -> Dict[str, Any]:
        """Optimize repository structure based on analysis"""
        analysis = self.analyze_repository_utilization()

        optimization = {
            "timestamp": datetime.now().isoformat(),
            "current_state": analysis,
            "optimizations": [],
            "actions_required": []
        }

        # Generate optimization recommendations
        dist = analysis["content_distribution"]
        total = sum(dist.values())

        if total > 0:
            # Check for misclassified content
            if dist["private"] > dist["public"] * 2:
                optimization["optimizations"].append({
                    "type": "rebalance",
                    "description": "Consider moving some private content to public",
                    "priority": "medium"
                })

            # Check for local content sync
            if dist["local_enterprise"] > 0:
                optimization["actions_required"].append({
                    "action": "sync_local_to_private",
                    "description": "Sync local enterprise content to private repository",
                    "priority": "high"
                })

        return optimization

    def generate_utilization_report(self) -> Dict[str, Any]:
        """Generate comprehensive utilization report"""
        analysis = self.analyze_repository_utilization()
        optimization = self.optimize_repository_structure()

        report = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "optimization": optimization,
            "summary": {
                "total_files": sum(analysis["content_distribution"].values()),
                "public_files": analysis["content_distribution"]["public"],
                "private_files": analysis["content_distribution"]["private"],
                "local_files": analysis["content_distribution"]["local_enterprise"],
                "recommendations_count": len(analysis["recommendations"]),
                "optimizations_count": len(optimization["optimizations"])
            }
        }

        return report


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Holistic Repository Utilization")
        parser.add_argument("--analyze", action="store_true", help="Analyze repository utilization")
        parser.add_argument("--optimize", action="store_true", help="Optimize repository structure")
        parser.add_argument("--report", action="store_true", help="Generate utilization report")
        parser.add_argument("--route", type=str, help="Route a specific file")

        args = parser.parse_args()

        manager = RepositoryUtilizationManager(project_root)

        if args.route:
            file_path = project_root / args.route
            routing = manager.router.route_content(file_path)
            print(f"File: {routing['file']}")
            print(f"Classification: {routing['classification']}")
            print(f"Target Repository: {routing['target_repository']}")

        if args.analyze:
            analysis = manager.analyze_repository_utilization()
            print("=" * 80)
            print("📊 REPOSITORY UTILIZATION ANALYSIS")
            print("=" * 80)
            print(f"\nContent Distribution:")
            dist = analysis["content_distribution"]
            print(f"  Public: {dist['public']} files")
            print(f"  Private: {dist['private']} files")
            print(f"  Local Enterprise: {dist['local_enterprise']} files")

            if analysis["recommendations"]:
                print(f"\nRecommendations:")
                for rec in analysis["recommendations"]:
                    print(f"  - {rec}")
            print()

        if args.optimize:
            optimization = manager.optimize_repository_structure()
            print("=" * 80)
            print("🔧 REPOSITORY OPTIMIZATION")
            print("=" * 80)

            if optimization["optimizations"]:
                print("\nOptimizations:")
                for opt in optimization["optimizations"]:
                    print(f"  [{opt['priority']}] {opt['description']}")

            if optimization["actions_required"]:
                print("\nActions Required:")
                for action in optimization["actions_required"]:
                    print(f"  [{action['priority']}] {action['description']}")
            print()

        if args.report:
            report = manager.generate_utilization_report()
            report_file = project_root / "data" / "repository_utilization_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Utilization report saved: {report_file.name}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()