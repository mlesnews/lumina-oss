#!/usr/bin/env python3
"""
Test regex pattern usage with SYPHON @ff regex tools
"""

from syphon.regex_tools import SyphonRegexTools, grep, awk, sed
from pathlib import Path

def test_pattern_search():
    """Test regex pattern searching"""
    tools = SyphonRegexTools()

    # Example text
    text = """
import sys
from pathlib import Path
import re

# Test comment
def function_name():
    pass

class ClassName:
    pass
"""

    # Pattern examples
    patterns = [
        (r'def\s+\w+', 'Function definitions'),
        (r'class\s+\w+', 'Class definitions'),
        (r'import\s+\w+', 'Import statements'),
        (r'#.*', 'Comments'),
    ]

    print("=" * 70)
    print("🔍 Regex Pattern Search Examples")
    print("=" * 70)

    for pattern, description in patterns:
        print(f"\n📋 Pattern: {pattern} ({description})")
        results = grep(pattern, text)
        print(f"   Found {len(results)} matches:")
        for result in results:
            print(f"   Line {result['line_number']}: {result['line'].strip()}")

    print("\n" + "=" * 70)
    print("✅ Regex pattern testing complete!")

if __name__ == "__main__":
    test_pattern_search()
