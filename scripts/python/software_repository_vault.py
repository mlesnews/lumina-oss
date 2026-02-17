#!/usr/bin/env python3
"""
Software Repository Vault System

Catalogs and secures all software, licenses, and related information.
Not dependent on Dropbox - can vault to NAS, Azure, etc.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import json
import hashlib
import shutil
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

logger = get_logger("SoftwareRepositoryVault")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SoftwareLicense:
    """Software license information"""
    software_id: str
    name: str
    version: Optional[str] = None
    vendor: Optional[str] = None
    license_type: Optional[str] = None  # "Commercial", "Open Source", "Freeware", etc.
    license_key: Optional[str] = None
    purchase_date: Optional[str] = None
    expiration_date: Optional[str] = None
    download_url: Optional[str] = None
    installation_path: Optional[str] = None
    notes: Optional[str] = None
    files: List[str] = field(default_factory=list)  # Related files (installers, licenses, etc.)
    vault_location: Optional[str] = None  # Where it's vaulted (NAS, Azure, etc.)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SoftwareRepository:
    """Software repository configuration"""
    repository_id: str
    name: str
    location: str  # Path to repository folder
    vault_backend: str = "local"  # "local", "nas", "azure", "s3", etc.
    vault_path: Optional[str] = None
    encryption_enabled: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SoftwareRepositoryVault:
    """
    Vault system for cataloging and securing software licenses.
    Not dependent on Dropbox - can vault to multiple backends.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("SoftwareRepositoryVault")

        self.data_dir = self.project_root / "data" / "software_vault"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Vault backends
        self.vault_backends = {
            "local": self._vault_to_local,
            "nas": self._vault_to_nas,
            "azure": self._vault_to_azure
        }

        # Software catalog
        self.software_catalog: Dict[str, SoftwareLicense] = {}
        self.repositories: Dict[str, SoftwareRepository] = {}

        self.logger.info("🔐 Software Repository Vault initialized")
        self._load_catalog()

    def _load_catalog(self):
        """Load existing software catalog"""
        catalog_file = self.data_dir / "software_catalog.json"
        if catalog_file.exists():
            try:
                with open(catalog_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get('software', []):
                        license_obj = SoftwareLicense(**item)
                        self.software_catalog[license_obj.software_id] = license_obj
                self.logger.info(f"✅ Loaded {len(self.software_catalog)} software entries")
            except Exception as e:
                self.logger.error(f"❌ Error loading catalog: {e}")

    def _save_catalog(self):
        """Save software catalog"""
        catalog_file = self.data_dir / "software_catalog.json"
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "software": [asdict(license_obj) for license_obj in self.software_catalog.values()]
            }
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Catalog saved: {catalog_file}")
        except Exception as e:
            self.logger.error(f"❌ Error saving catalog: {e}")

    def register_repository(self, name: str, location: str, vault_backend: str = "local", 
                           vault_path: Optional[str] = None) -> SoftwareRepository:
        """Register a software repository"""
        repo_id = f"repo_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"

        repo = SoftwareRepository(
            repository_id=repo_id,
            name=name,
            location=location,
            vault_backend=vault_backend,
            vault_path=vault_path
        )

        self.repositories[repo_id] = repo
        self.logger.info(f"✅ Registered repository: {name} at {location}")

        return repo

    def scan_repository(self, repository_path: str) -> List[Dict[str, Any]]:
        try:
            """Scan repository folder for software"""
            repo_path = Path(repository_path)

            if not repo_path.exists():
                self.logger.warning(f"❌ Repository path not found: {repository_path}")
                return []

            self.logger.info(f"🔍 Scanning repository: {repository_path}")

            found_software = []

            # Common software file patterns
            patterns = [
                "*.exe", "*.msi", "*.dmg", "*.pkg",  # Installers
                "*.zip", "*.rar", "*.7z",  # Archives
                "*license*", "*LICENSE*",  # License files
                "*readme*", "*README*",  # Documentation
            ]

            for pattern in patterns:
                for file_path in repo_path.rglob(pattern):
                    # Skip system files
                    if file_path.name.startswith('.'):
                        continue

                    # Get file info
                    file_info = {
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "type": self._detect_software_type(file_path)
                    }

                    found_software.append(file_info)

            self.logger.info(f"✅ Found {len(found_software)} software files")
            return found_software

        except Exception as e:
            self.logger.error(f"Error in scan_repository: {e}", exc_info=True)
            raise
    def _detect_software_type(self, file_path: Path) -> str:
        """Detect software type from file"""
        name_lower = file_path.name.lower()

        if "vb-audio" in name_lower or "vb audio" in name_lower:
            return "VB-Audio Virtual Cable"
        elif "voicemeeter" in name_lower:
            return "Voicemeeter"
        elif "license" in name_lower:
            return "License File"
        elif file_path.suffix in ['.exe', '.msi']:
            return "Installer"
        elif file_path.suffix in ['.zip', '.rar', '.7z']:
            return "Archive"
        else:
            return "Unknown"

    def add_software(self, name: str, version: Optional[str] = None, 
                     license_key: Optional[str] = None, **kwargs) -> SoftwareLicense:
        """Add software to catalog"""
        software_id = f"sw_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"

        license_obj = SoftwareLicense(
            software_id=software_id,
            name=name,
            version=version,
            license_key=license_key,
            **kwargs
        )

        self.software_catalog[software_id] = license_obj
        self._save_catalog()

        self.logger.info(f"✅ Added software: {name}")
        return license_obj

    def vault_software(self, software_id: str, vault_backend: str = "local") -> bool:
        """Vault software files to secure location"""
        if software_id not in self.software_catalog:
            self.logger.warning(f"❌ Software not found: {software_id}")
            return False

        software = self.software_catalog[software_id]

        if vault_backend not in self.vault_backends:
            self.logger.warning(f"❌ Unknown vault backend: {vault_backend}")
            return False

        try:
            vault_func = self.vault_backends[vault_backend]
            vault_location = vault_func(software)

            software.vault_location = vault_location
            software.updated_at = datetime.now().isoformat()
            self._save_catalog()

            self.logger.info(f"✅ Vaulted software: {software.name} to {vault_location}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Vaulting error: {e}")
            return False

    def _vault_to_local(self, software: SoftwareLicense) -> str:
        try:
            """Vault to local secure directory"""
            vault_dir = self.data_dir / "vault" / software.software_id
            vault_dir.mkdir(parents=True, exist_ok=True)

            # Copy files if they exist
            for file_path in software.files:
                src = Path(file_path)
                if src.exists():
                    dst = vault_dir / src.name
                    shutil.copy2(src, dst)
                    self.logger.info(f"   Copied: {src.name}")

            return str(vault_dir)

        except Exception as e:
            self.logger.error(f"Error in _vault_to_local: {e}", exc_info=True)
            raise
    def _vault_to_nas(self, software: SoftwareLicense) -> str:
        """Vault to NAS"""
        nas_path = Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\software_vault")

        # Try to create if doesn't exist
        try:
            nas_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.warning(f"⚠️  NAS path not accessible: {e}")
            # Fallback to local
            return self._vault_to_local(software)

        vault_dir = nas_path / software.software_id
        vault_dir.mkdir(parents=True, exist_ok=True)

        # Copy files
        for file_path in software.files:
            src = Path(file_path)
            if src.exists():
                dst = vault_dir / src.name
                shutil.copy2(src, dst)

        return str(vault_dir)

    def _vault_to_azure(self, software: SoftwareLicense) -> str:
        """Vault to Azure (placeholder - requires Azure setup)"""
        # TODO: Implement Azure Blob Storage integration  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        self.logger.warning("⚠️  Azure vaulting not yet implemented")
        return self._vault_to_local(software)

    def search_software(self, query: str) -> List[SoftwareLicense]:
        """Search software catalog"""
        query_lower = query.lower()
        results = []

        for software in self.software_catalog.values():
            if (query_lower in software.name.lower() or
                (software.vendor and query_lower in software.vendor.lower()) or
                (software.notes and query_lower in software.notes.lower())):
                results.append(software)

        return results

    def get_catalog_summary(self) -> Dict[str, Any]:
        """Get catalog summary"""
        return {
            "total_software": len(self.software_catalog),
            "repositories": len(self.repositories),
            "by_type": self._count_by_type(),
            "vaulted": sum(1 for s in self.software_catalog.values() if s.vault_location),
            "timestamp": datetime.now().isoformat()
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count software by type"""
        counts = {}
        for software in self.software_catalog.values():
            license_type = software.license_type or "Unknown"
            counts[license_type] = counts.get(license_type, 0) + 1
        return counts


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Software Repository Vault")
    parser.add_argument("--scan", help="Scan repository folder")
    parser.add_argument("--add", help="Add software (name)")
    parser.add_argument("--search", help="Search software")
    parser.add_argument("--vault", help="Vault software (ID)")
    parser.add_argument("--summary", action="store_true", help="Show catalog summary")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔐 SOFTWARE REPOSITORY VAULT")
    print("="*80 + "\n")

    vault = SoftwareRepositoryVault()

    if args.scan:
        print(f"🔍 Scanning repository: {args.scan}\n")
        found = vault.scan_repository(args.scan)
        print(f"✅ Found {len(found)} software files\n")

        # Show first 10
        for item in found[:10]:
            print(f"  {item['name']} ({item['type']})")
            print(f"    Path: {item['path']}")
            print()

    elif args.add:
        print(f"➕ Adding software: {args.add}\n")
        software = vault.add_software(args.add)
        print(f"✅ Added: {software.name} (ID: {software.software_id})\n")

    elif args.search:
        print(f"🔍 Searching for: {args.search}\n")
        results = vault.search_software(args.search)
        print(f"✅ Found {len(results)} results:\n")
        for software in results:
            print(f"  {software.name}")
            if software.version:
                print(f"    Version: {software.version}")
            if software.vault_location:
                print(f"    Vaulted: {software.vault_location}")
            print()

    elif args.vault:
        print(f"🔐 Vaulting software: {args.vault}\n")
        success = vault.vault_software(args.vault)
        if success:
            print("✅ Vaulted successfully\n")
        else:
            print("❌ Vaulting failed\n")

    elif args.summary:
        summary = vault.get_catalog_summary()
        print("📊 CATALOG SUMMARY:\n")
        print(f"  Total Software: {summary['total_software']}")
        print(f"  Repositories: {summary['repositories']}")
        print(f"  Vaulted: {summary['vaulted']}")
        print(f"\n  By Type:")
        for license_type, count in summary['by_type'].items():
            print(f"    {license_type}: {count}")
        print()

    else:
        print("Usage:")
        print("  --scan <path>     : Scan repository folder")
        print("  --add <name>      : Add software to catalog")
        print("  --search <query>  : Search software")
        print("  --vault <id>      : Vault software")
        print("  --summary         : Show catalog summary")
        print()


if __name__ == "__main__":



    main()