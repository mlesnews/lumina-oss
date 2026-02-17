#!/usr/bin/env python3
"""
JARVIS Card Catalog - Working Titles
Library-style card catalog system for tracking and updating working titles

@JARVIS @CARD_CATALOG @WORKING_TITLES @DEWEY @LIBRARY
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCardCatalog")


class CardCatalogWorkingTitles:
    """
    Card Catalog System for Working Titles

    Library-style card catalog for tracking and updating working titles
    with Dewey Decimal System-style organization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize card catalog system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Card catalog directory
        self.catalog_dir = self.project_root / "data" / "card_catalog"
        self.catalog_dir.mkdir(parents=True, exist_ok=True)

        # Working titles catalog file
        self.working_titles_file = self.catalog_dir / "working_titles.json"

        # Load existing catalog
        self.catalog = self._load_catalog()

        logger.info("✅ Card Catalog System initialized")
        logger.info("   Library-style working titles tracking")

    def _load_catalog(self) -> Dict[str, Any]:
        """Load card catalog from file"""
        if self.working_titles_file.exists():
            try:
                with open(self.working_titles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load catalog: {e}")

        return {
            "catalog_id": f"catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "cards": [],
            "metadata": {
                "total_cards": 0,
                "categories": {}
            }
        }

    def _save_catalog(self) -> None:
        """Save card catalog to file"""
        try:
            self.catalog["last_updated"] = datetime.now().isoformat()
            self.catalog["metadata"]["total_cards"] = len(self.catalog["cards"])

            with open(self.working_titles_file, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, indent=2, default=str)
            logger.info(f"✅ Catalog saved: {self.working_titles_file}")
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")

    def add_working_title(
        self,
        title: str,
        category: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dewey_number: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a working title to the card catalog"""
        logger.info("=" * 70)
        logger.info("📇 ADDING WORKING TITLE TO CARD CATALOG")
        logger.info("=" * 70)
        logger.info("")

        # Generate Dewey number if not provided
        if not dewey_number:
            dewey_number = self._generate_dewey_number(category)

        card_id = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        card = {
            "card_id": card_id,
            "dewey_number": dewey_number,
            "title": title,
            "category": category,
            "description": description or "",
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "metadata": metadata or {}
        }

        # Add to catalog
        self.catalog["cards"].append(card)

        # Update category count
        if category not in self.catalog["metadata"]["categories"]:
            self.catalog["metadata"]["categories"][category] = 0
        self.catalog["metadata"]["categories"][category] += 1

        # Save catalog
        self._save_catalog()

        logger.info(f"Card ID: {card_id}")
        logger.info(f"Dewey Number: {dewey_number}")
        logger.info(f"Title: {title}")
        logger.info(f"Category: {category}")
        logger.info(f"Tags: {', '.join(card['tags']) if card['tags'] else 'None'}")
        logger.info(f"Total Cards: {len(self.catalog['cards'])}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ WORKING TITLE ADDED TO CARD CATALOG")
        logger.info("=" * 70)

        return {
            "success": True,
            "card": card,
            "total_cards": len(self.catalog["cards"])
        }

    def update_working_title(
        self,
        card_id: Optional[str] = None,
        title: Optional[str] = None,
        new_title: Optional[str] = None,
        **updates
    ) -> Dict[str, Any]:
        """Update a working title in the card catalog"""
        logger.info("=" * 70)
        logger.info("📝 UPDATING WORKING TITLE IN CARD CATALOG")
        logger.info("=" * 70)
        logger.info("")

        # Find card by ID or title
        card = None
        card_index = None

        if card_id:
            for i, c in enumerate(self.catalog["cards"]):
                if c["card_id"] == card_id:
                    card = c
                    card_index = i
                    break
        elif title:
            for i, c in enumerate(self.catalog["cards"]):
                if c["title"] == title:
                    card = c
                    card_index = i
                    break

        if not card:
            logger.warning(f"⚠️  Card not found: {card_id or title}")
            return {"success": False, "message": "Card not found"}

        # Update card
        if new_title:
            card["title"] = new_title

        for key, value in updates.items():
            if key in card:
                card["title"] = value if key == "title" else card.get(key, value)
                card[key] = value

        card["last_updated"] = datetime.now().isoformat()

        # Update in catalog
        self.catalog["cards"][card_index] = card

        # Save catalog
        self._save_catalog()

        logger.info(f"Card ID: {card['card_id']}")
        logger.info(f"Title: {card['title']}")
        logger.info(f"Updated: {card['last_updated']}")
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ WORKING TITLE UPDATED")
        logger.info("=" * 70)

        return {
            "success": True,
            "card": card
        }

    def _generate_dewey_number(self, category: str) -> str:
        """Generate Dewey Decimal System number for category"""
        # Simple Dewey mapping
        dewey_map = {
            "technology": "000",
            "computer_science": "004",
            "software": "005",
            "artificial_intelligence": "006",
            "business": "650",
            "finance": "332",
            "marketing": "658",
            "science": "500",
            "mathematics": "510",
            "engineering": "620",
            "general": "000"
        }

        base_number = dewey_map.get(category.lower(), "000")

        # Add sequence number based on existing cards in category
        category_cards = [c for c in self.catalog["cards"] if c.get("category", "").lower() == category.lower()]
        sequence = len(category_cards) + 1

        return f"{base_number}.{sequence:03d}"

    def list_all_titles(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all working titles, optionally filtered by category"""
        if category:
            return [card for card in self.catalog["cards"] if card.get("category", "").lower() == category.lower()]
        return self.catalog["cards"]

    def search_titles(self, query: str) -> List[Dict[str, Any]]:
        """Search working titles by query"""
        query_lower = query.lower()
        results = []

        for card in self.catalog["cards"]:
            if (query_lower in card.get("title", "").lower() or
                query_lower in card.get("description", "").lower() or
                any(query_lower in tag.lower() for tag in card.get("tags", []))):
                results.append(card)

        return results

    def get_catalog_summary(self) -> Dict[str, Any]:
        """Get catalog summary"""
        return {
            "total_cards": len(self.catalog["cards"]),
            "categories": self.catalog["metadata"]["categories"],
            "last_updated": self.catalog["last_updated"],
            "catalog_id": self.catalog["catalog_id"]
        }


def main():
    """Main execution"""
    print("=" * 70)
    print("📇 CARD CATALOG - WORKING TITLES")
    print("   Library-style title tracking")
    print("=" * 70)
    print()

    catalog = CardCatalogWorkingTitles()

    # Add some example working titles
    print("Adding example working titles...")
    print()

    catalog.add_working_title(
        title="RoamWise.ai Stargate Portal",
        category="technology",
        description="Stargate-inspired web portal/gateway for RoamWise.ai",
        tags=["@roamwise", "@stargate", "@portal", "@gateway"]
    )

    catalog.add_working_title(
        title="Financial Premium Package",
        category="finance",
        description="Premium financial life domain coaching package",
        tags=["@financial", "@premium", "@addon"]
    )

    catalog.add_working_title(
        title="CIAB - Company/Business in a Box",
        category="business",
        description="Complete hardware + software deployment package",
        tags=["@ciab", "@deployment", "@asus", "@laptop"]
    )

    # Get summary
    summary = catalog.get_catalog_summary()

    print()
    print("=" * 70)
    print("📊 CATALOG SUMMARY")
    print("=" * 70)
    print(f"Total Cards: {summary['total_cards']}")
    print(f"Categories: {len(summary['categories'])}")
    print(f"Last Updated: {summary['last_updated']}")
    print("=" * 70)

    # List all titles
    print()
    print("=" * 70)
    print("📇 ALL WORKING TITLES")
    print("=" * 70)
    for card in catalog.list_all_titles():
        print(f"  [{card['dewey_number']}] {card['title']}")
        print(f"      Category: {card['category']}")
        print(f"      Tags: {', '.join(card['tags']) if card['tags'] else 'None'}")
        print()
    print("=" * 70)


if __name__ == "__main__":


    main()