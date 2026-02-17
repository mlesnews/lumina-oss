#!/usr/bin/env python3
"""
Verify VA SYPHON/R5/JARVIS Integrations

Verifies that all virtual assistants have active SYPHON/R5/JARVIS integrations.

Tags: #VA #VERIFICATION #SYPHON @JARVIS @LUMINA
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any

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

logger = get_logger("VerifyVASyphonIntegrations")


class VAIntegrationVerifier:
    """Verifies VA integrations"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.va_files = [
            project_root / "scripts" / "python" / "ironman_virtual_assistant.py",
            project_root / "scripts" / "python" / "kenny_imva_enhanced.py",
            project_root / "scripts" / "python" / "anakin_combat_virtual_assistant.py",
            project_root / "scripts" / "python" / "jarvis_virtual_assistant.py"
        ]

    def verify_integrations(self, va_file: Path) -> Dict[str, Any]:
        try:
            """Verify integrations in a VA file"""
            if not va_file.exists():
                return {"exists": False}

            with open(va_file, 'r', encoding='utf-8') as f:
                content = f.read()

            results = {
                "file": va_file.name,
                "exists": True,
                "syphon": {
                    "imported": "from syphon" in content or "import syphon" in content,
                    "initialized": "SYPHONSystem" in content and "self.syphon" in content,
                    "used": "self.syphon." in content and content.count("self.syphon.") > 1,
                    "active": "syphon_enhancement" in content.lower() or "syphon.extract" in content
                },
                "r5": {
                    "imported": "from r5" in content or "import r5" in content or "R5LivingContextMatrix" in content,
                    "initialized": "R5LivingContextMatrix" in content and "self.r5" in content,
                    "used": "self.r5." in content,
                    "active": "r5." in content.lower() or "r5_aggregation" in content.lower()
                },
                "jarvis": {
                    "imported": "JARVISFullTimeSuperAgent" in content or "from jarvis" in content,
                    "initialized": "JARVISFullTimeSuperAgent" in content and "self.jarvis" in content,
                    "used": "self.jarvis." in content,
                    "active": "jarvis." in content.lower() or "jarvis_integration" in content.lower()
                },
                "action_sequences": {
                    "imported": "VAActionSequenceSystem" in content or "va_action_sequence" in content,
                    "initialized": "VAActionSequenceSystem" in content and "action_sequence_system" in content,
                    "used": "action_sequence_system" in content,
                    "active": "start_all_sequences" in content or "integrate_action_sequences" in content
                }
            }

            return results

        except Exception as e:
            self.logger.error(f"Error in verify_integrations: {e}", exc_info=True)
            raise
    def verify_all(self) -> Dict[str, Any]:
        try:
            """Verify all VAs"""
            logger.info("=" * 80)
            logger.info("🔍 VERIFYING VA SYPHON/R5/JARVIS INTEGRATIONS")
            logger.info("=" * 80)
            logger.info("")

            all_results = {}

            for va_file in self.va_files:
                if va_file.exists():
                    results = self.verify_integrations(va_file)
                    all_results[va_file.stem] = results

                    logger.info(f"📋 {va_file.name}")
                    logger.info("-" * 80)

                    # SYPHON
                    syphon = results["syphon"]
                    syphon_status = "✅" if (syphon["imported"] and syphon["initialized"] and syphon["used"]) else "❌"
                    logger.info(f"  {syphon_status} SYPHON:")
                    logger.info(f"     Imported: {'✅' if syphon['imported'] else '❌'}")
                    logger.info(f"     Initialized: {'✅' if syphon['initialized'] else '❌'}")
                    logger.info(f"     Used: {'✅' if syphon['used'] else '❌'} ({content.count('self.syphon.') if 'content' in locals() else 0} calls)")
                    logger.info(f"     Active: {'✅' if syphon['active'] else '❌'}")

                    # R5
                    r5 = results["r5"]
                    r5_status = "✅" if (r5["imported"] and r5["initialized"] and r5["used"]) else "❌"
                    logger.info(f"  {r5_status} R5:")
                    logger.info(f"     Imported: {'✅' if r5['imported'] else '❌'}")
                    logger.info(f"     Initialized: {'✅' if r5['initialized'] else '❌'}")
                    logger.info(f"     Used: {'✅' if r5['used'] else '❌'}")
                    logger.info(f"     Active: {'✅' if r5['active'] else '❌'}")

                    # JARVIS
                    jarvis = results["jarvis"]
                    jarvis_status = "✅" if (jarvis["imported"] and jarvis["initialized"] and jarvis["used"]) else "❌"
                    logger.info(f"  {jarvis_status} JARVIS:")
                    logger.info(f"     Imported: {'✅' if jarvis['imported'] else '❌'}")
                    logger.info(f"     Initialized: {'✅' if jarvis['initialized'] else '❌'}")
                    logger.info(f"     Used: {'✅' if jarvis['used'] else '❌'}")
                    logger.info(f"     Active: {'✅' if jarvis['active'] else '❌'}")

                    # Action Sequences
                    action_seq = results["action_sequences"]
                    action_seq_status = "✅" if (action_seq["imported"] and action_seq["initialized"] and action_seq["used"]) else "❌"
                    logger.info(f"  {action_seq_status} Action Sequences:")
                    logger.info(f"     Imported: {'✅' if action_seq['imported'] else '❌'}")
                    logger.info(f"     Initialized: {'✅' if action_seq['initialized'] else '❌'}")
                    logger.info(f"     Used: {'✅' if action_seq['used'] else '❌'}")
                    logger.info(f"     Active: {'✅' if action_seq['active'] else '❌'}")

                    logger.info("")
                else:
                    logger.warning(f"⚠️  {va_file.name} not found")
                    logger.info("")

            # Summary
            logger.info("=" * 80)
            logger.info("📊 INTEGRATION SUMMARY")
            logger.info("=" * 80)

            total_vas = len(all_results)
            syphon_integrated = sum(1 for r in all_results.values() if r.get("syphon", {}).get("used", False))
            r5_integrated = sum(1 for r in all_results.values() if r.get("r5", {}).get("used", False))
            jarvis_integrated = sum(1 for r in all_results.values() if r.get("jarvis", {}).get("used", False))
            action_seq_integrated = sum(1 for r in all_results.values() if r.get("action_sequences", {}).get("used", False))

            logger.info(f"Total VAs: {total_vas}")
            logger.info(f"SYPHON Integrated: {syphon_integrated}/{total_vas} ✅" if syphon_integrated == total_vas else f"SYPHON Integrated: {syphon_integrated}/{total_vas} ⚠️")
            logger.info(f"R5 Integrated: {r5_integrated}/{total_vas} ✅" if r5_integrated == total_vas else f"R5 Integrated: {r5_integrated}/{total_vas} ⚠️")
            logger.info(f"JARVIS Integrated: {jarvis_integrated}/{total_vas} ✅" if jarvis_integrated == total_vas else f"JARVIS Integrated: {jarvis_integrated}/{total_vas} ⚠️")
            logger.info(f"Action Sequences Integrated: {action_seq_integrated}/{total_vas} ✅" if action_seq_integrated == total_vas else f"Action Sequences Integrated: {action_seq_integrated}/{total_vas} ⚠️")
            logger.info("")

            if syphon_integrated == total_vas and r5_integrated == total_vas:
                logger.info("✅ All integrations verified! VAs are ready with SYPHON/R5/JARVIS.")
            else:
                logger.warning("⚠️  Some integrations missing. Run syphon_va_improvement_system.py --all to fix.")

            logger.info("=" * 80)

            return all_results


        except Exception as e:
            self.logger.error(f"Error in verify_all: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        verifier = VAIntegrationVerifier(project_root)
        results = verifier.verify_all()

        # Save results
        import json
        results_file = project_root / "data" / "va_integration_verification.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"✅ Results saved: {results_file.name}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()