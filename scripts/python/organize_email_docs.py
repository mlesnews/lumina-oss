#!/usr/bin/env python3
"""
Organize and Cleanup Email Documentation
Consolidates all email-related documentation into organized structure
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

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

logger = get_logger("OrganizeEmailDocs")


def find_email_files() -> Dict[str, List[Path]]:
    try:
        """Find all email-related files"""

        email_files = {
            "setup": [],
            "configuration": [],
            "integration": [],
            "system": [],
            "outlook": [],
            "protonmail": [],
            "gmail": [],
            "other": []
        }

        # Search patterns
        patterns = {
            "setup": ["*SETUP*", "*setup*", "*SETUP_INSTRUCTIONS*", "*CONFIGURATION*"],
            "configuration": ["*CONFIG*", "*CONFIGURATION*", "*CREDENTIAL*"],
            "integration": ["*INTEGRATION*", "*SYPHON*", "*N8N*"],
            "system": ["*SYSTEM*", "*STATUS*", "*COMPLETE*"],
            "outlook": ["*OUTLOOK*", "*outlook*"],
            "protonmail": ["*PROTON*", "*PROTONBRIDGE*", "*PROTON_*"],
            "gmail": ["*GMAIL*", "*GMAIL_*"],
        }

        # Search in key directories
        search_dirs = [
            script_dir / "docs" / "email",
            script_dir / "docs" / "system",
            script_dir / "config" / "outlook",
            script_dir,
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for pattern_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    for file_path in search_dir.rglob(f"{pattern}.md"):
                        if "email" in file_path.name.lower() or "EMAIL" in file_path.name:
                            if pattern_type in email_files:
                                email_files[pattern_type].append(file_path)
                            else:
                                email_files["other"].append(file_path)

        # Also check root level email files
        root_email = script_dir.glob("*email*.md")
        for file_path in root_email:
            email_files["other"].append(file_path)

        # Remove duplicates
        for key in email_files:
            email_files[key] = list(set(email_files[key]))

        return email_files


    except Exception as e:
        logger.error(f"Error in find_email_files: {e}", exc_info=True)
        raise
def organize_email_docs(email_files: Dict[str, List[Path]]):
    try:
        """Organize email documentation into structured directories"""

        email_docs_dir = script_dir / "docs" / "email"
        email_docs_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        subdirs = {
            "setup": email_docs_dir / "setup",
            "configuration": email_docs_dir / "configuration",
            "integration": email_docs_dir / "integration",
            "outlook": email_docs_dir / "outlook",
            "protonmail": email_docs_dir / "protonmail",
            "gmail": email_docs_dir / "gmail",
            "system": email_docs_dir / "system",
            "archive": email_docs_dir / "archive"
        }

        for subdir in subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)

        organized = []
        archived = []

        # Organize files
        for category, files in email_files.items():
            if not files:
                continue

            target_dir = subdirs.get(category, subdirs["archive"])

            for file_path in files:
                if not file_path.exists():
                    continue

                # Skip if already in target location
                if file_path.parent == target_dir:
                    continue

                # Create new filename with timestamp if duplicate
                new_name = file_path.name
                target_path = target_dir / new_name

                if target_path.exists() and file_path != target_path:
                    # Archive the older one
                    archive_path = subdirs["archive"] / f"{datetime.now().strftime('%Y%m%d')}_{new_name}"
                    if file_path.stat().st_mtime < target_path.stat().st_mtime:
                        # Current file is older, archive it
                        shutil.move(str(file_path), str(archive_path))
                        archived.append(str(archive_path))
                        logger.info(f"📦 Archived (older): {file_path.name}")
                    else:
                        # Current file is newer, replace target and archive old target
                        old_target = subdirs["archive"] / f"{datetime.now().strftime('%Y%m%d')}_{target_path.name}"
                        shutil.move(str(target_path), str(old_target))
                        archived.append(str(old_target))
                        shutil.copy2(str(file_path), str(target_path))
                        organized.append(str(target_path))
                        logger.info(f"✅ Organized (replaced): {file_path.name}")
                else:
                    # No conflict, just move/copy
                    if file_path.parent.parent == email_docs_dir:
                        # Already in email docs, just ensure it's in right subdir
                        if file_path.parent != target_dir:
                            shutil.move(str(file_path), str(target_path))
                            organized.append(str(target_path))
                    else:
                        # Copy to preserve original location if needed
                        shutil.copy2(str(file_path), str(target_path))
                        organized.append(str(target_path))
                        logger.info(f"✅ Organized: {file_path.name}")

        return organized, archived, subdirs


    except Exception as e:
        logger.error(f"Error in organize_email_docs: {e}", exc_info=True)
        raise
def create_email_index(subdirs: Dict[str, Path], email_files: Dict[str, List[Path]]):
    """Create master index for email documentation"""

    index_content = """# Email Documentation Index

## 📚 Quick Reference

### Setup Guides
- **[Gmail Setup](gmail/GMAIL_MAILSTATION_SETUP.md)** - Gmail with MailStation
- **[Gmail Outlook NAS](gmail/GMAIL_OUTLOOK_NAS_SETUP.md)** - Gmail, Outlook, NAS integration
- **[ProtonMail Bridge](protonmail/)** - ProtonMail Bridge setup
- **[Outlook Configuration](outlook/)** - Outlook setup guides

### Configuration
- **[Credential Storage](configuration/CREDENTIAL_STORAGE_INSTRUCTIONS.md)** - How to store credentials
- **[Credential Names](configuration/CREDENTIAL_NAMES_REFERENCE.md)** - Azure Vault secret names
- **[IMAP Setup](configuration/IMAP_PORT_993_SETUP.md)** - IMAP configuration

### Integration
- **[Email SYPHON](integration/)** - SYPHON email integration
- **[N8N Integration](integration/)** - N8N email workflows
- **[System Integration](system/)** - System-level email integration

## 📁 Documentation Structure

### `/docs/email/setup/`
- Email service setup guides
- Initial configuration instructions

### `/docs/email/configuration/`
- Credential management
- Configuration details
- Port and protocol settings

### `/docs/email/integration/`
- SYPHON integration
- N8N workflows
- System integrations

### `/docs/email/outlook/`
- Outlook-specific setup
- Outlook configuration guides

### `/docs/email/protonmail/`
- ProtonMail Bridge setup
- ProtonMail configuration

### `/docs/email/gmail/`
- Gmail setup guides
- Gmail integration

### `/docs/email/system/`
- System-level email documentation
- Status and completion reports

### `/docs/email/archive/`
- Archived/duplicate files
- Historical versions

## 🎯 Quick Actions

### Setup Tasks
1. Gmail Setup → [Gmail Guides](gmail/)
2. ProtonMail Setup → [ProtonMail Guides](protonmail/)
3. Outlook Setup → [Outlook Guides](outlook/)

### Configuration
1. Store Credentials → [Credential Storage](configuration/CREDENTIAL_STORAGE_INSTRUCTIONS.md)
2. Check Secret Names → [Credential Names](configuration/CREDENTIAL_NAMES_REFERENCE.md)

### Integration
1. SYPHON Setup → [Integration Guides](integration/)
2. N8N Workflows → [Integration Guides](integration/)

---

**Last Updated:** [TIMESTAMP]
"""

    index_file = script_dir / "docs" / "email" / "INDEX.md"
    index_file.parent.mkdir(parents=True, exist_ok=True)

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content.replace("[TIMESTAMP]", datetime.now().isoformat()))

    logger.info(f"✅ Created email index: {index_file}")
    return index_file


def create_cleanup_report(organized: List[str], archived: List[str], email_files: Dict[str, List[Path]]):
    """Create cleanup report"""

    report_content = f"""# Email Documentation Organization Report

**Date:** {datetime.now().isoformat()}

## ✅ Actions Completed

### Files Organized
{len(organized)} files organized into structured directories:
- Setup: {len(email_files.get('setup', []))} files
- Configuration: {len(email_files.get('configuration', []))} files
- Integration: {len(email_files.get('integration', []))} files
- Outlook: {len(email_files.get('outlook', []))} files
- ProtonMail: {len(email_files.get('protonmail', []))} files
- Gmail: {len(email_files.get('gmail', []))} files
- System: {len(email_files.get('system', []))} files

### Files Archived
{len(archived)} duplicate/old files archived

## 📁 New Structure

### `/docs/email/`
- **INDEX.md** - Master index (START HERE)
- **setup/** - Setup guides
- **configuration/** - Configuration docs
- **integration/** - Integration guides
- **outlook/** - Outlook-specific
- **protonmail/** - ProtonMail-specific
- **gmail/** - Gmail-specific
- **system/** - System-level docs
- **archive/** - Archived files

## 🎯 Entry Point

**Start Here:** `docs/email/INDEX.md`

---

**Organization Complete!** ✅
"""

    report_file = script_dir / "docs" / "email" / "ORGANIZATION_REPORT.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.info(f"✅ Created cleanup report: {report_file}")
    return report_file


def main():
    """Main organization"""
    print("="*80)
    print("📧 ORGANIZING EMAIL DOCUMENTATION")
    print("="*80)
    print()

    print("📋 Step 1: Finding email files...")
    email_files = find_email_files()
    total_files = sum(len(files) for files in email_files.values())
    print(f"   ✅ Found {total_files} email-related files")
    for category, files in email_files.items():
        if files:
            print(f"      - {category}: {len(files)} files")
    print()

    print("📋 Step 2: Organizing files...")
    organized, archived, subdirs = organize_email_docs(email_files)
    print(f"   ✅ Organized {len(organized)} files")
    print(f"   ✅ Archived {len(archived)} duplicates")
    print()

    print("📋 Step 3: Creating master index...")
    index_file = create_email_index(subdirs, email_files)
    print(f"   ✅ Created: {index_file.relative_to(script_dir)}")
    print()

    print("📋 Step 4: Creating cleanup report...")
    report_file = create_cleanup_report(organized, archived, email_files)
    print(f"   ✅ Created: {report_file.relative_to(script_dir)}")
    print()

    print("="*80)
    print("✅ EMAIL DOCUMENTATION ORGANIZATION COMPLETE")
    print("="*80)
    print()
    print("📁 New Structure:")
    print("   - docs/email/INDEX.md - Master index (START HERE)")
    print("   - docs/email/setup/ - Setup guides")
    print("   - docs/email/configuration/ - Configuration")
    print("   - docs/email/integration/ - Integration guides")
    print("   - docs/email/outlook/ - Outlook setup")
    print("   - docs/email/protonmail/ - ProtonMail setup")
    print("   - docs/email/gmail/ - Gmail setup")
    print("   - docs/email/system/ - System docs")
    print("   - docs/email/archive/ - Archived files")
    print()
    print("📚 Entry Point: docs/email/INDEX.md")
    print()


if __name__ == "__main__":


    main()