#!/usr/bin/env python3
"""
Test Babelfish with Anime

Quick test script to test the Babelfish translation system with anime.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TestBabelfishAnime")


def test_translation():
    """Test translation with sample Japanese anime phrases"""

    print("\n" + "="*80)
    print("🐟 TESTING BABELFISH WITH ANIME - Sample Translation")
    print("="*80 + "\n")

    # Sample Japanese anime phrases
    test_phrases = [
        "こんにちは",  # Hello
        "ありがとうございます",  # Thank you very much
        "すみません",  # Excuse me / I'm sorry
        "おはようございます",  # Good morning
        "さようなら",  # Goodbye
        "頑張ってください",  # Good luck / Do your best
        "大丈夫ですか",  # Are you okay?
        "助けてください",  # Please help me
        "愛してる",  # I love you
        "ごめんなさい"  # I'm sorry
    ]

    # Try to use deep-translator
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source="ja", target="en")
        print("✅ Using deep-translator\n")

        results = []
        for i, phrase in enumerate(test_phrases, 1):
            try:
                translated = translator.translate(phrase)
                results.append({
                    "original": phrase,
                    "translated": translated,
                    "status": "success"
                })
                print(f"{i:2d}. 🇯🇵 {phrase:15s} → 🇺🇸 {translated}")
            except Exception as e:
                results.append({
                    "original": phrase,
                    "translated": None,
                    "status": "error",
                    "error": str(e)
                })
                print(f"{i:2d}. 🇯🇵 {phrase:15s} → ❌ Error: {e}")

        # Save results
        project_root = Path(".").resolve()
        data_dir = project_root / "data" / "babelfish"
        data_dir.mkdir(parents=True, exist_ok=True)

        test_file = data_dir / f"test_translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_type": "sample_anime_phrases",
                "results": results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n📁 Test results saved: {test_file}")
        print("\n✅ Translation test complete!\n")

        return True

    except ImportError:
        print("❌ deep-translator not installed")
        print("   Install: pip install deep-translator")
        return False
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return False


def test_with_file(file_path: str):
    """Test with a video or subtitle file"""

    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    print(f"\n📁 Testing with file: {file_path.name}\n")

    # Check if it's a subtitle file
    if file_path.suffix.lower() in ['.srt', '.ass', '.ssa', '.vtt']:
        print("📄 Subtitle file detected - extracting and translating...\n")

        try:
            from babelfish_subtitle_extractor import BabelfishSubtitleExtractor

            extractor = BabelfishSubtitleExtractor()

            # Extract subtitles
            subtitles = extractor.extract_subtitles_from_srt(file_path)

            if not subtitles:
                print("❌ No subtitles found in file")
                return False

            print(f"✅ Extracted {len(subtitles)} subtitles\n")

            # Show first few
            print("First 5 subtitles:")
            for i, sub in enumerate(subtitles[:5], 1):
                print(f"  {i}. {sub.get('text_clean', sub.get('text', ''))[:100]}")

            # Translate
            print("\n🌐 Translating...")
            translated = extractor.translate_subtitles(subtitles)

            # Show translated versions
            print("\nFirst 5 translated subtitles:")
            for i, sub in enumerate(translated[:5], 1):
                original = sub.get('original_text', sub.get('text_clean', ''))
                translated_text = sub.get('translated_text', '')
                print(f"  {i}. 🇯🇵 {original[:50]}")
                print(f"     🇺🇸 {translated_text[:100]}")

            # Save
            output_file = extractor.save_translated_subtitles(translated)
            srt_file = extractor.create_translated_srt(translated)

            print(f"\n📁 Files created:")
            print(f"   JSON: {output_file}")
            print(f"   SRT: {srt_file}")
            print("\n✅ Translation complete!\n")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Video file
    elif file_path.suffix.lower() in ['.mp4', '.mkv', '.avi', '.mov']:
        print("🎬 Video file detected - attempting to extract subtitles...\n")

        try:
            from babelfish_subtitle_extractor import BabelfishSubtitleExtractor

            extractor = BabelfishSubtitleExtractor()

            # Extract subtitles from video
            subtitles = extractor.extract_subtitles_from_video(file_path)

            if not subtitles:
                print("❌ No subtitles found in video file")
                print("   The video may not have embedded subtitles")
                print("   Try providing a separate .srt file instead")
                return False

            print(f"✅ Extracted {len(subtitles)} subtitles\n")

            # Translate
            print("🌐 Translating...")
            translated = extractor.translate_subtitles(subtitles)

            # Save
            output_file = extractor.save_translated_subtitles(translated)
            srt_file = extractor.create_translated_srt(translated)

            print(f"\n📁 Files created:")
            print(f"   JSON: {output_file}")
            print(f"   SRT: {srt_file}")
            print("\n✅ Translation complete!\n")

            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    else:
        print(f"❌ Unsupported file type: {file_path.suffix}")
        print("   Supported: .srt, .ass, .ssa, .vtt, .mp4, .mkv, .avi, .mov")
        return False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Babelfish with Anime")
    parser.add_argument("file", nargs="?", help="Video or subtitle file to test (optional)")
    parser.add_argument("--sample", action="store_true", help="Test with sample phrases")

    args = parser.parse_args()

    if args.file:
        # Test with provided file
        test_with_file(args.file)
    elif args.sample:
        # Test with sample phrases
        test_translation()
    else:
        # Default: test with sample phrases
        print("No file provided. Testing with sample phrases...\n")
        test_translation()
        print("\n" + "="*80)
        print("💡 TIP: To test with your anime file:")
        print("   python scripts/python/test_babelfish_anime.py <your_file.srt>")
        print("   or")
        print("   python scripts/python/test_babelfish_anime.py <your_video.mp4>")
        print("="*80 + "\n")


if __name__ == "__main__":



    main()