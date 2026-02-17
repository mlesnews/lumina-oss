#!/usr/bin/env python3
"""
Babelfish Subtitle Extractor - Phase 1

The SIMPLEST approach: Extract subtitles from video files.
If subtitles exist, use them. If not, translate them.

This is the "right under our noses" solution.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import re
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BabelfishSubtitleExtractor")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BabelfishSubtitleExtractor:
    """
    Extract and translate subtitles from video files.

    This is Phase 1 - the simplest approach.
    If the video has subtitles, we extract them.
    If they're in Japanese, we translate them.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("BabelfishSubtitleExtractor")

        self.data_dir = self.project_root / "data" / "babelfish"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.translator = None
        self.logger.info("🐟 Babelfish Subtitle Extractor initialized")

    def _initialize_translator(self) -> bool:
        """Initialize translation service"""
        try:
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source="ja", target="en")
            self.logger.info("✅ Translation service initialized")
            return True
        except ImportError:
            try:
                from googletrans import Translator
                self.translator = Translator()
                self.logger.info("✅ Translation service initialized (googletrans)")
                return True
            except ImportError:
                self.logger.warning("❌ No translation library. Install: pip install deep-translator")
                return False
        except Exception as e:
            self.logger.error(f"❌ Translation init error: {e}")
            return False

    def extract_subtitles_from_srt(self, srt_file: Path) -> List[Dict[str, Any]]:
        """Extract subtitles from .srt file"""
        try:
            import pysrt
            subs = pysrt.open(str(srt_file))

            subtitles = []
            for sub in subs:
                subtitles.append({
                    "index": sub.index,
                    "start": str(sub.start),
                    "end": str(sub.end),
                    "text": sub.text,
                    "text_clean": sub.text.replace('\n', ' ').strip()
                })

            self.logger.info(f"✅ Extracted {len(subtitles)} subtitles from {srt_file.name}")
            return subtitles

        except ImportError:
            self.logger.warning("❌ pysrt not installed. Install: pip install pysrt")
            # Fallback: manual parsing
            return self._parse_srt_manual(srt_file)
        except Exception as e:
            self.logger.error(f"❌ Error extracting subtitles: {e}")
            return []

    def _parse_srt_manual(self, srt_file: Path) -> List[Dict[str, Any]]:
        """Manual SRT parsing (fallback)"""
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple SRT parser
            pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\d+\n|\n*$)'
            matches = re.findall(pattern, content, re.DOTALL)

            subtitles = []
            for match in matches:
                index, start, end, text = match
                subtitles.append({
                    "index": int(index),
                    "start": start,
                    "end": end,
                    "text": text.strip(),
                    "text_clean": text.replace('\n', ' ').strip()
                })

            self.logger.info(f"✅ Manually parsed {len(subtitles)} subtitles")
            return subtitles

        except Exception as e:
            self.logger.error(f"❌ Manual parsing error: {e}")
            return []

    def extract_subtitles_from_video(self, video_file: Path) -> List[Dict[str, Any]]:
        """Extract subtitles from video file using ffmpeg"""
        try:
            import subprocess

            # Check if ffmpeg is available
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.warning("❌ ffmpeg not found. Install ffmpeg to extract subtitles from video files.")
                return []

            # Extract subtitles
            output_srt = self.data_dir / f"{video_file.stem}_extracted.srt"

            cmd = [
                'ffmpeg',
                '-i', str(video_file),
                '-map', '0:s:0',  # First subtitle track
                str(output_srt)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if output_srt.exists():
                self.logger.info(f"✅ Extracted subtitles to {output_srt.name}")
                return self.extract_subtitles_from_srt(output_srt)
            else:
                self.logger.warning("❌ No subtitles found in video file")
                return []

        except FileNotFoundError:
            self.logger.warning("❌ ffmpeg not found. Install ffmpeg.")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error extracting from video: {e}")
            return []

    def translate_subtitles(self, subtitles: List[Dict[str, Any]], 
                           source_lang: str = "ja", 
                           target_lang: str = "en") -> List[Dict[str, Any]]:
        """Translate subtitles"""
        if not self.translator:
            if not self._initialize_translator():
                return subtitles

        translated = []

        for sub in subtitles:
            original_text = sub.get("text_clean", sub.get("text", ""))

            if not original_text.strip():
                translated.append(sub)
                continue

            try:
                # Translate
                if hasattr(self.translator, 'translate'):
                    translated_text = self.translator.translate(original_text)
                else:
                    result = self.translator.translate(original_text, src=source_lang, dest=target_lang)
                    translated_text = result.text

                # Add translation
                sub_translated = sub.copy()
                sub_translated["original_text"] = original_text
                sub_translated["translated_text"] = translated_text
                sub_translated["source_language"] = source_lang
                sub_translated["target_language"] = target_lang

                translated.append(sub_translated)

                self.logger.debug(f"Translated: '{original_text[:50]}...' → '{translated_text[:50]}...'")

            except Exception as e:
                self.logger.error(f"Translation error: {e}")
                translated.append(sub)

        self.logger.info(f"✅ Translated {len(translated)} subtitles")
        return translated

    def save_translated_subtitles(self, subtitles: List[Dict[str, Any]], 
                                  output_file: Optional[Path] = None) -> Path:
        try:
            """Save translated subtitles to file"""
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = self.data_dir / f"translated_subtitles_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(subtitles, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Saved translated subtitles: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in save_translated_subtitles: {e}", exc_info=True)
            raise

    def create_translated_srt(self, subtitles: List[Dict[str, Any]], 
                              output_file: Optional[Path] = None) -> Path:
        """Create a new .srt file with translations"""
        try:
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = self.data_dir / f"translated_{timestamp}.srt"

            with open(output_file, 'w', encoding='utf-8') as f:
                for sub in subtitles:
                    f.write(f"{sub['index']}\n")
                    f.write(f"{sub['start']} --> {sub['end']}\n")

                    # Write both original and translated if available
                    if 'translated_text' in sub:
                        f.write(f"{sub['translated_text']}\n")
                        f.write(f"[Original: {sub.get('original_text', '')}]\n")
                    else:
                        f.write(f"{sub.get('text_clean', sub.get('text', ''))}\n")

                    f.write("\n")

            self.logger.info(f"📁 Created translated SRT: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in create_translated_srt: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Babelfish Subtitle Extractor - Phase 1")
        parser.add_argument("input", help="Input video file or .srt subtitle file")
        parser.add_argument("--translate", action="store_true", help="Translate subtitles to English")
        parser.add_argument("--output", help="Output file (default: auto-generated)")

        args = parser.parse_args()

        print("\n" + "="*80)
        print("🐟 BABELFISH SUBTITLE EXTRACTOR - Phase 1")
        print("="*80 + "\n")
        print("The simplest approach: Extract and translate subtitles from video files.")
        print("If subtitles exist, use them. If they're in Japanese, translate them.\n")

        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ File not found: {input_path}")
            return

        extractor = BabelfishSubtitleExtractor()

        # Extract subtitles
        if input_path.suffix.lower() == '.srt':
            print(f"📄 Extracting subtitles from SRT file: {input_path.name}")
            subtitles = extractor.extract_subtitles_from_srt(input_path)
        else:
            print(f"🎬 Extracting subtitles from video file: {input_path.name}")
            subtitles = extractor.extract_subtitles_from_video(input_path)

        if not subtitles:
            print("❌ No subtitles found or extracted.")
            return

        print(f"✅ Extracted {len(subtitles)} subtitles\n")

        # Translate if requested
        if args.translate:
            print("🌐 Translating subtitles...")
            subtitles = extractor.translate_subtitles(subtitles)
            print(f"✅ Translated {len(subtitles)} subtitles\n")

        # Save results
        output_path = Path(args.output) if args.output else None
        json_file = extractor.save_translated_subtitles(subtitles, output_path)

        if args.translate:
            srt_file = extractor.create_translated_srt(subtitles)
            print(f"\n📁 Files created:")
            print(f"   JSON: {json_file}")
            print(f"   SRT: {srt_file}")
        else:
            print(f"\n📁 Subtitles saved: {json_file}")

        print("\n✅ Done!\n")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()