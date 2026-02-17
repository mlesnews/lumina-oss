#!/usr/bin/env python3
"""
JARVIS Summary Reader

Reads summaries to user using TTS, with intelligent filtering:
- Skips code blocks
- Skips blank code
- Condenses/paraphrases using max tokens
- Uses condensed function from chat
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    JARVISElevenLabsTTS = None

logger = get_logger("JARVISSummaryReader")


class JARVISSummaryReader:
    """
    Reads summaries to user with intelligent filtering

    - Skips code blocks
    - Skips blank code
    - Condenses/paraphrases
    - Uses max tokens for summarization
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # TTS integration
        self.tts = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.tts = JARVISElevenLabsTTS(project_root=project_root)
                self.logger.info("✅ ElevenLabs TTS integrated")
            except Exception as e:
                self.logger.debug(f"ElevenLabs TTS not available: {e}")

        # Code block patterns
        self.code_block_patterns = [
            r'```[\s\S]*?```',  # Markdown code blocks
            r'`[^`]+`',  # Inline code
            r'<code>[\s\S]*?</code>',  # HTML code tags
            r'<pre>[\s\S]*?</pre>',  # HTML pre tags
        ]

        # Max tokens for condensing
        self.max_tokens = 500  # Default max tokens for summary

    def _remove_code_blocks(self, text: str) -> str:
        """Remove all code blocks from text"""
        cleaned = text

        for pattern in self.code_block_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE)

        # Remove blank lines and excessive whitespace
        lines = cleaned.split('\n')
        filtered_lines = []

        for line in lines:
            stripped = line.strip()
            # Skip blank lines and lines that look like code
            if stripped and not self._is_code_line(stripped):
                filtered_lines.append(stripped)

        return '\n'.join(filtered_lines)

    def _is_code_line(self, line: str) -> bool:
        """Check if a line looks like code"""
        # Heuristics for code detection
        code_indicators = [
            r'^\s*(def|class|import|from|if|for|while|return|try|except)\s',  # Python keywords
            r'^\s*[{}();]',  # Code punctuation at start
            r'^\s*\w+\s*=\s*[^=]',  # Variable assignment
            r'^\s*#.*',  # Comments
            r'^\s*//.*',  # Comments
            r'^\s*/\*.*',  # Comments
        ]

        for pattern in code_indicators:
            if re.match(pattern, line):
                return True

        return False

    def _condense_text(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Condense text using max tokens approach

        Uses simple truncation with sentence boundaries for now.
        In production, would use LLM for intelligent summarization.
        """
        if max_tokens is None:
            max_tokens = self.max_tokens

        # Simple word-based token estimation (rough: 1 token ≈ 0.75 words)
        words = text.split()
        estimated_tokens = len(words) * 0.75

        if estimated_tokens <= max_tokens:
            return text

        # Truncate to approximately max_tokens
        target_words = int(max_tokens / 0.75)
        truncated = ' '.join(words[:target_words])

        # Try to end at sentence boundary
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')

        last_sentence_end = max(last_period, last_exclamation, last_question)

        if last_sentence_end > target_words * 0.5:  # If we found a sentence end reasonably close
            truncated = truncated[:last_sentence_end + 1]

        # Add ellipsis if truncated
        if len(words) > target_words:
            truncated += "..."

        return truncated

    def _paraphrase_condense(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Paraphrase and condense text

        Uses the condensed function approach from chat.
        For now, uses simple condensing. In production, would use LLM.
        """
        # Remove code blocks first
        cleaned = self._remove_code_blocks(text)

        # Condense
        condensed = self._condense_text(cleaned, max_tokens)

        return condensed

    def read_summary(self, text: str, max_tokens: Optional[int] = None, skip_code: bool = True) -> Dict[str, Any]:
        """
        Read summary to user

        Args:
            text: Text to read
            max_tokens: Max tokens for condensing (default: 500)
            skip_code: Skip code blocks (default: True)
        """
        self.logger.info("📖 Reading summary...")

        # Process text
        if skip_code:
            processed = self._remove_code_blocks(text)
        else:
            processed = text

        # Condense/paraphrase
        condensed = self._paraphrase_condense(processed, max_tokens)

        self.logger.info(f"📝 Condensed to ~{len(condensed.split())} words")

        # Read with TTS
        if self.tts:
            try:
                # Try to speak (will fail gracefully if TTS not configured)
                self.tts.speak(condensed)
                return {
                    'success': True,
                    'read': condensed,
                    'original_length': len(text),
                    'condensed_length': len(condensed)
                }
            except Exception as e:
                self.logger.error(f"TTS error: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'read': condensed
                }
        else:
            # Fallback: just log
            self.logger.info(f"🗣️  Would read: {condensed[:100]}...")
            return {
                'success': False,
                'error': 'TTS not available',
                'read': condensed
            }

    def read_file_summary(self, file_path: Path, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Read summary from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return self.read_summary(content, max_tokens)

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Summary Reader")
        parser.add_argument("--text", type=str, help="Text to read")
        parser.add_argument("--file", type=str, help="File to read")
        parser.add_argument("--max-tokens", type=int, default=500, help="Max tokens for condensing")
        parser.add_argument("--no-skip-code", action="store_true", help="Don't skip code blocks")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        reader = JARVISSummaryReader(project_root)

        if args.file:
            result = reader.read_file_summary(Path(args.file), args.max_tokens)
        elif args.text:
            result = reader.read_summary(args.text, args.max_tokens, skip_code=not args.no_skip_code)
        else:
            print("Usage:")
            print("  --text 'text to read'     : Read text")
            print("  --file path/to/file       : Read file")
            print("  --max-tokens 500          : Max tokens for condensing")
            print("  --no-skip-code            : Don't skip code blocks")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()