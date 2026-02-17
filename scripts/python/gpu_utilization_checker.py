#!/usr/bin/env python3
"""
GPU Utilization Checker - AI/LLM Work Optimization

Checks GPU utilization for AI/LLM work and optimizes settings.
Target: 50% GPU utilization (currently seeing 1-5%).

Tags: #GPU #AI #LLM #OPTIMIZATION #CURSOR #DOCKER #OLLAMA @JARVIS @LUMINA @DOIT
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
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

logger = get_logger("GPUUtilizationChecker")


class GPUUtilizationChecker:
    """
    GPU Utilization Checker

    Checks and optimizes GPU usage for AI/LLM work.
    Target: 50% utilization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize GPU utilization checker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "gpu_utilization"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.target_utilization = 50.0  # Target: 50%
        self.current_utilization = 0.0

        logger.info("✅ GPU Utilization Checker initialized")
        logger.info(f"   Target utilization: {self.target_utilization}%")

    def check_gpu_utilization(self) -> Dict[str, Any]:
        """
        Check current GPU utilization

        Returns:
            GPU utilization status
        """
        logger.info("=" * 80)
        logger.info("📊 GPU UTILIZATION CHECK")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "timestamp": None,
            "gpu_available": False,
            "gpu_utilization": 0.0,
            "target_utilization": self.target_utilization,
            "status": "unknown",
            "issues": [],
            "recommendations": []
        }

        # Check NVIDIA GPU
        try:
            nvidia_result = self._check_nvidia_gpu()
            if nvidia_result.get("available"):
                result["gpu_available"] = True
                result["gpu_utilization"] = nvidia_result.get("utilization", 0.0)
                result["gpu_name"] = nvidia_result.get("name", "NVIDIA GPU")
                result["gpu_memory_used"] = nvidia_result.get("memory_used", 0)
                result["gpu_memory_total"] = nvidia_result.get("memory_total", 0)
        except Exception as e:
            logger.warning(f"   ⚠️  NVIDIA GPU check failed: {e}")
            result["issues"].append(f"NVIDIA GPU check: {str(e)}")

        # Check if utilization is below target
        if result["gpu_utilization"] < self.target_utilization:
            result["status"] = "below_target"
            result["issues"].append(f"GPU utilization ({result['gpu_utilization']:.1f}%) below target ({self.target_utilization}%)")
        else:
            result["status"] = "optimal"

        # Generate recommendations
        result["recommendations"] = self._generate_recommendations(result)

        logger.info(f"   GPU Available: {result['gpu_available']}")
        logger.info(f"   GPU Utilization: {result['gpu_utilization']:.1f}%")
        logger.info(f"   Target: {self.target_utilization}%")
        logger.info(f"   Status: {result['status']}")
        logger.info("")

        return result

    def _check_nvidia_gpu(self) -> Dict[str, Any]:
        """Check NVIDIA GPU using nvidia-smi"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(", ")
                if len(parts) >= 4:
                    return {
                        "available": True,
                        "name": parts[0],
                        "utilization": float(parts[1]),
                        "memory_used": int(parts[2]),
                        "memory_total": int(parts[3])
                    }
        except FileNotFoundError:
            logger.warning("   ⚠️  nvidia-smi not found - NVIDIA GPU may not be available")
        except Exception as e:
            logger.warning(f"   ⚠️  nvidia-smi error: {e}")

        return {"available": False}

    def _generate_recommendations(self, status: Dict[str, Any]) -> List[str]:
        """Generate recommendations for GPU optimization"""
        recommendations = []

        if not status.get("gpu_available"):
            recommendations.append("Install NVIDIA GPU drivers")
            recommendations.append("Verify GPU is detected: nvidia-smi")

        if status.get("gpu_utilization", 0) < self.target_utilization:
            recommendations.append("Check Cursor settings for GPU acceleration")
            recommendations.append("Check Docker GPU runtime configuration")
            recommendations.append("Check Ollama GPU settings (OLLAMA_NUM_GPU)")
            recommendations.append("Verify CUDA is available in Docker containers")
            recommendations.append("Check if models are using GPU (not CPU)")

        return recommendations

    def check_cursor_gpu_settings(self) -> Dict[str, Any]:
        """Check Cursor IDE GPU settings"""
        logger.info("📋 Checking Cursor IDE GPU Settings")
        logger.info("")

        settings_file = self.project_root / ".cursor" / "settings.json"
        result = {
            "settings_file": str(settings_file),
            "gpu_settings_found": False,
            "recommendations": []
        }

        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # Check for GPU-related settings
                if "ollama" in str(settings).lower():
                    result["gpu_settings_found"] = True
                    result["recommendations"].append("Cursor configured for Ollama (check OLLAMA_NUM_GPU)")
                else:
                    result["recommendations"].append("Add GPU acceleration settings to Cursor")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not check Cursor settings: {e}")

        return result

    def check_docker_gpu_settings(self) -> Dict[str, Any]:
        """Check Docker GPU configuration"""
        logger.info("📋 Checking Docker GPU Settings")
        logger.info("")

        docker_files = list(self.project_root.glob("**/docker-compose*.yml"))
        result = {
            "docker_files_checked": len(docker_files),
            "gpu_configured": False,
            "files_with_gpu": [],
            "recommendations": []
        }

        for docker_file in docker_files:
            try:
                with open(docker_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if "nvidia" in content.lower() or "gpu" in content.lower() or "device" in content.lower():
                    result["files_with_gpu"].append(str(docker_file))
                    result["gpu_configured"] = True
            except Exception as e:
                logger.warning(f"   ⚠️  Could not check {docker_file}: {e}")

        if not result["gpu_configured"]:
            result["recommendations"].append("Add GPU runtime to docker-compose.yml")
            result["recommendations"].append("Add deploy.resources.reservations.devices for NVIDIA GPU")

        return result

    def optimize_gpu_settings(self) -> Dict[str, Any]:
        """
        Optimize GPU settings for 50% utilization

        Returns:
            Optimization result
        """
        logger.info("=" * 80)
        logger.info("🚀 GPU OPTIMIZATION")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "cursor_settings": self.check_cursor_gpu_settings(),
            "docker_settings": self.check_docker_gpu_settings(),
            "gpu_status": self.check_gpu_utilization(),
            "optimizations_applied": []
        }

        # Generate optimization recommendations
        logger.info("📋 Optimization Recommendations:")
        logger.info("")

        if result["gpu_status"]["gpu_utilization"] < self.target_utilization:
            logger.info("   1. Set OLLAMA_NUM_GPU=1 in environment")
            logger.info("   2. Add GPU runtime to Docker: runtime: nvidia")
            logger.info("   3. Add GPU devices to Docker: deploy.resources.reservations.devices")
            logger.info("   4. Verify CUDA is available in containers")
            logger.info("   5. Check Ollama is using GPU: ollama ps")
            logger.info("")

        return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="GPU Utilization Checker")
    parser.add_argument("--check", action="store_true", help="Check GPU utilization")
    parser.add_argument("--optimize", action="store_true", help="Optimize GPU settings")
    parser.add_argument("--check-cursor", action="store_true", help="Check Cursor settings")
    parser.add_argument("--check-docker", action="store_true", help="Check Docker settings")

    args = parser.parse_args()

    checker = GPUUtilizationChecker()

    if args.optimize:
        checker.optimize_gpu_settings()
    elif args.check_cursor:
        checker.check_cursor_gpu_settings()
    elif args.check_docker:
        checker.check_docker_gpu_settings()
    elif args.check:
        checker.check_gpu_utilization()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())