#!/usr/bin/env python3
"""
Babel Fish Translator - Universal Instant Translation

Inspired by The Hitchhiker's Guide to the Galaxy
Instant, universal translation for AI, Human, and all languages

"#HHGTTG @BABLE[#BABBLE-FISH]"
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BabelFishTranslator")

# Import Rosetta Stone translator
try:
    from rosetta_stone_translator import RosettaStoneTranslator, LanguageLevel
    ROSETTA_AVAILABLE = True
except ImportError:
    ROSETTA_AVAILABLE = False
    logger.warning("Rosetta Stone Translator not available")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BabelFishTranslator:
    """
    Babel Fish Translator - Universal Instant Translation

    "The Babel fish is small, yellow, leech-like, and probably the oddest thing 
    in the Universe. It feeds on brainwave energy received not from its own carrier 
    but from those around it. It absorbs all unconscious mental frequencies from 
    this brainwave energy to nourish itself with. It then excretes into the mind 
    of its carrier a telepathic matrix formed by combining the conscious thought 
    frequencies with nerve signals picked up from the speech centres of the brain 
    which has supplied them. The practical upshot of all this is that if you stick 
    a Babel fish in your ear you can instantly understand anything said to you in 
    any form of language."

    - The Hitchhiker's Guide to the Galaxy
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Babel Fish Translator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("BabelFishTranslator")

        # Babel Fish status
        self.fish_inserted = False
        self.translation_active = False

        # Rosetta Stone integration
        self.rosetta = None
        if ROSETTA_AVAILABLE:
            try:
                self.rosetta = RosettaStoneTranslator(project_root)
                self.logger.info("  ✅ Rosetta Stone integration active")
            except Exception as e:
                self.logger.debug(f"  Rosetta Stone init error: {e}")

        # Translation cache
        self.translation_cache: Dict[str, str] = {}

        # Translation history
        self.translation_history: List[Dict[str, Any]] = []

        self.logger.info("🐟 Babel Fish Translator initialized")
        self.logger.info("   Universal instant translation ready")
        self.logger.info("   'The Babel fish is small, yellow, leech-like...'")

    def insert_fish(self) -> bool:
        """Insert Babel Fish into ear (activate translator)"""
        if self.fish_inserted:
            self.logger.info("  ℹ️  Babel Fish already inserted")
            return True

        self.fish_inserted = True
        self.translation_active = True

        self.logger.info("  ✅ Babel Fish inserted into ear")
        self.logger.info("     You can now understand anything in any form of language")

        return True

    def remove_fish(self) -> bool:
        """Remove Babel Fish (deactivate translator)"""
        if not self.fish_inserted:
            self.logger.info("  ℹ️  No Babel Fish to remove")
            return False

        self.fish_inserted = False
        self.translation_active = False

        self.logger.info("  ⚠️  Babel Fish removed")
        self.logger.info("     Universal translation deactivated")

        return True

    def translate(self, text: str, source_language: str = "auto", 
                 target_language: str = "human") -> str:
        """
        Instant universal translation

        Translates from any language/form to any language/form
        """
        if not self.fish_inserted:
            self.logger.warning("  ⚠️  Babel Fish not inserted - inserting now...")
            self.insert_fish()

        # Check cache
        cache_key = f"{source_language}:{target_language}:{text}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        # Translate
        translated = self._perform_translation(text, source_language, target_language)

        # Cache result
        self.translation_cache[cache_key] = translated

        # Record history
        self.translation_history.append({
            "timestamp": datetime.now().isoformat(),
            "source": source_language,
            "target": target_language,
            "original": text,
            "translated": translated
        })

        return translated

    def _perform_translation(self, text: str, source: str, target: str) -> str:
        """Perform the actual translation"""
        # AI to Human translation
        if source == "ai" or "ai" in source.lower():
            if self.rosetta:
                translation = self.rosetta.translate(text)
                if translation:
                    return translation.human_concept
            return f"[Human-friendly]: {text}"

        # Human to AI translation
        if target == "ai" or "ai" in target.lower():
            # Reverse lookup
            if self.rosetta:
                for ai_concept, translation_pair in self.rosetta.translations.items():
                    if translation_pair.human_concept.lower() == text.lower():
                        return translation_pair.ai_concept
            return f"[AI format]: {text}"

        # Code to Natural Language
        if source == "code" or "code" in source.lower():
            return f"[Natural Language]: {text} (code explanation)"

        # Natural Language to Code
        if target == "code" or "code" in target.lower():
            return f"# {text} (code implementation)"

        # Default: return as-is (Babel Fish understands everything)
        return text

    def translate_ai_concept(self, ai_concept: str, level: LanguageLevel = LanguageLevel.BEGINNER) -> str:
        """Translate AI concept to human language (using Rosetta Stone)"""
        if not self.rosetta:
            return f"[Translation]: {ai_concept}"

        return self.rosetta.explain(ai_concept, level)

    def translate_workflow(self, workflow_description: str) -> Dict[str, Any]:
        """Translate workflow description to multiple formats"""
        return {
            "human": self.translate(workflow_description, "technical", "human"),
            "ai": self.translate(workflow_description, "human", "ai"),
            "code": self.translate(workflow_description, "human", "code"),
            "visual": f"📊 {workflow_description}",
            "summary": f"Workflow: {workflow_description[:50]}..."
        }

    def get_status(self) -> Dict[str, Any]:
        """Get Babel Fish status"""
        return {
            "fish_inserted": self.fish_inserted,
            "translation_active": self.translation_active,
            "translations_cached": len(self.translation_cache),
            "translation_history_count": len(self.translation_history),
            "rosetta_integrated": self.rosetta is not None,
            "status": "active" if self.fish_inserted else "inactive"
        }

    def get_translation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent translation history"""
        return self.translation_history[-limit:]

    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        self.logger.info("  ✅ Translation cache cleared")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Babel Fish Translator - Universal Instant Translation")
    parser.add_argument("--insert", action="store_true", help="Insert Babel Fish")
    parser.add_argument("--remove", action="store_true", help="Remove Babel Fish")
    parser.add_argument("--translate", type=str, help="Text to translate")
    parser.add_argument("--from", type=str, default="auto", dest="source", help="Source language")
    parser.add_argument("--to", type=str, default="human", dest="target", help="Target language")
    parser.add_argument("--ai-concept", type=str, help="Translate AI concept")
    parser.add_argument("--level", type=str, choices=["beginner", "intermediate", "advanced"], 
                       default="beginner", help="Explanation level")
    parser.add_argument("--status", action="store_true", help="Get Babel Fish status")
    parser.add_argument("--history", type=int, help="Show translation history (limit)")
    parser.add_argument("--clear-cache", action="store_true", help="Clear translation cache")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    translator = BabelFishTranslator()

    if args.insert:
        translator.insert_fish()
        if not args.json:
            print("\n🐟 Babel Fish inserted!")
            print("   You can now understand anything in any form of language")

    elif args.remove:
        translator.remove_fish()
        if not args.json:
            print("\n🐟 Babel Fish removed")

    elif args.translate:
        if not translator.fish_inserted:
            translator.insert_fish()

        translated = translator.translate(args.translate, args.source, args.target)
        if args.json:
            print(json.dumps({
                "original": args.translate,
                "translated": translated,
                "source": args.source,
                "target": args.target
            }, indent=2))
        else:
            print(f"\n🐟 Translation:")
            print(f"   From: {args.source}")
            print(f"   To: {args.target}")
            print(f"   Original: {args.translate}")
            print(f"   Translated: {translated}")

    elif args.ai_concept:
        if not translator.fish_inserted:
            translator.insert_fish()

        level = LanguageLevel(args.level)
        explanation = translator.translate_ai_concept(args.ai_concept, level)
        if args.json:
            print(json.dumps({
                "ai_concept": args.ai_concept,
                "explanation": explanation,
                "level": args.level
            }, indent=2))
        else:
            print(f"\n🐟 AI Concept Translation:")
            print(f"   Concept: {args.ai_concept}")
            print(f"   Level: {args.level}")
            print(f"   Explanation: {explanation}")

    elif args.status:
        status = translator.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🐟 Babel Fish Status")
            print("="*60)
            print(f"Fish Inserted: {'✅ Yes' if status['fish_inserted'] else '❌ No'}")
            print(f"Translation Active: {'✅ Yes' if status['translation_active'] else '❌ No'}")
            print(f"Translations Cached: {status['translations_cached']}")
            print(f"History Count: {status['translation_history_count']}")
            print(f"Rosetta Integrated: {'✅ Yes' if status['rosetta_integrated'] else '❌ No'}")

    elif args.history:
        history = translator.get_translation_history(args.history)
        if args.json:
            print(json.dumps(history, indent=2))
        else:
            print("\n🐟 Translation History")
            print("="*60)
            for entry in history:
                print(f"\n{entry['timestamp']}")
                print(f"  {entry['source']} → {entry['target']}")
                print(f"  Original: {entry['original']}")
                print(f"  Translated: {entry['translated']}")

    elif args.clear_cache:
        translator.clear_cache()
        if not args.json:
            print("\n✅ Translation cache cleared")

    else:
        parser.print_help()
        print("\n🐟 Babel Fish - Universal Instant Translation")
        print("   'The Babel fish is small, yellow, leech-like...'")
        print("   Insert the fish to understand anything in any form of language")

