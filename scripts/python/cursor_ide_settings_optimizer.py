#!/usr/bin/env python3
"""
Cursor IDE Settings Optimizer for LUMINA

Discovers, optimizes, and documents all Cursor IDE settings including
experimental features. Provides recommendations and workarounds.

Tags: #CURSOR_IDE #SETTINGS #OPTIMIZATION #EXPERIMENTAL_FEATURES #LUMINA @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorSettingsOptimizer")


@dataclass
class CursorSetting:
    """Cursor IDE setting definition"""
    key: str
    value: Any
    category: str
    description: str
    experimental: bool = False
    recommended: bool = False
    recommended_value: Any = None
    workaround: Optional[str] = None
    issues: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class SettingCategory:
    """Category of settings"""
    name: str
    description: str
    settings: List[CursorSetting] = field(default_factory=list)


class CursorIDESettingsOptimizer:
    """
    Cursor IDE Settings Optimizer for LUMINA

    Discovers, optimizes, and documents all settings.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize settings optimizer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_dir = self.project_root / ".cursor"
        self.environment_file = self.cursor_dir / "environment.json"
        self.settings_file = self.cursor_dir / "settings.json"

        # Load current settings
        self.current_settings = self._load_current_settings()

        # Known settings database
        self.known_settings = self._build_settings_database()

        # Experimental features
        self.experimental_features = self._discover_experimental_features()

        logger.info("✅ Cursor IDE Settings Optimizer initialized")
        logger.info(f"   Current settings: {len(self.current_settings)} keys")
        logger.info(f"   Known settings: {len(self.known_settings)} settings")
        logger.info(f"   Experimental features: {len(self.experimental_features)} features")

    def _load_current_settings(self) -> Dict[str, Any]:
        """Load current settings from environment.json"""
        settings = {}

        if self.environment_file.exists():
            try:
                with open(self.environment_file, 'r') as f:
                    settings = json.load(f)
            except Exception as e:
                logger.error(f"   ❌ Error loading settings: {e}")

        return settings

    def _build_settings_database(self) -> Dict[str, CursorSetting]:
        """Build comprehensive settings database"""
        settings = {}

        # Agent Settings
        settings["agentCanUpdateSnapshot"] = CursorSetting(
            key="agentCanUpdateSnapshot",
            value=self.current_settings.get("agentCanUpdateSnapshot", True),
            category="Agent",
            description="Allow agent to update codebase snapshots",
            recommended=True,
            recommended_value=True,
            tags=["agent", "snapshot", "codebase"]
        )

        settings["agentMaxSteps"] = CursorSetting(
            key="agentMaxSteps",
            value=self.current_settings.get("agentMaxSteps", 50),
            category="Agent",
            description="Maximum steps agent can take in a single task",
            recommended=True,
            recommended_value=100,  # Increase for complex tasks
            workaround="If agent stops early, increase this value",
            tags=["agent", "steps", "limits"]
        )

        settings["agentContextWindow"] = CursorSetting(
            key="agentContextWindow",
            value=self.current_settings.get("agentContextWindow", 32768),
            category="Agent",
            description="Context window size for agent",
            recommended=True,
            recommended_value=32768,
            tags=["agent", "context", "memory"]
        )

        settings["agentAutoAccept"] = CursorSetting(
            key="agentAutoAccept",
            value=self.current_settings.get("agentAutoAccept", False),
            category="Agent",
            description="Automatically accept agent suggestions",
            recommended=False,
            recommended_value=False,
            workaround="Keep false for safety, use Accept All button when needed",
            tags=["agent", "safety", "auto-accept"]
        )

        # Composer Settings
        settings["composerMaxFiles"] = CursorSetting(
            key="composerMaxFiles",
            value=self.current_settings.get("composerMaxFiles", 50),
            category="Composer",
            description="Maximum files composer can edit",
            recommended=True,
            recommended_value=100,  # Increase for large refactorings
            tags=["composer", "files", "limits"]
        )

        settings["composerContextWindow"] = CursorSetting(
            key="composerContextWindow",
            value=self.current_settings.get("composerContextWindow", 32768),
            category="Composer",
            description="Context window size for composer",
            recommended=True,
            recommended_value=32768,
            tags=["composer", "context", "memory"]
        )

        settings["composerAutoApply"] = CursorSetting(
            key="composerAutoApply",
            value=self.current_settings.get("composerAutoApply", False),
            category="Composer",
            description="Automatically apply composer changes",
            recommended=False,
            recommended_value=False,
            workaround="Keep false for safety, review changes first",
            tags=["composer", "safety", "auto-apply"]
        )

        # Chat Settings
        settings["chatMaxHistory"] = CursorSetting(
            key="chatMaxHistory",
            value=self.current_settings.get("chatMaxHistory", 100),
            category="Chat",
            description="Maximum chat history messages",
            recommended=True,
            recommended_value=200,  # Increase for longer conversations
            tags=["chat", "history", "memory"]
        )

        settings["chatContextWindow"] = CursorSetting(
            key="chatContextWindow",
            value=self.current_settings.get("chatContextWindow", 32768),
            category="Chat",
            description="Context window size for chat",
            recommended=True,
            recommended_value=32768,
            tags=["chat", "context", "memory"]
        )

        settings["chatAutoFocus"] = CursorSetting(
            key="chatAutoFocus",
            value=self.current_settings.get("chatAutoFocus", True),
            category="Chat",
            description="Automatically focus chat input",
            recommended=True,
            recommended_value=True,
            tags=["chat", "ux", "focus"]
        )

        # Inline Completion Settings
        settings["inlineCompletionDelay"] = CursorSetting(
            key="inlineCompletionDelay",
            value=self.current_settings.get("inlineCompletionDelay", 100),
            category="Inline Completion",
            description="Delay before showing inline completions (ms)",
            recommended=True,
            recommended_value=50,  # Faster for better UX
            workaround="Lower value = faster completions, higher CPU",
            tags=["inline", "completion", "performance"]
        )

        settings["inlineCompletionMaxSuggestions"] = CursorSetting(
            key="inlineCompletionMaxSuggestions",
            value=self.current_settings.get("inlineCompletionMaxSuggestions", 5),
            category="Inline Completion",
            description="Maximum inline completion suggestions",
            recommended=True,
            recommended_value=10,  # More options
            tags=["inline", "completion", "suggestions"]
        )

        # Codebase Indexing
        settings["codebaseIndexingEnabled"] = CursorSetting(
            key="codebaseIndexingEnabled",
            value=self.current_settings.get("codebaseIndexingEnabled", True),
            category="Codebase Indexing",
            description="Enable codebase indexing for better context",
            recommended=True,
            recommended_value=True,
            tags=["indexing", "codebase", "context"]
        )

        settings["codebaseIndexingAutoIndex"] = CursorSetting(
            key="codebaseIndexingAutoIndex",
            value=self.current_settings.get("codebaseIndexingAutoIndex", True),
            category="Codebase Indexing",
            description="Automatically index codebase on changes",
            recommended=True,
            recommended_value=True,
            tags=["indexing", "auto", "codebase"]
        )

        settings["codebaseIndexingMaxFiles"] = CursorSetting(
            key="codebaseIndexingMaxFiles",
            value=self.current_settings.get("codebaseIndexingMaxFiles", 10000),
            category="Codebase Indexing",
            description="Maximum files to index",
            recommended=True,
            recommended_value=20000,  # Increase for large codebases
            workaround="Increase if codebase is large and context is missing",
            tags=["indexing", "files", "limits"]
        )

        # Refactoring
        settings["refactoringEnabled"] = CursorSetting(
            key="refactoringEnabled",
            value=self.current_settings.get("refactoringEnabled", True),
            category="Refactoring",
            description="Enable AI-powered refactoring",
            recommended=True,
            recommended_value=True,
            tags=["refactoring", "ai", "code-quality"]
        )

        settings["refactoringAutoSuggest"] = CursorSetting(
            key="refactoringAutoSuggest",
            value=self.current_settings.get("refactoringAutoSuggest", True),
            category="Refactoring",
            description="Automatically suggest refactorings",
            recommended=True,
            recommended_value=True,
            tags=["refactoring", "auto", "suggestions"]
        )

        # Test Generation
        settings["testGenerationEnabled"] = CursorSetting(
            key="testGenerationEnabled",
            value=self.current_settings.get("testGenerationEnabled", True),
            category="Test Generation",
            description="Enable AI-powered test generation",
            recommended=True,
            recommended_value=True,
            tags=["testing", "ai", "generation"]
        )

        settings["testGenerationFramework"] = CursorSetting(
            key="testGenerationFramework",
            value=self.current_settings.get("testGenerationFramework", "pytest"),
            category="Test Generation",
            description="Test framework to use",
            recommended=True,
            recommended_value="pytest",
            tags=["testing", "framework", "pytest"]
        )

        # Debugging
        settings["debuggingEnabled"] = CursorSetting(
            key="debuggingEnabled",
            value=self.current_settings.get("debuggingEnabled", True),
            category="Debugging",
            description="Enable AI-powered debugging",
            recommended=True,
            recommended_value=True,
            tags=["debugging", "ai", "troubleshooting"]
        )

        settings["debuggingAutoExplain"] = CursorSetting(
            key="debuggingAutoExplain",
            value=self.current_settings.get("debuggingAutoExplain", True),
            category="Debugging",
            description="Automatically explain errors",
            recommended=True,
            recommended_value=True,
            tags=["debugging", "auto", "explanations"]
        )

        # Summarization
        settings["summarizationEnabled"] = CursorSetting(
            key="summarizationEnabled",
            value=self.current_settings.get("summarizationEnabled", True),
            category="Summarization",
            description="Enable code summarization",
            recommended=True,
            recommended_value=True,
            tags=["summarization", "ai", "documentation"]
        )

        settings["summarizationAutoTrigger"] = CursorSetting(
            key="summarizationAutoTrigger",
            value=self.current_settings.get("summarizationAutoTrigger", True),
            category="Summarization",
            description="Automatically trigger summarization",
            recommended=True,
            recommended_value=True,
            tags=["summarization", "auto", "trigger"]
        )

        settings["summarizationThreshold"] = CursorSetting(
            key="summarizationThreshold",
            value=self.current_settings.get("summarizationThreshold", 10000),
            category="Summarization",
            description="File size threshold for summarization (chars)",
            recommended=True,
            recommended_value=10000,
            tags=["summarization", "threshold", "files"]
        )

        # Model Settings
        settings["localOnlyMode"] = CursorSetting(
            key="localOnlyMode",
            value=self.current_settings.get("localOnlyMode", True),
            category="Models",
            description="Use only local AI models",
            recommended=True,
            recommended_value=True,
            tags=["models", "local", "privacy"]
        )

        settings["defaultModel"] = CursorSetting(
            key="defaultModel",
            value=self.current_settings.get("defaultModel", "ULTRON"),
            category="Models",
            description="Default AI model to use",
            recommended=True,
            recommended_value="ULTRON",
            tags=["models", "default", "uluron"]
        )

        return settings

    def _discover_experimental_features(self) -> List[Dict[str, Any]]:
        """Discover experimental features"""
        features = [
            {
                "name": "Agent Multi-File Editing",
                "key": "agentMultiFileEditing",
                "description": "Allow agent to edit multiple files simultaneously",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for faster multi-file changes",
                "category": "Agent"
            },
            {
                "name": "Composer Batch Mode",
                "key": "composerBatchMode",
                "description": "Enable batch processing in composer",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for large refactorings",
                "category": "Composer"
            },
            {
                "name": "Chat Streaming",
                "key": "chatStreaming",
                "description": "Stream chat responses in real-time",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for faster chat responses",
                "category": "Chat"
            },
            {
                "name": "Codebase Semantic Search",
                "key": "codebaseSemanticSearch",
                "description": "Use semantic search for codebase queries",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for better code discovery",
                "category": "Codebase Indexing"
            },
            {
                "name": "Inline Completion Streaming",
                "key": "inlineCompletionStreaming",
                "description": "Stream inline completions as they generate",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for faster completions",
                "category": "Inline Completion"
            },
            {
                "name": "Multi-Model Ensemble",
                "key": "multiModelEnsemble",
                "description": "Use multiple models for better results",
                "experimental": True,
                "recommended": False,
                "recommended_value": False,
                "workaround": "May increase latency, use for critical tasks only",
                "category": "Models"
            },
            {
                "name": "Context Compression",
                "key": "contextCompression",
                "description": "Compress context to fit more information",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for large codebases",
                "category": "Context"
            },
            {
                "name": "Incremental Indexing",
                "key": "incrementalIndexing",
                "description": "Index codebase incrementally on changes",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for faster indexing",
                "category": "Codebase Indexing"
            },
            {
                "name": "Predictive Code Navigation",
                "key": "predictiveCodeNavigation",
                "description": "Predict which files you'll need next",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for better navigation",
                "category": "Navigation"
            },
            {
                "name": "Smart Code Folding",
                "key": "smartCodeFolding",
                "description": "Intelligently fold code based on context",
                "experimental": True,
                "recommended": True,
                "recommended_value": True,
                "workaround": "Enable for cleaner code view",
                "category": "UI"
            }
        ]

        return features

    def get_optimized_settings(self) -> Dict[str, Any]:
        """Get optimized settings for LUMINA"""
        optimized = {}

        for key, setting in self.known_settings.items():
            if setting.recommended:
                optimized[key] = setting.recommended_value
            else:
                optimized[key] = setting.value

        # Add experimental features
        for feature in self.experimental_features:
            if feature.get("recommended", False):
                optimized[feature["key"]] = feature["recommended_value"]

        return optimized

    def compare_settings(self) -> Dict[str, Any]:
        """Compare current vs recommended settings"""
        current = self.current_settings
        recommended = self.get_optimized_settings()

        differences = {
            "matches": [],
            "different": [],
            "missing": [],
            "extra": []
        }

        # Check known settings
        for key, setting in self.known_settings.items():
            current_val = current.get(key)
            recommended_val = setting.recommended_value if setting.recommended else setting.value

            if current_val == recommended_val:
                differences["matches"].append(key)
            else:
                differences["different"].append({
                    "key": key,
                    "current": current_val,
                    "recommended": recommended_val,
                    "category": setting.category,
                    "description": setting.description
                })

        # Check for missing recommended settings
        for key in recommended:
            if key not in current:
                differences["missing"].append({
                    "key": key,
                    "recommended": recommended[key]
                })

        # Check for extra settings (not in known database)
        for key in current:
            if key not in self.known_settings and key not in ["models", "workspace", "integrations", "features", "paths", "security", "performance"]:
                differences["extra"].append({
                    "key": key,
                    "value": current[key]
                })

        return differences

    def generate_optimization_report(self) -> str:
        """Generate optimization report"""
        comparison = self.compare_settings()

        report = []
        report.append("=" * 80)
        report.append("🔧 CURSOR IDE SETTINGS OPTIMIZATION REPORT FOR LUMINA")
        report.append("=" * 80)
        report.append("")

        # Summary
        total_settings = len(self.known_settings)
        matches = len(comparison["matches"])
        different = len(comparison["different"])
        missing = len(comparison["missing"])

        report.append("📊 SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Settings: {total_settings}")
        report.append(f"✅ Matches: {matches}")
        report.append(f"⚠️  Different: {different}")
        report.append(f"➕ Missing: {missing}")
        report.append("")

        # Different settings
        if comparison["different"]:
            report.append("⚠️  SETTINGS TO UPDATE")
            report.append("-" * 80)
            for diff in comparison["different"]:
                report.append(f"  {diff['key']}")
                report.append(f"    Current: {diff['current']}")
                report.append(f"    Recommended: {diff['recommended']}")
                report.append(f"    Category: {diff['category']}")
                report.append(f"    Description: {diff['description']}")
                report.append("")

        # Missing settings
        if comparison["missing"]:
            report.append("➕ RECOMMENDED SETTINGS TO ADD")
            report.append("-" * 80)
            for missing in comparison["missing"]:
                report.append(f"  {missing['key']}: {missing['recommended']}")
            report.append("")

        # Experimental features
        report.append("🧪 EXPERIMENTAL FEATURES")
        report.append("-" * 80)
        for feature in self.experimental_features:
            status = "✅ RECOMMENDED" if feature.get("recommended") else "⚠️  OPTIONAL"
            report.append(f"  {status}: {feature['name']}")
            report.append(f"    Key: {feature['key']}")
            report.append(f"    Description: {feature['description']}")
            if feature.get("workaround"):
                report.append(f"    Workaround: {feature['workaround']}")
            report.append("")

        # Workarounds
        report.append("🔧 WORKAROUNDS FOR COMMON PROBLEMS")
        report.append("-" * 80)
        report.append("")
        report.append("1. Agent stops early:")
        report.append("   → Increase agentMaxSteps to 100 or higher")
        report.append("")
        report.append("2. Missing context in large codebase:")
        report.append("   → Increase codebaseIndexingMaxFiles to 20000")
        report.append("   → Enable codebaseSemanticSearch (experimental)")
        report.append("")
        report.append("3. Slow inline completions:")
        report.append("   → Decrease inlineCompletionDelay to 50ms")
        report.append("   → Enable inlineCompletionStreaming (experimental)")
        report.append("")
        report.append("4. Composer can't handle large refactorings:")
        report.append("   → Increase composerMaxFiles to 100")
        report.append("   → Enable composerBatchMode (experimental)")
        report.append("")
        report.append("5. Chat context lost in long conversations:")
        report.append("   → Increase chatMaxHistory to 200")
        report.append("   → Enable contextCompression (experimental)")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)

    def apply_optimized_settings(self, dry_run: bool = True) -> Dict[str, Any]:
        """Apply optimized settings"""
        optimized = self.get_optimized_settings()

        if dry_run:
            logger.info("   🔍 DRY RUN - No changes will be made")
            return {
                "dry_run": True,
                "settings_to_update": optimized,
                "current_settings": self.current_settings
            }

        # Merge with current settings (preserve models, workspace, integrations, features, paths, security, performance)
        updated = self.current_settings.copy()

        # Update individual settings
        for key, value in optimized.items():
            if key not in ["models", "workspace", "integrations", "features", "paths", "security", "performance"]:
                updated[key] = value

        # Save
        try:
            with open(self.environment_file, 'w') as f:
                json.dump(updated, f, indent=2)
            logger.info(f"   ✅ Settings saved to {self.environment_file}")

            # Reload to verify
            self.current_settings = self._load_current_settings()

            return {
                "dry_run": False,
                "settings_updated": len(optimized),
                "file": str(self.environment_file)
            }
        except Exception as e:
            logger.error(f"   ❌ Error saving settings: {e}")
            return {
                "dry_run": False,
                "error": str(e)
            }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Settings Optimizer for LUMINA")
        parser.add_argument("--report", action="store_true", help="Generate optimization report")
        parser.add_argument("--compare", action="store_true", help="Compare current vs recommended")
        parser.add_argument("--optimize", action="store_true", help="Apply optimized settings")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't apply changes)")
        parser.add_argument("--experimental", action="store_true", help="Show experimental features")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        optimizer = CursorIDESettingsOptimizer()

        if args.report:
            report = optimizer.generate_optimization_report()
            print(report)

        elif args.compare:
            comparison = optimizer.compare_settings()
            if args.json:
                print(json.dumps(comparison, indent=2, default=str))
            else:
                print(f"Matches: {len(comparison['matches'])}")
                print(f"Different: {len(comparison['different'])}")
                print(f"Missing: {len(comparison['missing'])}")
                if comparison["different"]:
                    print("\nDifferent settings:")
                    for diff in comparison["different"]:
                        print(f"  {diff['key']}: {diff['current']} → {diff['recommended']}")

        elif args.optimize:
            result = optimizer.apply_optimized_settings(dry_run=args.dry_run)
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                if result.get("dry_run"):
                    print("🔍 DRY RUN - No changes made")
                    print(f"Settings that would be updated: {len(result['settings_to_update'])}")
                else:
                    if "error" in result:
                        print(f"❌ Error: {result['error']}")
                    else:
                        print(f"✅ Settings updated: {result['settings_updated']} settings")

        elif args.experimental:
            features = optimizer.experimental_features
            if args.json:
                print(json.dumps(features, indent=2, default=str))
            else:
                print("=" * 80)
                print("🧪 EXPERIMENTAL FEATURES")
                print("=" * 80)
                for feature in features:
                    status = "✅ RECOMMENDED" if feature.get("recommended") else "⚠️  OPTIONAL"
                    print(f"\n{status}: {feature['name']}")
                    print(f"  Key: {feature['key']}")
                    print(f"  Description: {feature['description']}")
                    if feature.get("workaround"):
                        print(f"  Workaround: {feature['workaround']}")

        else:
            # Default: show report
            report = optimizer.generate_optimization_report()
            print(report)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()