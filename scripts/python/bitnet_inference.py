#!/usr/bin/env python3
"""
BitNet Inference Wrapper - Microsoft 1-bit LLM Integration

Enables CPU-based LLM inference using Microsoft's BitNet framework:
- 100B models at 5-7 tokens/sec on CPU
- 2.37x to 6.17x faster than standard CPU inference
- 71.9%-82.2% energy reduction
- Works on NAS, laptops, desktops - any x86/ARM CPU

Usage:
    from bitnet_inference import BitNetInference

    bitnet = BitNetInference()
    response = bitnet.generate("What is the capital of France?")

    # Or via CLI
    python bitnet_inference.py --prompt "Hello world" --model 2b

Author: Lumina AI
"""

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("BitNetInference")

# Default paths - check NAS first, then local
NAS_MODELS_DIR = Path("M:/models/bitnet")
BITNET_DIR = Path(os.environ.get("BITNET_DIR", Path.home() / "bitnet"))
LOCAL_MODELS_DIR = BITNET_DIR / "models"

# Use NAS if available, otherwise local
MODELS_DIR = NAS_MODELS_DIR if NAS_MODELS_DIR.exists() else LOCAL_MODELS_DIR

# Available BitNet models
BITNET_MODELS = {
    "2b": {
        "name": "BitNet-b1.58-2B-4T",
        "hf_repo": "microsoft/BitNet-b1.58-2B-4T-gguf",
        "params": "2.4B",
        "speed_estimate": "50+ tok/s",
        "quality": "good",
        "recommended_threads": 8,
    },
    "0.7b": {
        "name": "bitnet_b1_58-large",
        "hf_repo": "1bitLLM/bitnet_b1_58-large",
        "params": "0.7B",
        "speed_estimate": "100+ tok/s",
        "quality": "basic",
        "recommended_threads": 4,
    },
    "3b": {
        "name": "bitnet_b1_58-3B",
        "hf_repo": "1bitLLM/bitnet_b1_58-3B",
        "params": "3.3B",
        "speed_estimate": "40+ tok/s",
        "quality": "good",
        "recommended_threads": 8,
    },
    "8b": {
        "name": "Llama3-8B-1.58-100B-tokens",
        "hf_repo": "HF1BitLLM/Llama3-8B-1.58-100B-tokens",
        "params": "8B",
        "speed_estimate": "20+ tok/s",
        "quality": "great",
        "recommended_threads": 16,
    },
    "falcon-3b": {
        "name": "Falcon3-3B-Instruct-1.58bit",
        "hf_repo": "tiiuae/Falcon3-3B-Instruct-1.58bit",
        "params": "3B",
        "speed_estimate": "40+ tok/s",
        "quality": "good",
        "recommended_threads": 8,
    },
    "falcon-7b": {
        "name": "Falcon3-7B-Instruct-1.58bit",
        "hf_repo": "tiiuae/Falcon3-7B-Instruct-1.58bit",
        "params": "7B",
        "speed_estimate": "25+ tok/s",
        "quality": "great",
        "recommended_threads": 12,
    },
}


@dataclass
class BitNetResponse:
    """Response from BitNet inference"""

    text: str
    tokens_generated: int
    tokens_per_second: float
    total_time: float
    model: str
    success: bool
    error: Optional[str] = None


class BitNetInference:
    """
    BitNet inference wrapper for CPU-based LLM inference.

    Uses Microsoft's bitnet.cpp for efficient 1-bit model inference.
    """

    def __init__(
        self,
        bitnet_dir: Optional[Path] = None,
        default_model: str = "2b",
        default_threads: Optional[int] = None,
    ):
        self.bitnet_dir = Path(bitnet_dir) if bitnet_dir else BITNET_DIR
        self.models_dir = self.bitnet_dir / "models"
        self.default_model = default_model
        self.default_threads = default_threads or os.cpu_count() or 8

        # Check if BitNet is installed
        self.is_installed = self._check_installation()

    def _check_installation(self) -> bool:
        """Check if BitNet is properly installed"""
        if not self.bitnet_dir.exists():
            logger.warning(f"BitNet not found at {self.bitnet_dir}")
            return False

        # Check for compiled llama-cli.exe
        llama_cli = self.bitnet_dir / "build" / "bin" / "llama-cli.exe"
        if llama_cli.exists():
            self.llama_cli_path = llama_cli
            return True

        # Fallback: check for run_inference.py
        inference_script = self.bitnet_dir / "run_inference.py"
        if inference_script.exists():
            self.llama_cli_path = None  # Use Python script
            return True

        logger.warning("BitNet llama-cli.exe or run_inference.py not found")
        return False

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available/downloaded models"""
        available = []

        for model_id, model_info in BITNET_MODELS.items():
            model_path = self.models_dir / model_info["name"]
            gguf_files = list(model_path.glob("*.gguf")) if model_path.exists() else []

            available.append(
                {
                    "id": model_id,
                    "name": model_info["name"],
                    "params": model_info["params"],
                    "speed": model_info["speed_estimate"],
                    "quality": model_info["quality"],
                    "downloaded": len(gguf_files) > 0,
                    "path": str(model_path) if gguf_files else None,
                    "gguf_file": str(gguf_files[0]) if gguf_files else None,
                }
            )

        return available

    def is_model_available(self, model_id: str) -> bool:
        """Check if a specific model is downloaded and ready"""
        if model_id not in BITNET_MODELS:
            return False

        model_info = BITNET_MODELS[model_id]
        model_path = self.models_dir / model_info["name"]
        gguf_files = list(model_path.glob("*.gguf")) if model_path.exists() else []

        return len(gguf_files) > 0

    def download_model(self, model_id: str = "2b") -> bool:
        """Download a BitNet model from HuggingFace"""
        if model_id not in BITNET_MODELS:
            logger.error(f"Unknown model: {model_id}")
            return False

        model_info = BITNET_MODELS[model_id]
        model_path = self.models_dir / model_info["name"]

        logger.info(f"Downloading {model_info['name']} from {model_info['hf_repo']}...")

        try:
            # Use huggingface-cli to download
            subprocess.run(
                [
                    "huggingface-cli",
                    "download",
                    model_info["hf_repo"],
                    "--local-dir",
                    str(model_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(f"Model downloaded to {model_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download model: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("huggingface-cli not found. Install with: pip install huggingface_hub")
            return False

    def generate(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        max_tokens: int = 256,
        temperature: float = 0.7,
        threads: Optional[int] = None,
        system_prompt: Optional[str] = None,
        conversation_mode: bool = False,
    ) -> BitNetResponse:
        """
        Generate text using BitNet model.

        Args:
            prompt: The input prompt
            model_id: Model to use (default: self.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            threads: Number of CPU threads
            system_prompt: System prompt for chat mode
            conversation_mode: Enable conversation/chat mode

        Returns:
            BitNetResponse with generated text and stats
        """
        if not self.is_installed:
            return BitNetResponse(
                text="",
                tokens_generated=0,
                tokens_per_second=0,
                total_time=0,
                model="",
                success=False,
                error="BitNet not installed. Run: scripts/powershell/setup_bitnet_homelab.ps1 -InstallDependencies",
            )

        model_id = model_id or self.default_model
        threads = threads or self.default_threads

        if not self.is_model_available(model_id):
            return BitNetResponse(
                text="",
                tokens_generated=0,
                tokens_per_second=0,
                total_time=0,
                model=model_id,
                success=False,
                error=f"Model {model_id} not downloaded. Run: scripts/powershell/setup_bitnet_homelab.ps1 -DownloadModels",
            )

        model_info = BITNET_MODELS[model_id]
        model_path = self.models_dir / model_info["name"]
        gguf_files = list(model_path.glob("*.gguf"))

        if not gguf_files:
            return BitNetResponse(
                text="",
                tokens_generated=0,
                tokens_per_second=0,
                total_time=0,
                model=model_id,
                success=False,
                error=f"No GGUF file found for model {model_id}",
            )

        gguf_file = gguf_files[0]

        # Build command - prefer compiled llama-cli.exe
        if hasattr(self, 'llama_cli_path') and self.llama_cli_path and self.llama_cli_path.exists():
            # Use compiled llama-cli.exe
            cmd = [
                str(self.llama_cli_path),
                "-m", str(gguf_file),
                "-n", str(max_tokens),
                "-p", system_prompt or prompt if system_prompt else prompt,
                "-t", str(threads),
                "--temp", str(temperature),
                "--no-display-prompt",  # Only show generated text
            ]
            logger.info(f"Running BitNet via llama-cli: {model_info['name']} with {threads} threads")
        else:
            # Fallback to Python script
            cmd = [
                "python",
                str(self.bitnet_dir / "run_inference.py"),
                "-m", str(gguf_file),
                "-n", str(max_tokens),
                "-p", system_prompt or prompt if system_prompt else prompt,
                "-t", str(threads),
                "-temp", str(temperature),
            ]
            if conversation_mode or system_prompt:
                cmd.append("-cnv")
            logger.info(f"Running BitNet via Python: {model_info['name']} with {threads} threads")

        try:
            start_time = time.time()

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.bitnet_dir),
            )

            total_time = time.time() - start_time

            if result.returncode != 0:
                return BitNetResponse(
                    text="",
                    tokens_generated=0,
                    tokens_per_second=0,
                    total_time=total_time,
                    model=model_id,
                    success=False,
                    error=f"BitNet error: {result.stderr[:500]}",
                )

            # Parse output
            output = result.stdout.strip()
            stderr = result.stderr

            # Try to extract actual performance from llama-cli output
            tokens_generated = max_tokens
            tokens_per_second = 0.0

            # Look for performance line like "eval time = 1476.06 ms / 19 runs ( 77.69 ms per token, 12.87 tokens per second)"
            import re
            perf_match = re.search(r'(\d+\.?\d*)\s*tokens per second', stderr)
            if perf_match:
                tokens_per_second = float(perf_match.group(1))

            tokens_match = re.search(r'eval time.*?/\s*(\d+)\s*runs', stderr)
            if tokens_match:
                tokens_generated = int(tokens_match.group(1))

            # Fallback estimate
            if tokens_per_second == 0:
                tokens_generated = len(output) // 4
                tokens_per_second = tokens_generated / max(0.1, total_time)

            return BitNetResponse(
                text=output,
                tokens_generated=tokens_generated,
                tokens_per_second=tokens_per_second,
                total_time=total_time,
                model=model_id,
                success=True,
            )

        except subprocess.TimeoutExpired:
            return BitNetResponse(
                text="",
                tokens_generated=0,
                tokens_per_second=0,
                total_time=300,
                model=model_id,
                success=False,
                error="Inference timed out (>5 minutes)",
            )
        except Exception as e:
            return BitNetResponse(
                text="",
                tokens_generated=0,
                tokens_per_second=0,
                total_time=0,
                model=model_id,
                success=False,
                error=str(e),
            )

    def benchmark(
        self, model_id: str = "2b", prompt_tokens: int = 512, gen_tokens: int = 128
    ) -> Dict[str, Any]:
        """Run a benchmark on a BitNet model"""
        if not self.is_installed:
            return {"success": False, "error": "BitNet not installed"}

        if not self.is_model_available(model_id):
            return {"success": False, "error": f"Model {model_id} not available"}

        model_info = BITNET_MODELS[model_id]
        model_path = self.models_dir / model_info["name"]
        gguf_files = list(model_path.glob("*.gguf"))

        if not gguf_files:
            return {"success": False, "error": "No GGUF file found"}

        cmd = [
            "python",
            str(self.bitnet_dir / "utils" / "e2e_benchmark.py"),
            "-m",
            str(gguf_files[0]),
            "-p",
            str(prompt_tokens),
            "-n",
            str(gen_tokens),
            "-t",
            str(self.default_threads),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.bitnet_dir),
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


def get_bitnet_status() -> Dict[str, Any]:
    """Get BitNet installation and model status"""
    bitnet = BitNetInference()

    return {
        "installed": bitnet.is_installed,
        "bitnet_dir": str(bitnet.bitnet_dir),
        "models_dir": str(bitnet.models_dir),
        "available_models": bitnet.get_available_models(),
        "cpu_threads": os.cpu_count(),
    }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="BitNet Inference - Microsoft 1-bit LLM CPU Inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check status
  python bitnet_inference.py --status

  # List models
  python bitnet_inference.py --list-models

  # Generate text
  python bitnet_inference.py --prompt "What is AI?" --model 2b

  # Run benchmark
  python bitnet_inference.py --benchmark --model 2b
        """,
    )

    parser.add_argument("--status", action="store_true", help="Show BitNet status")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--prompt", type=str, help="Generate text from prompt")
    parser.add_argument("--model", type=str, default="2b", help="Model to use (default: 2b)")
    parser.add_argument("--max-tokens", type=int, default=256, help="Max tokens to generate")
    parser.add_argument("--threads", type=int, help="CPU threads to use")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    parser.add_argument("--download", type=str, help="Download a model by ID")

    args = parser.parse_args()

    bitnet = BitNetInference()

    if args.status:
        status = get_bitnet_status()
        print("\n" + "=" * 60)
        print("BITNET STATUS")
        print("=" * 60)
        print(f"  Installed: {'✅' if status['installed'] else '❌'}")
        print(f"  Directory: {status['bitnet_dir']}")
        print(f"  CPU Threads: {status['cpu_threads']}")
        print("\n  Models:")
        for model in status["available_models"]:
            icon = "✅" if model["downloaded"] else "⬜"
            print(
                f"    {icon} {model['id']}: {model['name']} ({model['params']}) - {model['quality']}"
            )
        print("=" * 60)

    elif args.list_models:
        models = bitnet.get_available_models()
        print("\n" + "=" * 60)
        print("AVAILABLE BITNET MODELS")
        print("=" * 60)
        for model in models:
            icon = "✅" if model["downloaded"] else "⬜"
            print(f"\n{icon} {model['id']}")
            print(f"   Name: {model['name']}")
            print(f"   Params: {model['params']}")
            print(f"   Speed: {model['speed']}")
            print(f"   Quality: {model['quality']}")
            if model["downloaded"]:
                print(f"   Path: {model['path']}")
        print("\n" + "=" * 60)

    elif args.download:
        success = bitnet.download_model(args.download)
        if success:
            print(f"✅ Model {args.download} downloaded successfully")
        else:
            print(f"❌ Failed to download model {args.download}")

    elif args.benchmark:
        print(f"\n🔬 Running benchmark for model: {args.model}")
        result = bitnet.benchmark(args.model)
        if result["success"]:
            print(result["output"])
        else:
            print(f"❌ Benchmark failed: {result['error']}")

    elif args.prompt:
        print(f"\n💬 Generating with {args.model}...")
        response = bitnet.generate(
            prompt=args.prompt,
            model_id=args.model,
            max_tokens=args.max_tokens,
            threads=args.threads,
        )

        if response.success:
            print(f"\n🤖 Response:\n{response.text}")
            print(f"\n⏱️ Time: {response.total_time:.2f}s | {response.tokens_per_second:.1f} tok/s")
        else:
            print(f"\n❌ Error: {response.error}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
