#!/usr/bin/env python3
"""
JARVIS Voice & Vibecoding Status Report

Comprehensive status report on:
- JARVIS voice implementation
- Hands-free no-typing/clicking vibecoding
- Roadblocks preventing full deployment
- Delegation status
- Summit readiness

Tags: #jarvis #voice #vibecoding #hands-free #status #roadblocks #delegation
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("JARVISVoiceVibecodingStatus")


class ComponentStatus(Enum):
    """Component status levels"""
    OPERATIONAL = "operational"
    PARTIAL = "partial"
    NOT_IMPLEMENTED = "not_implemented"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class RoadblockSeverity(Enum):
    """Roadblock severity"""
    CRITICAL = "critical"  # Blocks full deployment
    HIGH = "high"  # Major impact
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact


@dataclass
class Component:
    """System component"""
    name: str
    status: ComponentStatus
    description: str
    file_path: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['status'] = self.status.value
        return result


@dataclass
class Roadblock:
    """Roadblock preventing deployment"""
    roadblock_id: str
    title: str
    severity: RoadblockSeverity
    description: str
    affected_components: List[str] = field(default_factory=list)
    potential_solutions: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    status: str = "open"

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


class JARVISVoiceVibecodingStatusReport:
    """
    Comprehensive status report on JARVIS voice and vibecoding
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts" / "python"

        logger.info("=" * 80)
        logger.info("📊 JARVIS VOICE & VIBECODING STATUS REPORT")
        logger.info("=" * 80)
        logger.info("")

    def check_voice_components(self) -> List[Component]:
        """Check JARVIS voice components"""
        components = []

        voice_files = [
            "jarvis_full_voice_mode.py",
            "jarvis_voice_activated.py",
            "jarvis_voice_activation.py",
            "jarvis_voice_interface.py",
            "jarvis_azure_voice_interface.py",
            "jarvis_async_voice_conversation.py",
            "activate_jarvis_voice.py",
            "start_jarvis_voice_conversation.py"
        ]

        for file_name in voice_files:
            file_path = self.scripts_dir / file_name
            exists = file_path.exists()

            if exists:
                # Try to determine status from file content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "VOICE_SYSTEM_AVAILABLE" in content or "Azure" in content:
                            status = ComponentStatus.PARTIAL if "ImportError" in content else ComponentStatus.OPERATIONAL
                        else:
                            status = ComponentStatus.OPERATIONAL
                except:
                    status = ComponentStatus.UNKNOWN
            else:
                status = ComponentStatus.NOT_IMPLEMENTED

            components.append(Component(
                name=file_name.replace('.py', ''),
                status=status,
                description=f"JARVIS voice component: {file_name}",
                file_path=str(file_path) if exists else None
            ))

        return components

    def check_hands_free_components(self) -> List[Component]:
        """Check hands-free vibecoding components"""
        components = []

        hands_free_files = [
            "jarvis_hands_free_cursor_control.py",
            "jarvis_hands_free_automation.py",
            "jarvis_hands_free_demo.py",
            "jarvis_hands_free_startup.py",
            "test_jarvis_hands_free_flow.py"
        ]

        for file_name in hands_free_files:
            file_path = self.scripts_dir / file_name
            exists = file_path.exists()

            if exists:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "MANUS_AVAILABLE" in content or "VOICE_AVAILABLE" in content:
                            status = ComponentStatus.PARTIAL if "ImportError" in content or "not available" in content else ComponentStatus.OPERATIONAL
                        else:
                            status = ComponentStatus.OPERATIONAL
                except:
                    status = ComponentStatus.UNKNOWN
            else:
                status = ComponentStatus.NOT_IMPLEMENTED

            components.append(Component(
                name=file_name.replace('.py', ''),
                status=status,
                description=f"Hands-free vibecoding component: {file_name}",
                file_path=str(file_path) if exists else None
            ))

        return components

    def identify_roadblocks(self) -> List[Roadblock]:
        """Identify roadblocks preventing full deployment"""
        roadblocks = []

        # Check for missing dependencies
        voice_components = self.check_voice_components()
        hands_free_components = self.check_hands_free_components()

        # Roadblock 1: Voice system dependencies
        missing_voice_deps = []
        if any(c.status == ComponentStatus.PARTIAL for c in voice_components):
            missing_voice_deps.append("Azure Speech SDK")
            missing_voice_deps.append("Voice activation system")

        if missing_voice_deps:
            roadblocks.append(Roadblock(
                roadblock_id="rb_001",
                title="Voice System Dependencies Missing",
                severity=RoadblockSeverity.CRITICAL,
                description="Voice components exist but dependencies may be missing or not properly configured",
                affected_components=[c.name for c in voice_components if c.status == ComponentStatus.PARTIAL],
                potential_solutions=[
                    "Install Azure Speech SDK: pip install azure-cognitiveservices-speech",
                    "Configure Azure credentials in Key Vault",
                    "Verify microphone and speaker setup",
                    "Test voice activation system"
                ]
            ))

        # Roadblock 2: Hands-free integration
        if any(c.status == ComponentStatus.PARTIAL for c in hands_free_components):
            roadblocks.append(Roadblock(
                roadblock_id="rb_002",
                title="Hands-Free Integration Incomplete",
                severity=RoadblockSeverity.HIGH,
                description="Hands-free components exist but may not be fully integrated with voice system",
                affected_components=[c.name for c in hands_free_components if c.status == ComponentStatus.PARTIAL],
                potential_solutions=[
                    "Integrate MANUS cursor controller with voice system",
                    "Ensure keyboard shortcut execution works",
                    "Test complete hands-free flow",
                    "Verify no-typing/clicking requirements met"
                ]
            ))

        # Roadblock 3: Summit readiness
        roadblocks.append(Roadblock(
            roadblock_id="rb_003",
            title="Summit Readiness Unknown",
            severity=RoadblockSeverity.MEDIUM,
            description="Need to verify if JARVIS can 'summit' and focus on addressing roadblocks",
            affected_components=["jarvis_chain_of_command_delegation.py", "All voice components"],
            potential_solutions=[
                "Verify Chain of Command delegation system",
                "Check if subagents are being delegated to",
                "Implement 5W1H analysis for delegation gaps",
                "Create summit readiness checklist"
            ]
        ))

        # Roadblock 4: Full deployment plan
        roadblocks.append(Roadblock(
            roadblock_id="rb_004",
            title="Full Deployment Plan Needed",
            severity=RoadblockSeverity.HIGH,
            description="Need comprehensive deployment and activation plan",
            affected_components=["All components"],
            potential_solutions=[
                "Create deployment roadmap",
                "Define activation sequence",
                "Identify testing requirements",
                "Document rollback procedures"
            ]
        ))

        return roadblocks

    def check_delegation_status(self) -> Dict[str, Any]:
        """Check if we're delegating to subagents"""
        delegation_file = self.scripts_dir / "jarvis_chain_of_command_delegation.py"
        auto_assignment_file = self.scripts_dir / "automated_agent_chat_session_assignment.py"

        delegation_status = {
            "chain_of_command_exists": delegation_file.exists(),
            "auto_assignment_exists": auto_assignment_file.exists(),
            "delegation_active": False,
            "subagents_configured": False,
            "issues": []
        }

        if delegation_file.exists():
            try:
                with open(delegation_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "JARVISChainOfCommand" in content:
                        delegation_status["delegation_active"] = True
                    if "SUBAGENT" in content:
                        delegation_status["subagents_configured"] = True
            except Exception as e:
                delegation_status["issues"].append(f"Error reading delegation file: {e}")

        if not delegation_status["delegation_active"]:
            delegation_status["issues"].append("Chain of Command delegation not active")

        if not delegation_status["subagents_configured"]:
            delegation_status["issues"].append("Subagents not configured")

        return delegation_status

    def generate_5w1h_analysis(self) -> Dict[str, Any]:
        """5W1H analysis for delegation gaps"""
        analysis = {
            "what": "Are we delegating to subagents?",
            "why": "To prevent JARVIS from being overloaded and ensure proper task distribution",
            "who": "JARVIS (summit) → Master Agents → Agents → Subagents",
            "when": "Should be happening for all @ASKS and tasks",
            "where": "Chain of Command system, Automated Agent Assignment",
            "how": "Through jarvis_chain_of_command_delegation.py and automated_agent_chat_session_assignment.py",
            "current_status": self.check_delegation_status(),
            "gaps": []
        }

        if not analysis["current_status"]["delegation_active"]:
            analysis["gaps"].append("Delegation system not active")

        if not analysis["current_status"]["subagents_configured"]:
            analysis["gaps"].append("Subagents not configured")

        return analysis

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        voice_components = self.check_voice_components()
        hands_free_components = self.check_hands_free_components()
        roadblocks = self.identify_roadblocks()
        delegation_status = self.check_delegation_status()
        analysis_5w1h = self.generate_5w1h_analysis()

        # Calculate overall status
        all_components = voice_components + hands_free_components
        operational_count = sum(1 for c in all_components if c.status == ComponentStatus.OPERATIONAL)
        partial_count = sum(1 for c in all_components if c.status == ComponentStatus.PARTIAL)
        not_impl_count = sum(1 for c in all_components if c.status == ComponentStatus.NOT_IMPLEMENTED)

        overall_status = "PARTIAL"
        if operational_count == len(all_components):
            overall_status = "OPERATIONAL"
        elif not_impl_count > operational_count:
            overall_status = "NOT_READY"

        report = {
            "report_date": datetime.now().isoformat(),
            "overall_status": overall_status,
            "summary": {
                "voice_components": len(voice_components),
                "hands_free_components": len(hands_free_components),
                "operational": operational_count,
                "partial": partial_count,
                "not_implemented": not_impl_count,
                "roadblocks": len(roadblocks),
                "critical_roadblocks": sum(1 for r in roadblocks if r.severity == RoadblockSeverity.CRITICAL)
            },
            "voice_components": [c.to_dict() for c in voice_components],
            "hands_free_components": [c.to_dict() for c in hands_free_components],
            "roadblocks": [r.to_dict() for r in roadblocks],
            "delegation_status": delegation_status,
            "5w1h_analysis": analysis_5w1h,
            "summit_readiness": {
                "can_summit": delegation_status["delegation_active"] and len(roadblocks) > 0,
                "roadblocks_blocking": [r.roadblock_id for r in roadblocks if r.severity == RoadblockSeverity.CRITICAL],
                "delegation_ready": delegation_status["delegation_active"]
            },
            "recommendations": [
                "Address critical roadblocks first",
                "Verify voice system dependencies",
                "Complete hands-free integration",
                "Activate delegation system",
                "Create deployment plan"
            ]
        }

        return report

    def print_report(self):
        """Print formatted status report"""
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("📊 JARVIS VOICE & VIBECODING STATUS REPORT")
        print("=" * 80)
        print(f"Report Date: {report['report_date']}")
        print(f"Overall Status: {report['overall_status']}")
        print("")

        print("📈 SUMMARY")
        print("-" * 80)
        print(f"Voice Components: {report['summary']['voice_components']}")
        print(f"Hands-Free Components: {report['summary']['hands_free_components']}")
        print(f"Operational: {report['summary']['operational']}")
        print(f"Partial: {report['summary']['partial']}")
        print(f"Not Implemented: {report['summary']['not_implemented']}")
        print(f"Roadblocks: {report['summary']['roadblocks']} ({report['summary']['critical_roadblocks']} critical)")
        print("")

        print("🎤 VOICE COMPONENTS")
        print("-" * 80)
        for comp in report['voice_components']:
            status_icon = "✅" if comp['status'] == "operational" else "⚠️" if comp['status'] == "partial" else "❌"
            print(f"{status_icon} {comp['name']}: {comp['status']}")
        print("")

        print("🖐️  HANDS-FREE COMPONENTS")
        print("-" * 80)
        for comp in report['hands_free_components']:
            status_icon = "✅" if comp['status'] == "operational" else "⚠️" if comp['status'] == "partial" else "❌"
            print(f"{status_icon} {comp['name']}: {comp['status']}")
        print("")

        print("🚧 ROADBLOCKS")
        print("-" * 80)
        for rb in report['roadblocks']:
            severity_icon = "🔴" if rb['severity'] == "critical" else "🟠" if rb['severity'] == "high" else "🟡"
            print(f"{severity_icon} [{rb['severity'].upper()}] {rb['title']}")
            print(f"   {rb['description']}")
            if rb['potential_solutions']:
                print("   Solutions:")
                for sol in rb['potential_solutions'][:3]:
                    print(f"     - {sol}")
            print("")

        print("👥 DELEGATION STATUS")
        print("-" * 80)
        del_status = report['delegation_status']
        print(f"Chain of Command: {'✅' if del_status['chain_of_command_exists'] else '❌'}")
        print(f"Auto Assignment: {'✅' if del_status['auto_assignment_exists'] else '❌'}")
        print(f"Delegation Active: {'✅' if del_status['delegation_active'] else '❌'}")
        print(f"Subagents Configured: {'✅' if del_status['subagents_configured'] else '❌'}")
        if del_status['issues']:
            print("Issues:")
            for issue in del_status['issues']:
                print(f"   ⚠️  {issue}")
        print("")

        print("❓ 5W1H ANALYSIS")
        print("-" * 80)
        analysis = report['5w1h_analysis']
        print(f"What: {analysis['what']}")
        print(f"Why: {analysis['why']}")
        print(f"Who: {analysis['who']}")
        print(f"When: {analysis['when']}")
        print(f"Where: {analysis['where']}")
        print(f"How: {analysis['how']}")
        if analysis['gaps']:
            print("Gaps:")
            for gap in analysis['gaps']:
                print(f"   ⚠️  {gap}")
        print("")

        print("🏔️  SUMMIT READINESS")
        print("-" * 80)
        summit = report['summit_readiness']
        print(f"Can Summit: {'✅' if summit['can_summit'] else '❌'}")
        print(f"Delegation Ready: {'✅' if summit['delegation_ready'] else '❌'}")
        if summit['roadblocks_blocking']:
            print(f"Blocking Roadblocks: {', '.join(summit['roadblocks_blocking'])}")
        print("")

        print("💡 RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        print("")

        print("=" * 80)
        print("")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Voice & Vibecoding Status Report")
        parser.add_argument('--json', action='store_true', help='Output as JSON')
        parser.add_argument('--save', type=str, metavar='FILE', help='Save report to file')

        args = parser.parse_args()

        reporter = JARVISVoiceVibecodingStatusReport()

        if args.json:
            report = reporter.generate_report()
            print(json.dumps(report, indent=2))
        else:
            reporter.print_report()

        if args.save:
            report = reporter.generate_report()
            output_file = Path(args.save)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"💾 Report saved to: {output_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()