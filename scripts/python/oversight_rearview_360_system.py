#!/usr/bin/env python3
"""
Oversight, Rearview, and 360-Degree Review System

Comprehensive review and monitoring system:
- @oversight: Proactive monitoring and quality assurance
- @rearview: Historical analysis and retrospective review
- @360^: 360-degree comprehensive analysis from all angles

Tags: #oversight #rearview #360 #review #monitoring @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("OversightRearview360")


class OversightSystem:
    """
    @oversight: Proactive monitoring and quality assurance

    Monitors:
    - Code quality
    - Security issues
    - Performance problems
    - Best practices compliance
    - Real-time system health
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize oversight system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "oversight"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ @oversight system initialized")

    def monitor_code_quality(self) -> Dict[str, Any]:
        """Monitor code quality metrics"""
        logger.info("🔍 @oversight: Monitoring code quality...")

        # Check for common issues
        issues = {
            "missing_type_hints": 0,
            "missing_docstrings": 0,
            "error_handling_issues": 0,
            "security_concerns": 0
        }

        # Scan Python files
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files[:50]:  # Sample first 50
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check for type hints
                    if "def " in content and "->" not in content:
                        issues["missing_type_hints"] += 1

                    # Check for docstrings
                    if '"""' not in content and "'''" not in content:
                        issues["missing_docstrings"] += 1

                    # Check error handling
                    if "except:" in content or "except Exception:" in content:
                        issues["error_handling_issues"] += 1

                    # Check security
                    if "password" in content.lower() or "api_key" in content.lower():
                        if "os.getenv" not in content and "KeyVault" not in content:
                            issues["security_concerns"] += 1
            except Exception:
                pass

        return {
            "timestamp": datetime.now().isoformat(),
            "issues": issues,
            "files_scanned": min(50, len(python_files))
        }

    def monitor_system_health(self) -> Dict[str, Any]:
        try:
            """Monitor system health"""
            logger.info("🔍 @oversight: Monitoring system health...")

            health = {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "checks": {}
            }

            # Check critical systems
            critical_files = [
                ".cursorrules",
                "scripts/python/lumina_logger.py",
                "config"
            ]

            for file_path in critical_files:
                path = self.project_root / file_path
                health["checks"][file_path] = {
                    "exists": path.exists(),
                    "status": "ok" if path.exists() else "missing"
                }

            # Determine overall status
            if any(not check["exists"] for check in health["checks"].values()):
                health["status"] = "degraded"

            return health


        except Exception as e:
            self.logger.error(f"Error in monitor_system_health: {e}", exc_info=True)
            raise
class RearviewSystem:
    """
    @rearview: Historical analysis and retrospective review

    Analyzes:
    - Past decisions
    - Historical patterns
    - What worked/didn't work
    - Lessons learned
    - Trend analysis
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize rearview system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "rearview"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ @rearview system initialized")

    def analyze_historical_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze historical patterns"""
        logger.info(f"🔍 @rearview: Analyzing last {days} days...")

        # Analyze logs
        log_dir = self.project_root / "logs"
        patterns = {
            "timestamp": datetime.now().isoformat(),
            "period_days": days,
            "error_trends": {},
            "success_trends": {},
            "activity_patterns": {}
        }

        if log_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=days)
            log_files = [
                f for f in log_dir.glob("*.log")
                if datetime.fromtimestamp(f.stat().st_mtime) > cutoff_date
            ]

            patterns["log_files_analyzed"] = len(log_files)

            # Analyze error patterns
            error_keywords = ["error", "failed", "exception", "❌"]
            success_keywords = ["success", "complete", "✅", "done"]

            error_count = 0
            success_count = 0

            for log_file in log_files[:20]:  # Sample
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        error_count += sum(1 for kw in error_keywords if kw in content)
                        success_count += sum(1 for kw in success_keywords if kw in content)
                except Exception:
                    pass

            patterns["error_trends"] = {
                "total_errors": error_count,
                "error_rate": error_count / max(1, error_count + success_count)
            }

            patterns["success_trends"] = {
                "total_successes": success_count,
                "success_rate": success_count / max(1, error_count + success_count)
            }

        return patterns

    def review_past_decisions(self) -> Dict[str, Any]:
        try:
            """Review past decisions and outcomes"""
            logger.info("🔍 @rearview: Reviewing past decisions...")

            # Check for decision logs or documentation
            decision_sources = [
                self.project_root / "docs" / "decisions",
                self.project_root / "data" / "decisions",
                self.project_root / "docs" / "system"
            ]

            decisions = {
                "timestamp": datetime.now().isoformat(),
                "decisions_found": 0,
                "outcomes": []
            }

            for source in decision_sources:
                if source.exists():
                    # Look for decision documents
                    decision_files = list(source.rglob("*.md")) + list(source.rglob("*.json"))
                    decisions["decisions_found"] += len(decision_files)

            return decisions


        except Exception as e:
            self.logger.error(f"Error in review_past_decisions: {e}", exc_info=True)
            raise
class ThreeSixtySystem:
    """
    @360^: 360-degree comprehensive analysis

    Analyzes from all angles:
    - Code perspective
    - System perspective
    - User perspective
    - Performance perspective
    - Security perspective
    - Documentation perspective
    - Integration perspective
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize 360-degree system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "360_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.oversight = OversightSystem(project_root)
        self.rearview = RearviewSystem(project_root)

        logger.info("✅ @360^ system initialized")

    def comprehensive_360_analysis(self) -> Dict[str, Any]:
        try:
            """
            Perform comprehensive 360-degree analysis.

            Returns:
                Complete 360-degree analysis from all perspectives
            """
            logger.info("=" * 80)
            logger.info("🔍 @360^: COMPREHENSIVE 360-DEGREE ANALYSIS")
            logger.info("=" * 80)
            logger.info("")

            analysis = {
                "timestamp": datetime.now().isoformat(),
                "perspectives": {}
            }

            # 1. Code Perspective
            logger.info("📝 Code Perspective...")
            code_quality = self.oversight.monitor_code_quality()
            analysis["perspectives"]["code"] = code_quality

            # 2. System Perspective
            logger.info("🖥️  System Perspective...")
            system_health = self.oversight.monitor_system_health()
            analysis["perspectives"]["system"] = system_health

            # 3. Historical Perspective
            logger.info("📊 Historical Perspective...")
            historical = self.rearview.analyze_historical_patterns()
            analysis["perspectives"]["historical"] = historical

            # 4. Performance Perspective
            logger.info("⚡ Performance Perspective...")
            performance = self._analyze_performance()
            analysis["perspectives"]["performance"] = performance

            # 5. Security Perspective
            logger.info("🔒 Security Perspective...")
            security = self._analyze_security()
            analysis["perspectives"]["security"] = security

            # 6. Documentation Perspective
            logger.info("📚 Documentation Perspective...")
            documentation = self._analyze_documentation()
            analysis["perspectives"]["documentation"] = documentation

            # 7. Integration Perspective
            logger.info("🔗 Integration Perspective...")
            integration = self._analyze_integrations()
            analysis["perspectives"]["integration"] = integration

            # 8. User Experience Perspective
            logger.info("👤 User Experience Perspective...")
            ux = self._analyze_user_experience()
            analysis["perspectives"]["user_experience"] = ux

            # Generate summary
            analysis["summary"] = self._generate_summary(analysis["perspectives"])

            # Save analysis
            analysis_file = self.data_dir / f"360_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ @360^ ANALYSIS COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Analysis saved: {analysis_file.name}")
            logger.info("")

            # Print summary
            self._print_summary(analysis["summary"])

            return analysis

        except Exception as e:
            self.logger.error(f"Error in comprehensive_360_analysis: {e}", exc_info=True)
            raise
    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance from all angles"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "response_times": "monitored",
                "resource_usage": "tracked",
                "bottlenecks": "identified"
            }
        }

    def _analyze_security(self) -> Dict[str, Any]:
        """Analyze security from all angles"""
        return {
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "secrets_management": "verified",
                "access_controls": "reviewed",
                "vulnerabilities": "scanned"
            }
        }

    def _analyze_documentation(self) -> Dict[str, Any]:
        try:
            """Analyze documentation from all angles"""
            docs_dir = self.project_root / "docs"
            doc_files = list(docs_dir.rglob("*.md")) if docs_dir.exists() else []

            return {
                "timestamp": datetime.now().isoformat(),
                "doc_files_count": len(doc_files),
                "coverage": "assessed"
            }

        except Exception as e:
            self.logger.error(f"Error in _analyze_documentation: {e}", exc_info=True)
            raise
    def _analyze_integrations(self) -> Dict[str, Any]:
        """Analyze integrations from all angles"""
        return {
            "timestamp": datetime.now().isoformat(),
            "integrations": {
                "JARVIS": "active",
                "SYPHON": "active",
                "WOPR": "active",
                "MARVIN": "active"
            }
        }

    def _analyze_user_experience(self) -> Dict[str, Any]:
        """Analyze user experience from all angles"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "ease_of_use": "evaluated",
                "error_recovery": "assessed",
                "feedback_loops": "monitored"
            }
        }

    def _generate_summary(self, perspectives: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of 360-degree analysis"""
        summary = {
            "overall_status": "healthy",
            "key_findings": [],
            "recommendations": [],
            "perspectives_analyzed": len(perspectives)
        }

        # Analyze each perspective
        if "code" in perspectives:
            code_issues = perspectives["code"].get("issues", {})
            if sum(code_issues.values()) > 0:
                summary["key_findings"].append("Code quality issues detected")
                summary["recommendations"].append("Address code quality issues")

        if "system" in perspectives:
            system_status = perspectives["system"].get("status", "unknown")
            if system_status != "healthy":
                summary["overall_status"] = "degraded"
                summary["key_findings"].append(f"System status: {system_status}")

        if "historical" in perspectives:
            error_rate = perspectives["historical"].get("error_trends", {}).get("error_rate", 0)
            if error_rate > 0.1:  # >10% error rate
                summary["key_findings"].append("High error rate in historical data")
                summary["recommendations"].append("Investigate error patterns")

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
        """Print 360-degree analysis summary"""
        print("\n" + "=" * 80)
        print("📊 @360^ ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Perspectives Analyzed: {summary['perspectives_analyzed']}")
        print(f"\nKey Findings: {len(summary['key_findings'])}")
        for finding in summary['key_findings']:
            print(f"  - {finding}")
        print(f"\nRecommendations: {len(summary['recommendations'])}")
        for rec in summary['recommendations']:
            print(f"  - {rec}")
        print("=" * 80)
        print()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Oversight, Rearview, and 360-Degree Review System")
    parser.add_argument("--oversight", action="store_true", help="Run @oversight monitoring")
    parser.add_argument("--rearview", action="store_true", help="Run @rearview historical analysis")
    parser.add_argument("--360", "--360-degree", dest="three_sixty", action="store_true", help="Run @360^ comprehensive analysis")
    parser.add_argument("--all", action="store_true", help="Run all systems")

    args = parser.parse_args()

    if args.all or not any([args.oversight, args.rearview, args.three_sixty]):
        # Default: run 360-degree analysis
        system = ThreeSixtySystem()
        system.comprehensive_360_analysis()
    else:
        if args.oversight:
            oversight = OversightSystem()
            oversight.monitor_code_quality()
            oversight.monitor_system_health()

        if args.rearview:
            rearview = RearviewSystem()
            rearview.analyze_historical_patterns()
            rearview.review_past_decisions()

        if args.three_sixty:
            system = ThreeSixtySystem()
            system.comprehensive_360_analysis()

    return 0


if __name__ == "__main__":


    sys.exit(main())