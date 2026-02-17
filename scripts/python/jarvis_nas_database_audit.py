#!/usr/bin/env python3
"""
JARVIS NAS Database Audit

Audits database usage on KAIJU NAS and verifies proper integration
with @DBE (Database Engineer) and @DBA (Database Administrator) systems.

Tags: #DATABASE[@DB] @TEAM @DBE @DBA
"""

import sys
import json
import sqlite3
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISNASDatabaseAudit")

try:
    from nas_physics_cache import NASPhysicsCache
    NAS_AVAILABLE = True
except ImportError:
    NAS_AVAILABLE = False
    logger.warning("NAS integration not available")


class NASDatabaseAuditor:
    """
    NAS Database Auditor

    Audits database usage on KAIJU NAS and ensures proper
    integration with @DBE and @DBA systems.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # NAS configuration
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_path = f"\\\\{self.nas_ip}\\backups\\MATT_Backups"

        # Database services to check
        self.database_services = {
            "postgresql": {"port": 5432, "enabled": False},
            "mysql": {"port": 3306, "enabled": False},
            "mariadb": {"port": 3306, "enabled": False},
            "mongodb": {"port": 27017, "enabled": False},
            "sqlite": {"port": None, "enabled": True},  # File-based
            "influxdb": {"port": 8086, "enabled": False},
            "timescaledb": {"port": 5432, "enabled": False}
        }

        # Local database usage
        self.local_databases: List[Dict[str, Any]] = []

        # NAS database usage
        self.nas_databases: List[Dict[str, Any]] = []

        # DBE/DBA integration
        self.dbe_system = None
        self.dba_system = None
        self._init_dbe_dba()

        self.logger.info("✅ NAS Database Auditor initialized")

    def _init_dbe_dba(self):
        """Initialize @DBE and @DBA systems"""
        try:
            from jarvis_dbe_system import JARVISDatabaseEngineer
            self.dbe_system = JARVISDatabaseEngineer(self.project_root)
            self.logger.info("✅ @DBE (Database Engineer) initialized")
        except ImportError:
            self.logger.debug("@DBE system not available")

        try:
            from jarvis_dba_system import JARVISDatabaseAdministrator
            self.dba_system = JARVISDatabaseAdministrator(self.project_root)
            self.logger.info("✅ @DBA (Database Administrator) initialized")
        except ImportError:
            self.logger.debug("@DBA system not available")

    def scan_local_databases(self) -> List[Dict[str, Any]]:
        """Scan for local SQLite databases"""
        self.logger.info("🔍 Scanning for local databases...")

        databases = []

        # Common database locations
        db_locations = [
            self.project_root / "data" / "*.db",
            self.project_root / "data" / "*.sqlite",
            self.project_root / "data" / "*.sqlite3",
            self.project_root / "data" / "jarvis_memory" / "*.db",
            self.project_root / "data" / "workflows" / "*.db"
        ]

        for pattern in db_locations:
            for db_file in self.project_root.glob(str(pattern).replace(str(self.project_root) + "\\", "")):
                try:
                    db_info = self._analyze_sqlite_db(db_file)
                    databases.append(db_info)
                except Exception as e:
                    self.logger.debug(f"Error analyzing {db_file}: {e}")

        self.local_databases = databases
        self.logger.info(f"   Found {len(databases)} local database(s)")

        return databases

    def _analyze_sqlite_db(self, db_path: Path) -> Dict[str, Any]:
        """Analyze a SQLite database"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            # Get database size
            db_size = db_path.stat().st_size if db_path.exists() else 0

            # Get row counts
            table_counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                except Exception:
                    pass

            conn.close()

            return {
                "path": str(db_path),
                "type": "sqlite",
                "tables": tables,
                "table_count": len(tables),
                "size_bytes": db_size,
                "size_mb": db_size / (1024 * 1024),
                "table_row_counts": table_counts,
                "location": "local"
            }
        except Exception as e:
            return {
                "path": str(db_path),
                "type": "sqlite",
                "error": str(e),
                "location": "local"
            }

    def check_nas_database_services(self) -> Dict[str, Any]:
        """Check for database services on NAS"""
        self.logger.info(f"🔍 Checking database services on NAS ({self.nas_ip})...")

        results = {
            "nas_ip": self.nas_ip,
            "services": {},
            "accessible": False
        }

        # Check each database service
        for service_name, config in self.database_services.items():
            if config["port"]:
                try:
                    response = requests.get(
                        f"http://{self.nas_ip}:{config['port']}",
                        timeout=2
                    )
                    results["services"][service_name] = {
                        "port": config["port"],
                        "accessible": True,
                        "status_code": response.status_code
                    }
                except requests.exceptions.ConnectionError:
                    results["services"][service_name] = {
                        "port": config["port"],
                        "accessible": False,
                        "error": "Connection refused"
                    }
                except Exception as e:
                    results["services"][service_name] = {
                        "port": config["port"],
                        "accessible": False,
                        "error": str(e)
                    }
            else:
                # File-based databases (SQLite)
                results["services"][service_name] = {
                    "port": None,
                    "accessible": "file_based",
                    "note": "Check NAS file system"
                }

        # Check NAS file system access (with error handling)
        nas_db_path = Path(self.nas_path) / "databases"
        try:
            accessible = nas_db_path.exists()
            results["nas_file_system"] = {
                "path": str(nas_db_path),
                "accessible": accessible,
                "note": "NAS database directory"
            }
        except (OSError, PermissionError) as e:
            results["nas_file_system"] = {
                "path": str(nas_db_path),
                "accessible": False,
                "error": str(e),
                "note": "NAS database directory access failed - check credentials"
            }

        return results

    def audit_database_usage(self) -> Dict[str, Any]:
        try:
            """Comprehensive database usage audit"""
            self.logger.info("================================================================================")
            self.logger.info("NAS DATABASE AUDIT")
            self.logger.info("================================================================================")

            # Scan local databases
            local_dbs = self.scan_local_databases()

            # Check NAS services
            nas_services = self.check_nas_database_services()

            # Analyze usage patterns
            usage_analysis = self._analyze_usage_patterns(local_dbs)

            # Check DBE/DBA integration
            dbe_dba_status = self._check_dbe_dba_integration()

            # Analyze databases with DBE
            dbe_analysis = {}
            if self.dbe_system:
                for db in local_dbs:
                    db_path = Path(db["path"])
                    analysis = self.dbe_system.analyze_database(db_path)
                    dbe_analysis[db["path"]] = analysis

            # Check database health with DBA
            dba_health = {}
            if self.dba_system:
                for db in local_dbs:
                    db_path = Path(db["path"])
                    health = self.dba_system.monitor_database_health(db_path)
                    dba_health[db["path"]] = health

            audit_report = {
                "timestamp": datetime.now().isoformat(),
                "local_databases": {
                    "count": len(local_dbs),
                    "databases": local_dbs,
                    "total_size_mb": sum(db.get("size_mb", 0) for db in local_dbs),
                    "total_tables": sum(db.get("table_count", 0) for db in local_dbs)
                },
                "nas_services": nas_services,
                "usage_analysis": usage_analysis,
                "dbe_dba_integration": dbe_dba_status,
                "dbe_analysis": dbe_analysis,
                "dba_health": dba_health,
                "recommendations": self._generate_recommendations(local_dbs, nas_services, usage_analysis, dbe_analysis, dba_health)
            }

            return audit_report

        except Exception as e:
            self.logger.error(f"Error in audit_database_usage: {e}", exc_info=True)
            raise
    def _analyze_usage_patterns(self, databases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze database usage patterns"""
        analysis = {
            "databases_on_local": len([db for db in databases if db.get("location") == "local"]),
            "databases_on_nas": len([db for db in databases if db.get("location") == "nas"]),
            "sqlite_databases": len([db for db in databases if db.get("type") == "sqlite"]),
            "largest_database": max(databases, key=lambda x: x.get("size_mb", 0)) if databases else None,
            "most_tables": max(databases, key=lambda x: x.get("table_count", 0)) if databases else None,
            "total_size_mb": sum(db.get("size_mb", 0) for db in databases)
        }

        return analysis

    def _check_dbe_dba_integration(self) -> Dict[str, Any]:
        """Check @DBE and @DBA system integration"""
        status = {
            "dbe_available": self.dbe_system is not None,
            "dba_available": self.dba_system is not None,
            "integration_status": "full" if (self.dbe_system and self.dba_system) else ("partial" if (self.dbe_system or self.dba_system) else "none")
        }

        if status["integration_status"] == "full":
            status["recommendation"] = "✅ @DBE and @DBA systems are properly integrated"
        elif status["integration_status"] == "partial":
            status["recommendation"] = "⚠️  Partial integration - ensure both @DBE and @DBA are available"
        else:
            status["recommendation"] = "❌ @DBE and @DBA systems not available - implement for proper database management"

        return status

    def _generate_recommendations(self, local_dbs: List[Dict[str, Any]],
                                     nas_services: Dict[str, Any],
                                     usage_analysis: Dict[str, Any],
                                     dbe_analysis: Dict[str, Any],
                                     dba_health: Dict[str, Any]) -> List[str]:
        try:
            """Generate recommendations for database usage"""
            recommendations = []

            # Check if databases are on NAS
            if usage_analysis["databases_on_nas"] == 0:
                recommendations.append("⚠️  No databases found on NAS - consider migrating large databases to NAS for better storage and backup")

            # Check database sizes
            if usage_analysis["total_size_mb"] > 1000:
                recommendations.append("⚠️  Large database footprint (>1GB) - consider archiving old data or moving to NAS")

            # Check DBE/DBA integration
            if not self.dbe_system or not self.dba_system:
                recommendations.append("⚠️  @DBE and @DBA systems not fully implemented - ensure both are available")

            # Check DBE recommendations
            for db_path, analysis in dbe_analysis.items():
                if "recommendations" in analysis:
                    for rec in analysis["recommendations"]:
                        recommendations.append(f"   {rec}")

            # Check DBA health
            for db_path, health in dba_health.items():
                if not health.get("healthy", True):
                    recommendations.append(f"⚠️  Database {Path(db_path).name} health check failed: {health.get('error', 'Unknown error')}")

            # Check NAS services
            accessible_services = [name for name, config in nas_services.get("services", {}).items() 
                                  if config.get("accessible") is True]
            if not accessible_services:
                recommendations.append("⚠️  No database services accessible on NAS - verify NAS database services are running")

            # Check for proper backup
            recommendations.append("✅ Ensure all databases have proper backup strategy")
            recommendations.append("✅ Implement database monitoring and health checks")

            return recommendations


        except Exception as e:
            self.logger.error(f"Error in _generate_recommendations: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="NAS Database Audit")
        parser.add_argument("--audit", action="store_true", help="Run comprehensive audit")
        parser.add_argument("--scan-local", action="store_true", help="Scan local databases")
        parser.add_argument("--check-nas", action="store_true", help="Check NAS database services")
        parser.add_argument("--report", action="store_true", help="Generate audit report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        auditor = NASDatabaseAuditor(project_root)

        if args.audit or not any(vars(args).values()):
            report = auditor.audit_database_usage()
            print("\n" + "="*80)
            print("NAS DATABASE AUDIT REPORT")
            print("="*80)
            print(f"\nLocal Databases: {report['local_databases']['count']}")
            print(f"Total Size: {report['local_databases']['total_size_mb']:.2f} MB")
            print(f"Total Tables: {report['local_databases']['total_tables']}")

            print(f"\nNAS Services:")
            for service, config in report['nas_services'].get('services', {}).items():
                status = "✅ ACCESSIBLE" if config.get('accessible') is True else "❌ NOT ACCESSIBLE"
                print(f"   {service}: {status}")

            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")

            if args.report:
                report_file = project_root / "data" / "nas_database_audit_report.json"
                report_file.parent.mkdir(parents=True, exist_ok=True)
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"\n✅ Report saved: {report_file}")

        elif args.scan_local:
            databases = auditor.scan_local_databases()
            print(f"\nFound {len(databases)} local database(s):")
            for db in databases:
                print(f"   {db['path']}: {db.get('table_count', 0)} tables, {db.get('size_mb', 0):.2f} MB")

        elif args.check_nas:
            services = auditor.check_nas_database_services()
            print(f"\nNAS Database Services ({services['nas_ip']}):")
            for service, config in services.get('services', {}).items():
                print(f"   {service}: {config}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()