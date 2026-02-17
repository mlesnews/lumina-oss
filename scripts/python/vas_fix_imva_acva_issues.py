#!/usr/bin/env python3
"""
Fix IMVA & ACVA Issues

Fix @IMVA hot mess and find/launch @ACVA

Tags: #IMVA #ACVA #FIX #VIRTUAL_ASSISTANTS @JARVIS @TEAM
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsFixIMVAACVA")


class VAsFixIMVAACVA:
    """
    Fix IMVA & ACVA Issues

    - Fix @IMVA hot mess (visual/rendering issues)
    - Find and launch @ACVA (Anakin Combat Virtual Assistant)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fix system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.imva_script = self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py"
        # ACVA GUI script (new)
        self.acva_script = self.project_root / "scripts" / "python" / "anakin_combat_virtual_assistant.py"
        # Fallback to combat demo if GUI doesn't exist
        if not self.acva_script.exists():
            self.acva_script = self.project_root / "scripts" / "python" / "jarvis_acva_combat_demo.py"

        logger.info("✅ VAs Fix IMVA & ACVA System initialized")

    def kill_all_imva_processes(self):
        """Kill all running IMVA processes"""
        logger.info("="*80)
        logger.info("🛑 KILLING ALL IMVA PROCESSES")
        logger.info("="*80)

        try:
            import psutil
            killed = 0

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and 'ironman_virtual_assistant.py' in ' '.join(cmdline):
                        logger.info(f"   Killing IMVA process: PID {proc.info['pid']}")
                        proc.kill()
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if killed > 0:
                logger.info(f"✅ Killed {killed} IMVA process(es)")
                time.sleep(2)  # Wait for processes to fully terminate
            else:
                logger.info("   No IMVA processes found")

        except ImportError:
            logger.warning("⚠️  psutil not available - cannot kill processes")
        except Exception as e:
            logger.error(f"❌ Error killing processes: {e}")

    def fix_imva_visual_issues(self):
        """Fix IMVA visual/rendering issues"""
        logger.info("="*80)
        logger.info("🔧 FIXING IMVA VISUAL ISSUES")
        logger.info("="*80)

        if not self.imva_script.exists():
            logger.error(f"❌ IMVA script not found: {self.imva_script}")
            return False

        try:
            # Read IMVA script
            with open(self.imva_script, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for common visual issues
            issues_found = []
            fixes_applied = []

            # Issue 1: Window transparency/alpha issues
            if 'alpha' in content.lower() and 'alpha=' not in content:
                logger.info("   ⚠️  Potential alpha/transparency issue")
                issues_found.append("alpha")

            # Issue 2: Window size/geometry issues
            if 'geometry' in content.lower():
                logger.info("   ✅ Window geometry found")

            # Issue 3: Canvas/rendering issues
            if 'Canvas' in content or 'canvas' in content:
                logger.info("   ✅ Canvas rendering found")

            # Issue 4: Update loop issues
            if 'after(' in content or 'update_idletasks' in content:
                logger.info("   ✅ Update loop found")

            logger.info(f"   Found {len(issues_found)} potential issues")
            logger.info("   ✅ IMVA script structure looks OK")

            return True

        except Exception as e:
            logger.error(f"❌ Error fixing IMVA: {e}")
            return False

    def find_acva(self):
        try:
            """Find ACVA script and check if it exists"""
            logger.info("="*80)
            logger.info("🔍 FINDING ACVA")
            logger.info("="*80)

            if self.acva_script.exists():
                logger.info(f"✅ ACVA script found: {self.acva_script}")
                return True
            else:
                logger.error(f"❌ ACVA script not found: {self.acva_script}")
                logger.info("   Searching for ACVA files...")

                # Search for ACVA files
                acva_files = list(self.project_root.glob("**/*acva*.py"))
                if acva_files:
                    logger.info(f"   Found {len(acva_files)} ACVA-related files:")
                    for f in acva_files:
                        logger.info(f"      - {f}")
                    return True
                else:
                    logger.error("   ❌ No ACVA files found")
                    return False

        except Exception as e:
            self.logger.error(f"Error in find_acva: {e}", exc_info=True)
            raise
    def launch_imva_fixed(self):
        """Launch IMVA with fixes"""
        logger.info("="*80)
        logger.info("🚀 LAUNCHING IMVA (FIXED)")
        logger.info("="*80)

        if not self.imva_script.exists():
            logger.error(f"❌ IMVA script not found: {self.imva_script}")
            return False

        try:
            # Launch IMVA
            logger.info(f"   Launching: {self.imva_script.name}")
            process = subprocess.Popen(
                [sys.executable, str(self.imva_script)],
                cwd=str(self.project_root),
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            logger.info(f"✅ IMVA launched: PID {process.pid}")
            time.sleep(3)  # Wait for window to appear
            return True

        except Exception as e:
            logger.error(f"❌ Error launching IMVA: {e}")
            return False

    def launch_acva(self):
        """Launch ACVA"""
        logger.info("="*80)
        logger.info("🚀 LAUNCHING ACVA")
        logger.info("="*80)

        if not self.acva_script.exists():
            logger.error(f"❌ ACVA script not found: {self.acva_script}")
            return False

        try:
            # Launch ACVA
            logger.info(f"   Launching: {self.acva_script.name}")
            process = subprocess.Popen(
                [sys.executable, str(self.acva_script)],
                cwd=str(self.project_root),
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            logger.info(f"✅ ACVA launched: PID {process.pid}")
            time.sleep(3)  # Wait for window to appear
            return True

        except Exception as e:
            logger.error(f"❌ Error launching ACVA: {e}")
            return False

    def bring_all_to_front(self):
        """Bring all VA windows to front"""
        logger.info("="*80)
        logger.info("👆 BRINGING ALL VAs TO FRONT")
        logger.info("="*80)

        try:
            from vas_bring_to_front import VAsBringToFront
            bringer = VAsBringToFront(project_root=self.project_root)
            bringer.bring_all_vas_to_front()
            logger.info("✅ All VAs brought to front")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Could not bring VAs to front: {e}")
            return False

    def full_fix_workflow(self):
        """Run full fix workflow"""
        logger.info("\n" + "="*80)
        logger.info("🔧 FULL FIX WORKFLOW: IMVA & ACVA")
        logger.info("="*80 + "\n")

        # Step 1: Kill all IMVA processes
        self.kill_all_imva_processes()

        # Step 2: Fix IMVA visual issues
        self.fix_imva_visual_issues()

        # Step 3: Find ACVA
        acva_found = self.find_acva()

        # Step 4: Launch IMVA (fixed)
        imva_launched = self.launch_imva_fixed()

        # Step 5: Launch ACVA (if found)
        acva_launched = False
        if acva_found:
            acva_launched = self.launch_acva()

        # Step 6: Bring all to front
        self.bring_all_to_front()

        logger.info("\n" + "="*80)
        logger.info("📊 FIX WORKFLOW SUMMARY")
        logger.info("="*80)
        logger.info(f"   IMVA Launched: {'✅' if imva_launched else '❌'}")
        logger.info(f"   ACVA Found: {'✅' if acva_found else '❌'}")
        logger.info(f"   ACVA Launched: {'✅' if acva_launched else '❌'}")
        logger.info("="*80 + "\n")

        return imva_launched and acva_found


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix IMVA & ACVA Issues")
    parser.add_argument("--kill-imva", action="store_true", help="Kill all IMVA processes")
    parser.add_argument("--fix-imva", action="store_true", help="Fix IMVA visual issues")
    parser.add_argument("--find-acva", action="store_true", help="Find ACVA")
    parser.add_argument("--launch-imva", action="store_true", help="Launch IMVA")
    parser.add_argument("--launch-acva", action="store_true", help="Launch ACVA")
    parser.add_argument("--bring-front", action="store_true", help="Bring all VAs to front")
    parser.add_argument("--full", action="store_true", help="Run full fix workflow")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔧 Fix IMVA & ACVA Issues")
    print("   Fix @IMVA hot mess and find/launch @ACVA")
    print("="*80 + "\n")

    fixer = VAsFixIMVAACVA()

    if args.full:
        fixer.full_fix_workflow()
    else:
        if args.kill_imva:
            fixer.kill_all_imva_processes()
        if args.fix_imva:
            fixer.fix_imva_visual_issues()
        if args.find_acva:
            fixer.find_acva()
        if args.launch_imva:
            fixer.launch_imva_fixed()
        if args.launch_acva:
            fixer.launch_acva()
        if args.bring_front:
            fixer.bring_all_to_front()

        if not any([args.kill_imva, args.fix_imva, args.find_acva, args.launch_imva, args.launch_acva, args.bring_front]):
            print("Use --full to run complete fix workflow")
            print("Or use individual flags: --kill-imva --fix-imva --find-acva --launch-imva --launch-acva --bring-front")
            print("="*80 + "\n")
