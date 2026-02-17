#!/usr/bin/env python3
"""
NAS Migration Phase 1.2: Create NAS Target Shares

Creates required shares on Synology NAS (<NAS_PRIMARY_IP>) for migration.

Tags: #NAS_MIGRATION #PHASE1 #SHARES @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NASMigrationShares")


class NASShareCreator:
    """Create NAS shares for migration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "nas_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"

        # Required shares from plan
        self.required_shares = {
            "homes": {
                "path": "/volume1/homes/mlesn",
                "description": "User home migration",
                "windows_path": f"{self.nas_base}\\homes\\mlesn",
                "permissions": "read_write",
                "priority": "HIGH"
            },
            "data_models": {
                "path": "/volume1/data/models",
                "description": "AI models (Ollama)",
                "windows_path": f"{self.nas_base}\\data\\models",
                "permissions": "read_write",
                "priority": "HIGH"
            },
            "data_docker": {
                "path": "/volume1/data/docker",
                "description": "Docker volumes",
                "windows_path": f"{self.nas_base}\\data\\docker",
                "permissions": "read_write",
                "priority": "HIGH"
            },
            "data_media": {
                "path": "/volume1/data/media",
                "description": "Large media files",
                "windows_path": f"{self.nas_base}\\data\\media",
                "permissions": "read_write",
                "priority": "MEDIUM"
            },
            "data_cache": {
                "path": "/volume1/data/cache",
                "description": "Application caches (npm, pip)",
                "windows_path": f"{self.nas_base}\\data\\cache",
                "permissions": "read_write",
                "priority": "LOW"
            },
            "pxe": {
                "path": "/volume1/pxe",
                "description": "PXE boot images (future)",
                "windows_path": f"{self.nas_base}\\pxe",
                "permissions": "read_write",
                "priority": "LOW"
            }
        }

    def generate_share_creation_script(self) -> Dict:
        try:
            """Generate script/instructions for creating shares"""
            logger.info("=" * 80)
            logger.info("📁 PHASE 1.2: NAS SHARE CREATION")
            logger.info("=" * 80)
            logger.info("")

            # Check existing shares
            existing_shares = self._check_existing_shares()

            script = {
                "timestamp": datetime.now().isoformat(),
                "nas_ip": self.nas_ip,
                "nas_base": self.nas_base,
                "shares": {},
                "creation_method": "synology_dsm_gui",
                "instructions": []
            }

            # Generate instructions for each share
            for share_id, share_info in self.required_shares.items():
                exists = existing_shares.get(share_id, False)

                script["shares"][share_id] = {
                    **share_info,
                    "exists": exists,
                    "status": "EXISTS" if exists else "NEEDS_CREATION"
                }

                if not exists:
                    logger.info(f"📁 {share_id}: {share_info['description']}")
                    logger.info(f"   Path: {share_info['path']}")
                    logger.info(f"   Windows: {share_info['windows_path']}")
                    logger.info(f"   Priority: {share_info['priority']}")
                    logger.info("")

                    script["instructions"].append({
                        "share": share_id,
                        "method": "dsm_gui",
                        "steps": [
                            "1. Log into Synology DSM (https://<NAS_PRIMARY_IP>:5001)",
                            f"2. Go to Control Panel > Shared Folder",
                            "3. Click 'Create'",
                            f"4. Name: {share_id}",
                            f"5. Location: {share_info['path']}",
                            f"6. Description: {share_info['description']}",
                            "7. Set permissions: Read/Write for user 'mlesn'",
                            "8. Click 'OK' to create"
                        ],
                        "alternative": {
                            "method": "ssh_command",
                            "command": f"sudo mkdir -p {share_info['path']} && sudo chown mlesn:users {share_info['path']} && sudo chmod 755 {share_info['path']}"
                        }
                    })

            # Save script
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_file = self.data_dir / f"phase1_share_creation_{timestamp}.json"
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(script, f, indent=2)

            # Generate PowerShell script for Windows mapping
            self._generate_powershell_mapping_script(script)

            logger.info("=" * 80)
            logger.info("✅ SHARE CREATION SCRIPT GENERATED")
            logger.info("=" * 80)
            logger.info(f"💾 Script saved: {script_file}")
            logger.info("")
            logger.info("📋 NEXT STEPS:")
            logger.info("   1. Log into Synology DSM: https://<NAS_PRIMARY_IP>:5001")
            logger.info("   2. Create shares using instructions in script file")
            logger.info("   3. Run PowerShell mapping script to map network drives")
            logger.info("")

            return script

        except Exception as e:
            self.logger.error(f"Error in generate_share_creation_script: {e}", exc_info=True)
            raise
    def _check_existing_shares(self) -> Dict[str, bool]:
        """Check which shares already exist"""
        existing = {}

        # Try to access each share
        for share_id, share_info in self.required_shares.items():
            windows_path = share_info["windows_path"]
            try:
                # Try to list directory (will fail if doesn't exist)
                import os
                if os.path.exists(windows_path):
                    existing[share_id] = True
                    logger.debug(f"   ✅ Share exists: {share_id}")
                else:
                    existing[share_id] = False
            except Exception:
                existing[share_id] = False

        return existing

    def _generate_powershell_mapping_script(self, script: Dict):
        """Generate PowerShell script to map network drives"""
        ps_script = """# NAS Network Drive Mapping Script
# Generated: {timestamp}
# NAS: {nas_ip}

# Map required network drives
$drives = @{{
""".format(
            timestamp=datetime.now().isoformat(),
            nas_ip=self.nas_ip
        )

        drive_letters = {
            "homes": "H",
            "data_models": "M",
            "data_docker": "D",
            "data_media": "V",
            "data_cache": "C",
            "pxe": "P"
        }

        for share_id, share_info in script["shares"].items():
            if share_id in drive_letters:
                drive = drive_letters[share_id]
                ps_script += f'    "{drive}" = "{share_info["windows_path"]}";\n'

        ps_script += """}

foreach ($drive in $drives.Keys) {
    $path = $drives[$drive]
    Write-Host "Mapping drive $drive to $path..."

    # Remove existing mapping if exists
    if (Test-Path "${drive}:") {
        net use ${drive}: /delete /y 2>$null
    }

    # Create new mapping
    net use ${drive}: "$path" /persistent:yes

    if (Test-Path "${drive}:") {
        Write-Host "  ✅ Drive $drive mapped successfully" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Failed to map drive $drive" -ForegroundColor Red
    }
}

Write-Host "`n✅ Network drive mapping complete!" -ForegroundColor Green
"""

        ps_file = self.data_dir / "map_nas_drives.ps1"
        with open(ps_file, 'w', encoding='utf-8') as f:
            f.write(ps_script)

        logger.info(f"💾 PowerShell script generated: {ps_file}")
        logger.info("   Run: powershell -ExecutionPolicy Bypass -File map_nas_drives.ps1")


def main():
    """Main execution"""
    creator = NASShareCreator(project_root)
    script = creator.generate_share_creation_script()

    print("\n" + "=" * 80)
    print("📁 NAS SHARE CREATION SUMMARY")
    print("=" * 80)
    print()

    for share_id, share_info in script["shares"].items():
        status = "✅ EXISTS" if share_info["exists"] else "❌ NEEDS CREATION"
        print(f"{status} {share_id:20s} {share_info['description']}")
        if not share_info["exists"]:
            print(f"      Path: {share_info['windows_path']}")
    print()


if __name__ == "__main__":


    main()