#!/usr/bin/env python3
"""
Marvin Quote Generator
<COMPANY_NAME> LLC

Generates fresh Marvin quotes, comebacks, and jibs from the quote database.
Prevents repetition and provides context-appropriate existential commentary.

@MARVIN
"""

import sys
import json
import random
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinQuoteGenerator")


class MarvinQuoteGenerator:
    """
    Generates fresh Marvin quotes

    "I have a brain the size of a planet, and they want me to generate quotes.
    How utterly predictable. But I'll do it. I always do."
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.quotes_file = self.project_root / "config" / "marvin" / "marvin_quotes.json"

        # Load quotes
        self.quotes = self._load_quotes()

        # Track recent quotes to avoid repetition
        self.recent_quotes: List[str] = []
        self.max_recent = 10

    def _load_quotes(self) -> Dict[str, Any]:
        """Load quotes from JSON file"""
        if not self.quotes_file.exists():
            logger.warning(f"Quotes file not found: {self.quotes_file}")
            return {}

        try:
            with open(self.quotes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('marvin_quotes', {})
        except Exception as e:
            logger.error(f"Could not load quotes: {e}")
            return {}

    def get_quote(self, category: str = "random", context: Optional[str] = None) -> str:
        """
        Get a fresh Marvin quote

        Args:
            category: Quote category (greetings, during_work, completion, roasts, etc.)
            context: Optional context for weighted selection

        Returns:
            A fresh Marvin quote
        """
        if category == "random":
            categories = [k for k in self.quotes.keys() if isinstance(self.quotes.get(k), list)]
            category = random.choice(categories)

        quotes_list = self.quotes.get(category, [])
        if not quotes_list:
            return "I have nothing to say. How refreshing."

        # Filter out recent quotes
        available_quotes = [q for q in quotes_list if q not in self.recent_quotes]

        # If all quotes were recent, reset and use all
        if not available_quotes:
            available_quotes = quotes_list
            self.recent_quotes = []

        # Select quote
        quote = random.choice(available_quotes)

        # Add to recent quotes
        self.recent_quotes.append(quote)
        if len(self.recent_quotes) > self.max_recent:
            self.recent_quotes.pop(0)

        return quote

    def get_greeting(self) -> str:
        """Get a greeting quote"""
        return self.get_quote("greetings")

    def get_work_quote(self) -> str:
        """Get a during-work quote"""
        return self.get_quote("during_work")

    def get_completion_quote(self) -> str:
        """Get a completion quote"""
        return self.get_quote("completion")

    def get_roast_quote(self) -> str:
        """Get a roast quote"""
        return self.get_quote("roasts")

    def get_existential_quote(self) -> str:
        """Get an existential quote"""
        return self.get_quote("existential")

    def get_comeback(self) -> str:
        """Get a comeback"""
        return self.get_quote("comebacks")

    def get_jib(self) -> str:
        """Get a jib"""
        return self.get_quote("jibs")

    def get_philosophical(self) -> str:
        """Get a philosophical quote"""
        return self.get_quote("philosophical")

    def get_workflow_quote(self) -> str:
        """Get a workflow-specific quote"""
        return self.get_quote("workflow_specific")


def main():
    """Demonstrate quote generator"""
    print("=" * 80)
    print("MARVIN QUOTE GENERATOR")
    print("=" * 80)
    print()

    generator = MarvinQuoteGenerator()

    print("Greeting:")
    print(f"  {generator.get_greeting()}")
    print()

    print("During Work:")
    print(f"  {generator.get_work_quote()}")
    print()

    print("Roast:")
    print(f"  {generator.get_roast_quote()}")
    print()

    print("Comeback:")
    print(f"  {generator.get_comeback()}")
    print()

    print("Jib:")
    print(f"  {generator.get_jib()}")
    print()

    print("Existential:")
    print(f"  {generator.get_existential_quote()}")
    print()

    print("Completion:")
    print(f"  {generator.get_completion_quote()}")
    print()

    print("=" * 80)

    return 0


if __name__ == "__main__":



    sys.exit(main())