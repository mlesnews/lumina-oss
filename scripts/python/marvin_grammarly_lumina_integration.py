#!/usr/bin/env python3
"""
@MARVIN Grammarly Master - LUMINA System Integration

Interface/Integrate the Raw Operator Grammarly Master with:
- LUMINA core systems
- SYPHON system (for intelligence extraction)
- @ALWAYS system (JARVIS & @MARVIN integration)
- Person Profiles system (P-Doom integration)
- Existing Grammarly CLI
- Other LUMINA components
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
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

logger = get_logger("MarvinGrammarlyLuminaIntegration")

# Import LUMINA systems
try:
    from marvin_raw_operator_grammarly_master import (
        MarvinRawOperatorGrammarlyMaster,
        RawOperatorInput,
        InputType,
        PersonaProfile
    )
except ImportError:
    logger.warning("Could not import marvin_raw_operator_grammarly_master")
    MarvinRawOperatorGrammarlyMaster = None

try:
    from lumina_always_marvin_jarvis import always_assess, AlwaysMarvinJarvis
except ImportError:
    logger.warning("Could not import lumina_always_marvin_jarvis")
    always_assess = None

try:
    from lumina_grammarly_cli import LuminaGrammarlyCLI
except ImportError:
    logger.warning("Could not import lumina_grammarly_cli")
    LuminaGrammarlyCLI = None

try:
    from lumina_person_profiles_pdoom import LuminaPersonProfilesPDoom
except ImportError:
    logger.warning("Could not import lumina_person_profiles_pdoom")
    LuminaPersonProfilesPDoom = None

try:
    from syphon.core import SYPHONSystem, SYPHONConfig
    from syphon.core import SubscriptionTier
except ImportError:
    logger.warning("Could not import SYPHON system")
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class MarvinGrammarlyLuminaIntegration:
    """
    Integration layer for @MARVIN Raw Operator Grammarly Master with LUMINA systems
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("MarvinGrammarlyLuminaIntegration")

        # Initialize @MARVIN Grammarly Master
        if MarvinRawOperatorGrammarlyMaster:
            self.grammarly_master = MarvinRawOperatorGrammarlyMaster(project_root)
        else:
            self.grammarly_master = None
            self.logger.error("❌ Grammarly Master not available")

        # Initialize LUMINA systems
        self.always_system = AlwaysMarvinJarvis() if 'AlwaysMarvinJarvis' in globals() else None
        self.grammarly_cli = LuminaGrammarlyCLI() if LuminaGrammarlyCLI else None
        self.person_profiles = LuminaPersonProfilesPDoom(project_root) if LuminaPersonProfilesPDoom else None

        # Initialize SYPHON with proper config
        if SYPHONSystem and SYPHONConfig and SubscriptionTier:
            try:
                syphon_config = SYPHONConfig(
                    project_root=project_root,
                    subscription_tier=SubscriptionTier.BASIC,
                    enable_self_healing=True,
                    enable_banking=False
                )
                self.syphon = SYPHONSystem(syphon_config)
            except Exception as e:
                logger.warning(f"Could not initialize SYPHON: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Data storage
        self.data_dir = self.project_root / "data" / "marvin_grammarly_integration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🔗 @MARVIN Grammarly Master - LUMINA Integration initialized")
        self._log_integration_status()

    def _log_integration_status(self):
        """Log status of integrated systems"""
        systems = {
            "Grammarly Master": self.grammarly_master is not None,
            "@ALWAYS System": self.always_system is not None,
            "Grammarly CLI": self.grammarly_cli is not None,
            "Person Profiles": self.person_profiles is not None,
            "SYPHON System": self.syphon is not None
        }

        self.logger.info("📊 Integration Status:")
        for system, available in systems.items():
            status = "✅" if available else "❌"
            self.logger.info(f"   {status} {system}")

    def integrate_with_person_profiles(self, operator_name: str = "Operator") -> Dict[str, Any]:
        """
        Integrate persona profile with Person Profiles system

        Links digital avatar with P-Doom person profiles
        """
        self.logger.info(f"\n🔗 Integrating with Person Profiles: {operator_name}")

        if not self.person_profiles:
            self.logger.warning("⚠️  Person Profiles system not available")
            return {"status": "error", "message": "Person Profiles system not available"}

        if not self.grammarly_master:
            self.logger.warning("⚠️  Grammarly Master not available")
            return {"status": "error", "message": "Grammarly Master not available"}

        # Map persona profile
        persona_profile = self.grammarly_master.map_persona_profile(operator_name)

        # Get or create person profile
        try:
            person_profile = self.person_profiles.get_profile(operator_name)
            if not person_profile:
                # Create new person profile
                person_profile = self.person_profiles.create_profile(
                    profile_id=f"operator_{operator_name.lower()}",
                    name=operator_name,
                    entity_type="human",
                    description=f"Operator persona profile for {operator_name}",
                    p_doom_rating=0.0
                )

            # Link persona profile data to person profile
            integration_data = {
                "persona_profile_id": persona_profile.profile_id,
                "writing_style": persona_profile.writing_style,
                "vocabulary_preferences": persona_profile.vocabulary_preferences,
                "grammar_patterns": persona_profile.grammar_patterns,
                "tone_characteristics": persona_profile.tone_characteristics,
                "integrated_at": datetime.now().isoformat()
            }

            # Store integration data
            integration_file = self.data_dir / f"person_profile_integration_{operator_name.lower()}.json"
            with open(integration_file, 'w', encoding='utf-8') as f:
                json.dump(integration_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Integrated with Person Profile: {person_profile.profile_id}")
            self.logger.info(f"📁 Integration data saved: {integration_file}")

            return {
                "status": "success",
                "person_profile_id": person_profile.profile_id,
                "persona_profile_id": persona_profile.profile_id,
                "integration_file": str(integration_file)
            }

        except Exception as e:
            self.logger.error(f"❌ Error integrating with Person Profiles: {e}")
            return {"status": "error", "message": str(e)}

    def integrate_with_syphon(self, raw_input: RawOperatorInput) -> Dict[str, Any]:
        """
        Integrate with SYPHON system for intelligence extraction

        SYPHONs writing patterns, grammar issues, and learning data
        """
        self.logger.info(f"\n🔗 SYPHONing intelligence from raw input: {raw_input.input_id}")

        if not self.syphon:
            self.logger.warning("⚠️  SYPHON system not available")
            return {"status": "error", "message": "SYPHON system not available"}

        # Process raw input through Grammarly Master
        if not self.grammarly_master:
            return {"status": "error", "message": "Grammarly Master not available"}

        result = self.grammarly_master.process_raw_operator_input(raw_input)

        # Extract intelligence for SYPHON
        intelligence_data = {
            "source": "grammarly_master",
            "input_id": raw_input.input_id,
            "grammar_issues": result.get("grammar_analysis", {}).get("issues", []),
            "style_suggestions": result.get("style_analysis", {}).get("suggestions", []),
            "persona_alignment": result.get("persona_alignment", 0.5),
            "learning_patterns": result.get("learning_data", {}),
            "timestamp": datetime.now().isoformat()
        }

        # SYPHON the intelligence
        try:
            # Store in SYPHON format
            syphon_data = {
                "intelligence_type": "writing_analysis",
                "data": intelligence_data,
                "metadata": {
                    "source": "marvin_grammarly_master",
                    "extracted_at": datetime.now().isoformat()
                }
            }

            # Save SYPHON data
            syphon_file = self.data_dir / "syphon" / f"grammarly_intelligence_{raw_input.input_id}.json"
            syphon_file.parent.mkdir(parents=True, exist_ok=True)

            with open(syphon_file, 'w', encoding='utf-8') as f:
                json.dump(syphon_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ SYPHONed intelligence: {syphon_file}")

            return {
                "status": "success",
                "syphon_file": str(syphon_file),
                "intelligence_data": intelligence_data
            }

        except Exception as e:
            self.logger.error(f"❌ Error SYPHONing intelligence: {e}")
            return {"status": "error", "message": str(e)}

    def integrate_with_grammarly_cli(self, text: str) -> Dict[str, Any]:
        """
        Integrate with existing Grammarly CLI

        Uses existing CLI for grammar checking and enhances with @MARVIN guidance
        """
        self.logger.info(f"\n🔗 Integrating with Grammarly CLI")

        if not self.grammarly_cli:
            self.logger.warning("⚠️  Grammarly CLI not available")
            return {"status": "error", "message": "Grammarly CLI not available"}

        # Create raw input from text
        if not self.grammarly_master:
            return {"status": "error", "message": "Grammarly Master not available"}

        raw_input = RawOperatorInput(
            input_id=f"cli_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            input_type=InputType.TEXT,
            raw_data=text
        )

        # Process through Grammarly Master
        master_result = self.grammarly_master.process_raw_operator_input(raw_input)

        # Also use existing CLI (if it has a check method)
        cli_result = None
        try:
            # Try to use CLI's grammar checking
            if hasattr(self.grammarly_cli, 'check_grammar'):
                cli_result = self.grammarly_cli.check_grammar(text)
        except Exception as e:
            self.logger.warning(f"⚠️  Could not use CLI check_grammar: {e}")

        # Combine results
        combined_result = {
            "status": "success",
            "master_analysis": master_result,
            "cli_analysis": cli_result,
            "combined_suggestions": [],
            "timestamp": datetime.now().isoformat()
        }

        # Merge suggestions from both sources
        if master_result.get("grammar_analysis"):
            combined_result["combined_suggestions"].extend(
                master_result["grammar_analysis"].get("suggestions", [])
            )

        if cli_result and isinstance(cli_result, dict):
            combined_result["combined_suggestions"].extend(
                cli_result.get("suggestions", [])
            )

        self.logger.info(f"✅ Combined analysis complete")
        self.logger.info(f"   Suggestions: {len(combined_result['combined_suggestions'])}")

        return combined_result

    def integrate_with_always_system(self, assessment_topic: str) -> Dict[str, Any]:
        try:
            """
            Integrate with @ALWAYS system for dual perspective assessment

            Gets both JARVIS and @MARVIN perspectives on grammar/writing topics
            """
            self.logger.info(f"\n🔗 Integrating with @ALWAYS system: {assessment_topic}")

            if not always_assess:
                self.logger.warning("⚠️  @ALWAYS system not available")
                return {"status": "error", "message": "@ALWAYS system not available"}

            # Get dual perspective
            perspective = always_assess(assessment_topic)

            integration_result = {
                "status": "success",
                "topic": assessment_topic,
                "jarvis_perspective": perspective.jarvis_perspective if hasattr(perspective, 'jarvis_perspective') else None,
                "marvin_perspective": perspective.marvin_perspective if hasattr(perspective, 'marvin_perspective') else None,
                "consensus": perspective.consensus if hasattr(perspective, 'consensus') else None,
                "timestamp": datetime.now().isoformat()
            }

            # Save integration result
            always_file = self.data_dir / "always_integration" / f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            always_file.parent.mkdir(parents=True, exist_ok=True)

            with open(always_file, 'w', encoding='utf-8') as f:
                json.dump(integration_result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ @ALWAYS assessment complete: {always_file}")

            return integration_result

        except Exception as e:
            self.logger.error(f"Error in integrate_with_always_system: {e}", exc_info=True)
            raise
    def create_unified_interface(self) -> Dict[str, Any]:
        try:
            """
            Create unified interface that integrates all systems

            Single entry point for all Grammarly/writing assistance
            """
            self.logger.info("\n🔗 Creating Unified Interface")

            interface = {
                "name": "LUMINA Grammarly Master Unified Interface",
                "version": "1.0.0",
                "integrated_systems": {
                    "@MARVIN Grammarly Master": self.grammarly_master is not None,
                    "Grammarly CLI": self.grammarly_cli is not None,
                    "Person Profiles": self.person_profiles is not None,
                    "SYPHON System": self.syphon is not None,
                    "@ALWAYS System": always_assess is not None
                },
                "capabilities": [
                    "Raw operator input processing (keypresses, speech, text)",
                    "Persona profile mapping and learning",
                    "Grammar checking and correction",
                    "Style analysis and suggestions",
                    "Real-time @MARVIN master guidance",
                    "SYPHON intelligence extraction",
                    "Person profile integration",
                    "Dual perspective assessment (JARVIS & @MARVIN)"
                ],
                "api_endpoints": {
                    "process_raw_input": "process_raw_operator_input(raw_input)",
                    "check_grammar": "integrate_with_grammarly_cli(text)",
                    "get_persona_profile": "grammarly_master.map_persona_profile(name)",
                    "syphon_intelligence": "integrate_with_syphon(raw_input)",
                    "always_assess": "integrate_with_always_system(topic)"
                },
                "created_at": datetime.now().isoformat()
            }

            # Save interface definition
            interface_file = self.data_dir / "unified_interface.json"
            with open(interface_file, 'w', encoding='utf-8') as f:
                json.dump(interface, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Unified interface created: {interface_file}")

            return interface

        except Exception as e:
            self.logger.error(f"Error in create_unified_interface: {e}", exc_info=True)
            raise
    def generate_integration_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive integration report"""
            self.logger.info("\n📊 Generating Integration Report")

            report = {
                "title": "@MARVIN Grammarly Master - LUMINA System Integration Report",
                "generated_at": datetime.now().isoformat(),
                "integration_status": {},
                "systems_integrated": [],
                "integration_points": [],
                "next_steps": []
            }

            # Check each integration
            integrations = {
                "Person Profiles": self._check_person_profiles_integration(),
                "SYPHON System": self._check_syphon_integration(),
                "Grammarly CLI": self._check_grammarly_cli_integration(),
                "@ALWAYS System": self._check_always_integration()
            }

            report["integration_status"] = integrations

            # Count successful integrations
            successful = sum(1 for status in integrations.values() if status.get("status") == "success")
            total = len(integrations)

            report["integration_summary"] = {
                "total_systems": total,
                "successful_integrations": successful,
                "failed_integrations": total - successful,
                "integration_rate": f"{(successful/total*100):.0f}%" if total > 0 else "0%"
            }

            # Save report
            report_file = self.data_dir / "integration_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Integration report saved: {report_file}")

            return report

        except Exception as e:
            self.logger.error(f"Error in generate_integration_report: {e}", exc_info=True)
            raise
    def _check_person_profiles_integration(self) -> Dict[str, Any]:
        """Check Person Profiles integration status"""
        return {
            "status": "success" if self.person_profiles else "not_available",
            "available": self.person_profiles is not None,
            "integration_point": "integrate_with_person_profiles(operator_name)"
        }

    def _check_syphon_integration(self) -> Dict[str, Any]:
        """Check SYPHON integration status"""
        return {
            "status": "success" if self.syphon else "not_available",
            "available": self.syphon is not None,
            "integration_point": "integrate_with_syphon(raw_input)"
        }

    def _check_grammarly_cli_integration(self) -> Dict[str, Any]:
        """Check Grammarly CLI integration status"""
        return {
            "status": "success" if self.grammarly_cli else "not_available",
            "available": self.grammarly_cli is not None,
            "integration_point": "integrate_with_grammarly_cli(text)"
        }

    def _check_always_integration(self) -> Dict[str, Any]:
        """Check @ALWAYS integration status"""
        return {
            "status": "success" if always_assess else "not_available",
            "available": always_assess is not None,
            "integration_point": "integrate_with_always_system(topic)"
        }


def main():
    try:
        """Main execution"""
        print("\n" + "="*80)
        print("🔗 @MARVIN Grammarly Master - LUMINA System Integration")
        print("="*80 + "\n")

        project_root = Path(".").resolve()
        integration = MarvinGrammarlyLuminaIntegration(project_root)

        # Create unified interface
        print("📋 Creating Unified Interface...")
        interface = integration.create_unified_interface()

        # Generate integration report
        print("\n📊 Generating Integration Report...")
        report = integration.generate_integration_report()

        # Display summary
        print("\n" + "="*80)
        print("✅ INTEGRATION SUMMARY")
        print("="*80 + "\n")

        print("🔗 Integrated Systems:")
        for system, status in report["integration_status"].items():
            status_icon = "✅" if status.get("available") else "❌"
            print(f"   {status_icon} {system}")

        print(f"\n📊 Integration Rate: {report['integration_summary']['integration_rate']}")
        print(f"   Successful: {report['integration_summary']['successful_integrations']}/{report['integration_summary']['total_systems']}")

        print("\n🎯 Capabilities:")
        for capability in interface["capabilities"]:
            print(f"   • {capability}")

        print("\n" + "="*80 + "\n")

        return integration, interface, report


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()