#!/usr/bin/env python3
"""
Deploy All Cron Entries to NAS Kron
<COMPANY_NAME> LLC

Deploys all cron files to NAS Kron scheduler.

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_kron_daemon_manager import NASKronDaemonManager

def main():
    try:
        """Deploy all cron files to NAS"""
        project_root = Path(__file__).parent.parent.parent
        cron_dir = project_root / "data" / "tasks" / "nas_kron"

        print("=" * 80)
        print("DEPLOYING ALL CRON ENTRIES TO NAS KRON")
        print("=" * 80)
        print()

        manager = NASKronDaemonManager(project_root)

        # Check credentials before deploying; prompt login if missing
        creds = manager._get_credentials()
        if not creds:
            print("❌ No credentials active. Please run: az login")
            try:
                from prompt_nas_login import print_nas_login_prompts
                print_nas_login_prompts()
            except ImportError:
                print("   Then ensure nas-username and nas-password exist in Key Vault (jarvis-lumina).")
            return 1

        cron_files = list(cron_dir.glob("*.cron"))

        if not cron_files:
            print("❌ No cron files found in data/tasks/nas_kron/")
            return 1

        print(f"Found {len(cron_files)} cron file(s):")
        for cron_file in cron_files:
            print(f"  - {cron_file.name}")
        print()

        deployed = 0
        failed = 0

        for cron_file in cron_files:
            print(f"🚀 Deploying {cron_file.name}...")
            if manager.deploy_cron_to_nas(cron_file):
                print(f"   ✅ Deployed successfully")
                deployed += 1
            else:
                print(f"   ❌ Deployment failed")
                failed += 1
            print()

        print("=" * 80)
        print("DEPLOYMENT SUMMARY")
        print("=" * 80)
        print(f"Total cron files: {len(cron_files)}")
        print(f"Successfully deployed: {deployed}")
        print(f"Failed: {failed}")
        print("=" * 80)

        if failed > 0:
            print()
            print("⚠️  Some deployments failed. Check NAS SSH configuration.")
            print("   Config file: config/lumina_nas_ssh_config.json")

        return 0 if failed == 0 else 1

    except Exception as e:
        print(f"❌ Error in main: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
if __name__ == "__main__":



    sys.exit(main())