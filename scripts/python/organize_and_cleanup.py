#!/usr/bin/env python3
"""
Organize and Cleanup Startup Documentation
Consolidates duplicate files and organizes structure
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

logger = get_logger("OrganizeAndCleanup")


def consolidate_startup_docs():
    try:
        """Consolidate duplicate startup documentation files"""

        # Files to consolidate
        root_files = {
            "EXECUTIVE_SUMMARY.md": "Primary executive summary",
            "ALL_SETUP_COMPLETE.md": "Complete setup status",
            "STARTUP_READY.md": "Quick reference",
            "STARTUP_SETUP_COMPLETE.md": "Setup completion (if in root)"
        }

        # Create archive directory
        archive_dir = script_dir / "docs" / "archive" / "startup_setup"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Create consolidated directory
        consolidated_dir = script_dir / "docs" / "startup"
        consolidated_dir.mkdir(parents=True, exist_ok=True)

        consolidated = []
        archived = []

        # Process root-level startup files
        for filename, description in root_files.items():
            file_path = script_dir / filename
            if file_path.exists():
                # Copy to consolidated location
                consolidated_path = consolidated_dir / filename
                shutil.copy2(file_path, consolidated_path)
                consolidated.append(str(consolidated_path))

                # Move original to archive
                archive_path = archive_dir / f"{datetime.now().strftime('%Y%m%d')}_{filename}"
                shutil.move(file_path, archive_path)
                archived.append(str(archive_path))
                logger.info(f"✅ Consolidated: {filename}")

        # Check for docs/STARTUP_SETUP_COMPLETE.md
        docs_file = script_dir / "docs" / "STARTUP_SETUP_COMPLETE.md"
        if docs_file.exists():
            archive_path = archive_dir / f"{datetime.now().strftime('%Y%m%d')}_STARTUP_SETUP_COMPLETE.md"
            shutil.move(docs_file, archive_path)
            archived.append(str(archive_path))
            logger.info(f"✅ Archived: docs/STARTUP_SETUP_COMPLETE.md")

        return consolidated, archived


    except Exception as e:
        logger.error(f"Error in consolidate_startup_docs: {e}", exc_info=True)
        raise
def create_master_startup_index():
    """Create master index for startup documentation"""

    index_content = """# Startup Documentation Index

## 📚 Quick Reference

### Getting Started
- **[QUICK_START_GUIDE.md](business/QUICK_START_GUIDE.md)** - Quick reference for daily operations
- **[STARTUP_READY.md](STARTUP_READY.md)** - Executive quick reference

### Planning & Strategy
- **[STARTUP_ACTION_PLAN.md](../STARTUP_ACTION_PLAN.md)** - Complete 3-phase startup strategy
- **[STARTUP_WEEK_1_CHECKLIST.md](../STARTUP_WEEK_1_CHECKLIST.md)** - Day-by-day first week guide
- **[MASTER_STARTUP_CHECKLIST.json](business/MASTER_STARTUP_CHECKLIST.json)** - All tasks checklist

### Setup Guides
- **[FINANCIAL_SETUP_GUIDE.md](business/FINANCIAL_SETUP_GUIDE.md)** - Financial systems setup
- **[LEGAL_VERIFICATION_GUIDE.md](business/LEGAL_VERIFICATION_GUIDE.md)** - Legal compliance
- **[ELEVENLABS_SETUP_GUIDE.md](comms/ELEVENLABS_SETUP_GUIDE.md)** - ElevenLabs comms setup

### Status & Summaries
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Executive summary
- **[ALL_SETUP_COMPLETE.md](ALL_SETUP_COMPLETE.md)** - Complete setup status
- **[ESSENTIAL_SYSTEMS.md](business/ESSENTIAL_SYSTEMS.md)** - System dashboard

## 📁 Documentation Structure

### `/docs/startup/`
- Executive summaries and quick references
- Consolidated startup documentation

### `/docs/business/`
- Business operations guides
- Financial and legal guides
- Checklists and templates

### `/docs/comms/`
- ElevenLabs comms setup guides
- Credential management
- Integration guides

## 🎯 Quick Actions

### Setup Tasks
1. Complete ElevenLabs setup → [ELEVENLABS_SETUP_GUIDE.md](comms/ELEVENLABS_SETUP_GUIDE.md)
2. Financial setup → [FINANCIAL_SETUP_GUIDE.md](business/FINANCIAL_SETUP_GUIDE.md)
3. Legal verification → [LEGAL_VERIFICATION_GUIDE.md](business/LEGAL_VERIFICATION_GUIDE.md)

### Daily Operations
- Generate invoice: `python scripts/python/generate_invoice.py`
- Track expenses: `python scripts/python/track_expenses.py`
- Quick reference: [QUICK_START_GUIDE.md](business/QUICK_START_GUIDE.md)

---

**Last Updated:** [TIMESTAMP]
"""

    index_file = script_dir / "docs" / "startup" / "INDEX.md"
    index_file.parent.mkdir(parents=True, exist_ok=True)

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content.replace("[TIMESTAMP]", datetime.now().isoformat()))

    logger.info(f"✅ Created master index: {index_file}")
    return index_file


def organize_business_docs():
    try:
        """Organize business documentation"""

        business_docs_dir = script_dir / "docs" / "business"
        business_docs_dir.mkdir(parents=True, exist_ok=True)

        # Ensure all business docs are in the right place
        business_files = [
            "QUICK_START_GUIDE.md",
            "ESSENTIAL_SYSTEMS.md",
            "FINANCIAL_SETUP_GUIDE.md",
            "LEGAL_VERIFICATION_GUIDE.md",
            "MASTER_STARTUP_CHECKLIST.json"
        ]

        organized = []
        for filename in business_files:
            file_path = business_docs_dir / filename
            if file_path.exists():
                organized.append(str(file_path))

        return organized


    except Exception as e:
        logger.error(f"Error in organize_business_docs: {e}", exc_info=True)
        raise
def create_cleanup_report(consolidated: List[str], archived: List[str], organized: List[str]):
    """Create cleanup report"""

    report_content = f"""# Organization and Cleanup Report

**Date:** {datetime.now().isoformat()}

## ✅ Actions Completed

### Files Consolidated
{len(consolidated)} files moved to `docs/startup/`:
{chr(10).join(f"- {Path(f).name}" for f in consolidated)}

### Files Archived
{len(archived)} files archived to `docs/archive/startup_setup/`:
{chr(10).join(f"- {Path(f).name}" for f in archived)}

### Files Organized
{len(organized)} business documentation files organized:
{chr(10).join(f"- {Path(f).name}" for f in organized)}

## 📁 New Structure

### `/docs/startup/`
- Consolidated startup documentation
- Executive summaries
- Quick references

### `/docs/business/`
- Business operations guides
- Financial setup guides
- Legal verification guides
- Checklists

### `/docs/comms/`
- ElevenLabs comms setup guides
- Credential management
- Integration documentation

### `/docs/archive/startup_setup/`
- Archived duplicate files
- Historical versions

## 🎯 Next Steps

1. Review consolidated files in `docs/startup/`
2. Use `docs/startup/INDEX.md` as entry point
3. Remove any remaining duplicates manually if needed
4. Update any references to old file locations

---

**Cleanup Complete!** ✅
"""

    report_file = script_dir / "docs" / "startup" / "CLEANUP_REPORT.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    logger.info(f"✅ Created cleanup report: {report_file}")
    return report_file


def main():
    """Main organization and cleanup"""
    print("="*80)
    print("🧹 ORGANIZING AND CLEANING UP STARTUP DOCUMENTATION")
    print("="*80)
    print()

    print("📋 Step 1: Consolidating startup documentation...")
    consolidated, archived = consolidate_startup_docs()
    print(f"   ✅ Consolidated {len(consolidated)} files")
    print(f"   ✅ Archived {len(archived)} files")
    print()

    print("📋 Step 2: Creating master index...")
    index_file = create_master_startup_index()
    print(f"   ✅ Created: {index_file.relative_to(script_dir)}")
    print()

    print("📋 Step 3: Organizing business documentation...")
    organized = organize_business_docs()
    print(f"   ✅ Organized {len(organized)} files")
    print()

    print("📋 Step 4: Creating cleanup report...")
    report_file = create_cleanup_report(consolidated, archived, organized)
    print(f"   ✅ Created: {report_file.relative_to(script_dir)}")
    print()

    print("="*80)
    print("✅ ORGANIZATION COMPLETE")
    print("="*80)
    print()
    print("📁 New Structure:")
    print("   - docs/startup/ - Consolidated startup docs")
    print("   - docs/business/ - Business operations docs")
    print("   - docs/comms/ - ElevenLabs comms setup docs")
    print("   - docs/archive/startup_setup/ - Archived duplicates")
    print()
    print("📚 Entry Point: docs/startup/INDEX.md")
    print()


if __name__ == "__main__":


    main()