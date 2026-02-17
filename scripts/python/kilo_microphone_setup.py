#!/usr/bin/env python3
"""
Kilo Code Microphone Setup Script

This script configures the microphone for Kilo Code voice input.
It tests the microphone, lists available devices, and verifies dependencies.

Usage:
    python scripts/python/kilo_microphone_setup.py --setup
    python scripts/python/kilo_microphone_setup.py --list-devices
    python scripts/python/kilo_microphone_setup.py --test
    python scripts/python/kilo_microphone_setup.py --all
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def check_dependencies() -> dict:
    """Check if required dependencies are installed."""
    results = {
        "sounddevice": False,
        "numpy": False,
        "pydantic": False,
        "speechrecognition": False,
        "pyaudio": False,
    }

    try:
        import sounddevice
        results["sounddevice"] = True
        print("✅ sounddevice is installed")
    except ImportError as e:
        print(f"❌ sounddevice is NOT installed: {e}")

    try:
        import numpy
        results["numpy"] = True
        print("✅ numpy is installed")
    except ImportError as e:
        print(f"❌ numpy is NOT installed: {e}")

    try:
        from pydantic import BaseModel
        results["pydantic"] = True
        print("✅ pydantic is installed")
    except ImportError as e:
        print(f"❌ pydantic is NOT installed: {e}")

    try:
        import speech_recognition
        results["speechrecognition"] = True
        print("✅ speechrecognition is installed")
    except ImportError as e:
        print(f"❌ speechrecognition is NOT installed: {e}")

    try:
        import pyaudio
        results["pyaudio"] = True
        print("✅ pyaudio is installed")
    except ImportError as e:
        print(f"❌ pyaudio is NOT installed: {e}")

    return results


def list_microphone_devices() -> list:
    """List all available microphone devices."""
    try:
        import sounddevice as sd
        devices = sd.query_devices(kind="input")
        print("\n🎤 Available Microphone Devices:")
        print("=" * 60)

        # Handle different output formats from sounddevice
        device_list = []
        if isinstance(devices, list):
            device_list = devices
            for i, device in enumerate(devices):
                if isinstance(device, dict):
                    print(f"  [{i}] {device.get('name', 'Unknown')}")
                    print(f"      Channels: {device.get('max_input_channels', 'N/A')}")
                    print(f"      Sample Rate: {device.get('default_samplerate', 'N/A')} Hz")
                else:
                    print(f"  [{i}] {device}")
        elif isinstance(devices, dict):
            # Single device - format is different
            device_list = [devices]
            print(f"  [0] {devices.get('name', 'Unknown')}")
            print(f"      Channels: {devices.get('max_input_channels', 'N/A')}")
            print(f"      Sample Rate: {devices.get('default_samplerate', 'N/A')} Hz")
        else:
            print(f"  {devices}")

        print("=" * 60)
        return device_list
    except Exception as e:
        print(f"❌ Error listing devices: {e}")
        # Try alternative method
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            print(f"\n🎤 Available Microphone Devices (via PyAudio):")
            print("=" * 60)
            for i in range(num_devices):
                if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                    print(f"  [{i}] {p.get_device_info_by_host_api_device_index(0, i).get('name')}")
            print("=" * 60)
            return list(range(num_devices))
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
        return []


def test_microphone(device_index: Optional[int] = None) -> bool:
    """Test the microphone with a short recording."""
    try:
        import sounddevice as sd
        import numpy as np

        print(f"\n🔊 Testing microphone (device index: {device_index})...")

        # Configure the stream
        sample_rate = 16000
        duration = 2  # seconds

        # Record audio
        audio_data = sd.rec(
            int(sample_rate * duration),
            samplerate=sample_rate,
            channels=1,
            dtype='float32',
            device=device_index
        )

        # Wait for recording to complete
        sd.wait()

        # Calculate volume
        volume = np.linalg.norm(audio_data)
        print(f"   Volume level: {volume:.4f}")

        if volume > 0.001:
            print("✅ Microphone is working! Audio detected.")
            return True
        else:
            print("⚠️  Microphone is connected but no audio detected.")
            print("   Try speaking louder or checking your microphone settings.")
            return False

    except Exception as e:
        print(f"❌ Error testing microphone: {e}")
        return False


def create_kilo_config(device_index: Optional[int] = None):
    """Create or update the kilo_config.json file."""
    config_path = project_root / "kilo_config.json"

    config = {
        "device_index": device_index,
        "sample_rate": 16000,
        "channels": 1,
        "chunk_size": 1024,
        "timeout": 5.0,
    }

    try:
        if config_path.exists():
            existing_config = json.loads(config_path.read_text())
            existing_config.update(config)
            config = existing_config

        config_path.write_text(json.dumps(config, indent=2))
        print(f"✅ Configuration saved to: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")

    try:
        import subprocess

        packages = [
            "sounddevice",
            "numpy",
            "pydantic",
            "SpeechRecognition",
        ]

        for package in packages:
            print(f"   Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ])

        # For pyaudio on Windows, we need a different approach
        try:
            import pyaudio
        except ImportError:
            print("   Installing pyaudio (may require manual installation on some systems)...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "pyaudio"
            ])

        print("✅ Dependencies installed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def run_setup():
    """Run the complete microphone setup."""
    print("=" * 60)
    print("🎤 Kilo Code Microphone Setup")
    print("=" * 60)

    # Check dependencies
    print("\n1️⃣  Checking dependencies...")
    deps = check_dependencies()

    # Install missing dependencies
    missing = [k for k, v in deps.items() if not v]
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        if input("   Install missing dependencies? (y/n): ").lower() == 'y':
            install_dependencies()
            deps = check_dependencies()

    # List devices
    print("\n2️⃣  Listing available microphone devices...")
    devices = list_microphone_devices()

    if not devices:
        print("❌ No microphone devices found!")
        print("   Please check your microphone connection and permissions.")
        return False

    # Test microphone
    print("\n3️⃣  Testing microphone...")
    device_index = None
    if len(devices) > 1:
        print("   Multiple devices found. Select one to test:")
        for i, device in enumerate(devices):
            print(f"   [{i}] {device['name']}")
        try:
            device_index = int(input("   Enter device index (or press Enter for default): ").strip() or "0")
        except ValueError:
            device_index = 0

    if test_microphone(device_index):
        # Create configuration
        print("\n4️⃣  Saving configuration...")
        create_kilo_config(device_index)

        print("\n" + "=" * 60)
        print("✅ Microphone setup complete!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. Run: python scripts/python/kilo_module.py")
        print("   2. Or integrate with your Kilo Code workflow")
        return True
    else:
        print("\n❌ Microphone test failed!")
        print("   Please check your microphone settings and try again.")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kilo Code Microphone Setup")
    parser.add_argument("--setup", action="store_true", help="Run complete setup")
    parser.add_argument("--list-devices", action="store_true", help="List available devices")
    parser.add_argument("--test", action="store_true", help="Test microphone")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--all", action="store_true", help="Run all checks")

    args = parser.parse_args()

    if args.all or args.setup:
        run_setup()
    elif args.list_devices:
        list_microphone_devices()
    elif args.test:
        test_microphone()
    elif args.install:
        install_dependencies()
    else:
        run_setup()
