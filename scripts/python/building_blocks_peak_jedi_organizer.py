#!/usr/bin/env python3
"""
@BASIC @BUILDINGBLOCKS + @PEAK + @JEDIARCHIVE Unified Organizer

Determines @BASIC @BUILDINGBLOCKS of @OP @INTENT (operational intent),
utilizes @PEAK patterns, and organizes everything through:
- Jedi Archives (@JEDIARCHIVE)
- Head Jedi Librarian Jocasta Nu (@JOCOSTA-NU)
- Card Catalog-Dewey-Decimal System

This system creates a unified knowledge organization pipeline:
1. Extract @BASIC @BUILDINGBLOCKS from operational intent
2. Identify and utilize @PEAK patterns
3. Classify and organize via Dewey Decimal
4. Catalog in Jedi Archives with Jocasta Nu
5. Make searchable via Card Catalog

Tags: #BUILDINGBLOCKS #PEAK #JEDIARCHIVE #JOCOSTA-NU #DEWEY #CATALOG @JARVIS @TEAM
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BuildingBlocksPeakJediOrganizer")

# Peak Pattern System
try:
    from peak_pattern_system import PeakPatternSystem, PatternType
    PEAK_PATTERNS_AVAILABLE = True
except ImportError:
    PEAK_PATTERNS_AVAILABLE = False
    PeakPatternSystem = None
    PatternType = None

# Jedi Librarian System
try:
    from jedi_librarian_system import JediLibrarian
    JEDI_LIBRARIAN_AVAILABLE = True
except ImportError:
    JEDI_LIBRARIAN_AVAILABLE = False
    JediLibrarian = None

# Jedi Archives Organizer
try:
    from jedi_archives_organizer import JediArchivesOrganizer
    JEDI_ARCHIVES_AVAILABLE = True
except ImportError:
    JEDI_ARCHIVES_AVAILABLE = False
    JediArchivesOrganizer = None

# SYPHON integration
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None


class BuildingBlockType(Enum):
    """Types of @BASIC @BUILDINGBLOCKS"""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    PATTERN = "pattern"
    CONFIG = "config"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    DATA_STRUCTURE = "data_structure"
    API = "api"
    UTILITY = "utility"


class OperationalIntent(Enum):
    """Types of @OP @INTENT (operational intent)"""
    AUTOMATION = "automation"
    INTELLIGENCE = "intelligence"
    COORDINATION = "coordination"
    EXTRACTION = "extraction"
    ORGANIZATION = "organization"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    INTEGRATION = "integration"


@dataclass
class BuildingBlock:
    """A @BASIC @BUILDINGBLOCK extracted from operational intent"""
    block_id: str
    block_type: BuildingBlockType
    name: str
    description: str
    operational_intent: OperationalIntent
    code_snippet: str = ""
    dependencies: List[str] = field(default_factory=list)
    peak_patterns: List[str] = field(default_factory=list)
    dewey_classification: str = ""
    location: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['block_type'] = self.block_type.value
        data['operational_intent'] = self.operational_intent.value
        data['extracted_at'] = self.extracted_at.isoformat()
        return data


@dataclass
class CatalogEntry:
    """A Card Catalog entry in the Jedi Archives"""
    entry_id: str
    title: str
    dewey_classification: str
    building_blocks: List[str] = field(default_factory=list)
    peak_patterns: List[str] = field(default_factory=list)
    operational_intent: List[str] = field(default_factory=list)
    location: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cataloged_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['cataloged_at'] = self.cataloged_at.isoformat()
        return data


class BuildingBlocksPeakJediOrganizer:
    """
    Unified Organizer: @BASIC @BUILDINGBLOCKS + @PEAK + @JEDIARCHIVE

    Determines building blocks from operational intent, utilizes @PEAK patterns,
    and organizes everything through Jedi Archives with Jocasta Nu.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified organizer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.building_blocks_dir = self.data_dir / "building_blocks"
        self.building_blocks_dir.mkdir(parents=True, exist_ok=True)

        # Peak Pattern System
        self.peak_system = None
        if PEAK_PATTERNS_AVAILABLE:
            try:
                self.peak_system = PeakPatternSystem(project_root=self.project_root)
                logger.info("✅ @PEAK Pattern System initialized")
            except Exception as e:
                logger.warning(f"⚠️  @PEAK Pattern System not available: {e}")

        # Jedi Librarian (Jocasta Nu)
        self.librarian = None
        if JEDI_LIBRARIAN_AVAILABLE:
            try:
                self.librarian = JediLibrarian(project_root=self.project_root)
                logger.info("✅ Jedi Librarian (Jocasta Nu) initialized")
            except Exception as e:
                logger.warning(f"⚠️  Jedi Librarian not available: {e}")

        # Jedi Archives Organizer
        self.archives_organizer = None
        if JEDI_ARCHIVES_AVAILABLE:
            try:
                self.archives_organizer = JediArchivesOrganizer(project_root=self.project_root)
                logger.info("✅ Jedi Archives Organizer initialized")
            except Exception as e:
                logger.warning(f"⚠️  Jedi Archives Organizer not available: {e}")

        # SYPHON integration
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=self.project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        # Building blocks registry
        self.building_blocks_registry: Dict[str, BuildingBlock] = {}
        self.catalog_entries: Dict[str, CatalogEntry] = {}

        logger.info("✅ Building Blocks + @PEAK + Jedi Archive Organizer initialized")

    def extract_building_blocks_from_intent(self, 
                                           intent_text: str,
                                           operational_intent: OperationalIntent) -> List[BuildingBlock]:
        """
        Extract @BASIC @BUILDINGBLOCKS from operational intent

        Analyzes intent text to identify fundamental building blocks
        """
        logger.info(f"🔍 Extracting building blocks from {operational_intent.value} intent...")

        building_blocks = []

        # Extract functions
        function_pattern = r'def\s+(\w+)\s*\([^)]*\)\s*:'
        functions = re.findall(function_pattern, intent_text)
        for func_name in functions:
            block = BuildingBlock(
                block_id=f"func_{func_name}",
                block_type=BuildingBlockType.FUNCTION,
                name=func_name,
                description=f"Function extracted from {operational_intent.value} intent",
                operational_intent=operational_intent,
                code_snippet=self._extract_code_snippet(intent_text, func_name, "function"),
                metadata={"source": "intent_extraction"}
            )
            building_blocks.append(block)

        # Extract classes
        class_pattern = r'class\s+(\w+)\s*(?:\([^)]*\))?\s*:'
        classes = re.findall(class_pattern, intent_text)
        for class_name in classes:
            block = BuildingBlock(
                block_id=f"class_{class_name}",
                block_type=BuildingBlockType.CLASS,
                name=class_name,
                description=f"Class extracted from {operational_intent.value} intent",
                operational_intent=operational_intent,
                code_snippet=self._extract_code_snippet(intent_text, class_name, "class"),
                metadata={"source": "intent_extraction"}
            )
            building_blocks.append(block)

        # Extract patterns (using @PEAK)
        if self.peak_system:
            try:
                peak_patterns = self.peak_system.extract_patterns_from_code(intent_text)
                for pattern in peak_patterns:
                    block = BuildingBlock(
                        block_id=f"pattern_{pattern.pattern_id}",
                        block_type=BuildingBlockType.PATTERN,
                        name=pattern.name,
                        description=pattern.description,
                        operational_intent=operational_intent,
                        peak_patterns=[pattern.pattern_id],
                        metadata={"pattern_data": pattern.to_dict()}
                    )
                    building_blocks.append(block)
            except Exception as e:
                logger.debug(f"Could not extract @PEAK patterns: {e}")

        # Extract workflows
        workflow_keywords = ['workflow', 'process', 'pipeline', 'orchestration']
        for keyword in workflow_keywords:
            if keyword in intent_text.lower():
                block = BuildingBlock(
                    block_id=f"workflow_{keyword}",
                    block_type=BuildingBlockType.WORKFLOW,
                    name=f"{keyword.title()} Workflow",
                    description=f"Workflow identified from {operational_intent.value} intent",
                    operational_intent=operational_intent,
                    metadata={"keyword": keyword}
                )
                building_blocks.append(block)

        logger.info(f"✅ Extracted {len(building_blocks)} building blocks")
        return building_blocks

    def identify_peak_patterns(self, building_blocks: List[BuildingBlock]) -> List[BuildingBlock]:
        """
        Identify and link @PEAK patterns to building blocks
        """
        if not self.peak_system:
            return building_blocks

        logger.info("🔍 Identifying @PEAK patterns for building blocks...")

        for block in building_blocks:
            # Search for matching @PEAK patterns
            try:
                # Try to extract patterns from code snippet
                if block.code_snippet:
                    matching_patterns = self.peak_system.extract_patterns_from_code(block.code_snippet)
                    if matching_patterns:
                        block.peak_patterns = [p.pattern_id for p in matching_patterns]
                        logger.debug(f"  ✅ Linked {len(matching_patterns)} @PEAK patterns to {block.name}")

                # Also search existing patterns for matches
                search_text = (block.code_snippet or block.description).lower()
                for pattern_id, pattern in self.peak_system.patterns.items():
                    if any(tag in search_text for tag in pattern.tags):
                        if pattern_id not in block.peak_patterns:
                            block.peak_patterns.append(pattern_id)
            except Exception as e:
                logger.debug(f"Could not identify @PEAK patterns for {block.name}: {e}")

        return building_blocks

    def classify_with_dewey(self, building_blocks: List[BuildingBlock]) -> List[BuildingBlock]:
        """
        Classify building blocks using Dewey Decimal System via Jocasta Nu
        """
        if not self.librarian:
            return building_blocks

        logger.info("📚 Classifying building blocks with Dewey Decimal System...")

        # Map operational intent to Dewey categories
        intent_to_dewey = {
            OperationalIntent.AUTOMATION: ("technology", "1"),
            OperationalIntent.INTELLIGENCE: ("computer_science", "5"),
            OperationalIntent.COORDINATION: ("computer_science", "3"),
            OperationalIntent.EXTRACTION: ("computer_science", "4"),
            OperationalIntent.ORGANIZATION: ("computer_science", "2"),
            OperationalIntent.OPTIMIZATION: ("technology", "2"),
            OperationalIntent.SECURITY: ("technology", "3"),
            OperationalIntent.MONITORING: ("technology", "4"),
            OperationalIntent.ANALYSIS: ("computer_science", "6"),
            OperationalIntent.INTEGRATION: ("technology", "5")
        }

        for block in building_blocks:
            category, sub = intent_to_dewey.get(
                block.operational_intent,
                ("computer_science", "0")
            )

            dewey = self.librarian.classify_artifact(category, sub)
            block.dewey_classification = dewey

            logger.debug(f"  ✅ Classified {block.name} as {dewey}")

        return building_blocks

    def catalog_in_jedi_archives(self, building_blocks: List[BuildingBlock]) -> List[CatalogEntry]:
        """
        Catalog building blocks in Jedi Archives via Jocasta Nu
        """
        logger.info("🏛️  Cataloging building blocks in Jedi Archives...")

        catalog_entries = []

        # Group building blocks by operational intent
        blocks_by_intent: Dict[OperationalIntent, List[BuildingBlock]] = {}
        for block in building_blocks:
            if block.operational_intent not in blocks_by_intent:
                blocks_by_intent[block.operational_intent] = []
            blocks_by_intent[block.operational_intent].append(block)

        # Create catalog entries
        for intent, blocks in blocks_by_intent.items():
            # Get Dewey classification
            dewey = blocks[0].dewey_classification if blocks else ""

            entry = CatalogEntry(
                entry_id=f"CAT-{intent.value.upper()}-{datetime.now().strftime('%Y%m%d')}",
                title=f"{intent.value.title()} Building Blocks",
                dewey_classification=dewey,
                building_blocks=[b.block_id for b in blocks],
                peak_patterns=[p for b in blocks for p in b.peak_patterns],
                operational_intent=[intent.value],
                tags=[intent.value, "building_blocks", "@peak", "@jediarchive"],
                metadata={
                    "total_blocks": len(blocks),
                    "block_types": list(set([b.block_type.value for b in blocks]))
                }
            )

            catalog_entries.append(entry)
            self.catalog_entries[entry.entry_id] = entry

            logger.info(f"  ✅ Cataloged {len(blocks)} blocks for {intent.value}")

        return catalog_entries

    def save_building_blocks_registry(self) -> Path:
        try:
            """Save building blocks registry to file"""
            registry_file = self.building_blocks_dir / "building_blocks_registry.json"

            registry_data = {
                "version": "1.0.0",
                "name": "@BASIC @BUILDINGBLOCKS Registry",
                "description": "Registry of all building blocks extracted from operational intent",
                "last_updated": datetime.now().isoformat(),
                "total_blocks": len(self.building_blocks_registry),
                "building_blocks": {
                    block_id: block.to_dict()
                    for block_id, block in self.building_blocks_registry.items()
                }
            }

            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"✅ Building blocks registry saved: {registry_file}")
            return registry_file

        except Exception as e:
            self.logger.error(f"Error in save_building_blocks_registry: {e}", exc_info=True)
            raise
    def save_catalog_entries(self) -> Path:
        try:
            """Save catalog entries to Jedi Archives"""
            if not self.librarian:
                logger.warning("Jedi Librarian not available")
                return None

            catalog_file = self.project_root / "data" / "holocron" / "BUILDING_BLOCKS_CATALOG.json"
            catalog_file.parent.mkdir(parents=True, exist_ok=True)

            catalog_data = {
                "version": "1.0.0",
                "name": "Building Blocks Card Catalog",
                "description": "Card catalog of building blocks organized by Jocasta Nu",
                "last_updated": datetime.now().isoformat(),
                "total_entries": len(self.catalog_entries),
                "entries": {
                    entry_id: entry.to_dict()
                    for entry_id, entry in self.catalog_entries.items()
                }
            }

            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog_data, f, indent=2, ensure_ascii=False, default=str)

            # Update HOLOCRON_INDEX.json
            self._update_holocron_index(catalog_file)

            logger.info(f"✅ Catalog entries saved: {catalog_file}")
            return catalog_file

        except Exception as e:
            self.logger.error(f"Error in save_catalog_entries: {e}", exc_info=True)
            raise
    def _update_holocron_index(self, catalog_file: Path):
        try:
            """Update HOLOCRON_INDEX.json with catalog entries"""
            index_file = self.project_root / "data" / "holocron" / "HOLOCRON_INDEX.json"

            if not index_file.exists():
                index_data = {"entries": {}}
            else:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)

            if "entries" not in index_data:
                index_data["entries"] = {}

            # Add catalog entries to index
            for entry_id, entry in self.catalog_entries.items():
                index_data["entries"][entry_id] = {
                    "title": entry.title,
                    "location": str(catalog_file.relative_to(self.project_root)),
                    "classification": entry.dewey_classification,
                    "tags": entry.tags,
                    "last_updated": entry.cataloged_at.isoformat(),
                    "type": "building_blocks_catalog"
                }

            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"✅ Updated HOLOCRON_INDEX.json with {len(self.catalog_entries)} entries")

        except Exception as e:
            self.logger.error(f"Error in _update_holocron_index: {e}", exc_info=True)
            raise
    def _extract_code_snippet(self, text: str, name: str, type: str) -> str:
        """Extract code snippet for a function or class"""
        if type == "function":
            pattern = rf'def\s+{name}\s*\([^)]*\)\s*:.*?(?=\n\s*(?:def|class|\Z))'
        elif type == "class":
            pattern = rf'class\s+{name}\s*(?:\([^)]*\))?\s*:.*?(?=\n\s*(?:class|def|\Z))'
        else:
            return ""

        match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
        return match.group(0) if match else ""

    def process_operational_intent(self, 
                                  intent_text: str,
                                  operational_intent: OperationalIntent) -> Dict[str, Any]:
        """
        Complete pipeline: Extract building blocks → Identify @PEAK → Classify → Catalog

        This is the main method that orchestrates the entire process.
        """
        logger.info(f"🚀 Processing {operational_intent.value} operational intent...")

        # Step 1: Extract building blocks
        building_blocks = self.extract_building_blocks_from_intent(intent_text, operational_intent)

        # Step 2: Identify @PEAK patterns
        building_blocks = self.identify_peak_patterns(building_blocks)

        # Step 3: Classify with Dewey Decimal
        building_blocks = self.classify_with_dewey(building_blocks)

        # Step 4: Register building blocks
        for block in building_blocks:
            self.building_blocks_registry[block.block_id] = block

        # Step 5: Catalog in Jedi Archives
        catalog_entries = self.catalog_in_jedi_archives(building_blocks)

        # Step 6: Save everything
        registry_file = self.save_building_blocks_registry()
        catalog_file = self.save_catalog_entries()

        return {
            "building_blocks": [b.to_dict() for b in building_blocks],
            "catalog_entries": [e.to_dict() for e in catalog_entries],
            "registry_file": str(registry_file),
            "catalog_file": str(catalog_file) if catalog_file else None,
            "total_blocks": len(building_blocks),
            "total_catalog_entries": len(catalog_entries)
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("@BASIC @BUILDINGBLOCKS + @PEAK + @JEDIARCHIVE Unified Organizer")
    print("="*80 + "\n")

    organizer = BuildingBlocksPeakJediOrganizer()

    # Example: Process an operational intent
    example_intent = """
    def extract_intelligence(self, source: str) -> Dict[str, Any]:
        \"\"\"Extract intelligence from source\"\"\"
        # @PEAK: Use SYPHON for extraction
        result = self.syphon.extract(source)
        return result

    class IntelligenceProcessor:
        \"\"\"Process extracted intelligence\"\"\"
        def __init__(self):
            self.processor = IntelligenceProcessor()
    """

    result = organizer.process_operational_intent(
        example_intent,
        OperationalIntent.INTELLIGENCE
    )

    print(f"✅ Processed {result['total_blocks']} building blocks")
    print(f"✅ Created {result['total_catalog_entries']} catalog entries")
    print(f"📚 Registry: {result['registry_file']}")
    if result['catalog_file']:
        print(f"🏛️  Catalog: {result['catalog_file']}")

    print("\n✅ Unified Organizer Test Complete")
    print("="*80 + "\n")
