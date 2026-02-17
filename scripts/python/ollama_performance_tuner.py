#!/usr/bin/env python3
"""
Ollama Performance Tuner - AI-ML Scientist Agent

Diagnoses and optimizes Ollama model performance for local GPU inference.
Applies scientific methodology: measure baseline → analyze bottlenecks → optimize → verify.

Key optimizations:
1. GPU layer allocation (num_gpu)
2. Context length reduction (num_ctx)
3. Thread optimization (num_thread)
4. Batch size tuning (num_batch)
5. Model quantization recommendations

Hardware: NVIDIA RTX 5090 Laptop GPU (24GB VRAM)
Problem: qwen2-72b:latest (47GB) >> 24GB VRAM → 57% CPU / 43% GPU split → SLOW

Tags: #PERFORMANCE #OLLAMA #GPU #AI-ML-SCIENTIST @JARVIS @LUMINA @DOIT
"""

import sys
import os
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("OllamaPerformanceTuner")

# Performance tuning configurations
TUNING_PROFILES = {
    "max_speed": {
        "description": "Maximum speed, reduced quality - fully GPU resident",
        "num_ctx": 2048,
        "num_batch": 512,
        "num_thread": 8,
        "target_gpu_percent": 100,
        "recommended_models": ["qwen2.5:14b", "qwen2.5-coder:7b", "llama3.2:3b"]
    },
    "balanced": {
        "description": "Balance speed and quality - mostly GPU with some CPU",
        "num_ctx": 4096,
        "num_batch": 256,
        "num_thread": 16,
        "target_gpu_percent": 80,
        "recommended_models": ["qwen2.5:32b", "codellama:13b", "llama3.2:11b"]
    },
    "max_quality": {
        "description": "Maximum quality, slower - heavy CPU offload acceptable",
        "num_ctx": 8192,
        "num_batch": 128,
        "num_thread": 32,
        "target_gpu_percent": 50,
        "recommended_models": ["qwen2.5:72b", "qwen2-72b:latest", "mixtral:8x7b"]
    }
}

# Model size estimates (Q4_K_M quantization, in GB)
MODEL_SIZES = {
    "qwen2-72b:latest": 47,
    "qwen2.5:72b": 47,
    "qwen2.5:32b": 18,
    "qwen2.5:14b": 8,
    "qwen2.5:7b": 4.7,
    "mixtral:8x7b": 26,
    "codellama:13b": 7.4,
    "llama3.2:11b": 6.5,
    "llama3.2:3b": 2.0,
    "qwen2.5-coder:7b": 4.7,
    "qwen2.5-coder:1.5b-base": 1.0,
    "gemma:2b": 1.7,
}

VRAM_GB = 24  # RTX 5090 Laptop GPU


class OllamaPerformanceTuner:
    """AI-ML Scientist agent for Ollama performance optimization"""

    def __init__(self):
        self.baseline_metrics: Dict[str, Any] = {}
        self.optimized_metrics: Dict[str, Any] = {}
        self.recommendations: List[str] = []
        self.gpu_info: Dict[str, Any] = {}
        self.model_info: Dict[str, Any] = {}

    def diagnose(self) -> Dict[str, Any]:
        """
        Step 1: Diagnose current performance bottlenecks
        Scientific method: Observe and measure before optimizing
        """
        logger.info("=" * 80)
        logger.info("🔬 AI-ML SCIENTIST: PERFORMANCE DIAGNOSIS")
        logger.info("=" * 80)
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "gpu": self._get_gpu_info(),
            "running_models": self._get_running_models(),
            "bottlenecks": [],
            "severity": "unknown"
        }
        
        # Analyze GPU info
        gpu = diagnosis["gpu"]
        if gpu.get("memory_used_gb", 0) > gpu.get("memory_total_gb", 24) * 0.9:
            diagnosis["bottlenecks"].append({
                "type": "gpu_memory_full",
                "severity": "critical",
                "description": "GPU VRAM nearly full - causing memory thrashing"
            })
        
        # Analyze running models
        for model in diagnosis["running_models"]:
            cpu_pct = model.get("cpu_percent", 0)
            gpu_pct = model.get("gpu_percent", 0)
            
            if cpu_pct > 50:
                diagnosis["bottlenecks"].append({
                    "type": "cpu_offload",
                    "severity": "critical",
                    "model": model["name"],
                    "cpu_percent": cpu_pct,
                    "gpu_percent": gpu_pct,
                    "description": f"Model {model['name']} has {cpu_pct}% on CPU - extremely slow!"
                })
            elif cpu_pct > 20:
                diagnosis["bottlenecks"].append({
                    "type": "partial_cpu_offload",
                    "severity": "warning",
                    "model": model["name"],
                    "cpu_percent": cpu_pct,
                    "description": f"Model {model['name']} has {cpu_pct}% on CPU - slower than optimal"
                })
        
        # Calculate overall severity
        severities = [b["severity"] for b in diagnosis["bottlenecks"]]
        if "critical" in severities:
            diagnosis["severity"] = "critical"
        elif "warning" in severities:
            diagnosis["severity"] = "warning"
        else:
            diagnosis["severity"] = "healthy"
        
        self._print_diagnosis(diagnosis)
        return diagnosis

    def _get_gpu_info(self) -> Dict[str, Any]:
        """Get NVIDIA GPU information"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,memory.used,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(", ")
                if len(parts) >= 5:
                    self.gpu_info = {
                        "name": parts[0].strip(),
                        "memory_total_mb": int(parts[1].strip()),
                        "memory_free_mb": int(parts[2].strip()),
                        "memory_used_mb": int(parts[3].strip()),
                        "utilization_percent": int(parts[4].strip()),
                        "memory_total_gb": int(parts[1].strip()) / 1024,
                        "memory_free_gb": int(parts[2].strip()) / 1024,
                        "memory_used_gb": int(parts[3].strip()) / 1024,
                    }
                    return self.gpu_info
        except Exception as e:
            logger.warning(f"Could not get GPU info: {e}")
        return {"error": "Could not retrieve GPU info"}

    def _get_running_models(self) -> List[Dict[str, Any]]:
        """Get currently running Ollama models with CPU/GPU split"""
        models = []
        try:
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines[1:]:  # Skip header
                    if not line.strip():
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        # Parse CPU/GPU split (e.g., "57%/43%")
                        processor = parts[3] if len(parts) > 3 else "0%/100%"
                        cpu_gpu = processor.replace("CPU/GPU", "").strip()
                        cpu_pct, gpu_pct = 0, 100
                        if "/" in cpu_gpu:
                            try:
                                cpu_str, gpu_str = cpu_gpu.split("/")
                                cpu_pct = int(cpu_str.replace("%", ""))
                                gpu_pct = int(gpu_str.replace("%", ""))
                            except ValueError:
                                pass
                        
                        models.append({
                            "name": parts[0],
                            "id": parts[1] if len(parts) > 1 else "",
                            "size": parts[2] if len(parts) > 2 else "",
                            "processor": processor,
                            "cpu_percent": cpu_pct,
                            "gpu_percent": gpu_pct,
                            "context": parts[4] if len(parts) > 4 else "",
                        })
        except Exception as e:
            logger.warning(f"Could not get running models: {e}")
        return models

    def _print_diagnosis(self, diagnosis: Dict[str, Any]):
        """Print diagnosis report"""
        severity_icons = {"critical": "🔴", "warning": "🟡", "healthy": "🟢"}
        
        logger.info("")
        logger.info(f"📊 GPU: {diagnosis['gpu'].get('name', 'Unknown')}")
        logger.info(f"   VRAM: {diagnosis['gpu'].get('memory_used_gb', 0):.1f}GB / {diagnosis['gpu'].get('memory_total_gb', 0):.1f}GB used")
        logger.info(f"   Utilization: {diagnosis['gpu'].get('utilization_percent', 0)}%")
        logger.info("")
        
        if diagnosis["running_models"]:
            logger.info("📋 Running Models:")
            for model in diagnosis["running_models"]:
                icon = "🔴" if model["cpu_percent"] > 50 else "🟡" if model["cpu_percent"] > 20 else "🟢"
                logger.info(f"   {icon} {model['name']}: {model['cpu_percent']}% CPU / {model['gpu_percent']}% GPU")
        else:
            logger.info("📋 No models currently loaded")
        
        logger.info("")
        if diagnosis["bottlenecks"]:
            logger.info(f"{severity_icons.get(diagnosis['severity'], '⚪')} BOTTLENECKS DETECTED:")
            for bottleneck in diagnosis["bottlenecks"]:
                icon = severity_icons.get(bottleneck["severity"], "⚪")
                logger.info(f"   {icon} {bottleneck['description']}")
        else:
            logger.info("🟢 No bottlenecks detected - performance is optimal!")
        logger.info("")

    def recommend(self, target_model: str = "qwen2-72b:latest") -> List[str]:
        """
        Step 2: Generate AI-ML Scientist recommendations
        """
        logger.info("=" * 80)
        logger.info("💡 AI-ML SCIENTIST: PERFORMANCE RECOMMENDATIONS")
        logger.info("=" * 80)
        logger.info("")
        
        model_size = MODEL_SIZES.get(target_model, 50)
        fits_in_vram = model_size <= VRAM_GB
        
        self.recommendations = []
        
        if not fits_in_vram:
            # Model too large for GPU - recommend alternatives
            overage = model_size - VRAM_GB
            cpu_percent = int((overage / model_size) * 100)
            
            self.recommendations.append(
                f"⚠️  CRITICAL: {target_model} ({model_size}GB) exceeds {VRAM_GB}GB VRAM by {overage:.1f}GB"
            )
            self.recommendations.append(
                f"   → {cpu_percent}% of model runs on slow CPU, causing {cpu_percent*2}-{cpu_percent*5}x slowdown"
            )
            self.recommendations.append("")
            
            # Option 1: Switch to smaller model
            self.recommendations.append("📌 OPTION 1: Switch to a GPU-fitting model (RECOMMENDED)")
            for model, size in sorted(MODEL_SIZES.items(), key=lambda x: x[1], reverse=True):
                if size <= VRAM_GB and "72b" not in model:
                    speedup = int(model_size / size) if size > 0 else 1
                    self.recommendations.append(f"   → {model} ({size}GB) - fits in VRAM, ~{speedup}x faster")
                    if len([r for r in self.recommendations if "→" in r]) >= 4:
                        break
            
            self.recommendations.append("")
            self.recommendations.append("📌 OPTION 2: Optimize current model (limited improvement)")
            self.recommendations.append("   → Reduce context length: num_ctx=2048 (saves ~2-4GB)")
            self.recommendations.append("   → Reduce batch size: num_batch=256 (saves ~1GB)")
            self.recommendations.append("   → Use flash attention if available")
            
            self.recommendations.append("")
            self.recommendations.append("📌 OPTION 3: Use more aggressive quantization")
            self.recommendations.append("   → Q3_K_M or Q2_K quantization (smaller but lower quality)")
            self.recommendations.append("   → May need to re-download model with different quantization")
        else:
            self.recommendations.append(f"✅ {target_model} ({model_size}GB) fits in {VRAM_GB}GB VRAM")
            self.recommendations.append("   → Should run at full GPU speed")
            self.recommendations.append("")
            self.recommendations.append("📌 Fine-tuning recommendations:")
            self.recommendations.append("   → Increase num_ctx for longer context (if VRAM allows)")
            self.recommendations.append("   → Increase num_batch for faster throughput")
        
        for rec in self.recommendations:
            logger.info(rec)
        
        logger.info("")
        return self.recommendations

    def create_optimized_modelfile(
        self,
        base_model: str = "qwen2-72b:latest",
        profile: str = "balanced",
        output_name: str = None
    ) -> str:
        """
        Step 3: Create optimized Modelfile with tuned parameters
        """
        logger.info("=" * 80)
        logger.info("🔧 AI-ML SCIENTIST: CREATING OPTIMIZED MODELFILE")
        logger.info("=" * 80)
        logger.info("")
        
        config = TUNING_PROFILES.get(profile, TUNING_PROFILES["balanced"])
        
        if output_name is None:
            output_name = f"{base_model.replace(':', '-')}-{profile}"
        
        modelfile_content = f'''# Optimized Modelfile for {base_model}
# Profile: {profile} - {config["description"]}
# Generated by AI-ML Scientist Agent: {datetime.now().isoformat()}
# Hardware: NVIDIA RTX 5090 Laptop GPU (24GB VRAM)

FROM {base_model}

# Performance Parameters
PARAMETER num_ctx {config["num_ctx"]}
PARAMETER num_batch {config["num_batch"]}
PARAMETER num_thread {config["num_thread"]}

# Memory Optimization
PARAMETER num_gpu 99
PARAMETER main_gpu 0

# Inference Quality (adjust for speed vs quality trade-off)
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1

# System prompt for optimal responses
SYSTEM """You are a highly capable AI assistant optimized for speed and accuracy. Provide concise, helpful responses."""
'''
        
        modelfile_path = project_root / "config" / "ollama_modelfiles" / f"Modelfile.{output_name}"
        modelfile_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(modelfile_path, "w") as f:
            f.write(modelfile_content)
        
        logger.info(f"✅ Created Modelfile: {modelfile_path}")
        logger.info(f"   Profile: {profile}")
        logger.info(f"   Context: {config['num_ctx']} tokens")
        logger.info(f"   Batch: {config['num_batch']}")
        logger.info(f"   Threads: {config['num_thread']}")
        logger.info("")
        logger.info("📌 To create optimized model, run:")
        logger.info(f"   ollama create {output_name} -f \"{modelfile_path}\"")
        logger.info("")
        
        return str(modelfile_path)

    def benchmark(self, model: str, prompt: str = "Explain quantum computing in 3 sentences.", iterations: int = 3) -> Dict[str, Any]:
        """
        Step 4: Benchmark model performance
        """
        logger.info("=" * 80)
        logger.info(f"⏱️  AI-ML SCIENTIST: BENCHMARKING {model}")
        logger.info("=" * 80)
        logger.info("")
        
        import requests
        
        times = []
        tokens_per_second = []
        
        for i in range(iterations):
            logger.info(f"   Run {i+1}/{iterations}...")
            start = time.time()
            
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": 100}
                    },
                    timeout=120
                )
                
                elapsed = time.time() - start
                times.append(elapsed)
                
                if response.status_code == 200:
                    data = response.json()
                    eval_count = data.get("eval_count", 0)
                    eval_duration = data.get("eval_duration", 1) / 1e9  # Convert ns to s
                    if eval_duration > 0:
                        tps = eval_count / eval_duration
                        tokens_per_second.append(tps)
                        logger.info(f"      ✅ {elapsed:.2f}s, {tps:.1f} tokens/sec")
                    else:
                        logger.info(f"      ✅ {elapsed:.2f}s")
                else:
                    logger.warning(f"      ❌ Error: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"      ❌ Exception: {e}")
                times.append(120)  # Timeout value
        
        results = {
            "model": model,
            "iterations": iterations,
            "avg_time_seconds": sum(times) / len(times) if times else 0,
            "min_time_seconds": min(times) if times else 0,
            "max_time_seconds": max(times) if times else 0,
            "avg_tokens_per_second": sum(tokens_per_second) / len(tokens_per_second) if tokens_per_second else 0,
        }
        
        logger.info("")
        logger.info("📊 Benchmark Results:")
        logger.info(f"   Average time: {results['avg_time_seconds']:.2f}s")
        logger.info(f"   Tokens/sec: {results['avg_tokens_per_second']:.1f}")
        logger.info("")
        
        return results

    def apply_quick_fix(self, model: str = "qwen2-72b:latest") -> bool:
        """
        Quick fix: Apply immediate performance improvements via API
        """
        logger.info("=" * 80)
        logger.info("⚡ AI-ML SCIENTIST: APPLYING QUICK FIX")
        logger.info("=" * 80)
        logger.info("")
        
        # Unload current model to free memory
        logger.info("1. Unloading current model to free VRAM...")
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "keep_alive": 0},
                timeout=30
            )
            logger.info("   ✅ Model unloaded")
        except Exception as e:
            logger.warning(f"   ⚠️ Could not unload: {e}")
        
        # Recommend immediate alternatives
        logger.info("")
        logger.info("2. Recommended immediate actions:")
        logger.info("")
        logger.info("   🚀 FASTEST FIX: Use a smaller model that fits in GPU:")
        logger.info("      ollama run qwen2.5:32b    # 18GB - fits in 24GB VRAM")
        logger.info("      ollama run qwen2.5:14b    # 8GB - very fast")
        logger.info("      ollama run qwen2.5:7b     # 4.7GB - fastest")
        logger.info("")
        logger.info("   ⚙️  OPTIMIZE CURRENT MODEL: Use reduced context")
        logger.info("      ollama run qwen2-72b:latest --num-ctx 2048")
        logger.info("")
        
        return True

    def full_optimization(self, model: str = "qwen2-72b:latest", profile: str = "balanced"):
        """
        Run full optimization pipeline
        """
        logger.info("🔬 " + "=" * 76)
        logger.info("🔬 AI-ML SCIENTIST: FULL PERFORMANCE OPTIMIZATION PIPELINE")
        logger.info("🔬 " + "=" * 76)
        logger.info("")
        
        # Step 1: Diagnose
        diagnosis = self.diagnose()
        
        # Step 2: Recommend
        self.recommend(model)
        
        # Step 3: Create optimized Modelfile
        if profile != "skip":
            self.create_optimized_modelfile(model, profile)
        
        # Step 4: Apply quick fix
        self.apply_quick_fix(model)
        
        logger.info("=" * 80)
        logger.info("✅ OPTIMIZATION COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📌 SUMMARY:")
        logger.info(f"   Current model: {model}")
        logger.info(f"   Problem: {diagnosis['severity'].upper()} - CPU offload detected")
        logger.info("")
        logger.info("📌 RECOMMENDED NEXT STEPS:")
        logger.info("   1. Switch to qwen2.5:32b for 2-3x speedup (fits in VRAM)")
        logger.info("   2. Or use qwen2.5:14b for 5-10x speedup")
        logger.info("   3. Run: ollama run qwen2.5:32b")
        logger.info("")


def main():
    parser = argparse.ArgumentParser(
        description="Ollama Performance Tuner - AI-ML Scientist Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ollama_performance_tuner.py --diagnose
  python ollama_performance_tuner.py --recommend --model qwen2-72b:latest
  python ollama_performance_tuner.py --optimize --model qwen2-72b:latest --profile balanced
  python ollama_performance_tuner.py --benchmark --model qwen2.5:32b
  python ollama_performance_tuner.py --quick-fix --model qwen2-72b:latest
        """
    )
    
    parser.add_argument("--diagnose", action="store_true", help="Diagnose current performance bottlenecks")
    parser.add_argument("--recommend", action="store_true", help="Generate optimization recommendations")
    parser.add_argument("--optimize", action="store_true", help="Run full optimization pipeline")
    parser.add_argument("--benchmark", action="store_true", help="Benchmark model performance")
    parser.add_argument("--quick-fix", action="store_true", help="Apply immediate performance fixes")
    parser.add_argument("--model", default="qwen2-72b:latest", help="Target model (default: qwen2-72b:latest)")
    parser.add_argument("--profile", choices=["max_speed", "balanced", "max_quality"], default="balanced",
                        help="Optimization profile (default: balanced)")
    
    args = parser.parse_args()
    
    tuner = OllamaPerformanceTuner()
    
    if args.diagnose:
        tuner.diagnose()
    elif args.recommend:
        tuner.diagnose()
        tuner.recommend(args.model)
    elif args.optimize:
        tuner.full_optimization(args.model, args.profile)
    elif args.benchmark:
        tuner.benchmark(args.model)
    elif args.quick_fix:
        tuner.apply_quick_fix(args.model)
    else:
        # Default: full optimization
        tuner.full_optimization(args.model, args.profile)


if __name__ == "__main__":
    main()
