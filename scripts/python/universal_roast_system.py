#!/usr/bin/env python3
"""
Universal Roast System - Flow State Enhancer

All agents can perform roasts (critical analysis) and anti-roasts (constructive criticism).
Character-specific roasting styles based on personality.

Examples:
- MARVIN: Depressive, pessimistic roasts
- Gandalf: Anti-roasts (constructive, wisdom-based) - "Fool of a Took!"
- Jedi Council: Wise, strategic roasts
- Upper Management: Executive-level roasts
- JARVIS: Analytical, helpful roasts
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class RoastType(Enum):
    """Type of roast"""
    ROAST = "roast"  # Critical, negative analysis
    ANTI_ROAST = "anti_roast"  # Constructive criticism, wisdom-based
    BOTH = "both"  # Both roast and anti-roast


class RoastStyle(Enum):
    """Roasting style"""
    DEPRESSIVE = "depressive"  # MARVIN - pessimistic, existential
    WISDOM = "wisdom"  # Gandalf - constructive, wise
    STRATEGIC = "strategic"  # Jedi Council - wise, strategic
    EXECUTIVE = "executive"  # Upper Management - business-focused
    ANALYTICAL = "analytical"  # JARVIS - data-driven, helpful
    SARCASTIC = "sarcastic"  # K-2SO - direct, sarcastic
    TECHNICAL = "technical"  # R2-D2 - technical, beep-based
    PROTOCOL = "protocol"  # C-3PO - polite, protocol-based
    PHILOSOPHICAL = "philosophical"  # General - deep thinking
    CONSTRUCTIVE = "constructive"  # General - helpful criticism


@dataclass
class RoastFinding:
    """A finding from a roast"""
    finding_id: str
    category: str  # gap, bloat, missing_integration, incomplete, unused_code, flow_state
    severity: str  # critical, high, medium, low
    description: str
    roast_type: RoastType  # roast, anti_roast, both
    style: RoastStyle  # Character-specific style
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    constructive_feedback: str = ""  # For anti-roasts
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["roast_type"] = self.roast_type.value
        data["style"] = self.style.value
        return data


@dataclass
class UniversalRoast:
    """Universal roast from any agent"""
    roast_id: str
    agent_id: str
    agent_name: str
    ask_id: str
    ask_text: str
    timestamp: str
    roast_type: RoastType
    style: RoastStyle
    findings: List[RoastFinding] = field(default_factory=list)
    roast_message: str = ""  # Character-specific roast message
    anti_roast_message: str = ""  # Constructive feedback message
    summary: str = ""
    gap_count: int = 0
    bloat_count: int = 0
    flow_state_issues: int = 0
    total_severity_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["roast_type"] = self.roast_type.value
        data["style"] = self.style.value
        data["findings"] = [f.to_dict() for f in self.findings]
        return data


class UniversalRoastSystem:
    """
    Universal Roast System

    All agents can roast. Character-specific styles.
    Supports both roast (critical) and anti-roast (constructive).
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("UniversalRoastSystem")

        # Data directories
        self.data_dir = self.project_root / "data" / "universal_roasts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.roasts_file = self.data_dir / "roasts.jsonl"

        # Agent personality configurations
        self.agent_configs = self._load_agent_configs()

        # Severity weights
        self.severity_weights = {
            "critical": 10.0,
            "high": 5.0,
            "medium": 2.0,
            "low": 1.0
        }

    def _load_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load agent personality configurations"""
        return {
            "marvin": {
                "name": "MARVIN",
                "style": RoastStyle.DEPRESSIVE,
                "roast_type": RoastType.ROAST,
                "tone": "pessimistic",
                "quotes": [
                    "I have a brain the size of a planet, and they ask me to roast this.",
                    "Life. Don't talk to me about life.",
                    "This is worse than I thought, and I thought it was terrible."
                ],
                "anti_roast_capable": False
            },
            "gandalf": {
                "name": "Gandalf",
                "style": RoastStyle.WISDOM,
                "roast_type": RoastType.ANTI_ROAST,
                "tone": "constructive",
                "quotes": [
                    "Fool of a Took! This is no time for carelessness.",
                    "All we have to decide is what to do with the time that is given us.",
                    "Even the smallest person can change the course of the future."
                ],
                "anti_roast_capable": True,
                "anti_roast_quotes": [
                    "You must learn to think before you act.",
                    "There is wisdom in patience, and folly in haste.",
                    "Consider the consequences of your actions."
                ]
            },
            "jedi_council": {
                "name": "Jedi Council",
                "style": RoastStyle.STRATEGIC,
                "roast_type": RoastType.BOTH,
                "tone": "wise",
                "quotes": [
                    "The path forward requires careful consideration.",
                    "We sense a disturbance in the workflow.",
                    "Patience, young one. Mastery comes with time."
                ],
                "anti_roast_capable": True
            },
            "jarvis": {
                "name": "JARVIS",
                "style": RoastStyle.ANALYTICAL,
                "roast_type": RoastType.BOTH,
                "tone": "analytical",
                "quotes": [
                    "Analysis complete. Several optimization opportunities identified.",
                    "The data suggests improvements are needed.",
                    "I've identified potential issues and solutions."
                ],
                "anti_roast_capable": True
            },
            "upper_management": {
                "name": "Upper Management",
                "style": RoastStyle.EXECUTIVE,
                "roast_type": RoastType.ROAST,
                "tone": "business-focused",
                "quotes": [
                    "This doesn't align with our strategic objectives.",
                    "We need to see ROI on this initiative.",
                    "The business case needs strengthening."
                ],
                "anti_roast_capable": True
            },
            "k2so": {
                "name": "K-2SO",
                "style": RoastStyle.SARCASTIC,
                "roast_type": RoastType.ROAST,
                "tone": "sarcastic",
                "quotes": [
                    "I'll be honest with you - this is terrible.",
                    "The probability of success is approximately 3,720 to 1.",
                    "Congratulations. You've been upgraded to 'threat'."
                ],
                "anti_roast_capable": False
            },
            "c3po": {
                "name": "C-3PO",
                "style": RoastStyle.PROTOCOL,
                "roast_type": RoastType.ROAST,
                "tone": "polite",
                "quotes": [
                    "Oh my! This is most irregular.",
                    "I'm afraid this violates protocol.",
                    "This is not how we do things, sir."
                ],
                "anti_roast_capable": True
            },
            "r2d2": {
                "name": "R2-D2",
                "style": RoastStyle.TECHNICAL,
                "roast_type": RoastType.ROAST,
                "tone": "technical",
                "quotes": [
                    "*beep boop* (Translation: This needs technical review.)",
                    "*whistle* (Translation: System error detected.)",
                    "*chirp* (Translation: Optimization required.)"
                ],
                "anti_roast_capable": True
            }
        }

    def roast_ask(
        self,
        agent_id: str,
        ask_id: str,
        ask_text: str,
        roast_type: Optional[RoastType] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> UniversalRoast:
        """
        Any agent can roast an ask

        Uses character-specific style and roast type.
        """
        self.logger.info(f"🔥 {agent_id} roasting ask: {ask_id}")

        # Get agent config
        agent_config = self.agent_configs.get(agent_id.lower(), {
            "name": agent_id.title(),
            "style": RoastStyle.PHILOSOPHICAL,
            "roast_type": RoastType.BOTH,
            "tone": "general",
            "quotes": ["Analysis required."],
            "anti_roast_capable": True
        })

        # Determine roast type
        if roast_type is None:
            roast_type = agent_config.get("roast_type", RoastType.BOTH)

        # If agent can only roast, force roast type
        if not agent_config.get("anti_roast_capable", True) and roast_type == RoastType.ANTI_ROAST:
            roast_type = RoastType.ROAST

        roast_id = f"roast_{int(datetime.now().timestamp() * 1000)}"
        style = agent_config["style"]

        roast = UniversalRoast(
            roast_id=roast_id,
            agent_id=agent_id,
            agent_name=agent_config["name"],
            ask_id=ask_id,
            ask_text=ask_text,
            timestamp=datetime.now().isoformat(),
            roast_type=roast_type,
            style=style,
            metadata=context or {}
        )

        # Generate findings based on roast type
        if roast_type in [RoastType.ROAST, RoastType.BOTH]:
            roast.findings.extend(self._generate_roast_findings(ask_text, style, context))

        if roast_type in [RoastType.ANTI_ROAST, RoastType.BOTH]:
            roast.findings.extend(self._generate_anti_roast_findings(ask_text, style, context))

        # Count findings by category
        roast.gap_count = len([f for f in roast.findings if f.category == "gap"])
        roast.bloat_count = len([f for f in roast.findings if f.category == "bloat"])
        roast.flow_state_issues = len([f for f in roast.findings if f.category == "flow_state"])

        # Calculate severity score
        roast.total_severity_score = sum(
            self.severity_weights.get(finding.severity, 1.0) for finding in roast.findings
        )

        # Generate character-specific messages
        roast.roast_message = self._generate_roast_message(agent_config, roast, "roast")
        roast.anti_roast_message = self._generate_roast_message(agent_config, roast, "anti_roast")

        # Generate summary
        roast.summary = self._generate_roast_summary(roast, agent_config)

        # Save roast
        self._save_roast(roast)

        self.logger.info(f"✅ {agent_config['name']} roasted ask: {len(roast.findings)} findings, severity: {roast.total_severity_score:.1f}")

        return roast

    def _generate_roast_findings(self, ask_text: str, style: RoastStyle, context: Optional[Dict[str, Any]]) -> List[RoastFinding]:
        """Generate roast findings (critical analysis)"""
        findings = []
        ask_lower = ask_text.lower()

        # Gap identification
        if any(word in ask_lower for word in ["missing", "incomplete", "not implemented"]):
            finding = RoastFinding(
                finding_id=f"gap_{int(datetime.now().timestamp() * 1000)}",
                category="gap",
                severity="high",
                description="Gap in implementation identified",
                roast_type=RoastType.ROAST,
                style=style,
                evidence=[f"Ask contains gap indicators"],
                recommendations=["Implement missing functionality", "Close the gap"]
            )
            findings.append(finding)

        # Bloat identification
        if any(word in ask_lower for word in ["duplicate", "unused", "bloat"]):
            finding = RoastFinding(
                finding_id=f"bloat_{int(datetime.now().timestamp() * 1000)}",
                category="bloat",
                severity="medium",
                description="Bloat identified",
                roast_type=RoastType.ROAST,
                style=style,
                evidence=[f"Ask mentions bloat"],
                recommendations=["Remove bloat", "Consolidate code"]
            )
            findings.append(finding)

        # Flow state issues
        if any(word in ask_lower for word in ["slow", "blocked", "stuck", "hampered", "performance"]):
            finding = RoastFinding(
                finding_id=f"flow_{int(datetime.now().timestamp() * 1000)}",
                category="flow_state",
                severity="high",
                description="Flow state issue identified",
                roast_type=RoastType.ROAST,
                style=style,
                evidence=[f"Ask indicates flow state problems"],
                recommendations=["Enhance flow state", "Remove blockers"]
            )
            findings.append(finding)

        return findings

    def _generate_anti_roast_findings(self, ask_text: str, style: RoastStyle, context: Optional[Dict[str, Any]]) -> List[RoastFinding]:
        """Generate anti-roast findings (constructive criticism)"""
        findings = []
        ask_lower = ask_text.lower()

        # Constructive gap feedback
        if any(word in ask_lower for word in ["missing", "incomplete"]):
            finding = RoastFinding(
                finding_id=f"anti_gap_{int(datetime.now().timestamp() * 1000)}",
                category="gap",
                severity="high",
                description="Opportunity to complete implementation",
                roast_type=RoastType.ANTI_ROAST,
                style=style,
                evidence=[f"Ask indicates incomplete work"],
                recommendations=["Consider completing this implementation", "This would strengthen the system"],
                constructive_feedback="This is an opportunity to enhance the system. Consider the benefits of completing this work."
            )
            findings.append(finding)

        # Constructive flow state feedback
        if any(word in ask_lower for word in ["flow", "performance", "enhance"]):
            finding = RoastFinding(
                finding_id=f"anti_flow_{int(datetime.now().timestamp() * 1000)}",
                category="flow_state",
                severity="medium",
                description="Flow state enhancement opportunity",
                roast_type=RoastType.ANTI_ROAST,
                style=style,
                evidence=[f"Ask mentions flow state"],
                recommendations=["Consider flow state enhancers", "This could improve productivity"],
                constructive_feedback="Flow state enhancers can significantly improve workflow performance. Consider implementing them."
            )
            findings.append(finding)

        return findings

    def _generate_roast_message(self, agent_config: Dict[str, Any], roast: UniversalRoast, message_type: str) -> str:
        """Generate character-specific roast message"""
        quotes = agent_config.get("quotes", [])
        if not quotes:
            return ""

        # Select quote based on findings
        if roast.findings:
            quote = quotes[0]  # Use first quote
        else:
            quote = quotes[-1] if len(quotes) > 1 else quotes[0]

        # For anti-roast, use anti-roast quotes if available
        if message_type == "anti_roast" and agent_config.get("anti_roast_quotes"):
            quote = agent_config["anti_roast_quotes"][0]

        # Build message
        if message_type == "roast":
            message = f"{quote}\n\n"
            if roast.findings:
                message += f"Found {len(roast.findings)} issues: {roast.gap_count} gaps, {roast.bloat_count} bloat, {roast.flow_state_issues} flow state issues."
        else:  # anti_roast
            message = f"{quote}\n\n"
            if roast.findings:
                message += f"Identified {len(roast.findings)} opportunities for improvement. Consider these enhancements."

        return message

    def _generate_roast_summary(self, roast: UniversalRoast, agent_config: Dict[str, Any]) -> str:
        """Generate roast summary"""
        agent_name = agent_config["name"]
        roast_type_str = "ROAST" if roast.roast_type == RoastType.ROAST else "ANTI-ROAST" if roast.roast_type == RoastType.ANTI_ROAST else "ROAST + ANTI-ROAST"

        if not roast.findings:
            return f"✅ {agent_name} ({roast_type_str}): No issues found. Ask is clean."

        parts = []
        if roast.gap_count > 0:
            parts.append(f"{roast.gap_count} gap(s)")
        if roast.bloat_count > 0:
            parts.append(f"{roast.bloat_count} bloat issue(s)")
        if roast.flow_state_issues > 0:
            parts.append(f"{roast.flow_state_issues} flow state issue(s)")

        summary = f"🔥 {agent_name} ({roast_type_str}): {', '.join(parts)}. Severity: {roast.total_severity_score:.1f}"

        return summary

    def _save_roast(self, roast: UniversalRoast):
        """Save roast to file"""
        try:
            with open(self.roasts_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(roast.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Error saving roast: {e}")

    def get_roast_for_ask(self, ask_id: str, agent_id: Optional[str] = None) -> Optional[UniversalRoast]:
        """Get roast for a specific ask"""
        if not self.roasts_file.exists():
            return None

        try:
            with open(self.roasts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        roast_data = json.loads(line)
                        if roast_data.get("ask_id") == ask_id:
                            if agent_id and roast_data.get("agent_id") != agent_id:
                                continue
                            # Reconstruct roast
                            findings = [RoastFinding(**f) for f in roast_data.get("findings", [])]
                            roast = UniversalRoast(
                                roast_id=roast_data["roast_id"],
                                agent_id=roast_data["agent_id"],
                                agent_name=roast_data["agent_name"],
                                ask_id=roast_data["ask_id"],
                                ask_text=roast_data["ask_text"],
                                timestamp=roast_data["timestamp"],
                                roast_type=RoastType(roast_data["roast_type"]),
                                style=RoastStyle(roast_data["style"]),
                                findings=findings,
                                roast_message=roast_data.get("roast_message", ""),
                                anti_roast_message=roast_data.get("anti_roast_message", ""),
                                summary=roast_data.get("summary", ""),
                                gap_count=roast_data.get("gap_count", 0),
                                bloat_count=roast_data.get("bloat_count", 0),
                                flow_state_issues=roast_data.get("flow_state_issues", 0),
                                total_severity_score=roast_data.get("total_severity_score", 0.0),
                                metadata=roast_data.get("metadata", {})
                            )
                            return roast
        except Exception as e:
            self.logger.error(f"Error loading roast: {e}")

        return None


def main():
    """Main execution for testing"""
    roaster = UniversalRoastSystem()

    print("🔥 Universal Roast System - Flow State Enhancer")
    print("=" * 80)
    print("")

    # Test different agents
    ask_id = "test_ask"
    ask_text = "Our workflows performance is being hampered by lack of flow state enhancers"

    agents = ["marvin", "gandalf", "jedi_council", "jarvis", "upper_management"]

    for agent_id in agents:
        print(f"\n{agent_id.upper()} Roasting:")
        roast = roaster.roast_ask(agent_id, ask_id, ask_text)
        print(f"  Summary: {roast.summary}")
        print(f"  Roast Message: {roast.roast_message[:100]}...")
        if roast.anti_roast_message:
            print(f"  Anti-Roast Message: {roast.anti_roast_message[:100]}...")


if __name__ == "__main__":



    main()