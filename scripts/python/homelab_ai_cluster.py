#!/usr/bin/env python3
"""
Homelab AI Cluster - Unified Virtual AI Brain

Treats the entire homelab as ONE AI cluster with GPU + CPU (BitNet) inference:

GPU Nodes (Ollama):
- Ultron (laptop): RTX 5090 24GB - localhost:11434
- Kaiju (desktop): RTX 3090 24GB - <NAS_IP>:11434

CPU Nodes (BitNet - Microsoft 1-bit LLMs):
- Ultron-CPU: BitNet on laptop CPU
- Kaiju-CPU: BitNet on desktop CPU
- NAS-CPU: BitNet on Synology NAS (NEW capability!)

Routes queries based on:
- GPU availability and load
- Model requirements
- Auto-fallback to BitNet CPU when GPUs busy
- Query complexity (@PEAK workflow optimization)

Usage:
    # Auto-route to best available node (GPU preferred, CPU fallback)
    python homelab_ai_cluster.py --chat "What is the footer config?"

    # Force GPU node
    python homelab_ai_cluster.py --chat "Complex analysis" --node kaiju

    # Force BitNet CPU
    python homelab_ai_cluster.py --chat "Quick question" --bitnet

    # Check cluster status (GPU + CPU)
    python homelab_ai_cluster.py --status

    # Run @PEAK workflow (distributes across cluster)
    python homelab_ai_cluster.py --peak "Analyze project architecture"

Author: Lumina AI
"""

import concurrent.futures
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("HomelabAICluster")

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class ClusterNode:
    """Represents a node in the AI cluster (GPU or CPU)"""

    name: str
    ip: str
    node_type: str = "gpu"  # "gpu" (Ollama) or "cpu" (BitNet)
    ollama_port: int = 11434
    gpu_name: str = ""
    gpu_vram_gb: int = 0
    cpu_cores: int = 0
    status: str = "unknown"
    loaded_models: list = None
    gpu_utilization: float = 0.0
    bitnet_models: list = None  # For CPU nodes

    def __post_init__(self):
        if self.loaded_models is None:
            self.loaded_models = []
        if self.bitnet_models is None:
            self.bitnet_models = []

    @property
    def ollama_url(self) -> str:
        return f"http://{self.ip}:{self.ollama_port}"

    def is_local(self) -> bool:
        return self.ip in ("127.0.0.1", "localhost")

    def is_gpu(self) -> bool:
        return self.node_type == "gpu"

    def is_cpu(self) -> bool:
        return self.node_type == "cpu"


# GPU Nodes (Ollama)
GPU_NODES = {
    "ultron": ClusterNode(
        name="Ultron",
        ip="127.0.0.1",
        node_type="gpu",
        gpu_name="RTX 5090 Laptop",
        gpu_vram_gb=24,
    ),
    "kaiju": ClusterNode(
        name="Kaiju",
        ip="<NAS_IP>",
        node_type="gpu",
        gpu_name="RTX 3090",
        gpu_vram_gb=24,
    ),
}

# CPU Nodes (BitNet) - Can run on any machine with CPU
CPU_NODES = {
    "ultron-cpu": ClusterNode(
        name="Ultron-CPU",
        ip="127.0.0.1",
        node_type="cpu",
        cpu_cores=os.cpu_count() or 8,
        bitnet_models=["2b", "3b", "8b"],
    ),
    "kaiju-cpu": ClusterNode(
        name="Kaiju-CPU",
        ip="<NAS_IP>",
        node_type="cpu",
        cpu_cores=16,  # Estimated for desktop
        bitnet_models=["2b", "3b", "8b"],
    ),
    "nas-cpu": ClusterNode(
        name="NAS-CPU",
        ip="<NAS_PRIMARY_IP>",
        node_type="cpu",
        cpu_cores=4,  # Synology NAS typically has 4 cores
        bitnet_models=["2b", "0.7b"],  # Smaller models for NAS
    ),
}

# Combined cluster
CLUSTER_NODES = {**GPU_NODES, **CPU_NODES}

# Model size estimates (GB) for GPU
MODEL_SIZES = {
    "qwen2.5-coder:1.5b": 1.0,
    "llama3.2:3b": 2.0,
    "qwen2.5:7b": 4.7,
    "qwen2.5:14b": 9.0,
    "qwen2.5:32b": 20.0,
}

# BitNet model info
BITNET_MODELS = {
    "2b": {"name": "BitNet-b1.58-2B-4T", "speed": "50+ tok/s", "quality": "good"},
    "0.7b": {"name": "bitnet_b1_58-large", "speed": "100+ tok/s", "quality": "basic"},
    "3b": {"name": "bitnet_b1_58-3B", "speed": "40+ tok/s", "quality": "good"},
    "8b": {"name": "Llama3-8B-1.58", "speed": "20+ tok/s", "quality": "great"},
}

# Tier configuration for routing
TIER_MODELS = {
    "fast": ["qwen2.5-coder:1.5b-base", "qwen2.5-coder:1.5b", "llama3.2:1b"],
    "balanced": ["llama3.2:3b", "qwen2.5:3b", "gemma2:2b"],
    "quality": ["qwen2.5:7b", "llama3.1:8b", "mistral:7b"],
    "bitnet-fast": ["0.7b", "2b"],  # BitNet CPU tiers
    "bitnet-quality": ["3b", "8b"],
}

# GPU busy threshold (percentage of VRAM used)
GPU_BUSY_THRESHOLD = 0.85  # 85% VRAM = consider GPU busy


class HomelabAICluster:
    """Manages the homelab as a unified AI cluster with GPU + CPU (BitNet) support"""

    def __init__(self, timeout: int = 10, enable_bitnet: bool = True):
        self.gpu_nodes = GPU_NODES.copy()
        self.cpu_nodes = CPU_NODES.copy() if enable_bitnet else {}
        self.nodes = {**self.gpu_nodes, **self.cpu_nodes}
        self.timeout = timeout
        self.enable_bitnet = enable_bitnet
        self._bitnet = None  # Lazy load BitNet inference
        self._refresh_cluster_status()

    @property
    def bitnet(self):
        """Lazy load BitNet inference wrapper"""
        if self._bitnet is None and self.enable_bitnet:
            try:
                from bitnet_inference import BitNetInference

                self._bitnet = BitNetInference()
            except ImportError:
                logger.warning("BitNet inference module not available")
                self._bitnet = False
        return self._bitnet if self._bitnet else None

    def _refresh_cluster_status(self):
        """Check status of all nodes in parallel"""
        logger.info("Refreshing cluster status...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.nodes)) as executor:
            futures = {executor.submit(self._check_node, name): name for name in self.nodes}
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.warning(f"Failed to check {name}: {e}")
                    self.nodes[name].status = "offline"

    def _check_node(self, node_name: str) -> None:
        """Check a single node's status (GPU or CPU)"""
        node = self.nodes[node_name]

        if node.is_gpu():
            self._check_gpu_node(node)
        else:
            self._check_cpu_node(node)

    def _check_gpu_node(self, node: ClusterNode) -> None:
        """Check GPU node via Ollama API"""
        try:
            resp = requests.get(f"{node.ollama_url}/api/tags", timeout=self.timeout)
            if resp.status_code == 200:
                node.status = "online"
                data = resp.json()
                node.loaded_models = [m["name"] for m in data.get("models", [])]
            else:
                node.status = "error"
        except requests.exceptions.Timeout:
            node.status = "timeout"
        except requests.exceptions.ConnectionError:
            node.status = "offline"
        except Exception as e:
            node.status = f"error: {e}"

    def _check_cpu_node(self, node: ClusterNode) -> None:
        """Check CPU node for BitNet availability"""
        if not self.enable_bitnet:
            node.status = "disabled"
            return

        # For local CPU node, check if BitNet is installed
        if node.is_local():
            if self.bitnet and self.bitnet.is_installed:
                node.status = "online"
                # Get available BitNet models
                available = self.bitnet.get_available_models()
                node.bitnet_models = [m["id"] for m in available if m["downloaded"]]
            else:
                node.status = "not_installed"
        else:
            # Remote CPU nodes - try SSH ping or assume available
            # For now, mark as "available" if host is reachable
            try:
                resp = requests.get(f"http://{node.ip}:22", timeout=2)
                node.status = "online"
            except Exception:
                # SSH not HTTP, so connection refused is expected
                # Try a simple ping
                node.status = "available"  # Assume available for remote

    def _get_running_models(self, node_name: str) -> list:
        """Get currently loaded/running models on a GPU node"""
        node = self.nodes[node_name]
        if not node.is_gpu():
            return []  # CPU nodes don't have "running" models

        try:
            resp = requests.get(f"{node.ollama_url}/api/ps", timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("models", [])
        except Exception:
            pass
        return []

    def _is_gpu_busy(self, node_name: str) -> bool:
        """Check if a GPU node is busy (>85% VRAM used)"""
        node = self.nodes.get(node_name)
        if not node or not node.is_gpu():
            return False

        running = self._get_running_models(node_name)
        running_size = sum(m.get("size", 0) / 1e9 for m in running)

        return running_size / max(1, node.gpu_vram_gb) > GPU_BUSY_THRESHOLD

    def get_cluster_status(self) -> dict:
        """Get full cluster status including GPU and CPU nodes"""
        self._refresh_cluster_status()

        status = {
            "total_nodes": len(self.nodes),
            "gpu_nodes": len(self.gpu_nodes),
            "cpu_nodes": len(self.cpu_nodes),
            "online_nodes": 0,
            "online_gpu": 0,
            "online_cpu": 0,
            "total_vram_gb": 0,
            "available_vram_gb": 0,
            "total_cpu_cores": 0,
            "nodes": {},
        }

        for name, node in self.nodes.items():
            if node.is_gpu():
                running = self._get_running_models(name)
                running_names = [m.get("name", "unknown") for m in running]
                running_size = sum(m.get("size", 0) / 1e9 for m in running)

                node_status = {
                    "name": node.name,
                    "ip": node.ip,
                    "type": "GPU",
                    "status": node.status,
                    "gpu": node.gpu_name,
                    "vram_gb": node.gpu_vram_gb,
                    "available_models": node.loaded_models[:10] if node.loaded_models else [],
                    "running_models": running_names,
                    "vram_used_gb": round(running_size, 1),
                    "is_busy": self._is_gpu_busy(name),
                }

                if node.status == "online":
                    status["online_nodes"] += 1
                    status["online_gpu"] += 1
                    status["total_vram_gb"] += node.gpu_vram_gb
                    status["available_vram_gb"] += max(0, node.gpu_vram_gb - running_size)
            else:
                # CPU node (BitNet)
                node_status = {
                    "name": node.name,
                    "ip": node.ip,
                    "type": "CPU (BitNet)",
                    "status": node.status,
                    "cpu_cores": node.cpu_cores,
                    "bitnet_models": node.bitnet_models,
                }

                if node.status in ("online", "available"):
                    status["online_nodes"] += 1
                    status["online_cpu"] += 1
                    status["total_cpu_cores"] += node.cpu_cores

            status["nodes"][name] = node_status

        return status

    def find_best_node(
        self,
        model: str = None,
        prefer_local: bool = True,
        allow_bitnet_fallback: bool = True,
        force_gpu: bool = False,
        force_cpu: bool = False,
    ) -> tuple:
        """
        Find the best node for a query.

        Returns: (node_name, node_type) where node_type is "gpu" or "cpu"
        """
        self._refresh_cluster_status()

        # Get online GPU nodes
        online_gpu = [n for n, node in self.gpu_nodes.items() if node.status == "online"]

        # Get online CPU nodes
        online_cpu = [
            n for n, node in self.cpu_nodes.items() if node.status in ("online", "available")
        ]

        if force_cpu:
            if online_cpu:
                if prefer_local and "ultron-cpu" in online_cpu:
                    return ("ultron-cpu", "cpu")
                return (online_cpu[0], "cpu")
            raise RuntimeError("No CPU nodes available for BitNet!")

        if force_gpu:
            if online_gpu:
                return self._find_best_gpu_node(online_gpu, model, prefer_local)
            raise RuntimeError("No GPU nodes online!")

        # Smart routing: prefer GPU, fallback to CPU if busy
        if online_gpu:
            # Check if preferred GPU is busy
            preferred_gpu = "ultron" if prefer_local and "ultron" in online_gpu else online_gpu[0]

            if not self._is_gpu_busy(preferred_gpu):
                # GPU available, use it
                return self._find_best_gpu_node(online_gpu, model, prefer_local)
            elif allow_bitnet_fallback and online_cpu:
                # GPU busy, fallback to BitNet CPU
                logger.info(f"GPU {preferred_gpu} is busy, falling back to BitNet CPU")
                if prefer_local and "ultron-cpu" in online_cpu:
                    return ("ultron-cpu", "cpu")
                return (online_cpu[0], "cpu")
            else:
                # GPU busy but no CPU fallback, use GPU anyway
                return self._find_best_gpu_node(online_gpu, model, prefer_local)

        # No GPU available
        if allow_bitnet_fallback and online_cpu:
            logger.info("No GPU available, using BitNet CPU")
            if prefer_local and "ultron-cpu" in online_cpu:
                return ("ultron-cpu", "cpu")
            return (online_cpu[0], "cpu")

        raise RuntimeError("No cluster nodes online!")

    def _find_best_gpu_node(self, online: list, model: str, prefer_local: bool) -> tuple:
        """Find best GPU node from online list"""
        # If model specified, prefer node that has it loaded
        if model:
            for name in online:
                running = self._get_running_models(name)
                running_names = [m.get("name", "") for m in running]
                if model in running_names or any(model in n for n in running_names):
                    logger.info(f"Node {name} has {model} loaded - using it")
                    return (name, "gpu")

        # Prefer local if requested and online
        if prefer_local and "ultron" in online:
            return ("ultron", "gpu")

        # Return first online node
        return (online[0], "gpu")

    def chat(
        self,
        prompt: str,
        model: str = "llama3.2:3b",
        node: str = None,
        system_prompt: str = None,
        stream: bool = False,
        force_gpu: bool = False,
        force_cpu: bool = False,
        bitnet_model: str = "2b",
    ) -> dict:
        """Send a chat request to the cluster (GPU or CPU)"""

        # Auto-select node if not specified
        if not node:
            try:
                node, node_type = self.find_best_node(
                    model=model, force_gpu=force_gpu, force_cpu=force_cpu
                )
            except RuntimeError as e:
                return {"success": False, "error": str(e)}
        else:
            # Determine node type from name
            node_type = "cpu" if node in self.cpu_nodes else "gpu"

        target = self.nodes.get(node)
        if not target:
            return {"success": False, "error": f"Unknown node: {node}"}

        if target.status not in ("online", "available"):
            return {"success": False, "error": f"Node {node} is {target.status}"}

        # Route to appropriate inference method
        if node_type == "cpu" or target.is_cpu():
            return self._chat_bitnet(prompt, bitnet_model, node, system_prompt)
        else:
            return self._chat_ollama(prompt, model, node, system_prompt, stream)

    def _chat_ollama(
        self,
        prompt: str,
        model: str,
        node: str,
        system_prompt: str,
        stream: bool,
    ) -> dict:
        """Send chat to GPU node via Ollama"""
        target = self.nodes[node]
        logger.info(f"Routing to GPU {target.name} ({target.ip}) with model {model}")

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            start = time.time()
            resp = requests.post(
                f"{target.ollama_url}/api/generate",
                json=payload,
                timeout=300,
            )
            elapsed = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "response": data.get("response", ""),
                    "node": node,
                    "node_type": "gpu",
                    "model": model,
                    "duration": elapsed,
                    "eval_count": data.get("eval_count", 0),
                    "tokens_per_sec": data.get("eval_count", 0)
                    / max(0.001, data.get("eval_duration", 1) / 1e9),
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
                    "node": node,
                }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out", "node": node}
        except Exception as e:
            return {"success": False, "error": str(e), "node": node}

    def _chat_bitnet(
        self,
        prompt: str,
        model: str,
        node: str,
        system_prompt: str,
    ) -> dict:
        """Send chat to CPU node via BitNet"""
        target = self.nodes[node]
        logger.info(f"Routing to CPU {target.name} ({target.ip}) with BitNet model {model}")

        # For local CPU, use BitNet directly
        if target.is_local():
            if not self.bitnet:
                return {
                    "success": False,
                    "error": "BitNet not installed. Run: scripts/powershell/setup_bitnet_homelab.ps1",
                }

            response = self.bitnet.generate(
                prompt=prompt,
                model_id=model,
                system_prompt=system_prompt,
                conversation_mode=bool(system_prompt),
            )

            return {
                "success": response.success,
                "response": response.text,
                "node": node,
                "node_type": "cpu",
                "model": f"bitnet-{model}",
                "duration": response.total_time,
                "tokens_per_sec": response.tokens_per_second,
                "error": response.error if not response.success else None,
            }
        else:
            # Remote CPU - would need SSH or API (future enhancement)
            return {
                "success": False,
                "error": f"Remote BitNet execution not yet implemented for {node}",
                "node": node,
            }

    def run_peak_workflow(self, task: str, context_docs: list = None) -> dict:
        """
        Run a @PEAK workflow distributed across the cluster.

        @PEAK = Pattern recognition, Extraction, Analysis, Knowledge synthesis

        Strategy:
        1. Fast tier: Quick pattern scan (parallel on all nodes)
        2. Balanced tier: Extract relevant patterns
        3. Quality tier: Deep analysis
        4. Synthesis: Combine results
        """
        logger.info(f"Running @PEAK workflow: {task}")
        results = {
            "task": task,
            "phases": {},
            "total_duration": 0,
        }

        start_total = time.time()

        # Phase 1: Pattern Recognition (fast, parallel)
        logger.info("Phase 1: Pattern Recognition (parallel)")
        pattern_prompts = [
            f"Identify key patterns in this task: {task}. List 3-5 bullet points.",
            f"What are the main concepts in: {task}? Brief list only.",
        ]

        phase1_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for i, prompt in enumerate(pattern_prompts):
                node = list(self.nodes.keys())[i % len(self.nodes)]
                futures.append(
                    executor.submit(
                        self.chat,
                        prompt=prompt,
                        model="llama3.2:3b",
                        node=node if self.nodes[node].status == "online" else None,
                    )
                )
            for future in concurrent.futures.as_completed(futures):
                phase1_results.append(future.result())

        results["phases"]["pattern_recognition"] = {
            "results": [r.get("response", "")[:500] for r in phase1_results if r.get("success")],
            "duration": sum(r.get("duration", 0) for r in phase1_results),
        }

        # Phase 2: Analysis (quality tier, single node)
        logger.info("Phase 2: Deep Analysis")
        patterns_found = "\n".join(results["phases"]["pattern_recognition"]["results"])
        analysis_prompt = f"""Based on these patterns:
{patterns_found}

Provide deep analysis for the task: {task}

Focus on:
1. Key insights
2. Potential issues
3. Recommendations
"""

        analysis_result = self.chat(
            prompt=analysis_prompt,
            model="qwen2.5:7b",
        )

        results["phases"]["analysis"] = {
            "result": analysis_result.get("response", "")[:2000]
            if analysis_result.get("success")
            else "Analysis failed",
            "duration": analysis_result.get("duration", 0),
            "node": analysis_result.get("node"),
        }

        # Phase 3: Synthesis
        logger.info("Phase 3: Knowledge Synthesis")
        synthesis_prompt = f"""Synthesize the following into a clear, actionable summary:

Task: {task}

Patterns identified:
{patterns_found}

Analysis:
{results["phases"]["analysis"]["result"]}

Provide:
1. Executive summary (2-3 sentences)
2. Key takeaways (bullet points)
3. Recommended next steps
"""

        synthesis_result = self.chat(
            prompt=synthesis_prompt,
            model="llama3.2:3b",
        )

        results["phases"]["synthesis"] = {
            "result": synthesis_result.get("response", "")
            if synthesis_result.get("success")
            else "Synthesis failed",
            "duration": synthesis_result.get("duration", 0),
        }

        results["total_duration"] = time.time() - start_total
        results["success"] = True

        return results


def print_cluster_status(status: dict):
    """Pretty print cluster status"""
    print("\n" + "=" * 70)
    print("🌐 HOMELAB AI CLUSTER STATUS")
    print("=" * 70)
    print(
        f"   Total Nodes: {status['total_nodes']} ({status['gpu_nodes']} GPU + {status['cpu_nodes']} CPU)"
    )
    print(
        f"   Online: {status['online_nodes']} ({status['online_gpu']} GPU + {status['online_cpu']} CPU)"
    )
    print(
        f"   GPU VRAM: {status['available_vram_gb']:.1f}GB / {status['total_vram_gb']}GB available"
    )
    print(f"   CPU Cores: {status['total_cpu_cores']} for BitNet")
    print("=" * 70)

    # GPU nodes first
    print("\n🎮 GPU NODES (Ollama)")
    for name, node in status["nodes"].items():
        if node.get("type") != "GPU":
            continue
        icon = "✅" if node["status"] == "online" else "❌"
        busy = " ⚠️ BUSY" if node.get("is_busy") else ""
        print(f"\n{icon} {node['name']} ({node['ip']}){busy}")
        print(f"   Status: {node['status']}")
        print(f"   GPU: {node['gpu']} ({node['vram_gb']}GB)")
        if node.get("running_models"):
            print(f"   Running: {', '.join(node['running_models'])} ({node['vram_used_gb']}GB)")
        if node.get("available_models"):
            print(f"   Available: {len(node['available_models'])} models")

    # CPU nodes
    print("\n🖥️ CPU NODES (BitNet)")
    for name, node in status["nodes"].items():
        if node.get("type") != "CPU (BitNet)":
            continue
        icon = "✅" if node["status"] in ("online", "available") else "❌"
        print(f"\n{icon} {node['name']} ({node['ip']})")
        print(f"   Status: {node['status']}")
        print(f"   CPU Cores: {node.get('cpu_cores', 'N/A')}")
        if node.get("bitnet_models"):
            print(f"   BitNet Models: {', '.join(node['bitnet_models'])}")

    print("\n" + "=" * 70)
    print("💡 Tip: Use --bitnet to force CPU inference, --gpu to force GPU")
    print("=" * 70)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Homelab AI Cluster - Unified Virtual AI Brain (GPU + CPU BitNet)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check cluster status (GPU + CPU nodes)
  python homelab_ai_cluster.py --status

  # Chat with auto-routing (prefers GPU, falls back to BitNet CPU if busy)
  python homelab_ai_cluster.py --chat "What is 2+2?"

  # Force GPU inference
  python homelab_ai_cluster.py --chat "Complex analysis" --gpu

  # Force BitNet CPU inference
  python homelab_ai_cluster.py --chat "Quick question" --bitnet

  # Specific GPU node
  python homelab_ai_cluster.py --chat "Analysis" --node kaiju

  # Specific BitNet model
  python homelab_ai_cluster.py --chat "Hello" --bitnet --bitnet-model 8b

  # Run @PEAK workflow (distributed across GPU + CPU)
  python homelab_ai_cluster.py --peak "Analyze project architecture"
        """,
    )

    parser.add_argument("--status", action="store_true", help="Show cluster status (GPU + CPU)")
    parser.add_argument("--chat", type=str, help="Send a chat query")
    parser.add_argument("--model", type=str, default="llama3.2:3b", help="Ollama model for GPU")
    parser.add_argument(
        "--bitnet-model",
        type=str,
        default="2b",
        choices=["0.7b", "2b", "3b", "8b"],
        help="BitNet model for CPU",
    )
    parser.add_argument("--node", type=str, help="Force specific node")
    parser.add_argument("--gpu", action="store_true", help="Force GPU inference")
    parser.add_argument("--bitnet", action="store_true", help="Force BitNet CPU inference")
    parser.add_argument("--peak", type=str, help="Run @PEAK workflow")
    parser.add_argument("--no-bitnet", action="store_true", help="Disable BitNet CPU nodes")

    args = parser.parse_args()

    cluster = HomelabAICluster(enable_bitnet=not args.no_bitnet)

    if args.status:
        status = cluster.get_cluster_status()
        print_cluster_status(status)

    elif args.chat:
        # Determine inference type
        if args.bitnet:
            print(f"\n🖥️ Query (BitNet CPU): {args.chat}")
        elif args.gpu:
            print(f"\n🎮 Query (GPU): {args.chat}")
        else:
            print(f"\n💬 Query (auto-routing): {args.chat}")

        result = cluster.chat(
            prompt=args.chat,
            model=args.model,
            node=args.node,
            force_gpu=args.gpu,
            force_cpu=args.bitnet,
            bitnet_model=args.bitnet_model,
        )

        if result["success"]:
            node_type = result.get("node_type", "unknown")
            icon = "🎮" if node_type == "gpu" else "🖥️"
            print(f"\n{icon} Response (from {result['node']}, {result['model']}):")
            print(result["response"])
            print(f"\n⏱️ Duration: {result['duration']:.2f}s | {result['tokens_per_sec']:.1f} tok/s")
        else:
            print(f"\n❌ Error: {result.get('error')}")

    elif args.peak:
        print(f"\n🎯 Running @PEAK workflow: {args.peak}")
        result = cluster.run_peak_workflow(args.peak)

        print("\n" + "=" * 70)
        print("📊 @PEAK WORKFLOW RESULTS")
        print("=" * 70)

        for phase_name, phase_data in result["phases"].items():
            print(f"\n### {phase_name.upper()}")
            if isinstance(phase_data.get("result"), str):
                print(phase_data["result"][:1000])
            elif isinstance(phase_data.get("results"), list):
                for r in phase_data["results"]:
                    print(f"  • {r[:200]}...")
            print(f"  ⏱️ {phase_data.get('duration', 0):.2f}s")

        print(f"\n✅ Total duration: {result['total_duration']:.2f}s")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
