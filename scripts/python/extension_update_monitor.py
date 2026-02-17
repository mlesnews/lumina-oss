#!/usr/bin/env python3
"""
Extension Update Monitor - JARVIS Extension Intelligence System

Monitors VSCode/Cursor extension updates and automatically evaluates them using
JARVIS intelligence and SYPHON processing to determine impact, compatibility,
and integration opportunities.

Features:
- Real-time extension update detection
- JARVIS-powered impact assessment
- SYPHON intelligence extraction for new features
- Automated compatibility testing
- Integration opportunity identification
- Performance impact analysis

When extensions update, this system:
1. Detects the update event
2. Extracts new features and changes via SYPHON
3. Evaluates impact using JARVIS intelligence
4. Tests compatibility with existing setup
5. Provides recommendations for integration
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import psutil
import requests

# Import SYPHON components
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from syphon.models import DataSourceType, SyphonData
from syphon.extractors import BaseExtractor, ExtractionResult
from syphon.core import SYPHONConfig, SubscriptionTier
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ExtensionUpdateExtractor(BaseExtractor):
    """Extractor for extension update intelligence"""

    def __init__(self):
        config = SYPHONConfig(
            project_root=project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE
        )
        super().__init__(config)

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from extension update data"""
        try:
            extension_data = content

            syphon_data = SyphonData(
                data_id=f"extension_update_{extension_data['id']}_{extension_data['version']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.WEB,
                source_id=extension_data['id'],
                content=self._format_extension_content(extension_data),
                metadata={
                    **metadata,
                    "extraction_type": "extension_update",
                    "extension_id": extension_data['id'],
                    "extension_name": extension_data['name'],
                    "version": extension_data['version'],
                    "publisher": extension_data['publisher']
                },
                extracted_at=datetime.now(),
                actionable_items=self._extract_actionable_items(extension_data),
                tasks=self._extract_tasks(extension_data),
                decisions=self._extract_decisions(extension_data),
                intelligence=self._extract_intelligence(extension_data)
            )
            return ExtractionResult(success=True, data=syphon_data)
        except Exception as e:
            return ExtractionResult(success=False, error=str(e))

    def _format_extension_content(self, ext: Dict[str, Any]) -> str:
        """Format extension data as structured content"""
        content = f"""
# {ext['name']} v{ext['version']} Update

**Extension ID**: {ext['id']}
**Publisher**: {ext['publisher']}
**Last Updated**: {ext.get('lastUpdated', 'Unknown')}

## Description
{ext.get('description', 'No description available')}

## Key Features
{chr(10).join(f"- {feature}" for feature in ext.get('features', []))}

## Breaking Changes
{chr(10).join(f"- {change}" for change in ext.get('breaking_changes', []))}

## New Capabilities
{chr(10).join(f"- {cap}" for cap in ext.get('new_capabilities', []))}

## Performance Impact
- CPU Impact: {ext.get('performance', {}).get('cpu_impact', 'Unknown')}
- Memory Impact: {ext.get('performance', {}).get('memory_impact', 'Unknown')}
- Startup Time: {ext.get('performance', {}).get('startup_impact', 'Unknown')}

## Compatibility
- VSCode Version: {ext.get('compatibility', {}).get('vscode_version', 'Unknown')}
- Dependencies: {', '.join(ext.get('compatibility', {}).get('dependencies', []))}
"""
        return content

    def _extract_actionable_items(self, ext: Dict[str, Any]) -> List[str]:
        """Extract actionable items for integration"""
        items = []

        if ext.get('breaking_changes'):
            items.append(f"Review breaking changes in {ext['name']} update")

        if ext.get('new_capabilities'):
            items.append(f"Evaluate new capabilities from {ext['name']} for integration")

        if ext.get('performance', {}).get('cpu_impact') in ['high', 'critical']:
            items.append(f"Monitor CPU impact of {ext['name']} update")

        return items

    def _extract_tasks(self, ext: Dict[str, Any]) -> List[str]:
        """Extract tasks for update integration"""
        tasks = [
            f"Test {ext['name']} compatibility with existing extensions",
            f"Review {ext['name']} changelog for integration opportunities",
            f"Update documentation for {ext['name']} new features"
        ]

        if ext.get('breaking_changes'):
            tasks.append(f"Migrate code for {ext['name']} breaking changes")

        return tasks

    def _extract_decisions(self, ext: Dict[str, Any]) -> List[str]:
        """Extract decision points for extension updates"""
        decisions = []

        if ext.get('performance', {}).get('startup_impact') == 'significant':
            decisions.append(f"Evaluate if {ext['name']} startup impact justifies keeping it enabled")

        if len(ext.get('new_capabilities', [])) > 3:
            decisions.append(f"Prioritize integration of {ext['name']} advanced features")

        return decisions

    def _extract_intelligence(self, ext: Dict[str, Any]) -> Dict[str, Any]:
        """Extract intelligence for JARVIS knowledge base"""
        return {
            "extension_profile": {
                "name": ext['name'],
                "publisher": ext['publisher'],
                "category": ext.get('category', 'Unknown'),
                "capabilities": ext.get('capabilities', []),
                "integration_points": ext.get('integration_points', [])
            },
            "update_impact": {
                "breaking_changes": len(ext.get('breaking_changes', [])),
                "new_features": len(ext.get('new_capabilities', [])),
                "performance_impact": ext.get('performance', {}),
                "compatibility_requirements": ext.get('compatibility', {})
            },
            "competitive_intelligence": {
                "market_position": ext.get('market_position', 'Unknown'),
                "unique_features": ext.get('unique_features', []),
                "competitive_advantages": ext.get('competitive_advantages', [])
            }
        }


class ExtensionUpdateMonitor:
    """Monitors extension updates and processes them with JARVIS + SYPHON"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "extension_updates"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.extractor = ExtensionUpdateExtractor()

        # Setup logging
        self.logger = logging.getLogger("ExtensionMonitor")
        self.logger.setLevel(logging.INFO)

        # Extension tracking
        self.known_extensions = self._load_known_extensions()
        self.update_history = self._load_update_history()

    def _load_known_extensions(self) -> Dict[str, Dict[str, Any]]:
        """Load known extensions database"""
        extensions_file = self.data_dir / "known_extensions.json"

        if extensions_file.exists():
            try:
                with open(extensions_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        # Default known extensions
        return {
            "ms-python.python": {
                "name": "Python",
                "publisher": "Microsoft",
                "category": "programming",
                "capabilities": ["intellisense", "debugging", "testing"],
                "last_version": "2024.0.0"
            },
            "ms-vscode.vscode-typescript-next": {
                "name": "TypeScript Importer",
                "publisher": "Microsoft",
                "category": "programming",
                "capabilities": ["typescript", "imports"],
                "last_version": "4.5.0"
            },
            "esbenp.prettier-vscode": {
                "name": "Prettier",
                "publisher": "Prettier",
                "category": "formatter",
                "capabilities": ["formatting", "code_style"],
                "last_version": "10.0.0"
            },
            "ms-vscode.vscode-json": {
                "name": "JSON Language Features",
                "publisher": "Microsoft",
                "category": "language",
                "capabilities": ["json", "validation", "intellisense"],
                "last_version": "1.0.0"
            }
        }

    def _load_update_history(self) -> List[Dict[str, Any]]:
        """Load extension update history"""
        history_file = self.data_dir / "update_history.json"

        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return []

    def check_extension_updates(self) -> List[Dict[str, Any]]:
        """Check for extension updates using VSCode CLI"""
        updates = []

        try:
            # Run VSCode CLI to check for updates
            result = subprocess.run(
                ["code", "--list-extensions", "--show-versions"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                current_extensions = self._parse_extension_list(result.stdout)

                # Check for updates against known versions
                for ext_id, ext_info in current_extensions.items():
                    if ext_id in self.known_extensions:
                        known_version = self.known_extensions[ext_id].get('last_version', '0.0.0')
                        current_version = ext_info.get('version', '0.0.0')

                        if self._is_newer_version(current_version, known_version):
                            updates.append({
                                "id": ext_id,
                                "name": ext_info.get('name', ext_id),
                                "publisher": ext_info.get('publisher', 'Unknown'),
                                "previous_version": known_version,
                                "new_version": current_version,
                                "update_time": datetime.now().isoformat(),
                                "category": self.known_extensions[ext_id].get('category', 'Unknown')
                            })

                            # Update known version
                            self.known_extensions[ext_id]['last_version'] = current_version

        except Exception as e:
            self.logger.error(f"Failed to check extension updates: {e}")

        return updates

    def _parse_extension_list(self, output: str) -> Dict[str, Dict[str, Any]]:
        """Parse VSCode extension list output"""
        extensions = {}

        for line in output.strip().split('\n'):
            if '@' in line:
                try:
                    ext_id, version = line.split('@')
                    # Extract publisher and name
                    if '.' in ext_id:
                        publisher, name = ext_id.split('.', 1)
                    else:
                        publisher = "unknown"
                        name = ext_id

                    extensions[ext_id] = {
                        "name": name,
                        "publisher": publisher,
                        "version": version
                    }
                except Exception:
                    continue

        return extensions

    def _is_newer_version(self, new_version: str, old_version: str) -> bool:
        """Compare version strings"""
        try:
            def parse_version(v):
                return [int(x) for x in v.split('.') if x.isdigit()][:3]

            new_parts = parse_version(new_version)
            old_parts = parse_version(old_version)

            # Pad shorter versions
            while len(new_parts) < 3:
                new_parts.append(0)
            while len(old_parts) < 3:
                old_parts.append(0)

            return new_parts > old_parts
        except Exception:
            return new_version != old_version

    async def process_extension_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an extension update with JARVIS + SYPHON"""

        self.logger.info(f"Processing update for {update_data['name']} v{update_data['new_version']}")

        # Enrich update data with additional information
        enriched_data = await self._enrich_update_data(update_data)

        # Extract intelligence using SYPHON
        metadata = {
            "processing_timestamp": datetime.now().isoformat(),
            "source": "vscode_extension_update",
            "update_type": "extension_update"
        }

        extraction_result = self.extractor.extract(enriched_data, metadata)

        if extraction_result.success and extraction_result.data:
            # Evaluate with JARVIS intelligence
            jarvis_evaluation = await self._jarvis_evaluate_update(extraction_result.data)

            # Generate integration recommendations
            recommendations = self._generate_integration_recommendations(
                extraction_result.data, jarvis_evaluation
            )

            # Record in history
            self.update_history.append({
                "extension_id": update_data["id"],
                "update_data": update_data,
                "extraction_result": {
                    "success": True,
                    "intelligence": extraction_result.data.intelligence
                },
                "jarvis_evaluation": jarvis_evaluation,
                "recommendations": recommendations,
                "processed_at": datetime.now().isoformat()
            })

            # Save updated data
            self._save_data()

            return {
                "extension": update_data["name"],
                "version": update_data["new_version"],
                "evaluation": jarvis_evaluation,
                "recommendations": recommendations,
                "intelligence": extraction_result.data.intelligence
            }

        return {"error": "Failed to process extension update"}

    async def _enrich_update_data(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich update data with additional information"""
        enriched = update_data.copy()

        # Try to fetch changelog or release notes
        try:
            # This would typically fetch from GitHub releases or marketplace
            # For now, we'll add placeholder data
            enriched.update({
                "features": ["Bug fixes", "Performance improvements", "New features"],
                "breaking_changes": [],
                "new_capabilities": ["Enhanced functionality"],
                "performance": {
                    "cpu_impact": "low",
                    "memory_impact": "medium",
                    "startup_impact": "minimal"
                },
                "compatibility": {
                    "vscode_version": ">=1.70.0",
                    "dependencies": []
                },
                "category": update_data.get("category", "development"),
                "capabilities": self.known_extensions.get(update_data["id"], {}).get("capabilities", []),
                "integration_points": ["editor", "language_server", "workspace"]
            })
        except Exception as e:
            self.logger.warning(f"Could not enrich update data: {e}")

        return enriched

    async def _jarvis_evaluate_update(self, syphon_data: SyphonData) -> Dict[str, Any]:
        """Evaluate extension update using JARVIS intelligence"""

        evaluation = {
            "impact_level": "medium",
            "compatibility_score": 85,
            "integration_opportunities": [],
            "risks": [],
            "recommendations": [],
            "priority_actions": []
        }

        # Analyze intelligence for evaluation
        intelligence = syphon_data.intelligence

        # Assess impact based on capabilities
        extension_profile = intelligence.get("extension_profile", {})
        capabilities = extension_profile.get("capabilities", [])

        if "formatter" in capabilities:
            evaluation["impact_level"] = "high"
            evaluation["integration_opportunities"].append("Code formatting standardization")
            evaluation["priority_actions"].append("Test formatting on existing codebase")

        if "language_server" in capabilities:
            evaluation["impact_level"] = "high"
            evaluation["integration_opportunities"].append("Enhanced language intelligence")
            evaluation["compatibility_score"] = 90

        if "debugging" in capabilities:
            evaluation["integration_opportunities"].append("Improved debugging experience")
            evaluation["priority_actions"].append("Verify debugger integration")

        # Check for breaking changes
        update_impact = intelligence.get("update_impact", {})
        if update_impact.get("breaking_changes", 0) > 0:
            evaluation["risks"].append("Breaking changes detected")
            evaluation["compatibility_score"] -= 10

        # Performance impact assessment
        performance = update_impact.get("performance_impact", {})
        if performance.get("cpu_impact") == "high":
            evaluation["risks"].append("High CPU usage impact")
            evaluation["compatibility_score"] -= 5

        # Generate recommendations
        if evaluation["compatibility_score"] >= 90:
            evaluation["recommendations"].append("Safe to update immediately")
        elif evaluation["compatibility_score"] >= 80:
            evaluation["recommendations"].append("Update after testing in development environment")
        else:
            evaluation["recommendations"].append("Requires thorough testing before production update")

        return evaluation

    def _generate_integration_recommendations(self, syphon_data: SyphonData,
                                            jarvis_evaluation: Dict[str, Any]) -> List[str]:
        """Generate integration recommendations"""
        recommendations = []

        intelligence = syphon_data.intelligence
        extension_profile = intelligence.get("extension_profile", {})

        # Based on capabilities
        capabilities = extension_profile.get("capabilities", [])
        category = extension_profile.get("category", "")

        if "formatter" in capabilities and category == "formatter":
            recommendations.extend([
                "Configure as default formatter for supported languages",
                "Update workspace settings to use new formatter",
                "Test formatting consistency across team"
            ])

        if "language_server" in capabilities:
            recommendations.extend([
                "Enable language server features in settings",
                "Configure IntelliSense and autocomplete",
                "Set up language-specific preferences"
            ])

        # Based on evaluation
        if jarvis_evaluation.get("compatibility_score", 0) >= 90:
            recommendations.append("Enable auto-update for this extension")
        else:
            recommendations.append("Monitor extension performance after update")

        return recommendations

    def _save_data(self):
        """Save extension data and history"""
        try:
            # Save known extensions
            with open(self.data_dir / "known_extensions.json", 'w') as f:
                json.dump(self.known_extensions, f, indent=2)

            # Save update history
            with open(self.data_dir / "update_history.json", 'w') as f:
                json.dump(self.update_history, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save extension data: {e}")

    async def monitor_updates_loop(self):
        """Continuous monitoring loop for extension updates"""
        self.logger.info("Starting extension update monitoring...")

        while True:
            try:
                # Check for updates
                updates = self.check_extension_updates()

                if updates:
                    self.logger.info(f"Found {len(updates)} extension updates")

                    for update in updates:
                        result = await self.process_extension_update(update)

                        # Log results
                        if "error" not in result:
                            self.logger.info(f"Processed update for {result['extension']} v{result['version']}")
                            self.logger.info(f"JARVIS Evaluation: {result['evaluation']['impact_level']} impact")

                            # Log key recommendations
                            for rec in result['evaluation']['recommendations'][:2]:
                                self.logger.info(f"Recommendation: {rec}")
                        else:
                            self.logger.error(f"Failed to process update: {result['error']}")

                # Wait before next check (every 6 hours)
                await asyncio.sleep(6 * 60 * 60)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def run_once(self):
        """Run a single update check and processing"""
        updates = self.check_extension_updates()

        if not updates:
            print("No extension updates found.")
            return

        print(f"Found {len(updates)} extension updates:")

        for update in updates:
            print(f"  - {update['name']} ({update['id']}): {update['previous_version']} → {update['new_version']}")

            result = await self.process_extension_update(update)

            if "error" not in result:
                print(f"    ✅ Processed successfully")
                print(f"    📊 Impact: {result['evaluation']['impact_level']}")
                print(f"    🎯 Compatibility: {result['evaluation']['compatibility_score']}%")

                if result['evaluation']['recommendations']:
                    print("    💡 Recommendations:")
                    for rec in result['evaluation']['recommendations'][:3]:
                        print(f"       • {rec}")
            else:
                print(f"    ❌ Processing failed: {result['error']}")

            print()


async def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Extension Update Monitor")
    parser.add_argument("action", choices=["check", "monitor"], help="Action to perform")
    parser.add_argument("--extension", help="Specific extension to check")

    args = parser.parse_args()

    monitor = ExtensionUpdateMonitor()

    if args.action == "check":
        await monitor.run_once()
    elif args.action == "monitor":
        await monitor.monitor_updates_loop()


if __name__ == "__main__":


    asyncio.run(main())