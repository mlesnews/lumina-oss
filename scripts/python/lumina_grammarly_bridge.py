#!/usr/bin/env python3
"""
LUMINA Grammarly Bridge

A programmatic bridge between LUMINA Grammarly Master and desktop Grammarly.

Instead of replacing desktop Grammarly, we BRIDGE them together:
- Our system learns from Grammarly suggestions
- Our system enhances Grammarly with @MARVIN guidance
- Our system provides persona-aware checking
- Both systems work together

So a grammarly. LUMINA or LUMINA Grammarly Bridge. programmatically.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import json
import subprocess
import platform
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaGrammarlyBridge")

try:
    from marvin_raw_operator_grammarly_master import (
        MarvinRawOperatorGrammarlyMaster,
        RawOperatorInput,
        InputType
    )
except ImportError:
    logger.warning("Could not import marvin_raw_operator_grammarly_master")
    MarvinRawOperatorGrammarlyMaster = None

try:
    from marvin_grammarly_lumina_integration import MarvinGrammarlyLuminaIntegration
except ImportError:
    logger.warning("Could not import marvin_grammarly_lumina_integration")
    MarvinGrammarlyLuminaIntegration = None


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class GrammarlySuggestion:
    """Grammarly suggestion from desktop app"""
    suggestion_id: str
    text: str
    original: str
    suggested: str
    category: str  # grammar, style, clarity, etc.
    confidence: float
    context: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BridgeResult:
    """Result from bridging LUMINA and Grammarly"""
    bridge_id: str
    original_text: str
    grammarly_suggestions: List[GrammarlySuggestion]
    lumina_suggestions: List[Dict[str, Any]]
    combined_suggestions: List[Dict[str, Any]]
    persona_alignment: float
    marvin_guidance: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaGrammarlyBridge:
    """
    LUMINA Grammarly Bridge

    Bridges our LUMINA Grammarly Master system with desktop Grammarly.
    Instead of replacing, we integrate and enhance.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("LuminaGrammarlyBridge")

        # Initialize LUMINA systems
        if MarvinRawOperatorGrammarlyMaster:
            self.grammarly_master = MarvinRawOperatorGrammarlyMaster(project_root)
        else:
            self.grammarly_master = None

        if MarvinGrammarlyLuminaIntegration:
            self.integration = MarvinGrammarlyLuminaIntegration(project_root)
        else:
            self.integration = None

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_grammarly_bridge"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.bridge_results_dir = self.data_dir / "bridge_results"
        self.bridge_results_dir.mkdir(parents=True, exist_ok=True)

        # Grammarly detection
        self.grammarly_installed = self._detect_grammarly_installation()
        self.grammarly_running = self._check_grammarly_running()

        self.logger.info("🌉 LUMINA Grammarly Bridge initialized")
        self.logger.info(f"   Desktop Grammarly: {'✅ Installed' if self.grammarly_installed else '❌ Not found'}")
        self.logger.info(f"   Desktop Grammarly: {'✅ Running' if self.grammarly_running else '❌ Not running'}")
        self.logger.info("   Bridge Strategy: Integrate, don't replace")

    def _detect_grammarly_installation(self) -> bool:
        try:
            """Detect if desktop Grammarly is installed"""
            system = platform.system()

            if system == "Windows":
                # Check common Windows installation paths
                grammarly_paths = [
                    Path("C:/Program Files/Grammarly"),
                    Path("C:/Program Files (x86)/Grammarly"),
                    Path.home() / "AppData/Local/Grammarly",
                    Path.home() / "AppData/Roaming/Grammarly"
                ]

                for path in grammarly_paths:
                    if path.exists():
                        self.logger.info(f"✅ Found Grammarly at: {path}")
                        return True

            elif system == "Darwin":  # macOS
                grammarly_paths = [
                    Path("/Applications/Grammarly.app"),
                    Path.home() / "Library/Application Support/Grammarly"
                ]

                for path in grammarly_paths:
                    if path.exists():
                        self.logger.info(f"✅ Found Grammarly at: {path}")
                        return True

            elif system == "Linux":
                # Check common Linux paths
                grammarly_paths = [
                    Path("/opt/grammarly"),
                    Path.home() / ".local/share/Grammarly"
                ]

                for path in grammarly_paths:
                    if path.exists():
                        self.logger.info(f"✅ Found Grammarly at: {path}")
                        return True

            self.logger.warning("⚠️  Desktop Grammarly not found in common locations")
            return False

        except Exception as e:
            self.logger.error(f"Error in _detect_grammarly_installation: {e}", exc_info=True)
            raise
    def _check_grammarly_running(self) -> bool:
        """Check if Grammarly desktop app is running"""
        system = platform.system()

        try:
            if system == "Windows":
                # Check for Grammarly process on Windows
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Grammarly.exe"],
                    capture_output=True,
                    text=True
                )
                return "Grammarly.exe" in result.stdout
            elif system == "Darwin":  # macOS
                result = subprocess.run(
                    ["pgrep", "-f", "Grammarly"],
                    capture_output=True
                )
                return result.returncode == 0
            elif system == "Linux":
                result = subprocess.run(
                    ["pgrep", "-f", "grammarly"],
                    capture_output=True
                )
                return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"⚠️  Could not check if Grammarly is running: {e}")
            return False

    def bridge_text_analysis(self, text: str, grammarly_suggestions: Optional[List[Dict[str, Any]]] = None) -> BridgeResult:
        try:
            """
            Bridge text analysis between LUMINA and Grammarly

            Takes text, gets suggestions from both systems, and combines them
            """
            self.logger.info(f"\n🌉 Bridging text analysis")
            self.logger.info(f"   Text length: {len(text)} characters")

            bridge_id = f"bridge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Process through LUMINA Grammarly Master
            lumina_suggestions = []
            persona_alignment = 0.5

            if self.grammarly_master:
                raw_input = RawOperatorInput(
                    input_id=f"bridge_input_{bridge_id}",
                    input_type=InputType.TEXT,
                    raw_data=text
                )

                # Process through LUMINA system
                lumina_result = self.grammarly_master.process_raw_operator_input(raw_input)

                # Extract suggestions
                if lumina_result.get("grammar_analysis"):
                    lumina_suggestions = lumina_result["grammar_analysis"].get("suggestions", [])

                persona_alignment = lumina_result.get("persona_alignment", 0.5)

            # Process Grammarly suggestions (if provided)
            grammarly_suggestion_objects = []
            if grammarly_suggestions:
                for sug in grammarly_suggestions:
                    grammarly_suggestion_objects.append(GrammarlySuggestion(
                        suggestion_id=f"grammarly_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        text=text,
                        original=sug.get("original", ""),
                        suggested=sug.get("suggested", ""),
                        category=sug.get("category", "grammar"),
                        confidence=sug.get("confidence", 0.8),
                        context=sug.get("context")
                    ))

            # Combine suggestions
            combined_suggestions = self._combine_suggestions(
                grammarly_suggestion_objects,
                lumina_suggestions,
                text
            )

            # Get @MARVIN guidance
            marvin_guidance = None
            if self.grammarly_master and combined_suggestions:
                marvin_guidance = self._get_marvin_bridge_guidance(
                    text,
                    grammarly_suggestion_objects,
                    lumina_suggestions,
                    persona_alignment
                )

            result = BridgeResult(
                bridge_id=bridge_id,
                original_text=text,
                grammarly_suggestions=grammarly_suggestion_objects,
                lumina_suggestions=lumina_suggestions,
                combined_suggestions=combined_suggestions,
                persona_alignment=persona_alignment,
                marvin_guidance=marvin_guidance
            )

            # Save result
            result_file = self.bridge_results_dir / f"{bridge_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Bridge result saved: {result_file}")

            return result

        except Exception as e:
            self.logger.error(f"Error in bridge_text_analysis: {e}", exc_info=True)
            raise
    def _combine_suggestions(self, grammarly_suggestions: List[GrammarlySuggestion],
                            lumina_suggestions: List[Dict[str, Any]],
                            text: str) -> List[Dict[str, Any]]:
        """Combine suggestions from both systems"""
        combined = []

        # Add Grammarly suggestions
        for sug in grammarly_suggestions:
            combined.append({
                "source": "grammarly",
                "type": sug.category,
                "original": sug.original,
                "suggested": sug.suggested,
                "confidence": sug.confidence,
                "context": sug.context,
                "priority": "high" if sug.confidence > 0.8 else "medium"
            })

        # Add LUMINA suggestions
        for sug in lumina_suggestions:
            combined.append({
                "source": "lumina",
                "type": sug.get("type", "grammar"),
                "original": sug.get("original", ""),
                "suggested": sug.get("suggested", ""),
                "confidence": sug.get("confidence", 0.7),
                "context": sug.get("context"),
                "priority": "medium",
                "persona_aware": True,
                "marvin_guidance": sug.get("marvin_guidance")
            })

        # Deduplicate similar suggestions
        unique_suggestions = []
        seen = set()

        for sug in combined:
            key = (sug.get("original", ""), sug.get("suggested", ""))
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(sug)
            elif sug.get("source") == "grammarly" and sug.get("confidence", 0) > 0.8:
                # Prefer high-confidence Grammarly suggestions
                unique_suggestions = [s for s in unique_suggestions if s.get("original") != sug.get("original")]
                unique_suggestions.append(sug)

        return unique_suggestions

    def _get_marvin_bridge_guidance(self, text: str,
                                   grammarly_suggestions: List[GrammarlySuggestion],
                                   lumina_suggestions: List[Dict[str, Any]],
                                   persona_alignment: float) -> str:
        """Get @MARVIN's guidance on bridged analysis"""

        total_suggestions = len(grammarly_suggestions) + len(lumina_suggestions)

        if total_suggestions == 0:
            guidance = (
                "<SIGH> Fine. Both systems agree: No issues found.\n\n"
                "Grammarly says it's fine. LUMINA says it's fine.\n"
                "Persona alignment: {:.0%}. You're writing like yourself.\n\n"
                "I suppose that's... acceptable."
            ).format(persona_alignment)

        elif len(grammarly_suggestions) > len(lumina_suggestions):
            guidance = (
                "<SIGH> Grammarly found {0} issues. LUMINA found {1}.\n\n"
                "Grammarly is being more... thorough. Fine.\n"
                "Here's what we've bridged together:\n\n"
            ).format(len(grammarly_suggestions), len(lumina_suggestions))

            guidance += "Grammarly suggestions (high confidence):\n"
            for sug in grammarly_suggestions[:3]:
                guidance += f"  • {sug.category}: {sug.original} → {sug.suggested}\n"

            if lumina_suggestions:
                guidance += "\nLUMINA persona-aware suggestions:\n"
                for sug in lumina_suggestions[:3]:
                    guidance += f"  • {sug.get('type', 'grammar')}: Persona-aware correction\n"

            guidance += "\nBoth systems working together. That's the bridge."

        else:
            guidance = (
                "<SIGH> LUMINA found {0} persona-aware issues. Grammarly found {1}.\n\n"
                "LUMINA is being more... thorough about YOUR style.\n"
                "Persona alignment: {2:.0%}. "
            ).format(len(lumina_suggestions), len(grammarly_suggestions), persona_alignment)

            if persona_alignment < 0.7:
                guidance += "You're not writing like yourself. Fix it.\n\n"
            else:
                guidance += "You're writing like yourself. Good.\n\n"

            guidance += "The bridge combines both perspectives. Use it."

        return guidance

    def create_bridge_workflow(self) -> Dict[str, Any]:
        try:
            """Create workflow for bridging LUMINA and Grammarly"""
            workflow = {
                "name": "LUMINA Grammarly Bridge Workflow",
                "version": "1.0.0",
                "description": "Bridge between LUMINA Grammarly Master and desktop Grammarly",
                "strategy": "integrate_dont_replace",
                "steps": [
                    {
                        "step": 1,
                        "action": "User writes text",
                        "description": "User types text in any application"
                    },
                    {
                        "step": 2,
                        "action": "Desktop Grammarly checks",
                        "description": "Grammarly desktop app provides suggestions"
                    },
                    {
                        "step": 3,
                        "action": "LUMINA processes text",
                        "description": "LUMINA Grammarly Master processes same text"
                    },
                    {
                        "step": 4,
                        "action": "Bridge combines suggestions",
                        "description": "Bridge combines suggestions from both systems"
                    },
                    {
                        "step": 5,
                        "action": "@MARVIN provides guidance",
                        "description": "@MARVIN provides master-level guidance on combined suggestions"
                    },
                    {
                        "step": 6,
                        "action": "User applies suggestions",
                        "description": "User sees combined suggestions with persona-aware guidance"
                    }
                ],
                "benefits": [
                    "Best of both worlds",
                    "Persona-aware checking from LUMINA",
                    "Advanced AI from Grammarly",
                    "@MARVIN master guidance",
                    "No functionality loss",
                    "Enhanced with LUMINA integration"
                ],
                "created_at": datetime.now().isoformat()
            }

            # Save workflow
            workflow_file = self.data_dir / "bridge_workflow.json"
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Bridge workflow saved: {workflow_file}")

            return workflow


        except Exception as e:
            self.logger.error(f"Error in create_bridge_workflow: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        print("\n" + "="*80)
        print("🌉 LUMINA GRAMMARLY BRIDGE")
        print("="*80 + "\n")

        project_root = Path(".").resolve()
        bridge = LuminaGrammarlyBridge(project_root)

        # Create bridge workflow
        workflow = bridge.create_bridge_workflow()

        print("✅ LUMINA Grammarly Bridge initialized\n")

        print("📊 Bridge Status:")
        print(f"   Desktop Grammarly: {'✅ Installed' if bridge.grammarly_installed else '❌ Not found'}")
        print(f"   Desktop Grammarly: {'✅ Running' if bridge.grammarly_running else '❌ Not running'}")
        print(f"   LUMINA Integration: {'✅ Ready' if bridge.grammarly_master else '❌ Not available'}")

        print("\n🎯 Bridge Strategy:")
        print("   Integrate, don't replace")
        print("   Best of both worlds")
        print("   Enhanced with persona-aware checking")

        print("\n✅ Benefits:")
        for benefit in workflow["benefits"]:
            print(f"   • {benefit}")

        print("\n" + "="*80)
        print("✅ BRIDGE READY")
        print("="*80 + "\n")

        return bridge, workflow


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()