#!/usr/bin/env python3
"""
#KEYMASTER - High-Level Coordination Engine for the @TRIAD

Coordinates the @TRIAD (@TRIAGE + @BAU + @DOIT) and calls @ZUUL (@gatekeeper).
Implements the "Spectrum Editor Workflow" and "@v3 Verification".

"Are you the Keymaster?"

Tags: #KEYMASTER #TRIAD #ZUUL #SPECTRUM #V3 #EDITOR_WORKFLOW @LUMINA @JARVIS @DOIT
"""

import sys
import argparse
from pathlib import Path
import logging
logger = logging.getLogger("keymaster")


# Integrated Library Import
try:
    from lumina_core import ZuulGatekeeper, EditorWorkflow, V3Verifier, setup_paths
    setup_paths()
except ImportError:
    # Manual fallback for development
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from lumina_core import ZuulGatekeeper, EditorWorkflow, V3Verifier

def main():
    try:
        parser = argparse.ArgumentParser(description="#KEYMASTER Coordination Engine")
        parser.add_argument("files", nargs="*", help="Files to audit, sweep, or verify")
        parser.add_argument("--sweep", action="store_true", help="Run Spectrum Editor Sweep")
        parser.add_argument("--v3", action="store_true", help="Run Triple-Verification Protocol")
        parser.add_argument("--auto", action="store_true", help="Initiate YO JOE! Automation")
        parser.add_argument("--triad", action="store_true", help="Run full @TRIAD protocol")
        args = parser.parse_args()

        if args.auto:
            print("\n🦅 #KEYMASTER: Initiating YO JOE! Automation...")
            workflow = EditorWorkflow()
            # This triggers the automated fix cycle
            # For now, it runs a sweep and then a hypothetical fixer
            stack = workflow.sweep(args.files)
            print(f"\n📊 Initial Stack: Dirty={len(stack.red_stack)+len(stack.orange_stack)}")
            print("📌 Fixing RED and ORANGE files...")
            # Fix logic would go here
            workflow.auto_fix_stack()
            print("\n✅ Automation cycle complete. Rerunning sweep...")
            stack = workflow.sweep(args.files)
            sys.exit(0 if not (stack.red_stack or stack.orange_stack) else 1)

        if args.sweep:
            workflow = EditorWorkflow()
            print("\n🧹 #KEYMASTER: Initiating Spectrum Sweep...")
            stack = workflow.sweep(args.files)

            print(f"\n📊 Spectrum Results:")
            print(f"   🔴 RED (Dirty/Errors):    {len(stack.red_stack)}")
            for f in stack.red_stack: print(f"      - {Path(f).name}")

            print(f"   🟠 ORANGE (Dirty/Warn):   {len(stack.orange_stack)}")
            for f in stack.orange_stack: print(f"      - {Path(f).name}")

            print(f"   🔵 BLUE (Info/Review):    {len(stack.blue_stack)}")
            for f in stack.blue_stack: print(f"      - {Path(f).name}")

            print(f"   🔘 CYAN (Git Modified):   {len(stack.cyan_stack)}")
            for f in stack.cyan_stack: print(f"      - {Path(f).name}")

            print(f"   🔘 GREY (Git Clean):      {len(stack.grey_stack)}")
            print(f"   🟢 GREEN (Satisfied):     {len(stack.green_stack)}")

            safe_to_close = len(stack.grey_stack) + len(stack.green_stack)
            if safe_to_close > 0:
                print(f"\n✅ {safe_to_close} files are SAFE TO CLOSE (GREY/GREEN).")

            if stack.red_stack or stack.orange_stack or stack.cyan_stack:
                print("\n📌 Status: DIRTY. Systematically fixing Stack...")
                sys.exit(1)
            else:
                print("\n✨ Status: CLEAN. Gozer is satisfied.")
                sys.exit(0)

        if args.v3:
            verifier = V3Verifier()
            print("\n🛡️  #KEYMASTER: Initiating @v3 Triple-Verification...")
            report = verifier.verify_files(args.files)

            print(f"\n📈 Verification Report:")
            print(f"   V1: Work Verified:      {'✅' if report.v1_work_verified else '❌'}")
            print(f"   V2: Integration Valid:  {'✅' if report.v2_integration_validated else '❌'}")
            print(f"   V3: Truth Verified:     {'✅' if report.v3_truth_verified else '❌'}")

            if not report.v3_truth_verified:
                for detail in report.details: print(f"      - {detail}")
                sys.exit(1)
            else:
                print("\n⚡ Battletested. @v3 Complete. (GREEN)")
                sys.exit(0)

        # Default Audit Mode
        keymaster = ZuulGatekeeper()
        print("\n🗝️  #KEYMASTER: Initiating Spectrum Audit...")

        all_green = True
        for file_path in args.files:
            audit = keymaster.audit(file_path)
            if audit.status.value in ["RED", "ORANGE", "CYAN"]:
                all_green = False

        if all_green:
            print("\n⚡ #KEYMASTER: The @TRIAD is complete. (GREEN)")
            sys.exit(0)
        else:
            print("\n🔥 #KEYMASTER: Spectrum Audit Failed. (RED/ORANGE/CYAN)")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()