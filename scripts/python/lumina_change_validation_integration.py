#!/usr/bin/env python3
"""
LUMINA Change Validation Integration

Integrates change validation, visual/audible confirmation, keyboard verification,
microphone activation, and fidelity enhancement into LUMINA system.

@VALIDATION @CONFIRMATION @INTEGRATION @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
logger = get_logger("lumina_change_validation_integration")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import validation systems
try:
    from change_validation_system import ChangeValidationSystem
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

try:
    from automatic_microphone_activation import AutomaticMicrophoneActivation
    MIC_ACTIVATION_AVAILABLE = True
except ImportError:
    MIC_ACTIVATION_AVAILABLE = False

try:
    from keyboard_mapping_verification import KeyboardMappingVerification
    KEYBOARD_VERIFICATION_AVAILABLE = True
except ImportError:
    KEYBOARD_VERIFICATION_AVAILABLE = False

try:
    from virtual_assistant_fidelity_enhancer import VirtualAssistantFidelityEnhancer
    FIDELITY_ENHANCER_AVAILABLE = True
except ImportError:
    FIDELITY_ENHANCER_AVAILABLE = False


class LUMINAChangeValidationIntegration:
    """
    LUMINA Change Validation Integration

    Integrates all validation and confirmation systems.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize LUMINA change validation integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LUMINAValidation")

        # Systems
        self.change_validator = None
        self.mic_activation = None
        self.keyboard_verifier = None
        self.fidelity_enhancer = None

        # Initialize systems
        self._initialize_systems()

        self.logger.info("=" * 80)
        self.logger.info("✅ LUMINA CHANGE VALIDATION INTEGRATION")
        self.logger.info("=" * 80)
        self.logger.info(f"   Change Validation: {'✅' if self.change_validator else '❌'}")
        self.logger.info(f"   Microphone Activation: {'✅' if self.mic_activation else '❌'}")
        self.logger.info(f"   Keyboard Verification: {'✅' if self.keyboard_verifier else '❌'}")
        self.logger.info(f"   Fidelity Enhancer: {'✅' if self.fidelity_enhancer else '❌'}")
        self.logger.info("=" * 80)

    def _initialize_systems(self):
        """Initialize all validation systems"""
        # Initialize change validation
        if VALIDATION_AVAILABLE:
            try:
                self.change_validator = ChangeValidationSystem(project_root=self.project_root)
                self.logger.info("✅ Change Validation: INITIALIZED")
            except Exception as e:
                self.logger.warning(f"⚠️  Change Validation initialization failed: {e}")

        # Initialize microphone activation
        if MIC_ACTIVATION_AVAILABLE:
            try:
                self.mic_activation = AutomaticMicrophoneActivation(project_root=self.project_root)
                self.mic_activation.start()
                self.logger.info("✅ Microphone Activation: STARTED")
            except Exception as e:
                self.logger.warning(f"⚠️  Microphone Activation initialization failed: {e}")

        # Initialize keyboard verification
        if KEYBOARD_VERIFICATION_AVAILABLE:
            try:
                self.keyboard_verifier = KeyboardMappingVerification(project_root=self.project_root)
                self.logger.info("✅ Keyboard Verification: INITIALIZED")
            except Exception as e:
                self.logger.warning(f"⚠️  Keyboard Verification initialization failed: {e}")

        # Initialize fidelity enhancer
        if FIDELITY_ENHANCER_AVAILABLE:
            try:
                self.fidelity_enhancer = VirtualAssistantFidelityEnhancer(project_root=self.project_root)
                self.fidelity_enhancer.enhance_all_assistants()
                self.logger.info("✅ Fidelity Enhancer: INITIALIZED & ENHANCED")
            except Exception as e:
                self.logger.warning(f"⚠️  Fidelity Enhancer initialization failed: {e}")

    def validate_change(self, change_type: str, description: str, target: str) -> str:
        """Record, apply, and validate a change with confirmations"""
        if not self.change_validator:
            self.logger.warning("⚠️  Change validator not available")
            return None

        # Record change
        change_id = self.change_validator.record_change(change_type, description, target)

        # Apply and verify
        verified = self.change_validator.apply_change(change_id)

        if verified:
            self.logger.info(f"✅ Change validated with visual and audible confirmation: {change_id}")
        else:
            self.logger.warning(f"⚠️  Change validation failed: {change_id}")

        return change_id

    def verify_keyboard_mappings(self) -> Dict[str, Any]:
        """Verify all keyboard mappings"""
        if not self.keyboard_verifier:
            return {"error": "Keyboard verifier not available"}

        return self.keyboard_verifier.verify_all_mappings()

    def get_validation_status(self) -> Dict[str, Any]:
        """Get validation status"""
        status = {
            "change_validation": {
                "available": self.change_validator is not None,
                "total_changes": len(self.change_validator.changes) if self.change_validator else 0
            },
            "microphone_activation": {
                "available": self.mic_activation is not None,
                "active": self.mic_activation.microphone_active if self.mic_activation else False,
                "passive_listening": self.mic_activation.passive_listening if self.mic_activation else False
            },
            "keyboard_verification": {
                "available": self.keyboard_verifier is not None,
                "total_mappings": len(self.keyboard_verifier.expected_mappings) if self.keyboard_verifier else 0
            },
            "fidelity_enhancement": {
                "available": self.fidelity_enhancer is not None,
                "enhanced_assistants": len(self.fidelity_enhancer.current_fidelity) if self.fidelity_enhancer else 0
            }
        }

        return status


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Change Validation Integration")
        parser.add_argument("--validate", nargs=3, metavar=("TYPE", "DESCRIPTION", "TARGET"),
                           help="Validate a change")
        parser.add_argument("--verify-keyboard", action="store_true", help="Verify keyboard mappings")
        parser.add_argument("--status", action="store_true", help="Show validation status")

        args = parser.parse_args()

        integration = LUMINAChangeValidationIntegration()

        if args.validate:
            change_type, description, target = args.validate
            change_id = integration.validate_change(change_type, description, target)
            if change_id:
                print(f"✅ Change validated: {change_id}")
            else:
                print("❌ Change validation failed")

        if args.verify_keyboard:
            results = integration.verify_keyboard_mappings()
            import json
            print(json.dumps(results, indent=2))

        if args.status:
            status = integration.get_validation_status()
            import json
            print(json.dumps(status, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()