#!/usr/bin/env python3
"""
Find and Test Anime Files with Babelfish

Helps you find anime video/subtitle files and test them with Babelfish.
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FindAndTestAnime")


def find_anime_files(search_dirs: list = None):
    """Find anime-related files"""

    if search_dirs is None:
        # Common locations
        search_dirs = [
            Path.home() / "Downloads",
            Path.home() / "Videos",
            Path.home() / "Desktop",
            Path(".").resolve() / "output" / "videos"
        ]

    print("\n" + "="*80)
    print("🔍 SEARCHING FOR ANIME FILES")
    print("="*80 + "\n")

    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']
    subtitle_extensions = ['.srt', '.ass', '.ssa', '.vtt']

    found_files = {
        'videos': [],
        'subtitles': []
    }

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        print(f"📁 Searching: {search_dir}")

        try:
            # Search for video files
            for ext in video_extensions:
                for video_file in search_dir.rglob(f"*{ext}"):
                    if video_file.stat().st_size > 10 * 1024 * 1024:  # > 10MB
                        found_files['videos'].append(video_file)
                        print(f"   🎬 Found video: {video_file.name} ({video_file.stat().st_size / (1024*1024):.1f} MB)")

            # Search for subtitle files
            for ext in subtitle_extensions:
                for sub_file in search_dir.rglob(f"*{ext}"):
                    found_files['subtitles'].append(sub_file)
                    print(f"   📄 Found subtitle: {sub_file.name}")

        except PermissionError:
            print(f"   ⚠️  Permission denied: {search_dir}")
        except Exception as e:
            print(f"   ⚠️  Error searching {search_dir}: {e}")

    print(f"\n✅ Found {len(found_files['videos'])} video files")
    print(f"✅ Found {len(found_files['subtitles'])} subtitle files\n")

    return found_files


def interactive_test(found_files: dict):
    """Interactive testing"""

    if not found_files['videos'] and not found_files['subtitles']:
        print("❌ No anime files found.")
        print("\n💡 TIP: You can manually specify a file:")
        print("   python scripts/python/test_babelfish_anime.py <your_file>")
        return

    print("="*80)
    print("📋 FOUND FILES - Select one to test:")
    print("="*80 + "\n")

    all_files = []

    # List subtitle files first (easier to test)
    if found_files['subtitles']:
        print("📄 SUBTITLE FILES:")
        for i, sub_file in enumerate(found_files['subtitles'], 1):
            print(f"   {i}. {sub_file.name}")
            print(f"      Path: {sub_file}")
            all_files.append(('subtitle', sub_file))
        print()

    # List video files
    if found_files['videos']:
        print("🎬 VIDEO FILES:")
        start_idx = len(found_files['subtitles']) + 1
        for i, video_file in enumerate(found_files['videos'], start_idx):
            print(f"   {i}. {video_file.name}")
            print(f"      Path: {video_file}")
            all_files.append(('video', video_file))
        print()

    # Ask user to select
    try:
        choice = input(f"Enter number (1-{len(all_files)}) or 'q' to quit: ").strip()

        if choice.lower() == 'q':
            print("\n👋 Exiting...\n")
            return

        choice_num = int(choice)
        if 1 <= choice_num <= len(all_files):
            file_type, selected_file = all_files[choice_num - 1]

            print(f"\n✅ Selected: {selected_file.name}")
            print(f"   Type: {file_type}")
            print(f"   Path: {selected_file}\n")

            # Test it
            print("="*80)
            print("🐟 TESTING WITH BABELFISH")
            print("="*80 + "\n")

            from test_babelfish_anime import test_with_file
            test_with_file(str(selected_file))
        else:
            print(f"❌ Invalid choice. Please enter 1-{len(all_files)}")

    except ValueError:
        print("❌ Invalid input. Please enter a number or 'q'")
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Find and Test Anime Files with Babelfish")
        parser.add_argument("--dir", help="Directory to search (default: common locations)")
        parser.add_argument("--file", help="Direct file path to test")

        args = parser.parse_args()

        if args.file:
            # Test directly with provided file
            from test_babelfish_anime import test_with_file
            test_with_file(args.file)
        else:
            # Find files
            search_dirs = [Path(args.dir)] if args.dir else None
            found_files = find_anime_files(search_dirs)

            # Interactive test
            interactive_test(found_files)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()