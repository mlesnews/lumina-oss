#!/usr/bin/env python3
"""
NAS Migration Phase 1: Immediate Disk Relief - Disk Analysis

Identifies space hogs and large files for migration to NAS.

Tags: #NAS_MIGRATION #DISK_ANALYSIS #PHASE1 @JARVIS @LUMINA
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import subprocess

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

logger = get_logger("NASMigrationPhase1")


class DiskAnalyzer:
    """Analyze disk usage and identify space hogs"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "nas_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # NAS configuration
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"

        # Target directories to analyze
        self.analysis_targets = {
            "ollama_models": [
                Path(os.environ.get("OLLAMA_MODELS", "C:\\Users\\mlesn\\.ollama\\models")),
                Path("C:\\Users\\mlesn\\AppData\\Local\\Ollama"),
            ],
            "docker_volumes": [
                Path("C:\\Users\\mlesn\\AppData\\Local\\Docker"),
                Path("C:\\ProgramData\\Docker"),
            ],
            "npm_cache": [
                Path(os.environ.get("npm_config_cache", "C:\\Users\\mlesn\\AppData\\Local\\npm-cache")),
            ],
            "pip_cache": [
                Path(os.environ.get("PIP_CACHE_DIR", "C:\\Users\\mlesn\\AppData\\Local\\pip\\Cache")),
            ],
            "downloads": [
                Path("C:\\Users\\mlesn\\Downloads"),
            ],
            "videos": [
                Path("C:\\Users\\mlesn\\Videos"),
                Path("C:\\Users\\mlesn\\Documents\\Videos"),
            ],
            "media": [
                Path("C:\\Users\\mlesn\\Pictures"),
                Path("C:\\Users\\mlesn\\Music"),
            ],
            "project_backups": [
                Path("C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\backups"),
            ],
        }

    def get_directory_size(self, path: Path) -> Tuple[int, int]:
        """
        Get directory size in bytes and file count

        Returns:
            (size_bytes, file_count)
        """
        total_size = 0
        file_count = 0

        if not path.exists():
            return 0, 0

        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                        file_count += 1
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError) as e:
            logger.warning(f"   ⚠️  Could not analyze {path}: {e}")

        return total_size, file_count

    def find_large_files(self, path: Path, min_size_gb: float = 1.0) -> List[Dict]:
        """Find files larger than min_size_gb"""
        large_files = []
        min_size_bytes = int(min_size_gb * 1024 * 1024 * 1024)

        if not path.exists():
            return large_files

        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        size = filepath.stat().st_size
                        if size >= min_size_bytes:
                            large_files.append({
                                "path": str(filepath),
                                "size_bytes": size,
                                "size_gb": round(size / (1024**3), 2),
                                "relative_path": str(filepath.relative_to(path)) if path in filepath.parents else str(filepath)
                            })
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError) as e:
            logger.warning(f"   ⚠️  Could not scan {path}: {e}")

        # Sort by size descending
        large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        return large_files

    def analyze_disk_usage(self) -> Dict:
        try:
            """Analyze disk usage across all target directories"""
            logger.info("=" * 80)
            logger.info("📊 PHASE 1: DISK USAGE ANALYSIS")
            logger.info("=" * 80)
            logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "disk_usage": {},
                "large_files": {},
                "space_hogs": [],
                "total_analyzed_gb": 0.0,
                "recommendations": []
            }

            # Analyze each category
            for category, paths in self.analysis_targets.items():
                logger.info(f"📁 Analyzing {category}...")
                category_total = 0
                category_files = 0
                category_large_files = []

                for path in paths:
                    if path.exists():
                        size_bytes, file_count = self.get_directory_size(path)
                        size_gb = round(size_bytes / (1024**3), 2)
                        category_total += size_bytes
                        category_files += file_count

                        logger.info(f"   {path}: {size_gb} GB ({file_count:,} files)")

                        # Find large files (>1GB)
                        large = self.find_large_files(path, min_size_gb=1.0)
                        category_large_files.extend(large)

                category_total_gb = round(category_total / (1024**3), 2)
                results["disk_usage"][category] = {
                    "total_gb": category_total_gb,
                    "file_count": category_files,
                    "paths": [str(p) for p in paths]
                }

                if category_large_files:
                    results["large_files"][category] = category_large_files[:10]  # Top 10
                    logger.info(f"   ✅ Found {len(category_large_files)} large files (>1GB)")

                if category_total_gb > 5.0:  # More than 5GB
                    results["space_hogs"].append({
                        "category": category,
                        "size_gb": category_total_gb,
                        "priority": "HIGH" if category_total_gb > 20 else "MEDIUM"
                    })
                    results["total_analyzed_gb"] += category_total_gb

                logger.info("")

            # Generate recommendations
            results["recommendations"] = self._generate_recommendations(results)

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.data_dir / f"phase1_disk_analysis_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            logger.info("=" * 80)
            logger.info("✅ ANALYSIS COMPLETE")
            logger.info("=" * 80)
            logger.info(f"📊 Total space analyzed: {results['total_analyzed_gb']:.2f} GB")
            logger.info(f"📁 Space hogs found: {len(results['space_hogs'])}")
            logger.info(f"💾 Results saved: {results_file}")
            logger.info("")

            return results

        except Exception as e:
            self.logger.error(f"Error in analyze_disk_usage: {e}", exc_info=True)
            raise
    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Generate migration recommendations"""
        recommendations = []

        # Sort space hogs by size
        space_hogs = sorted(results["space_hogs"], key=lambda x: x["size_gb"], reverse=True)

        for hog in space_hogs:
            category = hog["category"]
            size_gb = hog["size_gb"]

            if category == "ollama_models":
                recommendations.append({
                    "action": "migrate_ollama_models",
                    "category": category,
                    "size_gb": size_gb,
                    "target": f"{self.nas_base}\\data\\models\\ollama",
                    "priority": "HIGH",
                    "steps": [
                        f"Create NAS share: {self.nas_base}\\data\\models",
                        f"Set OLLAMA_MODELS env var to NAS path",
                        "Move models directory",
                        "Restart Ollama service"
                    ]
                })
            elif category == "docker_volumes":
                recommendations.append({
                    "action": "migrate_docker_volumes",
                    "category": category,
                    "size_gb": size_gb,
                    "target": f"{self.nas_base}\\data\\docker",
                    "priority": "HIGH",
                    "steps": [
                        f"Create NAS share: {self.nas_base}\\data\\docker",
                        "Stop Docker Desktop",
                        "Move volumes to NAS",
                        "Update Docker Desktop settings",
                        "Restart Docker Desktop"
                    ]
                })
            elif category in ["downloads", "videos", "media"]:
                recommendations.append({
                    "action": f"migrate_{category}",
                    "category": category,
                    "size_gb": size_gb,
                    "target": f"{self.nas_base}\\homes\\mlesn\\{category.title()}",
                    "priority": "MEDIUM",
                    "steps": [
                        f"Create NAS share: {self.nas_base}\\homes\\mlesn",
                        f"Move {category} to NAS",
                        "Create Windows folder redirection"
                    ]
                })
            elif category in ["npm_cache", "pip_cache"]:
                recommendations.append({
                    "action": f"redirect_{category}",
                    "category": category,
                    "size_gb": size_gb,
                    "target": f"{self.nas_base}\\data\\cache\\{category}",
                    "priority": "LOW",
                    "steps": [
                        f"Create NAS share: {self.nas_base}\\data\\cache",
                        f"Set {category.upper()}_DIR env var",
                        "Clear local cache"
                    ]
                })

        return recommendations

    def print_summary(self, results: Dict):
        """Print analysis summary"""
        print("\n" + "=" * 80)
        print("📊 DISK ANALYSIS SUMMARY")
        print("=" * 80)
        print()

        print("🔴 SPACE HOGS (>5GB):")
        for hog in sorted(results["space_hogs"], key=lambda x: x["size_gb"], reverse=True):
            print(f"   {hog['category']:20s} {hog['size_gb']:8.2f} GB [{hog['priority']}]")
        print()

        print("💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"\n   {i}. {rec['action'].replace('_', ' ').title()}")
            print(f"      Size: {rec['size_gb']:.2f} GB")
            print(f"      Target: {rec['target']}")
            print(f"      Priority: {rec['priority']}")
        print()


def main():
    """Main execution"""
    analyzer = DiskAnalyzer(project_root)
    results = analyzer.analyze_disk_usage()
    analyzer.print_summary(results)

    return results


if __name__ == "__main__":


    main()