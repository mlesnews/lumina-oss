#!/usr/bin/env python3
"""
Measure JARVIS Mode & @FOCUS Effectiveness

"What good is it unless we measure?"

Measures:
- @FOCUS level (concentration, clarity, precision)
- JARVIS mode effectiveness
- Frequency alignment
- Vibecoding quality
- Knowledge accumulation

Tags: #MEASUREMENT #JARVIS-MODE #FOCUS #KNOWLEDGE #POWER
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger(__name__)


class JARVISModeFocusMeasurement:
    """Measure JARVIS Mode & @FOCUS Effectiveness"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.measurements_dir = self.project_root / "data" / "measurements" / "jarvis_mode_focus"
        self.measurements_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("📊 JARVIS MODE & @FOCUS MEASUREMENT SYSTEM")
        logger.info("=" * 80)
        logger.info("  'What good is it unless we measure?'")
        logger.info("=" * 80)

    def measure_focus(self) -> Dict[str, Any]:
        """Measure @FOCUS level"""
        focus_metrics = {
            "concentration": {
                "level": 0.0,  # 0.0 to 1.0
                "indicators": ["attention_span", "distraction_level", "task_engagement"],
                "measurement": "Subjective + objective indicators"
            },
            "clarity": {
                "level": 0.0,  # 0.0 to 1.0
                "indicators": ["understanding", "vision_clarity", "decision_clarity"],
                "measurement": "Subjective + objective indicators"
            },
            "precision": {
                "level": 0.0,  # 0.0 to 1.0
                "indicators": ["execution_accuracy", "error_rate", "quality_score"],
                "measurement": "Objective metrics"
            },
            "overall_focus": {
                "level": 0.0,  # Average of concentration, clarity, precision
                "timestamp": datetime.now().isoformat()
            }
        }

        return focus_metrics

    def measure_jarvis_mode(self) -> Dict[str, Any]:
        """Measure JARVIS mode effectiveness"""
        jarvis_metrics = {
            "vibecoding_quality": {
                "level": 0.0,  # 0.0 to 1.0
                "indicators": ["vibe_alignment", "flow_state", "satisfaction"],
                "measurement": "Subjective + objective indicators"
            },
            "frequency_alignment": {
                "level": 0.0,  # 0.0 to 1.0
                "indicators": ["reality_match", "channel_alignment", "signal_clarity"],
                "measurement": "Frequency analysis"
            },
            "microverse_adjustments": {
                "count": 0,
                "effectiveness": 0.0,  # 0.0 to 1.0
                "measurement": "Count and effectiveness of @MICRO adjustments"
            },
            "simulator_usage": {
                "wopr_usage": 0,
                "matrix_usage": 0,
                "animatrix_usage": 0,
                "effectiveness": 0.0,  # 0.0 to 1.0
                "measurement": "Usage count and effectiveness"
            },
            "overall_jarvis_mode": {
                "level": 0.0,  # Composite score
                "timestamp": datetime.now().isoformat()
            }
        }

        return jarvis_metrics

    def measure_knowledge(self) -> Dict[str, Any]:
        try:
            """Measure knowledge accumulation"""
            knowledge_metrics = {
                "knowledge_accumulation": {
                    "holocron_entries": 0,
                    "captains_log_entries": 0,
                    "documentation_files": 0,
                    "discussions_saved": 0,
                    "measurement": "Count of knowledge artifacts"
                },
                "knowledge_accessibility": {
                    "searchability": 0.0,  # 0.0 to 1.0
                    "organization": 0.0,  # 0.0 to 1.0
                    "completeness": 0.0,  # 0.0 to 1.0
                    "measurement": "Accessibility metrics"
                },
                "knowledge_power": {
                    "power_level": 0.0,  # 0.0 to 1.0
                    "formula": "Knowledge accumulation × Accessibility = Power",
                    "measurement": "Knowledge power calculation"
                },
                "timestamp": datetime.now().isoformat()
            }

            # Count actual knowledge artifacts
            holocron_dir = self.project_root / "data" / "holocrons"
            captains_log_dir = self.project_root / "data" / "captains_log"
            docs_dir = self.project_root / "docs"

            if holocron_dir.exists():
                knowledge_metrics["knowledge_accumulation"]["holocron_entries"] = len(list(holocron_dir.glob("*.json")))

            if captains_log_dir.exists():
                knowledge_metrics["knowledge_accumulation"]["captains_log_entries"] = len(list(captains_log_dir.glob("*.json")))

            if docs_dir.exists():
                knowledge_metrics["knowledge_accumulation"]["documentation_files"] = len(list(docs_dir.rglob("*.md")))

            return knowledge_metrics

        except Exception as e:
            self.logger.error(f"Error in measure_knowledge: {e}", exc_info=True)
            raise
    def measure_all(self) -> Dict[str, Any]:
        """Measure everything"""
        measurements = {
            "timestamp": datetime.now().isoformat(),
            "measurement_principle": "What good is it unless we measure?",
            "knowledge_power": "#KNOWLEDGE IS INDEED @POWER",
            "focus": self.measure_focus(),
            "jarvis_mode": self.measure_jarvis_mode(),
            "knowledge": self.measure_knowledge(),
            "overall_score": {
                "focus_score": 0.0,
                "jarvis_mode_score": 0.0,
                "knowledge_power_score": 0.0,
                "composite_score": 0.0
            }
        }

        # Calculate composite scores (placeholder - would need actual data)
        measurements["overall_score"]["focus_score"] = 0.0  # Would calculate from focus metrics
        measurements["overall_score"]["jarvis_mode_score"] = 0.0  # Would calculate from jarvis metrics
        measurements["overall_score"]["knowledge_power_score"] = 0.0  # Would calculate from knowledge metrics
        measurements["overall_score"]["composite_score"] = 0.0  # Average of all scores

        return measurements

    def save_measurements(self, measurements: Dict[str, Any]) -> Path:
        try:
            """Save measurements - preserve perfect history"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.measurements_dir / f"measurement_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(measurements, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Measurements saved: {output_file.name}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in save_measurements: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point - @DOIT"""
        project_root = Path(__file__).parent.parent.parent
        measurement = JARVISModeFocusMeasurement(project_root)

        measurements = measurement.measure_all()
        output_file = measurement.save_measurements(measurements)

        print("=" * 80)
        print("📊 JARVIS MODE & @FOCUS MEASUREMENTS")
        print("=" * 80)
        print()
        print("  Principle: 'What good is it unless we measure?'")
        print("  Knowledge: '#KNOWLEDGE IS INDEED @POWER'")
        print()
        print("  @FOCUS Metrics:")
        print(f"    Concentration: {measurements['focus']['overall_focus']['level']:.2f}")
        print(f"    Clarity: {measurements['focus']['overall_focus']['level']:.2f}")
        print(f"    Precision: {measurements['focus']['overall_focus']['level']:.2f}")
        print()
        print("  JARVIS Mode Metrics:")
        print(f"    Vibecoding Quality: {measurements['jarvis_mode']['overall_jarvis_mode']['level']:.2f}")
        print(f"    Frequency Alignment: {measurements['jarvis_mode']['frequency_alignment']['level']:.2f}")
        print()
        print("  Knowledge Metrics:")
        print(f"    Holocron Entries: {measurements['knowledge']['knowledge_accumulation']['holocron_entries']}")
        print(f"    Captain's Log Entries: {measurements['knowledge']['knowledge_accumulation']['captains_log_entries']}")
        print(f"    Documentation Files: {measurements['knowledge']['knowledge_accumulation']['documentation_files']}")
        print()
        print(f"  Measurements saved: {output_file.name}")
        print("=" * 80)

        return measurements


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()