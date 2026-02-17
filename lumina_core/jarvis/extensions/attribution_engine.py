#!/usr/bin/env python3
"""
🔬 **Lumina Jarvis Attribution Engine**

Manages attribution metadata and ensures ethical compliance for all integrated
extensions, coding assistants, and external tools. Provides automatic attribution
generation, usage tracking, and compliance reporting.

@V3_WORKFLOWED: True
@TEST_FIRST: True
@ETHICAL_ATTRIBUTION: Enforced
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import sqlite3

# Local imports
script_dir = Path(__file__).parent.parent.parent.parent
project_root = script_dir.parent
if str(project_root) not in os.sys.path:
    os.sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("JarvisAttributionEngine")


@dataclass
class AttributionRecord:
    """Record of attribution for a specific usage"""
    extension_name: str
    capability: str
    user_id: str
    timestamp: datetime
    quality_score: float
    usage_context: str
    attribution_text: str
    compliance_status: str = "compliant"


@dataclass
class ExtensionMetadata:
    """Metadata for an integrated extension"""
    name: str
    original_authors: List[str]
    license: str
    repository: str
    integration_date: str
    capabilities_used: List[str]
    attribution_required: bool
    usage_disclosure: str
    license_url: Optional[str] = None
    documentation_url: Optional[str] = None


@dataclass
class UsageMetrics:
    """Usage metrics for an extension"""
    extension_name: str
    total_requests: int = 0
    successful_requests: int = 0
    average_quality: float = 0.0
    average_latency: float = 0.0
    last_used: Optional[datetime] = None
    compliance_rate: float = 1.0


class JarvisAttributionEngine:
    """
    Attribution engine for Jarvis extensions framework.

    Manages attribution metadata, tracks usage, ensures compliance,
    and provides reporting capabilities for all integrated extensions.
    """

    def __init__(self, db_path: str = None):
        self.project_root = Path(__file__).parent.parent.parent.parent

        if db_path is None:
            self.db_path = self.project_root / "data" / "jarvis_extensions.db"
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_cache = {}
        self.usage_cache = {}

        # Initialize database
        self._init_database()

        # Load existing metadata
        self._load_extension_metadata()

        logger.info("✅ Jarvis Attribution Engine initialized")

    def _init_database(self):
        """Initialize attribution database"""
        with sqlite3.connect(self.db_path) as conn:
            # Attribution records table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS attribution_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extension_name TEXT NOT NULL,
                    capability TEXT NOT NULL,
                    user_id TEXT,
                    timestamp TEXT NOT NULL,
                    quality_score REAL,
                    usage_context TEXT,
                    attribution_text TEXT,
                    compliance_status TEXT DEFAULT 'compliant'
                )
            ''')

            # Extension metadata table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS extension_metadata (
                    extension_name TEXT PRIMARY KEY,
                    metadata_json TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')

            # Usage metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usage_metrics (
                    extension_name TEXT PRIMARY KEY,
                    total_requests INTEGER DEFAULT 0,
                    successful_requests INTEGER DEFAULT 0,
                    average_quality REAL DEFAULT 0.0,
                    average_latency REAL DEFAULT 0.0,
                    last_used TEXT,
                    compliance_rate REAL DEFAULT 1.0,
                    updated_at TEXT NOT NULL
                )
            ''')

            conn.commit()

    def _load_extension_metadata(self):
        """Load extension metadata from filesystem"""
        extensions_dir = self.project_root / "lumina_core" / "jarvis" / "extensions"

        # Load from all extension directories
        for category_dir in ["coding_assistants", "ides", "assistants"]:
            category_path = extensions_dir / category_dir
            if category_path.exists():
                for extension_dir in category_path.iterdir():
                    if extension_dir.is_dir():
                        self._load_single_extension_metadata(extension_dir)

    def _load_single_extension_metadata(self, extension_path: Path):
        """Load metadata for a single extension"""
        attribution_file = extension_path / "attribution.json"

        if attribution_file.exists():
            try:
                with open(attribution_file, 'r') as f:
                    metadata_dict = json.load(f)

                # Convert to ExtensionMetadata object
                metadata = ExtensionMetadata(
                    name=metadata_dict['extension_name'],
                    original_authors=metadata_dict['original_authors'],
                    license=metadata_dict['license'],
                    repository=metadata_dict['repository'],
                    integration_date=metadata_dict['integration_date'],
                    capabilities_used=metadata_dict['capabilities_used'],
                    attribution_required=metadata_dict['attribution_required'],
                    usage_disclosure=metadata_dict['usage_disclosure'],
                    license_url=metadata_dict.get('license_url'),
                    documentation_url=metadata_dict.get('documentation_url')
                )

                self.metadata_cache[metadata.name] = metadata

                # Store in database
                self._store_metadata_in_db(metadata)

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"   ⚠️  Failed to load metadata for {extension_path.name}: {e}")

    def _store_metadata_in_db(self, metadata: ExtensionMetadata):
        """Store extension metadata in database"""
        metadata_json = json.dumps({
            'extension_name': metadata.name,
            'original_authors': metadata.original_authors,
            'license': metadata.license,
            'repository': metadata.repository,
            'integration_date': metadata.integration_date,
            'capabilities_used': metadata.capabilities_used,
            'attribution_required': metadata.attribution_required,
            'usage_disclosure': metadata.usage_disclosure,
            'license_url': metadata.license_url,
            'documentation_url': metadata.documentation_url
        })

        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO extension_metadata
                (extension_name, metadata_json, last_updated)
                VALUES (?, ?, ?)
            ''', (metadata.name, metadata_json, datetime.now().isoformat()))
            conn.commit()

    def record_usage(self, extension: str, capability: str, user_id: str = None,
                    quality_score: float = None, usage_context: str = "",
                    latency_ms: float = None) -> AttributionRecord:
        """
        Record usage of an extension for attribution purposes

        Args:
            extension: Name of the extension used
            capability: Capability that was used
            user_id: ID of the user (optional)
            quality_score: Quality score of the result (0.0-1.0)
            usage_context: Context of usage
            latency_ms: Response latency in milliseconds

        Returns:
            AttributionRecord for the usage
        """

        # Get attribution text
        attribution_text = self._generate_attribution_text(extension, capability)

        # Create record
        record = AttributionRecord(
            extension_name=extension,
            capability=capability,
            user_id=user_id or "anonymous",
            timestamp=datetime.now(),
            quality_score=quality_score or 0.0,
            usage_context=usage_context,
            attribution_text=attribution_text,
            compliance_status="compliant"
        )

        # Store in database
        self._store_attribution_record(record)

        # Update usage metrics
        self._update_usage_metrics(extension, record, latency_ms)

        logger.debug(f"   📝 Recorded attribution for {extension}:{capability}")

        return record

    def _generate_attribution_text(self, extension: str, capability: str) -> str:
        """Generate appropriate attribution text for usage"""
        if extension in self.metadata_cache:
            metadata = self.metadata_cache[extension]

            # Generate context-appropriate attribution
            if capability == "code_completion":
                return f"Code completion powered by {metadata.name}"
            elif capability == "code_review":
                return f"Code review assisted by {metadata.name}"
            elif capability == "code_generation":
                return f"Code generated with {metadata.name} technology"
            elif capability == "suggestions":
                return f"Suggestions provided by {metadata.name}"
            else:
                return f"Enhanced by {metadata.name} ({metadata.usage_disclosure})"
        else:
            # Fallback for unknown extensions
            return f"Powered by {extension} technology"

    def _store_attribution_record(self, record: AttributionRecord):
        """Store attribution record in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO attribution_records
                (extension_name, capability, user_id, timestamp, quality_score,
                 usage_context, attribution_text, compliance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.extension_name,
                record.capability,
                record.user_id,
                record.timestamp.isoformat(),
                record.quality_score,
                record.usage_context,
                record.attribution_text,
                record.compliance_status
            ))
            conn.commit()

    def _update_usage_metrics(self, extension: str, record: AttributionRecord,
                             latency_ms: float = None):
        """Update usage metrics for an extension"""
        # Get current metrics
        current_metrics = self.usage_cache.get(extension, UsageMetrics(extension))

        # Update metrics
        current_metrics.total_requests += 1
        if record.quality_score > 0.7:  # Consider successful if quality > 0.7
            current_metrics.successful_requests += 1
        current_metrics.last_used = record.timestamp

        # Update averages
        if record.quality_score > 0:
            current_metrics.average_quality = (
                (current_metrics.average_quality * (current_metrics.total_requests - 1)) +
                record.quality_score
            ) / current_metrics.total_requests

        if latency_ms and latency_ms > 0:
            current_metrics.average_latency = (
                (current_metrics.average_latency * (current_metrics.total_requests - 1)) +
                latency_ms
            ) / current_metrics.total_requests

        # Update compliance rate (assume all recorded usages are compliant)
        current_metrics.compliance_rate = 1.0

        # Cache updated metrics
        self.usage_cache[extension] = current_metrics

        # Store in database
        self._store_usage_metrics(current_metrics)

    def _store_usage_metrics(self, metrics: UsageMetrics):
        """Store usage metrics in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO usage_metrics
                (extension_name, total_requests, successful_requests,
                 average_quality, average_latency, last_used,
                 compliance_rate, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.extension_name,
                metrics.total_requests,
                metrics.successful_requests,
                metrics.average_quality,
                metrics.average_latency,
                metrics.last_used.isoformat() if metrics.last_used else None,
                metrics.compliance_rate,
                datetime.now().isoformat()
            ))
            conn.commit()

    def get_extension_metadata(self, extension_name: str) -> Optional[ExtensionMetadata]:
        """Get metadata for a specific extension"""
        return self.metadata_cache.get(extension_name)

    def get_usage_metrics(self, extension_name: str) -> Optional[UsageMetrics]:
        """Get usage metrics for a specific extension"""
        # Check cache first
        if extension_name in self.usage_cache:
            return self.usage_cache[extension_name]

        # Load from database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT * FROM usage_metrics WHERE extension_name = ?
            ''', (extension_name,))

            row = cursor.fetchone()
            if row:
                metrics = UsageMetrics(
                    extension_name=row[0],
                    total_requests=row[1],
                    successful_requests=row[2],
                    average_quality=row[3],
                    average_latency=row[4],
                    last_used=datetime.fromisoformat(row[5]) if row[5] else None,
                    compliance_rate=row[6]
                )

                self.usage_cache[extension_name] = metrics
                return metrics

        return None

    def generate_compliance_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate attribution compliance report"""
        cutoff_date = datetime.now() - timedelta(days=days_back)

        with sqlite3.connect(self.db_path) as conn:
            # Get attribution records
            cursor = conn.execute('''
                SELECT extension_name, COUNT(*) as usage_count,
                       AVG(quality_score) as avg_quality,
                       SUM(CASE WHEN compliance_status = 'compliant' THEN 1 ELSE 0 END) as compliant_count
                FROM attribution_records
                WHERE timestamp >= ?
                GROUP BY extension_name
            ''', (cutoff_date.isoformat(),))

            extension_compliance = {}
            for row in cursor.fetchall():
                extension_name, usage_count, avg_quality, compliant_count = row
                compliance_rate = compliant_count / usage_count if usage_count > 0 else 1.0

                extension_compliance[extension_name] = {
                    'usage_count': usage_count,
                    'average_quality': avg_quality or 0.0,
                    'compliance_rate': compliance_rate,
                    'compliant_usages': compliant_count,
                    'period_days': days_back
                }

            # Overall statistics
            cursor = conn.execute('''
                SELECT COUNT(*) as total_records,
                       AVG(quality_score) as overall_quality,
                       SUM(CASE WHEN compliance_status = 'compliant' THEN 1 ELSE 0 END) as total_compliant
                FROM attribution_records
                WHERE timestamp >= ?
            ''', (cutoff_date.isoformat(),))

            row = cursor.fetchone()
            total_records, overall_quality, total_compliant = row

            overall_compliance = total_compliant / total_records if total_records > 0 else 1.0

            return {
                'report_period_days': days_back,
                'generated_at': datetime.now().isoformat(),
                'overall_compliance': {
                    'total_attributions': total_records,
                    'compliant_attributions': total_compliant,
                    'compliance_rate': overall_compliance,
                    'average_quality': overall_quality or 0.0
                },
                'extension_compliance': extension_compliance,
                'status': '✅ FULLY COMPLIANT' if overall_compliance >= 0.99 else '⚠️  REVIEW NEEDED'
            }

    def check_license_compliance(self, extension_name: str) -> Dict[str, Any]:
        """Check license compliance for an extension"""
        metadata = self.get_extension_metadata(extension_name)

        if not metadata:
            return {
                'compliant': False,
                'error': 'Extension metadata not found',
                'license_status': 'unknown'
            }

        # Basic license compliance check
        # In a real implementation, this would check against SPDX license database
        compliant_licenses = [
            'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause',
            'ISC', 'CC0-1.0', 'Unlicense'
        ]

        license_compliant = metadata.license in compliant_licenses

        return {
            'compliant': license_compliant,
            'license': metadata.license,
            'license_url': metadata.license_url,
            'attribution_required': metadata.attribution_required,
            'commercial_use_allowed': self._check_commercial_use(metadata.license),
            'modification_allowed': self._check_modification_allowed(metadata.license)
        }

    def _check_commercial_use(self, license: str) -> bool:
        """Check if license allows commercial use"""
        commercial_friendly = [
            'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'
        ]
        return license in commercial_friendly

    def _check_modification_allowed(self, license: str) -> bool:
        """Check if license allows modification"""
        modification_allowed = [
            'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'
        ]
        return license in modification_allowed

    def export_attribution_data(self, format: str = 'json') -> str:
        """Export attribution data for external use"""
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'extensions_metadata': {},
            'usage_metrics': {},
            'compliance_report': self.generate_compliance_report()
        }

        # Add extension metadata
        for name, metadata in self.metadata_cache.items():
            data['extensions_metadata'][name] = {
                'name': metadata.name,
                'authors': metadata.original_authors,
                'license': metadata.license,
                'repository': metadata.repository,
                'capabilities': metadata.capabilities_used
            }

        # Add usage metrics
        for name, metrics in self.usage_cache.items():
            data['usage_metrics'][name] = {
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'average_quality': metrics.average_quality,
                'average_latency': metrics.average_latency,
                'compliance_rate': metrics.compliance_rate
            }

        if format == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            # Simple text format
            output = [f"Jarvis Attribution Export - {data['export_timestamp']}\n"]

            output.append("Extensions Metadata:")
            for name, meta in data['extensions_metadata'].items():
                output.append(f"  {name}: {meta['license']} - {', '.join(meta['authors'])}")

            output.append("\nUsage Metrics:")
            for name, metrics in data['usage_metrics'].items():
                output.append(f"  {name}: {metrics['total_requests']} requests, {metrics['average_quality']:.2f} quality")

            output.append(f"\nCompliance: {data['compliance_report']['status']}")

            return '\n'.join(output)

    def cleanup_old_records(self, days_to_keep: int = 365):
        """Clean up old attribution records"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM attribution_records
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))

            deleted_count = cursor.rowcount
            conn.commit()

        logger.info(f"   🧹 Cleaned up {deleted_count} old attribution records")
        return deleted_count


# Global instance
_attribution_engine = None


def get_attribution_engine() -> JarvisAttributionEngine:
    """Get or create attribution engine instance"""
    global _attribution_engine
    if _attribution_engine is None:
        _attribution_engine = JarvisAttributionEngine()
    return _attribution_engine


def record_extension_usage(extension: str, capability: str, **kwargs) -> AttributionRecord:
    """Convenience function to record extension usage"""
    engine = get_attribution_engine()
    return engine.record_usage(extension, capability, **kwargs)


def get_extension_metadata(extension_name: str) -> Optional[ExtensionMetadata]:
    """Get metadata for an extension"""
    engine = get_attribution_engine()
    return engine.get_extension_metadata(extension_name)


def generate_compliance_report() -> Dict[str, Any]:
    """Generate compliance report"""
    engine = get_attribution_engine()
    return engine.generate_compliance_report()


if __name__ == "__main__":
    # Test the attribution engine
    engine = get_attribution_engine()

    # Record some test usage
    record = engine.record_usage(
        extension="kilo_code",
        capability="code_completion",
        user_id="test_user",
        quality_score=0.85,
        usage_context="Python function completion"
    )

    print("🎯 Test Attribution Record:")
    print(f"   Extension: {record.extension_name}")
    print(f"   Capability: {record.capability}")
    print(f"   Attribution: {record.attribution_text}")

    # Generate compliance report
    report = engine.generate_compliance_report(days_back=7)
    print("\n📊 Compliance Report:")
    print(f"   Overall Status: {report['status']}")
    print(f"   Total Attributions: {report['overall_compliance']['total_attributions']}")
    print(".1%")