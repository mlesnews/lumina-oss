#!/usr/bin/env python3
"""
L.A.F.F. - Produce Content from Ingestion Aggregations & Collations

Produce content (books, docuseries) from all ingested/aggregated/collated data:
- SYPHON extractions
- @asks system
- Source research findings
- Agent intelligence
- Daily source sweeps

ORDER 66: @DOIT execution command

Tags: #LAUGH #FACTORY #CONTENT #PRODUCTION #INGESTION #AGGREGATION #COLLATION #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LAFFProduceFromIngestions")


class LAFFProduceFromIngestions:
    """
    L.A.F.F. - Produce Content from Ingestion Aggregations & Collations

    Produces content from all ingested/aggregated/collated data sources
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize content producer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"

        # L.A.F.F. Factory
        try:
            from lumina_film_factory import LuminaFilmFactory
            self.factory = LuminaFilmFactory(project_root=self.project_root)
            logger.info("✅ L.A.F.F. Factory initialized")
        except Exception as e:
            self.factory = None
            logger.error(f"❌ Failed to initialize L.A.F.F. Factory: {e}")

        logger.info("✅ L.A.F.F. Produce From Ingestions initialized")

    def produce_content_from_all_sources(self) -> Dict[str, Any]:
        """
        Produce content from all ingestion aggregations and collations

        ORDER 66: @DOIT execution command
        """
        logger.info("="*80)
        logger.info("🎬 ORDER 66: L.A.F.F. Content Production from Ingestions")
        logger.info("="*80)

        if not self.factory:
            return {
                "success": False,
                "error": "L.A.F.F. Factory not available"
            }

        production_result = {
            "timestamp": datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT",
            "sources_analyzed": [],
            "productions_created": [],
            "success": True,
            "errors": []
        }

        # 1. Aggregate data from all sources
        logger.info("\n📊 Aggregating data from all ingestion sources...")
        aggregated_data = self._aggregate_all_ingestion_data()
        production_result["sources_analyzed"] = aggregated_data.get("sources", [])
        logger.info(f"   ✅ Analyzed {len(aggregated_data.get('sources', []))} data sources")

        # 2. Produce Book from aggregated data
        logger.info("\n📚 Producing Book from aggregated data...")
        try:
            book_data = self._prepare_book_data(aggregated_data)
            if book_data:
                book = self.factory.produce_book(
                    title=book_data.get("title", "LUMINA Intelligence: Collected Wisdom"),
                    subtitle=book_data.get("subtitle", "Content from LUMINA Ecosystem Ingestion Aggregations"),
                    author="L.A.F.F. - LUMINA A FILM FACTORY"
                )
                if book:
                    production_result["productions_created"].append({
                        "type": "book",
                        "production_id": book.production_id,
                        "title": book.title,
                        "chapters": len(book.chapters)
                    })
                    logger.info(f"   ✅ Book produced: {book.title} ({len(book.chapters)} chapters)")
        except Exception as e:
            error_msg = f"Error producing book: {e}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            production_result["errors"].append(error_msg)

        # 3. Produce Docuseries from aggregated data
        logger.info("\n🎬 Producing Docuseries from aggregated data...")
        try:
            docuseries_data = self._prepare_docuseries_data(aggregated_data)
            if docuseries_data:
                docuseries = self.factory.produce_docuseries(
                    title=docuseries_data.get("title", "LUMINA Deep Dive: Intelligence & Insights"),
                    description=docuseries_data.get("description", "A docuseries exploring insights from LUMINA ecosystem data aggregations")
                )
                if docuseries:
                    production_result["productions_created"].append({
                        "type": "docuseries",
                        "production_id": docuseries.production_id,
                        "title": docuseries.title,
                        "episodes": len(docuseries.chapters)
                    })
                    logger.info(f"   ✅ Docuseries produced: {docuseries.title} ({len(docuseries.chapters)} episodes)")
        except Exception as e:
            error_msg = f"Error producing docuseries: {e}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            production_result["errors"].append(error_msg)

        logger.info("="*80)
        logger.info("✅ L.A.F.F. Content Production Complete")
        logger.info(f"   Productions Created: {len(production_result['productions_created'])}")
        logger.info("="*80)

        return production_result

    def _aggregate_all_ingestion_data(self) -> Dict[str, Any]:
        """Aggregate data from all ingestion sources"""
        aggregated = {
            "sources": [],
            "asks": [],
            "syphon_extractions": [],
            "source_research": [],
            "intelligence": [],
            "total_items": 0
        }

        # 1. @asks system
        asks_dir = self.data_dir / "asks"
        if asks_dir.exists():
            ask_files = list(asks_dir.glob("*.json"))
            for ask_file in ask_files[:50]:  # Limit to 50 most recent
                try:
                    with open(ask_file, 'r', encoding='utf-8') as f:
                        ask_data = json.load(f)
                        aggregated["asks"].append({
                            "ask": ask_data.get("ask", ""),
                            "description": ask_data.get("description", ""),
                            "tags": ask_data.get("tags", []),
                            "timestamp": ask_data.get("timestamp", "")
                        })
                        aggregated["total_items"] += 1
                except:
                    pass
            if aggregated["asks"]:
                aggregated["sources"].append(f"@asks system ({len(aggregated['asks'])} asks)")

        # 2. SYPHON extractions
        syphon_dir = self.data_dir / "syphon"
        if syphon_dir.exists():
            # Check imported sources
            imported_dir = syphon_dir / "imported_sources"
            if imported_dir.exists():
                import_files = list(imported_dir.glob("import_result_*.json"))
                for import_file in import_files[:10]:  # Limit to 10 most recent
                    try:
                        with open(import_file, 'r', encoding='utf-8') as f:
                            import_data = json.load(f)
                            extractions = import_data.get("syphon_extractions", [])
                            if extractions:
                                aggregated["syphon_extractions"].extend(extractions)
                                aggregated["total_items"] += len(extractions)
                    except:
                        pass
            if aggregated["syphon_extractions"]:
                aggregated["sources"].append(f"SYPHON extractions ({len(aggregated['syphon_extractions'])} items)")

        # 3. Source research findings
        source_research_dir = self.data_dir / "source_deep_research_missions"
        if source_research_dir.exists():
            mission_file = source_research_dir / "mission.json"
            if mission_file.exists():
                try:
                    with open(mission_file, 'r', encoding='utf-8') as f:
                        mission_data = json.load(f)
                        scans = mission_data.get("daily_scans", [])
                        for scan in scans[:20]:  # Limit to 20 most recent scans
                            findings = scan.get("social_media_findings", []) + scan.get("academic_paper_findings", [])
                            aggregated["source_research"].extend(findings)
                            aggregated["total_items"] += len(findings)
                    if aggregated["source_research"]:
                        aggregated["sources"].append(f"Source research ({len(aggregated['source_research'])} findings)")
                except:
                    pass

        # 4. Intelligence data
        intelligence_dir = self.data_dir / "intelligence"
        if intelligence_dir.exists():
            intel_files = list(intelligence_dir.glob("*.json"))
            for intel_file in intel_files[:20]:  # Limit to 20 most recent
                try:
                    with open(intel_file, 'r', encoding='utf-8') as f:
                        intel_data = json.load(f)
                        if isinstance(intel_data, list):
                            aggregated["intelligence"].extend(intel_data)
                        else:
                            aggregated["intelligence"].append(intel_data)
                        aggregated["total_items"] += 1
                except:
                    pass
            if aggregated["intelligence"]:
                aggregated["sources"].append(f"Intelligence data ({len(aggregated['intelligence'])} items)")

        return aggregated

    def _prepare_book_data(self, aggregated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepare book data from aggregated sources"""
        if not aggregated_data.get("total_items", 0):
            return None

        # Create book structure from aggregated data
        title = "LUMINA Intelligence: Collected Wisdom from Ecosystem Aggregations"
        subtitle = f"Content from {len(aggregated_data['sources'])} data sources ({aggregated_data['total_items']} items)"

        return {
            "title": title,
            "subtitle": subtitle,
            "sources": aggregated_data["sources"],
            "content_summary": {
                "asks_count": len(aggregated_data.get("asks", [])),
                "syphon_extractions_count": len(aggregated_data.get("syphon_extractions", [])),
                "source_research_count": len(aggregated_data.get("source_research", [])),
                "intelligence_count": len(aggregated_data.get("intelligence", []))
            }
        }

    def _prepare_docuseries_data(self, aggregated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepare docuseries data from aggregated sources"""
        if not aggregated_data.get("total_items", 0):
            return None

        title = "LUMINA Deep Dive: Intelligence & Insights from Ecosystem Data"
        description = f"A docuseries exploring insights from {len(aggregated_data['sources'])} data sources, featuring {aggregated_data['total_items']} aggregated items including @asks, SYPHON extractions, source research, and intelligence data."

        return {
            "title": title,
            "description": description,
            "sources": aggregated_data["sources"],
            "episodes_preview": {
                "asks_episode": f"Exploring {len(aggregated_data.get('asks', []))} @asks",
                "syphon_episode": f"SYPHON Intelligence: {len(aggregated_data.get('syphon_extractions', []))} extractions",
                "research_episode": f"Source Research Findings: {len(aggregated_data.get('source_research', []))} discoveries",
                "intelligence_episode": f"Intelligence Analysis: {len(aggregated_data.get('intelligence', []))} insights"
            }
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎬 L.A.F.F. - Produce Content from Ingestion Aggregations & Collations")
    print("="*80 + "\n")

    producer = LAFFProduceFromIngestions()
    result = producer.produce_content_from_all_sources()

    print("\n" + "="*80)
    print("📊 PRODUCTION RESULTS")
    print("="*80)
    print(f"Timestamp: {result['timestamp']}")
    print(f"Execution Type: {result['execution_type']}")
    print(f"Success: {result['success']}")

    print(f"\nSources Analyzed: {len(result['sources_analyzed'])}")
    for source in result['sources_analyzed']:
        print(f"   📊 {source}")

    print(f"\nProductions Created: {len(result['productions_created'])}")
    for production in result['productions_created']:
        prod_type = production.get('type', 'unknown')
        title = production.get('title', 'Unknown')
        count = production.get('chapters') or production.get('episodes', 0)
        count_type = 'chapters' if prod_type == 'book' else 'episodes'
        print(f"   🎬 {prod_type.upper()}: {title} ({count} {count_type})")

    if result.get('errors'):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   ❌ {error}")

    print("\n✅ L.A.F.F. Content Production Complete")
    print("="*80 + "\n")
