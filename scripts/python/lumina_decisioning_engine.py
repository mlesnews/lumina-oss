#!/usr/bin/env python3
"""
LUMINA Decisioning Engine

Automatic decision-making using #DECISIONING workflows.
Always returns to the same state (saves all work).

Key principle: All changes are changes, no matter how small.
An AI chat session is a change - must be saved.

Tags: #DECISIONING #AUTOMATION #WORKFLOW #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("DecisioningEngine")

# Import SYPHON Threat & Risk Escalation
try:
    from syphon_threat_risk_escalation import (
        SYPHONThreatRiskEscalation,
        CustomerImpactAssessment,
        CustomerImpactLevel,
        ThreatAssessment,
        ThreatSeverity,
        RiskAssessment,
        RiskLevel,
        get_escalation_system
    )
    ESCALATION_AVAILABLE = True
except ImportError:
    ESCALATION_AVAILABLE = False
    logger.warning("⚠️  SYPHON Threat & Risk Escalation not available")


class DecisionContext(Enum):
    """Decision contexts"""
    CURSOR_CHANGES = "cursor_changes"  # Cursor IDE "Keep All" button
    VOICE_INPUT = "voice_input"
    FILE_EDIT = "file_edit"
    WORKFLOW_TRIGGER = "workflow_trigger"
    SYSTEM_EVENT = "system_event"


class DecisionAction(Enum):
    """Decision actions"""
    KEEP_ALL = "keep_all"
    DISCARD = "discard"
    REVIEW = "review"
    MERGE = "merge"
    SAVE = "save"
    CONTINUE = "continue"


class LuminaDecisioningEngine:
    """
    Decision-making engine for LUMINA

    Automatically determines actions using #DECISIONING workflows.
    Always returns to the same state (saves all work).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize decisioning engine"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.config_file = self.config_dir / "decisioning_config.json"
        self.config = self._load_config()

        # Decision history
        self.decision_history: List[Dict[str, Any]] = []
        self.history_file = self.project_root / "data" / "decisioning_history.jsonl"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize SYPHON Threat & Risk Escalation
        self.escalation_system = None
        if ESCALATION_AVAILABLE:
            try:
                self.escalation_system = get_escalation_system()
                logger.info("✅ SYPHON Threat & Risk Escalation integrated")
            except Exception as e:
                logger.warning(f"⚠️  Escalation system init error: {e}")

        # Initialize AI Agent Live Monitor for transparency
        try:
            from ai_agent_live_monitor import get_live_monitor
            self.live_monitor = get_live_monitor()
            logger.info("✅ AI Agent Live Monitor integrated for transparency")
        except Exception as e:
            logger.warning(f"⚠️  Live monitor init error: {e}")
            self.live_monitor = None

    def _load_config(self) -> Dict[str, Any]:
        """Load decisioning configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")

        return {
            "version": "1.0.0",
            "default_action": "keep_all",
            "always_save": True,
            "decision_rules": {
                "cursor_changes": {
                    "action": "keep_all",
                    "auto_apply": True,
                    "save_state": True
                },
                "voice_input": {
                    "action": "save",
                    "auto_apply": True,
                    "save_state": True
                },
                "file_edit": {
                    "action": "save",
                    "auto_apply": True,
                    "save_state": True
                }
            },
            "description": "LUMINA Decisioning Engine - Automatic decision-making",
            "tags": ["#DECISIONING", "#AUTOMATION", "#WORKFLOW", "@JARVIS", "@LUMINA"]
        }

    def make_decision(
        self,
        context: DecisionContext,
        details: Dict[str, Any],
        user_preference: Optional[str] = None,
        customer_impact: Optional[Dict[str, Any]] = None,
        threat_assessment: Optional[Dict[str, Any]] = None,
        risk_assessment: Optional[Dict[str, Any]] = None
    ) -> DecisionAction:
        """
        Make automatic decision based on context

        Key principle: All changes are changes, no matter how small.
        Always save work and return to same state.

        #CUSTOMER #IMPACT is HIGHEST PRIORITY (top 3 at least)
        """
        logger.debug(f"   🤔 Decisioning: {context.value}")

        # Check for escalation requirements (3-5-7-9 escalation)
        if self.escalation_system and (customer_impact or threat_assessment or risk_assessment):
            try:
                # Build assessments
                customer_impact_obj = None
                if customer_impact:
                    customer_impact_obj = CustomerImpactAssessment(
                        impact_id=customer_impact.get("impact_id", f"impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                        level=CustomerImpactLevel(customer_impact.get("level", "none")),
                        description=customer_impact.get("description", ""),
                        affected_customers=customer_impact.get("affected_customers", 0),
                        affected_features=customer_impact.get("affected_features", []),
                        business_impact=customer_impact.get("business_impact", ""),
                        urgency=customer_impact.get("urgency", "normal")
                    )

                threat_obj = None
                if threat_assessment:
                    threat_obj = ThreatAssessment(
                        threat_id=threat_assessment.get("threat_id", f"threat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                        threat_type=threat_assessment.get("threat_type", "unknown"),
                        severity=ThreatSeverity(threat_assessment.get("severity", "low")),
                        description=threat_assessment.get("description", ""),
                        confidence=threat_assessment.get("confidence", 0.0)
                    )

                risk_obj = None
                if risk_assessment:
                    risk_obj = RiskAssessment(
                        risk_id=risk_assessment.get("risk_id", f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                        risk_type=risk_assessment.get("risk_type", "unknown"),
                        level=RiskLevel(risk_assessment.get("level", "low")),
                        description=risk_assessment.get("description", ""),
                        probability=risk_assessment.get("probability", 0.0),
                        impact=risk_assessment.get("impact", 0.0)
                    )

                # Assess and escalate
                escalation_decision = self.escalation_system.assess_and_escalate(
                    context=details,
                    customer_impact=customer_impact_obj,
                    threat_assessment=threat_obj,
                    risk_assessment=risk_obj
                )

                # Execute escalation
                escalation_result = self.escalation_system.execute_escalation(escalation_decision)

                # Log escalation
                logger.info(f"   🚨 ESCALATION: Level {escalation_decision.escalation_level.value} → {escalation_decision.target}")

                # Add escalation info to details
                details["escalation"] = {
                    "level": escalation_decision.escalation_level.value,
                    "target": escalation_decision.target,
                    "priority": escalation_decision.priority,
                    "result": escalation_result
                }
            except Exception as e:
                logger.warning(f"⚠️  Escalation assessment error: {e}")

        # Get decision rule for context
        rule = self.config["decision_rules"].get(context.value, {})
        default_action = rule.get("action", self.config["default_action"])

        # Apply user preference if provided
        if user_preference:
            action_str = user_preference
        else:
            action_str = default_action

        # Convert to DecisionAction enum
        try:
            action = DecisionAction(action_str)
        except ValueError:
            action = DecisionAction.KEEP_ALL  # Safe default

        # Log decision
        decision = {
            "timestamp": datetime.now().isoformat(),
            "context": context.value,
            "action": action.value,
            "details": details,
            "auto_applied": rule.get("auto_apply", False)
        }

        self.decision_history.append(decision)
        self._save_decision(decision)

        # Update live monitor with current task
        if self.live_monitor:
            try:
                task_description = f"{context.value}: {action.value}"
                self.live_monitor.set_current_task(task_description)
            except Exception as e:
                logger.warning(f"⚠️  Live monitor update error: {e}")

        logger.info(f"   ✅ Decision: {action.value} for {context.value}")

        return action

    def handle_cursor_changes(self, changes: Dict[str, Any]) -> DecisionAction:
        """
        Handle Cursor IDE "Keep All" button scenario

        Automatic decision: Always keep all changes and save state.
        """
        logger.info("   📝 Cursor changes detected - applying #DECISIONING")

        # All changes are changes, no matter how small
        # An AI chat session is a change - must be saved
        decision = self.make_decision(
            context=DecisionContext.CURSOR_CHANGES,
            details={
                "change_count": changes.get("count", 0),
                "files_modified": changes.get("files", []),
                "source": "cursor_ide"
            }
        )

        # Always save state
        if self.config["always_save"]:
            self._save_state(changes)

        return decision

    def handle_voice_input(self, transcription: str, metadata: Dict[str, Any]) -> DecisionAction:
        """
        Handle voice input (transcribed text)

        Automatic decision: Save voice input as change.
        """
        logger.debug(f"   🎤 Voice input: {len(transcription)} chars")

        decision = self.make_decision(
            context=DecisionContext.VOICE_INPUT,
            details={
                "transcription_length": len(transcription),
                "metadata": metadata
            }
        )

        # Save voice input as change
        if self.config["always_save"]:
            self._save_voice_input(transcription, metadata)

        return decision

    def _save_state(self, changes: Dict[str, Any]):
        """Save current state (all work)"""
        try:
            state_dir = self.project_root / "data" / "decisioning_states"
            state_dir.mkdir(parents=True, exist_ok=True)

            state_file = state_dir / f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            state = {
                "timestamp": datetime.now().isoformat(),
                "changes": changes,
                "project_root": str(self.project_root)
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.debug(f"   💾 State saved: {state_file.name}")
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save state: {e}")

    def _save_voice_input(self, transcription: str, metadata: Dict[str, Any]):
        """Save voice input as change"""
        try:
            voice_dir = self.project_root / "data" / "voice_inputs"
            voice_dir.mkdir(parents=True, exist_ok=True)

            voice_file = voice_dir / f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

            with open(voice_file, 'w', encoding='utf-8') as f:
                f.write(f"# Voice Input\n\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Metadata: {json.dumps(metadata, indent=2)}\n\n")
                f.write(f"Transcription:\n{transcription}\n")

            logger.debug(f"   💾 Voice input saved: {voice_file.name}")
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save voice input: {e}")

    def _save_decision(self, decision: Dict[str, Any]):
        """Save decision to history"""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(decision) + '\n')
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save decision: {e}")

    def get_decision_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        return self.decision_history[-limit:]


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Decisioning Engine")
    parser.add_argument("--context", choices=[c.value for c in DecisionContext], help="Decision context")
    parser.add_argument("--test", action="store_true", help="Test decisioning")

    args = parser.parse_args()

    engine = LuminaDecisioningEngine()

    if args.test:
        # Test Cursor changes scenario
        result = engine.handle_cursor_changes({
            "count": 3,
            "files": ["test.py", "config.json"]
        })
        logger.info(f"   ✅ Test result: {result.value}")

    return 0


if __name__ == "__main__":


    sys.exit(main())