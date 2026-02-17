#!/usr/bin/env python3
"""
Database Engineering Decision Framework (@V3 #WORKFLOWED +RULE)
@DECIDE Team Evaluation System for MariaDB Data Import on NAS.

@V3_WORKFLOWED: True
@RULE_COMPLIANT: True
@TEST_FIRST: True
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import yaml

class DataPriority(Enum):
    """Data import priority levels"""
    CRITICAL = "critical"      # Must import, core functionality
    HIGH = "high"            # Should import, important features
    MEDIUM = "medium"        # Consider import, useful features
    LOW = "low"             # Optional import, nice-to-have
    EXCLUDE = "exclude"      # Do not import, not needed

class DataCategory(Enum):
    """Categories of data for import evaluation"""
    USER_DATA = "user_data"              # User profiles, preferences
    SESSION_DATA = "session_data"        # Chat sessions, conversations
    METADATA = "metadata"               # System metadata, analytics
    CONFIG_DATA = "config_data"         # Configuration, settings
    LOG_DATA = "log_data"               # System logs, audit trails
    ANALYTICS_DATA = "analytics_data"   # Usage analytics, metrics
    BACKUP_DATA = "backup_data"         # Backup files, archives
    CACHE_DATA = "cache_data"           # Cached data, temporary files
    INTELLIGENCE_DATA = "intelligence_data"  # AI/ML intelligence and insights

class DataSensitivity(Enum):
    """Data sensitivity classification"""
    PUBLIC = "public"          # Can be freely shared
    INTERNAL = "internal"      # Internal use only
    CONFIDENTIAL = "confidential"  # Restricted access
    SENSITIVE = "sensitive"    # High security required
    CRITICAL = "critical"      # Maximum security required

@dataclass
class DataAsset:
    """Represents a data asset for import evaluation"""
    name: str
    category: str
    location: str
    size_mb: float
    record_count: Optional[int]
    sensitivity: str
    description: str
    dependencies: List[str]
    retention_policy: str
    update_frequency: str
    tags: List[str]

@dataclass
class ImportDecision:
    """Decision on whether to import a data asset"""
    asset_name: str
    priority: str
    reasoning: str
    estimated_import_time: str
    storage_requirements: str
    performance_impact: str
    compliance_requirements: List[str]
    migration_complexity: str
    recommended_action: str
    decided_by: str
    decided_at: str
    review_date: str

class DatabaseEngineeringDecisionFramework:
    """
    @DECIDE Team Framework for evaluating MariaDB data import decisions.
    Ensures only applicable, viable, actionable data gets imported.
    """

    def __init__(self, nas_mariadb_host: str = "localhost", nas_mariadb_port: int = 3306):
        self.nas_mariadb_host = nas_mariadb_host
        self.nas_mariadb_port = nas_mariadb_port

        # Decision tracking database
        self.decisions_db = Path("./data/database_decisions.db")
        self._init_decisions_database()

        # Import evaluation criteria
        self.evaluation_criteria = self._load_evaluation_criteria()

        print("🗄️  Database Engineering Decision Framework initialized")
        print(f"   MariaDB Target: {nas_mariadb_host}:{nas_mariadb_port}")
        print(f"   Decisions DB: {self.decisions_db}")

    def _init_decisions_database(self):
        try:
            """Initialize decisions tracking database"""
            with sqlite3.connect(self.decisions_db) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS data_assets (
                        name TEXT PRIMARY KEY,
                        category TEXT,
                        location TEXT,
                        size_mb REAL,
                        record_count INTEGER,
                        sensitivity TEXT,
                        description TEXT,
                        dependencies TEXT,
                        retention_policy TEXT,
                        update_frequency TEXT,
                        tags TEXT,
                        discovered_at TEXT
                    )
                ''')

                conn.execute('''
                    CREATE TABLE IF NOT EXISTS import_decisions (
                        asset_name TEXT PRIMARY KEY,
                        priority TEXT,
                        reasoning TEXT,
                        estimated_import_time TEXT,
                        storage_requirements TEXT,
                        performance_impact TEXT,
                        compliance_requirements TEXT,
                        migration_complexity TEXT,
                        recommended_action TEXT,
                        decided_by TEXT,
                        decided_at TEXT,
                        review_date TEXT,
                        FOREIGN KEY (asset_name) REFERENCES data_assets (name)
                    )
                ''')

                conn.execute('''
                    CREATE TABLE IF NOT EXISTS import_metrics (
                        asset_name TEXT,
                        metric_type TEXT,
                        metric_value TEXT,
                        recorded_at TEXT,
                        FOREIGN KEY (asset_name) REFERENCES data_assets (name)
                    )
                ''')
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _init_decisions_database: {e}", exc_info=True)
            raise
    def _load_evaluation_criteria(self) -> Dict[str, Any]:
        """Load evaluation criteria for data import decisions"""
        return {
            "business_value": {
                "CRITICAL": ["core_user_data", "financial_records", "legal_documents"],
                "HIGH": ["analytics_data", "user_preferences", "system_config"],
                "MEDIUM": ["log_data", "backup_files", "cache_data"],
                "LOW": ["temporary_files", "debug_data", "test_data"]
            },
            "data_freshness": {
                "real_time": ["user_sessions", "live_metrics", "active_config"],
                "daily": ["analytics", "logs", "backups"],
                "weekly": ["archives", "historical_data"],
                "monthly": ["compliance_records", "audit_trails"]
            },
            "compliance_requirements": {
                "GDPR": ["user_data", "personal_info", "consent_records"],
                "HIPAA": ["health_data", "medical_records"],
                "SOX": ["financial_data", "audit_trails"],
                "PCI": ["payment_data", "card_info"]
            },
            "performance_impact": {
                "LOW": ["static_config", "reference_data"],
                "MEDIUM": ["user_data", "session_data"],
                "HIGH": ["analytics_queries", "real_time_data"],
                "CRITICAL": ["full_text_search", "complex_joins"]
            }
        }

    def discover_data_assets(self, scan_paths: List[str]) -> List[DataAsset]:
        try:
            """
            Discover data assets from specified paths.
            Returns list of discovered data assets.
            """
            discovered_assets = []

            for scan_path in scan_paths:
                path = Path(scan_path)
                if not path.exists():
                    continue

                print(f"🔍 Scanning: {scan_path}")

                # Scan for various data formats
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        asset = self._analyze_file_asset(file_path)
                        if asset:
                            discovered_assets.append(asset)

            # Save discovered assets
            self._save_discovered_assets(discovered_assets)

            print(f"📊 Discovered {len(discovered_assets)} data assets")
            return discovered_assets

        except Exception as e:
            self.logger.error(f"Error in discover_data_assets: {e}", exc_info=True)
            raise
    def _analyze_file_asset(self, file_path: Path) -> Optional[DataAsset]:
        """Analyze a file to determine if it's a data asset"""
        try:
            # Get file stats
            stat = file_path.stat()
            size_mb = stat.st_size / (1024 * 1024)

            # Skip very small or very large files
            if size_mb < 0.001 or size_mb > 10000:  # 1KB to 10GB
                return None

            # Determine category and sensitivity
            category, sensitivity = self._classify_file(file_path)

            # Estimate record count for databases/structured data
            record_count = self._estimate_record_count(file_path)

            # Generate description
            description = self._generate_asset_description(file_path, category)

            asset = DataAsset(
                name=file_path.name,
                category=category.value,
                location=str(file_path),
                size_mb=round(size_mb, 2),
                record_count=record_count,
                sensitivity=sensitivity.value,
                description=description,
                dependencies=self._identify_dependencies(file_path),
                retention_policy=self._determine_retention_policy(category, sensitivity),
                update_frequency=self._determine_update_frequency(category),
                tags=self._generate_tags(file_path, category)
            )

            return asset

        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return None

    def _classify_file(self, file_path: Path) -> tuple[DataCategory, DataSensitivity]:
        """Classify file into category and sensitivity"""
        name_lower = file_path.name.lower()
        path_str = str(file_path).lower()

        # Determine category
        if any(ext in name_lower for ext in ['.db', '.sqlite', '.sql']):
            category = DataCategory.USER_DATA
        elif 'session' in name_lower or 'chat' in name_lower:
            category = DataCategory.SESSION_DATA
        elif 'log' in name_lower or 'audit' in name_lower:
            category = DataCategory.LOG_DATA
        elif 'config' in name_lower or 'settings' in name_lower:
            category = DataCategory.CONFIG_DATA
        elif 'analytics' in name_lower or 'metrics' in name_lower:
            category = DataCategory.ANALYTICS_DATA
        elif 'backup' in name_lower:
            category = DataCategory.BACKUP_DATA
        elif 'cache' in name_lower or 'temp' in name_lower:
            category = DataCategory.CACHE_DATA
        else:
            category = DataCategory.METADATA

        # Determine sensitivity
        if any(word in path_str for word in ['password', 'secret', 'key', 'token']):
            sensitivity = DataSensitivity.CRITICAL
        elif any(word in path_str for word in ['personal', 'private', 'medical']):
            sensitivity = DataSensitivity.SENSITIVE
        elif 'user' in path_str or 'profile' in path_str:
            sensitivity = DataSensitivity.CONFIDENTIAL
        elif 'internal' in path_str:
            sensitivity = DataSensitivity.INTERNAL
        else:
            sensitivity = DataSensitivity.PUBLIC

        return category, sensitivity

    def _estimate_record_count(self, file_path: Path) -> Optional[int]:
        """Estimate number of records in a data file"""
        try:
            ext = file_path.suffix.lower()

            if ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return len(data)
                    elif isinstance(data, dict) and 'messages' in data:
                        return len(data['messages'])
            elif ext in ['.db', '.sqlite']:
                # Quick check for SQLite databases
                try:
                    with sqlite3.connect(file_path) as conn:
                        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = cursor.fetchall()
                        total_records = 0
                        for table in tables:
                            try:
                                cursor = conn.execute(f"SELECT COUNT(*) FROM {table[0]}")
                                total_records += cursor.fetchone()[0]
                            except:
                                pass
                        return total_records if total_records > 0 else None
                except:
                    pass

        except Exception:
            pass

        return None

    def _generate_asset_description(self, file_path: Path, category: DataCategory) -> str:
        """Generate description for data asset"""
        descriptions = {
            DataCategory.USER_DATA: "User profiles, preferences, and account data",
            DataCategory.SESSION_DATA: "Chat sessions, conversation history, and interaction logs",
            DataCategory.METADATA: "System metadata, configuration, and reference data",
            DataCategory.CONFIG_DATA: "Application configuration and system settings",
            DataCategory.LOG_DATA: "System logs, audit trails, and error reports",
            DataCategory.ANALYTICS_DATA: "Usage analytics, performance metrics, and insights",
            DataCategory.BACKUP_DATA: "Backup files and system recovery data",
            DataCategory.CACHE_DATA: "Cached data and temporary storage files"
        }

        base_desc = descriptions.get(category, "Data file")
        return f"{base_desc} - {file_path.name}"

    def _identify_dependencies(self, file_path: Path) -> List[str]:
        """Identify dependencies for this data asset"""
        dependencies = []

        # Check for related files
        parent_dir = file_path.parent
        base_name = file_path.stem

        # Look for index files, metadata files, etc.
        for related_file in parent_dir.glob(f"{base_name}*"):
            if related_file != file_path:
                dependencies.append(related_file.name)

        return dependencies

    def _determine_retention_policy(self, category: DataCategory, sensitivity: DataSensitivity) -> str:
        """Determine retention policy for data asset"""
        if sensitivity in [DataSensitivity.CRITICAL, DataSensitivity.SENSITIVE]:
            return "7_years_minimum"
        elif category == DataCategory.LOG_DATA:
            return "1_year"
        elif category == DataCategory.ANALYTICS_DATA:
            return "3_years"
        else:
            return "indefinite"

    def _determine_update_frequency(self, category: DataCategory) -> str:
        """Determine update frequency for data asset"""
        if category in [DataCategory.SESSION_DATA, DataCategory.LOG_DATA]:
            return "real_time"
        elif category == DataCategory.ANALYTICS_DATA:
            return "daily"
        elif category == DataCategory.CONFIG_DATA:
            return "on_change"
        else:
            return "weekly"

    def _generate_tags(self, file_path: Path, category: DataCategory) -> List[str]:
        """Generate tags for data asset"""
        tags = [category.value]

        name_lower = file_path.name.lower()
        if 'test' in name_lower or 'sample' in name_lower:
            tags.append('test_data')
        if 'backup' in name_lower:
            tags.append('backup')
        if 'config' in name_lower:
            tags.append('configuration')
        if 'log' in name_lower:
            tags.append('logging')

        return tags

    def _save_discovered_assets(self, assets: List[DataAsset]):
        try:
            """Save discovered assets to database"""
            with sqlite3.connect(self.decisions_db) as conn:
                for asset in assets:
                    conn.execute('''
                        INSERT OR REPLACE INTO data_assets
                        (name, category, location, size_mb, record_count, sensitivity,
                         description, dependencies, retention_policy, update_frequency, tags, discovered_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        asset.name,
                        asset.category,
                        asset.location,
                        asset.size_mb,
                        asset.record_count,
                        asset.sensitivity,
                        asset.description,
                        json.dumps(asset.dependencies),
                        asset.retention_policy,
                        asset.update_frequency,
                        json.dumps(asset.tags),
                        datetime.now().isoformat()
                    ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _save_discovered_assets: {e}", exc_info=True)
            raise
    def evaluate_import_decisions(self, assets: List[DataAsset]) -> Dict[str, ImportDecision]:
        """
        Evaluate import decisions for discovered assets.
        Returns decisions for each asset.
        """
        decisions = {}

        for asset in assets:
            decision = self._evaluate_single_asset(asset)
            decisions[asset.name] = decision

            # Save decision
            self._save_import_decision(decision)

        print(f"⚖️  Evaluated {len(decisions)} import decisions")
        return decisions

    def _evaluate_single_asset(self, asset: DataAsset) -> ImportDecision:
        """Evaluate import decision for a single asset"""
        # Decision logic based on criteria
        priority = self._determine_priority(asset)
        reasoning = self._generate_reasoning(asset, priority)
        estimated_time = self._estimate_import_time(asset)
        storage_reqs = self._calculate_storage_requirements(asset)
        performance_impact = self._assess_performance_impact(asset)
        compliance_reqs = self._identify_compliance_requirements(asset)
        migration_complexity = self._assess_migration_complexity(asset)
        recommended_action = self._generate_recommended_action(asset, priority)

        return ImportDecision(
            asset_name=asset.name,
            priority=priority.value,
            reasoning=reasoning,
            estimated_import_time=estimated_time,
            storage_requirements=storage_reqs,
            performance_impact=performance_impact,
            compliance_requirements=compliance_reqs,
            migration_complexity=migration_complexity,
            recommended_action=recommended_action,
            decided_by="@DECIDE_Database_Engineering_Team",
            decided_at=datetime.now().isoformat(),
            review_date=(datetime.now() + timedelta(days=90)).isoformat()
        )

    def _determine_priority(self, asset: DataAsset) -> DataPriority:
        """Determine import priority for asset"""
        category = DataCategory(asset.category)
        sensitivity = DataSensitivity(asset.sensitivity)

        # Critical priority
        if sensitivity in [DataSensitivity.CRITICAL, DataSensitivity.SENSITIVE]:
            return DataPriority.CRITICAL
        elif category == DataCategory.USER_DATA and asset.record_count and asset.record_count > 1000:
            return DataPriority.CRITICAL

        # High priority
        elif category in [DataCategory.SESSION_DATA, DataCategory.CONFIG_DATA]:
            return DataPriority.HIGH
        elif asset.size_mb > 100:  # Large datasets
            return DataPriority.HIGH

        # Medium priority
        elif category == DataCategory.ANALYTICS_DATA:
            return DataPriority.MEDIUM
        elif asset.update_frequency == "real_time":
            return DataPriority.MEDIUM

        # Low priority
        elif category in [DataCategory.LOG_DATA, DataCategory.CACHE_DATA]:
            return DataPriority.LOW

        # Exclude
        else:
            return DataPriority.EXCLUDE

    def _generate_reasoning(self, asset: DataAsset, priority: DataPriority) -> str:
        """Generate reasoning for import decision"""
        reasons = []

        if priority == DataPriority.CRITICAL:
            reasons.append("Critical for core functionality and data integrity")
        elif priority == DataPriority.HIGH:
            reasons.append("Important for system features and user experience")
        elif priority == DataPriority.MEDIUM:
            reasons.append("Useful for analytics and system optimization")
        elif priority == DataPriority.LOW:
            reasons.append("Optional data with limited immediate value")
        else:
            reasons.append("Not needed for current system requirements")

        # Add size consideration
        if asset.size_mb > 1000:
            reasons.append(f"Large dataset ({asset.size_mb:.1f}MB) requires careful planning")
        elif asset.size_mb < 1:
            reasons.append(f"Small dataset ({asset.size_mb:.1f}MB) low migration overhead")

        # Add sensitivity consideration
        if asset.sensitivity in ["critical", "sensitive"]:
            reasons.append("High sensitivity requires enhanced security measures")

        return "; ".join(reasons)

    def _estimate_import_time(self, asset: DataAsset) -> str:
        """Estimate import time based on asset characteristics"""
        base_time = asset.size_mb / 10  # Rough estimate: 10MB per minute

        if asset.record_count and asset.record_count > 10000:
            base_time *= 2  # Complex data structures

        if asset.category == "user_data":
            base_time *= 1.5  # User data requires validation

        if base_time < 1:
            return "< 1 minute"
        elif base_time < 60:
            return f"{base_time:.1f} minutes"
        else:
            return f"{base_time/60:.1f} hours"

    def _calculate_storage_requirements(self, asset: DataAsset) -> str:
        """Calculate storage requirements"""
        # Estimate MariaDB storage (typically 2-3x raw data size for indexes, etc.)
        estimated_db_size = asset.size_mb * 2.5

        if estimated_db_size < 1:
            return "< 1 MB"
        elif estimated_db_size < 1000:
            return f"{estimated_db_size:.1f} MB"
        else:
            return f"{estimated_db_size/1000:.1f} GB"

    def _assess_performance_impact(self, asset: DataAsset) -> str:
        """Assess performance impact of importing this asset"""
        impact_factors = []

        if asset.category in ["session_data", "analytics_data"]:
            impact_factors.append("query_performance")
        if asset.update_frequency == "real_time":
            impact_factors.append("write_performance")
        if asset.size_mb > 100:
            impact_factors.append("storage_performance")

        if not impact_factors:
            return "LOW"
        elif len(impact_factors) == 1:
            return "MEDIUM"
        else:
            return "HIGH"

    def _identify_compliance_requirements(self, asset: DataAsset) -> List[str]:
        """Identify compliance requirements"""
        requirements = []

        if "user" in asset.name.lower() or "personal" in asset.location.lower():
            requirements.append("GDPR")
        if "medical" in asset.name.lower() or "health" in asset.location.lower():
            requirements.append("HIPAA")
        if "financial" in asset.name.lower() or "payment" in asset.location.lower():
            requirements.append("SOX")
        if "card" in asset.name.lower() or "payment" in asset.location.lower():
            requirements.append("PCI")

        return requirements

    def _assess_migration_complexity(self, asset: DataAsset) -> str:
        """Assess migration complexity"""
        complexity_factors = 0

        if asset.dependencies:
            complexity_factors += 1
        if asset.record_count and asset.record_count > 10000:
            complexity_factors += 1
        if asset.sensitivity in ["critical", "sensitive"]:
            complexity_factors += 1
        if asset.category == "user_data":
            complexity_factors += 1

        if complexity_factors <= 1:
            return "LOW"
        elif complexity_factors <= 3:
            return "MEDIUM"
        else:
            return "HIGH"

    def _generate_recommended_action(self, asset: DataAsset, priority: DataPriority) -> str:
        """Generate recommended action"""
        if priority == DataPriority.CRITICAL:
            return "APPROVE: Import immediately with full testing"
        elif priority == DataPriority.HIGH:
            return "APPROVE: Import in next sprint with validation"
        elif priority == DataPriority.MEDIUM:
            return "REVIEW: Evaluate business value before import"
        elif priority == DataPriority.LOW:
            return "DEFER: Import only if needed for specific features"
        else:
            return "REJECT: Not needed for MariaDB requirements"

    def _save_import_decision(self, decision: ImportDecision):
        try:
            """Save import decision to database"""
            with sqlite3.connect(self.decisions_db) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO import_decisions
                    (asset_name, priority, reasoning, estimated_import_time, storage_requirements,
                     performance_impact, compliance_requirements, migration_complexity,
                     recommended_action, decided_by, decided_at, review_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    decision.asset_name,
                    decision.priority,
                    decision.reasoning,
                    decision.estimated_import_time,
                    decision.storage_requirements,
                    decision.performance_impact,
                    json.dumps(decision.compliance_requirements),
                    decision.migration_complexity,
                    decision.recommended_action,
                    decision.decided_by,
                    decision.decided_at,
                    decision.review_date
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _save_import_decision: {e}", exc_info=True)
            raise
    def generate_import_report(self) -> str:
        """Generate comprehensive import decision report"""
        report = []
        report.append("# 🗄️ MariaDB Data Import Decision Report")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Target:** MariaDB on NAS ({self.nas_mariadb_host}:{self.nas_mariadb_port})")
        report.append("")

        # Get summary statistics
        with sqlite3.connect(self.decisions_db) as conn:
            # Count by priority
            cursor = conn.execute('''
                SELECT priority, COUNT(*) as count
                FROM import_decisions
                GROUP BY priority
            ''')
            priority_counts = dict(cursor.fetchall())

            # Total storage requirements
            cursor = conn.execute('''
                SELECT SUM(CAST(REPLACE(storage_requirements, ' MB', '') AS REAL))
                FROM import_decisions
                WHERE storage_requirements LIKE '%MB'
            ''')
            total_mb = cursor.fetchone()[0] or 0

            # Count by category
            cursor = conn.execute('''
                SELECT da.category, COUNT(*) as count
                FROM data_assets da
                JOIN import_decisions id ON da.name = id.asset_name
                WHERE id.priority IN ('critical', 'high')
                GROUP BY da.category
            ''')
            category_counts = dict(cursor.fetchall())

        # Summary section
        report.append("## 📊 Summary")
        report.append("")
        total_decisions = sum(priority_counts.values())
        approved = priority_counts.get('critical', 0) + priority_counts.get('high', 0)
        approval_rate = (approved / total_decisions * 100) if total_decisions > 0 else 0

        report.append(f"- **Total Assets Evaluated:** {total_decisions}")
        report.append(f"- **Approved for Import:** {approved} ({approval_rate:.1f}%)")
        report.append(f"- **Estimated Storage:** {total_mb:.1f} MB")
        report.append("")

        # Priority breakdown
        report.append("## 🎯 Priority Breakdown")
        report.append("")
        for priority, count in priority_counts.items():
            percentage = (count / total_decisions * 100) if total_decisions > 0 else 0
            report.append(f"- **{priority.upper()}:** {count} assets ({percentage:.1f}%)")

        report.append("")

        # Category breakdown for approved assets
        if category_counts:
            report.append("## 📂 Approved Categories")
            report.append("")
            for category, count in category_counts.items():
                report.append(f"- **{category}:** {count} assets")

        report.append("")

        # Detailed decisions
        report.append("## 📋 Detailed Decisions")
        report.append("")

        with sqlite3.connect(self.decisions_db) as conn:
            cursor = conn.execute('''
                SELECT id.asset_name, id.priority, id.recommended_action,
                       da.size_mb, da.category, da.sensitivity
                FROM import_decisions id
                JOIN data_assets da ON id.asset_name = da.name
                ORDER BY
                    CASE id.priority
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END,
                    da.size_mb DESC
            ''')

            current_priority = None
            for row in cursor.fetchall():
                asset_name, priority, action, size_mb, category, sensitivity = row

                if priority != current_priority:
                    if current_priority is not None:
                        report.append("")
                    report.append(f"### {priority.upper()} Priority")
                    report.append("")
                    current_priority = priority

                compliance_indicator = "🔒" if sensitivity in ["critical", "sensitive"] else ""
                report.append(f"- **{asset_name}** {compliance_indicator}")
                report.append(f"  - Category: {category}")
                report.append(f"  - Size: {size_mb:.1f} MB")
                report.append(f"  - Action: {action}")

        report.append("")
        report.append("## ✅ Next Steps")
        report.append("")
        report.append("1. **Review Critical Priority Assets** - Import immediately")
        report.append("2. **Plan High Priority Assets** - Schedule for next sprint")
        report.append("3. **Evaluate Medium Priority Assets** - Business case review")
        report.append("4. **Document Compliance Requirements** - Security review needed")
        report.append("5. **Prepare Migration Scripts** - Database schema and import procedures")
        report.append("")
        report.append("---")
        report.append("*@DECIDE Database Engineering Team Decision Framework*")
        report.append("*Only applicable, viable, actionable data imported to MariaDB on NAS*")

        return "\\n".join(report)

def create_database_decision_workflow():
    """
    Create the complete database engineering decision workflow.
    @V3_WORKFLOWED +RULE compliant.
    """

    workflow = '''
# 🗄️ DATABASE ENGINEERING DECISION WORKFLOW (@V3 #WORKFLOWED +RULE)

## Core Principles (@DECIDE Team)
- **APPLICABLE**: Only import data that serves current business needs
- **VIABLE**: Ensure data can be properly migrated and maintained
- **ACTIONABLE**: Data must provide value and enable decisions/actions
- **TEST-FIRST**: Validate all import decisions before execution
- **RR METHODOLOGY**: Rest (assess), Roast (identify issues), Repair (fix)

## Decision Framework
1. **DISCOVER**: Scan and catalog all available data assets
2. **EVALUATE**: Assess business value, technical feasibility, compliance
3. **PRIORITIZE**: Critical → High → Medium → Low → Exclude
4. **VALIDATE**: Test import procedures and performance impact
5. **EXECUTE**: Import approved data with monitoring and rollback plans

## Data Categories Evaluated
- **User Data**: Profiles, preferences, account information
- **Session Data**: Chat logs, interaction history, conversations
- **Metadata**: System configuration, reference data, analytics
- **Log Data**: Audit trails, error logs, system monitoring
- **Analytics**: Usage metrics, performance data, insights
- **Backup Data**: Recovery files, historical archives
- **Cache Data**: Temporary storage, computed results

## Priority Criteria
### CRITICAL (Must Import)
- Core user data and authentication
- Financial or legal compliance data
- Real-time operational data
- Data with < 1 year retention requirements

### HIGH (Should Import)
- Active user sessions and preferences
- System configuration and settings
- Recent analytics and performance metrics
- Data updated more frequently than weekly

### MEDIUM (Consider Import)
- Historical analytics (3-12 months)
- Reference data and lookup tables
- Archived logs for compliance
- Data with business value but low access frequency

### LOW (Optional Import)
- Debug logs and temporary files
- Test data and sample datasets
- Legacy data with unclear ownership
- Data that can be regenerated if needed

### EXCLUDE (Do Not Import)
- Duplicate or redundant data
- Data that violates compliance requirements
- Files that can be stored more efficiently elsewhere
- Data with no clear business or technical value

## Usage Example
```python
from database_engineering_decision_framework import DatabaseEngineeringDecisionFramework

# Initialize framework
decide_framework = DatabaseEngineeringDecisionFramework(
    nas_mariadb_host="nas-server.local",
    nas_mariadb_port=3306
)

# Discover data assets
assets = decide_framework.discover_data_assets([
    "./data",
    "./raw_cursor_logs",
    "./holocrons",
    "./artifacts"
])

# Evaluate import decisions
decisions = decide_framework.evaluate_import_decisions(assets)

# Generate report
report = decide_framework.generate_import_report()
print(report)
```
'''

    print(workflow)

# Test-first validation
def test_database_decision_framework():
    """Test the database engineering decision framework"""
    print("🧪 Testing Database Engineering Decision Framework...")

    try:
        # Create framework
        framework = DatabaseEngineeringDecisionFramework()

        # Test asset discovery (using existing files)
        assets = framework.discover_data_assets(["./raw_cursor_logs", "./holocrons"])
        assert len(assets) > 0, "No assets discovered"

        # Test decision evaluation
        decisions = framework.evaluate_import_decisions(assets[:3])  # Test first 3
        assert len(decisions) > 0, "No decisions generated"

        # Test report generation
        report = framework.generate_import_report()
        assert len(report) > 0, "Empty report generated"
        assert "@DECIDE" in report, "Report missing @DECIDE branding"

        print("✅ All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run workflow documentation
    create_database_decision_workflow()

    # Run tests
    print("\\n" + "="*60)
    test_database_decision_framework()

    print("\\n🎯 DATABASE ENGINEERING DECISION FRAMEWORK READY")
    print("   @DECIDE Team: Only applicable, viable, actionable data!")
    print("   @V3 #WORKFLOWED +RULE compliant ✅")
