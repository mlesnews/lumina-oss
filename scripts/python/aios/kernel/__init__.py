"""
AIOS Kernel - Full Operating System Kernel

Complete operating system kernel with:
- Microkernel
- Compatibility Layer
- SteamVR/OpenXR Integration
- Hardware Abstraction Layer

Tags: #AIOS_KERNEL #OPERATING_SYSTEM @JARVIS @LUMINA
"""

from .microkernel import (
    AIOSMicrokernel,
    Process,
    ProcessState,
    MemoryBlock,
    MemoryType
)
from .compatibility_layer import (
    CompatibilityLayer,
    OSType,
    CompatibilityMode
)
from .steamvr_integration import (
    SteamVRIntegration,
    VRRuntime,
    VRDeviceType,
    VRDevice,
    VRPose
)
from .hardware_abstraction import (
    HardwareAbstractionLayer,
    Architecture,
    GPUVendor,
    CPUInfo,
    MemoryInfo,
    GPUInfo
)

__all__ = [
    'AIOSMicrokernel',
    'Process',
    'ProcessState',
    'MemoryBlock',
    'MemoryType',
    'CompatibilityLayer',
    'OSType',
    'CompatibilityMode',
    'SteamVRIntegration',
    'VRRuntime',
    'VRDeviceType',
    'VRDevice',
    'VRPose',
    'HardwareAbstractionLayer',
    'Architecture',
    'GPUVendor',
    'CPUInfo',
    'MemoryInfo',
    'GPUInfo'
]
