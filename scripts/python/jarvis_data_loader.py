#!/usr/bin/env python3
"""
JARVIS Comprehensive Data Loader

Loads and provides access to all JARVIS inspiration data from comprehensive research.
Siphons all JARVIS lore, quotes, personality traits, and capabilities.

Tags: #JARVIS #DATA #INSPIRATION #SYPHON @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDataLoader")


class JARVISDataLoader:
    """
    JARVIS Comprehensive Data Loader

    Loads all JARVIS inspiration data from comprehensive research:
    - MCU films
    - Marvel Comics
    - Disney+ resources
    - Fan sites and wikis
    - YouTube videos and shorts
    - Character analyses
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Data Loader"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_file = self.project_root / "data" / "jarvis_comprehensive_data.json"

        self.data: Dict[str, Any] = {}
        self._load_data()

        logger.info("✅ JARVIS Comprehensive Data Loader initialized")
        logger.info(f"   Loaded {len(self.get_all_quotes())} quotes")
        logger.info(f"   Loaded {len(self.get_capabilities())} capability categories")

    def _load_data(self):
        """Load comprehensive JARVIS data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"✅ Loaded JARVIS comprehensive data from {self.data_file.name}")
            except Exception as e:
                logger.error(f"❌ Error loading JARVIS data: {e}")
                self.data = {}
        else:
            logger.warning(f"⚠️  JARVIS data file not found: {self.data_file}")
            self.data = {}

    def get_personality_traits(self) -> List[str]:
        """Get core personality traits"""
        return self.data.get("jarvis", {}).get("personality", {}).get("core_traits", [])

    def get_communication_style(self) -> Dict[str, Any]:
        """Get communication style details"""
        return self.data.get("jarvis", {}).get("personality", {}).get("communication_style", {})

    def get_behavioral_patterns(self) -> List[str]:
        """Get behavioral patterns"""
        return self.data.get("jarvis", {}).get("personality", {}).get("behavioral_patterns", [])

    def get_all_quotes(self) -> List[Dict[str, Any]]:
        """Get all quotes organized by category"""
        quotes_data = self.data.get("jarvis", {}).get("quotes", {})
        all_quotes = []

        for category, quotes in quotes_data.items():
            if isinstance(quotes, list):
                for quote in quotes:
                    if isinstance(quote, dict):
                        quote["category"] = category
                        all_quotes.append(quote)
                    elif isinstance(quote, str):
                        all_quotes.append({
                            "quote": quote,
                            "category": category
                        })

        return all_quotes

    def get_quotes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get quotes by category (iconic, proactive, safety, operational, humor, greetings)"""
        quotes_data = self.data.get("jarvis", {}).get("quotes", {})
        return quotes_data.get(category, [])

    def get_random_quote(self, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a random quote, optionally filtered by category"""
        import random

        if category:
            quotes = self.get_quotes_by_category(category)
        else:
            quotes = self.get_all_quotes()

        if quotes:
            return random.choice(quotes)
        return None

    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get all capabilities organized by category"""
        return self.data.get("jarvis", {}).get("capabilities", {})

    def get_capabilities_by_category(self, category: str) -> List[str]:
        """Get capabilities by category"""
        capabilities = self.get_capabilities()
        return capabilities.get(category, [])

    def get_key_scenes(self) -> List[Dict[str, Any]]:
        """Get key scenes from films"""
        return self.data.get("jarvis", {}).get("key_scenes", [])

    def get_relationships(self) -> Dict[str, Any]:
        """Get relationship dynamics"""
        return self.data.get("jarvis", {}).get("relationships", {})

    def get_themes(self) -> List[str]:
        """Get thematic elements"""
        return self.data.get("jarvis", {}).get("themes", [])

    def get_visual_characteristics(self) -> Dict[str, Any]:
        """Get visual characteristics and color scheme"""
        return self.data.get("jarvis", {}).get("visual_characteristics", {})

    def get_origin_info(self) -> Dict[str, Any]:
        """Get origin and evolution information"""
        return self.data.get("jarvis", {}).get("origin", {})

    def get_edwin_jarvis_info(self) -> Dict[str, Any]:
        """Get Edwin Jarvis (human butler) information"""
        return self.data.get("edwin_jarvis", {})

    def get_films_appearances(self) -> List[str]:
        """Get list of films JARVIS appears in"""
        return self.data.get("jarvis", {}).get("films_appearances", [])

    def get_quote_for_context(self, context: str) -> Optional[Dict[str, Any]]:
        """Get a quote appropriate for a given context"""
        context_lower = context.lower()

        # Map contexts to quote categories
        context_mapping = {
            "greeting": "greetings",
            "welcome": "greetings",
            "safety": "safety",
            "warning": "safety",
            "danger": "safety",
            "operation": "operational",
            "system": "operational",
            "status": "operational",
            "proactive": "proactive",
            "analysis": "proactive",
            "threat": "proactive",
            "humor": "humor",
            "funny": "humor"
        }

        for key, category in context_mapping.items():
            if key in context_lower:
                quotes = self.get_quotes_by_category(category)
                if quotes:
                    import random
                    return random.choice(quotes)

        # Default to iconic quotes
        quotes = self.get_quotes_by_category("iconic")
        if quotes:
            import random
            return random.choice(quotes)

        return None

    def get_personality_summary(self) -> Dict[str, Any]:
        """Get comprehensive personality summary"""
        return {
            "core_traits": self.get_personality_traits(),
            "communication_style": self.get_communication_style(),
            "behavioral_patterns": self.get_behavioral_patterns(),
            "themes": self.get_themes(),
            "relationships": self.get_relationships()
        }

    def get_complete_profile(self) -> Dict[str, Any]:
        """Get complete JARVIS profile"""
        return {
            "origin": self.get_origin_info(),
            "personality": self.get_personality_summary(),
            "capabilities": self.get_capabilities(),
            "quotes": {
                "total": len(self.get_all_quotes()),
                "by_category": {
                    cat: len(self.get_quotes_by_category(cat))
                    for cat in ["iconic", "proactive", "safety", "operational", "humor", "greetings"]
                }
            },
            "key_scenes": len(self.get_key_scenes()),
            "visual": self.get_visual_characteristics(),
            "films": self.get_films_appearances(),
            "edwin_jarvis_inspiration": self.get_edwin_jarvis_info()
        }


def main():
    try:
        """Main entry point for testing"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Comprehensive Data Loader")
        parser.add_argument('--quotes', action='store_true', help='Show all quotes')
        parser.add_argument('--quote-category', type=str, help='Show quotes by category')
        parser.add_argument('--random-quote', action='store_true', help='Get random quote')
        parser.add_argument('--capabilities', action='store_true', help='Show capabilities')
        parser.add_argument('--personality', action='store_true', help='Show personality')
        parser.add_argument('--profile', action='store_true', help='Show complete profile')
        parser.add_argument('--context', type=str, help='Get quote for context')

        args = parser.parse_args()

        loader = JARVISDataLoader()

        if args.quotes:
            quotes = loader.get_all_quotes()
            print(f"\n📝 All JARVIS Quotes ({len(quotes)}):")
            print("=" * 80)
            for quote in quotes:
                if isinstance(quote, dict):
                    print(f"\n  \"{quote.get('quote', quote)}\"")
                    if 'context' in quote:
                        print(f"    Context: {quote['context']}")
                    if 'meaning' in quote:
                        print(f"    Meaning: {quote['meaning']}")
                    if 'category' in quote:
                        print(f"    Category: {quote['category']}")
                else:
                    print(f"  • {quote}")
            return 0

        if args.quote_category:
            quotes = loader.get_quotes_by_category(args.quote_category)
            print(f"\n📝 {args.quote_category.title()} Quotes ({len(quotes)}):")
            print("=" * 80)
            for quote in quotes:
                if isinstance(quote, dict):
                    print(f"\n  \"{quote.get('quote', quote)}\"")
                    if 'context' in quote:
                        print(f"    Context: {quote['context']}")
                else:
                    print(f"  • {quote}")
            return 0

        if args.random_quote:
            quote = loader.get_random_quote()
            if quote:
                print(f"\n🎲 Random JARVIS Quote:")
                print("=" * 80)
                if isinstance(quote, dict):
                    print(f"  \"{quote.get('quote', quote)}\"")
                    if 'context' in quote:
                        print(f"    Context: {quote['context']}")
                    if 'meaning' in quote:
                        print(f"    Meaning: {quote['meaning']}")
                else:
                    print(f"  {quote}")
            return 0

        if args.capabilities:
            capabilities = loader.get_capabilities()
            print(f"\n⚙️  JARVIS Capabilities:")
            print("=" * 80)
            for category, items in capabilities.items():
                print(f"\n  {category.replace('_', ' ').title()}:")
                for item in items:
                    print(f"    • {item}")
            return 0

        if args.personality:
            personality = loader.get_personality_summary()
            print(f"\n🧠 JARVIS Personality:")
            print("=" * 80)
            print(f"\n  Core Traits:")
            for trait in personality.get("core_traits", []):
                print(f"    • {trait}")
            print(f"\n  Communication Style:")
            for key, value in personality.get("communication_style", {}).items():
                print(f"    • {key}: {value}")
            print(f"\n  Behavioral Patterns:")
            for pattern in personality.get("behavioral_patterns", []):
                print(f"    • {pattern}")
            return 0

        if args.context:
            quote = loader.get_quote_for_context(args.context)
            if quote:
                print(f"\n💬 Quote for context '{args.context}':")
                print("=" * 80)
                if isinstance(quote, dict):
                    print(f"  \"{quote.get('quote', quote)}\"")
                else:
                    print(f"  {quote}")
            return 0

        if args.profile:
            profile = loader.get_complete_profile()
            print(f"\n📊 JARVIS Complete Profile:")
            print("=" * 80)
            print(json.dumps(profile, indent=2))
            return 0

        # Default: show summary
        profile = loader.get_complete_profile()
        print(f"\n📊 JARVIS Data Summary:")
        print("=" * 80)
        print(f"  Total Quotes: {profile['quotes']['total']}")
        print(f"  Key Scenes: {profile['key_scenes']}")
        print(f"  Films: {len(profile['films'])}")
        print(f"  Capability Categories: {len(profile['capabilities'])}")
        print(f"\n💡 Use --help for more options")
        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())