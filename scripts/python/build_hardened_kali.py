#!/usr/bin/env python3
"""
Build Hardened Kali Linux Docker Image
Custom-tailored for MILLENIUM_FALC laptop with security checks and AI2AI integration

Tags: #security #kali #docker #hardening #AI2AI @JARVIS @LUMINA
"""

import sys
import subprocess
import json
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

logger = get_logger("BuildHardenedKali")


class HardenedKaliBuilder:
    """
    Build and secure hardened Kali Linux Docker image
    with AI2AI integration for automated security monitoring
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize builder"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.docker_dir = self.project_root / "docker" / "kali-hardened"
        self.data_dir = self.project_root / "data" / "kali_builds"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # System specs (MILLENIUM_FALC)
        self.system_specs = {
            "architecture": "x64",
            "ram_gb": 64,
            "system": "MILLENIUM_FALC",
            "os": "Windows"
        }

        # Image configuration
        self.image_name = "kali-hardened-millennium-falc"
        self.image_tag = "latest"

        logger.info("✅ Hardened Kali Builder initialized")
        logger.info(f"   Target: {self.system_specs['system']}")
        logger.info(f"   Architecture: {self.system_specs['architecture']}")
        logger.info(f"   RAM: {self.system_specs['ram_gb']}GB")

    def check_prerequisites(self) -> Dict[str, Any]:
        """Check prerequisites (Docker, system requirements)"""
        logger.info("=" * 80)
        logger.info("🔍 CHECKING PREREQUISITES")
        logger.info("=" * 80)
        logger.info("")

        checks = {
            "docker_available": False,
            "docker_running": False,
            "docker_version": None,
            "disk_space_gb": 0,
            "nas_available": False
        }

        # Check Docker
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                checks["docker_available"] = True
                checks["docker_version"] = result.stdout.strip()
                logger.info(f"   ✅ Docker available: {checks['docker_version']}")
            else:
                logger.warning("   ⚠️  Docker not available")
        except Exception as e:
            logger.warning(f"   ⚠️  Docker check failed: {e}")

        # Check Docker running
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                checks["docker_running"] = True
                logger.info("   ✅ Docker daemon is running")
            else:
                logger.warning("   ⚠️  Docker daemon not running")
        except Exception as e:
            logger.warning(f"   ⚠️  Docker daemon check failed: {e}")

        # Check NAS availability
        nas_ip = "<NAS_PRIMARY_IP>"
        try:
            result = subprocess.run(
                ["ping", "-n", "1", nas_ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                checks["nas_available"] = True
                logger.info(f"   ✅ NAS available: {nas_ip}")
            else:
                logger.warning(f"   ⚠️  NAS not accessible: {nas_ip}")
        except Exception as e:
            logger.debug(f"   Could not ping NAS: {e}")

        return checks

    def build_image(self, use_cache: bool = True) -> Dict[str, Any]:
        """Build the hardened Kali Linux image"""
        logger.info("=" * 80)
        logger.info("🔨 BUILDING HARDENED KALI LINUX IMAGE")
        logger.info("=" * 80)
        logger.info("")

        build_result = {
            "timestamp": datetime.now().isoformat(),
            "image_name": f"{self.image_name}:{self.image_tag}",
            "success": False,
            "build_time_seconds": 0,
            "image_size_mb": 0,
            "errors": []
        }

        dockerfile_path = self.docker_dir / "Dockerfile"
        if not dockerfile_path.exists():
            logger.error(f"   ❌ Dockerfile not found: {dockerfile_path}")
            build_result["errors"].append(f"Dockerfile not found: {dockerfile_path}")
            return build_result

        logger.info(f"   📄 Dockerfile: {dockerfile_path}")
        logger.info(f"   🏷️  Image: {build_result['image_name']}")
        logger.info("")

        # Build command
        build_cmd = [
            "docker", "build",
            "-t", build_result["image_name"],
            "-f", str(dockerfile_path),
            str(self.docker_dir)
        ]

        if not use_cache:
            build_cmd.append("--no-cache")

        logger.info(f"   🔨 Running: {' '.join(build_cmd)}")
        logger.info("")

        start_time = datetime.now()

        try:
            process = subprocess.Popen(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Stream output
            for line in process.stdout:
                print(f"   {line.rstrip()}")

            process.wait()
            build_time = (datetime.now() - start_time).total_seconds()
            build_result["build_time_seconds"] = build_time

            if process.returncode == 0:
                build_result["success"] = True
                logger.info("")
                logger.info(f"   ✅ Build successful! ({build_time:.1f}s)")

                # Get image size
                try:
                    result = subprocess.run(
                        ["docker", "images", build_result["image_name"], "--format", "{{.Size}}"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        size_str = result.stdout.strip()
                        # Parse size (e.g., "2.5GB" -> 2500)
                        if "GB" in size_str:
                            build_result["image_size_mb"] = float(size_str.replace("GB", "")) * 1024
                        elif "MB" in size_str:
                            build_result["image_size_mb"] = float(size_str.replace("MB", ""))
                        logger.info(f"   📦 Image size: {size_str}")
                except Exception as e:
                    logger.debug(f"   Could not get image size: {e}")
            else:
                build_result["errors"].append(f"Build failed with exit code {process.returncode}")
                logger.error(f"   ❌ Build failed (exit code: {process.returncode})")

        except Exception as e:
            build_result["errors"].append(str(e))
            logger.error(f"   ❌ Build error: {e}")

        return build_result

    def run_security_checks(self, container_name: str = "kali-security-check") -> Dict[str, Any]:
        """Run security checks on the built image"""
        logger.info("=" * 80)
        logger.info("🔒 RUNNING SECURITY CHECKS")
        logger.info("=" * 80)
        logger.info("")

        security_results = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "security_issues": [],
            "hardening_applied": [],
            "recommendations": []
        }

        image_name = f"{self.image_name}:{self.image_tag}"

        # 1. Run Trivy scan (if available)
        logger.info("   🔍 Scanning for vulnerabilities (Trivy)...")
        try:
            result = subprocess.run(
                ["trivy", "image", image_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.info("   ✅ Trivy scan completed")
                security_results["trivy_scan"] = result.stdout
            else:
                logger.warning("   ⚠️  Trivy not available or scan failed")
        except FileNotFoundError:
            logger.info("   ℹ️  Trivy not installed (optional)")
        except Exception as e:
            logger.debug(f"   Trivy scan error: {e}")

        # 2. Run Docker Scout (if available)
        logger.info("   🔍 Scanning with Docker Scout...")
        try:
            result = subprocess.run(
                ["docker", "scout", "quickview", image_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                logger.info("   ✅ Docker Scout scan completed")
                security_results["docker_scout_scan"] = result.stdout
            else:
                logger.warning("   ⚠️  Docker Scout scan failed")
        except Exception as e:
            logger.debug(f"   Docker Scout scan error: {e}")

        # 3. Check image configuration
        logger.info("   🔍 Checking image configuration...")
        try:
            result = subprocess.run(
                ["docker", "inspect", image_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                inspect_data = json.loads(result.stdout)
                if inspect_data:
                    config = inspect_data[0].get("Config", {})

                    # Check for non-root user
                    if config.get("User") and config["User"] != "root":
                        security_results["hardening_applied"].append("Non-root user configured")
                        logger.info("   ✅ Non-root user configured")
                    else:
                        security_results["security_issues"].append("Running as root user")
                        logger.warning("   ⚠️  Running as root user")

                    # Check for health check
                    if config.get("Healthcheck"):
                        security_results["hardening_applied"].append("Health check configured")
                        logger.info("   ✅ Health check configured")
                    else:
                        security_results["recommendations"].append("Add health check")
                        logger.info("   ℹ️  Consider adding health check")
        except Exception as e:
            logger.debug(f"   Image inspection error: {e}")

        logger.info("")
        logger.info(f"   📊 Security Summary:")
        logger.info(f"      Hardening applied: {len(security_results['hardening_applied'])}")
        logger.info(f"      Security issues: {len(security_results['security_issues'])}")
        logger.info(f"      Recommendations: {len(security_results['recommendations'])}")

        return security_results

    def setup_ai2ai_integration(self) -> Dict[str, Any]:
        """Set up AI2AI integration for automated security monitoring"""
        logger.info("=" * 80)
        logger.info("🤖 SETTING UP AI2AI INTEGRATION")
        logger.info("=" * 80)
        logger.info("")

        ai2ai_config = {
            "timestamp": datetime.now().isoformat(),
            "integrated": False,
            "monitoring_enabled": False,
            "message_bus_connected": False
        }

        # Try to import JARVIS AI2AI components
        try:
            sys.path.insert(0, str(self.project_root / "scripts" / "python"))
            from jarvis_assistant_framework import JARVISAssistantFramework

            framework = JARVISAssistantFramework()
            ai2ai_config["integrated"] = True
            ai2ai_config["message_bus_connected"] = True
            ai2ai_config["monitoring_enabled"] = True

            logger.info("   ✅ JARVIS AI2AI Message Bus connected")
            logger.info("   ✅ Automated security monitoring enabled")

            # Register this build with AI2AI
            framework.send_message({
                "type": "kali_build",
                "system": self.system_specs["system"],
                "image": f"{self.image_name}:{self.image_tag}",
                "status": "building",
                "timestamp": datetime.now().isoformat()
            })

        except ImportError:
            logger.warning("   ⚠️  JARVIS AI2AI framework not available")
            logger.info("   ℹ️  Continuing without AI2AI integration")
        except Exception as e:
            logger.warning(f"   ⚠️  AI2AI integration error: {e}")

        return ai2ai_config

    def configure_nas_storage(self) -> Dict[str, Any]:
        try:
            """Configure NAS storage for Docker volumes"""
            logger.info("=" * 80)
            logger.info("💾 CONFIGURING NAS STORAGE")
            logger.info("=" * 80)
            logger.info("")

            nas_config = {
                "timestamp": datetime.now().isoformat(),
                "nas_ip": "<NAS_PRIMARY_IP>",
                "volumes_configured": [],
                "storage_path": None
            }

            # NAS paths
            nas_paths = [
                "\\\\<NAS_PRIMARY_IP>\\backups\\docker\\kali",
                "M:\\docker\\kali",
                "N:\\docker\\kali"
            ]

            for path_str in nas_paths:
                path = Path(path_str)
                if path.exists():
                    nas_config["storage_path"] = str(path)
                    nas_config["volumes_configured"].append(str(path))
                    logger.info(f"   ✅ NAS path available: {path}")
                    break

            if not nas_config["storage_path"]:
                logger.warning("   ⚠️  No NAS path available")
                logger.info("   ℹ️  Will use local Docker volumes")
                nas_config["storage_path"] = "local"

            return nas_config

        except Exception as e:
            self.logger.error(f"Error in configure_nas_storage: {e}", exc_info=True)
            raise
    def generate_build_report(self, build_result: Dict, security_results: Dict,
                                  ai2ai_config: Dict, nas_config: Dict) -> Dict[str, Any]:
        """Generate comprehensive build report"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_specs": self.system_specs,
                "build": build_result,
                "security": security_results,
                "ai2ai": ai2ai_config,
                "nas": nas_config,
                "summary": {
                    "build_success": build_result.get("success", False),
                    "security_issues": len(security_results.get("security_issues", [])),
                    "hardening_applied": len(security_results.get("hardening_applied", [])),
                    "ai2ai_integrated": ai2ai_config.get("integrated", False),
                    "nas_configured": nas_config.get("storage_path") != "local"
                }
            }

            # Save report
            report_file = self.data_dir / f"build_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("📊 BUILD REPORT GENERATED")
            logger.info("=" * 80)
            logger.info(f"   Report: {report_file.name}")
            logger.info("")

            # Print summary
            print("\n" + "=" * 80)
            print("🔒 HARDENED KALI LINUX BUILD REPORT")
            print("=" * 80)
            print(f"Build Status: {'✅ SUCCESS' if report['summary']['build_success'] else '❌ FAILED'}")
            print(f"Security Issues: {report['summary']['security_issues']}")
            print(f"Hardening Applied: {report['summary']['hardening_applied']}")
            print(f"AI2AI Integrated: {'✅ YES' if report['summary']['ai2ai_integrated'] else '❌ NO'}")
            print(f"NAS Configured: {'✅ YES' if report['summary']['nas_configured'] else '❌ NO'}")
            print("=" * 80)
            print()

            return report

        except Exception as e:
            self.logger.error(f"Error in generate_build_report: {e}", exc_info=True)
            raise
    def build_complete(self, skip_security: bool = False, skip_ai2ai: bool = False) -> Dict[str, Any]:
        """Complete build process with all steps"""
        logger.info("=" * 80)
        logger.info("🚀 HARDENED KALI LINUX BUILD - COMPLETE PROCESS")
        logger.info("=" * 80)
        logger.info("")

        # 1. Check prerequisites
        prerequisites = self.check_prerequisites()
        if not prerequisites.get("docker_available"):
            logger.error("   ❌ Docker not available. Cannot proceed.")
            return {"error": "Docker not available"}

        # 2. Setup AI2AI (before build for monitoring)
        ai2ai_config = {}
        if not skip_ai2ai:
            ai2ai_config = self.setup_ai2ai_integration()

        # 3. Configure NAS storage
        nas_config = self.configure_nas_storage()

        # 4. Build image
        build_result = self.build_image()

        if not build_result.get("success"):
            logger.error("   ❌ Build failed. Cannot proceed with security checks.")
            return {"error": "Build failed", "build_result": build_result}

        # 5. Run security checks
        security_results = {}
        if not skip_security:
            security_results = self.run_security_checks()

        # 6. Generate report
        report = self.generate_build_report(build_result, security_results, ai2ai_config, nas_config)

        return report


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Build Hardened Kali Linux Docker Image")
    parser.add_argument("--build", action="store_true", help="Build the image")
    parser.add_argument("--security-check", action="store_true", help="Run security checks only")
    parser.add_argument("--skip-security", action="store_true", help="Skip security checks")
    parser.add_argument("--skip-ai2ai", action="store_true", help="Skip AI2AI integration")
    parser.add_argument("--full", action="store_true", help="Full build with all checks")

    args = parser.parse_args()

    builder = HardenedKaliBuilder()

    if args.full or not any(vars(args).values()):
        # Default: full build
        builder.build_complete(skip_security=args.skip_security, skip_ai2ai=args.skip_ai2ai)
    elif args.build:
        builder.build_image()
    elif args.security_check:
        builder.run_security_checks()
    else:
        builder.check_prerequisites()

    return 0


if __name__ == "__main__":


    sys.exit(main())