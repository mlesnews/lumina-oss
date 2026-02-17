#!/usr/bin/env python3
"""
Check GPU Usage for All AI/LLM Endpoints
                    -LUM THE MODERN
"""
import requests
import subprocess
import json
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("GPUUsageCheck")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GPUUsageCheck")

def check_nvidia_smi():
    """Check nvidia-smi for GPU usage"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception as e:
        logger.warning(f"Could not run nvidia-smi: {e}")
        return None

def check_ollama_gpu(endpoint, name):
    """Check if Ollama endpoint is using GPU"""
    try:
        # Check if models are loaded
        ps_response = requests.get(f"{endpoint}/api/ps", timeout=5)
        if ps_response.status_code == 200:
            ps_data = ps_response.json()
            models = ps_data.get("models", [])

            # Try to get GPU info from a model show command
            # Note: This requires the model to be available
            gpu_info = {}
            if models:
                model_name = models[0].get("name", "")
                if model_name:
                    # Check model details
                    show_response = requests.get(f"{endpoint}/api/show", params={"name": model_name}, timeout=5)
                    if show_response.status_code == 200:
                        show_data = show_response.json()
                        gpu_info = {
                            "model": model_name,
                            "details": show_data.get("details", {}),
                            "modelfile": show_data.get("modelfile", "")
                        }

            return {
                "endpoint": endpoint,
                "name": name,
                "status": "online",
                "models_loaded": len(models),
                "models": [m.get("name") for m in models],
                "gpu_info": gpu_info,
                "note": "Check size_vram field in /api/ps to see GPU memory usage"
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

def check_iron_legion_gpu(endpoint, name):
    """Check Iron Legion endpoint GPU usage"""
    try:
        # Iron Legion uses OpenAI-compatible API
        root_response = requests.get(f"{endpoint}/", timeout=5)
        if root_response.status_code == 200:
            root_data = root_response.json()
            return {
                "endpoint": endpoint,
                "name": name,
                "status": "online",
                "service": root_data.get("service", ""),
                "model": root_data.get("model", ""),
                "note": "Iron Legion runs on RTX 3090 (KAIJU_NO_8 desktop)"
            }
        else:
            return {
                "endpoint": endpoint,
                "name": name,
                "status": "offline",
                "error": f"HTTP {root_response.status_code}"
            }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "name": name,
            "status": "error",
            "error": str(e)
        }

def main():
    logger.info("=" * 80)
    logger.info("🔍 GPU USAGE CHECK - All AI/LLM Endpoints")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)

    # Check nvidia-smi
    logger.info("\n📊 NVIDIA GPU Status (Local Host):")
    nvidia_info = check_nvidia_smi()
    if nvidia_info:
        logger.info(nvidia_info)
    else:
        logger.warning("   ⚠️  nvidia-smi not available (may not have NVIDIA GPU or drivers)")

    # Check ULTRON Local
    logger.info("\n🚀 ULTRON Local (localhost:11434):")
    ultron_local = check_ollama_gpu("http://localhost:11434", "ULTRON Local")
    logger.info(f"   Status: {ultron_local.get('status')}")
    if ultron_local.get('status') == 'online':
        logger.info(f"   Models loaded: {ultron_local.get('models_loaded', 0)}")
        if ultron_local.get('models'):
            logger.info(f"   Models: {', '.join(ultron_local['models'])}")
        logger.info(f"   GPU: RTX 5090 Mobile (24GB VRAM)")
        logger.info(f"   Note: Check size_vram in /api/ps response to verify GPU usage")

    # Check ULTRON KAIJU (NAS)
    logger.info("\n📦 ULTRON KAIJU (NAS - <NAS_PRIMARY_IP>:11434):")
    ultron_kaiju = check_ollama_gpu("http://<NAS_PRIMARY_IP>:11434", "ULTRON KAIJU")
    logger.info(f"   Status: {ultron_kaiju.get('status')}")
    if ultron_kaiju.get('status') == 'online':
        logger.info(f"   Models loaded: {ultron_kaiju.get('models_loaded', 0)}")
        if ultron_kaiju.get('models'):
            logger.info(f"   Models: {', '.join(ultron_kaiju['models'])}")
        logger.info(f"   GPU: CPU-only (Synology NAS has no GPU)")
        logger.info(f"   Note: NAS runs CPU-only Ollama")

    # Check Iron Legion nodes
    logger.info("\n⚔️  IRON LEGION Cluster (KAIJU_NO_8 - <NAS_IP>):")
    iron_legion_nodes = [
        ("http://<NAS_IP>:3001", "Mark I - Code"),
        ("http://<NAS_IP>:3002", "Mark II - General"),
        ("http://<NAS_IP>:3003", "Mark III - Quick"),
        ("http://<NAS_IP>:3004", "Mark IV - Balanced"),
        ("http://<NAS_IP>:3005", "Mark V - Reasoning"),
        ("http://<NAS_IP>:3006", "Mark VI - Complex"),
        ("http://<NAS_IP>:3007", "Mark VII - Fallback")
    ]

    for endpoint, name in iron_legion_nodes:
        node_info = check_iron_legion_gpu(endpoint, name)
        logger.info(f"   {name}: {node_info.get('status')} - {node_info.get('model', 'N/A')}")

    logger.info(f"\n   GPU: RTX 3090 (24GB VRAM) - Shared across all 7 Iron Legion nodes")

    logger.info("\n" + "=" * 80)
    logger.info("📊 SUMMARY")
    logger.info("=" * 80)
    logger.info("   ULTRON Local: RTX 5090 Mobile (24GB) - Should use GPU")
    logger.info("   ULTRON KAIJU: CPU-only (NAS has no GPU)")
    logger.info("   IRON LEGION: RTX 3090 (24GB) - Shared across 7 nodes")
    logger.info("=" * 80)
    logger.info("\n💡 To verify GPU usage:")
    logger.info("   1. Check nvidia-smi output above")
    logger.info("   2. Check size_vram field in Ollama /api/ps response")
    logger.info("   3. Monitor GPU memory usage during inference")
    logger.info("=" * 80)

if __name__ == "__main__":


    main()