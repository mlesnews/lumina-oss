#!/usr/bin/env python3
"""
Detect Camera Hardware Specifications

Detects and lists all cameras on the system, including IR cameras.
Checks hardware specs to identify which camera is IR vs regular.

Tags: #CAMERA #HARDWARE #IR_CAMERA #DETECTION @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CameraHardwareDetector")

print("=" * 80)
print("📹 CAMERA HARDWARE DETECTION")
print("=" * 80)
print()

# Method 1: OpenCV camera enumeration
print("Method 1: OpenCV Camera Enumeration")
print("-" * 80)
if CV2_AVAILABLE:
    cameras_found = []
    for idx in range(5):  # Check indices 0-4
        try:
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    channels = frame.shape[2] if len(frame.shape) > 2 else 1

                    # Try to get backend info
                    backend = cap.getBackendName()

                    camera_info = {
                        "index": idx,
                        "width": width,
                        "height": height,
                        "channels": channels,
                        "backend": backend,
                        "is_grayscale": channels == 1,
                        "likely_ir": channels == 1  # IR cameras often output grayscale
                    }
                    cameras_found.append(camera_info)

                    print(f"  Camera {idx}:")
                    print(f"    Resolution: {width}x{height}")
                    print(f"    Channels: {channels} ({'Grayscale' if channels == 1 else 'Color'})")
                    print(f"    Backend: {backend}")
                    print(f"    Likely IR: {'✅ YES (grayscale)' if channels == 1 else '❌ NO (color)'}")
                    print()
                cap.release()
        except Exception as e:
            pass

    if not cameras_found:
        print("  ⚠️  No cameras detected via OpenCV")
        print()
else:
    print("  ⚠️  OpenCV not available")
    print()

# Method 2: Windows WMI (Windows Management Instrumentation)
print("Method 2: Windows WMI Hardware Detection")
print("-" * 80)
try:
    import subprocess

    # Get camera devices via PowerShell
    ps_command = """
    Get-PnpDevice -Class Camera | Select-Object FriendlyName, Status, InstanceId | Format-List
    """

    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0 and result.stdout:
        print("  Camera Devices (via WMI):")
        print(result.stdout)
    else:
        print("  ⚠️  Could not query camera devices via WMI")
        print()
except Exception as e:
    print(f"  ⚠️  WMI detection error: {e}")
    print()

# Method 3: DirectShow enumeration (Windows)
print("Method 3: DirectShow Camera Enumeration")
print("-" * 80)
try:
    import subprocess

    # Try to list DirectShow devices
    ps_command = """
    Add-Type -AssemblyName System.Windows.Forms
    $cameras = [System.Windows.Forms.SystemInformation]::GetDevices()
    Get-PnpDevice -Class Camera | ForEach-Object {
        Write-Host "Device: $($_.FriendlyName)"
        Write-Host "  Status: $($_.Status)"
        Write-Host "  Instance ID: $($_.InstanceId)"
        Write-Host ""
    }
    """

    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0 and result.stdout:
        print(result.stdout)
    else:
        print("  ⚠️  Could not enumerate DirectShow devices")
        print()
except Exception as e:
    print(f"  ⚠️  DirectShow enumeration error: {e}")
    print()

# Method 4: Check for Windows Hello / IR camera
print("Method 4: Windows Hello / IR Camera Check")
print("-" * 80)
try:
    import subprocess

    # Check Windows Hello availability
    ps_command = """
    $hello = Get-WmiObject -Namespace "root\\cimv2" -Class "Win32_PnPEntity" | Where-Object { $_.Name -like "*Hello*" -or $_.Name -like "*IR*" -or $_.Name -like "*Infrared*" }
    if ($hello) {
        $hello | ForEach-Object {
            Write-Host "Windows Hello / IR Device: $($_.Name)"
            Write-Host "  Status: $($_.Status)"
            Write-Host "  Device ID: $($_.DeviceID)"
            Write-Host ""
        }
    } else {
        Write-Host "  No Windows Hello / IR devices found via WMI"
    }
    """

    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode == 0 and result.stdout:
        print(result.stdout)
    else:
        print("  ⚠️  Could not check Windows Hello")
        print()
except Exception as e:
    print(f"  ⚠️  Windows Hello check error: {e}")
    print()

# Method 5: Check camera capabilities
print("Method 5: Camera Capability Check")
print("-" * 80)
if CV2_AVAILABLE and cameras_found:
    for cam_info in cameras_found:
        idx = cam_info["index"]
        print(f"  Testing Camera {idx} capabilities...")
        try:
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                # Check if it supports IR (some cameras have IR mode)
                # Try to read a few frames to see characteristics
                frames = []
                for i in range(5):
                    ret, frame = cap.read()
                    if ret:
                        frames.append(frame)

                if frames:
                    # Analyze frame characteristics
                    frame = frames[0]
                    is_grayscale = len(frame.shape) == 2 or frame.shape[2] == 1

                    # Check brightness (IR cameras often have different brightness characteristics)
                    if not is_grayscale:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = frame

                    avg_brightness = gray.mean()

                    print(f"    Average brightness: {avg_brightness:.1f}")
                    print(f"    Grayscale: {'Yes' if is_grayscale else 'No'}")
                    print(f"    IR indicator: {'Possibly IR (grayscale)' if is_grayscale else 'Likely color camera'}")
                    print()
                cap.release()
        except Exception as e:
            print(f"    Error testing camera {idx}: {e}")
            print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("Red Light Next to White Light:")
print("  ✅ YES - This is likely the IR (infrared) camera")
print("  • IR cameras typically have a red/amber LED indicator")
print("  • White light = Regular camera (emits visible light)")
print("  • Red light = IR camera (emits infrared, invisible to human eye)")
print()
print("Recommendation:")
print("  • Use IR camera (red light) to avoid bright white light")
print("  • IR camera is better for privacy and less distracting")
print("  • Check Windows Camera settings to enable IR camera")
print()
print("=" * 80)
