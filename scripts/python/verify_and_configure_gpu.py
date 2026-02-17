#!/usr/bin/env python3
"""
Verify and Configure GPU Usage for All AI/LLM Endpoints
                    -LUM THE MODERN

Based on case study findings and best practices.
"""
import requests
import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("GPUVerification")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GPUVerification")

def check_nvidia_gpu():
    """Check NVIDIA GPU availability and status"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(", ")
            return {
                "available": True,
                "index": gpu_info[0],
                "name": gpu_info[1],
                "utilization": gpu_info[2],
                "memory_used_mb": gpu_info[3].replace(" MiB", ""),
                "memory_total_mb": gpu_info[4].replace(" MiB", ""),
                "driver_version": gpu_info[5]
            }
        else:
            return {"available": False, "error": result.stderr}
    except FileNotFoundError:
        return {"available": False, "error": "nvidia-smi not found"}
    except Exception as e:
        return {"available": False, "error": str(e)}

def check_docker_gpu_access():
    """Check if Docker has GPU access"""
    try:
        # Check if nvidia-container-runtime is available
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "nvidia" in result.stdout.lower() or "gpu" in result.stdout.lower():
            return {"gpu_access": True, "details": "NVIDIA runtime detected"}
        else:
            return {"gpu_access": False, "details": "No NVIDIA runtime detected in docker info"}
    except Exception as e:
        return {"gpu_access": False, "error": str(e)}

def check_ollama_gpu_config(endpoint: str, name: str):
    """Check Ollama GPU configuration"""
    try:
        # Check if endpoint is accessible
        ps_response = requests.get(f"{endpoint}/api/ps", timeout=5)
        if ps_response.status_code == 200:
            ps_data = ps_response.json()
            models = ps_data.get("models", [])

            # Check for GPU memory usage
            gpu_models = []
            cpu_models = []

            for model in models:
                size_vram = model.get("size_vram", 0)
                if size_vram > 0:
                    gpu_models.append({
                        "name": model.get("name"),
                        "size_vram": size_vram,
                        "size": model.get("size", 0)
                    })
                else:
                    cpu_models.append({
                        "name": model.get("name"),
                        "size": model.get("size", 0)
                    })

            return {
                "endpoint": endpoint,
                "name": name,
                "status": "online",
                "gpu_models": gpu_models,
                "cpu_models": cpu_models,
                "total_models": len(models),
                "using_gpu": len(gpu_models) > 0
            }
        else:
            return {
                "endpoint": endpoint,
                "name": name,
                "status": "offline",
                "error": f"HTTP {ps_response.status_code}"
            }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "name": name,
            "status": "error",
            "error": str(e)
        }

def verify_gpu_inference(endpoint: str, model: str):
    """Verify GPU usage during inference"""
    try:
        # Get initial GPU memory
        initial_gpu = check_nvidia_gpu()
        initial_memory = int(initial_gpu.get("memory_used_mb", 0)) if initial_gpu.get("available") else 0

        # Run inference
        payload = {
            "model": model,
            "prompt": "Test GPU inference",
            "stream": False,
            "options": {"num_predict": 10}
        }

        response = requests.post(f"{endpoint}/api/generate", json=payload, timeout=30)

        # Get GPU memory after inference
        final_gpu = check_nvidia_gpu()
        final_memory = int(final_gpu.get("memory_used_mb", 0)) if final_gpu.get("available") else 0

        memory_delta = final_memory - initial_memory

        return {
            "success": response.status_code == 200,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_delta_mb": memory_delta,
            "using_gpu": memory_delta > 0 or final_memory > 100  # If memory increased or already high
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def configure_ollama_gpu():
    """Provide instructions for configuring Ollama GPU"""
    instructions = []

    # Check Docker GPU access
    docker_gpu = check_docker_gpu_access()
    if not docker_gpu.get("gpu_access"):
        instructions.append({
            "step": "Configure Docker GPU Access",
            "priority": "high",
            "instructions": [
                "1. Install NVIDIA Container Toolkit",
                "2. Configure Docker to use nvidia runtime",
                "3. Restart Docker service",
                "4. Verify with: docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi"
            ]
        })

    # Check Ollama container
    instructions.append({
        "step": "Verify Ollama Container GPU Access",
        "priority": "high",
        "instructions": [
            "1. Check if Ollama container is running: docker ps | grep ollama",
            "2. Verify GPU access: docker exec ollama nvidia-smi",
            "3. If not accessible, restart with: docker run --gpus all -d -p 11434:11434 ollama/ollama"
        ]
    })

    return instructions

def main():
    try:
        logger.info("=" * 80)
        logger.info("🔍 GPU VERIFICATION & CONFIGURATION")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

        # Check NVIDIA GPU
        logger.info("\n📊 NVIDIA GPU Status:")
        gpu_info = check_nvidia_gpu()
        if gpu_info.get("available"):
            logger.info(f"   ✅ GPU Available: {gpu_info['name']}")
            logger.info(f"   📈 Utilization: {gpu_info['utilization']}")
            logger.info(f"   💾 Memory: {gpu_info['memory_used_mb']} MB / {gpu_info['memory_total_mb']} MB")
            logger.info(f"   🔧 Driver: {gpu_info['driver_version']}")
        else:
            logger.warning(f"   ⚠️  GPU Not Available: {gpu_info.get('error', 'Unknown error')}")

        # Check Docker GPU Access
        logger.info("\n🐳 Docker GPU Access:")
        docker_gpu = check_docker_gpu_access()
        if docker_gpu.get("gpu_access"):
            logger.info(f"   ✅ {docker_gpu.get('details')}")
        else:
            logger.warning(f"   ⚠️  {docker_gpu.get('details', docker_gpu.get('error', 'Unknown'))}")

        # Check ULTRON Local
        logger.info("\n🚀 ULTRON Local (localhost:11434):")
        ultron_local = check_ollama_gpu_config("http://localhost:11434", "ULTRON Local")
        logger.info(f"   Status: {ultron_local.get('status')}")
        if ultron_local.get('status') == 'online':
            logger.info(f"   Total Models: {ultron_local.get('total_models', 0)}")
            if ultron_local.get('using_gpu'):
                logger.info(f"   ✅ Using GPU: {len(ultron_local.get('gpu_models', []))} models")
                for model in ultron_local.get('gpu_models', []):
                    logger.info(f"      - {model['name']}: {model['size_vram']} bytes VRAM")
            else:
                logger.warning(f"   ⚠️  Not using GPU (models may be CPU-only or not loaded)")

        # Check ULTRON KAIJU (NAS - CPU-only expected)
        logger.info("\n📦 ULTRON KAIJU (NAS - <NAS_PRIMARY_IP>:11434):")
        ultron_kaiju = check_ollama_gpu_config("http://<NAS_PRIMARY_IP>:11434", "ULTRON KAIJU")
        logger.info(f"   Status: {ultron_kaiju.get('status')}")
        if ultron_kaiju.get('status') == 'online':
            logger.info(f"   Total Models: {ultron_kaiju.get('total_models', 0)}")
            logger.info(f"   ℹ️  Expected: CPU-only (NAS has no GPU)")

        # Configuration Instructions
        logger.info("\n" + "=" * 80)
        logger.info("🔧 CONFIGURATION INSTRUCTIONS")
        logger.info("=" * 80)
        instructions = configure_ollama_gpu()
        for instruction in instructions:
            logger.info(f"\n📋 {instruction['step']} (Priority: {instruction['priority']})")
            for step in instruction['instructions']:
                logger.info(f"   {step}")

        # Generate report
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "gpu_info": gpu_info,
            "docker_gpu": docker_gpu,
            "ultron_local": ultron_local,
            "ultron_kaiju": ultron_kaiju,
            "instructions": instructions
        }

        report_path = project_root / "data" / "gpu_verification_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"\n💾 Report saved: {report_path}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()