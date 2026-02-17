#!/usr/bin/env python3
"""
LUMINA System Reboot with Post-Reboot Evaluation

Reboots system and sets up automatic post-reboot evaluation.
Uses decision-making workflows and troubleshooting.

Tags: #REBOOT #SYSTEM_EVALUATION #AUTOMATION @JARVIS @LUMINA
"""

import sys
import subprocess
import winreg
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    logger = get_adaptive_logger("LuminaSystemReboot")
except ImportError:
    from lumina_logger import get_logger
    logger = get_logger("LuminaSystemReboot")


def setup_post_reboot_evaluation():
    """Set up post-reboot evaluation in Windows Registry"""
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\RunOnce"

        post_reboot_script = project_root / "scripts" / "python" / "lumina_post_reboot_evaluation.pyw"

        # Create launcher script
        launcher_content = f'''#!/usr/bin/env pythonw
"""LUMINA Post-Reboot Evaluation Launcher"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lumina_post_reboot_evaluation import main
main()
'''

        with open(post_reboot_script, 'w', encoding='utf-8') as f:
            f.write(launcher_content)

        # Find Pythonw
        pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not Path(pythonw_exe).exists():
            pythonw_exe = sys.executable

        # Register in RunOnce (runs once after reboot)
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            reg_path,
            0,
            winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(
            key,
            "LUMINA_PostRebootEvaluation",
            0,
            winreg.REG_SZ,
            f'"{pythonw_exe}" "{post_reboot_script}"'
        )

        winreg.CloseKey(key)

        logger.info("   ✅ Post-reboot evaluation configured")
        return True

    except Exception as e:
        logger.error(f"   ❌ Error setting up post-reboot evaluation: {e}")
        return False


def reboot_system():
    """Reboot the system"""
    logger.info("")
    logger.info("🔄 REBOOTING SYSTEM...")
    logger.info("")
    logger.info("   ⚠️  System will reboot in 10 seconds")
    logger.info("   💡 Post-reboot evaluation will run automatically")
    logger.info("")

    try:
        # Schedule reboot
        subprocess.run(
            ["shutdown", "/r", "/t", "10", "/c", "LUMINA System Reboot - Post-reboot evaluation will run automatically"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logger.info("   ✅ Reboot scheduled")
        return True
    except Exception as e:
        logger.error(f"   ❌ Error scheduling reboot: {e}")
        return False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA System Reboot with Evaluation")
    parser.add_argument("--reboot", action="store_true", help="Reboot system now")
    parser.add_argument("--setup-only", action="store_true", help="Only setup post-reboot evaluation")

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("🔄 LUMINA SYSTEM REBOOT & EVALUATION")
    logger.info("="*80)
    logger.info("")

    # Add notification
    try:
        from lumina_notification_system import LuminaNotificationSystem
        notification = LuminaNotificationSystem()
        notification.show_notification(
            "LUMINA Reboot",
            "System reboot initiated - post-reboot evaluation will run automatically",
            "info"
        )
    except Exception:
        pass  # Notification failure shouldn't block reboot

    # Setup post-reboot evaluation
    logger.info("1️⃣  Setting up post-reboot evaluation...")
    if setup_post_reboot_evaluation():
        logger.info("   ✅ Post-reboot evaluation will run automatically after reboot")
    else:
        logger.warning("   ⚠️  Post-reboot evaluation setup failed")

    if args.setup_only:
        logger.info("")
        logger.info("✅ Setup complete (no reboot)")
        return 0

    if args.reboot:
        # Run immediate evaluation before reboot - with error recovery
        logger.info("")
        logger.info("2️⃣  Running pre-reboot evaluation...")
        try:
            from lumina_error_recovery import LuminaErrorRecovery, RetryConfig
            from lumina_holistic_system_evaluation import LuminaHolisticSystemEvaluation

            error_recovery = LuminaErrorRecovery()

            def run_pre_reboot_evaluation():
                evaluator = LuminaHolisticSystemEvaluation()
                return evaluator.run_evaluation()

            error_recovery.execute_with_recovery(
                operation=run_pre_reboot_evaluation,
                operation_name="Pre-Reboot Evaluation",
                retry_config=RetryConfig(max_attempts=2, delay=1.0)
            )
        except Exception as e:
            logger.warning(f"   ⚠️  Pre-reboot evaluation failed: {e}")
            # Continue with reboot even if evaluation fails

        # Reboot
        if reboot_system():
            logger.info("")
            logger.info("="*80)
            logger.info("✅ REBOOT INITIATED")
            logger.info("="*80)
            logger.info("")
            logger.info("💡 After reboot:")
            logger.info("   • Post-reboot evaluation will run automatically")
            logger.info("   • All systems will be evaluated")
            logger.info("   • Weak spots will be identified")
            logger.info("   • Optimization recommendations will be generated")
            logger.info("")
            return 0
        else:
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":


    sys.exit(main())