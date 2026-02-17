#!/usr/bin/env python3
"""
PREVENT MEMORY DRIFT: Warm Recycle Memory Protection

Prevents AI memory drift by creating checkpoints before warm recycle
and restoring memory state after warm recycle.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class MemoryDriftPreventer:
    """
    Prevents AI memory drift during Cursor IDE warm recycle
    by creating checkpoints and restoring memory state
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize memory drift preventer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.memory_dir = self.data_dir / "memory"
        self.checkpoint_dir = self.data_dir / "memory_checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🛡️ Memory Drift Preventer initialized")

    def create_checkpoint_before_recycle(self) -> Path:
        try:
            """
            Create a memory checkpoint before warm recycle

            Returns:
                Path to checkpoint file
            """
            logger.info("="*80)
            logger.info("🛡️ CREATING MEMORY CHECKPOINT BEFORE WARM RECYCLE")
            logger.info("="*80)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_file = self.checkpoint_dir / f"memory_checkpoint_{timestamp}.json"

            checkpoint = {
                "checkpoint_metadata": {
                    "created_at": datetime.now().isoformat(),
                    "reason": "warm_recycle_protection",
                    "checkpoint_type": "full_memory_backup"
                },
                "memory_sources": self._capture_memory_sources(),
                "workflow_memory": self._capture_workflow_memory(),
                "session_memory": self._capture_session_memory(),
                "context_memory": self._capture_context_memory(),
                "r5_living_matrix": self._capture_r5_memory(),
                "master_feedback_loop": self._capture_master_feedback_loop(),
                "intelligence_memory": self._capture_intelligence_memory()
            }

            # Save checkpoint
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Checkpoint created: {checkpoint_file.name}")
            logger.info(f"   Memory sources: {len(checkpoint['memory_sources'])}")
            logger.info(f"   Workflow memory items: {len(checkpoint.get('workflow_memory', []))}")
            logger.info(f"   Session memory items: {len(checkpoint.get('session_memory', []))}")

            # Also create a "latest" checkpoint for easy restoration
            latest_checkpoint = self.checkpoint_dir / "memory_checkpoint_latest.json"
            shutil.copy(checkpoint_file, latest_checkpoint)
            logger.info(f"✅ Latest checkpoint updated: {latest_checkpoint.name}")

            logger.info("="*80)
            logger.info("✅ CHECKPOINT CREATION COMPLETE")
            logger.info("="*80)

            return checkpoint_file

        except Exception as e:
            self.logger.error(f"Error in create_checkpoint_before_recycle: {e}", exc_info=True)
            raise
    def _capture_memory_sources(self) -> List[Dict[str, Any]]:
        """Capture all memory source locations"""
        memory_sources = []

        # Memory directory files (short_term_memories.json, etc.)
        if self.memory_dir.exists():
            for mem_file in self.memory_dir.rglob("*.json"):
                try:
                    file_stat = mem_file.stat()
                    memory_sources.append({
                        "path": str(mem_file.relative_to(self.project_root)),
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "critical": mem_file.name in ["short_term_memories.json", "long_term_memories.json"]
                    })
                except Exception as e:
                    logger.warning(f"⚠️  Could not read memory file {mem_file}: {e}")

        # Also capture memory persistence config
        memory_config = self.project_root / "config" / "memory_persistence.json"
        if memory_config.exists():
            try:
                file_stat = memory_config.stat()
                memory_sources.append({
                    "path": str(memory_config.relative_to(self.project_root)),
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "critical": True
                })
            except Exception as e:
                logger.warning(f"⚠️  Could not read memory config: {e}")

        return memory_sources

    def _capture_workflow_memory(self) -> List[Dict[str, Any]]:
        """Capture workflow memory"""
        workflow_memory = []

        # Workflow memory persistence files
        memory_workflows_dir = self.memory_dir / "workflows"
        if memory_workflows_dir.exists():
            for mem_file in memory_workflows_dir.rglob("*.json"):
                try:
                    with open(mem_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        workflow_memory.append({
                            "type": "workflow_memory",
                            "file": str(mem_file.relative_to(self.project_root)),
                            "size": mem_file.stat().st_size,
                            "modified": datetime.fromtimestamp(mem_file.stat().st_mtime).isoformat()
                        })
                except Exception as e:
                    logger.warning(f"⚠️  Could not read workflow memory file {mem_file}: {e}")

        # Workflow completion verifications
        completion_dir = self.data_dir / "completion_verifications"
        if completion_dir.exists():
            for verif_file in completion_dir.glob("*.json"):
                try:
                    with open(verif_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        workflow_memory.append({
                            "type": "completion_verification",
                            "file": str(verif_file.relative_to(self.project_root)),
                            "data": data
                        })
                except Exception as e:
                    logger.warning(f"⚠️  Could not read verification file {verif_file}: {e}")

        return workflow_memory

    def _capture_session_memory(self) -> List[Dict[str, Any]]:
        """Capture session memory"""
        session_memory = []

        # Resumed sessions
        resumed_sessions_dir = self.data_dir / "resumed_sessions"
        if resumed_sessions_dir.exists():
            for session_file in resumed_sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        session_memory.append({
                            "type": "resumed_session",
                            "file": str(session_file.relative_to(self.project_root)),
                            "session_id": session_file.stem,
                            "size": session_file.stat().st_size
                        })
                except Exception as e:
                    logger.warning(f"⚠️  Could not read session file {session_file}: {e}")

        return session_memory

    def _capture_context_memory(self) -> Dict[str, Any]:
        """Capture context memory"""
        context_memory = {
            "r5_sessions": [],
            "master_todo": None,
            "ask_database": None
        }

        # R5 Living Matrix sessions
        r5_dir = self.project_root / "scripts" / "data" / "r5_living_matrix" / "sessions"
        if r5_dir.exists():
            for r5_file in r5_dir.glob("*.json"):
                context_memory["r5_sessions"].append({
                    "file": str(r5_file.relative_to(self.project_root)),
                    "size": r5_file.stat().st_size,
                    "modified": datetime.fromtimestamp(r5_file.stat().st_mtime).isoformat()
                })

        # Master TODO
        master_todo = self.project_root / "MASTER_TODO.md"
        if master_todo.exists():
            context_memory["master_todo"] = {
                "path": str(master_todo.relative_to(self.project_root)),
                "size": master_todo.stat().st_size,
                "modified": datetime.fromtimestamp(master_todo.stat().st_mtime).isoformat()
            }

        # Ask database
        ask_db = self.data_dir / "ask_database" / "asks.json"
        if ask_db.exists():
            try:
                with open(ask_db, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    context_memory["ask_database"] = {
                        "path": str(ask_db.relative_to(self.project_root)),
                        "total_asks": len(data),
                        "size": ask_db.stat().st_size
                    }
            except Exception as e:
                logger.warning(f"⚠️  Could not read ask database: {e}")

        return context_memory

    def _capture_r5_memory(self) -> Dict[str, Any]:
        try:
            """Capture R5 Living Matrix memory"""
            r5_memory = {
                "matrix_file": None,
                "sessions_count": 0
            }

            r5_matrix = self.project_root / "scripts" / "data" / "r5_living_matrix" / "LIVING_CONTEXT_MATRIX_PROMPT.md"
            if r5_matrix.exists():
                r5_memory["matrix_file"] = {
                    "path": str(r5_matrix.relative_to(self.project_root)),
                    "size": r5_matrix.stat().st_size,
                    "modified": datetime.fromtimestamp(r5_matrix.stat().st_mtime).isoformat()
                }

            r5_sessions_dir = self.project_root / "scripts" / "data" / "r5_living_matrix" / "sessions"
            if r5_sessions_dir.exists():
                r5_memory["sessions_count"] = len(list(r5_sessions_dir.glob("*.json")))

            return r5_memory

        except Exception as e:
            self.logger.error(f"Error in _capture_r5_memory: {e}", exc_info=True)
            raise
    def _capture_master_feedback_loop(self) -> Dict[str, Any]:
        try:
            """Capture Master Feedback Loop memory"""
            feedback_memory = {
                "feedback_files": [],
                "total_feedback": 0
            }

            feedback_dir = self.data_dir / "master_feedback_loop"
            if feedback_dir.exists():
                for feedback_file in feedback_dir.glob("*.json"):
                    feedback_memory["feedback_files"].append({
                        "file": str(feedback_file.relative_to(self.project_root)),
                        "size": feedback_file.stat().st_size,
                        "modified": datetime.fromtimestamp(feedback_file.stat().st_mtime).isoformat()
                    })
                    feedback_memory["total_feedback"] += 1

            return feedback_memory

        except Exception as e:
            self.logger.error(f"Error in _capture_master_feedback_loop: {e}", exc_info=True)
            raise
    def _capture_intelligence_memory(self) -> Dict[str, Any]:
        try:
            """Capture intelligence memory"""
            intel_memory = {
                "intelligence_files": [],
                "holocron_entries": []
            }

            intel_dir = self.data_dir / "intelligence"
            if intel_dir.exists():
                for intel_file in intel_dir.glob("*.md"):
                    intel_memory["intelligence_files"].append({
                        "file": str(intel_file.relative_to(self.project_root)),
                        "size": intel_file.stat().st_size,
                        "modified": datetime.fromtimestamp(intel_file.stat().st_mtime).isoformat()
                    })

            holocron_dir = self.data_dir / "holocron"
            if holocron_dir.exists():
                for holocron_file in holocron_dir.glob("*.md"):
                    intel_memory["holocron_entries"].append({
                        "file": str(holocron_file.relative_to(self.project_root)),
                        "size": holocron_file.stat().st_size
                    })

            return intel_memory

        except Exception as e:
            self.logger.error(f"Error in _capture_intelligence_memory: {e}", exc_info=True)
            raise
    def restore_memory_after_recycle(self, checkpoint_file: Optional[Path] = None) -> bool:
        """
        Restore memory from checkpoint after warm recycle

        Args:
            checkpoint_file: Path to checkpoint file (defaults to latest)

        Returns:
            True if restoration successful
        """
        logger.info("="*80)
        logger.info("🔄 RESTORING MEMORY AFTER WARM RECYCLE")
        logger.info("="*80)

        if checkpoint_file is None:
            checkpoint_file = self.checkpoint_dir / "memory_checkpoint_latest.json"

        if not checkpoint_file.exists():
            logger.error(f"❌ Checkpoint file not found: {checkpoint_file}")
            logger.info("💡 No checkpoint to restore. This may be the first run.")
            return False

        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)

            logger.info(f"✅ Checkpoint loaded: {checkpoint_file.name}")
            logger.info(f"   Created at: {checkpoint.get('checkpoint_metadata', {}).get('created_at', 'unknown')}")

            # Verify memory sources still exist
            memory_sources = checkpoint.get("memory_sources", [])
            logger.info(f"📊 Verifying {len(memory_sources)} memory sources...")

            verified_count = 0
            for source in memory_sources:
                source_path = self.project_root / source["path"]
                if source_path.exists():
                    verified_count += 1
                else:
                    logger.warning(f"⚠️  Memory source missing: {source['path']}")

            logger.info(f"✅ Verified {verified_count}/{len(memory_sources)} memory sources exist")

            # Log restoration summary
            logger.info("\n📊 Memory Restoration Summary:")
            logger.info(f"   Workflow memory items: {len(checkpoint.get('workflow_memory', []))}")
            logger.info(f"   Session memory items: {len(checkpoint.get('session_memory', []))}")
            logger.info(f"   R5 sessions: {checkpoint.get('r5_living_matrix', {}).get('sessions_count', 0)}")
            logger.info(f"   Feedback loop entries: {checkpoint.get('master_feedback_loop', {}).get('total_feedback', 0)}")
            logger.info(f"   Intelligence files: {len(checkpoint.get('intelligence_memory', {}).get('intelligence_files', []))}")

            logger.info("="*80)
            logger.info("✅ MEMORY RESTORATION VERIFIED")
            logger.info("="*80)

            return True

        except Exception as e:
            logger.error(f"❌ Error restoring memory: {e}")
            return False

    def verify_memory_integrity(self) -> Dict[str, Any]:
        """
        Verify memory integrity after warm recycle

        Returns:
            Integrity report
        """
        logger.info("="*80)
        logger.info("🔍 VERIFYING MEMORY INTEGRITY")
        logger.info("="*80)

        integrity_report = {
            "verified_at": datetime.now().isoformat(),
            "memory_sources_verified": 0,
            "memory_sources_missing": 0,
            "workflow_memory_verified": 0,
            "session_memory_verified": 0,
            "critical_files_verified": [],
            "warnings": []
        }

        # Check latest checkpoint
        latest_checkpoint = self.checkpoint_dir / "memory_checkpoint_latest.json"
        if latest_checkpoint.exists():
            try:
                with open(latest_checkpoint, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)

                # Verify memory sources
                for source in checkpoint.get("memory_sources", []):
                    source_path = self.project_root / source["path"]
                    if source_path.exists():
                        integrity_report["memory_sources_verified"] += 1
                    else:
                        integrity_report["memory_sources_missing"] += 1
                        integrity_report["warnings"].append(f"Missing memory source: {source['path']}")

                # Verify critical files
                critical_paths = [
                    "MASTER_TODO.md",
                    "data/ask_database/asks.json",
                    "data/memory"
                ]

                for critical_path in critical_paths:
                    critical_file = self.project_root / critical_path
                    if critical_file.exists():
                        integrity_report["critical_files_verified"].append(critical_path)
                    else:
                        integrity_report["warnings"].append(f"Critical file missing: {critical_path}")

            except Exception as e:
                integrity_report["warnings"].append(f"Error reading checkpoint: {e}")
        else:
            integrity_report["warnings"].append("No checkpoint found")

        logger.info(f"✅ Memory sources verified: {integrity_report['memory_sources_verified']}")
        logger.info(f"⚠️  Memory sources missing: {integrity_report['memory_sources_missing']}")
        logger.info(f"✅ Critical files verified: {len(integrity_report['critical_files_verified'])}")

        if integrity_report["warnings"]:
            logger.warning(f"⚠️  Warnings: {len(integrity_report['warnings'])}")
            for warning in integrity_report["warnings"]:
                logger.warning(f"   - {warning}")

        logger.info("="*80)
        logger.info("✅ MEMORY INTEGRITY VERIFICATION COMPLETE")
        logger.info("="*80)

        return integrity_report

def main():
    try:
        """Main execution"""
        preventer = MemoryDriftPreventer()

        import argparse
        parser = argparse.ArgumentParser(description="Prevent AI Memory Drift")
        parser.add_argument("--checkpoint", action="store_true", help="Create checkpoint before warm recycle")
        parser.add_argument("--restore", action="store_true", help="Restore memory after warm recycle")
        parser.add_argument("--verify", action="store_true", help="Verify memory integrity")
        parser.add_argument("--checkpoint-file", type=str, help="Specific checkpoint file to restore")

        args = parser.parse_args()

        if args.checkpoint:
            preventer.create_checkpoint_before_recycle()
        elif args.restore:
            checkpoint_file = Path(args.checkpoint_file) if args.checkpoint_file else None
            preventer.restore_memory_after_recycle(checkpoint_file)
        elif args.verify:
            preventer.verify_memory_integrity()
        else:
            # Default: create checkpoint
            logger.info("Creating checkpoint before warm recycle...")
            preventer.create_checkpoint_before_recycle()

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()