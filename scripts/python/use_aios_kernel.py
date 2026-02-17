#!/usr/bin/env python3
"""
How to Use AIOS Kernel - Practical Guide

This shows you how to ACTUALLY USE the AIOS kernel.
It's ACTIONABLE and VIABLE - not just documentation.

Usage:
    python scripts/python/use_aios_kernel.py

Tags: #AIOS_KERNEL #USAGE #ACTIONABLE @JARVIS @LUMINA
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

# Import kernel integration
try:
    from aios.kernel.aios_kernel_integration import AIOSKernelIntegration
except ImportError:
    # Fallback path
    sys.path.insert(0, str(Path(__file__).parent / "aios" / "kernel"))
    from aios_kernel_integration import AIOSKernelIntegration


def main():
    """Practical usage examples"""
    print("=" * 80)
    print("📖 HOW TO USE AIOS KERNEL - ACTIONABLE GUIDE")
    print("=" * 80)
    print()

    # Initialize
    print("STEP 1: Initialize AIOS Kernel")
    print("-" * 80)
    kernel = AIOSKernelIntegration()
    print("✅ Kernel initialized!")
    print()

    # Example 1: Run a process
    print("EXAMPLE 1: Run a Process")
    print("-" * 80)
    process = kernel.run_process("my_application", "python", ["app.py", "--arg", "value"])
    print(f"   Created process: {process['name']} (PID: {process['pid']})")
    print(f"   Memory allocated: {process['memory_used'] / 1024:.2f} KB")
    print()

    # Example 2: File operations
    print("EXAMPLE 2: File Operations")
    print("-" * 80)
    kernel.create_file("/data/myfile.txt", "Hello from AIOS Kernel!")
    content = kernel.read_file("/data/myfile.txt")
    print(f"   Created and read file: {content}")
    print()

    # Example 3: System information
    print("EXAMPLE 3: Get System Information")
    print("-" * 80)
    info = kernel.get_system_info()
    print(f"   CPU: {info['hardware']['cpu']['architecture']}")
    print(f"   Cores: {info['hardware']['cpu']['cores']}")
    print(f"   Memory: {info['hardware']['memory']['total_gb']:.2f} GB")
    print(f"   Running Processes: {info['kernel']['processes']['total']}")
    print()

    # Example 4: OS compatibility
    print("EXAMPLE 4: OS Compatibility (Run Windows/Linux/macOS code)")
    print("-" * 80)
    # Translate Windows API call
    result = kernel.translate_os_call("windows", "CreateFile", "C:\\test.txt", 0, 0)
    print(f"   Windows CreateFile → AIOS: {result}")
    # Translate Linux API call
    result = kernel.translate_os_call("linux", "open", "/test.txt", 0)
    print(f"   Linux open → AIOS: {result}")
    print()

    # Example 5: VR integration
    print("EXAMPLE 5: VR/AR Integration")
    print("-" * 80)
    vr = kernel.initialize_vr()
    print(f"   VR Status: {vr['status']}")
    print(f"   SteamVR: {'Available' if vr['steamvr'] else 'Not Available'}")
    print(f"   OpenXR: {'Available' if vr['openxr'] else 'Not Available'}")
    print()

    print("=" * 80)
    print("✅ This is ACTIONABLE and VIABLE!")
    print("   The AIOS kernel is USABLE, not just documentation.")
    print("=" * 80)
    print()
    print("NEXT STEPS:")
    print("  1. Import AIOSKernelIntegration in your code")
    print("  2. Use kernel.run_process() to run applications")
    print("  3. Use kernel.create_file() / read_file() for file operations")
    print("  4. Use kernel.translate_os_call() for OS compatibility")
    print("  5. Use kernel.initialize_vr() for VR/AR support")
    print()


if __name__ == "__main__":


    main()