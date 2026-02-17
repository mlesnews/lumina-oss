#!/usr/bin/env python3
"""
JARVIS Populate Virtual Employees

Populates the virtual employee database with all known employees
from the project.

Tags: #DATABASE[@DB] @TEAM
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_virtual_employee_manager import VirtualEmployeeManager
    MANAGER_AVAILABLE = True
except ImportError:
    MANAGER_AVAILABLE = False
    print("❌ Virtual Employee Manager not available")


# Known virtual employees from the project
KNOWN_EMPLOYEES = [
    {
        "employee_name": "@DBE",
        "job_slot": "database_engineer",
        "role": "engineer",
        "department": "Database",
        "description": "Database Engineer - Handles database design, optimization, and engineering",
        "responsibilities": [
            "Database design and optimization",
            "Schema management",
            "Performance optimization",
            "Query optimization",
            "Index management",
            "Database migration"
        ],
        "skills": [
            "SQL",
            "Database Design",
            "Performance Tuning",
            "Query Optimization",
            "Index Management"
        ],
        "status": "active",
        "integration_status": 1.0,
        "metadata": {
            "module": "jarvis_dbe_system.py",
            "tags": ["#DATABASE[@DB]", "@TEAM", "@DBE"]
        }
    },
    {
        "employee_name": "@DBA",
        "job_slot": "database_administrator",
        "role": "administrator",
        "department": "Database",
        "description": "Database Administrator - Handles database administration, backup, and recovery",
        "responsibilities": [
            "Database administration",
            "User management",
            "Security and access control",
            "Backup and recovery",
            "Performance monitoring",
            "Capacity planning",
            "Disaster recovery"
        ],
        "skills": [
            "Database Administration",
            "Backup and Recovery",
            "Security",
            "Performance Monitoring",
            "Disaster Recovery"
        ],
        "status": "active",
        "integration_status": 1.0,
        "metadata": {
            "module": "jarvis_dba_system.py",
            "tags": ["#DATABASE[@DB]", "@TEAM", "@DBA"]
        }
    },
    {
        "employee_name": "Windows Systems Engineer",
        "job_slot": "systems_engineer",
        "role": "engineer",
        "department": "Infrastructure",
        "description": "Windows Systems Engineer - Manages PC, OS, and applications as parts of JARVIS's body",
        "responsibilities": [
            "PC hardware management",
            "OS health monitoring",
            "Application health monitoring",
            "System log parsing and tailing",
            "Health baseline management",
            "System maintenance"
        ],
        "skills": [
            "Windows Administration",
            "System Monitoring",
            "Log Analysis",
            "Health Management",
            "System Maintenance"
        ],
        "status": "active",
        "integration_status": 0.1,
        "metadata": {
            "module": "jarvis_windows_systems_engineer.py",
            "tags": ["#TROUBLESHOOTING", "@TEAM"]
        }
    },
    {
        "employee_name": "Systems Disaster Recovery Engineer",
        "job_slot": "disaster_recovery_engineer",
        "role": "engineer",
        "department": "Infrastructure",
        "description": "Systems Disaster Recovery Engineer - Prevents duplicate code, ensures proper data management, applies IT standards",
        "responsibilities": [
            "Prevent duplicate code",
            "Ensure proper data management",
            "Apply IT standards",
            "Code validation",
            "Disaster recovery planning",
            "Rollback management"
        ],
        "skills": [
            "Disaster Recovery",
            "Code Validation",
            "Data Management",
            "IT Standards",
            "Rollback Management"
        ],
        "status": "active",
        "integration_status": 0.1,
        "metadata": {
            "module": "jarvis_systems_disaster_recovery_engineer.py",
            "tags": ["#TROUBLESHOOTING", "@TEAM"]
        }
    },
    {
        "employee_name": "ULTRON Fencing System",
        "job_slot": "cluster_fencing_engineer",
        "role": "engineer",
        "department": "Infrastructure",
        "description": "ULTRON Fencing System - Intelligent cluster node isolation with AIQ and JEDI-COUNCIL",
        "responsibilities": [
            "Cluster node health monitoring",
            "Intelligent fencing decisions",
            "Troubleshooting integration",
            "AIQ decision-making",
            "JEDI-COUNCIL consultation",
            "Automatic recovery"
        ],
        "skills": [
            "Cluster Management",
            "Fencing",
            "Troubleshooting",
            "Decision-Making",
            "AIQ Integration"
        ],
        "status": "active",
        "integration_status": 1.0,
        "metadata": {
            "module": "jarvis_ultron_fencing_system.py",
            "tags": ["#TROUBLESHOOTING", "#DECISIONING", "@AIQ", "#JEDI-COUNCIL"]
        }
    },
    {
        "employee_name": "Local-First LLM Router",
        "job_slot": "llm_router_engineer",
        "role": "engineer",
        "department": "AI Infrastructure",
        "description": "Local-First LLM Router - Enforces local AI resource usage before cloud",
        "responsibilities": [
            "Local AI resource routing",
            "Cloud API blocking",
            "Resource health monitoring",
            "Usage statistics tracking",
            "Local-first enforcement"
        ],
        "skills": [
            "LLM Routing",
            "Resource Management",
            "Local AI",
            "Cloud Management"
        ],
        "status": "active",
        "integration_status": 1.0,
        "metadata": {
            "module": "jarvis_local_first_llm_router.py",
            "tags": ["#AI", "@TEAM"]
        }
    },
    {
        "employee_name": "Enhanced Memory Schema Engineer",
        "job_slot": "memory_schema_engineer",
        "role": "engineer",
        "department": "Database",
        "description": "Enhanced Memory Schema Engineer - Designs and maintains enhanced persistent memory schema",
        "responsibilities": [
            "Schema design",
            "Table optimization",
            "Cell management",
            "Query optimization",
            "Long-term storage"
        ],
        "skills": [
            "Database Design",
            "Schema Management",
            "Query Optimization",
            "Long-Term Storage"
        ],
        "status": "active",
        "integration_status": 1.0,
        "metadata": {
            "module": "jarvis_enhanced_persistent_memory_schema.py",
            "tags": ["#DATABASE[@DB]", "@TEAM"]
        }
    },
    {
        "employee_name": "Systems Storage Engineer",
        "job_slot": "storage_engineer",
        "role": "engineer",
        "department": "Infrastructure",
        "description": "Systems Storage Engineer - Manages system storage, disk space, NAS migration, and storage optimization",
        "responsibilities": [
            "Disk space monitoring and management",
            "NAS migration and network drive mapping",
            "Storage optimization",
            "Data lifecycle management",
            "Storage capacity planning",
            "Docker volume management",
            "Network drive management",
            "Storage health monitoring"
        ],
        "skills": [
            "Storage Management",
            "Disk Space Optimization",
            "NAS Migration",
            "Network Drive Mapping",
            "Capacity Planning",
            "Data Lifecycle Management",
            "Storage Health Monitoring"
        ],
        "status": "active",
        "integration_status": 1.0,
        "metadata": {
            "module": "jarvis_systems_storage_engineer.py",
            "tags": ["#STORAGE", "#SYSTEM-HEALTH", "#NAS-MIGRATION", "@TEAM"]
        }
    },
    {
        "employee_name": "Network Engineer",
        "job_slot": "network_engineer",
        "role": "engineer",
        "department": "Network",
        "description": "Network Engineer - Manages network infrastructure, connectivity, and network drive mappings",
        "responsibilities": [
            "Network infrastructure management",
            "Network drive mapping",
            "NAS connectivity",
            "Network monitoring",
            "Bandwidth optimization",
            "Network troubleshooting",
            "Network security"
        ],
        "skills": [
            "Network Management",
            "Network Drive Mapping",
            "NAS Connectivity",
            "Network Monitoring",
            "Troubleshooting",
            "Network Security"
        ],
        "status": "active",
        "integration_status": 1.0,
        "metadata": {
            "module": "jarvis_network_engineer.py",
            "tags": ["#NETWORK", "#INFRASTRUCTURE", "@TEAM"]
        }
    },
    {
        "employee_name": "Network Administrator",
        "job_slot": "network_administrator",
        "role": "administrator",
        "department": "Network",
        "description": "Network Administrator - Administers network infrastructure, security, and access control",
        "responsibilities": [
            "Network administration",
            "Network security",
            "Access control",
            "Network policies",
            "Network monitoring",
            "Bandwidth management",
            "Network compliance"
        ],
        "skills": [
            "Network Administration",
            "Network Security",
            "Access Control",
            "Policy Management",
            "Network Compliance"
        ],
        "status": "active",
        "integration_status": 0.5,
        "metadata": {
            "module": "jarvis_network_administrator.py",
            "tags": ["#NETWORK", "#SECURITY", "@TEAM"]
        }
    }
]


def populate_employees(project_root: Path) -> Dict[str, Any]:
    """Populate virtual employee database with known employees"""
    if not MANAGER_AVAILABLE:
        return {"error": "Virtual Employee Manager not available"}

    manager = VirtualEmployeeManager(project_root)

    results = {
        "added": [],
        "updated": [],
        "errors": []
    }

    for emp_data in KNOWN_EMPLOYEES:
        try:
            # Check if employee already exists
            existing = manager.get_all_employees()
            existing_ids = [e.get("employee_id") for e in existing]

            # Generate employee ID
            job_slot = emp_data["job_slot"]
            employee_id = f"emp_{job_slot.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"

            # Check if exists by job_slot
            existing_by_slot = [e for e in existing if e.get("job_slot") == job_slot]

            if existing_by_slot:
                # Update existing
                existing_id = existing_by_slot[0].get("employee_id")
                update_data = {k: v for k, v in emp_data.items() if k != "employee_name" and k != "job_slot"}
                result = manager.update_employee(existing_id, update_data)
                if result.get("success"):
                    results["updated"].append(emp_data["employee_name"])
            else:
                # Add new
                result = manager.add_employee(
                    employee_name=emp_data["employee_name"],
                    job_slot=emp_data["job_slot"],
                    role=emp_data["role"],
                    department=emp_data.get("department"),
                    description=emp_data.get("description"),
                    responsibilities=emp_data.get("responsibilities"),
                    skills=emp_data.get("skills"),
                    status=emp_data.get("status", "active"),
                    metadata=emp_data.get("metadata")
                )
                if result.get("success"):
                    results["added"].append(emp_data["employee_name"])
                    # Update integration status if provided
                    if "integration_status" in emp_data:
                        manager.update_employee(result["employee_id"], {
                            "integration_status": emp_data["integration_status"]
                        })
                else:
                    results["errors"].append(f"{emp_data['employee_name']}: {result.get('error')}")
        except Exception as e:
            results["errors"].append(f"{emp_data.get('employee_name', 'Unknown')}: {str(e)}")

    return results


if __name__ == "__main__":
    from datetime import datetime

    project_root = Path(__file__).parent.parent.parent
    results = populate_employees(project_root)

    print("\n" + "="*80)
    print("VIRTUAL EMPLOYEE POPULATION")
    print("="*80)
    print(f"Added: {len(results.get('added', []))}")
    for name in results.get('added', []):
        print(f"   ✅ {name}")

    print(f"\nUpdated: {len(results.get('updated', []))}")
    for name in results.get('updated', []):
        print(f"   🔄 {name}")

    if results.get('errors'):
        print(f"\nErrors: {len(results.get('errors', []))}")
        for error in results.get('errors', []):
            print(f"   ❌ {error}")

    print("="*80)
