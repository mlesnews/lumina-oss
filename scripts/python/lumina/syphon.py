#!/usr/bin/env python3
"""
@syphon - Pattern Search and Extraction

Lower-ranked alias for grep - pattern search and extraction.
Part of the flow: @syphon => @pipe => @peak <=> @reality

Tags: #SYPHON #SEARCH #PATTERN #EXTRACTION @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import re
import sys

# Add project root to path for unified engine
script_dir = Path(__file__).parent.parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.pattern_unified_engine import PatternUnifiedEngine
    UNIFIED_ENGINE_AVAILABLE = True
except ImportError:
    UNIFIED_ENGINE_AVAILABLE = False
    PatternUnifiedEngine = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("Syphon")


class Syphon:
    """
    @syphon - Pattern Search and Extraction

    Lower-ranked alias for grep. Extracts patterns, searches codebase,
    finds information. Output flows to @pipe for processing.

    Part of flow: @syphon => @pipe => @peak <=> @reality
    """

    def __init__(self):
        """Initialize @syphon"""
        logger.info("🔍 @syphon initialized (pattern search)")

        # Initialize unified pattern engine if available
        if UNIFIED_ENGINE_AVAILABLE:
            self.unified_engine = PatternUnifiedEngine()
            logger.info("   ✅ Using Pattern Unified Engine (EXTRAPOLATION <=> REGEX <=> PATTERN MATCHING)")
        else:
            self.unified_engine = None
            logger.warning("   ⚠️  Pattern Unified Engine not available, using fallback")

    def search(
        self,
        pattern: str,
        path: Optional[str] = None,
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Search for pattern in codebase.

        Args:
            pattern: Pattern to search for
            path: Path to search (default: current directory)
            case_sensitive: Case sensitive search

        Returns:
            Search results
        """
        if path is None:
            path = "."

        path_obj = Path(path)
        if not path_obj.exists():
            return {
                'error': f'Path not found: {path}',
                'matches': []
            }

        # Use unified engine if available
        if self.unified_engine:
            try:
                # Read file content for unified engine
                if path_obj.is_file():
                    with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()
                    result = self.unified_engine.unified_operation("extract", data, pattern)
                    matches = [{"file": str(path_obj), "match": m, "line": 0} for m in result.extracted]
                elif path_obj.is_dir():
                    matches = []
                    for file_path in path_obj.rglob("*"):
                        if file_path.is_file():
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    data = f.read()
                                result = self.unified_engine.unified_operation("extract", data, pattern)
                                matches.extend([{"file": str(file_path), "match": m, "line": 0} for m in result.extracted])
                            except Exception:
                                continue
            except Exception as e:
                logger.warning(f"   Unified engine error, falling back: {e}")
                # Fall through to original implementation
                pass

        # Fallback to original implementation
        if not matches:
            matches = []
            flags = 0 if case_sensitive else re.IGNORECASE

            try:
                pattern_re = re.compile(pattern, flags)

                # Search files
                if path_obj.is_file():
                    matches.extend(self._search_file(path_obj, pattern_re))
                elif path_obj.is_dir():
                    for file_path in path_obj.rglob("*"):
                        if file_path.is_file():
                            matches.extend(self._search_file(file_path, pattern_re))
            except re.error as e:
                return {
                    'error': f'Invalid pattern: {e}',
                    'matches': []
                }

        return {
            'pattern': pattern,
            'path': str(path),
            'match_count': len(matches),
            'matches': matches
        }

    def _search_file(self, file_path: Path, pattern: re.Pattern) -> List[Dict[str, Any]]:
        """Search pattern in a single file"""
        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.search(line):
                        matches.append({
                            'file': str(file_path),
                            'line': line_num,
                            'content': line.strip()
                        })
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")

        return matches

    def extract_patterns(
        self,
        pattern: str,
        path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract patterns from codebase.

        Args:
            pattern: Pattern to extract
            path: Path to search

        Returns:
            Extracted patterns
        """
        results = self.search(pattern, path)

        # Extract unique patterns
        patterns = set()
        for match in results.get('matches', []):
            # Extract pattern from match
            content = match.get('content', '')
            # Simple extraction - can be enhanced
            patterns.add(content)

        return {
            'pattern': pattern,
            'extracted_count': len(patterns),
            'patterns': list(patterns),
            'raw_results': results
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("🔍 @SYPHON - Pattern Search and Extraction")
    print("=" * 80)
    print()

    syphon = Syphon()

    # Search
    print("SEARCHING:")
    print("-" * 80)
    results = syphon.search("balance", "scripts/python/lumina")
    print(f"Pattern: {results['pattern']}")
    print(f"Matches: {results['match_count']}")
    if results['match_count'] > 0:
        print(f"First match: {results['matches'][0]}")
    print()

    # Extract patterns
    print("EXTRACTING PATTERNS:")
    print("-" * 80)
    extracted = syphon.extract_patterns("def.*balance", "scripts/python/lumina")
    print(f"Extracted: {extracted['extracted_count']} patterns")
    print()

    print("=" * 80)
    print("🔍 @syphon => @pipe => @peak <=> @reality")
    print("=" * 80)


if __name__ == "__main__":


    main()