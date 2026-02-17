#!/usr/bin/env python3
"""
Complete Startup Setup - Run all essential setup scripts
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartupCompleteSetup")


def run_script(script_name: str, description: str) -> bool:
    """Run a setup script"""
    print(f"\n{'='*80}")
    print(f"📋 {description}")
    print(f"{'='*80}")

    script_path = script_dir / "scripts" / "python" / script_name

    if not script_path.exists():
        print(f"⚠️  Script not found: {script_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_dir),
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def main():
    """Run complete startup setup"""
    print("=" * 80)
    print("🚀 COMPLETE STARTUP SETUP")
    print("=" * 80)
    print()
    print("This will run all essential setup scripts for your startup.")
    print("You can skip any step by pressing Ctrl+C and continuing.")
    print()

    input("Press Enter to continue...")
    print()

    # Setup steps
    steps = [
        ("setup_business_operations.py", "Business Operations Setup"),
        # Note: ElevenLabs credentials configured via Azure Key Vault
    ]

    completed = []
    failed = []

    for script, description in steps:
        try:
            if run_script(script, description):
                completed.append(description)
                print(f"✅ {description} completed")
            else:
                failed.append(description)
                print(f"❌ {description} failed")
        except KeyboardInterrupt:
            print(f"\n⏸️  Skipped: {description}")
            continue

    print()
    print("=" * 80)
    print("📊 Setup Summary")
    print("=" * 80)
    print(f"✅ Completed: {len(completed)}")
    print(f"❌ Failed: {len(failed)}")
    print()

    if completed:
        print("✅ Completed Steps:")
        for step in completed:
            print(f"   - {step}")
        print()

    if failed:
        print("❌ Failed Steps:")
        for step in failed:
            print(f"   - {step}")
        print()

    print("📋 Manual Steps Required:")
    print("   1. Complete ElevenLabs setup:")
    print("      - Get API key from ElevenLabs dashboard")
    print("      - Configure ConvAI agent and SMS")
    print("      - Run: python scripts/python/configure_11labs_sms_phone.py")
    print()
    print("   2. Configure business information:")
    print("      - Edit config/business.json")
    print("      - Store sensitive info in Azure Vault")
    print()
    print("   3. Review and customize templates:")
    print("      - templates/invoice_template.html")
    print("      - templates/proposal_template.md")
    print("      - templates/sop_template.md")
    print()
    print("=" * 80)
    print("🎉 Setup process complete!")
    print("=" * 80)
    print()
    print("📚 Next: Read docs/STARTUP_ACTION_PLAN.md for detailed guidance")


if __name__ == "__main__":


    main()