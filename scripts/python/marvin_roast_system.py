#!/usr/bin/env python3
"""
MARVIN Roast System - Critical Analysis & Gap Identification

MARVIN roasts asks to identify:
- Gaps in implementation
- Bloat in code/documentation
- Missing integrations
- Incomplete workflows
- Unused code

JARVIS uses these roasts to close gaps and reduce bloat.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


@dataclass
class RoastFinding:
    """A finding from MARVIN's roast"""
    finding_id: str
    category: str  # gap, bloat, missing_integration, incomplete, unused_code
    severity: str  # critical, high, medium, low
    description: str
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MarvinRoast:
    """MARVIN's complete roast of an ask"""
    roast_id: str
    ask_id: str
    ask_text: str
    timestamp: str
    findings: List[RoastFinding] = field(default_factory=list)
    summary: str = ""
    gap_count: int = 0
    bloat_count: int = 0
    missing_integration_count: int = 0
    incomplete_count: int = 0
    unused_code_count: int = 0
    total_severity_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["findings"] = [f.to_dict() for f in self.findings]
        return data


class MarvinRoastSystem:
    """
    MARVIN Roast System

    Roasts asks to identify gaps, bloat, and issues.
    JARVIS uses these roasts to close gaps and reduce bloat.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("MarvinRoastSystem")

        # Data directories
        self.data_dir = self.project_root / "data" / "marvin_roasts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.roasts_file = self.data_dir / "roasts.jsonl"

        # Severity weights
        self.severity_weights = {
            "critical": 10.0,
            "high": 5.0,
            "medium": 2.0,
            "low": 1.0
        }

    def roast_ask(self, ask_id: str, ask_text: str, context: Optional[Dict[str, Any]] = None) -> MarvinRoast:
        """
        MARVIN roasts an ask

        Identifies gaps, bloat, missing integrations, incomplete workflows, unused code.
        """
        self.logger.info(f"🔥 MARVIN roasting ask: {ask_id}")

        roast_id = f"roast_{int(datetime.now().timestamp() * 1000)}"

        roast = MarvinRoast(
            roast_id=roast_id,
            ask_id=ask_id,
            ask_text=ask_text,
            timestamp=datetime.now().isoformat(),
            metadata=context or {}
        )

        # Analyze ask for gaps
        gap_findings = self._identify_gaps(ask_text, context)
        roast.findings.extend(gap_findings)
        roast.gap_count = len(gap_findings)

        # Analyze ask for bloat
        bloat_findings = self._identify_bloat(ask_text, context)
        roast.findings.extend(bloat_findings)
        roast.bloat_count = len(bloat_findings)

        # Analyze ask for missing integrations
        integration_findings = self._identify_missing_integrations(ask_text, context)
        roast.findings.extend(integration_findings)
        roast.missing_integration_count = len(integration_findings)

        # Analyze ask for incomplete workflows
        incomplete_findings = self._identify_incomplete_workflows(ask_text, context)
        roast.findings.extend(incomplete_findings)
        roast.incomplete_count = len(incomplete_findings)

        # Analyze ask for unused code
        unused_findings = self._identify_unused_code(ask_text, context)
        roast.findings.extend(unused_findings)
        roast.unused_code_count = len(unused_findings)

        # Calculate total severity score
        roast.total_severity_score = sum(
            self.severity_weights.get(finding.severity, 1.0) for finding in roast.findings
        )

        # Generate summary
        roast.summary = self._generate_roast_summary(roast)

        # Save roast
        self._save_roast(roast)

        self.logger.info(f"✅ MARVIN roasted ask: {len(roast.findings)} findings, severity: {roast.total_severity_score:.1f}")

        return roast

    def _identify_gaps(self, ask_text: str, context: Optional[Dict[str, Any]]) -> List[RoastFinding]:
        """Identify gaps in implementation"""
        findings = []
        ask_lower = ask_text.lower()

        # Check for common gap indicators
        gap_indicators = {
            "missing": ["missing", "not implemented", "doesn't exist", "not created", "not configured"],
            "incomplete": ["incomplete", "partial", "half", "unfinished", "todo", "fixme"],
            "disconnected": ["not connected", "not integrated", "doesn't talk", "isolated", "disconnected"],
            "manual": ["manual", "human", "by hand", "requires", "need to"]
        }

        for category, indicators in gap_indicators.items():
            for indicator in indicators:
                if indicator in ask_lower:
                    finding = RoastFinding(
                        finding_id=f"gap_{int(datetime.now().timestamp() * 1000)}",
                        category="gap",
                        severity="high" if category in ["missing", "disconnected"] else "medium",
                        description=f"Gap identified: {category} - '{indicator}' found in ask",
                        evidence=[f"Ask contains: '{indicator}'"],
                        recommendations=[
                            f"Implement missing {category} functionality",
                            f"Close gap by completing {category}",
                            f"Integrate {category} with existing systems"
                        ]
                    )
                    findings.append(finding)
                    break

        # Check context for gaps
        if context:
            if context.get("workflow_id") and not context.get("workflow_executed"):
                findings.append(RoastFinding(
                    finding_id=f"gap_workflow_{int(datetime.now().timestamp() * 1000)}",
                    category="gap",
                    severity="critical",
                    description="Workflow identified but not executed",
                    evidence=["Workflow ID exists but execution status unknown"],
                    recommendations=["Execute workflow", "Verify workflow integration"]
                ))

        return findings

    def _identify_bloat(self, ask_text: str, context: Optional[Dict[str, Any]]) -> List[RoastFinding]:
        """Identify bloat in code/documentation"""
        findings = []
        ask_lower = ask_text.lower()

        # Check for bloat indicators
        bloat_indicators = {
            "duplicate": ["duplicate", "copy", "same", "redundant", "repeat"],
            "unused": ["unused", "dead", "orphan", "abandoned"],
            "overcomplicated": ["complex", "complicated", "overengineered", "bloated"],
            "documentation": ["documentation", "docs", "readme", "comments"]
        }

        for category, indicators in bloat_indicators.items():
            for indicator in indicators:
                if indicator in ask_lower:
                    finding = RoastFinding(
                        finding_id=f"bloat_{int(datetime.now().timestamp() * 1000)}",
                        category="bloat",
                        severity="medium" if category == "documentation" else "high",
                        description=f"Bloat identified: {category} - '{indicator}' found in ask",
                        evidence=[f"Ask mentions: '{indicator}'"],
                        recommendations=[
                            f"Remove {category} bloat",
                            f"Consolidate {category}",
                            f"Simplify {category} implementation"
                        ]
                    )
                    findings.append(finding)
                    break

        return findings

    def _identify_missing_integrations(self, ask_text: str, context: Optional[Dict[str, Any]]) -> List[RoastFinding]:
        """Identify missing integrations"""
        findings = []
        ask_lower = ask_text.lower()

        # Check for integration indicators
        integration_keywords = ["integrate", "connect", "link", "hook up", "wire", "bridge"]
        integration_targets = ["api", "service", "platform", "system", "database", "workflow"]

        has_integration_keyword = any(keyword in ask_lower for keyword in integration_keywords)
        has_integration_target = any(target in ask_lower for target in integration_targets)

        if has_integration_keyword or has_integration_target:
            finding = RoastFinding(
                finding_id=f"integration_{int(datetime.now().timestamp() * 1000)}",
                category="missing_integration",
                severity="high",
                description="Missing integration identified",
                evidence=[
                    f"Ask mentions integration: {ask_text[:100]}",
                    "Integration may not be implemented"
                ],
                recommendations=[
                    "Implement missing integration",
                    "Verify integration endpoints",
                    "Test integration connectivity"
                ]
            )
            findings.append(finding)

        return findings

    def _identify_incomplete_workflows(self, ask_text: str, context: Optional[Dict[str, Any]]) -> List[RoastFinding]:
        """Identify incomplete workflows"""
        findings = []
        ask_lower = ask_text.lower()

        # Check for incomplete workflow indicators
        incomplete_indicators = [
            "incomplete", "partial", "half", "unfinished", "todo", "fixme",
            "not working", "broken", "doesn't work", "fails"
        ]

        if any(indicator in ask_lower for indicator in incomplete_indicators):
            finding = RoastFinding(
                finding_id=f"incomplete_{int(datetime.now().timestamp() * 1000)}",
                category="incomplete",
                severity="critical",
                description="Incomplete workflow identified",
                evidence=["Ask indicates complete or broken workflow"],
                recommendations=[
                    "Complete workflow implementation",
                    "Fix broken workflow steps",
                    "Verify workflow end-to-end"
                ]
            )
            findings.append(finding)

        return findings

    def _identify_unused_code(self, ask_text: str, context: Optional[Dict[str, Any]]) -> List[RoastFinding]:
        """Identify unused code"""
        findings = []
        ask_lower = ask_text.lower()

        # Check for unused code indicators
        unused_indicators = ["unused", "dead", "orphan", "abandoned", "not used", "exists but"]

        if any(indicator in ask_lower for indicator in unused_indicators):
            finding = RoastFinding(
                finding_id=f"unused_{int(datetime.now().timestamp() * 1000)}",
                category="unused_code",
                severity="medium",
                description="Unused code identified",
                evidence=["Ask mentions unused or dead code"],
                recommendations=[
                    "Remove unused code",
                    "Consolidate duplicate code",
                    "Archive unused code"
                ]
            )
            findings.append(finding)

        return findings

    def _generate_roast_summary(self, roast: MarvinRoast) -> str:
        """Generate roast summary"""
        if not roast.findings:
            return "✅ No issues found. Ask is clean."

        summary_parts = []

        if roast.gap_count > 0:
            summary_parts.append(f"{roast.gap_count} gap(s) identified")
        if roast.bloat_count > 0:
            summary_parts.append(f"{roast.bloat_count} bloat issue(s) found")
        if roast.missing_integration_count > 0:
            summary_parts.append(f"{roast.missing_integration_count} missing integration(s)")
        if roast.incomplete_count > 0:
            summary_parts.append(f"{roast.incomplete_count} incomplete workflow(s)")
        if roast.unused_code_count > 0:
            summary_parts.append(f"{roast.unused_code_count} unused code issue(s)")

        summary = f"🔥 MARVIN ROAST: {', '.join(summary_parts)}. Total severity: {roast.total_severity_score:.1f}"

        return summary

    def _save_roast(self, roast: MarvinRoast):
        """Save roast to file"""
        try:
            with open(self.roasts_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(roast.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Error saving roast: {e}")

    def get_roast_for_ask(self, ask_id: str) -> Optional[MarvinRoast]:
        """Get roast for a specific ask"""
        if not self.roasts_file.exists():
            return None

        try:
            with open(self.roasts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        roast_data = json.loads(line)
                        if roast_data.get("ask_id") == ask_id:
                            # Reconstruct roast
                            findings = [RoastFinding(**f) for f in roast_data.get("findings", [])]
                            roast = MarvinRoast(
                                roast_id=roast_data["roast_id"],
                                ask_id=roast_data["ask_id"],
                                ask_text=roast_data["ask_text"],
                                timestamp=roast_data["timestamp"],
                                findings=findings,
                                summary=roast_data.get("summary", ""),
                                gap_count=roast_data.get("gap_count", 0),
                                bloat_count=roast_data.get("bloat_count", 0),
                                missing_integration_count=roast_data.get("missing_integration_count", 0),
                                incomplete_count=roast_data.get("incomplete_count", 0),
                                unused_code_count=roast_data.get("unused_code_count", 0),
                                total_severity_score=roast_data.get("total_severity_score", 0.0),
                                metadata=roast_data.get("metadata", {})
                            )
                            return roast
        except Exception as e:
            self.logger.error(f"Error loading roast: {e}")

        return None


def main():
    """Main execution for testing"""
    roaster = MarvinRoastSystem()

    print("🔥 MARVIN Roast System")
    print("=" * 80)
    print("")

    # Test roast
    roast = roaster.roast_ask(
        "complete_the_lumina_extension",
        "Complete the Lumina extension we've been working on for a year",
        context={"workflow_id": "lumina_extension", "workflow_executed": False}
    )

    print(f"✅ Roast Summary: {roast.summary}")
    print(f"   Findings: {len(roast.findings)}")
    print(f"   Gaps: {roast.gap_count}")
    print(f"   Bloat: {roast.bloat_count}")
    print(f"   Severity Score: {roast.total_severity_score:.1f}")
    print("")
    print("Top Findings:")
    for i, finding in enumerate(roast.findings[:5], 1):
        print(f"   {i}. [{finding.severity.upper()}] {finding.description}")


if __name__ == "__main__":



    main()