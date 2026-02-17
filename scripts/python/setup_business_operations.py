#!/usr/bin/env python3
"""
Setup Business Operations - Initialize essential business systems
Creates directory structure, templates, and initial configurations
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

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

logger = get_logger("SetupBusinessOperations")


def create_directory_structure():
    """Create essential business directories"""
    directories = [
        "data/clients",
        "data/invoices",
        "data/proposals",
        "data/projects",
        "data/contracts",
        "data/financial",
        "data/legal",
        "templates",
        "docs/business",
        "docs/sops",
        "scripts/business"
    ]

    created = []
    for dir_path in directories:
        full_path = script_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        created.append(str(full_path))
        logger.info(f"✅ Created: {dir_path}")

    return created


def create_business_config():
    try:
        """Create initial business configuration file"""
        config = {
            "business": {
                "name": "[COMPANY_NAME]",
                "legal_name": "[LEGAL_NAME]",
                "ein": "[REDACTED - Stored in Azure Vault]",
                "entity_type": "[LLC/CORP/etc]",
                "founded_date": "[DATE]",
                "address": {
                    "street": "[REDACTED - Stored in Azure Vault]",
                    "city": "[CITY]",
                    "state": "[STATE]",
                    "zip": "[ZIP]"
                },
                "contact": {
                    "phone": "[REDACTED - Stored in Azure Vault]",
                    "email": "[REDACTED - Stored in Azure Vault]",
                    "website": "[WEBSITE]"
                }
            },
            "financial": {
                "accounting_software": "[SOFTWARE_NAME]",
                "fiscal_year_end": "[MONTH/DAY]",
                "currency": "USD",
                "tax_id": "[REDACTED - Stored in Azure Vault]"
            },
            "operations": {
                "timezone": "America/New_York",
                "business_hours": {
                    "monday": "9:00 AM - 5:00 PM",
                    "tuesday": "9:00 AM - 5:00 PM",
                    "wednesday": "9:00 AM - 5:00 PM",
                    "thursday": "9:00 AM - 5:00 PM",
                    "friday": "9:00 AM - 5:00 PM",
                    "saturday": "Closed",
                    "sunday": "Closed"
                }
            },
            "security": {
                "credential_storage": "Azure Key Vault",
                "vault_url": "[REDACTED - Stored in Azure Vault]",
                "redaction_policy": "enforced"
            },
            "created": datetime.now().isoformat(),
            "note": "All sensitive information stored in Azure Key Vault. See SECURITY_REDACTION_POLICY.md"
        }

        config_file = script_dir / "config" / "business.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Created business config: {config_file}")
        return config_file


    except Exception as e:
        logger.error(f"Error in create_business_config: {e}", exc_info=True)
        raise
def create_client_database_template():
    try:
        """Create client database template"""
        template = {
            "clients": [],
            "schema": {
                "client_id": "Unique identifier",
                "name": "Client name",
                "contact_person": "[REDACTED - Stored in Azure Vault]",
                "email": "[REDACTED - Stored in Azure Vault]",
                "phone": "[REDACTED - Stored in Azure Vault]",
                "address": "[REDACTED - Stored in Azure Vault]",
                "status": "active/inactive/prospect",
                "created_date": "ISO date",
                "notes": "Additional information"
            },
            "note": "Sensitive client information should be stored in Azure Key Vault with client-specific secret names"
        }

        db_file = script_dir / "data" / "clients" / "clients_database.json"
        db_file.parent.mkdir(parents=True, exist_ok=True)

        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Created client database template: {db_file}")
        return db_file


    except Exception as e:
        logger.error(f"Error in create_client_database_template: {e}", exc_info=True)
        raise
def create_task_management_structure():
    try:
        """Create task management structure"""
        tasks = {
            "projects": [],
            "tasks": [],
            "categories": [
                "Legal",
                "Financial",
                "Operations",
                "Marketing",
                "Sales",
                "Development",
                "Support",
                "Administrative"
            ],
            "priorities": ["Critical", "High", "Medium", "Low"],
            "statuses": ["Not Started", "In Progress", "Blocked", "Completed", "Cancelled"],
            "created": datetime.now().isoformat()
        }

        tasks_file = script_dir / "data" / "tasks.json"

        with open(tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Created task management structure: {tasks_file}")
        return tasks_file


    except Exception as e:
        logger.error(f"Error in create_task_management_structure: {e}", exc_info=True)
        raise
def main():
    """Setup business operations"""
    print("=" * 80)
    print("🚀 Business Operations Setup")
    print("=" * 80)
    print()

    print("📁 Creating directory structure...")
    directories = create_directory_structure()
    print(f"   ✅ Created {len(directories)} directories")
    print()

    print("⚙️  Creating business configuration...")
    config_file = create_business_config()
    print(f"   ✅ Configuration template created")
    print(f"   📝 Edit: {config_file}")
    print()

    print("👥 Creating client database template...")
    db_file = create_client_database_template()
    print(f"   ✅ Client database template created")
    print()

    print("✅ Creating task management structure...")
    tasks_file = create_task_management_structure()
    print(f"   ✅ Task management structure created")
    print()

    print("=" * 80)
    print("✅ Business Operations Setup Complete!")
    print("=" * 80)
    print()
    print("📋 Next Steps:")
    print("   1. Edit config/business.json with your company information")
    print("   2. Store sensitive info (EIN, addresses, etc.) in Azure Vault")
    print("   3. Use templates/ for invoices, proposals, and SOPs")
    print("   4. Start adding clients to data/clients/clients_database.json")
    print("   5. Use data/tasks.json for task management")
    print()
    print("📚 Templates Available:")
    print("   - templates/invoice_template.html")
    print("   - templates/proposal_template.md")
    print("   - templates/sop_template.md")
    print("   - templates/client_onboarding_checklist.md")
    print()


if __name__ == "__main__":


    main()