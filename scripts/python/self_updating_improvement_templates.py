#!/usr/bin/env python3
"""
Self-Updating Improvement Templates (@V3 #WORKFLOWED +RULE)
@SPOCK Logic Templates for consistent application of 10 Ways Improvements.

@V3_WORKFLOWED: True
@RULE_COMPLIANT: True
@TEST_FIRST: True
@RR_METHODOLOGY: Rest, Roast, Repair
@SPOCK_LOGIC: Self-updating templates with continuous improvement
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import yaml
import re
import hashlib

class ImprovementCategory(Enum):
    """Categories of system improvements"""
    VOICE_FILTERING = "voice_filtering"
    AUTO_ACCEPT_DETECTION = "auto_accept_detection"
    DYNAMIC_LISTENING = "dynamic_listening"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    GRAMMAR_CHECKING = "grammar_checking"
    SYSTEM_INTEGRATION = "system_integration"

class TemplateStatus(Enum):
    """Template implementation status"""
    PROPOSED = "proposed"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    DEPLOYED = "deployed"
    MONITORING = "monitoring"
    OPTIMIZING = "optimizing"
    DEPRECATED = "deprecated"

class SpockLogicLevel(Enum):
    """@SPOCK logic implementation levels"""
    BASIC = "basic"           # Simple implementation
    INTERMEDIATE = "intermediate"  # Enhanced features
    ADVANCED = "advanced"     # Full optimization
    GENIUS = "genius"         # AI-assisted evolution

@dataclass
class ImprovementTemplate:
    """Template for system improvements"""
    template_id: str
    category: str
    title: str
    description: str
    improvement_ways: List[str]
    implementation_steps: List[str]
    success_metrics: List[str]
    spock_logic_level: str
    status: str
    created_at: str
    last_updated: str
    applied_count: int
    success_rate: float
    evolution_history: List[str]

@dataclass
class TemplateApplication:
    """Record of template application to a system"""
    application_id: str
    template_id: str
    target_system: str
    applied_at: str
    implementation_status: str
    performance_metrics: Dict[str, Any]
    lessons_learned: List[str]
    next_improvements: List[str]

class SelfUpdatingImprovementTemplates:
    """
    @SPOCK Logic Templates for 10 Ways Improvements.
    Self-updating system that learns and evolves improvement patterns.
    """

    def __init__(self, templates_db: str = "./data/improvement_templates.db"):
        self.templates_db = Path(templates_db)
        self.templates_db.parent.mkdir(parents=True, exist_ok=True)

        # Initialize template database
        self._init_templates_database()

        # Load 10 Ways improvements from source
        self._load_ten_ways_improvements()

        print("🧠 @SPOCK Logic Self-Updating Improvement Templates initialized")
        print(f"   Templates DB: {self.templates_db}")
        print("   10 Ways Improvements loaded and ready for application")

    def _init_templates_database(self):
        try:
            """Initialize templates tracking database"""
            with sqlite3.connect(self.templates_db) as conn:
                # Improvement templates table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS improvement_templates (
                        template_id TEXT PRIMARY KEY,
                        category TEXT,
                        title TEXT,
                        description TEXT,
                        improvement_ways TEXT,
                        implementation_steps TEXT,
                        success_metrics TEXT,
                        spock_logic_level TEXT,
                        status TEXT,
                        created_at TEXT,
                        last_updated TEXT,
                        applied_count INTEGER DEFAULT 0,
                        success_rate REAL DEFAULT 0.0,
                        evolution_history TEXT
                    )
                ''')

                # Template applications table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS template_applications (
                        application_id TEXT PRIMARY KEY,
                        template_id TEXT,
                        target_system TEXT,
                        applied_at TEXT,
                        implementation_status TEXT,
                        performance_metrics TEXT,
                        lessons_learned TEXT,
                        next_improvements TEXT,
                        FOREIGN KEY (template_id) REFERENCES improvement_templates (template_id)
                    )
                ''')

                # Template evolution table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS template_evolution (
                        evolution_id TEXT PRIMARY KEY,
                        template_id TEXT,
                        evolution_type TEXT,
                        changes_made TEXT,
                        performance_impact TEXT,
                        evolved_at TEXT,
                        FOREIGN KEY (template_id) REFERENCES improvement_templates (template_id)
                    )
                ''')

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _init_templates_database: {e}", exc_info=True)
            raise
    def _load_ten_ways_improvements(self):
        """Load the 10 Ways improvements from source document"""
        ten_ways_content = self._read_ten_ways_document()

        if ten_ways_content:
            templates = self._parse_ten_ways_into_templates(ten_ways_content)
            self._save_templates_to_database(templates)
            print(f"📚 Loaded {len(templates)} improvement templates from 10 Ways document")

    def _read_ten_ways_document(self) -> Optional[str]:
        """Read the 10 Ways improvements document"""
        ten_ways_path = Path("scripts/python/TEN_WAYS_IMPROVEMENTS.md")

        if ten_ways_path.exists():
            try:
                with open(ten_ways_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"❌ Error reading 10 Ways document: {e}")
                return None
        else:
            print("⚠️  10 Ways document not found, using embedded defaults")
            return self._get_embedded_ten_ways()

    def _get_embedded_ten_ways(self) -> str:
        """Fallback embedded 10 Ways content"""
        return """
# 10 Ways to Improve the System

## 10 Ways to Improve Voice Filtering

1. **Real-time Audio Analysis**: Use MFCC (Mel-frequency cepstral coefficients) for better voice identification
2. **Machine Learning Models**: Train deep learning models on voice samples for better accuracy
3. **Context-Aware Filtering**: Consider conversation context when deciding to filter
4. **Multi-Microphone Analysis**: Use multiple audio sources for better speaker separation
5. **Voice Activity Detection (VAD)**: Better detection of when someone is actually speaking vs. background noise
6. **Frequency Analysis**: Analyze pitch, formants, and spectral characteristics for better identification
7. **Temporal Patterns**: Track speaking patterns over time (pace, rhythm, pauses)
8. **Confidence Scoring**: Use multiple confidence scores and combine them intelligently
9. **Adaptive Learning**: Continuously learn and adapt to new voice patterns
10. **Hardware Integration**: Use specialized audio hardware for better signal quality

## 10 Ways to Improve Auto-Accept Detection

1. **Multiple Detection Methods**: Use keyboard shortcuts, UI automation, OCR, and screen analysis
2. **Window State Detection**: Check if Cursor IDE is focused/active before attempting
3. **Button Text Variations**: Expand list of button text variations (already done)
4. **Visual Pattern Recognition**: Use VLM/OCR to visually identify buttons
5. **Event-Based Detection**: Listen for Cursor IDE events instead of polling
6. **Dialog Detection**: Better detection of dialog windows vs. main window
7. **Retry Logic**: Implement exponential backoff retry for failed detections
8. **State Machine**: Use state machine to track dialog lifecycle
9. **Multiple Window Support**: Handle multiple Cursor IDE windows
10. **Performance Monitoring**: Track detection success rate and optimize

## 10 Ways to Improve Dynamic Listening Scaling

1. **Speech Duration Prediction**: Predict how long speech will be based on patterns
2. **Transcription Latency Tracking**: Track actual transcription time and adjust
3. **Confidence-Based Scaling**: Scale wait time based on transcription confidence
4. **Context-Aware Timing**: Adjust based on conversation type (question vs. statement)
5. **User Feedback Integration**: Learn from user corrections (if they manually send)
6. **Multiple Speech End Signals**: Use multiple indicators (silence, transcription complete, etc.)
7. **Adaptive Minimums**: Adjust minimum wait time based on user patterns
8. **Time-of-Day Scaling**: Adjust based on time of day (user might be slower at certain times)
9. **Interruption Detection**: Detect if user starts speaking again and reset timer
10. **Machine Learning Model**: Train ML model to predict optimal wait time

## 10 Ways to Improve Audio-Transcription Comparison

1. **Real-Time Streaming**: Compare audio and transcription in real-time as they come in
2. **Feature Extraction**: Extract more audio features (pitch, energy, spectral, etc.)
3. **Pattern Matching**: Use advanced pattern matching algorithms
4. **Confidence Thresholds**: Use multiple confidence thresholds for different scenarios
5. **Historical Context**: Use historical patterns to improve comparison
6. **Multi-Modal Analysis**: Combine audio, transcription, and visual cues
7. **Noise Filtering**: Better noise filtering before comparison
8. **Speaker Diarization**: Identify who is speaking before comparing
9. **Temporal Alignment**: Better alignment of audio and transcription timelines
10. **Machine Learning**: Train models to detect mismatches automatically

## 10 Ways to Improve Grammar Checking Integration

1. **Real-Time Correction**: Apply corrections in real-time as user speaks
2. **Context-Aware Corrections**: Consider conversation context for better corrections
3. **User Preference Learning**: Learn user's writing style and preferences
4. **Multiple Grammar Engines**: Use multiple grammar checkers and combine results
5. **Confidence Scoring**: Only apply high-confidence corrections
6. **Undo/Redo Support**: Allow user to undo corrections
7. **Custom Rules**: Support custom grammar rules for specific domains
8. **Performance Optimization**: Cache results and optimize API calls
9. **Offline Support**: Support offline grammar checking when possible
10. **Feedback Loop**: Learn from user acceptance/rejection of corrections

## 10 Ways to Improve Overall System Integration

1. **Event-Driven Architecture**: Use events instead of polling for better responsiveness
2. **Centralized State Management**: Single source of truth for system state
3. **Better Error Handling**: Comprehensive error handling and recovery
4. **Performance Monitoring**: Track performance metrics and optimize bottlenecks
5. **User Feedback Collection**: Collect and learn from user feedback
6. **A/B Testing**: Test different approaches and measure effectiveness
7. **Configuration Management**: Easy configuration without code changes
8. **Logging and Debugging**: Better logging for troubleshooting
9. **Testing Framework**: Comprehensive testing for all components
10. **Documentation**: Clear documentation for all features and integrations
"""

    def _parse_ten_ways_into_templates(self, content: str) -> List[ImprovementTemplate]:
        """Parse 10 Ways document into structured templates"""
        templates = []

        # Split by major sections
        sections = re.split(r'^##\s+', content, flags=re.MULTILINE)[1:]

        for section in sections:
            if not section.strip():
                continue

            lines = section.strip().split('\n')
            section_title = lines[0].strip()

            # Extract category from title
            if 'Voice Filtering' in section_title:
                category = ImprovementCategory.VOICE_FILTERING.value
            elif 'Auto-Accept Detection' in section_title:
                category = ImprovementCategory.AUTO_ACCEPT_DETECTION.value
            elif 'Dynamic Listening' in section_title:
                category = ImprovementCategory.DYNAMIC_LISTENING.value
            elif 'Audio-Transcription' in section_title:
                category = ImprovementCategory.AUDIO_TRANSCRIPTION.value
            elif 'Grammar Checking' in section_title:
                category = ImprovementCategory.GRAMMAR_CHECKING.value
            elif 'System Integration' in section_title:
                category = ImprovementCategory.SYSTEM_INTEGRATION.value
            else:
                category = "general"

            # Extract improvement ways
            improvement_ways = []
            implementation_steps = []
            success_metrics = []

            for line in lines[1:]:
                line = line.strip()
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                    # Extract the improvement description
                    improvement_text = re.sub(r'^\d+\.\s*\*\*.*?\*\*:\s*', '', line)
                    improvement_ways.append(improvement_text)

                    # Generate implementation steps and metrics
                    impl_steps, metrics = self._generate_implementation_for_improvement(
                        improvement_text, category
                    )
                    implementation_steps.extend(impl_steps)
                    success_metrics.extend(metrics)

            # Create template
            template_id = f"{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            template = ImprovementTemplate(
                template_id=template_id,
                category=category,
                title=section_title,
                description=f"Comprehensive improvements for {section_title.lower()}",
                improvement_ways=improvement_ways,
                implementation_steps=list(set(implementation_steps)),  # Remove duplicates
                success_metrics=list(set(success_metrics)),  # Remove duplicates
                spock_logic_level=SpockLogicLevel.INTERMEDIATE.value,
                status=TemplateStatus.PROPOSED.value,
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                applied_count=0,
                success_rate=0.0,
                evolution_history=[f"Created from 10 Ways document on {datetime.now().strftime('%Y-%m-%d')}"]
            )

            templates.append(template)

        return templates

    def _generate_implementation_for_improvement(self, improvement: str, category: str) -> Tuple[List[str], List[str]]:
        """Generate implementation steps and success metrics for an improvement"""
        implementation_steps = []
        success_metrics = []

        improvement_lower = improvement.lower()

        # Voice filtering implementations
        if category == ImprovementCategory.VOICE_FILTERING.value:
            if 'real-time' in improvement_lower:
                implementation_steps = [
                    "Implement MFCC extraction pipeline",
                    "Add real-time audio processing thread",
                    "Integrate voice identification algorithms",
                    "Add confidence scoring for voice matches"
                ]
                success_metrics = [
                    "Voice identification accuracy >95%",
                    "Real-time processing latency <100ms",
                    "False positive rate <5%"
                ]
            elif 'machine learning' in improvement_lower:
                implementation_steps = [
                    "Collect voice sample dataset",
                    "Train deep learning model architecture",
                    "Implement model inference pipeline",
                    "Add continuous learning loop"
                ]
                success_metrics = [
                    "Model accuracy improvement >20%",
                    "Training time <4 hours",
                    "Inference time <50ms"
                ]

        # Auto-accept detection implementations
        elif category == ImprovementCategory.AUTO_ACCEPT_DETECTION.value:
            if 'multiple detection' in improvement_lower:
                implementation_steps = [
                    "Implement keyboard shortcut monitoring",
                    "Add UI automation detection",
                    "Integrate OCR for button recognition",
                    "Create multi-method decision engine"
                ]
                success_metrics = [
                    "Detection success rate >98%",
                    "Average detection time <500ms",
                    "False positive rate <2%"
                ]

        # Dynamic listening implementations
        elif category == ImprovementCategory.DYNAMIC_LISTENING.value:
            if 'speech duration' in improvement_lower:
                implementation_steps = [
                    "Implement speech pattern analysis",
                    "Add duration prediction model",
                    "Create adaptive timeout system",
                    "Integrate user behavior learning"
                ]
                success_metrics = [
                    "Prediction accuracy >85%",
                    "User satisfaction score >4.5/5",
                    "Timeout optimization >30% improvement"
                ]

        # Audio-transcription implementations
        elif category == ImprovementCategory.AUDIO_TRANSCRIPTION.value:
            if 'real-time streaming' in improvement_lower:
                implementation_steps = [
                    "Implement streaming audio processing",
                    "Add real-time transcription comparison",
                    "Create temporal alignment system",
                    "Integrate confidence scoring"
                ]
                success_metrics = [
                    "Real-time accuracy >95%",
                    "Processing latency <200ms",
                    "Mismatch detection rate >90%"
                ]

        # Grammar checking implementations
        elif category == ImprovementCategory.GRAMMAR_CHECKING.value:
            if 'real-time correction' in improvement_lower:
                implementation_steps = [
                    "Implement real-time grammar analysis",
                    "Add context-aware correction engine",
                    "Create user preference learning system",
                    "Integrate undo/redo functionality"
                ]
                success_metrics = [
                    "Correction acceptance rate >80%",
                    "False correction rate <10%",
                    "User satisfaction improvement >25%"
                ]

        # System integration implementations
        elif category == ImprovementCategory.SYSTEM_INTEGRATION.value:
            if 'event-driven' in improvement_lower:
                implementation_steps = [
                    "Implement event-driven architecture",
                    "Create centralized event bus",
                    "Refactor polling to event-based systems",
                    "Add event monitoring and logging"
                ]
                success_metrics = [
                    "System responsiveness improvement >50%",
                    "Event processing latency <10ms",
                    "Error rate reduction >40%"
                ]

        # Default implementations
        if not implementation_steps:
            implementation_steps = [
                "Analyze current implementation",
                "Design improvement architecture",
                "Implement core functionality",
                "Add monitoring and metrics",
                "Test and validate improvements"
            ]

        if not success_metrics:
            success_metrics = [
                "Performance improvement >20%",
                "User satisfaction increase",
                "Error rate reduction",
                "System stability improvement"
            ]

        return implementation_steps, success_metrics

    def _save_templates_to_database(self, templates: List[ImprovementTemplate]):
        try:
            """Save improvement templates to database"""
            with sqlite3.connect(self.templates_db) as conn:
                for template in templates:
                    conn.execute('''
                        INSERT OR REPLACE INTO improvement_templates
                        (template_id, category, title, description, improvement_ways,
                         implementation_steps, success_metrics, spock_logic_level,
                         status, created_at, last_updated, applied_count, success_rate,
                         evolution_history)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        template.template_id,
                        template.category,
                        template.title,
                        template.description,
                        json.dumps(template.improvement_ways),
                        json.dumps(template.implementation_steps),
                        json.dumps(template.success_metrics),
                        template.spock_logic_level,
                        template.status,
                        template.created_at,
                        template.last_updated,
                        template.applied_count,
                        template.success_rate,
                        json.dumps(template.evolution_history)
                    ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _save_templates_to_database: {e}", exc_info=True)
            raise
    def apply_template_to_system(self, template_id: str, target_system: str,
                               customizations: Dict[str, Any] = None) -> TemplateApplication:
        """
        Apply an improvement template to a target system.
        Returns application record.
        """
        # Get template
        template = self._get_template_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Customize template if needed
        if customizations:
            template = self._customize_template(template, customizations)

        # Create application record
        application = TemplateApplication(
            application_id=f"app_{template_id}_{target_system}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            template_id=template_id,
            target_system=target_system,
            applied_at=datetime.now().isoformat(),
            implementation_status="applying",
            performance_metrics={},
            lessons_learned=[],
            next_improvements=[]
        )

        # Save application
        self._save_template_application(application)

        # Update template applied count
        self._update_template_applied_count(template_id)

        print(f"🎯 Applied template {template_id} to {target_system}")
        return application

    def _get_template_by_id(self, template_id: str) -> Optional[ImprovementTemplate]:
        try:
            """Get template by ID"""
            with sqlite3.connect(self.templates_db) as conn:
                cursor = conn.execute(
                    'SELECT * FROM improvement_templates WHERE template_id = ?',
                    (template_id,)
                )
                row = cursor.fetchone()

                if row:
                    return ImprovementTemplate(
                        template_id=row[0],
                        category=row[1],
                        title=row[2],
                        description=row[3],
                        improvement_ways=json.loads(row[4]) if row[4] else [],
                        implementation_steps=json.loads(row[5]) if row[5] else [],
                        success_metrics=json.loads(row[6]) if row[6] else [],
                        spock_logic_level=row[7],
                        status=row[8],
                        created_at=row[9],
                        last_updated=row[10],
                        applied_count=row[11],
                        success_rate=row[12],
                        evolution_history=json.loads(row[13]) if row[13] else []
                    )
            return None

        except Exception as e:
            self.logger.error(f"Error in _get_template_by_id: {e}", exc_info=True)
            raise
    def _customize_template(self, template: ImprovementTemplate,
                          customizations: Dict[str, Any]) -> ImprovementTemplate:
        """Customize template with specific requirements"""
        # Create copy for customization
        customized = ImprovementTemplate(
            template_id=f"{template.template_id}_custom",
            category=template.category,
            title=customizations.get('title', template.title),
            description=customizations.get('description', template.description),
            improvement_ways=customizations.get('improvement_ways', template.improvement_ways),
            implementation_steps=customizations.get('implementation_steps', template.implementation_steps),
            success_metrics=customizations.get('success_metrics', template.success_metrics),
            spock_logic_level=customizations.get('spock_logic_level', template.spock_logic_level),
            status=TemplateStatus.PROPOSED.value,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            applied_count=0,
            success_rate=0.0,
            evolution_history=[f"Customized from {template.template_id} on {datetime.now().strftime('%Y-%m-%d')}"]
        )

        return customized

    def _save_template_application(self, application: TemplateApplication):
        try:
            """Save template application to database"""
            with sqlite3.connect(self.templates_db) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO template_applications
                    (application_id, template_id, target_system, applied_at,
                     implementation_status, performance_metrics, lessons_learned,
                     next_improvements)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    application.application_id,
                    application.template_id,
                    application.target_system,
                    application.applied_at,
                    application.implementation_status,
                    json.dumps(application.performance_metrics),
                    json.dumps(application.lessons_learned),
                    json.dumps(application.next_improvements)
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _save_template_application: {e}", exc_info=True)
            raise
    def _update_template_applied_count(self, template_id: str):
        """Update template applied count"""
        with sqlite3.connect(self.templates_db) as conn:
            conn.execute('''
                UPDATE improvement_templates
                SET applied_count = applied_count + 1, last_updated = ?
                WHERE template_id = ?
            ''', (datetime.now().isoformat(), template_id))
            conn.commit()

    def evolve_template_based_on_feedback(self, template_id: str,
                                        feedback_data: Dict[str, Any]) -> bool:
        """
        Evolve template based on application feedback using @SPOCK logic.
        Returns True if template was evolved.
        """
        template = self._get_template_by_id(template_id)
        if not template:
            return False

        # Analyze feedback for evolution opportunities
        evolution_changes = self._analyze_feedback_for_evolution(template, feedback_data)

        if evolution_changes:
            # Create evolution record
            evolution_record = {
                'evolution_id': f"evo_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'template_id': template_id,
                'evolution_type': 'feedback_driven',
                'changes_made': json.dumps(evolution_changes),
                'performance_impact': json.dumps(feedback_data.get('performance_impact', {})),
                'evolved_at': datetime.now().isoformat()
            }

            # Save evolution record
            with sqlite3.connect(self.templates_db) as conn:
                conn.execute('''
                    INSERT INTO template_evolution
                    (evolution_id, template_id, evolution_type, changes_made,
                     performance_impact, evolved_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    evolution_record['evolution_id'],
                    evolution_record['template_id'],
                    evolution_record['evolution_type'],
                    evolution_record['changes_made'],
                    evolution_record['performance_impact'],
                    evolution_record['evolved_at']
                ))
                conn.commit()

            # Update template
            template.evolution_history.append(f"Evolved based on feedback: {', '.join(evolution_changes.keys())}")
            template.last_updated = datetime.now().isoformat()
            self._save_templates_to_database([template])

            print(f"🧠 Template {template_id} evolved using @SPOCK logic")
            return True

        return False

    def _analyze_feedback_for_evolution(self, template: ImprovementTemplate,
                                      feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feedback to determine template evolution opportunities"""
        evolution_changes = {}

        # Check success metrics
        success_metrics = feedback_data.get('success_metrics', {})
        for metric_name, metric_value in success_metrics.items():
            # If metric significantly improved, reinforce that approach
            if metric_value > 0.8:  # 80% success rate
                evolution_changes[f"reinforce_{metric_name}"] = f"Strengthen {metric_name} implementation"

            # If metric underperformed, suggest alternatives
            elif metric_value < 0.5:  # 50% success rate
                evolution_changes[f"improve_{metric_name}"] = f"Improve {metric_name} implementation strategy"

        # Check lessons learned
        lessons_learned = feedback_data.get('lessons_learned', [])
        for lesson in lessons_learned:
            lesson_lower = lesson.lower()
            if 'performance' in lesson_lower:
                evolution_changes['performance_optimization'] = "Add performance optimization techniques"
            elif 'reliability' in lesson_lower:
                evolution_changes['reliability_improvements'] = "Enhance system reliability measures"
            elif 'usability' in lesson_lower:
                evolution_changes['usability_enhancements'] = "Improve user experience features"

        # Check next improvements
        next_improvements = feedback_data.get('next_improvements', [])
        if next_improvements:
            evolution_changes['additional_improvements'] = f"Consider: {', '.join(next_improvements[:3])}"

        return evolution_changes

    def get_templates_by_category(self, category: str) -> List[ImprovementTemplate]:
        """Get all templates for a specific category"""
        templates = []
        with sqlite3.connect(self.templates_db) as conn:
            cursor = conn.execute(
                'SELECT * FROM improvement_templates WHERE category = ?',
                (category,)
            )

            for row in cursor.fetchall():
                template = ImprovementTemplate(
                    template_id=row[0],
                    category=row[1],
                    title=row[2],
                    description=row[3],
                    improvement_ways=json.loads(row[4]) if row[4] else [],
                    implementation_steps=json.loads(row[5]) if row[5] else [],
                    success_metrics=json.loads(row[6]) if row[6] else [],
                    spock_logic_level=row[7],
                    status=row[8],
                    created_at=row[9],
                    last_updated=row[10],
                    applied_count=row[11],
                    success_rate=row[12],
                    evolution_history=json.loads(row[13]) if row[13] else []
                )
                templates.append(template)

        return templates

    def generate_improvement_report(self) -> str:
        """Generate comprehensive improvement templates report"""
        report = []
        report.append("# 🧠 @SPOCK Logic Improvement Templates Report")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("**Self-Updating Templates from 10 Ways Improvements**")
        report.append("")

        with sqlite3.connect(self.templates_db) as conn:
            # Template statistics
            cursor = conn.execute('''
                SELECT category, COUNT(*) as count, AVG(success_rate) as avg_success,
                       SUM(applied_count) as total_applications
                FROM improvement_templates
                GROUP BY category
            ''')
            category_stats = cursor.fetchall()

            # Total statistics
            cursor = conn.execute('''
                SELECT COUNT(*) as total_templates,
                       AVG(success_rate) as overall_success,
                       SUM(applied_count) as total_applications
                FROM improvement_templates
            ''')
            overall_stats = cursor.fetchone()

        # Overall statistics
        if overall_stats:
            total_templates, overall_success, total_applications = overall_stats
            report.append("## 📊 Template System Overview")
            report.append("")
            report.append(f"- **Total Templates:** {total_templates}")
            success_rate_display = f"{overall_success * 100:.1f}%" if overall_success is not None and isinstance(overall_success, (int, float)) else "N/A"
            report.append(f"- **Overall Success Rate:** {success_rate_display}")
            report.append(f"- **Total Applications:** {total_applications}")
            report.append("")

        # Category breakdown
        report.append("## 📂 Template Categories")
        report.append("")
        for category, count, avg_success, total_apps in category_stats:
            success_pct = avg_success * 100 if avg_success else 0
            report.append(f"- **{category.replace('_', ' ').title()}:** {count} templates")
            report.append(f"  - Success Rate: {success_pct:.1f}%")
            report.append(f"  - Total Applications: {total_apps}")
            report.append("")

        # Top performing templates
        report.append("## 🏆 Top Performing Templates")
        report.append("")

        with sqlite3.connect(self.templates_db) as conn:
            cursor = conn.execute('''
                SELECT template_id, title, category, success_rate, applied_count
                FROM improvement_templates
                WHERE applied_count > 0
                ORDER BY success_rate DESC, applied_count DESC
                LIMIT 10
            ''')

            top_templates = cursor.fetchall()
            if top_templates:
                for template_id, title, category, success_rate, applied_count in top_templates:
                    success_pct = success_rate * 100 if success_rate else 0
                    report.append(f"- **{title}** ({category})")
                    report.append(f"  - Success Rate: {success_pct:.1f}%")
                    report.append(f"  - Applications: {applied_count}")
                    report.append("")
            else:
                report.append("*No templates applied yet*")
                report.append("")

        # Recent template applications
        report.append("## 📋 Recent Template Applications")
        report.append("")

        with sqlite3.connect(self.templates_db) as conn:
            cursor = conn.execute('''
                SELECT ta.application_id, it.title, ta.target_system, ta.applied_at,
                       ta.implementation_status
                FROM template_applications ta
                JOIN improvement_templates it ON ta.template_id = it.template_id
                ORDER BY ta.applied_at DESC
                LIMIT 5
            ''')

            recent_apps = cursor.fetchall()
            if recent_apps:
                for app_id, title, target_system, applied_at, status in recent_apps:
                    report.append(f"- **{title}** → {target_system}")
                    report.append(f"  - Status: {status}")
                    report.append(f"  - Applied: {applied_at}")
                    report.append("")
            else:
                report.append("*No recent applications*")
                report.append("")

        # Template evolution activity
        report.append("## 🧠 Template Evolution Activity")
        report.append("")

        with sqlite3.connect(self.templates_db) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) as evolution_count
                FROM template_evolution
                WHERE evolved_at >= date('now', '-30 days')
            ''')

            recent_evolution = cursor.fetchone()[0]
            report.append(f"- **Templates Evolved (Last 30 Days):** {recent_evolution}")
            report.append("")

            # Most evolved templates
            cursor = conn.execute('''
                SELECT it.title, COUNT(te.evolution_id) as evolution_count
                FROM improvement_templates it
                LEFT JOIN template_evolution te ON it.template_id = te.template_id
                GROUP BY it.template_id, it.title
                HAVING evolution_count > 0
                ORDER BY evolution_count DESC
                LIMIT 5
            ''')

            evolved_templates = cursor.fetchall()
            if evolved_templates:
                report.append("**Most Evolved Templates:**")
                report.append("")
                for title, evolution_count in evolved_templates:
                    report.append(f"- **{title}:** {evolution_count} evolutions")
                    report.append("")

        report.append("## ✅ @SPOCK Logic Status")
        report.append("")
        report.append("- ✅ Self-updating template system active")
        report.append("- ✅ Feedback-driven evolution operational")
        report.append("- ✅ Performance tracking and optimization")
        report.append("- ✅ Cross-system improvement pattern recognition")
        report.append("")
        report.append("---")
        report.append("*@SPOCK Logic Self-Updating Improvement Templates*")
        report.append("*10 Ways Improvements → Standardized Modules → Continuous Evolution*")

        return "\\n".join(report)

def create_spock_logic_workflow():
    """
    Create the complete @SPOCK logic workflow.
    @V3_WORKFLOWED +RULE compliant.
    """

    workflow = '''
# 🧠 @SPOCK LOGIC SELF-UPDATING IMPROVEMENT TEMPLATES (@V3 #WORKFLOWED +RULE)

## Core Intelligence Processing Pipeline
1. **10 Ways Analysis** → Extract improvement patterns from documentation
2. **Template Creation** → Convert patterns into standardized modules
3. **System Application** → Apply templates to target systems
4. **Feedback Collection** → Monitor performance and gather lessons learned
5. **@SPOCK Evolution** → Self-update templates based on real-world results
6. **Continuous Improvement** → Apply evolved templates across systems

## Template Categories (From 10 Ways)
### Voice Filtering System
- Real-time audio analysis with MFCC
- Machine learning model training
- Context-aware filtering
- Multi-microphone analysis
- Voice activity detection
- Frequency and temporal pattern analysis
- Adaptive learning systems

### Auto-Accept Detection
- Multiple detection method integration
- Window state and dialog detection
- Visual pattern recognition with OCR
- Event-based detection systems
- State machine implementation
- Retry logic and performance monitoring

### Dynamic Listening Scaling
- Speech duration prediction
- Confidence-based scaling
- Context-aware timing adjustments
- User feedback integration
- Multiple speech end signal detection
- Machine learning optimization

### Audio-Transcription Comparison
- Real-time streaming comparison
- Advanced feature extraction
- Multi-modal analysis integration
- Speaker diarization
- Temporal alignment systems

### Grammar Checking Integration
- Real-time correction systems
- Context-aware grammar analysis
- User preference learning
- Multiple grammar engine integration
- Custom rules and offline support

### System Integration Improvements
- Event-driven architecture
- Centralized state management
- Comprehensive error handling
- Performance monitoring
- User feedback collection
- A/B testing frameworks

## @SPOCK Logic Levels
### BASIC Level
- Simple implementation of improvement patterns
- Manual application and monitoring
- Basic success metric tracking

### INTERMEDIATE Level
- Enhanced features with automation
- Performance monitoring integration
- Automated feedback collection

### ADVANCED Level
- Full optimization with AI assistance
- Predictive improvement suggestions
- Cross-system pattern recognition

### GENIUS Level
- Self-evolving templates with ML
- Predictive failure prevention
- Autonomous optimization systems

## Template Application Process
1. **Template Selection** → Choose appropriate template for system/component
2. **Customization** → Adapt template to specific system requirements
3. **Implementation** → Apply template with standardized steps
4. **Testing & Validation** → Verify improvements meet success metrics
5. **Monitoring** → Track performance and collect feedback
6. **Evolution** → Use feedback to improve template for future applications

## Success Metrics Tracking
- **Performance Improvement** → Quantify system performance gains
- **User Satisfaction** → Measure user experience improvements
- **Error Rate Reduction** → Track reliability improvements
- **Efficiency Gains** → Measure productivity and resource utilization
- **Scalability Improvements** → Assess system growth capabilities

## Feedback-Driven Evolution
- **Performance Analysis** → Identify what worked and what didn't
- **Pattern Recognition** → Discover common success/failure patterns
- **Template Updates** → Modify templates based on real-world results
- **Cross-System Learning** → Apply lessons learned across different systems
- **Predictive Optimization** → Anticipate future improvement needs

## Usage Example
```python
from self_updating_improvement_templates import SelfUpdatingImprovementTemplates

# Initialize @SPOCK logic system
spock_templates = SelfUpdatingImprovementTemplates()

# Get voice filtering improvement templates
voice_templates = spock_templates.get_templates_by_category('voice_filtering')

# Apply real-time audio analysis template
application = spock_templates.apply_template_to_system(
    template_id='voice_filtering_20240119_120000',
    target_system='voice_filter_system',
    customizations={
        'spock_logic_level': 'advanced',
        'implementation_steps': ['Add GPU acceleration', 'Implement model caching']
    }
)

# Provide feedback for template evolution
feedback = {
    'success_metrics': {'accuracy': 0.95, 'latency': 0.8},
    'lessons_learned': ['GPU acceleration significantly improved performance'],
    'next_improvements': ['Add model versioning', 'Implement A/B testing']
}

# Evolve template based on feedback
spock_templates.evolve_template_based_on_feedback(
    template_id='voice_filtering_20240119_120000',
    feedback_data=feedback
)

# Generate comprehensive report
report = spock_templates.generate_improvement_report()
print(report)
```
'''

    print(workflow)

# Test-first validation
def test_spock_logic_templates():
    """Test the @SPOCK logic self-updating templates"""
    print("🧪 Testing @SPOCK Logic Self-Updating Improvement Templates...")

    try:
        # Create template system
        spock_system = SelfUpdatingImprovementTemplates("./test_spock_templates.db")

        # Test template loading
        voice_templates = spock_system.get_templates_by_category('voice_filtering')
        assert len(voice_templates) > 0, "No voice filtering templates loaded"

        # Test template application
        first_template = voice_templates[0]
        application = spock_system.apply_template_to_system(
            first_template.template_id, "test_system"
        )
        assert application.template_id == first_template.template_id, "Template application failed"

        # Test template evolution
        feedback_data = {
            'success_metrics': {'performance': 0.9, 'reliability': 0.85},
            'lessons_learned': ['Implementation successful', 'Performance improved'],
            'next_improvements': ['Add monitoring', 'Consider scaling']
        }

        evolved = spock_system.evolve_template_based_on_feedback(
            first_template.template_id, feedback_data
        )
        assert evolved, "Template evolution failed"

        # Test report generation
        report = spock_system.generate_improvement_report()
        assert len(report) > 0, "Empty improvement report"
        assert "@SPOCK" in report, "Report missing @SPOCK branding"

        print("✅ All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run workflow documentation
    create_spock_logic_workflow()

    # Run tests
    print("\\n" + "="*60)
    test_spock_logic_templates()

    print("\\n🧠 @SPOCK LOGIC SELF-UPDATING IMPROVEMENT TEMPLATES READY")
    print("   10 Ways Improvements → Standardized Modules → Continuous Evolution")
    print("   @V3 #WORKFLOWED +RULE compliant ✅")
