#!/usr/bin/env python3
"""
JARVIS Virtual Employee Manager

Manages job slots and virtual employees for the company.
Allows adding, updating, deleting, and querying virtual employees.

Features:
- Job slot management
- Virtual employee tracking
- Role and responsibility management
- Integration status tracking
- Performance metrics

Tags: #DATABASE[@DB] @TEAM
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISVirtualEmployee")


class EmployeeStatus(Enum):
    """Employee status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ONBOARDING = "onboarding"
    ARCHIVED = "archived"


class EmployeeRole(Enum):
    """Employee roles"""
    ENGINEER = "engineer"
    ADMINISTRATOR = "administrator"
    ANALYST = "analyst"
    MANAGER = "manager"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    CONSULTANT = "consultant"


class VirtualEmployeeManager:
    """
    Virtual Employee Manager

    Manages job slots and virtual employees for the company.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Database path (use enhanced memory database)
        self.db_path = project_root / "data" / "jarvis_memory" / "enhanced_memory.db"

        # Initialize employee table
        self._init_employee_table()

        self.logger.info("✅ Virtual Employee Manager initialized")

    def _init_employee_table(self):
        """Initialize virtual_employees table in enhanced database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Create virtual_employees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS virtual_employees (
                    employee_id TEXT PRIMARY KEY,
                    employee_name TEXT NOT NULL,
                    job_slot TEXT NOT NULL,
                    role TEXT NOT NULL,
                    department TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    description TEXT,
                    responsibilities TEXT,
                    skills TEXT,
                    integration_status REAL DEFAULT 0.0,
                    performance_score REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_active TEXT,
                    metadata TEXT
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_name ON virtual_employees(employee_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_job_slot ON virtual_employees(job_slot)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_role ON virtual_employees(role)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON virtual_employees(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_department ON virtual_employees(department)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_integration_status ON virtual_employees(integration_status)')

            conn.commit()
            conn.close()

            self.logger.info("✅ Virtual employees table initialized")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize employee table: {e}", exc_info=True)
            raise

    def add_employee(self, employee_name: str, job_slot: str, role: str,
                    department: Optional[str] = None,
                    description: Optional[str] = None,
                    responsibilities: Optional[List[str]] = None,
                    skills: Optional[List[str]] = None,
                    status: str = "active",
                    metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a new virtual employee

        Args:
            employee_name: Name of the employee (e.g., "@DBE", "Windows Systems Engineer")
            job_slot: Job slot identifier (e.g., "database_engineer", "systems_engineer")
            role: Employee role (engineer, administrator, analyst, etc.)
            department: Department (optional)
            description: Employee description
            responsibilities: List of responsibilities
            skills: List of skills
            status: Employee status (active, inactive, onboarding, archived)
            metadata: Additional metadata
        """
        self.logger.info(f"➕ Adding virtual employee: {employee_name} ({job_slot})")

        # Generate employee ID
        employee_id = f"emp_{job_slot.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO virtual_employees
                (employee_id, employee_name, job_slot, role, department, status, description,
                 responsibilities, skills, created_at, updated_at, last_active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                employee_id,
                employee_name,
                job_slot,
                role,
                department,
                status,
                description,
                json.dumps(responsibilities or []),
                json.dumps(skills or []),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(metadata or {})
            ))

            conn.commit()
            conn.close()

            self.logger.info(f"✅ Added virtual employee: {employee_name} (ID: {employee_id})")

            return {
                "success": True,
                "employee_id": employee_id,
                "employee_name": employee_name,
                "job_slot": job_slot
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to add employee: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def update_employee(self, employee_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing virtual employee"""
        self.logger.info(f"🔄 Updating virtual employee: {employee_id}")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Build update query
            update_fields = []
            update_values = []

            allowed_fields = [
                "employee_name", "job_slot", "role", "department", "status",
                "description", "responsibilities", "skills", "integration_status",
                "performance_score", "metadata"
            ]

            for field, value in updates.items():
                if field in allowed_fields:
                    if field in ["responsibilities", "skills", "metadata"]:
                        value = json.dumps(value) if value else None
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)

            if not update_fields:
                return {"success": False, "error": "No valid fields to update"}

            # Add updated_at
            update_fields.append("updated_at = ?")
            update_values.append(datetime.now().isoformat())

            # Add employee_id for WHERE clause
            update_values.append(employee_id)

            sql = f"UPDATE virtual_employees SET {', '.join(update_fields)} WHERE employee_id = ?"
            cursor.execute(sql, update_values)

            conn.commit()
            conn.close()

            self.logger.info(f"✅ Updated virtual employee: {employee_id}")

            return {
                "success": True,
                "employee_id": employee_id,
                "fields_updated": len(update_fields) - 1  # Exclude updated_at
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to update employee: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def delete_employee(self, employee_id: str, archive: bool = True) -> Dict[str, Any]:
        """Delete (or archive) a virtual employee"""
        if archive:
            # Archive instead of delete
            return self.update_employee(employee_id, {"status": "archived"})
        else:
            # Actually delete
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()

                cursor.execute("DELETE FROM virtual_employees WHERE employee_id = ?", (employee_id,))

                conn.commit()
                conn.close()

                self.logger.info(f"✅ Deleted virtual employee: {employee_id}")

                return {
                    "success": True,
                    "employee_id": employee_id
                }

            except Exception as e:
                self.logger.error(f"❌ Failed to delete employee: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e)
                }

    def get_all_employees(self, status: Optional[str] = None, 
                         department: Optional[str] = None,
                         role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all virtual employees

        Args:
            status: Filter by status (active, inactive, etc.)
            department: Filter by department
            role: Filter by role
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build query
            conditions = []
            params = []

            if status:
                conditions.append("status = ?")
                params.append(status)

            if department:
                conditions.append("department = ?")
                params.append(department)

            if role:
                conditions.append("role = ?")
                params.append(role)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            cursor.execute(f'''
                SELECT * FROM virtual_employees
                WHERE {where_clause}
                ORDER BY employee_name ASC
            ''', params)

            rows = cursor.fetchall()
            employees = []

            for row in rows:
                emp = dict(row)
                # Parse JSON fields
                if emp.get("responsibilities"):
                    try:
                        emp["responsibilities"] = json.loads(emp["responsibilities"])
                    except:
                        pass
                if emp.get("skills"):
                    try:
                        emp["skills"] = json.loads(emp["skills"])
                    except:
                        pass
                if emp.get("metadata"):
                    try:
                        emp["metadata"] = json.loads(emp["metadata"])
                    except:
                        pass
                employees.append(emp)

            conn.close()

            return employees

        except Exception as e:
            self.logger.error(f"❌ Failed to get employees: {e}", exc_info=True)
            return []

    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific virtual employee"""
        employees = self.get_all_employees()
        for emp in employees:
            if emp.get("employee_id") == employee_id:
                return emp
        return None

    def get_employees_by_job_slot(self, job_slot: str) -> List[Dict[str, Any]]:
        """Get all employees with a specific job slot"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM virtual_employees
                WHERE job_slot = ?
                ORDER BY employee_name ASC
            ''', (job_slot,))

            rows = cursor.fetchall()
            employees = [dict(row) for row in rows]

            conn.close()

            return employees

        except Exception as e:
            self.logger.error(f"❌ Failed to get employees by job slot: {e}", exc_info=True)
            return []

    def get_company_roster(self) -> Dict[str, Any]:
        """Get complete company roster with statistics"""
        all_employees = self.get_all_employees()

        # Statistics
        stats = {
            "total_employees": len(all_employees),
            "by_status": {},
            "by_role": {},
            "by_department": {},
            "active_employees": len([e for e in all_employees if e.get("status") == "active"]),
            "average_integration": 0.0,
            "average_performance": 0.0
        }

        # Count by status
        for emp in all_employees:
            status = emp.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # Count by role
        for emp in all_employees:
            role = emp.get("role", "unknown")
            stats["by_role"][role] = stats["by_role"].get(role, 0) + 1

        # Count by department
        for emp in all_employees:
            dept = emp.get("department") or "unassigned"
            stats["by_department"][dept] = stats["by_department"].get(dept, 0) + 1

        # Calculate averages
        if all_employees:
            integration_scores = [e.get("integration_status", 0.0) for e in all_employees if e.get("integration_status")]
            performance_scores = [e.get("performance_score", 0.0) for e in all_employees if e.get("performance_score")]

            if integration_scores:
                stats["average_integration"] = sum(integration_scores) / len(integration_scores)
            if performance_scores:
                stats["average_performance"] = sum(performance_scores) / len(performance_scores)

        return {
            "timestamp": datetime.now().isoformat(),
            "employees": all_employees,
            "statistics": stats
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Virtual Employee Manager")
        parser.add_argument("--add", nargs=3, metavar=("NAME", "JOB_SLOT", "ROLE"), help="Add employee")
        parser.add_argument("--list", action="store_true", help="List all employees")
        parser.add_argument("--roster", action="store_true", help="Get company roster")
        parser.add_argument("--get", type=str, help="Get specific employee by ID")
        parser.add_argument("--job-slot", type=str, help="Get employees by job slot")
        parser.add_argument("--update", type=str, help="Update employee (provide JSON)")
        parser.add_argument("--delete", type=str, help="Delete employee by ID")
        parser.add_argument("--status", type=str, help="Filter by status")
        parser.add_argument("--department", type=str, help="Filter by department")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = VirtualEmployeeManager(project_root)

        if args.add:
            name, job_slot, role = args.add
            result = manager.add_employee(name, job_slot, role)
            import json
            print(json.dumps(result, indent=2))

        elif args.list:
            employees = manager.get_all_employees(
                status=args.status,
                department=args.department
            )
            print(f"\n📋 Virtual Employees ({len(employees)} total):")
            print("="*80)
            for emp in employees:
                status_icon = "✅" if emp.get("status") == "active" else "⏸️" if emp.get("status") == "inactive" else "📦"
                print(f"{status_icon} {emp.get('employee_name')} ({emp.get('job_slot')})")
                print(f"   Role: {emp.get('role')}, Department: {emp.get('department') or 'N/A'}")
                print(f"   Integration: {emp.get('integration_status', 0.0)*100:.1f}%")
                print()

        elif args.roster:
            roster = manager.get_company_roster()
            stats = roster["statistics"]
            print("\n" + "="*80)
            print("COMPANY ROSTER")
            print("="*80)
            print(f"Total Employees: {stats['total_employees']}")
            print(f"Active Employees: {stats['active_employees']}")
            print(f"Average Integration: {stats['average_integration']*100:.1f}%")
            print(f"Average Performance: {stats['average_performance']*100:.1f}%")
            print("\nBy Status:")
            for status, count in stats['by_status'].items():
                print(f"   {status}: {count}")
            print("\nBy Role:")
            for role, count in stats['by_role'].items():
                print(f"   {role}: {count}")
            print("\nBy Department:")
            for dept, count in stats['by_department'].items():
                print(f"   {dept}: {count}")
            print("\nEmployees:")
            for emp in roster["employees"]:
                print(f"   - {emp.get('employee_name')} ({emp.get('job_slot')}) - {emp.get('status')}")

        elif args.get:
            employee = manager.get_employee(args.get)
            if employee:
                import json
                print(json.dumps(employee, indent=2, default=str))
            else:
                print(f"❌ Employee not found: {args.get}")

        elif args.job_slot:
            employees = manager.get_employees_by_job_slot(args.job_slot)
            print(f"\nEmployees with job slot '{args.job_slot}': {len(employees)}")
            for emp in employees:
                print(f"   - {emp.get('employee_name')} ({emp.get('employee_id')})")

        elif args.update:
            import json
            updates = json.loads(args.update)
            employee_id = updates.pop("employee_id")
            result = manager.update_employee(employee_id, updates)
            print(json.dumps(result, indent=2))

        elif args.delete:
            result = manager.delete_employee(args.delete, archive=True)
            import json
            print(json.dumps(result, indent=2))

        else:
            print("Usage:")
            print("  --add NAME JOB_SLOT ROLE     : Add new employee")
            print("  --list                      : List all employees")
            print("  --roster                    : Get company roster")
            print("  --get <employee_id>         : Get specific employee")
            print("  --job-slot <slot>           : Get employees by job slot")
            print("  --update <json>              : Update employee")
            print("  --delete <employee_id>       : Delete/archive employee")
            print("  --status <status>            : Filter by status")
            print("  --department <dept>          : Filter by department")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()