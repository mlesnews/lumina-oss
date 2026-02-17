#!/usr/bin/env python3
"""
AIOS Hardware Abstraction Layer (HAL)

Hardware abstraction for CPU, memory, storage, network, and GPU.
Supports x86_64, ARM, RISC-V architectures.

Tags: #AIOS_KERNEL #HAL #HARDWARE #ABSTRACTION @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
import platform
import psutil
import sys
from pathlib import Path

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIOSHAL")


class Architecture(Enum):
    """CPU architectures"""
    X86_64 = "x86_64"
    ARM = "arm"
    ARM64 = "arm64"
    RISC_V = "risc_v"
    UNKNOWN = "unknown"


class GPUVendor(Enum):
    """GPU vendors"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    APPLE = "apple"
    UNKNOWN = "unknown"


@dataclass
class CPUInfo:
    """CPU information"""
    architecture: Architecture
    cores: int
    threads: int
    frequency: float
    vendor: str
    model: str


@dataclass
class MemoryInfo:
    """Memory information"""
    total: int  # bytes
    available: int  # bytes
    used: int  # bytes
    free: int  # bytes


@dataclass
class GPUInfo:
    """GPU information"""
    vendor: GPUVendor
    model: str
    memory_total: int  # bytes
    memory_used: int  # bytes


class HardwareAbstractionLayer:
    """
    AIOS Hardware Abstraction Layer (HAL)

    Abstracts hardware differences across architectures and platforms.
    """

    def __init__(self):
        """Initialize Hardware Abstraction Layer"""
        logger.info("🔧 AIOS Hardware Abstraction Layer initializing...")

        # Detect hardware
        self.cpu_info = self._detect_cpu()
        self.memory_info = self._detect_memory()
        self.gpu_info = self._detect_gpu()
        self.storage_info = self._detect_storage()
        self.network_info = self._detect_network()

        logger.info(f"✅ HAL initialized - {self.cpu_info.architecture.value}, {self.cpu_info.cores} cores")

    def _detect_cpu(self) -> CPUInfo:
        """Detect CPU information"""
        machine = platform.machine().lower()

        # Determine architecture
        if 'x86_64' in machine or 'amd64' in machine:
            arch = Architecture.X86_64
        elif 'arm64' in machine or 'aarch64' in machine:
            arch = Architecture.ARM64
        elif 'arm' in machine:
            arch = Architecture.ARM
        elif 'risc' in machine:
            arch = Architecture.RISC_V
        else:
            arch = Architecture.UNKNOWN

        # Get CPU info
        cores = psutil.cpu_count(logical=False) or 1
        threads = psutil.cpu_count(logical=True) or cores
        freq = psutil.cpu_freq()
        frequency = freq.current if freq else 0.0

        return CPUInfo(
            architecture=arch,
            cores=cores,
            threads=threads,
            frequency=frequency,
            vendor=platform.processor(),
            model=platform.processor()
        )

    def _detect_memory(self) -> MemoryInfo:
        """Detect memory information"""
        mem = psutil.virtual_memory()

        return MemoryInfo(
            total=mem.total,
            available=mem.available,
            used=mem.used,
            free=mem.free
        )

    def _detect_gpu(self) -> Optional[GPUInfo]:
        """Detect GPU information"""
        # This would use platform-specific APIs
        # For now, return None (would detect via nvidia-smi, etc.)
        return None

    def _detect_storage(self) -> List[Dict[str, Any]]:
        """Detect storage devices"""
        disks = []

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free
                })
            except PermissionError:
                continue

        return disks

    def _detect_network(self) -> List[Dict[str, Any]]:
        """Detect network interfaces"""
        interfaces = []

        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                interfaces.append({
                    'interface': interface,
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask if hasattr(addr, 'netmask') else None
                })

        return interfaces

    def get_hardware_info(self) -> Dict[str, Any]:
        """Get complete hardware information"""
        return {
            'cpu': {
                'architecture': self.cpu_info.architecture.value,
                'cores': self.cpu_info.cores,
                'threads': self.cpu_info.threads,
                'frequency_mhz': self.cpu_info.frequency,
                'vendor': self.cpu_info.vendor,
                'model': self.cpu_info.model
            },
            'memory': {
                'total_gb': self.memory_info.total / (1024**3),
                'available_gb': self.memory_info.available / (1024**3),
                'used_gb': self.memory_info.used / (1024**3),
                'free_gb': self.memory_info.free / (1024**3)
            },
            'gpu': {
                'vendor': self.gpu_info.vendor.value if self.gpu_info else None,
                'model': self.gpu_info.model if self.gpu_info else None,
                'memory_total_gb': self.gpu_info.memory_total / (1024**3) if self.gpu_info else None
            },
            'storage': [
                {
                    'device': disk['device'],
                    'mountpoint': disk['mountpoint'],
                    'total_gb': disk['total'] / (1024**3),
                    'used_gb': disk['used'] / (1024**3),
                    'free_gb': disk['free'] / (1024**3)
                }
                for disk in self.storage_info
            ],
            'network': self.network_info
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("🔧 AIOS HARDWARE ABSTRACTION LAYER")
    print("   Hardware abstraction for all architectures")
    print("=" * 80)
    print()

    hal = HardwareAbstractionLayer()

    # Hardware info
    print("HARDWARE INFORMATION:")
    print("-" * 80)
    info = hal.get_hardware_info()

    print(f"CPU: {info['cpu']['architecture']} - {info['cpu']['cores']} cores, {info['cpu']['threads']} threads")
    print(f"Memory: {info['memory']['total_gb']:.2f} GB total, {info['memory']['available_gb']:.2f} GB available")
    print(f"GPU: {info['gpu']['vendor'] or 'Unknown'}")
    print(f"Storage: {len(info['storage'])} devices")
    print(f"Network: {len(info['network'])} interfaces")
    print()

    print("=" * 80)
    print("🔧 HAL - Hardware abstraction ready")
    print("=" * 80)


if __name__ == "__main__":


    main()