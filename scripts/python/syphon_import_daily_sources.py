#!/usr/bin/env python3
"""
SYPHON Import @DAILY @SOURCES

Begin all @syphon imports of @daily @sources.
Extracts intelligence from daily source sweeps using SYPHON system.

ORDER 66: @DOIT execution command

Tags: #SYPHON #DAILY #SOURCES #IMPORT #INTELLIGENCE #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
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

logger = get_logger("SYPHONImportDailySources")

# SYPHON integration
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType, SyphonData
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None
    SyphonData = None
    logger.warning("SYPHON system not available")

# Daily source sweeps integration
try:
    from source_deep_research_missions import SourceDeepResearchMissions, DailyScan
    SOURCE_RESEARCH_AVAILABLE = True
except ImportError:
    SOURCE_RESEARCH_AVAILABLE = False
    SourceDeepResearchMissions = None
    DailyScan = None


class SYPHONImportDailySources:
    """
    SYPHON Import @DAILY @SOURCES

    Begin all @syphon imports of @daily @sources.
    Extracts intelligence from daily source sweeps using SYPHON system.

    ORDER 66: @DOIT execution command
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON import system for daily sources"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.sweeps_dir = self.data_dir / "daily_source_sweeps"
        self.syphon_data_dir = self.data_dir / "syphon" / "imported_sources"
        self.syphon_data_dir.mkdir(parents=True, exist_ok=True)

        # SYPHON system
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=self.project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON system not available: {e}")

        # Source research missions
        self.source_research = None
        if SOURCE_RESEARCH_AVAILABLE:
            try:
                self.source_research = SourceDeepResearchMissions(project_root=self.project_root)
                logger.info("✅ Source Deep Research Missions initialized")
            except Exception as e:
                logger.warning(f"⚠️  Source Deep Research Missions not available: {e}")

        logger.info("✅ SYPHON Import Daily Sources initialized")

    def begin_all_syphon_imports(self) -> Dict[str, Any]:
        """
        Begin all @syphon imports of @daily @sources

        ORDER 66: @DOIT execution command

        Returns:
            Dict with import results
        """
        logger.info("="*80)
        logger.info("🚀 ORDER 66: Begin All @SYPHON Imports of @DAILY @SOURCES")
        logger.info("="*80)

        import_result = {
            "timestamp": datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT",
            "sources_imported": [],
            "total_items_imported": 0,
            "syphon_extractions": [],
            "success": True,
            "errors": []
        }

        if not self.syphon:
            error_msg = "SYPHON system not available"
            logger.error(f"❌ {error_msg}")
            import_result["success"] = False
            import_result["errors"].append(error_msg)
            return import_result

        # Find all daily source sweep files
        sweep_files = self._find_daily_sweep_files()
        logger.info(f"📋 Found {len(sweep_files)} daily source sweep files to import")

        # Import each sweep file into SYPHON
        for sweep_file in sweep_files:
            try:
                logger.info(f"📥 Importing: {sweep_file.name}...")
                import_data = self._import_sweep_file(sweep_file)

                if import_data:
                    import_result["sources_imported"].append({
                        "file": sweep_file.name,
                        "items_imported": import_data.get("items_imported", 0),
                        "syphon_extractions": import_data.get("syphon_extractions", 0)
                    })
                    import_result["total_items_imported"] += import_data.get("items_imported", 0)
                    import_result["syphon_extractions"].extend(import_data.get("syphon_extractions", []))
                    logger.info(f"   ✅ Imported {import_data.get('items_imported', 0)} items, {import_data.get('syphon_extractions', 0)} SYPHON extractions")
            except Exception as e:
                error_msg = f"Error importing {sweep_file.name}: {e}"
                logger.error(f"❌ {error_msg}", exc_info=True)
                import_result["errors"].append(error_msg)

        # Also import from current daily scans if available
        if self.source_research:
            try:
                logger.info("📥 Importing from current source research missions...")
                current_import = self._import_current_scans()
                if current_import:
                    import_result["sources_imported"].append({
                        "source": "current_scans",
                        "items_imported": current_import.get("items_imported", 0),
                        "syphon_extractions": current_import.get("syphon_extractions", 0)
                    })
                    import_result["total_items_imported"] += current_import.get("items_imported", 0)
                    import_result["syphon_extractions"].extend(current_import.get("syphon_extractions", []))
                    logger.info(f"   ✅ Imported {current_import.get('items_imported', 0)} items from current scans")
            except Exception as e:
                error_msg = f"Error importing current scans: {e}"
                logger.warning(f"⚠️  {error_msg}")
                import_result["errors"].append(error_msg)

        # Save import result
        result_file = self.syphon_data_dir / f"import_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(import_result, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"💾 Import result saved: {result_file.name}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save import result: {e}")

        logger.info("="*80)
        logger.info(f"✅ ORDER 66: @SYPHON Imports Complete")
        logger.info(f"   Sources Imported: {len(import_result['sources_imported'])}")
        logger.info(f"   Total Items: {import_result['total_items_imported']}")
        logger.info(f"   SYPHON Extractions: {len(import_result['syphon_extractions'])}")
        logger.info("="*80)

        return import_result

    def _find_daily_sweep_files(self) -> List[Path]:
        try:
            """Find all daily source sweep files"""
            sweep_files = []

            # Check sweeps directory
            if self.sweeps_dir.exists():
                # Look for execution result files
                for file in self.sweeps_dir.glob("execution_*.json"):
                    sweep_files.append(file)

                # Look for peak MCP execution files
                for file in self.sweeps_dir.glob("peak_mcp_execution_*.json"):
                    sweep_files.append(file)

            # Check source research missions data directory
            source_research_dir = self.data_dir / "source_deep_research_missions"
            if source_research_dir.exists():
                # Look for scan files
                scans_dir = source_research_dir / "scans"
                if scans_dir.exists():
                    for file in scans_dir.glob("scan_*.json"):
                        sweep_files.append(file)

            return sorted(sweep_files, key=lambda p: p.stat().st_mtime, reverse=True)

        except Exception as e:
            self.logger.error(f"Error in _find_daily_sweep_files: {e}", exc_info=True)
            raise
    def _import_sweep_file(self, sweep_file: Path) -> Optional[Dict[str, Any]]:
        """Import a sweep file into SYPHON"""
        try:
            with open(sweep_file, 'r', encoding='utf-8') as f:
                sweep_data = json.load(f)

            # Extract content from sweep data
            content_items = []

            # Extract from sweeps_executed
            for sweep in sweep_data.get("sweeps_executed", []):
                # Extract scan data
                scan_id = sweep.get("scan_id", "")
                sources_scanned = sweep.get("sources_scanned", 0)
                items_found = sweep.get("items_found", 0)
                categories = sweep.get("categories", {})

                content_items.append({
                    "type": "daily_scan",
                    "scan_id": scan_id,
                    "sources_scanned": sources_scanned,
                    "items_found": items_found,
                    "categories": categories
                })

            # Convert to text for SYPHON extraction
            import_text = json.dumps(content_items, indent=2)

            # Extract intelligence using SYPHON
            if self.syphon:
                result = self.syphon.extract(
                    DataSourceType.IDE,
                    import_text,
                    metadata={
                        "source": "daily_source_sweeps",
                        "file": sweep_file.name,
                        "imported_at": datetime.now().isoformat()
                    }
                )

                syphon_extractions = []
                if result.success and result.data:
                    # Extract actionable items, tasks, decisions, intelligence
                    if result.data.actionable_items:
                        syphon_extractions.extend(result.data.actionable_items)
                    if result.data.tasks:
                        syphon_extractions.extend([str(t) for t in result.data.tasks])
                    if result.data.decisions:
                        syphon_extractions.extend([str(d) for d in result.data.decisions])
                    if result.data.intelligence:
                        syphon_extractions.extend(result.data.intelligence)

                return {
                    "items_imported": len(content_items),
                    "syphon_extractions": syphon_extractions,
                    "syphon_success": result.success
                }

        except Exception as e:
            logger.error(f"Error importing sweep file {sweep_file.name}: {e}", exc_info=True)
            raise

        return None

    def _import_current_scans(self) -> Optional[Dict[str, Any]]:
        """Import current scans from source research missions"""
        if not self.source_research:
            return None

        try:
            # Get mission status to find scans
            mission_status = self.source_research.get_mission_status()
            total_scans = mission_status.get("total_daily_scans", 0)

            # Load mission data
            mission_file = self.data_dir / "source_deep_research_missions" / "mission.json"
            if mission_file.exists():
                with open(mission_file, 'r', encoding='utf-8') as f:
                    mission_data = json.load(f)

                # Extract scan data
                scans = mission_data.get("daily_scans", [])
                content_items = []

                for scan in scans:
                    # Extract findings from scan
                    social_media_findings = scan.get("social_media_findings", [])
                    academic_paper_findings = scan.get("academic_paper_findings", [])

                    for finding in social_media_findings + academic_paper_findings:
                        content_items.append({
                            "type": "research_finding",
                            "source": finding.get("source"),
                            "title": finding.get("title"),
                            "content": finding.get("content", "")[:500],  # Limit content length
                            "url": finding.get("url"),
                            "author": finding.get("author"),
                            "date": finding.get("date")
                        })

                # Convert to text for SYPHON extraction
                import_text = json.dumps(content_items, indent=2)

                # Extract intelligence using SYPHON
                if self.syphon:
                    result = self.syphon.extract(
                        DataSourceType.IDE,
                        import_text,
                        metadata={
                            "source": "source_research_missions",
                            "imported_at": datetime.now().isoformat()
                        }
                    )

                    syphon_extractions = []
                    if result.success and result.data:
                        if result.data.actionable_items:
                            syphon_extractions.extend(result.data.actionable_items)
                        if result.data.tasks:
                            syphon_extractions.extend([str(t) for t in result.data.tasks])
                        if result.data.decisions:
                            syphon_extractions.extend([str(d) for d in result.data.decisions])
                        if result.data.intelligence:
                            syphon_extractions.extend(result.data.intelligence)

                    return {
                        "items_imported": len(content_items),
                        "syphon_extractions": syphon_extractions,
                        "syphon_success": result.success
                    }

        except Exception as e:
            logger.error(f"Error importing current scans: {e}", exc_info=True)
            raise

        return None


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ORDER 66: Begin All @SYPHON Imports of @DAILY @SOURCES")
    print("="*80 + "\n")

    importer = SYPHONImportDailySources()
    result = importer.begin_all_syphon_imports()

    print("\n" + "="*80)
    print("📊 IMPORT RESULT")
    print("="*80)
    print(f"Execution Type: {result['execution_type']}")
    print(f"Success: {result['success']}")
    print(f"\nSources Imported: {len(result['sources_imported'])}")
    print(f"Total Items Imported: {result['total_items_imported']}")
    print(f"SYPHON Extractions: {len(result['syphon_extractions'])}")

    if result['sources_imported']:
        print(f"\n  Imported Sources:")
        for source in result['sources_imported']:
            source_name = source.get('file') or source.get('source', 'unknown')
            print(f"    📥 {source_name}: {source.get('items_imported', 0)} items, {source.get('syphon_extractions', 0)} extractions")

    if result.get('errors'):
        print(f"\n  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"    ⚠️  {error}")

    print("\n✅ ORDER 66: @SYPHON Imports Complete")
    print("="*80 + "\n")
