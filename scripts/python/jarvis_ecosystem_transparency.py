#!/usr/bin/env python3
"""
JARVIS Ecosystem Transparency Dashboard

Provides comprehensive transparency on:
- Workflow progress across entire environment
- Integration percentages (major/minor actors)
- Job slot roles and responsibilities
- IDE and browser utilization
- Virtual assistant notifications
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEcosystemTransparency")


@dataclass
class ActorStatus:
    """Status of an actor in the ecosystem"""
    name: str
    role: str
    status: str  # "active", "inactive", "partial", "missing"
    integration_percent: float
    responsibilities: List[str]
    last_active: Optional[str] = None
    utilization: float = 0.0


@dataclass
class WorkflowProgress:
    """Progress of a workflow"""
    workflow_id: str
    name: str
    status: str  # "complete", "in_progress", "pending", "failed"
    progress_percent: float
    steps_complete: int
    steps_total: int
    actors_involved: List[str]
    last_update: str


class JARVISEcosystemTransparency:
    """
    Comprehensive ecosystem transparency system
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.data_dir = project_root / "data" / "ecosystem_transparency"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load job slots
        self.job_slots = self._load_job_slots()
        self.actors = self._discover_actors()
        self.workflows = self._discover_workflows()

    def _load_job_slots(self) -> Dict[str, Any]:
        try:
            """Load job slot definitions"""
            job_slot_file = self.project_root / "data" / "jarvis_job_slots" / "job_slot_research.json"
            if job_slot_file.exists():
                with open(job_slot_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_job_slots: {e}", exc_info=True)
            raise
    def _discover_actors(self) -> List[ActorStatus]:
        try:
            """Discover all actors in the ecosystem"""
            actors = []

            # Major Actors (Core Systems)
            major_actors = [
                {
                    "name": "JARVIS",
                    "role": "Full-Time Super Agent",
                    "script": "jarvis_fulltime_super_agent.py",
                    "responsibilities": [
                        "Direct voice conversations",
                        "IDE control",
                        "Workflow orchestration",
                        "Memory management",
                        "Health monitoring"
                    ]
                },
                {
                    "name": "MARVIN",
                    "role": "Reality Check & Roast System",
                    "script": "jarvis_marvin_roast_system.py",
                    "responsibilities": [
                        "Critical analysis",
                        "Reality checks",
                        "Debate counterpoints",
                        "Generate next steps"
                    ]
                },
                {
                    "name": "MANUS",
                    "role": "Unified Control System",
                    "script": "manus_unified_control.py",
                    "responsibilities": [
                        "IDE control",
                        "Workstation control",
                        "Home lab control",
                        "Automation control",
                        "Neo browser control"
                    ]
                },
                {
                    "name": "R5 Living Context Matrix",
                    "role": "Long-Term Memory System",
                    "script": "r5_living_context_matrix.py",
                    "responsibilities": [
                        "Session aggregation",
                        "Long-term knowledge",
                        "Context preservation"
                    ]
                },
                {
                    "name": "Windows Systems Engineer",
                    "role": "PC Health Management",
                    "script": "jarvis_windows_systems_engineer.py",
                    "responsibilities": [
                        "PC hardware monitoring",
                        "OS health",
                        "Application health",
                        "Log parsing/tailing"
                    ]
                },
                {
                    "name": "Systems Disaster Recovery Engineer",
                    "role": "Code Quality & Standards",
                    "script": "jarvis_systems_disaster_recovery_engineer.py",
                    "responsibilities": [
                        "Duplicate code detection",
                        "IT standards enforcement",
                        "Data management",
                        "Conflict prevention"
                    ]
                },
                {
                    "name": "Physician, Heal Thyself",
                    "role": "Self-Healing System",
                    "script": "jarvis_physician_heal_thyself.py",
                    "responsibilities": [
                        "Self-diagnosis",
                        "Healing plan creation",
                        "Ethical execution",
                        "Hippocratic Oath principles"
                    ]
                }
            ]

            # Check each major actor
            for actor_def in major_actors:
                script_path = self.project_root / "scripts" / "python" / actor_def["script"]
                exists = script_path.exists()

                # Check if integrated
                integration_percent = self._calculate_integration(actor_def["name"], exists)

                actors.append(ActorStatus(
                    name=actor_def["name"],
                    role=actor_def["role"],
                    status="active" if exists and integration_percent > 80 else "partial" if exists else "missing",
                    integration_percent=integration_percent,
                    responsibilities=actor_def["responsibilities"],
                    last_active=self._get_last_active(actor_def["name"]),
                    utilization=self._calculate_utilization(actor_def["name"])
                ))

            # Minor Actors (Subsystems)
            minor_actors = [
                {
                    "name": "Auto-Accept Monitor",
                    "role": "Dialog Automation",
                    "script": "jarvis_auto_accept_monitor.py"
                },
                {
                    "name": "Summary Reader",
                    "role": "Voice Summary",
                    "script": "jarvis_summary_reader.py"
                },
                {
                    "name": "Persistent Memory",
                    "role": "Memory Management",
                    "script": "jarvis_persistent_memory.py"
                },
                {
                    "name": "Auto Git Manager",
                    "role": "Git Automation",
                    "script": "jarvis_auto_git_manager.py"
                },
                {
                    "name": "Validation Suite",
                    "role": "Code Validation",
                    "script": "jarvis_validation_suite.py"
                },
                {
                    "name": "Illumination Teacher",
                    "role": "Teaching System",
                    "script": "jarvis_illumination_teacher.py"
                },
                {
                    "name": "Storytelling Coach",
                    "role": "Storytelling",
                    "script": "lumina_storytelling_coach.py"
                },
                {
                    "name": "Innovation Coach",
                    "role": "Innovation",
                    "script": "lumina_innovation_coach.py"
                }
            ]

            for actor_def in minor_actors:
                script_path = self.project_root / "scripts" / "python" / actor_def["script"]
                exists = script_path.exists()
                integration_percent = self._calculate_integration(actor_def["name"], exists)

                actors.append(ActorStatus(
                    name=actor_def["name"],
                    role=actor_def["role"],
                    status="active" if exists and integration_percent > 50 else "partial" if exists else "missing",
                    integration_percent=integration_percent,
                    responsibilities=[actor_def.get("responsibilities", [actor_def["role"]])],
                    last_active=self._get_last_active(actor_def["name"]),
                    utilization=self._calculate_utilization(actor_def["name"])
                ))

            return actors

        except Exception as e:
            self.logger.error(f"Error in _discover_actors: {e}", exc_info=True)
            raise
    def _calculate_integration(self, actor_name: str, exists: bool) -> float:
        try:
            """Calculate integration percentage for an actor"""
            if not exists:
                return 0.0

            # Check if imported/used in other systems
            integration_score = 0.0

            # Check main JARVIS integration
            jarvis_file = self.project_root / "scripts" / "python" / "jarvis_fulltime_super_agent.py"
            if jarvis_file.exists():
                content = jarvis_file.read_text(encoding='utf-8')
                if actor_name.lower().replace(" ", "_") in content.lower():
                    integration_score += 30.0

            # Check if has active status file
            status_files = [
                f"{actor_name.upper().replace(' ', '_')}_ACTIVE.md",
                f"{actor_name.upper().replace(' ', '_')}_READY.md"
            ]
            for status_file in status_files:
                if (self.project_root / status_file).exists():
                    integration_score += 20.0
                    break

            # Check if has documentation
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                for doc_file in docs_dir.rglob(f"*{actor_name.replace(' ', '_')}*.md"):
                    integration_score += 10.0
                    break

            # Check if has data/logs
            data_dirs = [
                self.project_root / "data" / actor_name.lower().replace(" ", "_"),
                self.project_root / "data" / "logs" / actor_name.lower().replace(" ", "_")
            ]
            for data_dir in data_dirs:
                if data_dir.exists() and any(data_dir.iterdir()):
                    integration_score += 20.0
                    break

            # Check if has config
            config_files = [
                self.project_root / "config" / f"{actor_name.lower().replace(' ', '_')}_config.json"
            ]
            for config_file in config_files:
                if config_file.exists():
                    integration_score += 20.0
                    break

            return min(100.0, integration_score)

        except Exception as e:
            self.logger.error(f"Error in _calculate_integration: {e}", exc_info=True)
            raise
    def _get_last_active(self, actor_name: str) -> Optional[str]:
        try:
            """Get last active timestamp for an actor"""
            # Check logs
            log_dirs = [
                self.project_root / "data" / "logs",
                self.project_root / "data" / actor_name.lower().replace(" ", "_") / "logs"
            ]

            for log_dir in log_dirs:
                if log_dir.exists():
                    log_files = sorted(log_dir.rglob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
                    if log_files:
                        return datetime.fromtimestamp(log_files[0].stat().st_mtime).isoformat()

            return None

        except Exception as e:
            self.logger.error(f"Error in _get_last_active: {e}", exc_info=True)
            raise
    def _calculate_utilization(self, actor_name: str) -> float:
        """Calculate utilization percentage"""
        # Simple heuristic based on log activity
        log_dirs = [
            self.project_root / "data" / "logs",
            self.project_root / "data" / actor_name.lower().replace(" ", "_") / "logs"
        ]

        for log_dir in log_dirs:
            if log_dir.exists():
                log_files = list(log_dir.rglob("*.log"))
                if log_files:
                    # If has recent logs, assume some utilization
                    recent_logs = [f for f in log_files if (datetime.now().timestamp() - f.stat().st_mtime) < 86400]
                    if recent_logs:
                        return min(100.0, len(recent_logs) * 10.0)

        return 0.0

    def _discover_workflows(self) -> List[WorkflowProgress]:
        """Discover all workflows"""
        workflows = []

        # Check workflow files
        workflow_dir = self.project_root / "data" / "workflows"
        if workflow_dir.exists():
            for workflow_file in workflow_dir.glob("*.json"):
                try:
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        workflow_data = json.load(f)

                    workflow_id = workflow_file.stem
                    name = workflow_data.get("name", workflow_id)
                    steps = workflow_data.get("steps", [])
                    completed = sum(1 for step in steps if step.get("status") == "complete")

                    workflows.append(WorkflowProgress(
                        workflow_id=workflow_id,
                        name=name,
                        status="complete" if completed == len(steps) else "in_progress" if completed > 0 else "pending",
                        progress_percent=(completed / len(steps) * 100) if steps else 0.0,
                        steps_complete=completed,
                        steps_total=len(steps),
                        actors_involved=workflow_data.get("actors", []),
                        last_update=datetime.fromtimestamp(workflow_file.stat().st_mtime).isoformat()
                    ))
                except Exception as e:
                    self.logger.error(f"Error loading workflow {workflow_file}: {e}")

        return workflows

    def analyze_ide_utilization(self) -> Dict[str, Any]:
        """Analyze IDE utilization"""
        ide_scripts = [
            "jarvis_cursor_ide_keyboard_integration.py",
            "manus_cursor_chat_automation.py",
            "jarvis_auto_accept_monitor.py",
            "jarvis_use_mapped_shortcuts.py"
        ]

        found = 0
        active = 0

        for script in ide_scripts:
            script_path = self.project_root / "scripts" / "python" / script
            if script_path.exists():
                found += 1
                # Check if has active status
                if (self.project_root / f"{script_path.stem.upper()}_ACTIVE.md").exists():
                    active += 1

        return {
            "scripts_found": found,
            "scripts_active": active,
            "utilization_percent": (active / len(ide_scripts) * 100) if ide_scripts else 0.0,
            "potential": [
                "Code completion automation",
                "File navigation automation",
                "Search automation",
                "Refactoring automation",
                "Debugging automation",
                "Test execution automation"
            ]
        }

    def analyze_browser_utilization(self) -> Dict[str, Any]:
        """Analyze browser utilization"""
        browser_scripts = [
            "manus_neo_browser_control.py",
            "manus_neo_workflow_integration.py",
            "manus_neo_integration.py"
        ]

        found = 0
        active = 0

        for script in browser_scripts:
            script_path = self.project_root / "scripts" / "python" / script
            if script_path.exists():
                found += 1
                # Check if integrated
                if "neo" in script_path.read_text(encoding='utf-8').lower():
                    active += 1

        return {
            "scripts_found": found,
            "scripts_active": active,
            "utilization_percent": (active / len(browser_scripts) * 100) if browser_scripts else 0.0,
            "potential": [
                "Web automation",
                "API key extraction",
                "Form filling",
                "Data scraping",
                "Testing automation",
                "Monitoring automation"
            ]
        }

    def generate_transparency_report(self) -> Dict[str, Any]:
        """Generate comprehensive transparency report"""
        # Calculate overall integration
        major_actors = [a for a in self.actors if a.name in ["JARVIS", "MARVIN", "MANUS", "R5 Living Context Matrix", "Windows Systems Engineer", "Systems Disaster Recovery Engineer", "Physician, Heal Thyself"]]
        minor_actors = [a for a in self.actors if a.name not in [ma.name for ma in major_actors]]

        major_integration = sum(a.integration_percent for a in major_actors) / len(major_actors) if major_actors else 0.0
        minor_integration = sum(a.integration_percent for a in minor_actors) / len(minor_actors) if minor_actors else 0.0
        overall_integration = (major_integration * 0.7 + minor_integration * 0.3)

        # Workflow progress
        total_workflows = len(self.workflows)
        complete_workflows = sum(1 for w in self.workflows if w.status == "complete")
        workflow_progress = (complete_workflows / total_workflows * 100) if total_workflows > 0 else 0.0

        # IDE and Browser
        ide_util = self.analyze_ide_utilization()
        browser_util = self.analyze_browser_utilization()

        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_integration_percent": round(overall_integration, 2),
            "major_actors": {
                "count": len(major_actors),
                "average_integration": round(major_integration, 2),
                "actors": [asdict(a) for a in major_actors]
            },
            "minor_actors": {
                "count": len(minor_actors),
                "average_integration": round(minor_integration, 2),
                "actors": [asdict(a) for a in minor_actors]
            },
            "workflows": {
                "total": total_workflows,
                "complete": complete_workflows,
                "in_progress": sum(1 for w in self.workflows if w.status == "in_progress"),
                "pending": sum(1 for w in self.workflows if w.status == "pending"),
                "progress_percent": round(workflow_progress, 2),
                "workflows": [asdict(w) for w in self.workflows]
            },
            "ide_utilization": ide_util,
            "browser_utilization": browser_util,
            "job_slots": self._get_job_slot_breakdown()
        }

        return report

    def _get_job_slot_breakdown(self) -> Dict[str, Any]:
        """Get job slot breakdown"""
        if not self.job_slots:
            return {}

        slots = self.job_slots.get("job_slots", [])

        breakdown = {
            "total_slots": len(slots),
            "implemented": 0,
            "partial": 0,
            "missing": 0,
            "slots": []
        }

        for slot in slots:
            slot_name = slot.get("name", "")
            # Check if implemented
            script_name = slot.get("script", "").lower()
            implemented = False
            partial = False

            if script_name:
                script_path = self.project_root / "scripts" / "python" / script_name
                if script_path.exists():
                    implemented = True
                else:
                    # Check for similar names
                    for py_file in (self.project_root / "scripts" / "python").glob(f"*{slot_name.lower().replace(' ', '_')}*.py"):
                        partial = True
                        break

            status = "implemented" if implemented else "partial" if partial else "missing"
            if implemented:
                breakdown["implemented"] += 1
            elif partial:
                breakdown["partial"] += 1
            else:
                breakdown["missing"] += 1

            breakdown["slots"].append({
                "name": slot_name,
                "role": slot.get("role", ""),
                "responsibilities": slot.get("responsibilities", []),
                "status": status,
                "priority": slot.get("priority", "medium")
            })

        return breakdown

    def save_report(self, report: Dict[str, Any]) -> Path:
        """Save transparency report"""
        report_file = self.data_dir / f"transparency_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"✅ Transparency report saved: {report_file}")

        return report_file

    def generate_dashboard_markdown(self, report: Dict[str, Any]) -> str:
        """Generate markdown dashboard"""
        md = f"""# 🌐 JARVIS ECOSYSTEM TRANSPARENCY DASHBOARD

**Generated**: {report['timestamp']}

---

## 📊 OVERALL INTEGRATION STATUS

### **{report['overall_integration_percent']}% INTEGRATED**

- **Major Actors**: {report['major_actors']['average_integration']}% integrated ({report['major_actors']['count']} actors)
- **Minor Actors**: {report['minor_actors']['average_integration']}% integrated ({report['minor_actors']['count']} actors)

---

## 🎭 MAJOR ACTORS

"""

        for actor in report['major_actors']['actors']:
            status_emoji = "✅" if actor['status'] == 'active' else "⚠️" if actor['status'] == 'partial' else "❌"
            md += f"""### {status_emoji} **{actor['name']}** - {actor['role']}

- **Integration**: {actor['integration_percent']}%
- **Status**: {actor['status'].upper()}
- **Utilization**: {actor['utilization']}%
- **Last Active**: {actor['last_active'] or 'Never'}
- **Responsibilities**:
"""
            for resp in actor['responsibilities']:
                md += f"  - {resp}\n"
            md += "\n"

        md += "---\n\n## 🔧 MINOR ACTORS\n\n"

        for actor in report['minor_actors']['actors']:
            status_emoji = "✅" if actor['status'] == 'active' else "⚠️" if actor['status'] == 'partial' else "❌"
            md += f"""- {status_emoji} **{actor['name']}** ({actor['role']}) - {actor['integration_percent']}% integrated
"""

        md += f"""
---

## 📋 WORKFLOW PROGRESS

**Overall**: {report['workflows']['progress_percent']}% complete

- **Total Workflows**: {report['workflows']['total']}
- **Complete**: {report['workflows']['complete']} ✅
- **In Progress**: {report['workflows']['in_progress']} ⏳
- **Pending**: {report['workflows']['pending']} 📋

"""

        for workflow in report['workflows']['workflows']:
            status_emoji = "✅" if workflow['status'] == 'complete' else "⏳" if workflow['status'] == 'in_progress' else "📋"
            md += f"""### {status_emoji} {workflow['name']}

- **Progress**: {workflow['progress_percent']}% ({workflow['steps_complete']}/{workflow['steps_total']} steps)
- **Actors**: {', '.join(workflow['actors_involved']) if workflow['actors_involved'] else 'None'}
- **Last Update**: {workflow['last_update']}

"""

        md += f"""
---

## 💻 IDE UTILIZATION

**Current**: {report['ide_utilization']['utilization_percent']}%

- **Scripts Found**: {report['ide_utilization']['scripts_found']}/{len(['jarvis_cursor_ide_keyboard_integration.py', 'manus_cursor_chat_automation.py', 'jarvis_auto_accept_monitor.py', 'jarvis_use_mapped_shortcuts.py'])}
- **Scripts Active**: {report['ide_utilization']['scripts_active']}

### Potential Enhancements:
"""
        for potential in report['ide_utilization']['potential']:
            md += f"- {potential}\n"

        md += f"""
---

## 🌐 BROWSER UTILIZATION

**Current**: {report['browser_utilization']['utilization_percent']}%

- **Scripts Found**: {report['browser_utilization']['scripts_found']}/{len(['manus_neo_browser_control.py', 'manus_neo_workflow_integration.py', 'manus_neo_integration.py'])}
- **Scripts Active**: {report['browser_utilization']['scripts_active']}

### Potential Enhancements:
"""
        for potential in report['browser_utilization']['potential']:
            md += f"- {potential}\n"

        md += f"""
---

## 👔 JOB SLOTS BREAKDOWN

**Total Slots**: {report['job_slots'].get('total_slots', 0)}
- **Implemented**: {report['job_slots'].get('implemented', 0)} ✅
- **Partial**: {report['job_slots'].get('partial', 0)} ⚠️
- **Missing**: {report['job_slots'].get('missing', 0)} ❌

"""

        for slot in report['job_slots'].get('slots', []):
            status_emoji = "✅" if slot['status'] == 'implemented' else "⚠️" if slot['status'] == 'partial' else "❌"
            md += f"""### {status_emoji} **{slot['name']}** - {slot['role']}

**Priority**: {slot['priority'].upper()}
**Status**: {slot['status'].upper()}

**Responsibilities**:
"""
            for resp in slot.get('responsibilities', []):
                md += f"- {resp}\n"
            md += "\n"

        md += """
---

*Dashboard auto-updates every 5 minutes*
"""

        return md


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Ecosystem Transparency")
    parser.add_argument("--dashboard", action="store_true", help="Generate dashboard markdown")
    parser.add_argument("--json", action="store_true", help="Generate JSON report")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    transparency = JARVISEcosystemTransparency(project_root)

    report = transparency.generate_transparency_report()

    if args.json or not args:
        report_file = transparency.save_report(report)
        print(f"✅ Report saved: {report_file}")

    if args.dashboard or not args:
        dashboard_md = transparency.generate_dashboard_markdown(report)
        dashboard_file = project_root / "ECOSYSTEM_TRANSPARENCY_DASHBOARD.md"
        dashboard_file.write_text(dashboard_md, encoding='utf-8')
        print(f"✅ Dashboard saved: {dashboard_file}")

        print("\n" + "="*80)
        print("ECOSYSTEM TRANSPARENCY SUMMARY")
        print("="*80)
        print(f"Overall Integration: {report['overall_integration_percent']}%")
        print(f"Major Actors: {report['major_actors']['count']} ({report['major_actors']['average_integration']}% avg)")
        print(f"Minor Actors: {report['minor_actors']['count']} ({report['minor_actors']['average_integration']}% avg)")
        print(f"Workflows: {report['workflows']['progress_percent']}% complete")
        print(f"IDE Utilization: {report['ide_utilization']['utilization_percent']}%")
        print(f"Browser Utilization: {report['browser_utilization']['utilization_percent']}%")
        print("="*80)


if __name__ == "__main__":


    main()