#!/usr/bin/env python3
"""
Windows IR Camera Access via WinRT API

Attempts to access ASUS IR camera using Windows Runtime (WinRT) APIs.
This provides better access to Windows Hello IR cameras than OpenCV.

Tags: #WINDOWS #IR_CAMERA #WINRT #MEDIA_CAPTURE @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WindowsIRCameraAccess")

print("=" * 80)
print("📹 WINDOWS IR CAMERA ACCESS VIA WINRT API")
print("=" * 80)
print()

# Check for required packages
print("Checking required packages...")
print()

packages_needed = []
packages_available = []

# Check winrt-runtime
try:
    import winrt
    packages_available.append("winrt (monolithic)")
    print("✅ winrt (monolithic) - AVAILABLE")
except ImportError:
    try:
        import winrt.system
        packages_available.append("winrt-runtime")
        print("✅ winrt-runtime - AVAILABLE")
    except ImportError:
        packages_needed.append("winrt-runtime")
        print("❌ winrt-runtime - NOT INSTALLED")

# Check winrt-Windows.Media.Capture
try:
    from winrt.windows.media.capture import MediaCapture, MediaCaptureInitializationSettings
    packages_available.append("winrt-Windows.Media.Capture")
    print("✅ winrt-Windows.Media.Capture - AVAILABLE")
    MEDIA_CAPTURE_AVAILABLE = True
except ImportError:
    packages_needed.append("winrt-Windows.Media.Capture")
    print("❌ winrt-Windows.Media.Capture - NOT INSTALLED")
    MEDIA_CAPTURE_AVAILABLE = False

# Check winrt-Windows.Media.Capture.Frames
try:
    from winrt.windows.media.capture.frames import (
        MediaFrameSourceKind, MediaFrameReader, MediaFrameSource
    )
    packages_available.append("winrt-Windows.Media.Capture.Frames")
    print("✅ winrt-Windows.Media.Capture.Frames - AVAILABLE")
    FRAMES_AVAILABLE = True
except ImportError:
    packages_needed.append("winrt-Windows.Media.Capture.Frames")
    print("❌ winrt-Windows.Media.Capture.Frames - NOT INSTALLED")
    FRAMES_AVAILABLE = False

print()

if packages_needed:
    print("=" * 80)
    print("INSTALLATION REQUIRED")
    print("=" * 80)
    print()
    print("To access ASUS IR camera, install these packages:")
    print()
    for pkg in packages_needed:
        print(f"  pip install {pkg}")
    print()
    print("Full installation command:")
    print(f"  pip install {' '.join(packages_needed)}")
    print()
    print("=" * 80)
else:
    print("✅ All required packages are available!")
    print()

    if MEDIA_CAPTURE_AVAILABLE and FRAMES_AVAILABLE:
        print("=" * 80)
        print("TESTING IR CAMERA ACCESS")
        print("=" * 80)
        print()

        try:
            import asyncio

            async def test_ir_camera():
                """Test IR camera access"""
                print("Initializing MediaCapture...")
                try:
                    settings = MediaCaptureInitializationSettings()
                    # Set streaming mode to VIDEO
                    from winrt.windows.media.capture import StreamingCaptureMode
                    settings.streaming_capture_mode = StreamingCaptureMode.VIDEO

                    media_capture = MediaCapture()
                    # Try different initialization methods
                    try:
                        await media_capture.initialize_async(settings)
                    except TypeError:
                        # Try without settings (use defaults)
                        await media_capture.initialize_async()
                    print("✅ MediaCapture initialized")
                except Exception as e:
                    print(f"❌ MediaCapture initialization error: {e}")
                    import traceback
                    traceback.print_exc()
                    return

                print()
                print("Enumerating frame sources...")
                frame_sources = media_capture.frame_sources

                ir_source_found = False
                for source_id, source in frame_sources.items():
                    source_kind = source.info.source_kind
                    print(f"  Source: {source_id}")
                    print(f"    Kind: {source_kind}")

                    if source_kind == MediaFrameSourceKind.INFRARED:
                        print(f"    ✅ INFRARED SOURCE FOUND!")
                        ir_source_found = True

                        # Try to create frame reader
                        try:
                            reader = await media_capture.create_frame_reader_async(source)
                            print("    ✅ Frame reader created")

                            # Start reading
                            await reader.start_async()
                            print("    ✅ Frame reader started")

                            # Try to get a frame
                            result = await reader.try_acquire_latest_frame_async()
                            if result:
                                print("    ✅ IR frame acquired!")
                                frame = result.video_media_frame
                                print(f"    Frame format: {frame.format}")
                            else:
                                print("    ⚠️  No frame available yet")

                            await reader.stop_async()
                        except Exception as e:
                            print(f"    ⚠️  Error creating reader: {e}")

                if not ir_source_found:
                    print("  ⚠️  No infrared frame source found")
                    print("  Available sources:")
                    for source_id, source in frame_sources.items():
                        print(f"    - {source_id}: {source.info.source_kind}")

            print("Running async test...")
            asyncio.run(test_ir_camera())

        except Exception as e:
            print(f"❌ Error testing IR camera: {e}")
            import traceback
            traceback.print_exc()

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("Packages Available:")
for pkg in packages_available:
    print(f"  ✅ {pkg}")
print()
if packages_needed:
    print("Packages Needed:")
    for pkg in packages_needed:
        print(f"  ❌ {pkg}")
    print()
    print("Install with:")
    print(f"  pip install {' '.join(packages_needed)}")
print()
print("=" * 80)
