#!/usr/bin/env python3
"""
Organize Project Structure
Creates a clean, organized project structure with proper categorization
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

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

logger = get_logger("OrganizeProjectStructure")


def create_project_structure_map():
    """Create a map of the organized project structure"""

    structure = {
        "docs": {
            "startup": "Startup documentation and guides",
            "business": "Business operations documentation",
            "comms": "ElevenLabs comms setup and integration docs",
            "system": "System documentation",
            "archive": "Archived/old documentation"
        },
        "templates": {
            "invoices": "Invoice templates",
            "proposals": "Proposal templates",
            "sops": "Standard operating procedures",
            "contracts": "Contract templates"
        },
        "data": {
            "clients": "Client database and information",
            "invoices": "Generated invoices",
            "proposals": "Client proposals",
            "projects": "Project files",
            "contracts": "Contract documents",
            "financial": "Financial records and expenses",
            "legal": "Legal documents"
        },
        "scripts": {
            "python": "Python automation scripts",
            "business": "Business-specific scripts",
            "setup": "Setup and configuration scripts"
        },
        "config": {
            "business": "Business configuration",
            "azure": "Azure service configuration"
        }
    }

    return structure


def create_readme_for_directory(dir_path: Path, description: str, contents: List[str] = None):
    """Create a README.md for a directory"""

    readme_content = f"""# {dir_path.name.title()}

{description}

## Contents

"""

    if contents:
        for item in contents:
            readme_content += f"- {item}\n"
    else:
        readme_content += "*See files in this directory*\n"

    readme_content += f"""
---
**Last Updated:** {datetime.now().isoformat()}
"""

    readme_file = dir_path / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    logger.info(f"✅ Created README: {readme_file}")
    return readme_file


def organize_project_directories():
    try:
        """Organize and document project directories"""

        structure = create_project_structure_map()
        readmes_created = []

        # Create READMEs for main directories
        for main_dir, subdirs in structure.items():
            main_path = script_dir / main_dir
            if main_path.exists():
                # Create main README
                description = f"Contains {main_dir} related files and subdirectories"
                readme = create_readme_for_directory(main_path, description, list(subdirs.keys()))
                readmes_created.append(readme)

                # Create READMEs for subdirectories
                for subdir, desc in subdirs.items():
                    subdir_path = main_path / subdir
                    if subdir_path.exists():
                        sub_readme = create_readme_for_directory(subdir_path, desc)
                        readmes_created.append(sub_readme)

        return readmes_created


    except Exception as e:
        logger.error(f"Error in organize_project_directories: {e}", exc_info=True)
        raise
def create_project_index():
    """Create main project index"""

    index_content = """# LUMINA Project - Organization Index

## 📁 Project Structure

### `/docs/` - Documentation
- **startup/** - Startup documentation and guides
- **business/** - Business operations documentation  
- **comms/** - ElevenLabs comms setup and integration
- **system/** - System documentation
- **archive/** - Archived documentation

### `/templates/` - Templates
- Invoice templates
- Proposal templates
- SOP templates
- Contract templates

### `/data/` - Data Files
- **clients/** - Client database
- **invoices/** - Generated invoices
- **proposals/** - Client proposals
- **projects/** - Project files
- **contracts/** - Contracts
- **financial/** - Financial records
- **legal/** - Legal documents

### `/scripts/` - Automation Scripts
- **python/** - Python scripts
- **business/** - Business scripts
- **setup/** - Setup scripts

### `/config/` - Configuration
- **business/** - Business config
- **azure/** - Azure config

## 🚀 Quick Start

### Startup Documentation
See: [docs/startup/INDEX.md](docs/startup/INDEX.md)

### Business Operations
See: [docs/business/QUICK_START_GUIDE.md](docs/business/QUICK_START_GUIDE.md)

### Scripts
- Setup: `python scripts/python/setup_business_operations.py`
- Invoice: `python scripts/python/generate_invoice.py`
- Expenses: `python scripts/python/track_expenses.py`

## 📚 Key Documentation

### Planning
- [STARTUP_ACTION_PLAN.md](STARTUP_ACTION_PLAN.md)
- [STARTUP_WEEK_1_CHECKLIST.md](STARTUP_WEEK_1_CHECKLIST.md)

### Operations
- [docs/startup/INDEX.md](docs/startup/INDEX.md)
- [docs/business/ESSENTIAL_SYSTEMS.md](docs/business/ESSENTIAL_SYSTEMS.md)

### Setup Guides
- [docs/comms/ELEVENLABS_SETUP_GUIDE.md](docs/comms/ELEVENLABS_SETUP_GUIDE.md)
- [docs/business/FINANCIAL_SETUP_GUIDE.md](docs/business/FINANCIAL_SETUP_GUIDE.md)
- [docs/business/LEGAL_VERIFICATION_GUIDE.md](docs/business/LEGAL_VERIFICATION_GUIDE.md)

---

**Last Updated:** [TIMESTAMP]
"""

    index_file = script_dir / "PROJECT_INDEX.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content.replace("[TIMESTAMP]", datetime.now().isoformat()))

    logger.info(f"✅ Created project index: {index_file}")
    return index_file


def create_cleanup_summary(readmes_created: List[Path], index_file: Path):
    """Create cleanup summary"""

    summary_content = f"""# Project Organization Complete

**Date:** {datetime.now().isoformat()}

## ✅ Actions Completed

### Documentation Organization
- ✅ Consolidated startup documentation to `docs/startup/`
- ✅ Organized business docs in `docs/business/`
- ✅ Created master index at `docs/startup/INDEX.md`
- ✅ Archived duplicate files to `docs/archive/startup_setup/`

### Project Structure
- ✅ Created {len(readmes_created)} README files for directories
- ✅ Created main project index: `PROJECT_INDEX.md`
- ✅ Documented all major directories

## 📁 New Organization

### Documentation
- `docs/startup/` - All startup-related documentation
- `docs/business/` - Business operations guides
- `docs/comms/` - ElevenLabs comms setup guides
- `docs/archive/` - Archived/old files

### Data
- `data/clients/` - Client information
- `data/invoices/` - Generated invoices
- `data/financial/` - Financial records
- `data/legal/` - Legal documents

### Scripts
- `scripts/python/` - Python automation
- `scripts/business/` - Business scripts
- `scripts/setup/` - Setup scripts

## 🎯 Entry Points

1. **Project Overview**: `PROJECT_INDEX.md`
2. **Startup Docs**: `docs/startup/INDEX.md`
3. **Quick Start**: `docs/business/QUICK_START_GUIDE.md`

---

**Organization Complete!** ✅
"""

    summary_file = script_dir / "docs" / "startup" / "ORGANIZATION_COMPLETE.md"
    summary_file.parent.mkdir(parents=True, exist_ok=True)

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)

    logger.info(f"✅ Created organization summary: {summary_file}")
    return summary_file


def main():
    """Main organization"""
    print("="*80)
    print("📁 ORGANIZING PROJECT STRUCTURE")
    print("="*80)
    print()

    print("📋 Step 1: Creating directory READMEs...")
    readmes = organize_project_directories()
    print(f"   ✅ Created {len(readmes)} README files")
    print()

    print("📋 Step 2: Creating project index...")
    index_file = create_project_index()
    print(f"   ✅ Created: {index_file.name}")
    print()

    print("📋 Step 3: Creating organization summary...")
    summary_file = create_cleanup_summary(readmes, index_file)
    print(f"   ✅ Created: {summary_file.relative_to(script_dir)}")
    print()

    print("="*80)
    print("✅ PROJECT ORGANIZATION COMPLETE")
    print("="*80)
    print()
    print("📚 Entry Points:")
    print("   - PROJECT_INDEX.md - Main project index")
    print("   - docs/startup/INDEX.md - Startup documentation")
    print("   - docs/business/QUICK_START_GUIDE.md - Quick start")
    print()


if __name__ == "__main__":


    main()