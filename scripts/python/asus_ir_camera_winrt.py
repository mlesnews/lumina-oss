#!/usr/bin/env python3
"""
ASUS IR Camera Access via WinRT

Accesses ASUS IR camera using Windows Runtime API.
This provides better access than OpenCV for Windows Hello IR cameras.

Tags: #ASUS #IR_CAMERA #WINRT #WINDOWS_HELLO @JARVIS @LUMINA
"""

import sys
import asyncio
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from winrt.windows.media.capture import MediaCapture, MediaCaptureInitializationSettings, StreamingCaptureMode
    from winrt.windows.media.capture.frames import MediaFrameSourceKind, MediaFrameReader
    WINRT_AVAILABLE = True
    try:
        from winrt.windows.media.devices import InfraredTorchMode
        IR_TORCH_AVAILABLE = True
    except ImportError:
        IR_TORCH_AVAILABLE = False
except ImportError as e:
    WINRT_AVAILABLE = False
    print(f"❌ WinRT packages not available: {e}")
    print("   Install with: pip install winrt-runtime winrt-Windows.Media.Capture winrt-Windows.Media.Capture.Frames")
    sys.exit(1)

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ASUSIRCameraWinRT")


async def access_asus_ir_camera():
    """Access ASUS IR camera via WinRT API"""
    print("=" * 80)
    print("📹 ACCESSING ASUS IR CAMERA VIA WINRT")
    print("=" * 80)
    print()

    try:
        # Find source groups that include IR
        print("1. Finding camera source groups...")
        try:
            from winrt.windows.media.capture.frames import MediaFrameSourceGroup
            source_groups = await MediaFrameSourceGroup.find_all_async()
            print(f"   Found {len(source_groups)} source group(s)")

            # Look for source group with IR capability
            ir_group = None
            for group in source_groups:
                print(f"   Group: {group.display_name}")
                print(f"     Source count: {len(group.source_infos)}")
                for info in group.source_infos:
                    kind_value = int(info.source_kind) if hasattr(info.source_kind, '__int__') else info.source_kind
                    print(f"       Source: {info.id}")
                    print(f"       Kind: {info.source_kind} (value: {kind_value})")
                    # MediaFrameSourceKind.INFRARED is typically 2
                    if info.source_kind == MediaFrameSourceKind.INFRARED or kind_value == 2:
                        print(f"       ✅ IR source found in this group!")
                        ir_group = group
                        break
                if ir_group:
                    break
                print()

            if not ir_group:
                print("   ⚠️  No source group with IR found, using first group")
                if source_groups:
                    ir_group = source_groups[0]
                else:
                    print("   ❌ No source groups available")
                    return False
        except Exception as e:
            print(f"   ⚠️  Error finding source groups: {e}")
            ir_group = None

        # Initialize MediaCapture with source group
        print()
        print("2. Initializing MediaCapture...")
        try:
            from winrt.windows.media.capture import MediaCaptureSharingMode, MediaCaptureMemoryPreference

            settings = MediaCaptureInitializationSettings()
            settings.streaming_capture_mode = StreamingCaptureMode.VIDEO
            settings.sharing_mode = MediaCaptureSharingMode.SHARED_READ_ONLY  # More compatible
            settings.memory_preference = MediaCaptureMemoryPreference.CPU  # For software bitmaps

            if ir_group:
                settings.source_group = ir_group
                print(f"   Using source group: {ir_group.display_name}")

            media_capture = MediaCapture()
            # Initialize with settings (including source_group for IR)
            # WinRT async: await the IAsyncOperation directly
            try:
                # Create IAsyncOperation and await it
                init_operation = media_capture.initialize_async(settings)
                await init_operation
                print("   ✅ MediaCapture initialized with IR source group")
            except Exception as e:
                print(f"   ⚠️  Error with settings: {e}")
                # Fallback: try without source_group
                try:
                    settings_no_group = MediaCaptureInitializationSettings()
                    settings_no_group.streaming_capture_mode = StreamingCaptureMode.VIDEO
                    init_operation = media_capture.initialize_async(settings_no_group)
                    await init_operation
                    print("   ✅ MediaCapture initialized (without source group)")
                except Exception as e2:
                    # Last resort: initialize without settings
                    init_operation = media_capture.initialize_async()
                    await init_operation
                    print("   ✅ MediaCapture initialized (default, no settings)")
        except Exception as e:
            print(f"   ❌ MediaCapture initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        print()

        # Enumerate frame sources
        print("3. Enumerating frame sources...")
        frame_sources = media_capture.frame_sources

        ir_source = None
        ir_source_id = None

        for source_id, source in frame_sources.items():
            source_kind = source.info.source_kind
            source_info = source.info

            print(f"   Source ID: {source_id}")
            print(f"   Kind: {source_kind}")
            print(f"   MediaStreamType: {source_info.media_stream_type}")

            if source_kind == MediaFrameSourceKind.INFRARED:
                print(f"   ✅ INFRARED SOURCE FOUND!")
                ir_source = source
                ir_source_id = source_id
            print()

        if not ir_source:
            print("   ⚠️  No infrared source found in frame sources")
            print("   Available sources:")
            for source_id, source in frame_sources.items():
                print(f"     - {source_id}: {source.info.source_kind}")
            return None

        # Create frame reader for IR source
        print("4. Creating IR frame reader...")
        try:
            reader = await media_capture.create_frame_reader_async(ir_source)
            print("   ✅ Frame reader created")
        except Exception as e:
            print(f"   ❌ Error creating frame reader: {e}")
            return False
        print()

        # Start reading frames
        print("5. Starting frame reader...")
        try:
            await reader.start_async()
            print("   ✅ Frame reader started")
        except Exception as e:
            print(f"   ❌ Error starting frame reader: {e}")
            return False
        print()

        # Try to get IR frames
        print("6. Attempting to acquire IR frames...")
        frame_count = 0
        for i in range(10):  # Try 10 times
            result = await reader.try_acquire_latest_frame_async()
            if result:
                frame_count += 1
                frame = result.video_media_frame
                if frame:
                    video_frame = frame.get_video_frame()
                    if video_frame:
                        print(f"   ✅ IR frame {frame_count} acquired!")
                        print(f"      Format: {video_frame.software_bitmap.pixel_format}")
                        print(f"      Size: {video_frame.software_bitmap.pixel_width}x{video_frame.software_bitmap.pixel_height}")
            await asyncio.sleep(0.1)

        if frame_count > 0:
            print(f"   ✅ Successfully acquired {frame_count} IR frames!")
        else:
            print("   ⚠️  No IR frames acquired")

        # Stop reader
        await reader.stop_async()

        return True

    except Exception as e:
        print(f"❌ Error accessing IR camera: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    if not WINRT_AVAILABLE:
        print("❌ WinRT packages not available")
        return

    print()
    success = asyncio.run(access_asus_ir_camera())
    print()
    print("=" * 80)
    if success:
        print("✅ ASUS IR camera access successful!")
        print("   IR camera can be accessed via WinRT API")
    else:
        print("⚠️  ASUS IR camera access had issues")
        print("   May need Windows Hello setup or permissions")
    print("=" * 80)


if __name__ == "__main__":


    main()