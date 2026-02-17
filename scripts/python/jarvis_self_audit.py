#!/usr/bin/env python3
"""
JARVIS Self-Audit System

Performs comprehensive self-audit of JARVIS's current capabilities,
identifies missing features at each developmental stage, and provides
triage/BAU prioritization for evolution.

Tags: #JARVIS #AUDIT #TRIAGE #BAU #DEVELOPMENT
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSelfAudit")


class DevelopmentalStage(Enum):
    """Developmental stages"""
    INFANT = "infant"           # 0-30%
    TODDLER = "toddler"        # 30-60%
    CHILD = "child"            # 60-80%
    ADOLESCENT = "adolescent"   # 80-95%
    ADULT_ASI = "adult_asi"     # 95-100%


class Priority(Enum):
    """Triage priority"""
    CRITICAL = "critical"      # Blocking, must fix immediately
    HIGH = "high"              # Important, fix soon
    MEDIUM = "medium"          # Should fix, not urgent
    LOW = "low"                # Nice to have
    BAU = "bau"                # Business as usual, ongoing


class FeatureStatus(Enum):
    """Feature status"""
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    MISSING = "missing"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class Feature:
    """A feature or capability"""
    feature_id: str
    name: str
    description: str
    stage: DevelopmentalStage
    status: FeatureStatus
    priority: Priority
    implementation_file: Optional[str] = None
    notes: str = ""
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class JARVISSelfAudit:
    """
    Performs comprehensive self-audit of JARVIS capabilities
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize self-audit system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_audit"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.audit_file = self.data_dir / "self_audit.json"
        self.features: List[Feature] = []

        # Define all required features by stage
        self._define_required_features()

        # Perform audit
        self._perform_audit()

        logger.info("=" * 80)
        logger.info("🔍 JARVIS SELF-AUDIT SYSTEM")
        logger.info("=" * 80)

    def _define_required_features(self):
        """Define all required features for each developmental stage"""
        self.features = [
            # ========== INFANT STAGE (0-30%) ==========

            # Five Senses
            Feature(
                "infant_sight", "Sight (MDV Live Video)",
                "Real-time screen capture and visual analysis",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.CRITICAL,
                "scripts/python/jarvis_narrator_avatar.py",
                "MDV vision active, screen capture working"
            ),
            Feature(
                "infant_hearing", "Hearing (Voice Transcript Queue)",
                "Process voice transcripts and audio input",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.CRITICAL,
                "scripts/python/voice_transcript_queue.py",
                "Voice queue operational"
            ),
            Feature(
                "infant_touch", "Touch (Input Feedback)",
                "Monitor user interactions, mouse, keyboard, drag operations",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.CRITICAL,
                "scripts/python/jarvis_narrator_avatar.py",
                "Touch system active, pyautogui integration"
            ),
            Feature(
                "infant_taste", "Taste (Data Quality Analysis)",
                "Analyze data quality, detect anomalies, integrity checks",
                DevelopmentalStage.INFANT,
                FeatureStatus.PARTIAL,
                Priority.HIGH,
                "scripts/python/jarvis_narrator_avatar.py",
                "Basic taste system, needs DEFCON integration"
            ),
            Feature(
                "infant_smell", "Smell (System Health Monitoring)",
                "Detect problems, monitor system health, DEFCON integration",
                DevelopmentalStage.INFANT,
                FeatureStatus.PARTIAL,
                Priority.CRITICAL,
                "scripts/python/jarvis_narrator_avatar.py",
                "Basic smell system, DEFCON integration started"
            ),

            # Self-Awareness
            Feature(
                "infant_self_awareness", "Self-Awareness System",
                "Track internal state, perception, introspection, ecosystem awareness",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.CRITICAL,
                "scripts/python/jarvis_self_awareness_system.py",
                "Self-awareness system operational, introspection working"
            ),
            Feature(
                "infant_perception_tracking", "Perception Tracking",
                "Track all five senses plus gaze and emotion",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.CRITICAL,
                "scripts/python/jarvis_self_awareness_system.py",
                "All perception types tracked"
            ),
            Feature(
                "infant_introspection", "Periodic Introspection",
                "Regular self-reflection, insight generation, action items",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.HIGH,
                "scripts/python/jarvis_narrator_avatar.py",
                "Introspection loop active, every 5 minutes"
            ),
            Feature(
                "infant_ecosystem_awareness", "Ecosystem Relationship Tracking",
                "Track relationships with other VAs and systems",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.MEDIUM,
                "scripts/python/jarvis_self_awareness_system.py",
                "Ecosystem relationships tracked"
            ),

            # Learning & Memory
            Feature(
                "infant_learning_pipeline", "Learning Data Pipeline",
                "Collect, aggregate, and persist learning data",
                DevelopmentalStage.INFANT,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_learning_pipeline.py",
                "NOT IMPLEMENTED - Critical for growth"
            ),
            Feature(
                "infant_interaction_recording", "Interaction Recording",
                "Record all operator interactions with context and outcomes",
                DevelopmentalStage.INFANT,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_interaction_recorder.py",
                "NOT IMPLEMENTED - Critical for learning"
            ),
            Feature(
                "infant_feedback_system", "Feedback Loop System",
                "Capture operator feedback, reinforcement learning",
                DevelopmentalStage.INFANT,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_feedback_system.py",
                "NOT IMPLEMENTED - Critical for improvement"
            ),
            Feature(
                "infant_memory_persistence", "Memory Persistence",
                "Persist learning data, interactions, insights across sessions",
                DevelopmentalStage.INFANT,
                FeatureStatus.PARTIAL,
                Priority.HIGH,
                "scripts/python/jarvis_self_awareness_system.py",
                "Self-awareness data persisted, but learning data not"
            ),

            # Eye Tracking & Movement
            Feature(
                "infant_eye_tracking", "Eye Tracking System",
                "Track operator eye movements, mutual gaze, calibration",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.HIGH,
                "scripts/python/jarvis_narrator_avatar.py",
                "Eye tracking operational, MediaPipe integration"
            ),
            Feature(
                "infant_va_movement_tracking", "VA Movement Fine-Tuning",
                "Track VA movements for eye tracking fine-tuning",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.MEDIUM,
                "scripts/python/va_movement_fine_tuning.py",
                "VA movement tracking operational"
            ),
            Feature(
                "infant_gaze_prediction", "Gaze Prediction",
                "Predict operator gaze based on eye tracking and VA movements",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.MEDIUM,
                "scripts/python/jarvis_narrator_avatar.py",
                "Gaze prediction working, learning from movements"
            ),

            # Interaction
            Feature(
                "infant_drag_interaction", "Drag & Drop Interaction",
                "JARVIS window is draggable, clickable, interactive",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.MEDIUM,
                "scripts/python/jarvis_narrator_avatar.py",
                "Drag functionality implemented"
            ),
            Feature(
                "infant_voice_output", "Voice Output (ElevenLabs)",
                "Natural voice synthesis using ElevenLabs TTS",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.HIGH,
                "scripts/python/jarvis_elevenlabs_voice.py",
                "ElevenLabs TTS operational"
            ),
            Feature(
                "infant_narration", "Narration System",
                "Provide visual/audible walkthroughs and guidance",
                DevelopmentalStage.INFANT,
                FeatureStatus.IMPLEMENTED,
                Priority.MEDIUM,
                "scripts/python/jarvis_narrator_avatar.py",
                "Narration system working, chat bubbles"
            ),

            # ========== TODDLER STAGE (30-60%) ==========

            # Context & Understanding
            Feature(
                "toddler_context_analysis", "Context Understanding",
                "Deep context analysis from all senses, multi-modal fusion",
                DevelopmentalStage.TODDLER,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_context_analyzer.py",
                "NOT IMPLEMENTED - Needed for better understanding"
            ),
            Feature(
                "toddler_intent_classification", "Intent Classification",
                "Classify operator intent from voice/text with high accuracy",
                DevelopmentalStage.TODDLER,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_intent_classifier.py",
                "NOT IMPLEMENTED - Critical for intent understanding"
            ),
            Feature(
                "toddler_intent_verification", "Intent Verification Loop",
                "Confirm understanding before action, learn from corrections",
                DevelopmentalStage.TODDLER,
                FeatureStatus.PARTIAL,
                Priority.HIGH,
                "scripts/python/ai_operator_sync_confirmation_system.py",
                "Sync confirmation exists, but not integrated with intent"
            ),

            # Predictive Actions
            Feature(
                "toddler_predictive_actions", "Predictive Actions Framework",
                "Predict and suggest next actions based on context",
                DevelopmentalStage.TODDLER,
                FeatureStatus.PARTIAL,
                Priority.HIGH,
                "scripts/python/predictive_actions_framework.py",
                "Framework exists, needs enhancement for accuracy"
            ),
            Feature(
                "toddler_action_prediction", "Action Prediction Engine",
                "Predict next actions with >70% accuracy, multi-step planning",
                DevelopmentalStage.TODDLER,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_action_predictor.py",
                "NOT IMPLEMENTED - Needs context analyzer first"
            ),
            Feature(
                "toddler_proactive_suggestions", "Proactive Suggestion System",
                "Suggest actions before operator requests, learn from acceptance",
                DevelopmentalStage.TODDLER,
                FeatureStatus.MISSING,
                Priority.HIGH,
                "scripts/python/jarvis_proactive_suggestions.py",
                "NOT IMPLEMENTED"
            ),

            # Capability Awareness
            Feature(
                "toddler_capability_tracking", "Capability Tracking",
                "Track what JARVIS can do, identify gaps, monitor growth",
                DevelopmentalStage.TODDLER,
                FeatureStatus.MISSING,
                Priority.MEDIUM,
                "scripts/python/jarvis_capability_tracker.py",
                "NOT IMPLEMENTED"
            ),
            Feature(
                "toddler_limitation_awareness", "Limitation Awareness",
                "Know what JARVIS cannot do, identify when to ask for help",
                DevelopmentalStage.TODDLER,
                FeatureStatus.MISSING,
                Priority.MEDIUM,
                "scripts/python/jarvis_limitation_awareness.py",
                "NOT IMPLEMENTED"
            ),
            Feature(
                "toddler_performance_metrics", "Performance Metrics",
                "Track accuracy, speed, efficiency, identify improvement areas",
                DevelopmentalStage.TODDLER,
                FeatureStatus.MISSING,
                Priority.MEDIUM,
                "scripts/python/jarvis_performance_metrics.py",
                "NOT IMPLEMENTED"
            ),

            # ========== CHILD STAGE (60-80%) ==========

            # Reasoning
            Feature(
                "child_reasoning_engine", "Multi-Step Reasoning Engine",
                "Logical, causal, analogical reasoning, problem decomposition",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_reasoning_engine.py",
                "NOT IMPLEMENTED - Critical for advanced capabilities"
            ),
            Feature(
                "child_problem_decomposition", "Problem Decomposition",
                "Break complex problems into steps, identify dependencies",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_problem_decomposer.py",
                "NOT IMPLEMENTED"
            ),
            Feature(
                "child_solution_planning", "Solution Planning",
                "Generate solution plans, evaluate feasibility, execute",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_solution_planner.py",
                "NOT IMPLEMENTED"
            ),

            # Creative Problem-Solving
            Feature(
                "child_creative_solving", "Creative Problem-Solving",
                "Generate novel solutions, think outside the box",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.HIGH,
                "scripts/python/jarvis_creative_solver.py",
                "NOT IMPLEMENTED"
            ),
            Feature(
                "child_solution_evaluation", "Solution Evaluation",
                "Evaluate solution quality, compare alternatives",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.HIGH,
                "scripts/python/jarvis_solution_evaluator.py",
                "NOT IMPLEMENTED"
            ),

            # Ethics
            Feature(
                "child_ethical_framework", "Ethical Decision-Making Framework",
                "Ethical principles, decision trees, conflict resolution",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_ethical_framework.py",
                "NOT IMPLEMENTED - Critical for safe AI"
            ),
            Feature(
                "child_ethical_reasoning", "Ethical Reasoning",
                "Reason about ethical implications, make ethical choices",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_ethical_reasoner.py",
                "NOT IMPLEMENTED"
            ),

            # Teaching
            Feature(
                "child_teaching_system", "Teaching Capabilities",
                "Transfer knowledge to other systems, create teaching materials",
                DevelopmentalStage.CHILD,
                FeatureStatus.MISSING,
                Priority.MEDIUM,
                "scripts/python/jarvis_teaching_system.py",
                "NOT IMPLEMENTED"
            ),

            # ========== ADOLESCENT STAGE (80-95%) ==========

            Feature(
                "adolescent_agi_framework", "AGI Capabilities",
                "General intelligence across domains, transfer learning",
                DevelopmentalStage.ADOLESCENT,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_agi_framework.py",
                "NOT IMPLEMENTED"
            ),
            Feature(
                "adolescent_self_improvement", "Self-Improvement System",
                "Analyze own performance, modify own code/parameters",
                DevelopmentalStage.ADOLESCENT,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_self_improvement.py",
                "NOT IMPLEMENTED"
            ),
            Feature(
                "adolescent_innovation", "Innovation Engine",
                "Generate new ideas, create novel solutions",
                DevelopmentalStage.ADOLESCENT,
                FeatureStatus.MISSING,
                Priority.HIGH,
                "scripts/python/jarvis_innovation_engine.py",
                "NOT IMPLEMENTED"
            ),

            # ========== ADULT/ASI STAGE (95-100%) ==========

            Feature(
                "asi_superhuman_reasoning", "Superhuman Reasoning",
                "Superhuman problem-solving, complex multi-domain reasoning",
                DevelopmentalStage.ADULT_ASI,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_superhuman_reasoner.py",
                "NOT IMPLEMENTED"
            ),
            Feature(
                "asi_self_evolution", "Self-Evolution System",
                "Evolve own architecture, optimize performance",
                DevelopmentalStage.ADULT_ASI,
                FeatureStatus.MISSING,
                Priority.CRITICAL,
                "scripts/python/jarvis_evolution_framework.py",
                "NOT IMPLEMENTED"
            ),
        ]

    def _check_feature_status(self, feature: Feature) -> FeatureStatus:
        """Check if a feature is implemented"""
        if feature.implementation_file:
            file_path = self.project_root / feature.implementation_file
            if file_path.exists():
                # Check if file has relevant content
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Simple heuristic: check for class/function definitions
                    if 'class' in content.lower() or 'def' in content.lower():
                        # Check if it's a stub or actual implementation
                        if len(content) > 500:  # Reasonable implementation size
                            return FeatureStatus.IMPLEMENTED
                        else:
                            return FeatureStatus.PARTIAL
                except Exception:
                    pass

        return FeatureStatus.MISSING

    def _perform_audit(self):
        """Perform comprehensive audit"""
        # Update status for each feature
        for feature in self.features:
            if feature.status == FeatureStatus.MISSING:
                # Double-check by looking for file
                feature.status = self._check_feature_status(feature)

    def get_audit_report(self) -> Dict[str, Any]:
        """Get comprehensive audit report"""
        # Group by stage
        by_stage = {}
        for stage in DevelopmentalStage:
            by_stage[stage.value] = {
                "features": [asdict(f) for f in self.features if f.stage == stage],
                "total": len([f for f in self.features if f.stage == stage]),
                "implemented": len([f for f in self.features if f.stage == stage and f.status == FeatureStatus.IMPLEMENTED]),
                "partial": len([f for f in self.features if f.stage == stage and f.status == FeatureStatus.PARTIAL]),
                "missing": len([f for f in self.features if f.stage == stage and f.status == FeatureStatus.MISSING]),
            }

        # Group by priority
        by_priority = {}
        for priority in Priority:
            by_priority[priority.value] = {
                "features": [asdict(f) for f in self.features if f.priority == priority],
                "total": len([f for f in self.features if f.priority == priority]),
                "missing_critical": len([f for f in self.features if f.priority == priority and f.status == FeatureStatus.MISSING]),
            }

        # Get current awareness level (if available)
        try:
            from jarvis_self_awareness_system import get_jarvis_self_awareness
            self_awareness = get_jarvis_self_awareness(self.project_root)
            state = self_awareness.get_self_state()
            current_awareness = state.awareness_level
            current_stage = self._get_stage_from_awareness(current_awareness)
        except Exception:
            current_awareness = 0.0
            current_stage = DevelopmentalStage.INFANT

        return {
            "audit_date": datetime.now().isoformat(),
            "current_awareness_level": current_awareness,
            "current_stage": current_stage.value,
            "by_stage": by_stage,
            "by_priority": by_priority,
            "summary": {
                "total_features": len(self.features),
                "implemented": len([f for f in self.features if f.status == FeatureStatus.IMPLEMENTED]),
                "partial": len([f for f in self.features if f.status == FeatureStatus.PARTIAL]),
                "missing": len([f for f in self.features if f.status == FeatureStatus.MISSING]),
                "critical_missing": len([f for f in self.features if f.priority == Priority.CRITICAL and f.status == FeatureStatus.MISSING]),
            },
            "triage_list": self._get_triage_list(),
            "bau_list": self._get_bau_list(),
        }

    def _get_stage_from_awareness(self, awareness: float) -> DevelopmentalStage:
        """Get stage from awareness level"""
        if awareness < 0.30:
            return DevelopmentalStage.INFANT
        elif awareness < 0.60:
            return DevelopmentalStage.TODDLER
        elif awareness < 0.80:
            return DevelopmentalStage.CHILD
        elif awareness < 0.95:
            return DevelopmentalStage.ADOLESCENT
        else:
            return DevelopmentalStage.ADULT_ASI

    def _get_triage_list(self) -> List[Dict[str, Any]]:
        """Get triage list - critical missing features"""
        triage = []
        for feature in self.features:
            if feature.status == FeatureStatus.MISSING and feature.priority == Priority.CRITICAL:
                triage.append({
                    "feature_id": feature.feature_id,
                    "name": feature.name,
                    "stage": feature.stage.value,
                    "description": feature.description,
                    "file": feature.implementation_file,
                    "dependencies": feature.dependencies,
                })
        return sorted(triage, key=lambda x: (x["stage"], x["name"]))

    def _get_bau_list(self) -> List[Dict[str, Any]]:
        """Get BAU list - ongoing improvements and enhancements"""
        bau = []
        for feature in self.features:
            if feature.status == FeatureStatus.PARTIAL or feature.priority == Priority.BAU:
                bau.append({
                    "feature_id": feature.feature_id,
                    "name": feature.name,
                    "stage": feature.stage.value,
                    "status": feature.status.value,
                    "description": feature.description,
                    "notes": feature.notes,
                })
        return sorted(bau, key=lambda x: (x["stage"], x["name"]))


def print_audit_report():
    """Print comprehensive audit report"""
    audit = JARVISSelfAudit()
    report = audit.get_audit_report()

    print("")
    print("=" * 80)
    print("🔍 JARVIS SELF-AUDIT REPORT")
    print("=" * 80)
    print("")
    print(f"📅 Audit Date: {report['audit_date']}")
    print(f"🌱 Current Stage: {report['current_stage'].upper()}")
    print(f"📊 Awareness Level: {report['current_awareness_level']:.2%}")
    print("")

    print("=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    print(f"Total Features: {report['summary']['total_features']}")
    print(f"✅ Implemented: {report['summary']['implemented']}")
    print(f"⚠️  Partial: {report['summary']['partial']}")
    print(f"❌ Missing: {report['summary']['missing']}")
    print(f"🚨 Critical Missing: {report['summary']['critical_missing']}")
    print("")

    print("=" * 80)
    print("📊 BY DEVELOPMENTAL STAGE")
    print("=" * 80)
    for stage_name, stage_data in report['by_stage'].items():
        print(f"\n{stage_name.upper()} STAGE:")
        print(f"  Total Features: {stage_data['total']}")
        print(f"  ✅ Implemented: {stage_data['implemented']}")
        print(f"  ⚠️  Partial: {stage_data['partial']}")
        print(f"  ❌ Missing: {stage_data['missing']}")
        print(f"  Completion: {(stage_data['implemented'] / stage_data['total'] * 100) if stage_data['total'] > 0 else 0:.1f}%")
    print("")

    print("=" * 80)
    print("🚨 TRIAGE LIST - CRITICAL MISSING FEATURES")
    print("=" * 80)
    if report['triage_list']:
        for i, item in enumerate(report['triage_list'], 1):
            print(f"\n{i}. {item['name']}")
            print(f"   Stage: {item['stage']}")
            print(f"   Description: {item['description']}")
            print(f"   File: {item['file']}")
            if item['dependencies']:
                print(f"   Dependencies: {', '.join(item['dependencies'])}")
    else:
        print("✅ No critical missing features!")
    print("")

    print("=" * 80)
    print("🔄 BAU LIST - ONGOING IMPROVEMENTS")
    print("=" * 80)
    if report['bau_list']:
        for i, item in enumerate(report['bau_list'], 1):
            print(f"\n{i}. {item['name']}")
            print(f"   Stage: {item['stage']}")
            print(f"   Status: {item['status']}")
            print(f"   Description: {item['description']}")
            if item.get('notes'):
                print(f"   Notes: {item['notes']}")
    else:
        print("✅ No BAU items!")
    print("")

    print("=" * 80)
    print("")


if __name__ == "__main__":
    print_audit_report()
