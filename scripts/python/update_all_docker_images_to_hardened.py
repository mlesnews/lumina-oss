#!/usr/bin/env python3
"""
Update All Docker Images to Use Hardened Versions
Automated update system for migrating to hardened Kali image

Tags: #docker #security #update #hardening #automation @JARVIS @LUMINA
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UpdateAllDockerImagesToHardened")


class DockerImageUpdater:
    """
    Update all Docker images to use hardened versions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize updater"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "docker_image_updates"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.hardened_kali = "kali-hardened-millennium-falc:latest"

        logger.info("✅ Docker Image Updater initialized")

    def update_dockerfile_to_hardened(self, dockerfile_path: Path, backup: bool = True) -> Dict[str, Any]:
        """Update Dockerfile to use hardened Kali image"""
        result = {
            "file": str(dockerfile_path.relative_to(self.project_root)),
            "updated": False,
            "backup_created": False,
            "changes": []
        }

        try:
            # Backup
            if backup:
                backup_path = dockerfile_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy2(dockerfile_path, backup_path)
                result["backup_created"] = True
                result["backup_path"] = str(backup_path.relative_to(self.project_root))
                logger.info(f"   ✅ Backup created: {backup_path.name}")

            # Read Dockerfile
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Update FROM statements
            updated_lines = []
            for line in lines:
                original_line = line

                # Replace Kali images with hardened version
                if line.strip().startswith("FROM") and "kali" in line.lower():
                    if "kali-hardened" not in line.lower():
                        # Replace with hardened image
                        line = f"FROM {self.hardened_kali}\n"
                        result["changes"].append(f"Updated FROM to use {self.hardened_kali}")
                        logger.info(f"   ✅ Updated FROM statement")

                updated_lines.append(line)

            # Write updated Dockerfile
            if result["changes"]:
                with open(dockerfile_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                result["updated"] = True
                logger.info(f"   ✅ Dockerfile updated")
            else:
                logger.info(f"   ℹ️  No changes needed")

        except Exception as e:
            logger.error(f"   ❌ Error updating {dockerfile_path}: {e}")
            result["error"] = str(e)

        return result

    def update_docker_compose_to_hardened(self, compose_path: Path, backup: bool = True) -> Dict[str, Any]:
        """Update docker-compose file to use hardened image"""
        result = {
            "file": str(compose_path.relative_to(self.project_root)),
            "updated": False,
            "backup_created": False,
            "changes": []
        }

        try:
            # Backup
            if backup:
                backup_path = compose_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml")
                shutil.copy2(compose_path, backup_path)
                result["backup_created"] = True
                result["backup_path"] = str(backup_path.relative_to(self.project_root))

            # Read compose file
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Replace Kali image references
            if "kali" in content.lower() and "kali-hardened" not in content.lower():
                # Simple replacement (could be enhanced with YAML parsing)
                content = content.replace("kalilinux/kali", self.hardened_kali)
                content = content.replace("kali:latest", self.hardened_kali)
                content = content.replace("kali:rolling", self.hardened_kali)

                if content != original_content:
                    result["updated"] = True
                    result["changes"].append("Updated image references to hardened version")

                    # Write updated file
                    with open(compose_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"   ✅ docker-compose file updated")

        except Exception as e:
            logger.error(f"   ❌ Error updating {compose_path}: {e}")
            result["error"] = str(e)

        return result

    def update_all_to_hardened(self, dry_run: bool = False) -> Dict[str, Any]:
        try:
            """Update all Dockerfiles and docker-compose files to use hardened image"""
            logger.info("=" * 80)
            logger.info("🔄 UPDATING ALL DOCKER IMAGES TO HARDENED VERSIONS")
            logger.info("=" * 80)
            logger.info("")

            if dry_run:
                logger.info("   🔍 DRY RUN MODE - No files will be modified")
                logger.info("")

            # Import evaluator
            sys.path.insert(0, str(script_dir))
            from evaluate_all_docker_images import DockerImageEvaluator

            evaluator = DockerImageEvaluator(self.project_root)
            evaluation = evaluator.generate_evaluation_report()

            update_results = {
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "dockerfiles_updated": [],
                "compose_files_updated": [],
                "summary": {
                    "total_updated": 0,
                    "total_errors": 0
                }
            }

            # Update Dockerfiles that use Kali
            logger.info("")
            logger.info("=" * 80)
            logger.info("📝 UPDATING DOCKERFILES")
            logger.info("=" * 80)
            logger.info("")

            for dockerfile_analysis in evaluation.get("dockerfiles", []):
                if dockerfile_analysis.get("uses_kali") and not dockerfile_analysis.get("hardening_applied"):
                    dockerfile_path = self.project_root / dockerfile_analysis["path"]

                    logger.info(f"   📄 Updating: {dockerfile_analysis['path']}")

                    if not dry_run:
                        result = self.update_dockerfile_to_hardened(dockerfile_path)
                        update_results["dockerfiles_updated"].append(result)

                        if result.get("updated"):
                            update_results["summary"]["total_updated"] += 1
                        if result.get("error"):
                            update_results["summary"]["total_errors"] += 1
                    else:
                        logger.info(f"      [DRY RUN] Would update to {self.hardened_kali}")
                        update_results["dockerfiles_updated"].append({
                            "file": dockerfile_analysis["path"],
                            "dry_run": True
                        })

            # Update docker-compose files
            logger.info("")
            logger.info("=" * 80)
            logger.info("📝 UPDATING DOCKER-COMPOSE FILES")
            logger.info("=" * 80)
            logger.info("")

            for compose_analysis in evaluation.get("docker_compose", []):
                if compose_analysis.get("uses_kali"):
                    compose_path = self.project_root / compose_analysis["path"]

                    logger.info(f"   📄 Updating: {compose_analysis['path']}")

                    if not dry_run:
                        result = self.update_docker_compose_to_hardened(compose_path)
                        update_results["compose_files_updated"].append(result)

                        if result.get("updated"):
                            update_results["summary"]["total_updated"] += 1
                        if result.get("error"):
                            update_results["summary"]["total_errors"] += 1
                    else:
                        logger.info(f"      [DRY RUN] Would update to {self.hardened_kali}")
                        update_results["compose_files_updated"].append({
                            "file": compose_analysis["path"],
                            "dry_run": True
                        })

            # Save results
            report_file = self.data_dir / f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(update_results, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ UPDATE REPORT GENERATED")
            logger.info("=" * 80)
            logger.info(f"   Report: {report_file.name}")

            # Print summary
            print("\n" + "=" * 80)
            print("🔄 DOCKER IMAGE UPDATE SUMMARY")
            print("=" * 80)
            print(f"Mode: {'DRY RUN' if dry_run else 'LIVE UPDATE'}")
            print(f"Dockerfiles Updated: {len([r for r in update_results['dockerfiles_updated'] if r.get('updated')])}")
            print(f"Compose Files Updated: {len([r for r in update_results['compose_files_updated'] if r.get('updated')])}")
            print(f"Total Updated: {update_results['summary']['total_updated']}")
            print(f"Errors: {update_results['summary']['total_errors']}")
            print("=" * 80)
            print()

            return update_results


        except Exception as e:
            self.logger.error(f"Error in update_all_to_hardened: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Update All Docker Images to Hardened Versions")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (no files modified)")
    parser.add_argument("--update", action="store_true", help="Perform actual updates")

    args = parser.parse_args()

    updater = DockerImageUpdater()
    updater.update_all_to_hardened(dry_run=not args.update)

    return 0


if __name__ == "__main__":


    sys.exit(main())