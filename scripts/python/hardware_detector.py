#!/usr/bin/env python3
"""
Hardware Detection for LLM Optimization

Detects laptop hardware specifications and recommends optimal LLM configuration.
"""

import os
import platform
import subprocess
import json
from typing import Dict, Any, Optional
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("hardware_detector")




# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class HardwareDetector:
    """Detects hardware specifications for LLM optimization"""

    def __init__(self):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent.parent.parent

    def detect_hardware(self) -> Dict[str, Any]:
        """Detect all hardware specifications"""
        hardware = {
            "system": self.system,
            "cpu": self._detect_cpu(),
            "gpu": self._detect_gpu(),
            "memory": self._detect_memory(),
            "storage": self._detect_storage(),
            "recommendations": {}
        }

        hardware["recommendations"] = self._generate_recommendations(hardware)
        return hardware

    def _detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU information"""
        try:
            if self.system == "windows":
                # Use PowerShell for Windows
                cmd = ["powershell", "-Command",
                       "Get-WmiObject Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed | ConvertTo-Json"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                cpu_data = json.loads(result.stdout.strip())

                if isinstance(cpu_data, list):
                    cpu_data = cpu_data[0]

                return {
                    "name": cpu_data.get("Name", "Unknown").strip(),
                    "cores": cpu_data.get("NumberOfCores", 0),
                    "logical_processors": cpu_data.get("NumberOfLogicalProcessors", 0),
                    "max_clock_speed": cpu_data.get("MaxClockSpeed", 0),
                    "architecture": platform.machine()
                }
            else:
                # Linux/Mac detection
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()

                cores = len([line for line in cpuinfo.split('\n') if line.startswith('processor')])
                model_name = ""
                for line in cpuinfo.split('\n'):
                    if line.startswith('model name'):
                        model_name = line.split(':')[1].strip()
                        break

                return {
                    "name": model_name,
                    "cores": cores,
                    "logical_processors": cores,
                    "max_clock_speed": 0,  # Would need additional parsing
                    "architecture": platform.machine()
                }
        except Exception as e:
            print(f"Warning: CPU detection failed: {e}")
            return {
                "name": "Unknown",
                "cores": 4,
                "logical_processors": 4,
                "max_clock_speed": 0,
                "architecture": platform.machine()
            }

    def _detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU information"""
        try:
            if self.system == "windows":
                # PowerShell GPU detection
                cmd = ["powershell", "-Command",
                       "Get-WmiObject Win32_VideoController | Where-Object {$_.AdapterRAM -gt 0} | Select-Object Name,AdapterRAM,DriverVersion | ConvertTo-Json"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    gpu_data = json.loads(result.stdout.strip())
                    if isinstance(gpu_data, list):
                        gpu_data = gpu_data[0] if gpu_data else {}

                    adapter_ram = gpu_data.get("AdapterRAM", 0)
                    if isinstance(adapter_ram, str):
                        adapter_ram = int(adapter_ram) if adapter_ram.isdigit() else 0

                    return {
                        "name": gpu_data.get("Name", "Unknown").strip(),
                        "vram_gb": round(adapter_ram / (1024**3), 1) if adapter_ram > 0 else 0,
                        "driver_version": gpu_data.get("DriverVersion", "Unknown"),
                        "available": True
                    }

            # Fallback for Linux/Mac or failed Windows detection
            return self._detect_gpu_fallback()

        except Exception as e:
            print(f"Warning: GPU detection failed: {e}")
            return self._detect_gpu_fallback()

    def _detect_gpu_fallback(self) -> Dict[str, Any]:
        """Fallback GPU detection"""
        try:
            # Try nvidia-smi for NVIDIA GPUs
            result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    name, vram_mb = lines[0].split(',')
                    return {
                        "name": name.strip(),
                        "vram_gb": round(float(vram_mb) / 1024, 1),
                        "driver_version": "NVIDIA",
                        "available": True
                    }
        except:
            pass

        return {
            "name": "Unknown/Integrated",
            "vram_gb": 0,
            "driver_version": "Unknown",
            "available": False
        }

    def _detect_memory(self) -> Dict[str, Any]:
        """Detect system memory"""
        try:
            if self.system == "windows":
                cmd = ["powershell", "-Command",
                       "Get-WmiObject Win32_ComputerSystem | Select-Object TotalPhysicalMemory | ConvertTo-Json"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                mem_data = json.loads(result.stdout.strip())

                if isinstance(mem_data, list):
                    mem_data = mem_data[0]

                total_bytes = mem_data.get("TotalPhysicalMemory", 0)
                if isinstance(total_bytes, str):
                    total_bytes = int(total_bytes) if total_bytes.isdigit() else 0

                return {
                    "total_gb": round(total_bytes / (1024**3), 1),
                    "available_for_llm": round(total_bytes * 0.8 / (1024**3), 1)  # 80% for LLM
                }
            else:
                # Linux/Mac
                with open("/proc/meminfo", "r") as f:
                    meminfo = f.read()

                total_kb = 0
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        total_kb = int(line.split()[1])
                        break

                total_gb = round(total_kb / (1024**2), 1)
                return {
                    "total_gb": total_gb,
                    "available_for_llm": round(total_gb * 0.8, 1)
                }
        except Exception as e:
            print(f"Warning: Memory detection failed: {e}")
            return {"total_gb": 16, "available_for_llm": 12.8}

    def _detect_storage(self) -> Dict[str, Any]:
        """Detect storage information"""
        try:
            if self.system == "windows":
                cmd = ["powershell", "-Command",
                       "Get-WmiObject Win32_LogicalDisk -Filter 'DeviceID=\"C:\"' | Select-Object Size,FreeSpace | ConvertTo-Json"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    storage_data = json.loads(result.stdout.strip())
                    if isinstance(storage_data, list):
                        storage_data = storage_data[0]

                    size = storage_data.get("Size", 0)
                    free = storage_data.get("FreeSpace", 0)

                    return {
                        "total_gb": round(size / (1024**3), 1),
                        "free_gb": round(free / (1024**3), 1),
                        "available_for_models": round(free * 0.5 / (1024**3), 1)  # 50% for models
                    }

            # Fallback
            stat = os.statvfs('/')
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_available * stat.f_frsize

            return {
                "total_gb": round(total / (1024**3), 1),
                "free_gb": round(free / (1024**3), 1),
                "available_for_models": round(free * 0.5 / (1024**3), 1)
            }
        except Exception as e:
            print(f"Warning: Storage detection failed: {e}")
            return {"total_gb": 500, "free_gb": 200, "available_for_models": 100}

    def _generate_recommendations(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LLM recommendations based on hardware"""

        cpu_cores = hardware["cpu"]["cores"]
        gpu_vram = hardware["gpu"]["vram_gb"]
        memory_gb = hardware["memory"]["total_gb"]

        # Model size recommendations based on hardware
        if gpu_vram >= 24:  # RTX 5090 level
            model_size = "70B-405B"
            quantization = "FP16/GPTQ"
            context_length = 32768
        elif gpu_vram >= 16:  # RTX 4090 level
            model_size = "30B-70B"
            quantization = "GPTQ/FP16"
            context_length = 16384
        elif gpu_vram >= 12:  # RTX 4080 level
            model_size = "13B-30B"
            quantization = "GPTQ/FP16"
            context_length = 8192
        elif gpu_vram >= 8:  # RTX 4070 level
            model_size = "7B-13B"
            quantization = "GPTQ"
            context_length = 4096
        elif memory_gb >= 32:  # High memory, no good GPU
            model_size = "13B-30B"
            quantization = "GPTQ"
            context_length = 4096
        else:  # Standard configs
            model_size = "7B-13B"
            quantization = "GPTQ"
            context_length = 2048

        # Docker resource limits
        cpu_limit = min(cpu_cores, 16)  # Max 16 cores for stability
        memory_limit = min(memory_gb * 0.8, 64)  # Max 64GB, 80% of system
        gpu_layers = min(int(gpu_vram * 1.5), 50) if gpu_vram > 0 else 0

        return {
            "model_size": model_size,
            "quantization": quantization,
            "context_length": context_length,
            "docker_resources": {
                "cpu_limit": cpu_limit,
                "memory_limit_gb": memory_limit,
                "gpu_layers": gpu_layers,
                "num_threads": min(cpu_cores, 16)
            },
            "recommended_models": self._get_recommended_models(hardware),
            "performance_tips": self._get_performance_tips(hardware)
        }

    def _get_recommended_models(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Get recommended models based on hardware"""
        gpu_vram = hardware["gpu"]["vram_gb"]
        memory_gb = hardware["memory"]["total_gb"]

        if gpu_vram >= 24:  # RTX 5090
            return {
                "primary": "Meta-Llama-3.1-70B-Instruct",
                "fallback": "Meta-Llama-3.1-8B-Instruct",
                "quantization": "FP16",
                "max_context": 32768
            }
        elif gpu_vram >= 16:  # RTX 4090 level
            return {
                "primary": "Meta-Llama-3.1-70B-Instruct-Q4",
                "fallback": "Meta-Llama-3.1-8B-Instruct",
                "quantization": "Q4_K_M",
                "max_context": 16384
            }
        elif gpu_vram >= 8:  # RTX 4070 level
            return {
                "primary": "Meta-Llama-3.1-8B-Instruct",
                "fallback": "microsoft/wizardlm-2-8x22b",
                "quantization": "Q4_K_M",
                "max_context": 4096
            }
        else:  # CPU or low-end GPU
            return {
                "primary": "Meta-Llama-3.1-8B-Instruct-Q4",
                "fallback": "microsoft/DialoGPT-medium",
                "quantization": "Q4_K_M",
                "max_context": 2048
            }

    def _get_performance_tips(self, hardware: Dict[str, Any]) -> list:
        """Get performance optimization tips"""
        tips = []

        gpu_vram = hardware["gpu"]["vram_gb"]
        memory_gb = hardware["memory"]["total_gb"]
        cpu_cores = hardware["cpu"]["cores"]

        if gpu_vram >= 16:
            tips.append("GPU acceleration available - use CUDA for best performance")
        elif gpu_vram >= 8:
            tips.append("Moderate GPU - consider Q4 quantization for better speed")
        else:
            tips.append("CPU-only mode - use smaller models or quantization")

        if memory_gb >= 32:
            tips.append("High memory - can handle large context windows")
        elif memory_gb >= 16:
            tips.append("Good memory - optimize context length for performance")
        else:
            tips.append("Limited memory - use smaller context windows")

        if cpu_cores >= 8:
            tips.append("Multi-core CPU - enable parallel processing")
        else:
            tips.append("Limited cores - focus on GPU acceleration")

        return tips

    def save_hardware_profile(self, profile_path: Optional[str] = None) -> str:
        try:
            """Save hardware profile to file"""
            if profile_path is None:
                profile_path = self.project_root / "config" / "hardware_profile.json"

            profile_path.parent.mkdir(parents=True, exist_ok=True)

            hardware = self.detect_hardware()
            with open(profile_path, 'w') as f:
                json.dump(hardware, f, indent=2)

            return str(profile_path)

        except Exception as e:
            self.logger.error(f"Error in save_hardware_profile: {e}", exc_info=True)
            raise
    def load_hardware_profile(self, profile_path: Optional[str] = None) -> Dict[str, Any]:
        try:
            """Load hardware profile from file"""
            if profile_path is None:
                profile_path = self.project_root / "config" / "hardware_profile.json"

            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    return json.load(f)
            else:
                return self.detect_hardware()


        except Exception as e:
            self.logger.error(f"Error in load_hardware_profile: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Hardware Detection for LLM Optimization")
        parser.add_argument("action", choices=["detect", "save", "load", "recommend"], help="Action to perform")
        parser.add_argument("--profile", help="Hardware profile file path")

        args = parser.parse_args()

        detector = HardwareDetector()

        if args.action == "detect":
            hardware = detector.detect_hardware()
            print("🔍 Detected Hardware Configuration:")
            print(json.dumps(hardware, indent=2))

        elif args.action == "save":
            profile_path = detector.save_hardware_profile(args.profile)
            print(f"✅ Hardware profile saved to: {profile_path}")

        elif args.action == "load":
            hardware = detector.load_hardware_profile(args.profile)
            print("📂 Loaded Hardware Profile:")
            print(json.dumps(hardware, indent=2))

        elif args.action == "recommend":
            hardware = detector.detect_hardware()
            print("🎯 LLM Recommendations for your hardware:")
            print(json.dumps(hardware["recommendations"], indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":




    main()