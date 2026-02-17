#!/usr/bin/env python3
"""
JARVIS Disk Space Manager

Comprehensive disk space analysis and cleanup system.
Monitors disk usage, identifies large files/directories, and provides cleanup recommendations.

Tags: #SYSTEM-HEALTH #DISK-SPACE #CLEANUP
"""

import sys
import os
import psutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDiskSpace")


class JARVISDiskSpaceManager:
    """
    JARVIS Disk Space Manager

    Monitors and manages disk space across the system.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.critical_threshold = 10.0  # 10% free space is critical
        self.warning_threshold = 20.0   # 20% free space is warning

        self.logger.info("✅ JARVIS Disk Space Manager initialized")

    def get_disk_usage(self, drive: str = "C:") -> Dict[str, Any]:
        """Get disk usage for a drive"""
        try:
            disk = psutil.disk_usage(drive)
            total_gb = disk.total / (1024**3)
            used_gb = disk.used / (1024**3)
            free_gb = disk.free / (1024**3)
            percent_free = (disk.free / disk.total) * 100

            status = "critical" if percent_free < self.critical_threshold else \
                     "warning" if percent_free < self.warning_threshold else "healthy"

            return {
                "drive": drive,
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "percent_free": round(percent_free, 2),
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting disk usage for {drive}: {e}", exc_info=True)
            return {}

    def get_docker_space(self) -> Dict[str, Any]:
        """Get Docker disk usage"""
        self.logger.info("🔍 Analyzing Docker disk usage...")

        try:
            result = subprocess.run(
                ["docker", "system", "df", "--format", "{{.Type}}|{{.TotalCount}}|{{.Size}}|{{.Reclaimable}}"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                self.logger.warning("⚠️  Docker not available or command failed")
                return {}

            docker_data = {
                "images": {"total": 0, "reclaimable": 0},
                "containers": {"total": 0, "reclaimable": 0},
                "volumes": {"total": 0, "reclaimable": 0},
                "build_cache": {"total": 0, "reclaimable": 0}
            }

            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue

                parts = line.split('|')
                if len(parts) >= 4:
                    type_name = parts[0].lower()
                    total = parts[2]
                    reclaimable = parts[3]

                    # Parse size (e.g., "17.54GB" -> 17.54)
                    def parse_size(size_str):
                        if not size_str or size_str == "0B":
                            return 0.0
                        try:
                            if "GB" in size_str:
                                return float(size_str.replace("GB", "").strip())
                            elif "MB" in size_str:
                                return float(size_str.replace("MB", "").strip()) / 1024
                            elif "KB" in size_str:
                                return float(size_str.replace("KB", "").strip()) / (1024**2)
                            else:
                                return 0.0
                        except:
                            return 0.0

                    total_gb = parse_size(total)
                    reclaimable_gb = parse_size(reclaimable)

                    if "image" in type_name:
                        docker_data["images"]["total"] = total_gb
                        docker_data["images"]["reclaimable"] = reclaimable_gb
                    elif "container" in type_name:
                        docker_data["containers"]["total"] = total_gb
                        docker_data["containers"]["reclaimable"] = reclaimable_gb
                    elif "volume" in type_name:
                        docker_data["volumes"]["total"] = total_gb
                        docker_data["volumes"]["reclaimable"] = reclaimable_gb
                    elif "cache" in type_name or "build" in type_name:
                        docker_data["build_cache"]["total"] = total_gb
                        docker_data["build_cache"]["reclaimable"] = reclaimable_gb

            total_reclaimable = sum([
                docker_data["images"]["reclaimable"],
                docker_data["containers"]["reclaimable"],
                docker_data["build_cache"]["reclaimable"]
            ])

            docker_data["total_reclaimable_gb"] = round(total_reclaimable, 2)

            self.logger.info(f"   Docker reclaimable space: {total_reclaimable:.2f} GB")

            return docker_data

        except FileNotFoundError:
            self.logger.warning("⚠️  Docker not found")
            return {}
        except Exception as e:
            self.logger.error(f"❌ Error analyzing Docker space: {e}", exc_info=True)
            return {}

    def find_large_directories(self, path: Path, min_size_gb: float = 0.1) -> List[Dict[str, Any]]:
        """Find large directories"""
        self.logger.info(f"🔍 Finding large directories in {path} (min {min_size_gb}GB)...")

        large_dirs = []
        min_size_bytes = min_size_gb * (1024**3)

        try:
            for item in path.iterdir():
                if item.is_dir():
                    try:
                        total_size = sum(
                            f.stat().st_size for f in item.rglob('*') if f.is_file()
                        )

                        if total_size >= min_size_bytes:
                            size_gb = total_size / (1024**3)
                            large_dirs.append({
                                "path": str(item.relative_to(path)),
                                "size_gb": round(size_gb, 2),
                                "file_count": sum(1 for _ in item.rglob('*') if _.is_file())
                            })
                    except (PermissionError, OSError) as e:
                        self.logger.debug(f"   Skipping {item.name}: {e}")
                        continue

            # Sort by size
            large_dirs.sort(key=lambda x: x["size_gb"], reverse=True)

            self.logger.info(f"   Found {len(large_dirs)} large directories")

            return large_dirs[:20]  # Top 20

        except Exception as e:
            self.logger.error(f"❌ Error finding large directories: {e}", exc_info=True)
            return []

    def cleanup_docker(self, prune_images: bool = False, prune_build_cache: bool = False) -> Dict[str, Any]:
        """Cleanup Docker resources"""
        self.logger.info("🧹 Cleaning up Docker resources...")

        cleanup_result = {
            "images_pruned": False,
            "build_cache_pruned": False,
            "space_freed_gb": 0.0,
            "errors": []
        }

        try:
            # Prune build cache
            if prune_build_cache:
                self.logger.info("   Pruning Docker build cache...")
                result = subprocess.run(
                    ["docker", "builder", "prune", "-f"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    cleanup_result["build_cache_pruned"] = True
                    # Parse freed space from output
                    if "Total reclaimed space:" in result.stdout:
                        # Extract size from output
                        for line in result.stdout.split('\n'):
                            if "Total reclaimed space:" in line:
                                # Try to extract GB value
                                import re
                                match = re.search(r'(\d+\.?\d*)\s*GB', line)
                                if match:
                                    cleanup_result["space_freed_gb"] += float(match.group(1))
                    self.logger.info("   ✅ Build cache pruned")
                else:
                    cleanup_result["errors"].append(f"Build cache prune failed: {result.stderr}")

            # Prune unused images
            if prune_images:
                self.logger.info("   Pruning unused Docker images...")
                result = subprocess.run(
                    ["docker", "image", "prune", "-a", "-f"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    cleanup_result["images_pruned"] = True
                    # Parse freed space
                    if "Total reclaimed space:" in result.stdout:
                        import re
                        for line in result.stdout.split('\n'):
                            if "Total reclaimed space:" in line:
                                match = re.search(r'(\d+\.?\d*)\s*GB', line)
                                if match:
                                    cleanup_result["space_freed_gb"] += float(match.group(1))
                    self.logger.info("   ✅ Unused images pruned")
                else:
                    cleanup_result["errors"].append(f"Image prune failed: {result.stderr}")

            cleanup_result["space_freed_gb"] = round(cleanup_result["space_freed_gb"], 2)

        except Exception as e:
            self.logger.error(f"❌ Error during Docker cleanup: {e}", exc_info=True)
            cleanup_result["errors"].append(str(e))

        return cleanup_result

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive disk space report"""
        self.logger.info("📊 Generating disk space report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "disk_usage": {},
            "docker": {},
            "large_directories": [],
            "recommendations": [],
            "critical": False
        }

        # Disk usage
        disk_usage = self.get_disk_usage("C:")
        report["disk_usage"] = disk_usage

        if disk_usage.get("status") == "critical":
            report["critical"] = True

        # Docker analysis
        docker_data = self.get_docker_space()
        report["docker"] = docker_data

        # Large directories in project
        large_dirs = self.find_large_directories(self.project_root, min_size_gb=0.1)
        report["large_directories"] = large_dirs

        # Generate recommendations
        recommendations = []

        if disk_usage.get("percent_free", 100) < self.critical_threshold:
            recommendations.append({
                "priority": "CRITICAL",
                "action": "Free up disk space immediately",
                "details": f"Only {disk_usage.get('percent_free', 0):.1f}% free space remaining",
                "estimated_space_gb": docker_data.get("total_reclaimable_gb", 0)
            })

        if docker_data.get("total_reclaimable_gb", 0) > 1.0:
            recommendations.append({
                "priority": "HIGH",
                "action": "Clean up Docker resources",
                "details": f"{docker_data.get('total_reclaimable_gb', 0):.2f} GB reclaimable",
                "commands": [
                    "docker builder prune -f",
                    "docker image prune -a -f"
                ]
            })

        if large_dirs:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Review large directories",
                "details": f"{len(large_dirs)} directories over 0.1GB",
                "directories": [d["path"] for d in large_dirs[:5]]
            })

        report["recommendations"] = recommendations

        return report

    def save_report(self, report: Dict[str, Any]) -> Path:
        try:
            """Save report to file"""
            report_file = self.project_root / "data" / "system" / "disk_space_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"   ✅ Report saved to {report_file}")
            return report_file


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Disk Space Manager")
        parser.add_argument("--report", action="store_true", help="Generate disk space report")
        parser.add_argument("--cleanup-docker", action="store_true", help="Clean up Docker resources")
        parser.add_argument("--prune-images", action="store_true", help="Prune unused Docker images")
        parser.add_argument("--prune-cache", action="store_true", help="Prune Docker build cache")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = JARVISDiskSpaceManager(project_root)

        if args.report:
            report = manager.generate_report()
            report_file = manager.save_report(report)
            print(json.dumps(report, indent=2, default=str))
            print(f"\n✅ Report saved to: {report_file}")

        elif args.cleanup_docker or args.prune_images or args.prune_cache:
            result = manager.cleanup_docker(
                prune_images=args.prune_images or args.cleanup_docker,
                prune_build_cache=args.prune_cache or args.cleanup_docker
            )
            print(json.dumps(result, indent=2, default=str))

        else:
            # Default: generate report
            report = manager.generate_report()
            print(json.dumps(report, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()