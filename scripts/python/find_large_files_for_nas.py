#!/usr/bin/env python3
"""
Find Large Files for NAS Migration
Scans C: drive and project directories to identify files/directories to migrate to NAS.

Tags: #NAS #MIGRATION #DISK_SPACE #STORAGE
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import json

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FindLargeFilesForNAS")


class LargeFileFinder:
    """Find large files and directories for NAS migration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nas_base = r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups"

        # Common large file patterns to look for
        self.large_file_patterns = [
            "*.log",
            "*.cache",
            "*.tmp",
            "*.bak",
            "*.backup",
            "*.zip",
            "*.tar",
            "*.gz",
            "*.7z",
            "*.iso",
            "*.img",
            "*.vmdk",
            "*.vdi",
            "*.qcow2",
        ]

        # Directories that are typically large
        self.large_directory_patterns = [
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".venv",
            "venv",
            "env",
            ".cache",
            "cache",
            "logs",
            "log",
            "tmp",
            "temp",
            "backups",
            "backup",
            "build",
            "dist",
            ".build",
            ".dist",
            "target",
            ".target",
            "bin",
            "obj",
            ".git/objects",
            "docker_volumes",
            ".docker",
            "Downloads",
            "Videos",
            "Pictures",
            "Music",
        ]

        # Directories to scan (C: drive locations)
        self.scan_locations = [
            project_root,
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path("C:/Users/mlesn/AppData/Local/Temp"),
            Path("C:/Users/mlesn/AppData/Local"),
            Path("C:/Users/mlesn/AppData/Roaming"),
            Path("C:/Temp"),
            Path("C:/Windows/Temp"),
        ]

    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total

    def format_size(self, bytes_size: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"

    def find_large_directories(self, min_size_gb: float = 0.1) -> List[Dict[str, Any]]:
        """Find large directories that could be migrated"""
        logger.info(f"🔍 Scanning for directories larger than {min_size_gb} GB...")

        candidates = []
        min_size_bytes = min_size_gb * (1024 ** 3)

        for location in self.scan_locations:
            if not location.exists():
                continue

            logger.info(f"   Scanning: {location}")

            try:
                # Check if location itself matches patterns
                if any(pattern in location.name.lower() for pattern in self.large_directory_patterns):
                    size = self.get_directory_size(location)
                    if size >= min_size_bytes:
                        candidates.append({
                            "path": str(location),
                            "size_bytes": size,
                            "size_gb": round(size / (1024 ** 3), 2),
                            "type": "directory",
                            "priority": "HIGH" if size >= 1 * (1024 ** 3) else "MEDIUM",
                            "target": f"{self.nas_base}\\migrated_data\\{location.name}"
                        })

                # Scan subdirectories
                if location.is_dir():
                    try:
                        for item in location.iterdir():
                            if item.is_dir():
                                # Skip system directories and hidden
                                if item.name.startswith('.') and item.name != '.git':
                                    continue

                                # Check if matches large directory pattern
                                if any(pattern in item.name.lower() for pattern in self.large_directory_patterns):
                                    size = self.get_directory_size(item)
                                    if size >= min_size_bytes:
                                        candidates.append({
                                            "path": str(item),
                                            "size_bytes": size,
                                            "size_gb": round(size / (1024 ** 3), 2),
                                            "type": "directory",
                                            "priority": "HIGH" if size >= 1 * (1024 ** 3) else "MEDIUM",
                                            "target": f"{self.nas_base}\\migrated_data\\{item.name}"
                                        })
                    except (PermissionError, OSError) as e:
                        logger.debug(f"   Could not scan {location}: {e}")
            except Exception as e:
                logger.warning(f"   Error scanning {location}: {e}")

        # Sort by size (largest first)
        candidates.sort(key=lambda x: x["size_bytes"], reverse=True)
        return candidates

    def find_large_files(self, min_size_mb: float = 100) -> List[Dict[str, Any]]:
        """Find large individual files"""
        logger.info(f"🔍 Scanning for files larger than {min_size_mb} MB...")

        candidates = []
        min_size_bytes = min_size_mb * (1024 ** 2)

        for location in self.scan_locations:
            if not location.exists():
                continue

            try:
                if location.is_dir():
                    for pattern in self.large_file_patterns:
                        try:
                            for file_path in location.rglob(pattern):
                                if file_path.is_file():
                                    try:
                                        size = file_path.stat().st_size
                                        if size >= min_size_bytes:
                                            candidates.append({
                                                "path": str(file_path),
                                                "size_bytes": size,
                                                "size_gb": round(size / (1024 ** 3), 2),
                                                "type": "file",
                                                "priority": "MEDIUM",
                                                "target": f"{self.nas_base}\\migrated_files\\{file_path.name}"
                                            })
                                    except (OSError, PermissionError):
                                        pass
                        except (OSError, PermissionError):
                            pass
            except Exception as e:
                logger.debug(f"   Error scanning files in {location}: {e}")

        # Sort by size (largest first)
        candidates.sort(key=lambda x: x["size_bytes"], reverse=True)
        return candidates

    def scan_project_data_directories(self) -> List[Dict[str, Any]]:
        try:
            """Scan project data directories specifically"""
            logger.info("🔍 Scanning project data directories...")

            candidates = []
            data_dir = self.project_root / "data"

            if not data_dir.exists():
                return candidates

            # Scan all subdirectories in data/
            for item in data_dir.iterdir():
                if item.is_dir():
                    size = self.get_directory_size(item)
                    if size > 0:
                        size_gb = round(size / (1024 ** 3), 2)
                        if size_gb >= 0.01:  # At least 10 MB
                            candidates.append({
                                "path": str(item),
                                "size_bytes": size,
                                "size_gb": size_gb,
                                "type": "directory",
                                "priority": "HIGH" if size_gb >= 1.0 else "MEDIUM",
                                "target": f"{self.nas_base}\\lumina_data\\{item.name}"
                            })

            candidates.sort(key=lambda x: x["size_bytes"], reverse=True)
            return candidates

        except Exception as e:
            self.logger.error(f"Error in scan_project_data_directories: {e}", exc_info=True)
            raise
    def find_docker_volumes(self) -> List[Dict[str, Any]]:
        """Find Docker volumes that could be migrated"""
        logger.info("🔍 Scanning for Docker volumes...")

        candidates = []

        # Common Docker volume locations
        docker_locations = [
            Path("C:/ProgramData/Docker"),
            Path.home() / ".docker",
            Path("C:/Users/mlesn/AppData/Local/Docker"),
        ]

        for location in docker_locations:
            if location.exists():
                try:
                    # Look for volumes directory
                    volumes_dir = location / "volumes"
                    if volumes_dir.exists():
                        for volume in volumes_dir.iterdir():
                            if volume.is_dir():
                                size = self.get_directory_size(volume)
                                if size > 0:
                                    size_gb = round(size / (1024 ** 3), 2)
                                    if size_gb >= 0.1:  # At least 100 MB
                                        candidates.append({
                                            "path": str(volume),
                                            "size_bytes": size,
                                            "size_gb": size_gb,
                                            "type": "docker_volume",
                                            "priority": "HIGH",
                                            "target": f"{self.nas_base}\\docker_volumes\\{volume.name}"
                                        })
                except Exception as e:
                    logger.debug(f"   Error scanning Docker location {location}: {e}")

        candidates.sort(key=lambda x: x["size_bytes"], reverse=True)
        return candidates

    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report"""
        logger.info("=" * 80)
        logger.info("🔍 COMPREHENSIVE LARGE FILE SCAN FOR NAS MIGRATION")
        logger.info("=" * 80)

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "nas_base": self.nas_base,
            "directories": [],
            "files": [],
            "project_data": [],
            "docker_volumes": [],
            "summary": {}
        }

        # Find large directories
        logger.info("\n📁 Finding large directories...")
        report["directories"] = self.find_large_directories(min_size_gb=0.1)

        # Find large files
        logger.info("\n📄 Finding large files...")
        report["files"] = self.find_large_files(min_size_mb=100)

        # Scan project data
        logger.info("\n📦 Scanning project data directories...")
        report["project_data"] = self.scan_project_data_directories()

        # Find Docker volumes
        logger.info("\n🐳 Finding Docker volumes...")
        report["docker_volumes"] = self.find_docker_volumes()

        # Calculate summary
        total_size = sum(
            item["size_bytes"] for item in 
            report["directories"] + report["files"] + report["project_data"] + report["docker_volumes"]
        )

        report["summary"] = {
            "total_candidates": len(report["directories"]) + len(report["files"]) + len(report["project_data"]) + len(report["docker_volumes"]),
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024 ** 3), 2),
            "directories_count": len(report["directories"]),
            "files_count": len(report["files"]),
            "project_data_count": len(report["project_data"]),
            "docker_volumes_count": len(report["docker_volumes"]),
        }

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print formatted migration report"""
        print("\n" + "=" * 80)
        print("📊 NAS MIGRATION CANDIDATES REPORT")
        print("=" * 80)
        print(f"Generated: {report['timestamp']}")
        print(f"NAS Target: {report['nas_base']}")
        print()

        summary = report["summary"]
        print(f"Total Candidates: {summary['total_candidates']}")
        print(f"Total Size: {self.format_size(summary['total_size_bytes'])} ({summary['total_size_gb']:.2f} GB)")
        print()

        # Directories
        if report["directories"]:
            print("-" * 80)
            print(f"📁 LARGE DIRECTORIES ({len(report['directories'])} found)")
            print("-" * 80)
            for item in report["directories"][:20]:  # Top 20
                print(f"  {self.format_size(item['size_bytes']):>12} | {item['priority']:>6} | {item['path']}")
            if len(report["directories"]) > 20:
                print(f"  ... and {len(report['directories']) - 20} more")
            print()

        # Project Data
        if report["project_data"]:
            print("-" * 80)
            print(f"📦 PROJECT DATA DIRECTORIES ({len(report['project_data'])} found)")
            print("-" * 80)
            for item in report["project_data"]:
                print(f"  {self.format_size(item['size_bytes']):>12} | {item['priority']:>6} | {item['path']}")
            print()

        # Docker Volumes
        if report["docker_volumes"]:
            print("-" * 80)
            print(f"🐳 DOCKER VOLUMES ({len(report['docker_volumes'])} found)")
            print("-" * 80)
            for item in report["docker_volumes"]:
                print(f"  {self.format_size(item['size_bytes']):>12} | {item['priority']:>6} | {item['path']}")
            print()

        # Large Files
        if report["files"]:
            print("-" * 80)
            print(f"📄 LARGE FILES ({len(report['files'])} found, showing top 10)")
            print("-" * 80)
            for item in report["files"][:10]:
                print(f"  {self.format_size(item['size_bytes']):>12} | {item['path']}")
            if len(report["files"]) > 10:
                print(f"  ... and {len(report['files']) - 10} more")
            print()

        print("=" * 80)
        print(f"💾 Total space that could be freed: {self.format_size(summary['total_size_bytes'])}")
        print("=" * 80)
        print()


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Find large files for NAS migration")
        parser.add_argument("--output", "-o", type=str, help="Output JSON file path")
        parser.add_argument("--min-dir-gb", type=float, default=0.1, help="Minimum directory size in GB (default: 0.1)")
        parser.add_argument("--min-file-mb", type=float, default=100, help="Minimum file size in MB (default: 100)")

        args = parser.parse_args()

        finder = LargeFileFinder(project_root)
        report = finder.generate_migration_report()

        finder.print_report(report)

        # Save to file
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = project_root / "data" / "system" / f"nas_migration_candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Report saved to: {output_path}")

        return report


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()