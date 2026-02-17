#!/usr/bin/env python3
"""
LUMINA JARVIS Hybrid Integration

Integrates LUMINA JARVIS Hybrid Voice System with @DOIT, @BAU, @TRIAGE.
Automatic updates on the fly.

Tags: #LUMINA #JARVIS #HYBRID #VOICE #DIGITAL_CLONE #AVATAR #DOIT #BAU #TRIAGE @JARVIS @LUMINA @DIGITAL @CLONE @AVATAR
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from lumina_jarvis_hybrid_voice_system import LUMINAJARVISHybridVoice
    from doit_enhanced import DOITEnhanced
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINAJARVISHybridIntegration")


class LUMINAJARVISHybridIntegration:
    """
    LUMINA JARVIS Hybrid Integration

    Integrates hybrid voice system with @DOIT, @BAU, @TRIAGE.
    Automatic updates on the fly.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize systems
        self.hybrid_voice = LUMINAJARVISHybridVoice(project_root)
        self.doit = DOITEnhanced(project_root)

        logger.info("✅ LUMINA JARVIS Hybrid Integration initialized")
        logger.info("   🎭 Hybrid Voice System: ACTIVE")
        logger.info("   🚀 @DOIT Enhanced: ACTIVE")
        logger.info("   📋 @BAU: AUTO-INFERRED")
        logger.info("   🎯 @TRIAGE: AUTO-INFERRED")

    def process_with_doit(self, va_name: str, task: str, 
                         audio_file: Optional[str] = None,
                         text: Optional[str] = None) -> Dict[str, Any]:
        """
        Process voice input with @DOIT, @BAU, @TRIAGE integration

        Automatically:
        - Infers @BAU if routine operation
        - Infers @TRIAGE priority
        - Updates on the fly
        - Executes via @DOIT
        """
        logger.info("=" * 80)
        logger.info("🎭 LUMINA JARVIS HYBRID - @DOIT @BAU @TRIAGE")
        logger.info("=" * 80)
        logger.info("")

        # Process voice through hybrid system
        voice_result = self.hybrid_voice.process_voice_for_va(
            va_name=va_name,
            audio_file=audio_file,
            text=text
        )

        # Extract task from voice result
        if text:
            extracted_task = text
        elif voice_result.get("pipeline_steps"):
            # Extract from AI processing step
            ai_step = next(
                (s for s in voice_result["pipeline_steps"] if s.get("service") == "ai_companion"),
                None
            )
            if ai_step:
                extracted_task = ai_step.get("input", task)
            else:
                extracted_task = task
        else:
            extracted_task = task

        # Execute via @DOIT with @BAU and @TRIAGE
        doit_result = self.doit.doit(
            task_description=extracted_task,
            context={
                "va_name": va_name,
                "clone_id": voice_result.get("clone_id"),
                "voice_result": voice_result
            },
            auto_5w1h=True,
            auto_root_cause=True,
            execute=True
        )

        # Combine results
        combined_result = {
            "voice_processing": voice_result,
            "doit_execution": doit_result,
            "va_name": va_name,
            "priority": doit_result.get("priority", "medium"),
            "is_bau": doit_result.get("is_bau", False),
            "triage_assessment": doit_result.get("triage_assessment"),
            "bau_routine": doit_result.get("bau_routine")
        }

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ HYBRID INTEGRATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   VA: {va_name}")
        logger.info(f"   Priority: {combined_result['priority'].upper()}")
        logger.info(f"   @BAU: {combined_result['is_bau']}")
        logger.info("")

        return combined_result


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA JARVIS Hybrid Integration")
        parser.add_argument("--va", type=str, required=True, help="VA name (JARVIS, IMVA, ACVA)")
        parser.add_argument("--task", type=str, required=True, help="Task to execute")
        parser.add_argument("--voice", type=str, help="Voice input (audio file)")
        parser.add_argument("--text", type=str, help="Text input")

        args = parser.parse_args()

        integration = LUMINAJARVISHybridIntegration()
        result = integration.process_with_doit(
            va_name=args.va,
            task=args.task,
            audio_file=args.voice,
            text=args.text
        )

        import json
        print(json.dumps(result, indent=2, default=str))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())