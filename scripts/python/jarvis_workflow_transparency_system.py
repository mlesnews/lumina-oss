#!/usr/bin/env python3
"""
JARVIS Workflow Transparency System

Provides comprehensive visibility into workflow progress across the entire environment:
- Real-time workflow status
- Progress tracking
- Health monitoring
- Performance metrics
- Historical trends
- Alert system
- Centralized dashboard
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWorkflowTransparency")


@dataclass
class WorkflowStatus:
    """Workflow status information"""
    workflow_id: str
    workflow_name: str
    status: str  # pending, running, completed, failed, paused
    priority: str
    category: str
    progress: float  # 0.0 to 1.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    steps_total: int = 0
    steps_completed: int = 0
    steps_failed: int = 0
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data


class JARVISWorkflowTransparencySystem:
    """
    Comprehensive workflow transparency system
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Directories
        self.data_dir = project_root / "data" / "workflow_transparency"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.workflow_logs_dir = project_root / "data" / "workflow_logs"
        self.workflow_logs_dir.mkdir(parents=True, exist_ok=True)

        self.action_plans_dir = project_root / "data" / "action_plans"
        self.workflows_dir = project_root / "data" / "workflows"

        # Database for tracking
        self.db_path = self.data_dir / "workflow_transparency.db"
        self._init_database()

        # In-memory cache
        self.workflow_cache: Dict[str, WorkflowStatus] = {}
        self.last_update = None

    def _init_database(self):
        try:
            """Initialize SQLite database for workflow tracking"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Workflow status table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_status (
                    workflow_id TEXT PRIMARY KEY,
                    workflow_name TEXT,
                    status TEXT,
                    priority TEXT,
                    category TEXT,
                    progress REAL,
                    started_at TEXT,
                    completed_at TEXT,
                    duration REAL,
                    steps_total INTEGER,
                    steps_completed INTEGER,
                    steps_failed INTEGER,
                    current_step TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    updated_at TEXT
                )
            """)

            # Workflow history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT,
                    timestamp TEXT,
                    status TEXT,
                    progress REAL,
                    step_name TEXT,
                    message TEXT,
                    metadata TEXT
                )
            """)

            # Workflow metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    timestamp TEXT
                )
            """)

            conn.commit()
            conn.close()
            self.logger.info(f"✅ Database initialized: {self.db_path}")

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def scan_all_workflows(self) -> Dict[str, WorkflowStatus]:
        """Scan all workflow sources and build status map"""
        workflows: Dict[str, WorkflowStatus] = {}

        # 1. Scan workflow logs
        self.logger.info("Scanning workflow logs...")
        if self.workflow_logs_dir.exists():
            for log_file in self.workflow_logs_dir.glob("workflow_execution_*.json"):
                try:
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)

                    workflow_id = log_data.get('workflow_id', log_file.stem)
                    workflow_name = log_data.get('workflow_name', 'Unknown Workflow')

                    status = WorkflowStatus(
                        workflow_id=workflow_id,
                        workflow_name=workflow_name,
                        status=log_data.get('status', 'unknown'),
                        priority=log_data.get('priority', 'medium'),
                        category=log_data.get('category', 'general'),
                        progress=log_data.get('progress', 0.0),
                        started_at=datetime.fromisoformat(log_data['started_at']) if log_data.get('started_at') else None,
                        completed_at=datetime.fromisoformat(log_data['completed_at']) if log_data.get('completed_at') else None,
                        duration=log_data.get('duration'),
                        steps_total=log_data.get('steps_total', 0),
                        steps_completed=log_data.get('steps_completed', 0),
                        steps_failed=log_data.get('steps_failed', 0),
                        current_step=log_data.get('current_step'),
                        error_message=log_data.get('error_message'),
                        metadata=log_data.get('metadata', {})
                    )

                    workflows[workflow_id] = status
                except Exception as e:
                    self.logger.error(f"Error reading log file {log_file}: {e}")

        # 2. Scan action plans
        self.logger.info("Scanning action plans...")
        if self.action_plans_dir.exists():
            for plan_file in self.action_plans_dir.glob("jarvis_action_plan_*.json"):
                try:
                    with open(plan_file, 'r') as f:
                        plan_data = json.load(f)

                    plan_id = f"action_plan_{plan_file.stem}"
                    steps = plan_data.get('steps', [])
                    completed_steps = [s for s in steps if s.get('status') == 'completed']

                    workflows[plan_id] = WorkflowStatus(
                        workflow_id=plan_id,
                        workflow_name=plan_data.get('title', 'Action Plan'),
                        status='running' if len(completed_steps) < len(steps) else 'completed',
                        priority=plan_data.get('priority', 'medium'),
                        category='action_plan',
                        progress=len(completed_steps) / len(steps) if steps else 0.0,
                        steps_total=len(steps),
                        steps_completed=len(completed_steps),
                        steps_failed=len([s for s in steps if s.get('status') == 'failed']),
                        metadata={'plan_file': str(plan_file)}
                    )
                except Exception as e:
                    self.logger.error(f"Error reading plan file {plan_file}: {e}")

        # 3. Scan workflow definitions
        self.logger.info("Scanning workflow definitions...")
        if self.workflows_dir.exists():
            for workflow_file in self.workflows_dir.glob("*.json"):
                try:
                    with open(workflow_file, 'r') as f:
                        workflow_data = json.load(f)

                    # Handle different workflow formats
                    if isinstance(workflow_data, list):
                        for wf in workflow_data:
                            wf_id = wf.get('id', f"workflow_{workflow_file.stem}_{len(workflows)}")
                            workflows[wf_id] = WorkflowStatus(
                                workflow_id=wf_id,
                                workflow_name=wf.get('name', 'Unknown'),
                                status=wf.get('status', 'pending'),
                                priority=wf.get('priority', 'medium'),
                                category=wf.get('category', 'general'),
                                progress=wf.get('progress', 0.0),
                                metadata=wf
                            )
                    elif isinstance(workflow_data, dict):
                        wf_id = workflow_data.get('id', f"workflow_{workflow_file.stem}")
                        workflows[wf_id] = WorkflowStatus(
                            workflow_id=wf_id,
                            workflow_name=workflow_data.get('name', 'Unknown'),
                            status=workflow_data.get('status', 'pending'),
                            priority=workflow_data.get('priority', 'medium'),
                            category=workflow_data.get('category', 'general'),
                            progress=workflow_data.get('progress', 0.0),
                            metadata=workflow_data
                        )
                except Exception as e:
                    self.logger.error(f"Error reading workflow file {workflow_file}: {e}")

        # 4. Check for active processes
        self.logger.info("Checking for active workflow processes...")
        workflows.update(self._detect_active_processes())

        self.workflow_cache = workflows
        self.last_update = datetime.now()

        self.logger.info(f"✅ Scanned {len(workflows)} workflows")
        return workflows

    def _detect_active_processes(self) -> Dict[str, WorkflowStatus]:
        """Detect actively running workflow processes"""
        active_workflows = {}

        # Check for running Python processes that might be workflows
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('workflow' in str(arg).lower() for arg in cmdline):
                        # Extract workflow info from command line
                        workflow_id = f"process_{proc.info['pid']}"
                        active_workflows[workflow_id] = WorkflowStatus(
                            workflow_id=workflow_id,
                            workflow_name=' '.join(cmdline[-2:]) if len(cmdline) > 1 else 'Running Workflow',
                            status='running',
                            priority='medium',
                            category='process',
                            progress=0.5,  # Unknown progress
                            started_at=datetime.fromtimestamp(proc.info['create_time']),
                            metadata={'pid': proc.info['pid'], 'cmdline': cmdline}
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            self.logger.warning("psutil not available, skipping process detection")

        return active_workflows

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        workflows = self.scan_all_workflows()

        # Calculate statistics
        by_status = defaultdict(int)
        by_priority = defaultdict(int)
        by_category = defaultdict(int)
        total_progress = 0.0
        active_count = 0

        for wf in workflows.values():
            by_status[wf.status] += 1
            by_priority[wf.priority] += 1
            by_category[wf.category] += 1
            total_progress += wf.progress
            if wf.status == 'running':
                active_count += 1

        avg_progress = total_progress / len(workflows) if workflows else 0.0

        return {
            'total_workflows': len(workflows),
            'active_workflows': active_count,
            'by_status': dict(by_status),
            'by_priority': dict(by_priority),
            'by_category': dict(by_category),
            'average_progress': avg_progress,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'workflows': {wf_id: wf.to_dict() for wf_id, wf in workflows.items()}
        }

    def generate_dashboard(self) -> str:
        """Generate HTML dashboard"""
        summary = self.get_workflow_summary()
        workflows = summary['workflows']

        # Sort workflows by priority and status
        sorted_workflows = sorted(
            workflows.values(),
            key=lambda w: (
                {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(w.get('priority', 'medium'), 99),
                {'running': 0, 'pending': 1, 'failed': 2, 'completed': 3, 'paused': 4}.get(w.get('status', 'unknown'), 99)
            )
        )

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>JARVIS Workflow Transparency Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #e0e0e0;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            margin: 0;
            color: white;
            font-size: 2.5em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #e0e0e0;
        }}
        .workflow-list {{
            display: grid;
            gap: 15px;
        }}
        .workflow-card {{
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .workflow-card.running {{ border-color: #4CAF50; }}
        .workflow-card.completed {{ border-color: #2196F3; }}
        .workflow-card.failed {{ border-color: #f44336; }}
        .workflow-card.pending {{ border-color: #FF9800; }}
        .workflow-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .workflow-name {{
            font-size: 1.2em;
            font-weight: bold;
            color: #e0e0e0;
        }}
        .workflow-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-running {{ background: #4CAF50; color: white; }}
        .status-completed {{ background: #2196F3; color: white; }}
        .status-failed {{ background: #f44336; color: white; }}
        .status-pending {{ background: #FF9800; color: white; }}
        .progress-bar {{
            width: 100%;
            height: 25px;
            background: #2a2a2a;
            border-radius: 12px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .workflow-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 15px;
            font-size: 0.9em;
            color: #b0b0b0;
        }}
        .detail-item {{
            display: flex;
            justify-content: space-between;
        }}
        .detail-label {{
            color: #888;
        }}
        .detail-value {{
            color: #e0e0e0;
            font-weight: bold;
        }}
        .timestamp {{
            color: #888;
            font-size: 0.8em;
            text-align: right;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔄 JARVIS Workflow Transparency Dashboard</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Real-time workflow progress across the entire environment</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>Total Workflows</h3>
            <div class="value">{summary['total_workflows']}</div>
        </div>
        <div class="stat-card">
            <h3>Active Workflows</h3>
            <div class="value">{summary['active_workflows']}</div>
        </div>
        <div class="stat-card">
            <h3>Average Progress</h3>
            <div class="value">{summary['average_progress']:.1%}</div>
        </div>
        <div class="stat-card">
            <h3>Completed</h3>
            <div class="value">{summary['by_status'].get('completed', 0)}</div>
        </div>
        <div class="stat-card">
            <h3>Failed</h3>
            <div class="value">{summary['by_status'].get('failed', 0)}</div>
        </div>
        <div class="stat-card">
            <h3>Pending</h3>
            <div class="value">{summary['by_status'].get('pending', 0)}</div>
        </div>
    </div>

    <div class="workflow-list">
"""

        for wf in sorted_workflows:
            status_class = wf.get('status', 'pending')
            progress_pct = wf.get('progress', 0.0) * 100

            html += f"""
        <div class="workflow-card {status_class}">
            <div class="workflow-header">
                <div class="workflow-name">{wf.get('workflow_name', 'Unknown Workflow')}</div>
                <div class="workflow-status status-{status_class}">{status_class}</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_pct}%">{progress_pct:.1f}%</div>
            </div>
            <div class="workflow-details">
                <div class="detail-item">
                    <span class="detail-label">Priority:</span>
                    <span class="detail-value">{wf.get('priority', 'medium').upper()}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Category:</span>
                    <span class="detail-value">{wf.get('category', 'general')}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Steps:</span>
                    <span class="detail-value">{wf.get('steps_completed', 0)}/{wf.get('steps_total', 0)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Duration:</span>
                    <span class="detail-value">{wf.get('duration') or 0:.1f}s</span>
                </div>
"""

            current_step = wf.get('current_step')
            if current_step:
                html += f"""
                <div class="detail-item">
                    <span class="detail-label">Current Step:</span>
                    <span class="detail-value">{str(current_step)}</span>
                </div>
"""

            error_message = wf.get('error_message')
            if error_message:
                html += f"""
                <div class="detail-item" style="grid-column: 1 / -1;">
                    <span class="detail-label">Error:</span>
                    <span class="detail-value" style="color: #f44336;">{str(error_message)}</span>
                </div>
"""

            html += """
            </div>
        </div>
"""

        html += f"""
    </div>

    <div class="timestamp">
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</body>
</html>
"""

        return html

    def save_dashboard(self) -> Path:
        try:
            """Save dashboard HTML file"""
            dashboard_html = self.generate_dashboard()
            dashboard_file = self.project_root / "WORKFLOW_TRANSPARENCY_DASHBOARD.html"
            dashboard_file.write_text(dashboard_html, encoding='utf-8')
            self.logger.info(f"✅ Dashboard saved: {dashboard_file}")
            return dashboard_file

        except Exception as e:
            self.logger.error(f"Error in save_dashboard: {e}", exc_info=True)
            raise
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        summary = self.get_workflow_summary()

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_workflows': summary['total_workflows'],
                'active_workflows': summary['active_workflows'],
                'average_progress': summary['average_progress'],
                'by_status': summary['by_status'],
                'by_priority': summary['by_priority'],
                'by_category': summary['by_category']
            },
            'workflows': summary['workflows'],
            'alerts': self._generate_alerts(summary),
            'recommendations': self._generate_recommendations(summary)
        }

        return report

    def _generate_alerts(self, summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on workflow status"""
        alerts = []

        # Check for failed workflows
        failed_count = summary['by_status'].get('failed', 0)
        if failed_count > 0:
            alerts.append({
                'level': 'error',
                'message': f'{failed_count} workflow(s) have failed',
                'action': 'Review failed workflows and fix issues'
            })

        # Check for stuck workflows
        running_workflows = [w for w in summary['workflows'].values() 
                           if w.get('status') == 'running']
        for wf in running_workflows:
            duration = wf.get('duration')
            if duration and duration > 3600:  # Running for more than 1 hour
                alerts.append({
                    'level': 'warning',
                    'message': f"Workflow '{wf.get('workflow_name')}' has been running for {duration/3600:.1f} hours",
                    'action': 'Check if workflow is stuck or needs intervention'
                })

        # Check for low progress
        if summary['average_progress'] < 0.1 and summary['active_workflows'] > 0:
            alerts.append({
                'level': 'info',
                'message': 'Average workflow progress is low',
                'action': 'Review workflow execution and identify bottlenecks'
            })

        return alerts

    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations for workflow optimization"""
        recommendations = []

        # Check priority distribution
        critical_count = summary['by_priority'].get('critical', 0)
        if critical_count > 5:
            recommendations.append("Consider prioritizing critical workflows - too many critical items may indicate planning issues")

        # Check category distribution
        if len(summary['by_category']) > 10:
            recommendations.append("Workflows are spread across many categories - consider consolidation")

        # Check for pending workflows
        pending_count = summary['by_status'].get('pending', 0)
        if pending_count > summary['active_workflows']:
            recommendations.append("Many workflows are pending - consider starting more workflows in parallel")

        return recommendations


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Workflow Transparency System")
    parser.add_argument("--dashboard", action="store_true", help="Generate HTML dashboard")
    parser.add_argument("--report", action="store_true", help="Generate status report")
    parser.add_argument("--scan", action="store_true", help="Scan all workflows")
    parser.add_argument("--watch", action="store_true", help="Watch mode (continuous updates)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    transparency = JARVISWorkflowTransparencySystem(project_root)

    if args.dashboard or not args:
        dashboard_file = transparency.save_dashboard()
        print(f"\n✅ Dashboard generated: {dashboard_file}")
        print(f"   Open in browser: file:///{dashboard_file.as_uri().replace('file:///', '')}")

    if args.report:
        report = transparency.generate_status_report()
        report_file = project_root / "data" / "workflow_transparency" / f"status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✅ Status report saved: {report_file}")

    if args.scan:
        workflows = transparency.scan_all_workflows()
        print(f"\n✅ Scanned {len(workflows)} workflows")
        for wf_id, wf in workflows.items():
            print(f"   {wf.workflow_name}: {wf.status} ({wf.progress:.1%})")

    if args.watch:
        import time
        print("\n🔄 Watching workflows (Ctrl+C to stop)...")
        try:
            while True:
                transparency.save_dashboard()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Dashboard updated")
                time.sleep(30)  # Update every 30 seconds
        except KeyboardInterrupt:
            print("\n🛑 Stopped watching")


if __name__ == "__main__":


    main()