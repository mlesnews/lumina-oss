#!/usr/bin/env python3
"""
Unified @asks Processor
Handles @asks the same way regardless of input source (direct-text or voice-transcribed)

Tags: #ASKS #UNIFIED #TEXT #VOICE @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UnifiedAskProcessor")

try:
    from jarvis_restack_all_asks import ASKRestacker
    ASKS_AVAILABLE = True
except ImportError:
    ASKS_AVAILABLE = False
    ASKRestacker = None
    logger.warning("ASKRestacker not available")


class UnifiedAskProcessor:
    """
    Unified processor for @asks from any input source.
    Treats direct-text and voice-transcribed input identically.
    """

    def __init__(self, project_root: Optional[Path] = None, ask_restacker: Optional[ASKRestacker] = None):
        """
        Initialize unified ask processor

        Args:
            project_root: Project root directory
            ask_restacker: Optional ASKRestacker instance (will create if not provided)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # Initialize @asks system
        if ask_restacker:
            self.ask_restacker = ask_restacker
        elif ASKS_AVAILABLE:
            try:
                self.ask_restacker = ASKRestacker(project_root)
                logger.info("✅ Unified @asks processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize ASKRestacker: {e}")
                self.ask_restacker = None
        else:
            self.ask_restacker = None
            logger.warning("⚠️  @asks system not available")

    def process_ask(self, input_text: str, source: str = "unknown", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an @ask from any input source (text or voice-transcribed)

        Args:
            input_text: The input text (from direct text or voice transcription)
            source: Source identifier ("direct-text", "voice-transcribed", "chat", etc.)
            metadata: Optional metadata (timestamp, user_id, etc.)

        Returns:
            Dict with processing results
        """
        if not self.ask_restacker:
            return {
                "success": False,
                "error": "@asks system not available",
                "input_text": input_text,
                "source": source
            }

        # Normalize input text (same processing regardless of source)
        normalized_text = self._normalize_input(input_text)

        # Extract @asks from normalized text
        asks = self._extract_asks_from_text(normalized_text)

        # Process each ask
        results = []
        for ask in asks:
            result = self._process_single_ask(ask, source, metadata)
            results.append(result)

        return {
            "success": True,
            "input_text": input_text,
            "normalized_text": normalized_text,
            "source": source,
            "asks_found": len(asks),
            "asks": asks,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    def _normalize_input(self, text: str) -> str:
        """
        Normalize input text (same for both direct-text and voice-transcribed)

        Handles:
        - Voice transcription artifacts (punctuation, capitalization)
        - Common speech patterns
        - @ask markers
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Normalize @ask markers (handle variations)
        text = re.sub(r'@\s*ask\s*[:]?\s*', '@ASK ', text, flags=re.IGNORECASE)
        text = re.sub(r'@\s*asks\s*[:]?\s*', '@ASK ', text, flags=re.IGNORECASE)

        # Normalize common voice transcription patterns
        # "at ask" -> "@ASK"
        text = re.sub(r'\bat\s+ask\s*[:]?\s*', '@ASK ', text, flags=re.IGNORECASE)

        # Handle voice transcription punctuation issues
        # "period" -> "."
        text = re.sub(r'\s+period\s+', '. ', text, flags=re.IGNORECASE)
        # "comma" -> ","
        text = re.sub(r'\s+comma\s+', ', ', text, flags=re.IGNORECASE)

        # Normalize capitalization for @ASK markers
        text = re.sub(r'@ask\s+', '@ASK ', text, flags=re.IGNORECASE)

        return text

    def _extract_asks_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract @asks from normalized text (uses ASKRestacker pattern matching)
        """
        if not self.ask_restacker:
            return []

        # Use ASKRestacker's pattern matching
        asks = self.ask_restacker._find_ask_patterns(text)

        return asks

    def _process_single_ask(self, ask: Dict[str, Any], source: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a single @ask (same logic regardless of source)
        """
        ask_text = ask.get("text", "")
        priority = ask.get("priority", "normal")
        category = ask.get("category", "general")

        # Add source information
        ask["source"] = source
        ask["processed_at"] = datetime.now().isoformat()
        if metadata:
            ask["metadata"] = metadata

        logger.info(f"📝 Processing @ask from {source}: {ask_text[:80]}... (priority: {priority}, category: {category})")

        return {
            "success": True,
            "ask": ask,
            "priority": priority,
            "category": category
        }

    def process_batch(self, inputs: List[Dict[str, str]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a batch of @asks from multiple sources

        Args:
            inputs: List of dicts with "text" and "source" keys
            metadata: Optional metadata for the batch

        Returns:
            Dict with batch processing results
        """
        results = []
        for input_item in inputs:
            text = input_item.get("text", "")
            source = input_item.get("source", "unknown")
            result = self.process_ask(text, source, metadata)
            results.append(result)

        return {
            "success": True,
            "batch_size": len(inputs),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }


def process_ask_unified(input_text: str, source: str = "unknown", project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function to process a single @ask

    Args:
        input_text: Input text (from any source)
        source: Source identifier
        project_root: Optional project root

    Returns:
        Processing result dict
    """
    processor = UnifiedAskProcessor(project_root=project_root)
    return processor.process_ask(input_text, source)


if __name__ == "__main__":
    # Test unified processor
    processor = UnifiedAskProcessor()

    # Test with direct text
    print("\n" + "="*80)
    print("Testing Unified @asks Processor")
    print("="*80 + "\n")

    # Test 1: Direct text
    print("Test 1: Direct Text Input")
    result1 = processor.process_ask("@ASK please add feature X", source="direct-text")
    print(f"  Found {result1['asks_found']} asks")
    print(f"  Success: {result1['success']}\n")

    # Test 2: Voice transcribed
    print("Test 2: Voice Transcribed Input")
    result2 = processor.process_ask("at ask please add feature Y", source="voice-transcribed")
    print(f"  Found {result2['asks_found']} asks")
    print(f"  Success: {result2['success']}\n")

    # Test 3: Batch processing
    print("Test 3: Batch Processing (Mixed Sources)")
    batch_inputs = [
        {"text": "@ASK fix bug in module Z", "source": "direct-text"},
        {"text": "at ask please update documentation", "source": "voice-transcribed"},
        {"text": "can you please implement feature W", "source": "chat"}
    ]
    result3 = processor.process_batch(batch_inputs)
    print(f"  Processed {result3['batch_size']} inputs")
    print(f"  Total asks found: {sum(r['asks_found'] for r in result3['results'])}\n")

    print("="*80)
    print("✅ Unified @asks Processor Test Complete")
    print("="*80)
