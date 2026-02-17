#!/usr/bin/env python3
"""
SYPHON Workflow Telemetry System
📊 TELEMETRY / OBSERVABILITY for ALL Workflows

Extracts, collects, and analyzes workflow data for:
- Metrics & Analytics
- Database Import
- Exponential/Sequential Improvement
- Infinite Dynamic Scaling

This is what Nate from YouTube called "Telemetry" or "Observability" - 
instrumenting all workflows to collect data for continuous improvement.

#SYPHON #TELEMETRY #OBSERVABILITY #WORKFLOWS #METRICS #ANALYTICS #DYNAMICSCALING
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SYPHONWorkflowTelemetry")

# Import SYPHON
try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.storage import SyphonStorage
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("SYPHON not available")

# Import workflow systems
try:
    from workflow_outcome_tracker import WorkflowOutcomeTracker, WorkflowOutcome
    WORKFLOW_TRACKER_AVAILABLE = True
except ImportError:
    WORKFLOW_TRACKER_AVAILABLE = False
    logger.warning("WorkflowOutcomeTracker not available")


class TelemetryEventType(Enum):
    """Types of telemetry events"""
    WORKFLOW_START = "workflow_start"
    WORKFLOW_END = "workflow_end"
    WORKFLOW_STEP = "workflow_step"
    WORKFLOW_ERROR = "workflow_error"
    WORKFLOW_METRIC = "workflow_metric"
    WORKFLOW_DECISION = "workflow_decision"
    WORKFLOW_OUTCOME = "workflow_outcome"


@dataclass
class WorkflowTelemetryEvent:
    """Telemetry event from workflow execution"""
    event_id: str
    event_type: TelemetryEventType
    workflow_id: str
    workflow_name: str
    execution_id: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class WorkflowTelemetryMetrics:
    """Aggregated metrics for a workflow"""
    workflow_id: str
    workflow_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration: float = 0.0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    success_rate: float = 0.0
    error_rate: float = 0.0
    last_execution: Optional[datetime] = None
    first_execution: Optional[datetime] = None
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.last_execution:
            data['last_execution'] = self.last_execution.isoformat()
        if self.first_execution:
            data['first_execution'] = self.first_execution.isoformat()
        return data


class SYPHONWorkflowTelemetrySystem:
    """
    SYPHON Workflow Telemetry System

    Collects telemetry/observability data from all workflows for:
    - Metrics & Analytics
    - Database Import
    - Exponential/Sequential Improvement
    - Infinite Dynamic Scaling
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON Workflow Telemetry System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SYPHONWorkflowTelemetry")

        # Initialize SYPHON
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True,
                    storage_backend="database"  # Use database for telemetry
                )
                self.syphon = SYPHONSystem(config)
                self.syphon_storage = SyphonStorage(config)
                logger.info("✅ SYPHON initialized for telemetry")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON initialization failed: {e}")
                self.syphon = None
                self.syphon_storage = None
        else:
            self.syphon = None
            self.syphon_storage = None

        # Initialize workflow tracker
        if WORKFLOW_TRACKER_AVAILABLE:
            try:
                self.workflow_tracker = WorkflowOutcomeTracker(self.project_root)
                logger.info("✅ WorkflowOutcomeTracker initialized")
            except Exception as e:
                logger.warning(f"⚠️  WorkflowOutcomeTracker initialization failed: {e}")
                self.workflow_tracker = None
        else:
            self.workflow_tracker = None

        # Telemetry storage
        self.telemetry_dir = self.project_root / "data" / "workflow_telemetry"
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)

        # Database for telemetry
        self.db_path = self.telemetry_dir / "workflow_telemetry.db"
        self._init_database()

        # Event buffer for batch processing
        self.event_buffer: List[WorkflowTelemetryEvent] = []
        self.buffer_size = 100

        logger.info("📊 SYPHON Workflow Telemetry System initialized")
        logger.info(f"   Database: {self.db_path}")

    def _init_database(self) -> None:
        """Initialize SQLite database for telemetry"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    execution_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT,  -- JSON
                    metrics TEXT,  -- JSON
                    tags TEXT,  -- JSON
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Metrics table (aggregated)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_metrics (
                    workflow_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    total_executions INTEGER DEFAULT 0,
                    successful_executions INTEGER DEFAULT 0,
                    failed_executions INTEGER DEFAULT 0,
                    average_duration REAL DEFAULT 0.0,
                    total_duration REAL DEFAULT 0.0,
                    min_duration REAL DEFAULT 0.0,
                    max_duration REAL DEFAULT 0.0,
                    success_rate REAL DEFAULT 0.0,
                    error_rate REAL DEFAULT 0.0,
                    last_execution TEXT,
                    first_execution TEXT,
                    custom_metrics TEXT,  -- JSON
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Workflow executions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    execution_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds REAL,
                    success INTEGER DEFAULT 0,
                    outcome_text TEXT,
                    metrics TEXT,  -- JSON
                    workflow_data TEXT,  -- JSON
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_workflow_id 
                ON telemetry_events(workflow_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_execution_id 
                ON telemetry_events(execution_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp 
                ON telemetry_events(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_executions_workflow_id 
                ON workflow_executions(workflow_id)
            """)

            conn.commit()
            conn.close()
            logger.info("✅ Telemetry database initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")

    def capture_event(self, 
                     event_type: TelemetryEventType,
                     workflow_id: str,
                     workflow_name: str,
                     execution_id: str,
                     data: Optional[Dict[str, Any]] = None,
                     metrics: Optional[Dict[str, float]] = None,
                     tags: Optional[List[str]] = None) -> WorkflowTelemetryEvent:
        """
        Capture a telemetry event

        Args:
            event_type: Type of event
            workflow_id: Workflow identifier
            workflow_name: Human-readable workflow name
            execution_id: Execution identifier
            data: Event data
            metrics: Event metrics
            tags: Event tags

        Returns:
            WorkflowTelemetryEvent
        """
        event = WorkflowTelemetryEvent(
            event_id=f"event_{datetime.now().timestamp()}_{len(self.event_buffer)}",
            event_type=event_type,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            execution_id=execution_id,
            timestamp=datetime.now(),
            data=data or {},
            metrics=metrics or {},
            tags=tags or []
        )

        # Add to buffer
        self.event_buffer.append(event)

        # Flush buffer if full
        if len(self.event_buffer) >= self.buffer_size:
            self.flush_events()

        # Also save immediately for critical events
        if event_type in [TelemetryEventType.WORKFLOW_ERROR, TelemetryEventType.WORKFLOW_OUTCOME]:
            self._save_event_to_db(event)

        return event

    def flush_events(self) -> int:
        """Flush event buffer to database"""
        if not self.event_buffer:
            return 0

        count = 0
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            for event in self.event_buffer:
                self._save_event_to_db(event, cursor=cursor)
                count += 1

            conn.commit()
            conn.close()

            self.event_buffer.clear()
            logger.debug(f"✅ Flushed {count} events to database")
        except Exception as e:
            logger.error(f"❌ Error flushing events: {e}")

        return count

    def _save_event_to_db(self, event: WorkflowTelemetryEvent, cursor: Optional[sqlite3.Cursor] = None) -> None:
        """Save event to database"""
        close_conn = False
        if cursor is None:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            close_conn = True

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO telemetry_events 
                (event_id, event_type, workflow_id, workflow_name, execution_id, 
                 timestamp, data, metrics, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.event_type.value,
                event.workflow_id,
                event.workflow_name,
                event.execution_id,
                event.timestamp.isoformat(),
                json.dumps(event.data),
                json.dumps(event.metrics),
                json.dumps(event.tags)
            ))

            if close_conn:
                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"❌ Error saving event to database: {e}")
            if close_conn:
                conn.close()

    def track_workflow_execution(self,
                                workflow_id: str,
                                workflow_name: str,
                                execution_id: str,
                                started_at: datetime,
                                ended_at: Optional[datetime] = None,
                                success: bool = False,
                                outcome_text: str = "",
                                metrics: Optional[Dict[str, float]] = None,
                                workflow_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a complete workflow execution

        Args:
            workflow_id: Workflow identifier
            workflow_name: Human-readable workflow name
            execution_id: Execution identifier
            started_at: Start timestamp
            ended_at: End timestamp (optional)
            success: Whether execution succeeded
            outcome_text: Outcome description
            metrics: Execution metrics
            workflow_data: Full workflow execution data
        """
        # Capture start event
        self.capture_event(
            event_type=TelemetryEventType.WORKFLOW_START,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            execution_id=execution_id,
            data={"started_at": started_at.isoformat()},
            tags=["execution_start"]
        )

        # Calculate duration
        duration = 0.0
        if ended_at:
            duration = (ended_at - started_at).total_seconds()

        # Save execution to database
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO workflow_executions
                (execution_id, workflow_id, workflow_name, started_at, ended_at,
                 duration_seconds, success, outcome_text, metrics, workflow_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution_id,
                workflow_id,
                workflow_name,
                started_at.isoformat(),
                ended_at.isoformat() if ended_at else None,
                duration,
                1 if success else 0,
                outcome_text,
                json.dumps(metrics or {}),
                json.dumps(workflow_data or {})
            ))

            conn.commit()
            conn.close()

            # Update aggregated metrics
            self._update_workflow_metrics(workflow_id, workflow_name, duration, success)

            # Capture end event
            if ended_at:
                self.capture_event(
                    event_type=TelemetryEventType.WORKFLOW_END,
                    workflow_id=workflow_id,
                    workflow_name=workflow_name,
                    execution_id=execution_id,
                    data={"ended_at": ended_at.isoformat(), "duration": duration},
                    metrics=metrics or {},
                    tags=["execution_end", "success" if success else "failure"]
                )

            # Integrate with workflow tracker
            if self.workflow_tracker:
                try:
                    self.workflow_tracker.track_outcome(
                        workflow_name=workflow_name,
                        execution_id=execution_id,
                        success=success,
                        outcome_text=outcome_text,
                        metrics=metrics,
                        duration_seconds=duration,
                        workflow_data=workflow_data
                    )
                except Exception as e:
                    logger.warning(f"Could not track outcome: {e}")

            # SYPHON workflow data for intelligence extraction
            if self.syphon and workflow_data:
                try:
                    self._syphon_workflow_data(workflow_id, workflow_name, workflow_data)
                except Exception as e:
                    logger.warning(f"Could not syphon workflow data: {e}")

        except Exception as e:
            logger.error(f"❌ Error tracking workflow execution: {e}")

    def _update_workflow_metrics(self, workflow_id: str, workflow_name: str, 
                                 duration: float, success: bool) -> None:
        """Update aggregated workflow metrics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Get current metrics
            cursor.execute("""
                SELECT total_executions, successful_executions, failed_executions,
                       total_duration, min_duration, max_duration, first_execution
                FROM workflow_metrics
                WHERE workflow_id = ?
            """, (workflow_id,))

            row = cursor.fetchone()

            if row:
                total_exec, success_exec, failed_exec, total_dur, min_dur, max_dur, first_exec = row
                total_exec += 1
                if success:
                    success_exec += 1
                else:
                    failed_exec += 1
                total_dur += duration
                min_dur = min(min_dur, duration) if min_dur else duration
                max_dur = max(max_dur, duration) if max_dur else duration
            else:
                total_exec = 1
                success_exec = 1 if success else 0
                failed_exec = 0 if success else 1
                total_dur = duration
                min_dur = duration
                max_dur = duration
                first_exec = datetime.now().isoformat()

            avg_duration = total_dur / total_exec if total_exec > 0 else 0.0
            success_rate = (success_exec / total_exec * 100) if total_exec > 0 else 0.0
            error_rate = (failed_exec / total_exec * 100) if total_exec > 0 else 0.0

            cursor.execute("""
                INSERT OR REPLACE INTO workflow_metrics
                (workflow_id, workflow_name, total_executions, successful_executions,
                 failed_executions, average_duration, total_duration, min_duration,
                 max_duration, success_rate, error_rate, last_execution, first_execution)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow_id,
                workflow_name,
                total_exec,
                success_exec,
                failed_exec,
                avg_duration,
                total_dur,
                min_dur,
                max_dur,
                success_rate,
                error_rate,
                datetime.now().isoformat(),
                first_exec
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error updating workflow metrics: {e}")

    def _syphon_workflow_data(self, workflow_id: str, workflow_name: str, 
                              workflow_data: Dict[str, Any]) -> None:
        """Use SYPHON to extract intelligence from workflow data"""
        if not self.syphon:
            return

        try:
            # Convert workflow data to text for SYPHON extraction
            workflow_text = json.dumps(workflow_data, indent=2)

            # Extract actionable items, tasks, decisions, intelligence
            # Use SYPHON extractors if available
            actionable_items = []
            tasks = []
            decisions = []
            intelligence = {}

            # Try to extract using available methods
            try:
                # Use extractors if available
                if hasattr(self.syphon, 'extractors'):
                    # Try email extractor as generic extractor
                    for extractor_type, extractor in self.syphon.extractors.items():
                        if hasattr(extractor, 'extract_actionable_items'):
                            actionable_items = extractor.extract_actionable_items(workflow_text)
                            break
            except Exception:
                pass

            # Store extracted intelligence
            if self.syphon_storage:
                syphon_data = {
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_name,
                    "actionable_items": actionable_items,
                    "tasks": tasks,
                    "decisions": decisions,
                    "intelligence": intelligence,
                    "extracted_at": datetime.now().isoformat()
                }

                # Save to SYPHON storage
                self.syphon_storage.save_extracted_data(syphon_data)

            logger.debug(f"✅ SYPHON extracted intelligence from {workflow_name}")
        except Exception as e:
            logger.warning(f"⚠️  SYPHON extraction failed: {e}")

    def get_workflow_metrics(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get workflow metrics

        Args:
            workflow_id: Specific workflow ID, or None for all workflows

        Returns:
            Dict with workflow metrics
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            if workflow_id:
                cursor.execute("""
                    SELECT * FROM workflow_metrics WHERE workflow_id = ?
                """, (workflow_id,))
                row = cursor.fetchone()

                if row:
                    columns = [desc[0] for desc in cursor.description]
                    metrics = dict(zip(columns, row))
                    custom_metrics_str = metrics.get('custom_metrics')
                    if custom_metrics_str:
                        try:
                            metrics['custom_metrics'] = json.loads(custom_metrics_str)
                        except:
                            metrics['custom_metrics'] = {}
                    else:
                        metrics['custom_metrics'] = {}
                    return {"success": True, "metrics": metrics}
                else:
                    return {"success": False, "error": "Workflow not found"}
            else:
                cursor.execute("SELECT * FROM workflow_metrics")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                metrics_list = []
                for row in rows:
                    metrics = dict(zip(columns, row))
                    custom_metrics_str = metrics.get('custom_metrics')
                    if custom_metrics_str:
                        try:
                            metrics['custom_metrics'] = json.loads(custom_metrics_str)
                        except:
                            metrics['custom_metrics'] = {}
                    else:
                        metrics['custom_metrics'] = {}
                    metrics_list.append(metrics)

                return {"success": True, "metrics": metrics_list}
        except Exception as e:
            logger.error(f"❌ Error getting workflow metrics: {e}")
            return {"success": False, "error": str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def export_to_database(self, target_db_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Export telemetry data to external database

        Args:
            target_db_path: Path to target database (optional)

        Returns:
            Export result
        """
        # This would export to external database (PostgreSQL, MySQL, etc.)
        # For now, return summary
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Get counts
            cursor.execute("SELECT COUNT(*) FROM telemetry_events")
            event_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM workflow_executions")
            execution_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM workflow_metrics")
            metrics_count = cursor.fetchone()[0]

            conn.close()

            return {
                "success": True,
                "exported": {
                    "events": event_count,
                    "executions": execution_count,
                    "metrics": metrics_count
                },
                "message": "Telemetry data ready for export"
            }
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            return {"success": False, "error": str(e)}


# Global instance
_global_telemetry: Optional[SYPHONWorkflowTelemetrySystem] = None

def get_telemetry_system(project_root: Optional[Path] = None) -> SYPHONWorkflowTelemetrySystem:
    """Get or create global telemetry system instance"""
    global _global_telemetry
    if _global_telemetry is None:
        _global_telemetry = SYPHONWorkflowTelemetrySystem(project_root)
    return _global_telemetry


def main():
    try:
        """CLI interface for SYPHON Workflow Telemetry System"""
        import argparse

        parser = argparse.ArgumentParser(description="SYPHON Workflow Telemetry System")
        parser.add_argument("--metrics", help="Get metrics for workflow ID")
        parser.add_argument("--export", action="store_true", help="Export telemetry data")
        parser.add_argument("--flush", action="store_true", help="Flush event buffer")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        telemetry = get_telemetry_system()

        if args.flush:
            count = telemetry.flush_events()
            print(f"✅ Flushed {count} events to database")
            return

        if args.metrics:
            result = telemetry.get_workflow_metrics(args.metrics)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result.get("success"):
                    metrics = result.get("metrics", {})
                    print(f"\n📊 Metrics for {args.metrics}")
                    print("="*70)
                    print(f"Total Executions: {metrics.get('total_executions', 0)}")
                    print(f"Success Rate: {metrics.get('success_rate', 0):.2f}%")
                    print(f"Average Duration: {metrics.get('average_duration', 0):.2f}s")
                    print(f"Min Duration: {metrics.get('min_duration', 0):.2f}s")
                    print(f"Max Duration: {metrics.get('max_duration', 0):.2f}s")
                else:
                    print(f"❌ Error: {result.get('error')}")
            return

        if args.export:
            result = telemetry.export_to_database()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result.get("success"):
                    exported = result.get("exported", {})
                    print(f"\n📤 Export Summary")
                    print("="*70)
                    print(f"Events: {exported.get('events', 0)}")
                    print(f"Executions: {exported.get('executions', 0)}")
                    print(f"Metrics: {exported.get('metrics', 0)}")
                else:
                    print(f"❌ Error: {result.get('error')}")
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()