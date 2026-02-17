#!/usr/bin/env python3
"""
Homelab Audit Reporting and Visualization System

Generates comprehensive reports and visualizations from homelab audit data.
Supports symbiotic/autonomous change detection and complexity drift analysis.

Tags: #HOMELAB #AUDIT #REPORTING #VISUALIZATION #COMPLEXITY_DRIFT @JARVIS @LUMINA
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pymysql
from pymysql.cursors import DictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_audit_reporter")


class HomelabAuditReporter:
    """Generates reports from homelab audit data"""

    def __init__(
        self, host: str, user: str, password: str, database: str = "homelab_audit", port: int = 3306
    ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        """Connect to MariaDB"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset="utf8mb4",
                cursorclass=DictCursor,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        if not self.connection:
            if not self.connect():
                return {}

        cursor = self.connection.cursor()

        try:
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "summary": self._generate_summary(cursor),
                "devices": self._generate_device_report(cursor),
                "complexity_analysis": self._generate_complexity_analysis(cursor),
                "drift_analysis": self._generate_drift_analysis(cursor),
                "ecosystem_health": self._generate_ecosystem_health(cursor),
                "recommendations": self._generate_recommendations(cursor),
            }

            return report

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {}
        finally:
            cursor.close()

    def _generate_summary(self, cursor) -> Dict[str, Any]:
        """Generate summary statistics"""
        # Total devices
        cursor.execute("SELECT COUNT(DISTINCT device_id) as total FROM devices")
        total_devices = cursor.fetchone()["total"]

        # Total features
        cursor.execute("SELECT COUNT(*) as total FROM device_features")
        total_features = cursor.fetchone()["total"]

        # Devices by type
        cursor.execute("""
            SELECT device_type, COUNT(*) as count
            FROM devices
            GROUP BY device_type
        """)
        devices_by_type = {row["device_type"]: row["count"] for row in cursor.fetchall()}

        # Features by category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM device_features
            GROUP BY category
        """)
        features_by_category = {row["category"]: row["count"] for row in cursor.fetchall()}

        # Latest audit
        cursor.execute("SELECT * FROM audit_history ORDER BY audit_timestamp DESC LIMIT 1")
        latest_audit = cursor.fetchone()

        return {
            "total_devices": total_devices,
            "total_features": total_features,
            "devices_by_type": devices_by_type,
            "features_by_category": features_by_category,
            "latest_audit": latest_audit["audit_id"] if latest_audit else None,
            "latest_audit_timestamp": latest_audit["audit_timestamp"].isoformat()
            if latest_audit and hasattr(latest_audit["audit_timestamp"], "isoformat")
            else str(latest_audit["audit_timestamp"])
            if latest_audit
            else None,
        }

    def _generate_device_report(self, cursor) -> List[Dict[str, Any]]:
        """Generate device-level report"""
        cursor.execute("""
            SELECT d.*,
                   COUNT(DISTINCT df.feature_id) as feature_count,
                   COUNT(DISTINCT ds.service_id) as service_count,
                   COUNT(DISTINCT dni.interface_id) as interface_count
            FROM devices d
            LEFT JOIN device_features df ON d.device_id = df.device_id
            LEFT JOIN device_services ds ON d.device_id = ds.device_id
            LEFT JOIN device_network_interfaces dni ON d.device_id = dni.device_id
            GROUP BY d.device_id
            ORDER BY d.complexity_score DESC
        """)

        devices = []
        for row in cursor.fetchall():
            device = {
                "device_id": row["device_id"],
                "device_name": row["device_name"],
                "device_type": row["device_type"],
                "operating_system": row["operating_system"],
                "ip_address": row["ip_address"],
                "complexity_score": float(row["complexity_score"]),
                "feature_count": row["feature_count"],
                "service_count": row["service_count"],
                "interface_count": row["interface_count"],
                "last_audited": row["last_audited"].isoformat()
                if hasattr(row["last_audited"], "isoformat")
                else str(row["last_audited"]),
            }
            devices.append(device)

        return devices

    def _generate_complexity_analysis(self, cursor) -> Dict[str, Any]:
        """Generate complexity analysis"""
        # Complexity trends
        cursor.execute("""
            SELECT audit_timestamp, total_complexity_score, total_devices, total_features
            FROM audit_history
            ORDER BY audit_timestamp DESC
            LIMIT 30
        """)

        trends = []
        for row in cursor.fetchall():
            trends.append(
                {
                    "timestamp": row["audit_timestamp"].isoformat()
                    if hasattr(row["audit_timestamp"], "isoformat")
                    else str(row["audit_timestamp"]),
                    "complexity_score": float(row["total_complexity_score"]),
                    "devices": row["total_devices"],
                    "features": row["total_features"],
                }
            )

        # Top complex devices
        cursor.execute("""
            SELECT device_id, device_name, complexity_score
            FROM devices
            ORDER BY complexity_score DESC
            LIMIT 10
        """)

        top_complex = [
            {
                "device_id": row["device_id"],
                "device_name": row["device_name"],
                "complexity_score": float(row["complexity_score"]),
            }
            for row in cursor.fetchall()
        ]

        # Complexity by device type
        cursor.execute("""
            SELECT device_type, AVG(complexity_score) as avg_complexity, COUNT(*) as count
            FROM devices
            GROUP BY device_type
        """)

        by_type = {
            row["device_type"]: {
                "avg_complexity": float(row["avg_complexity"]),
                "count": row["count"],
            }
            for row in cursor.fetchall()
        }

        return {
            "trends": trends,
            "top_complex_devices": top_complex,
            "complexity_by_device_type": by_type,
        }

    def _generate_drift_analysis(self, cursor) -> Dict[str, Any]:
        """Generate complexity drift analysis"""
        # Recent drift events
        cursor.execute("""
            SELECT cdl.*, d.device_name
            FROM complexity_drift_log cdl
            JOIN devices d ON cdl.device_id = d.device_id
            ORDER BY cdl.drift_timestamp DESC
            LIMIT 50
        """)

        recent_drift = []
        for row in cursor.fetchall():
            recent_drift.append(
                {
                    "device_id": row["device_id"],
                    "device_name": row["device_name"],
                    "drift_type": row["drift_type"],
                    "timestamp": row["drift_timestamp"].isoformat()
                    if hasattr(row["drift_timestamp"], "isoformat")
                    else str(row["drift_timestamp"]),
                    "delta": json.loads(row["delta"])
                    if isinstance(row["delta"], str)
                    else row["delta"],
                }
            )

        # Drift by device
        cursor.execute("""
            SELECT device_id, COUNT(*) as drift_count
            FROM complexity_drift_log
            GROUP BY device_id
            ORDER BY drift_count DESC
        """)

        drift_by_device = {row["device_id"]: row["drift_count"] for row in cursor.fetchall()}

        # Drift by type
        cursor.execute("""
            SELECT drift_type, COUNT(*) as count
            FROM complexity_drift_log
            GROUP BY drift_type
        """)

        drift_by_type = {row["drift_type"]: row["count"] for row in cursor.fetchall()}

        return {
            "recent_drift_events": recent_drift,
            "drift_by_device": drift_by_device,
            "drift_by_type": drift_by_type,
        }

    def _generate_ecosystem_health(self, cursor) -> Dict[str, Any]:
        """Generate ecosystem health metrics"""
        # Device health (based on last audit)
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN last_audited > DATE_SUB(NOW(), INTERVAL 24 HOUR) THEN 1 ELSE 0 END) as recently_audited,
                SUM(CASE WHEN last_audited < DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as stale
            FROM devices
        """)

        health_row = cursor.fetchone()

        # Service health
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM device_services
            GROUP BY status
        """)

        service_health = {row["status"]: row["count"] for row in cursor.fetchall()}

        return {
            "device_health": {
                "total_devices": health_row["total"],
                "recently_audited": health_row["recently_audited"],
                "stale_devices": health_row["stale"],
                "health_percentage": round(
                    (health_row["recently_audited"] / health_row["total"] * 100)
                    if health_row["total"] > 0
                    else 0,
                    2,
                ),
            },
            "service_health": service_health,
        }

    def _generate_recommendations(self, cursor) -> List[str]:
        """Generate recommendations based on audit data"""
        recommendations = []

        # Check for stale devices
        cursor.execute("""
            SELECT device_id, device_name, last_audited
            FROM devices
            WHERE last_audited < DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)

        stale_devices = cursor.fetchall()
        if stale_devices:
            recommendations.append(
                f"⚠️  {len(stale_devices)} device(s) have not been audited in 7+ days. Consider running audit."
            )

        # Check for high complexity devices
        cursor.execute("""
            SELECT device_id, device_name, complexity_score
            FROM devices
            WHERE complexity_score > 50
            ORDER BY complexity_score DESC
        """)

        high_complexity = cursor.fetchall()
        if high_complexity:
            recommendations.append(
                f"🔴 {len(high_complexity)} device(s) have high complexity scores (>50). Consider simplification."
            )

        # Check for drift
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM complexity_drift_log
            WHERE drift_timestamp > DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """)

        recent_drift = cursor.fetchone()["count"]
        if recent_drift > 10:
            recommendations.append(
                f"📈 High complexity drift detected ({recent_drift} events in 24h). Monitor closely."
            )

        return recommendations

    def print_report(self, report: Dict[str, Any]):
        """Print formatted report"""
        print("=" * 80)
        print("HOMELAB TOP-DOWN AUDIT REPORT")
        print("=" * 80)
        print(f"Generated: {report['report_timestamp']}")
        print()

        # Summary
        summary = report["summary"]
        print("SUMMARY")
        print("-" * 80)
        print(f"Total Devices: {summary['total_devices']}")
        print(f"Total Features: {summary['total_features']}")
        print(f"Latest Audit: {summary['latest_audit_timestamp']}")
        print()

        print("Devices by Type:")
        for device_type, count in summary["devices_by_type"].items():
            print(f"  {device_type}: {count}")
        print()

        print("Features by Category:")
        for category, count in summary["features_by_category"].items():
            print(f"  {category}: {count}")
        print()

        # Devices
        print("DEVICES")
        print("-" * 80)
        for device in report["devices"][:10]:  # Top 10
            print(f"  {device['device_name']} ({device['device_type']})")
            print(f"    Complexity: {device['complexity_score']}")
            print(f"    Features: {device['feature_count']}, Services: {device['service_count']}")
            print()

        # Complexity Analysis
        complexity = report["complexity_analysis"]
        print("COMPLEXITY ANALYSIS")
        print("-" * 80)
        print("Top Complex Devices:")
        for device in complexity["top_complex_devices"][:5]:
            print(f"  {device['device_name']}: {device['complexity_score']}")
        print()

        # Drift Analysis
        drift = report["drift_analysis"]
        print("COMPLEXITY DRIFT")
        print("-" * 80)
        print(f"Recent Drift Events: {len(drift['recent_drift_events'])}")
        print("Drift by Type:")
        for drift_type, count in drift["drift_by_type"].items():
            print(f"  {drift_type}: {count}")
        print()

        # Ecosystem Health
        health = report["ecosystem_health"]
        print("ECOSYSTEM HEALTH")
        print("-" * 80)
        device_health = health["device_health"]
        print(f"Device Health: {device_health['health_percentage']}%")
        print(
            f"  Recently Audited: {device_health['recently_audited']}/{device_health['total_devices']}"
        )
        print(f"  Stale Devices: {device_health['stale_devices']}")
        print()

        # Recommendations
        if report["recommendations"]:
            print("RECOMMENDATIONS")
            print("-" * 80)
            for rec in report["recommendations"]:
                print(f"  {rec}")
            print()

        print("=" * 80)

    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()


def main():
    """Main entry point"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Generate homelab audit reports")
    parser.add_argument(
        "--host", default=os.environ.get("MARIADB_HOST", "<NAS_PRIMARY_IP>"), help="MariaDB host"
    )
    parser.add_argument(
        "--user", default=os.environ.get("MARIADB_USER", "lumina"), help="MariaDB user"
    )
    parser.add_argument(
        "--password", default=os.environ.get("MARIADB_PASSWORD"), help="MariaDB password"
    )
    parser.add_argument("--database", default="homelab_audit", help="Database name")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.password:
        print("Error: MariaDB password required (--password or MARIADB_PASSWORD env var)")
        sys.exit(1)

    reporter = HomelabAuditReporter(
        host=args.host, user=args.user, password=args.password, database=args.database
    )

    if reporter.connect():
        report = reporter.generate_comprehensive_report()

        if args.json:
            print(json.dumps(report, indent=2, default=str))
        else:
            reporter.print_report(report)

    reporter.close()


if __name__ == "__main__":
    main()
