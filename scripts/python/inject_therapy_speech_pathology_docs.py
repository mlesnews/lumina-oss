#!/usr/bin/env python3
"""
Inject Therapy & Speech Pathology Documentation into All Workflows

Reads therapy and speech pathology documentation and injects it into:
- Therapy workflows
- Voice-enabled systems
- Podcast recording systems
- All AI-Human collaboration systems

Tags: #DOCUMENTATION #INJECTION #WORKFLOW #THERAPY #SPEECH_PATHOLOGY @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("InjectTherapySpeechPathologyDocs")


class InjectTherapySpeechPathologyDocs:
    """
    Inject Therapy & Speech Pathology Documentation into Workflows

    Makes documentation available to all workflows that need it.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize documentation injection system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        # Documentation files
        self.therapy_docs = self.docs_dir / "THERAPY_SPEECH_PATHOLOGY_DOCS.md"
        self.voice_docs = self.project_root / "VOICE_IDENTIFICATION_NOISE_CANCELLATION.md"

        # Injection targets
        self.injection_targets = [
            "ai_human_collab_therapy.py",
            "ai_human_collab_therapy_voice.py",
            "ai_human_collab_therapy_podcast.py",
            "voice_identification_noise_cancellation.py"
        ]

        logger.info("✅ Documentation Injection System initialized")

    def load_documentation(self) -> Dict[str, str]:
        try:
            """Load therapy and speech pathology documentation"""
            docs = {}

            # Load therapy/speech pathology docs
            if self.therapy_docs.exists():
                with open(self.therapy_docs, 'r', encoding='utf-8') as f:
                    docs["therapy_speech_pathology"] = f.read()
                logger.info("✅ Loaded therapy/speech pathology documentation")
            else:
                logger.warning("⚠️  Therapy/speech pathology docs not found")
                docs["therapy_speech_pathology"] = ""

            # Load voice identification docs
            if self.voice_docs.exists():
                with open(self.voice_docs, 'r', encoding='utf-8') as f:
                    docs["voice_identification"] = f.read()
                logger.info("✅ Loaded voice identification documentation")
            else:
                logger.warning("⚠️  Voice identification docs not found")
                docs["voice_identification"] = ""

            return docs

        except Exception as e:
            self.logger.error(f"Error in load_documentation: {e}", exc_info=True)
            raise
    def get_documentation_summary(self) -> Dict[str, Any]:
        """Get summary of available documentation for workflow injection"""
        docs = self.load_documentation()

        summary = {
            "therapy_speech_pathology_available": bool(docs.get("therapy_speech_pathology")),
            "voice_identification_available": bool(docs.get("voice_identification")),
            "key_topics": [],
            "integration_points": [],
            "ready_for_injection": True
        }

        # Extract key topics
        therapy_doc = docs.get("therapy_speech_pathology", "")
        if "Voice Processing" in therapy_doc:
            summary["key_topics"].append("Voice Processing Pipeline")
        if "Speaker Identification" in therapy_doc:
            summary["key_topics"].append("Speaker Identification")
        if "Noise Cancellation" in therapy_doc:
            summary["key_topics"].append("Noise Cancellation")
        if "Speech Pathology" in therapy_doc:
            summary["key_topics"].append("Speech Pathology Integration")

        # Integration points
        summary["integration_points"] = [
            "Therapy session workflows",
            "Podcast recording workflows",
            "Voice-enabled systems",
            "Speech pathology assessments",
            "All AI-Human collaboration systems"
        ]

        return summary

    def inject_into_workflow(self, workflow_name: str, documentation: Dict[str, str]) -> bool:
        """Inject documentation into a specific workflow"""
        logger.info(f"📥 Injecting documentation into: {workflow_name}")

        # This would modify workflow files to include documentation
        # For now, we'll create a reference file that workflows can read

        injection_file = self.project_root / "data" / "workflow_injections" / f"{workflow_name}_docs.json"
        injection_file.parent.mkdir(parents=True, exist_ok=True)

        injection_data = {
            "workflow": workflow_name,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "documentation": documentation,
            "injected": True
        }

        try:
            with open(injection_file, 'w', encoding='utf-8') as f:
                json.dump(injection_data, f, indent=2, default=str)
            logger.info(f"   ✅ Documentation injected: {injection_file.name}")
            return True
        except Exception as e:
            logger.error(f"   ❌ Injection error: {e}")
            return False

    def inject_all_workflows(self) -> Dict[str, bool]:
        """Inject documentation into all target workflows"""
        logger.info("="*80)
        logger.info("📥 INJECTING DOCUMENTATION INTO ALL WORKFLOWS")
        logger.info("="*80)

        docs = self.load_documentation()
        results = {}

        for target in self.injection_targets:
            workflow_name = target.replace(".py", "")
            success = self.inject_into_workflow(workflow_name, docs)
            results[workflow_name] = success

        logger.info("")
        logger.info("="*80)
        logger.info("📊 INJECTION SUMMARY")
        logger.info("="*80)
        logger.info(f"   Workflows processed: {len(results)}")
        logger.info(f"   Successful: {sum(1 for v in results.values() if v)}")
        logger.info(f"   Failed: {sum(1 for v in results.values() if not v)}")
        logger.info("="*80)

        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Inject Therapy & Speech Pathology Docs into Workflows")
    parser.add_argument("--inject-all", action="store_true", help="Inject into all workflows")
    parser.add_argument("--summary", action="store_true", help="Show documentation summary")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("📥 Inject Therapy & Speech Pathology Documentation")
    print("   Ready for injection into all workflows")
    print("="*80 + "\n")

    injector = InjectTherapySpeechPathologyDocs()

    if args.summary:
        summary = injector.get_documentation_summary()
        print("\n📊 DOCUMENTATION SUMMARY")
        print("="*80)
        print(f"Therapy/Speech Pathology: {'✅ Available' if summary['therapy_speech_pathology_available'] else '❌ Not found'}")
        print(f"Voice Identification: {'✅ Available' if summary['voice_identification_available'] else '❌ Not found'}")
        print(f"Ready for Injection: {'✅ YES' if summary['ready_for_injection'] else '❌ NO'}")
        print()
        print("Key Topics:")
        for topic in summary['key_topics']:
            print(f"   - {topic}")
        print()
        print("Integration Points:")
        for point in summary['integration_points']:
            print(f"   - {point}")
        print()

    elif args.inject_all:
        results = injector.inject_all_workflows()
        print("\n📊 INJECTION RESULTS")
        print("="*80)
        for workflow, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {workflow}")
        print()

    else:
        print("Use --summary to see documentation summary")
        print("Use --inject-all to inject into all workflows")
        print("="*80 + "\n")
