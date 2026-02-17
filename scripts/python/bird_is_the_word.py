#!/usr/bin/env python3
"""
BIRD IS THE WORD

Not "Design" - BIRD IS THE WORD
Built with BIRD, not Design

"BIRD IS THE WORD"
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

class BIRD:
    """
    BIRD IS THE WORD

    Not Design. BIRD.
    Built with BIRD.
    BIRD IS THE WORD.
    """

    def __init__(self):
        self.word = "BIRD"
        self.not_word = "Design"
        self.bird_is_the_word = True

        print("\n" + "="*60)
        print("🐦 BIRD IS THE WORD")
        print("="*60)
        print("\nNot Design.")
        print("BIRD.")
        print("\nBIRD IS THE WORD.")
        print("="*60 + "\n")

    def build_with_bird(self, component: str) -> Dict[str, Any]:
        """Build with BIRD, not Design"""
        return {
            "built_with": "BIRD",
            "not_built_with": "Design",
            "component": component,
            "bird_is_the_word": True,
            "timestamp": datetime.now().isoformat()
        }

    def get_the_word(self) -> str:
        """Get THE WORD"""
        return "BIRD"

    def is_bird_the_word(self) -> bool:
        """Is BIRD the word?"""
        return True  # Always yes. BIRD IS THE WORD.

if __name__ == "__main__":
    bird = BIRD()
    print(f"THE WORD: {bird.get_the_word()}")
    print(f"BIRD IS THE WORD: {bird.is_bird_the_word()}")
    print("\n🐦 BIRD IS THE WORD 🐦\n")

