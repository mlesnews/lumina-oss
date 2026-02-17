#!/usr/bin/env python3
"""
NAS Migration Phase 2: Home Directory Migration

Implements Windows folder redirection and application data migration.

Tags: #NAS_MIGRATION #PHASE2 #HOME_DIRECTORY @JARVIS @LUMINA
"""

import sys
import os
import json
import subprocess
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

logger = get_logger("NASMigrationPhase2")


class HomeDirectoryMigrator:
    """Migrate home directory to NAS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "nas_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"
        self.nas_home = f"{self.nas_base}\\homes\\mlesn"

        # Windows folders to redirect
        self.windows_folders = {
            "Documents": {
                "local": Path(os.environ.get("USERPROFILE")) / "Documents",
                "nas": f"{self.nas_home}\\Documents",
                "registry_key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
                "registry_value": "Personal"
            },
            "Downloads": {
                "local": Path(os.environ.get("USERPROFILE")) / "Downloads",
                "nas": f"{self.nas_home}\\Downloads",
                "registry_key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
                "registry_value": "{374DE290-123F-4565-9164-39C4925E467B}"
            },
            "Pictures": {
                "local": Path(os.environ.get("USERPROFILE")) / "Pictures",
                "nas": f"{self.nas_home}\\Pictures",
                "registry_key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
                "registry_value": "My Pictures"
            },
            "Videos": {
                "local": Path(os.environ.get("USERPROFILE")) / "Videos",
                "nas": f"{self.nas_home}\\Videos",
                "registry_key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
                "registry_value": "My Video"
            },
            "Music": {
                "local": Path(os.environ.get("USERPROFILE")) / "Music",
                "nas": f"{self.nas_home}\\Music",
                "registry_key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders",
                "registry_value": "My Music"
            }
        }

    def generate_redirection_script(self) -> Dict:
        """Generate PowerShell script for folder redirection"""
        logger.info("=" * 80)
        logger.info("📁 PHASE 2.1: WINDOWS FOLDER REDIRECTION")
        logger.info("=" * 80)
        logger.info("")

        script_content = """# Windows Folder Redirection Script
# Generated: {timestamp}
# NAS: {nas_ip}

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{
    Write-Host "⚠️  This script requires Administrator privileges" -ForegroundColor Yellow
    Write-Host "   Right-click and 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}}

$nasHome = "{nas_home}"

# Ensure NAS share is accessible
if (-not (Test-Path $nasHome)) {{
    Write-Host "❌ NAS share not accessible: $nasHome" -ForegroundColor Red
    Write-Host "   Create share first using Phase 1.2 script" -ForegroundColor Yellow
    exit 1
}}

Write-Host "✅ NAS share accessible: $nasHome" -ForegroundColor Green
Write-Host ""

""".format(
            timestamp=datetime.now().isoformat(),
            nas_ip=self.nas_ip,
            nas_home=self.nas_home
        )

        # Add redirection for each folder
        for folder_name, folder_info in self.windows_folders.items():
            script_content += f"""
# Redirect {folder_name}
Write-Host "📁 Redirecting {folder_name}..." -ForegroundColor Cyan
$localPath = "{folder_info['local']}"
$nasPath = "{folder_info['nas']}"

# Create NAS directory if it doesn't exist
if (-not (Test-Path $nasPath)) {{
    New-Item -ItemType Directory -Path $nasPath -Force | Out-Null
    Write-Host "   ✅ Created NAS directory: $nasPath" -ForegroundColor Green
}}

# Move existing files if local folder has content
if ((Test-Path $localPath) -and ((Get-ChildItem $localPath -Force | Measure-Object).Count -gt 0)) {{
    Write-Host "   📦 Moving existing files to NAS..." -ForegroundColor Yellow
    robocopy "$localPath" "$nasPath" /E /MOVE /R:3 /W:5 /LOG:"$env:TEMP\\{folder_name}_migration.log"
    Write-Host "   ✅ Files moved" -ForegroundColor Green
}}

# Set registry value for folder redirection
$regKey = "{folder_info['registry_key']}"
$regValue = "{folder_info['registry_value']}"
$regPath = $nasPath

try {{
    Set-ItemProperty -Path "Registry::$regKey" -Name $regValue -Value $regPath -Type ExpandString -Force
    Write-Host "   ✅ Registry updated" -ForegroundColor Green
}} catch {{
    Write-Host "   ⚠️  Registry update failed: $_" -ForegroundColor Yellow
    Write-Host "      Manual update may be required" -ForegroundColor Yellow
}}

Write-Host ""
"""

        script_content += """
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ FOLDER REDIRECTION COMPLETE" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  You may need to log out and log back in for changes to take effect" -ForegroundColor Yellow
Write-Host ""
"""

        # Save script
        script_file = self.data_dir / "redirect_windows_folders.ps1"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"💾 PowerShell script generated: {script_file}")
        logger.info("   Run as Administrator: powershell -ExecutionPolicy Bypass -File redirect_windows_folders.ps1")
        logger.info("")

        return {
            "script_file": str(script_file),
            "folders": list(self.windows_folders.keys()),
            "nas_home": self.nas_home
        }

    def generate_application_migration_script(self) -> Dict:
        """Generate script for application data migration"""
        logger.info("=" * 80)
        logger.info("📦 PHASE 2.3: APPLICATION DATA MIGRATION")
        logger.info("=" * 80)
        logger.info("")

        applications = {
            "ollama": {
                "env_var": "OLLAMA_MODELS",
                "current_path": "C:\\Users\\mlesn\\AppData\\Local\\Ollama",
                "nas_path": f"{self.nas_base}\\data\\models\\ollama",
                "action": "redirect"
            },
            "docker": {
                "config_file": "C:\\Users\\mlesn\\.docker\\config.json",
                "current_path": "C:\\Users\\mlesn\\AppData\\Local\\Docker",
                "nas_path": f"{self.nas_base}\\data\\docker",
                "action": "migrate"
            },
            "vscode_extensions": {
                "current_path": "C:\\Users\\mlesn\\.vscode\\extensions",
                "nas_path": f"{self.nas_base}\\data\\cache\\vscode_extensions",
                "action": "redirect"
            },
            "npm_cache": {
                "env_var": "npm_config_cache",
                "current_path": "C:\\Users\\mlesn\\AppData\\Local\\npm-cache",
                "nas_path": f"{self.nas_base}\\data\\cache\\npm",
                "action": "redirect"
            },
            "pip_cache": {
                "env_var": "PIP_CACHE_DIR",
                "current_path": "C:\\Users\\mlesn\\AppData\\Local\\pip\\Cache",
                "nas_path": f"{self.nas_base}\\data\\cache\\pip",
                "action": "redirect"
            }
        }

        script_content = """# Application Data Migration Script
# Generated: {timestamp}

$nasBase = "{nas_base}"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "📦 APPLICATION DATA MIGRATION" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

""".format(
            timestamp=datetime.now().isoformat(),
            nas_base=self.nas_base
        )

        for app_name, app_info in applications.items():
            script_content += f"""
# {app_name.title()}
Write-Host "📦 Migrating {app_name}..." -ForegroundColor Cyan

"""

            if app_info["action"] == "redirect" and "env_var" in app_info:
                script_content += f"""
# Set environment variable
$envVar = "{app_info['env_var']}"
$nasPath = "{app_info['nas_path']}"

[Environment]::SetEnvironmentVariable($envVar, $nasPath, "User")
Write-Host "   ✅ Environment variable set: $envVar = $nasPath" -ForegroundColor Green

# Create NAS directory
if (-not (Test-Path $nasPath)) {{
    New-Item -ItemType Directory -Path $nasPath -Force | Out-Null
    Write-Host "   ✅ Created NAS directory" -ForegroundColor Green
}}
"""
            elif app_info["action"] == "migrate":
                script_content += f"""
# Migrate to NAS
$currentPath = "{app_info['current_path']}"
$nasPath = "{app_info['nas_path']}"

if ((Test-Path $currentPath) -and (Test-Path $nasPath)) {{
    Write-Host "   📦 Copying files to NAS..." -ForegroundColor Yellow
    robocopy "$currentPath" "$nasPath" /E /R:3 /W:5 /LOG:"$env:TEMP\\{app_name}_migration.log"
    Write-Host "   ✅ Migration complete" -ForegroundColor Green
}} else {{
    Write-Host "   ⚠️  Paths not accessible - check prerequisites" -ForegroundColor Yellow
}}
"""

            script_content += "Write-Host \"\"\n"

        script_content += """
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ APPLICATION MIGRATION COMPLETE" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Restart applications for changes to take effect" -ForegroundColor Yellow
Write-Host ""
"""

        script_file = self.data_dir / "migrate_application_data.ps1"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"💾 PowerShell script generated: {script_file}")
        logger.info("")

        return {
            "script_file": str(script_file),
            "applications": list(applications.keys())
        }

    def generate_symlink_script(self) -> Dict:
        """Generate script for creating symlinks"""
        logger.info("=" * 80)
        logger.info("🔗 PHASE 2.4: CREATE SYMLINKS")
        logger.info("=" * 80)
        logger.info("")

        symlinks = {
            "ollama_local": {
                "target": f"{self.nas_base}\\data\\models\\ollama",
                "link": "C:\\Users\\mlesn\\AppData\\Local\\Ollama",
                "description": "Ollama models symlink"
            },
            "docker_local": {
                "target": f"{self.nas_base}\\data\\docker",
                "link": "C:\\Users\\mlesn\\.docker\\nas",
                "description": "Docker NAS symlink"
            }
        }

        script_content = """# Symlink Creation Script
# Generated: {timestamp}
# Requires Administrator privileges

if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{
    Write-Host "⚠️  This script requires Administrator privileges" -ForegroundColor Yellow
    exit 1
}}

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "🔗 CREATING SYMLINKS" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

""".format(
            timestamp=datetime.now().isoformat()
        )

        for link_name, link_info in symlinks.items():
            script_content += f"""
# {link_info['description']}
Write-Host "🔗 Creating symlink: {link_name}..." -ForegroundColor Cyan
$target = "{link_info['target']}"
$link = "{link_info['link']}"

# Remove existing link if exists
if (Test-Path $link) {{
    Remove-Item $link -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "   🗑️  Removed existing link" -ForegroundColor Yellow
}}

# Create parent directory if needed
$linkParent = Split-Path $link -Parent
if (-not (Test-Path $linkParent)) {{
    New-Item -ItemType Directory -Path $linkParent -Force | Out-Null
}}

# Create symlink
try {{
    New-Item -ItemType SymbolicLink -Path $link -Target $target -Force | Out-Null
    Write-Host "   ✅ Symlink created: $link -> $target" -ForegroundColor Green
}} catch {{
    Write-Host "   ❌ Failed to create symlink: $_" -ForegroundColor Red
}}

Write-Host ""
"""

        script_content += """
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "✅ SYMLINK CREATION COMPLETE" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
"""

        script_file = self.data_dir / "create_symlinks.ps1"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"💾 PowerShell script generated: {script_file}")
        logger.info("")

        return {
            "script_file": str(script_file),
            "symlinks": list(symlinks.keys())
        }

    def analyze_dropbox_options(self) -> Dict:
        """Analyze Dropbox options (Phase 2.2)"""
        logger.info("=" * 80)
        logger.info("📦 PHASE 2.2: DROPBOX CONSIDERATION")
        logger.info("=" * 80)
        logger.info("")

        dropbox_path = Path("C:\\Users\\mlesn\\Dropbox")
        dropbox_size = 0
        dropbox_files = 0

        if dropbox_path.exists():
            # Get size (quick estimate)
            try:
                for item in dropbox_path.rglob("*"):
                    if item.is_file():
                        try:
                            dropbox_size += item.stat().st_size
                            dropbox_files += 1
                            if dropbox_files > 1000:  # Sample only
                                break
                        except:
                            pass
            except:
                pass

        dropbox_size_gb = round(dropbox_size / (1024**3), 2)

        options = {
            "option_a": {
                "name": "Keep Dropbox Local (Sync Subset Only)",
                "description": "Keep Dropbox on local disk, sync only essential projects",
                "pros": ["Fast local access", "No network dependency", "Existing sync works"],
                "cons": ["Uses local disk space", "Limited to subset"],
                "recommended_for": "If disk space allows after other migrations"
            },
            "option_b": {
                "name": "Move Dropbox to NAS (LAN Sync)",
                "description": "Move Dropbox folder to NAS, configure LAN sync",
                "pros": ["Frees local disk", "Centralized storage", "LAN sync faster"],
                "cons": ["Requires Dropbox LAN sync setup", "Network dependency"],
                "recommended_for": "If NAS has good performance and reliability"
            },
            "option_c": {
                "name": "Replace with Synology Drive",
                "description": "Replace Dropbox with Synology Drive for LUMINA projects",
                "pros": ["Full control", "No external service", "Integrated with NAS"],
                "cons": ["Migration effort", "Different sync mechanism"],
                "recommended_for": "If moving away from Dropbox is acceptable"
            }
        }

        result = {
            "dropbox_path": str(dropbox_path),
            "estimated_size_gb": dropbox_size_gb,
            "file_count_sample": dropbox_files,
            "options": options,
            "recommendation": "option_a" if dropbox_size_gb < 50 else "option_b"
        }

        logger.info(f"Dropbox path: {dropbox_path}")
        logger.info(f"Estimated size: {dropbox_size_gb:.2f} GB (sample)")
        logger.info("")
        logger.info("Options:")
        for opt_id, opt_info in options.items():
            logger.info(f"  {opt_id.upper()}: {opt_info['name']}")
            logger.info(f"    {opt_info['description']}")
        logger.info("")
        logger.info(f"Recommendation: {result['recommendation'].upper()}")
        logger.info("")

        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = self.data_dir / f"phase2_dropbox_analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        logger.info(f"💾 Analysis saved: {analysis_file}")
        logger.info("")

        return result


def main():
    try:
        """Main execution"""
        migrator = HomeDirectoryMigrator(project_root)

        # Generate all Phase 2 scripts
        logger.info("Generating Phase 2 migration scripts...")
        logger.info("")

        redirection = migrator.generate_redirection_script()
        application = migrator.generate_application_migration_script()
        symlinks = migrator.generate_symlink_script()
        dropbox = migrator.analyze_dropbox_options()

        print("\n" + "=" * 80)
        print("✅ PHASE 2 SCRIPTS GENERATED")
        print("=" * 80)
        print()
        print("Scripts created:")
        print(f"  📁 Folder redirection: {Path(redirection['script_file']).name}")
        print(f"  📦 Application migration: {Path(application['script_file']).name}")
        print(f"  🔗 Symlinks: {Path(symlinks['script_file']).name}")
        print()
        print("Next steps:")
        print("  1. Create NAS shares (Phase 1.2)")
        print("  2. Run folder redirection script (as Administrator)")
        print("  3. Run application migration script")
        print("  4. Run symlink creation script (as Administrator)")
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()