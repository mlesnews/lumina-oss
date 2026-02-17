#!/usr/bin/env python3
"""
Examine All VAs State & Re-SYPHON Intelligence Extraction

Examines current state of all Virtual Assistants (VAs):
- IMVA (Iron Man Virtual Assistant)
- ACVA (Anakin/Vader Combat Virtual Assistant)
- JARVIS VA
- Any other VAs

Then re-runs SYPHON intelligence extraction on all VA-related data.

ORDER 66: @DOIT execution command

Tags: #VAS #IMVA #ACVA #JARVIS #SYPHON #INTELLIGENCE #EXTRACTION #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import signal
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsStateResyphon")

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

# Unified system integration
try:
    from syphon_agents_asks_unified_system import SYPHONAgentsAsksUnifiedSystem
    UNIFIED_SYSTEM_AVAILABLE = True
except ImportError:
    UNIFIED_SYSTEM_AVAILABLE = False
    SYPHONAgentsAsksUnifiedSystem = None


class VAsStateResyphon:
    """
    Examine All VAs State & Re-SYPHON Intelligence Extraction

    Examines current state of all VAs and re-runs SYPHON extraction
    """

    def __init__(self, project_root: Optional[Path] = None, max_files_per_va: int = 5, extraction_timeout: int = 300, skip_syphon: bool = False):
        """
        Initialize VA state examiner and SYPHON re-extractor

        Args:
            project_root: Project root directory
            max_files_per_va: Maximum files to process per VA (default: 5)
            extraction_timeout: Timeout in seconds for SYPHON extraction (default: 300 = 5 minutes)
            skip_syphon: Skip SYPHON extraction entirely (default: False)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.vas_dir = self.data_dir / "vas"
        self.vas_dir.mkdir(parents=True, exist_ok=True)
        self.max_files_per_va = max_files_per_va
        self.extraction_timeout = extraction_timeout
        self.extraction_start_time = None
        self.skip_syphon = skip_syphon

        # SYPHON system
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=self.project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        # Unified system
        self.unified_system = None
        if UNIFIED_SYSTEM_AVAILABLE:
            try:
                self.unified_system = SYPHONAgentsAsksUnifiedSystem(project_root=self.project_root)
                logger.info("✅ Unified system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Unified system not available: {e}")

        logger.info("✅ VAs State Resyphon initialized")

    def examine_all_vas_and_resyphon(self) -> Dict[str, Any]:
        """
        Examine all VAs state and re-run SYPHON extraction

        ORDER 66: @DOIT execution command
        """
        logger.info("="*80)
        logger.info("🤖 ORDER 66: Examining All VAs State & Re-SYPHON Intelligence Extraction")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT",
            "vas_examined": [],
            "vas_state": {},
            "syphon_extractions": [],
            "success": True,
            "errors": []
        }

        # 1. Discover all VAs
        logger.info("\n🔍 Discovering all Virtual Assistants...")
        vas = self._discover_all_vas()
        logger.info(f"   ✅ Found {len(vas)} VAs")

        # 2. Examine each VA state
        logger.info("\n📊 Examining VA states...")
        for va_id, va_info in vas.items():
            try:
                va_state = self._examine_va_state(va_id, va_info)
                result["vas_examined"].append(va_id)
                result["vas_state"][va_id] = va_state
                logger.info(f"   ✅ {va_id}: {va_state.get('status', 'unknown')}")
            except Exception as e:
                error_msg = f"Error examining {va_id}: {e}"
                logger.error(f"❌ {error_msg}", exc_info=True)
                result["errors"].append(error_msg)

        # 3. Re-run SYPHON on all VA-related data
        if self.skip_syphon:
            logger.info("\n⏭️  Skipping SYPHON extraction (--skip-syphon enabled)")
            result["syphon_extractions"] = []
        else:
            logger.info("\n🧬 Re-running SYPHON intelligence extraction on VA data...")
            logger.info(f"   ⏱️  Timeout: {self.extraction_timeout}s | Max files per VA: {self.max_files_per_va}")
        if self.syphon and not self.skip_syphon:
            try:
                self.extraction_start_time = time.time()
                syphon_results = self._resyphon_va_data(vas)
                elapsed_time = time.time() - self.extraction_start_time
                result["syphon_extractions"] = syphon_results
                logger.info(f"   ✅ SYPHON extracted intelligence from {len(syphon_results)} sources")
                logger.info(f"   ⏱️  Extraction completed in {elapsed_time:.1f}s")
            except TimeoutError as e:
                error_msg = f"SYPHON extraction timeout after {self.extraction_timeout}s: {e}"
                logger.warning(f"⚠️  {error_msg}")
                result["errors"].append(error_msg)
                result["success"] = False
            except Exception as e:
                error_msg = f"Error re-running SYPHON: {e}"
                logger.error(f"❌ {error_msg}", exc_info=True)
                result["errors"].append(error_msg)
                result["success"] = False
        else:
            logger.warning("⚠️  SYPHON not available - skipping extraction")

        # 4. Save comprehensive report
        report_file = self.vas_dir / f"vas_state_resyphon_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"   ✅ Report saved: {report_file.name}")
        except Exception as e:
            logger.error(f"❌ Error saving report: {e}")

        logger.info("="*80)
        logger.info("✅ VAs State Examination & Re-SYPHON Complete")
        logger.info(f"   VAs Examined: {len(result['vas_examined'])}")
        logger.info(f"   SYPHON Extractions: {len(result['syphon_extractions'])}")
        logger.info("="*80)

        return result

    def _discover_all_vas(self) -> Dict[str, Dict[str, Any]]:
        try:
            """Discover all Virtual Assistants in the system"""
            vas = {}

            # IMVA (Iron Man Virtual Assistant)
            vas["IMVA"] = {
                "name": "Iron Man Virtual Assistant",
                "type": "visual_assistant",
                "module": "imva_matrix_simulation_pipe",
                "status_file": self.data_dir / "imva" / "state.json",
                "description": "Iron Man Virtual Assistant with visual matrix simulation"
            }

            # ACVA (Anakin/Vader Combat Virtual Assistant)
            vas["ACVA"] = {
                "name": "Anakin/Vader Combat Virtual Assistant",
                "type": "combat_assistant",
                "module": "jarvis_acva_combat_demo",
                "status_file": self.data_dir / "acva" / "state.json",
                "description": "Combat-focused Virtual Assistant"
            }

            # JARVIS VA
            vas["JARVIS_VA"] = {
                "name": "JARVIS Virtual Assistant",
                "type": "chat_coordinator",
                "module": "jarvis_va_chat_coordinator",
                "status_file": self.data_dir / "jarvis_va" / "state.json",
                "description": "JARVIS Virtual Assistant chat coordinator"
            }

            # Check for additional VAs in data directory
            va_data_dir = self.data_dir / "vas"
            if va_data_dir.exists():
                for va_subdir in va_data_dir.iterdir():
                    if va_subdir.is_dir():
                        va_id = va_subdir.name.upper()
                        if va_id not in vas:
                            vas[va_id] = {
                                "name": f"{va_id} Virtual Assistant",
                                "type": "unknown",
                                "status_file": va_subdir / "state.json",
                                "description": f"Discovered VA: {va_id}"
                            }

            return vas

        except Exception as e:
            self.logger.error(f"Error in _discover_all_vas: {e}", exc_info=True)
            raise
    def _examine_va_state(self, va_id: str, va_info: Dict[str, Any]) -> Dict[str, Any]:
        """Examine state of a specific VA"""
        state = {
            "va_id": va_id,
            "va_info": va_info,
            "status": "unknown",
            "last_updated": None,
            "configuration": {},
            "health": {},
            "data_files": [],
            "intelligence_items": []
        }

        # Check status file
        status_file = va_info.get("status_file")
        if status_file and status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    state["status"] = status_data.get("status", "active")
                    state["last_updated"] = status_data.get("last_updated")
                    state["configuration"] = status_data.get("configuration", {})
                    state["health"] = status_data.get("health", {})
            except Exception as e:
                state["status"] = f"error_reading_state: {e}"
        else:
            state["status"] = "no_state_file"

        # Check for VA data files (multiple possible locations)
        va_data_dirs = [
            self.data_dir / va_id.lower(),
            self.data_dir / "ironman_assistant" if va_id == "IMVA" else None,
            self.data_dir / "armoury_crate" if va_id == "ACVA" else None,
            self.data_dir / "jarvis_fulltime" if va_id == "JARVIS_VA" else None,
            self.data_dir / "jarvis" / "va" if va_id == "JARVIS_VA" else None,
        ]
        all_data_files = []
        for va_data_dir in va_data_dirs:
            if va_data_dir and va_data_dir.exists():
                data_files = list(va_data_dir.glob("*.json")) + list(va_data_dir.glob("*.txt")) + list(va_data_dir.glob("*.log"))
                all_data_files.extend([str(f.relative_to(self.project_root)) for f in data_files])
        state["data_files"] = all_data_files

        # Try to import and check VA module
        module_name = va_info.get("module")
        if module_name:
            try:
                module = __import__(module_name, fromlist=[''])
                if hasattr(module, 'get_state'):
                    va_state = module.get_state()
                    state["module_state"] = va_state
                    state["status"] = "module_available"
            except Exception as e:
                state["module_error"] = str(e)

        return state

    def _check_timeout(self) -> None:
        """Check if extraction timeout has been exceeded"""
        if self.extraction_start_time:
            elapsed = time.time() - self.extraction_start_time
            if elapsed > self.extraction_timeout:
                raise TimeoutError(f"SYPHON extraction exceeded timeout of {self.extraction_timeout}s")

    def _resyphon_va_data(self, vas: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Re-run SYPHON intelligence extraction on VA data

        Optimized with:
        - File limiting (max_files_per_va)
        - Timeout checking
        - Progress reporting
        - Batch processing
        """
        extractions = []

        if not self.syphon:
            return extractions

        total_vas = len(vas)
        for va_idx, (va_id, va_info) in enumerate(vas.items(), 1):
            # Check timeout before processing each VA
            self._check_timeout()

            logger.info(f"   📊 Processing {va_id} ({va_idx}/{total_vas})...")

            # Extract from VA data files (multiple possible locations)
            va_data_dirs = [
                self.data_dir / va_id.lower(),
                self.data_dir / "ironman_assistant" if va_id == "IMVA" else None,
                self.data_dir / "armoury_crate" if va_id == "ACVA" else None,
                self.data_dir / "jarvis_fulltime" if va_id == "JARVIS_VA" else None,
                self.data_dir / "jarvis" / "va" if va_id == "JARVIS_VA" else None,
            ]

            all_data_files = []
            for va_data_dir in va_data_dirs:
                if va_data_dir and va_data_dir.exists():
                    data_files = list(va_data_dir.glob("*.json")) + list(va_data_dir.glob("*.txt")) + list(va_data_dir.glob("*.log"))
                    all_data_files.extend(data_files)

            # Limit files per VA (optimized from 10 to 5)
            files_to_process = all_data_files[:self.max_files_per_va]
            total_files = len(files_to_process)

            if total_files == 0:
                logger.info(f"      ⚠️  No data files found for {va_id}")
                continue

            logger.info(f"      📁 Processing {total_files} file(s) for {va_id}...")

            # Process files in batches with progress reporting
            batch_size = 1  # Process 1 file at a time for better timeout control
            for batch_idx in range(0, total_files, batch_size):
                # Check timeout before each batch
                self._check_timeout()

                batch = files_to_process[batch_idx:batch_idx + batch_size]
                batch_num = (batch_idx // batch_size) + 1
                total_batches = (total_files + batch_size - 1) // batch_size

                logger.info(f"      🔄 Batch {batch_num}/{total_batches} ({len(batch)} file(s))...")

                for file_idx, data_file in enumerate(batch, 1):
                    # Check timeout before each file
                    self._check_timeout()

                    try:
                        # Check if file is empty
                        if data_file.stat().st_size == 0:
                            logger.debug(f"   ⚠️  Skipping empty file: {data_file.name}")
                            continue

                        with open(data_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if not content:
                                logger.debug(f"   ⚠️  Skipping empty content file: {data_file.name}")
                                continue

                            # Try to parse JSON if it's a JSON file
                            if data_file.suffix == '.json':
                                try:
                                    data = json.loads(content)
                                    content = json.dumps(data, indent=2)
                                except json.JSONDecodeError:
                                    # If JSON parsing fails, use raw content
                                    logger.debug(f"   ⚠️  Invalid JSON, using raw content: {data_file.name}")
                                    pass

                            # Extract intelligence using SYPHON email method (works for generic text)
                            # Check if syphon_email method exists, otherwise use extract_email
                            # OPTIMIZED: Skip SYPHON extraction for large files or use fast mode
                            syphon_result = None
                            actionable_items = []
                            tasks = []
                            decisions = []
                            intelligence = []

                            # Skip SYPHON for very large files (>100KB) to save time
                            file_size_kb = data_file.stat().st_size / 1024
                            if file_size_kb > 100:
                                logger.debug(f"         ⚠️  Skipping SYPHON for large file: {data_file.name} ({file_size_kb:.1f}KB)")
                            else:
                                try:
                                    # Check timeout before SYPHON extraction
                                    self._check_timeout()

                                    file_start_time = time.time()
                                    max_file_time = 10  # Max 10 seconds per file

                                    if hasattr(self.syphon, 'syphon_email'):
                                        syphon_result = self.syphon.syphon_email(
                                            email_id=f"{va_id}_{data_file.stem}",
                                            subject=f"VA Data: {va_id} - {data_file.name}",
                                            body=content[:50000],  # Limit content to 50KB for speed
                                            from_address=f"{va_id}@lumina.system",
                                            to_address="syphon@lumina.system",
                                            metadata={
                                                "va_id": va_id,
                                                "va_name": va_info.get("name"),
                                                "file": str(data_file.relative_to(self.project_root)),
                                                "source_type": "va_data_file"
                                            }
                                        )
                                    elif hasattr(self.syphon, 'extract_email'):
                                        syphon_result = self.syphon.extract_email(
                                            email_id=f"{va_id}_{data_file.stem}",
                                            subject=f"VA Data: {va_id} - {data_file.name}",
                                            body=content[:50000],  # Limit content to 50KB for speed
                                            from_address=f"{va_id}@lumina.system",
                                            to_address="syphon@lumina.system",
                                            metadata={
                                                "va_id": va_id,
                                                "va_name": va_info.get("name"),
                                                "file": str(data_file.relative_to(self.project_root)),
                                                "source_type": "va_data_file"
                                            }
                                        )
                                    elif hasattr(self.syphon, 'extract'):
                                        # Fallback: use extract method
                                        from syphon import DataSourceType
                                        syphon_result = self.syphon.extract(
                                            DataSourceType.OTHER,
                                            content[:50000],  # Limit content to 50KB for speed
                                            metadata={
                                                "va_id": va_id,
                                                "va_name": va_info.get("name"),
                                                "file": str(data_file.relative_to(self.project_root)),
                                                "source_type": "va_data_file"
                                            }
                                        )

                                    # Check if file processing took too long
                                    file_elapsed = time.time() - file_start_time
                                    if file_elapsed > max_file_time:
                                        logger.warning(f"         ⚠️  File extraction took {file_elapsed:.1f}s (limit: {max_file_time}s)")

                                    # Extract attributes (handle both SyphonData objects and dicts)
                                    if syphon_result:
                                        if hasattr(syphon_result, 'actionable_items'):
                                            actionable_items = syphon_result.actionable_items
                                            tasks = syphon_result.tasks
                                            decisions = syphon_result.decisions
                                            intelligence = syphon_result.intelligence
                                        elif isinstance(syphon_result, dict):
                                            actionable_items = syphon_result.get('actionable_items', [])
                                            tasks = syphon_result.get('tasks', [])
                                            decisions = syphon_result.get('decisions', [])
                                            intelligence = syphon_result.get('intelligence', [])
                                except TimeoutError:
                                    logger.warning(f"         ⚠️  Timeout during SYPHON extraction: {data_file.name}")
                                    raise  # Re-raise to stop processing
                                except Exception as e:
                                    logger.debug(f"         ⚠️  SYPHON extraction error: {e}")

                            # Create extraction result structure
                            extraction_result = {
                                "data_id": f"{va_id}_{data_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                "source_type": "va_data",
                                "source_id": f"{va_id}_{data_file.stem}",
                                "content": content[:500],  # Limit content preview
                                "metadata": {
                                    "va_id": va_id,
                                    "va_name": va_info.get("name"),
                                    "file": str(data_file.relative_to(self.project_root)),
                                    "extracted_at": datetime.now().isoformat()
                                },
                                "actionable_items": actionable_items,
                                "tasks": tasks,
                                "decisions": decisions,
                                "intelligence": intelligence,
                                "extracted_at": datetime.now().isoformat()
                            }

                            extractions.append({
                                "va_id": va_id,
                                "source_file": str(data_file.relative_to(self.project_root)),
                                "actionable_items": actionable_items,
                                "tasks": tasks,
                                "decisions": decisions,
                                "intelligence": intelligence,
                                "extracted_at": extraction_result["extracted_at"]
                            })
                    except Exception as e:
                        logger.warning(f"⚠️  Error extracting from {data_file}: {e}")

        # Also extract from unified system if available
        if self.unified_system:
            try:
                # Get VA intelligence from unified system
                # Try get_intelligence_for_agent (correct method name)
                if hasattr(self.unified_system, 'get_intelligence_for_agent'):
                    va_intelligence = self.unified_system.get_intelligence_for_agent(agent_id="all_vas")
                elif hasattr(self.unified_system, 'get_agent_intelligence'):
                    va_intelligence = self.unified_system.get_agent_intelligence(agent_id="all_vas")
                else:
                    va_intelligence = None

                if va_intelligence:
                    extractions.append({
                        "source": "unified_system",
                        "intelligence": va_intelligence
                    })
            except Exception as e:
                logger.warning(f"⚠️  Error extracting from unified system: {e}")

        return extractions


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Examine All VAs State & Re-SYPHON Intelligence Extraction")
    parser.add_argument('--max-files', type=int, default=5, help='Maximum files to process per VA (default: 5)')
    parser.add_argument('--timeout', type=int, default=300, help='Extraction timeout in seconds (default: 300)')
    parser.add_argument('--skip-syphon', action='store_true', help='Skip SYPHON extraction (faster execution)')

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🤖 Examine All VAs State & Re-SYPHON Intelligence Extraction")
    print("="*80)
    syphon_status = "SKIPPED" if args.skip_syphon else "ENABLED"
    print(f"   ⚙️  Configuration: Max files per VA={args.max_files}, Timeout={args.timeout}s, SYPHON={syphon_status}")
    print("="*80 + "\n")

    examiner = VAsStateResyphon(max_files_per_va=args.max_files, extraction_timeout=args.timeout, skip_syphon=args.skip_syphon)
    result = examiner.examine_all_vas_and_resyphon()

    print("\n" + "="*80)
    print("📊 EXAMINATION RESULTS")
    print("="*80)
    print(f"Timestamp: {result['timestamp']}")
    print(f"Execution Type: {result['execution_type']}")
    print(f"Success: {result['success']}")

    print(f"\nVAs Examined: {len(result['vas_examined'])}")
    for va_id in result['vas_examined']:
        va_state = result['vas_state'].get(va_id, {})
        status = va_state.get('status', 'unknown')
        print(f"   🤖 {va_id}: {status}")
        if va_state.get('data_files'):
            print(f"      📁 Data files: {len(va_state['data_files'])}")
        if va_state.get('module_state'):
            print(f"      ⚙️  Module: Available")

    print(f"\nSYPHON Extractions: {len(result['syphon_extractions'])}")
    total_items = sum(len(e.get('actionable_items', [])) for e in result['syphon_extractions'])
    total_tasks = sum(len(e.get('tasks', [])) for e in result['syphon_extractions'])
    total_intelligence = sum(len(e.get('intelligence', [])) for e in result['syphon_extractions'])
    print(f"   📊 Total actionable items: {total_items}")
    print(f"   📋 Total tasks: {total_tasks}")
    print(f"   🧬 Total intelligence items: {total_intelligence}")

    if result.get('errors'):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   ❌ {error}")

    print("\n✅ VAs State Examination & Re-SYPHON Complete")
    print("="*80 + "\n")
