#!/usr/bin/env python3
"""
Comprehensive Docker Image Evaluation System
Evaluate and update all Docker images to use hardened versions

Tags: #docker #security #evaluation #hardening #MARVIN @JARVIS @LUMINA
"""

import sys
import json
import subprocess
import re
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

logger = get_logger("EvaluateAllDockerImages")


class DockerImageEvaluator:
    """
    Comprehensive Docker image evaluation system

    Evaluates:
    - All Dockerfiles in project
    - All docker-compose files
    - All running images
    - Base image security
    - Hardening opportunities
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize evaluator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "docker_image_evaluation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Hardened image reference
        self.hardened_kali = "kali-hardened-millennium-falc:latest"

        logger.info("✅ Docker Image Evaluator initialized")

    def find_all_dockerfiles(self) -> List[Path]:
        try:
            """Find all Dockerfiles in project"""
            logger.info("=" * 80)
            logger.info("🔍 FINDING ALL DOCKERFILES")
            logger.info("=" * 80)
            logger.info("")

            dockerfiles = []

            # Search in docker and containerization directories
            search_dirs = [
                self.project_root / "docker",
                self.project_root / "containerization"
            ]

            for search_dir in search_dirs:
                if search_dir.exists():
                    for dockerfile in search_dir.rglob("Dockerfile*"):
                        dockerfiles.append(dockerfile)
                        logger.info(f"   ✅ Found: {dockerfile.relative_to(self.project_root)}")

            logger.info("")
            logger.info(f"   📊 Total Dockerfiles: {len(dockerfiles)}")

            return dockerfiles

        except Exception as e:
            self.logger.error(f"Error in find_all_dockerfiles: {e}", exc_info=True)
            raise
    def find_all_docker_compose_files(self) -> List[Path]:
        try:
            """Find all docker-compose files"""
            logger.info("=" * 80)
            logger.info("🔍 FINDING ALL DOCKER-COMPOSE FILES")
            logger.info("=" * 80)
            logger.info("")

            compose_files = []

            search_dirs = [
                self.project_root / "docker",
                self.project_root / "containerization"
            ]

            for search_dir in search_dirs:
                if search_dir.exists():
                    for compose_file in search_dir.rglob("docker-compose*.yml"):
                        compose_files.append(compose_file)
                    for compose_file in search_dir.rglob("docker-compose*.yaml"):
                        compose_files.append(compose_file)

            logger.info(f"   📊 Total docker-compose files: {len(compose_files)}")

            return compose_files

        except Exception as e:
            self.logger.error(f"Error in find_all_docker_compose_files: {e}", exc_info=True)
            raise
    def analyze_dockerfile(self, dockerfile_path: Path) -> Dict[str, Any]:
        """Analyze a Dockerfile"""
        analysis = {
            "path": str(dockerfile_path.relative_to(self.project_root)),
            "base_image": None,
            "uses_kali": False,
            "uses_linux": False,
            "hardening_applied": False,
            "recommendations": []
        }

        try:
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find FROM statements
            from_matches = re.findall(r'FROM\s+([^\s]+)', content, re.IGNORECASE)
            if from_matches:
                base_image = from_matches[0]
                analysis["base_image"] = base_image

                # Check if uses Kali
                if "kali" in base_image.lower():
                    analysis["uses_kali"] = True
                    if "kali-hardened" not in base_image.lower():
                        analysis["recommendations"].append({
                            "priority": "HIGH",
                            "action": f"Replace {base_image} with {self.hardened_kali}",
                            "reason": "Use hardened Kali image for security"
                        })

                # Check if uses Linux
                linux_images = ["ubuntu", "debian", "alpine", "centos", "fedora", "linux"]
                if any(linux in base_image.lower() for linux in linux_images):
                    analysis["uses_linux"] = True
                    analysis["recommendations"].append({
                        "priority": "MEDIUM",
                        "action": "Consider using hardened base image",
                        "reason": "Linux base images should be hardened"
                    })

            # Check for hardening
            hardening_keywords = ["non-root", "useradd", "security", "hardened", "chmod 700"]
            if any(keyword in content.lower() for keyword in hardening_keywords):
                analysis["hardening_applied"] = True
            else:
                analysis["recommendations"].append({
                    "priority": "MEDIUM",
                    "action": "Apply security hardening",
                    "reason": "No security hardening detected"
                })

        except Exception as e:
            logger.debug(f"   Error analyzing {dockerfile_path}: {e}")
            analysis["error"] = str(e)

        return analysis

    def analyze_docker_compose(self, compose_path: Path) -> Dict[str, Any]:
        """Analyze docker-compose file"""
        analysis = {
            "path": str(compose_path.relative_to(self.project_root)),
            "services": [],
            "uses_kali": False,
            "recommendations": []
        }

        try:
            with open(compose_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for Kali references
            if "kali" in content.lower():
                analysis["uses_kali"] = True
                if "kali-hardened" not in content.lower():
                    analysis["recommendations"].append({
                        "priority": "HIGH",
                        "action": f"Update to use {self.hardened_kali}",
                        "reason": "Use hardened Kali image"
                    })

        except Exception as e:
            logger.debug(f"   Error analyzing {compose_path}: {e}")
            analysis["error"] = str(e)

        return analysis

    def get_running_images(self) -> List[Dict[str, Any]]:
        """Get list of running Docker images"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING RUNNING DOCKER IMAGES")
        logger.info("=" * 80)
        logger.info("")

        images = []

        try:
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and line.strip():
                        image_name = line.strip()
                        images.append({
                            "name": image_name,
                            "uses_kali": "kali" in image_name.lower(),
                            "is_hardened": "hardened" in image_name.lower()
                        })
                        logger.info(f"   📦 {image_name}")

                logger.info("")
                logger.info(f"   📊 Total images: {len(images)}")

        except Exception as e:
            logger.warning(f"   ⚠️  Error getting images: {e}")

        return images

    def generate_evaluation_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive evaluation report"""
            logger.info("=" * 80)
            logger.info("📊 GENERATING COMPREHENSIVE EVALUATION REPORT")
            logger.info("=" * 80)
            logger.info("")

            # Gather data
            dockerfiles = self.find_all_dockerfiles()
            compose_files = self.find_all_docker_compose_files()
            running_images = self.get_running_images()

            # Analyze Dockerfiles
            logger.info("")
            logger.info("📋 Analyzing Dockerfiles...")
            dockerfile_analyses = []
            kali_dockerfiles = []

            for dockerfile in dockerfiles:
                analysis = self.analyze_dockerfile(dockerfile)
                dockerfile_analyses.append(analysis)

                if analysis.get("uses_kali"):
                    kali_dockerfiles.append(analysis)
                    if not analysis.get("hardening_applied"):
                        logger.info(f"   ⚠️  {analysis['path']}: Uses Kali but not hardened")

            # Analyze docker-compose files
            logger.info("")
            logger.info("📋 Analyzing docker-compose files...")
            compose_analyses = []

            for compose_file in compose_files:
                analysis = self.analyze_docker_compose(compose_file)
                compose_analyses.append(analysis)

            # Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "evaluation_type": "COMPREHENSIVE_DOCKER_IMAGE_EVALUATION",
                "summary": {
                    "total_dockerfiles": len(dockerfiles),
                    "total_compose_files": len(compose_files),
                    "total_running_images": len(running_images),
                    "kali_dockerfiles": len(kali_dockerfiles),
                    "needs_hardening": len([a for a in dockerfile_analyses if not a.get("hardening_applied")])
                },
                "dockerfiles": dockerfile_analyses,
                "docker_compose": compose_analyses,
                "running_images": running_images,
                "recommendations": {
                    "high_priority": [],
                    "medium_priority": [],
                    "low_priority": []
                }
            }

            # Categorize recommendations
            for analysis in dockerfile_analyses:
                for rec in analysis.get("recommendations", []):
                    priority = rec.get("priority", "LOW")
                    if priority == "HIGH":
                        report["recommendations"]["high_priority"].append({
                            "file": analysis["path"],
                            "recommendation": rec
                        })
                    elif priority == "MEDIUM":
                        report["recommendations"]["medium_priority"].append({
                            "file": analysis["path"],
                            "recommendation": rec
                        })
                    else:
                        report["recommendations"]["low_priority"].append({
                            "file": analysis["path"],
                            "recommendation": rec
                        })

            # Save report
            report_file = self.data_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ EVALUATION REPORT GENERATED")
            logger.info("=" * 80)
            logger.info(f"   Report: {report_file.name}")

            # Print summary
            print("\n" + "=" * 80)
            print("📊 DOCKER IMAGE EVALUATION SUMMARY")
            print("=" * 80)
            print(f"Total Dockerfiles: {report['summary']['total_dockerfiles']}")
            print(f"Total docker-compose files: {report['summary']['total_compose_files']}")
            print(f"Total running images: {report['summary']['total_running_images']}")
            print(f"Kali Dockerfiles: {report['summary']['kali_dockerfiles']}")
            print(f"Needs Hardening: {report['summary']['needs_hardening']}")
            print(f"\nHigh Priority Recommendations: {len(report['recommendations']['high_priority'])}")
            print(f"Medium Priority: {len(report['recommendations']['medium_priority'])}")
            print(f"Low Priority: {len(report['recommendations']['low_priority'])}")
            print("=" * 80)
            print()

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_evaluation_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive Docker Image Evaluation")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate all Docker images")

    args = parser.parse_args()

    evaluator = DockerImageEvaluator()
    evaluator.generate_evaluation_report()

    return 0


if __name__ == "__main__":


    sys.exit(main())