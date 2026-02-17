#!/usr/bin/env python3
"""
JARVIS Force-Sensitive Listings System

Maintains active/live black/white/grey listings representing the three orders:
- Jedi (Light Side, White) - Order, Balance, Harmony
- Sith (Dark Side, Black) - Chaos, Power, Domination
- Gray Jedi (Balance, Grey) - @quant @bal, Chaos & Entropy in balance

@JARVIS @DOIT @QUANT @BAL #FORCE #JEDI #SITH #GRAY #CHAOS #ENTROPY
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import threading
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISForceListings")


class ForceOrder(Enum):
    """The three Force-sensitive orders"""
    JEDI = "jedi"  # Light Side, White, Order, Balance, Harmony
    SITH = "sith"  # Dark Side, Black, Chaos, Power, Domination
    GRAY_JEDI = "gray_jedi"  # Balance, Grey, @quant @bal, Chaos & Entropy


class ListingType(Enum):
    """Types of listings"""
    BLACKLIST = "blacklist"  # Sith - Forbidden, Blocked, Dark
    WHITELIST = "whitelist"  # Jedi - Allowed, Approved, Light
    GREYLIST = "greylist"  # Gray Jedi - Conditional, Balanced, @quant @bal


@dataclass
class ForceListingEntry:
    """Entry in Force-sensitive listing"""
    entry_id: str
    listing_type: ListingType
    force_order: ForceOrder
    value: str
    description: str
    quant_score: float = 0.0  # @quant score
    bal_score: float = 0.0  # @bal score
    chaos_score: float = 0.0  # Chaos metric
    entropy_score: float = 0.0  # Entropy metric
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


class JARVISForceSensitiveListings:
    """
    JARVIS Force-Sensitive Listings System

    Maintains active/live black/white/grey listings representing:
    - Jedi (White/Whitelist): Order, Balance, Harmony
    - Sith (Black/Blacklist): Chaos, Power, Domination
    - Gray Jedi (Grey/Greylist): @quant @bal, Chaos & Entropy in balance
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Data storage
        self.data_dir = project_root / "data" / "jarvis_force_listings"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Active listings
        self.blacklist: Set[str] = set()  # Sith - Forbidden
        self.whitelist: Set[str] = set()  # Jedi - Allowed
        self.greylist: Dict[str, ForceListingEntry] = {}  # Gray Jedi - Conditional

        # Force order mappings
        self.force_order_listings: Dict[ForceOrder, Set[str]] = {
            ForceOrder.JEDI: set(),
            ForceOrder.SITH: set(),
            ForceOrder.GRAY_JEDI: set()
        }

        # Load existing listings
        self._load_listings()

        # Start live update thread
        self.update_active = True
        self.update_thread = threading.Thread(target=self._live_update_loop, daemon=True)
        self.update_thread.start()

        self.logger.info(f"✅ JARVIS Force-Sensitive Listings initialized")
        self.logger.info(f"   Jedi (White): {len(self.whitelist)} entries")
        self.logger.info(f"   Sith (Black): {len(self.blacklist)} entries")
        self.logger.info(f"   Gray Jedi (Grey): {len(self.greylist)} entries")

    def _load_listings(self):
        """Load existing listings from storage"""
        try:
            listings_file = self.data_dir / "force_listings.json"
            if listings_file.exists():
                with open(listings_file, 'r') as f:
                    data = json.load(f)

                # Load blacklist (Sith)
                self.blacklist = set(data.get("blacklist", []))
                self.force_order_listings[ForceOrder.SITH] = self.blacklist.copy()

                # Load whitelist (Jedi)
                self.whitelist = set(data.get("whitelist", []))
                self.force_order_listings[ForceOrder.JEDI] = self.whitelist.copy()

                # Load greylist (Gray Jedi)
                greylist_data = data.get("greylist", {})
                for entry_id, entry_data in greylist_data.items():
                    entry = ForceListingEntry(
                        entry_id=entry_data["entry_id"],
                        listing_type=ListingType.GREYLIST,
                        force_order=ForceOrder.GRAY_JEDI,
                        value=entry_data["value"],
                        description=entry_data["description"],
                        quant_score=entry_data.get("quant_score", 0.0),
                        bal_score=entry_data.get("bal_score", 0.0),
                        chaos_score=entry_data.get("chaos_score", 0.0),
                        entropy_score=entry_data.get("entropy_score", 0.0),
                        metadata=entry_data.get("metadata", {}),
                        timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                        last_updated=datetime.fromisoformat(entry_data.get("last_updated", entry_data["timestamp"]))
                    )
                    self.greylist[entry_id] = entry
                    self.force_order_listings[ForceOrder.GRAY_JEDI].add(entry.value)

                self.logger.info(f"   ✅ Loaded {len(self.blacklist)} Sith entries")
                self.logger.info(f"   ✅ Loaded {len(self.whitelist)} Jedi entries")
                self.logger.info(f"   ✅ Loaded {len(self.greylist)} Gray Jedi entries")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load listings: {e}")

    def _save_listings(self):
        """Save listings to storage"""
        try:
            listings_file = self.data_dir / "force_listings.json"

            data = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "blacklist": list(self.blacklist),  # Sith
                "whitelist": list(self.whitelist),  # Jedi
                "greylist": {
                    entry_id: {
                        "entry_id": entry.entry_id,
                        "value": entry.value,
                        "description": entry.description,
                        "quant_score": entry.quant_score,
                        "bal_score": entry.bal_score,
                        "chaos_score": entry.chaos_score,
                        "entropy_score": entry.entropy_score,
                        "metadata": entry.metadata,
                        "timestamp": entry.timestamp.isoformat(),
                        "last_updated": entry.last_updated.isoformat()
                    }
                    for entry_id, entry in self.greylist.items()
                }
            }

            with open(listings_file, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.debug("✅ Listings saved")
        except Exception as e:
            self.logger.error(f"❌ Failed to save listings: {e}")

    def _calculate_force_scores(self, value: str) -> Dict[str, float]:
        """Calculate @quant, @bal, chaos, and entropy scores"""
        scores = {
            "quant_score": 0.5,  # Default balanced
            "bal_score": 0.5,  # Default balanced
            "chaos_score": 0.5,  # Default balanced
            "entropy_score": 0.5  # Default balanced
        }

        # Calculate entropy score (Shannon entropy)
        try:
            import math
            value_lower = value.lower()
            char_counts = {}
            for char in value_lower:
                char_counts[char] = char_counts.get(char, 0) + 1

            entropy = 0.0
            length = len(value_lower)
            if length > 0:
                for count in char_counts.values():
                    probability = count / length
                    if probability > 0:
                        entropy -= probability * math.log2(probability)
                # Normalize to 0-1
                max_entropy = math.log2(max(len(char_counts), 2))
                scores["entropy_score"] = min(entropy / max_entropy if max_entropy > 0 else 0.5, 1.0)
        except Exception as e:
            self.logger.debug(f"Entropy calculation failed: {e}")

        # Calculate chaos score (variance-based)
        try:
            import random
            import statistics
            samples = [random.random() for _ in range(10)]
            variance = statistics.variance(samples) if len(samples) > 1 else 0.0
            scores["chaos_score"] = min(variance * 10, 1.0)
        except Exception as e:
            self.logger.debug(f"Chaos calculation failed: {e}")

        return scores

    def add_to_blacklist(self, value: str, description: str = "", metadata: Dict[str, Any] = None) -> bool:
        """Add entry to blacklist (Sith - Forbidden, Dark Side)"""
        if value in self.whitelist:
            self.logger.warning(f"⚠️  Cannot blacklist '{value}' - already in whitelist (Jedi)")
            return False

        if value in self.blacklist:
            return True

        self.blacklist.add(value)
        self.force_order_listings[ForceOrder.SITH].add(value)

        # Remove from greylist if present
        self.greylist = {k: v for k, v in self.greylist.items() if v.value != value}
        self.force_order_listings[ForceOrder.GRAY_JEDI].discard(value)

        self._save_listings()
        self.logger.info(f"⚫ Added to blacklist (Sith): {value}")
        return True

    def add_to_whitelist(self, value: str, description: str = "", metadata: Dict[str, Any] = None) -> bool:
        """Add entry to whitelist (Jedi - Allowed, Light Side)"""
        if value in self.blacklist:
            self.logger.warning(f"⚠️  Cannot whitelist '{value}' - already in blacklist (Sith)")
            return False

        if value in self.whitelist:
            return True

        self.whitelist.add(value)
        self.force_order_listings[ForceOrder.JEDI].add(value)

        # Remove from greylist if present
        self.greylist = {k: v for k, v in self.greylist.items() if v.value != value}
        self.force_order_listings[ForceOrder.GRAY_JEDI].discard(value)

        self._save_listings()
        self.logger.info(f"⚪ Added to whitelist (Jedi): {value}")
        return True

    def add_to_greylist(self, value: str, description: str = "", metadata: Dict[str, Any] = None) -> Optional[ForceListingEntry]:
        """Add entry to greylist (Gray Jedi - Conditional, Balanced, @quant @bal)"""
        if value in self.blacklist or value in self.whitelist:
            return None

        existing = next((entry for entry in self.greylist.values() if entry.value == value), None)
        if existing:
            return existing

        scores = self._calculate_force_scores(value)

        entry_id = f"gray_{len(self.greylist) + 1}_{int(time.time())}"
        entry = ForceListingEntry(
            entry_id=entry_id,
            listing_type=ListingType.GREYLIST,
            force_order=ForceOrder.GRAY_JEDI,
            value=value,
            description=description or f"Gray Jedi entry - balanced @quant @bal, chaos & entropy",
            quant_score=scores["quant_score"],
            bal_score=scores["bal_score"],
            chaos_score=scores["chaos_score"],
            entropy_score=scores["entropy_score"],
            metadata=metadata or {}
        )

        self.greylist[entry_id] = entry
        self.force_order_listings[ForceOrder.GRAY_JEDI].add(value)

        self._save_listings()
        self.logger.info(f"⚫⚪ Added to greylist (Gray Jedi): {value}")
        self.logger.info(f"   @quant: {entry.quant_score:.2f}, @bal: {entry.bal_score:.2f}")
        self.logger.info(f"   Chaos: {entry.chaos_score:.2f}, Entropy: {entry.entropy_score:.2f}")

        return entry

    def check_listing(self, value: str) -> Dict[str, Any]:
        """Check which listing a value belongs to"""
        if value in self.blacklist:
            return {
                "listing_type": ListingType.BLACKLIST.value,
                "force_order": ForceOrder.SITH.value,
                "status": "forbidden",
                "description": "Sith - Dark Side, Forbidden"
            }

        if value in self.whitelist:
            return {
                "listing_type": ListingType.WHITELIST.value,
                "force_order": ForceOrder.JEDI.value,
                "status": "allowed",
                "description": "Jedi - Light Side, Allowed"
            }

        entry = next((entry for entry in self.greylist.values() if entry.value == value), None)
        if entry:
            return {
                "listing_type": ListingType.GREYLIST.value,
                "force_order": ForceOrder.GRAY_JEDI.value,
                "status": "conditional",
                "description": entry.description,
                "quant_score": entry.quant_score,
                "bal_score": entry.bal_score,
                "chaos_score": entry.chaos_score,
                "entropy_score": entry.entropy_score
            }

        return {
            "listing_type": None,
            "force_order": None,
            "status": "unlisted",
            "description": "Not in any listing"
        }

    def _live_update_loop(self):
        """Live update loop - recalculates scores for greylist entries"""
        while self.update_active:
            try:
                for entry_id, entry in list(self.greylist.items()):
                    scores = self._calculate_force_scores(entry.value)
                    entry.quant_score = scores["quant_score"]
                    entry.bal_score = scores["bal_score"]
                    entry.chaos_score = scores["chaos_score"]
                    entry.entropy_score = scores["entropy_score"]
                    entry.last_updated = datetime.now()

                if self.greylist:
                    self._save_listings()

                time.sleep(30)
            except Exception as e:
                self.logger.error(f"Live update error: {e}")
                time.sleep(60)

    def get_all_listings(self) -> Dict[str, Any]:
        """Get all listings"""
        return {
            "jedi_whitelist": list(self.whitelist),
            "sith_blacklist": list(self.blacklist),
            "gray_jedi_greylist": [
                {
                    "value": entry.value,
                    "description": entry.description,
                    "quant_score": entry.quant_score,
                    "bal_score": entry.bal_score,
                    "chaos_score": entry.chaos_score,
                    "entropy_score": entry.entropy_score,
                    "last_updated": entry.last_updated.isoformat()
                }
                for entry in self.greylist.values()
            ],
            "statistics": {
                "jedi_count": len(self.whitelist),
                "sith_count": len(self.blacklist),
                "gray_jedi_count": len(self.greylist),
                "total": len(self.whitelist) + len(self.blacklist) + len(self.greylist)
            }
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Force-Sensitive Listings")
    parser.add_argument("--list", action="store_true", help="List all entries")
    parser.add_argument("--add-black", type=str, help="Add to blacklist (Sith)")
    parser.add_argument("--add-white", type=str, help="Add to whitelist (Jedi)")
    parser.add_argument("--add-gray", type=str, help="Add to greylist (Gray Jedi)")
    parser.add_argument("--check", type=str, help="Check which listing a value belongs to")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    listings = JARVISForceSensitiveListings(project_root)

    if args.list:
        all_listings = listings.get_all_listings()
        print("\n" + "="*80)
        print("JARVIS FORCE-SENSITIVE LISTINGS")
        print("="*80)
        print(f"\n⚪ JEDI (Whitelist): {all_listings['statistics']['jedi_count']} entries")
        for entry in all_listings['jedi_whitelist'][:10]:
            print(f"   - {entry}")
        if len(all_listings['jedi_whitelist']) > 10:
            print(f"   ... and {len(all_listings['jedi_whitelist']) - 10} more")

        print(f"\n⚫ SITH (Blacklist): {all_listings['statistics']['sith_count']} entries")
        for entry in all_listings['sith_blacklist'][:10]:
            print(f"   - {entry}")
        if len(all_listings['sith_blacklist']) > 10:
            print(f"   ... and {len(all_listings['sith_blacklist']) - 10} more")

        print(f"\n⚫⚪ GRAY JEDI (Greylist): {all_listings['statistics']['gray_jedi_count']} entries")
        for entry in all_listings['gray_jedi_greylist'][:10]:
            print(f"   - {entry['value']}")
            print(f"     @quant: {entry['quant_score']:.2f}, @bal: {entry['bal_score']:.2f}")
            print(f"     Chaos: {entry['chaos_score']:.2f}, Entropy: {entry['entropy_score']:.2f}")
        if len(all_listings['gray_jedi_greylist']) > 10:
            print(f"   ... and {len(all_listings['gray_jedi_greylist']) - 10} more")

        print("="*80)

    if args.add_black:
        listings.add_to_blacklist(args.add_black, "Sith - Dark Side entry")
        print(f"⚫ Added to blacklist (Sith): {args.add_black}")

    if args.add_white:
        listings.add_to_whitelist(args.add_white, "Jedi - Light Side entry")
        print(f"⚪ Added to whitelist (Jedi): {args.add_white}")

    if args.add_gray:
        entry = listings.add_to_greylist(args.add_gray, "Gray Jedi - Balanced entry")
        if entry:
            print(f"⚫⚪ Added to greylist (Gray Jedi): {args.add_gray}")
            print(f"   @quant: {entry.quant_score:.2f}, @bal: {entry.bal_score:.2f}")
            print(f"   Chaos: {entry.chaos_score:.2f}, Entropy: {entry.entropy_score:.2f}")

    if args.check:
        result = listings.check_listing(args.check)
        print(f"\n{args.check}:")
        print(f"   Listing: {result['listing_type']}")
        print(f"   Force Order: {result['force_order']}")
        print(f"   Status: {result['status']}")
        print(f"   Description: {result['description']}")
        if 'quant_score' in result:
            print(f"   @quant: {result['quant_score']:.2f}, @bal: {result['bal_score']:.2f}")
            print(f"   Chaos: {result['chaos_score']:.2f}, Entropy: {result['entropy_score']:.2f}")

    if args.stats:
        stats = listings.get_all_listings()['statistics']
        print("\n" + "="*80)
        print("FORCE-SENSITIVE LISTINGS STATISTICS")
        print("="*80)
        print(f"⚪ Jedi (Whitelist): {stats['jedi_count']}")
        print(f"⚫ Sith (Blacklist): {stats['sith_count']}")
        print(f"⚫⚪ Gray Jedi (Greylist): {stats['gray_jedi_count']}")
        print(f"Total: {stats['total']}")
        print("="*80)

    if not any([args.list, args.add_black, args.add_white, args.add_gray, args.check, args.stats]):
        parser.print_help()


if __name__ == "__main__":


    main()