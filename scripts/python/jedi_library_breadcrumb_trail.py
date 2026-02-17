#!/usr/bin/env python3
"""
Jedi Library Breadcrumb Trail System

Creates breadcrumb trails to holocrons in the Jedi Library/Temple.
Integrates with Cursor Docs for @Add references.

Tags: #BREADCRUMB #TRAIL #HOLOCRONS #JEDI_LIBRARY #TEMPLE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JediLibraryBreadcrumb")


@dataclass
class Breadcrumb:
    """Single breadcrumb in the trail"""
    label: str
    path: str
    holocron_id: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class BreadcrumbTrail:
    """Complete breadcrumb trail to a holocron"""
    trail_id: str
    destination: str  # Holocron path
    breadcrumbs: List[Breadcrumb]
    holocron_id: str
    category: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class HolocronReference:
    """Reference to a holocron for Cursor Docs"""
    holocron_id: str
    title: str
    path: str
    category: str
    breadcrumb_trail: List[str]
    cursor_doc_path: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class JediLibraryBreadcrumbSystem:
    """Breadcrumb trail system for Jedi Library/Temple holocrons"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.holocron_index = project_root / "data" / "holocron" / "HOLOCRON_INDEX.json"
        self.breadcrumb_index = project_root / "data" / "holocron" / "BREADCRUMB_TRAILS.json"
        self.cursor_docs_dir = project_root / ".cursor" / "docs"
        self.cursor_docs_dir.mkdir(parents=True, exist_ok=True)

    def load_holocron_index(self) -> Dict[str, Any]:
        """Load holocron index"""
        if self.holocron_index.exists():
            try:
                with open(self.holocron_index, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading holocron index: {e}")
        return {}

    def create_breadcrumb_trail(self, holocron_path: str, category: str = None) -> BreadcrumbTrail:
        try:
            """Create breadcrumb trail to a holocron"""
            # Parse path into breadcrumbs
            path_parts = Path(holocron_path).parts
            breadcrumbs = []

            current_path = ""
            for i, part in enumerate(path_parts):
                current_path = str(Path(current_path) / part) if current_path else part
                breadcrumb = Breadcrumb(
                    label=part.replace('_', ' ').title(),
                    path=current_path,
                    category=category if i == len(path_parts) - 1 else None
                )
                breadcrumbs.append(breadcrumb)

            # Get holocron ID from index
            holocron_id = self._get_holocron_id(holocron_path)

            trail = BreadcrumbTrail(
                trail_id=f"TRAIL-{holocron_id}",
                destination=holocron_path,
                breadcrumbs=breadcrumbs,
                holocron_id=holocron_id,
                category=category or "general"
            )

            return trail

        except Exception as e:
            self.logger.error(f"Error in create_breadcrumb_trail: {e}", exc_info=True)
            raise
    def _get_holocron_id(self, holocron_path: str) -> str:
        try:
            """Get holocron ID from path or index"""
            index = self.load_holocron_index()

            # Search for holocron in index
            for category, entries in index.get("entries", {}).items():
                for entry_id, entry_data in entries.items():
                    if entry_data.get("location") == holocron_path:
                        return entry_data.get("entry_id", "UNKNOWN")

            # Generate ID from path
            path_name = Path(holocron_path).stem
            return f"HOLOCRON-{path_name.upper().replace('-', '-')}"

        except Exception as e:
            self.logger.error(f"Error in _get_holocron_id: {e}", exc_info=True)
            raise
    def create_cursor_doc_reference(self, holocron: HolocronReference) -> Path:
        """Create Cursor Docs reference file for @Add"""
        # Create markdown file for Cursor Docs
        doc_content = f"""# {holocron.title}

**Holocron ID**: {holocron.holocron_id}  
**Category**: {holocron.category}  
**Path**: `{holocron.path}`

## Breadcrumb Trail

```
{' > '.join(holocron.breadcrumb_trail)}
```

## Tags

{', '.join([f'`{tag}`' for tag in holocron.tags])}

## Reference

Use `@Add {holocron.holocron_id}` or `@Add {Path(holocron.path).name}` in Cursor to reference this holocron.

---

*This is an auto-generated reference to a holocron in the Jedi Library/Temple.*
"""

        doc_file = self.cursor_docs_dir / f"{holocron.holocron_id}.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        logger.info(f"✅ Created Cursor Doc: {doc_file}")
        return doc_file

    def generate_all_breadcrumb_trails(self) -> Dict[str, BreadcrumbTrail]:
        """Generate breadcrumb trails for all holocrons"""
        index = self.load_holocron_index()
        trails = {}

        logger.info("🗺️  Generating breadcrumb trails for all holocrons...")

        for category, entries in index.get("entries", {}).items():
            if not isinstance(entries, dict):
                continue
            for entry_id, entry_data in entries.items():
                if not isinstance(entry_data, dict):
                    continue
                holocron_path = entry_data.get("location", "")
                if holocron_path:
                    trail = self.create_breadcrumb_trail(holocron_path, category)
                    trails[trail.trail_id] = trail
                    logger.info(f"   ✅ {trail.trail_id}: {holocron_path}")

        return trails

    def create_jedi_library_index(self) -> Dict[str, Any]:
        try:
            """Create master index of all holocrons with breadcrumb trails"""
            index = self.load_holocron_index()
            trails = self.generate_all_breadcrumb_trails()

            library_index = {
                "jedi_library_metadata": {
                    "name": "Jedi Library / Temple - Master Index",
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "status": "operational",
                    "location": "data/holocron/",
                    "cursor_docs_location": ".cursor/docs/"
                },
                "breadcrumb_system": {
                    "enabled": True,
                    "cursor_integration": True,
                    "reference_format": "@Add {holocron_id}",
                    "total_trails": len(trails)
                },
                "holocrons_by_category": {},
                "breadcrumb_trails": {}
            }

            # Organize by category
            for trail_id, trail in trails.items():
                category = trail.category
                if category not in library_index["holocrons_by_category"]:
                    library_index["holocrons_by_category"][category] = []

                library_index["holocrons_by_category"][category].append({
                    "holocron_id": trail.holocron_id,
                    "title": Path(trail.destination).stem,
                    "path": trail.destination,
                    "trail_id": trail_id,
                    "breadcrumbs": [b.label for b in trail.breadcrumbs]
                })

                library_index["breadcrumb_trails"][trail_id] = {
                    "destination": trail.destination,
                    "holocron_id": trail.holocron_id,
                    "breadcrumbs": [{"label": b.label, "path": b.path} for b in trail.breadcrumbs],
                    "category": trail.category,
                    "tags": trail.tags
                }

            return library_index

        except Exception as e:
            self.logger.error(f"Error in create_jedi_library_index: {e}", exc_info=True)
            raise
    def create_cursor_docs_for_all_holocrons(self) -> List[Path]:
        try:
            """Create Cursor Docs references for all holocrons"""
            index = self.load_holocron_index()
            created_docs = []

            logger.info("📚 Creating Cursor Docs for all holocrons...")

            for category, entries in index.get("entries", {}).items():
                if not isinstance(entries, dict):
                    continue
                for entry_id, entry_data in entries.items():
                    if not isinstance(entry_data, dict):
                        continue
                    holocron_path = entry_data.get("location", "")
                    if not holocron_path:
                        continue

                    # Create breadcrumb trail
                    path_parts = Path(holocron_path).parts
                    breadcrumb_trail = [p.replace('_', ' ').title() for p in path_parts]

                    holocron_ref = HolocronReference(
                        holocron_id=entry_data.get("entry_id", "UNKNOWN"),
                        title=entry_data.get("title", Path(holocron_path).stem),
                        path=holocron_path,
                        category=category,
                        breadcrumb_trail=breadcrumb_trail,
                        tags=entry_data.get("tags", [])
                    )

                    doc_file = self.create_cursor_doc_reference(holocron_ref)
                    created_docs.append(doc_file)

            logger.info(f"✅ Created {len(created_docs)} Cursor Doc references")
            return created_docs

        except Exception as e:
            self.logger.error(f"Error in create_cursor_docs_for_all_holocrons: {e}", exc_info=True)
            raise
    def save_breadcrumb_index(self, library_index: Dict[str, Any]):
        """Save breadcrumb index"""
        with open(self.breadcrumb_index, 'w', encoding='utf-8') as f:
            json.dump(library_index, f, indent=2, default=str)
        logger.info(f"✅ Saved breadcrumb index: {self.breadcrumb_index}")

    def get_breadcrumb_trail(self, holocron_id: str) -> Optional[BreadcrumbTrail]:
        """Get breadcrumb trail for a specific holocron"""
        if not self.breadcrumb_index.exists():
            return None

        try:
            with open(self.breadcrumb_index, 'r', encoding='utf-8') as f:
                index = json.load(f)

            for trail_id, trail_data in index.get("breadcrumb_trails", {}).items():
                if trail_data.get("holocron_id") == holocron_id:
                    breadcrumbs = [
                        Breadcrumb(label=b["label"], path=b["path"])
                        for b in trail_data.get("breadcrumbs", [])
                    ]
                    return BreadcrumbTrail(
                        trail_id=trail_id,
                        destination=trail_data["destination"],
                        breadcrumbs=breadcrumbs,
                        holocron_id=holocron_id,
                        category=trail_data.get("category", "general")
                    )
        except Exception as e:
            logger.error(f"Error loading breadcrumb trail: {e}")

        return None


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Jedi Library Breadcrumb Trail System")
    parser.add_argument("--generate", action="store_true", help="Generate all breadcrumb trails")
    parser.add_argument("--create-docs", action="store_true", help="Create Cursor Docs for all holocrons")
    parser.add_argument("--trail", type=str, metavar="HOLOCRON_ID", help="Get breadcrumb trail for holocron")
    parser.add_argument("--index", action="store_true", help="Create master Jedi Library index")

    args = parser.parse_args()

    system = JediLibraryBreadcrumbSystem(project_root)

    if args.generate:
        trails = system.generate_all_breadcrumb_trails()
        print(f"\n✅ Generated {len(trails)} breadcrumb trails")
        for trail_id, trail in trails.items():
            print(f"   {trail_id}: {' > '.join([b.label for b in trail.breadcrumbs])}")

    elif args.create_docs:
        docs = system.create_cursor_docs_for_all_holocrons()
        print(f"\n✅ Created {len(docs)} Cursor Doc references")
        print(f"   Location: {system.cursor_docs_dir}")
        print("\n💡 Use @Add in Cursor to reference these holocrons!")

    elif args.trail:
        trail = system.get_breadcrumb_trail(args.trail)
        if trail:
            print(f"\n🗺️  Breadcrumb Trail: {trail.trail_id}")
            print(f"   Destination: {trail.destination}")
            print(f"   Trail: {' > '.join([b.label for b in trail.breadcrumbs])}")
        else:
            print(f"❌ Trail not found for: {args.trail}")

    elif args.index:
        library_index = system.create_jedi_library_index()
        system.save_breadcrumb_index(library_index)

        print("\n" + "=" * 80)
        print("📚 JEDI LIBRARY / TEMPLE INDEX")
        print("=" * 80)
        print()
        print(f"Total Holocrons: {sum(len(v) for v in library_index['holocrons_by_category'].values())}")
        print(f"Total Breadcrumb Trails: {library_index['breadcrumb_system']['total_trails']}")
        print()
        print("Categories:")
        for category, holocrons in library_index["holocrons_by_category"].items():
            print(f"   - {category}: {len(holocrons)} holocrons")
        print()
        print(f"✅ Index saved to: {system.breadcrumb_index}")
        print(f"✅ Cursor Docs location: {system.cursor_docs_dir}")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":

    main()