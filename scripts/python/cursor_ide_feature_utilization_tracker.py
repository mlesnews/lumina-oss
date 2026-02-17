#!/usr/bin/env python3
"""
Cursor IDE Feature Utilization Tracker

Tracks which Cursor IDE features we're using and working toward 100% utilization.
Includes Resend button, dialogs, shortcuts, and all available features.

Tags: #CURSOR_IDE #FEATURE_TRACKING #UTILIZATION #100_PERCENT @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

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

logger = get_logger("CursorIDEFeatureTracker")


@dataclass
class CursorFeature:
    """Cursor IDE feature"""
    name: str
    category: str  # "button", "shortcut", "dialog", "api", "integration"
    description: str
    utilized: bool = False
    utilization_count: int = 0
    last_used: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    priority: str = "medium"  # "high", "medium", "low"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CursorIDEFeatureUtilizationTracker:
    """
    Cursor IDE Feature Utilization Tracker

    Tracks all Cursor IDE features and works toward 100% utilization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize feature tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_ide_features"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.features_file = self.data_dir / "features.json"
        self.features: Dict[str, CursorFeature] = {}

        # Initialize known features
        self._initialize_known_features()

        # Load existing tracking data
        self._load_features()

        logger.info("✅ Cursor IDE Feature Utilization Tracker initialized")
        logger.info(f"   Tracking {len(self.features)} features")
        logger.info(f"   Current utilization: {self.get_utilization_percentage():.1f}%")

    def _initialize_known_features(self):
        try:
            """Initialize known Cursor IDE features"""
            known_features = [
                # Buttons
                {
                    "name": "Resend Button",
                    "category": "button",
                    "description": "Resend failed AI requests (ECONNRESET recovery)",
                    "priority": "high",
                    "notes": ["Currently not utilized - should use for connection errors"]
                },
                {
                    "name": "Accept All Changes",
                    "category": "button",
                    "description": "Accept all file changes in dialog",
                    "priority": "high",
                    "notes": ["Has automation script but not fully integrated"]
                },
                {
                    "name": "Keep All",
                    "category": "button",
                    "description": "Keep all files in merge conflict",
                    "priority": "medium"
                },
                {
                    "name": "Discard All",
                    "category": "button",
                    "description": "Discard all changes",
                    "priority": "low"
                },

                # Shortcuts
                {
                    "name": "Ctrl+Shift+A (Auto-accept)",
                    "category": "shortcut",
                    "description": "Hotkey for auto-accepting dialogs",
                    "priority": "high",
                    "notes": ["Available in automate_cursor_dialogs.py"]
                },
                {
                    "name": "Ctrl+K Ctrl+S",
                    "category": "shortcut",
                    "description": "Keyboard shortcuts editor",
                    "priority": "medium"
                },
                {
                    "name": "Ctrl+Shift+P",
                    "category": "shortcut",
                    "description": "Command palette",
                    "priority": "high",
                    "utilized": True  # Commonly used
                },

                # Dialogs
                {
                    "name": "File Change Dialog",
                    "category": "dialog",
                    "description": "Dialog for accepting file changes",
                    "priority": "high",
                    "notes": ["Has automation but not always triggered"]
                },
                {
                    "name": "Merge Conflict Dialog",
                    "category": "dialog",
                    "description": "Dialog for resolving merge conflicts",
                    "priority": "medium"
                },

                # APIs & Integrations
                {
                    "name": "Cursor API",
                    "category": "api",
                    "description": "Programmatic access to Cursor IDE features",
                    "priority": "high",
                    "notes": ["Not fully explored - potential for automation"]
                },
                {
                    "name": "VS Code Extension API",
                    "category": "api",
                    "description": "VS Code extension API (Cursor is based on VS Code)",
                    "priority": "high",
                    "notes": ["Could create custom extensions"]
                },
                {
                    "name": "MCP Integration",
                    "category": "integration",
                    "description": "Model Context Protocol integration",
                    "priority": "high",
                    "utilized": True  # We use MCP
                },
                {
                    "name": "Cursor Settings API",
                    "category": "api",
                    "description": "Programmatic settings management",
                    "priority": "medium"
                },

                # Connection Features
                {
                    "name": "Connection Retry",
                    "category": "button",
                    "description": "Automatic retry on connection errors",
                    "priority": "high",
                    "notes": ["We have resilience system but not using Resend button"]
                },
                {
                    "name": "Error Recovery",
                    "category": "feature",
                    "description": "Built-in error recovery mechanisms",
                    "priority": "high",
                    "notes": ["Should integrate with our error monitoring"]
                },

                # AI Features (from Cursor Docs)
                {
                    "name": "AI Chat",
                    "category": "feature",
                    "description": "AI chat interface (Ctrl+L / Cmd+L)",
                    "priority": "high",
                    "utilized": True
                },
                {
                    "name": "AI Composer",
                    "category": "feature",
                    "description": "AI code composer (Ctrl+I / Cmd+I)",
                    "priority": "high",
                    "utilized": True
                },
                {
                    "name": "Cursor Tab",
                    "category": "feature",
                    "description": "Multi-line code suggestions based on project context",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs - reduces manual coding"]
                },
                {
                    "name": "Agent Mode",
                    "category": "feature",
                    "description": "Autonomous task handling - code generation, terminal commands, debugging (Ctrl+. / Cmd+.)",
                    "priority": "high",
                    "notes": ["From Cursor Docs - acts as co-developer", "Toggle in Composer"]
                },
                {
                    "name": "AI Autocomplete",
                    "category": "feature",
                    "description": "AI-powered autocomplete",
                    "priority": "high",
                    "utilized": True
                },
                {
                    "name": "AI Code Review",
                    "category": "feature",
                    "description": "AI code review suggestions",
                    "priority": "medium"
                },
                {
                    "name": "Toggle AI Models",
                    "category": "shortcut",
                    "description": "Toggle between AI models (Ctrl+/ / Cmd+/)",
                    "priority": "high",
                    "notes": ["From Cursor Docs - switch between OpenAI, Anthropic, Gemini, xAI"]
                },
                {
                    "name": "Add Code to Chat",
                    "category": "shortcut",
                    "description": "Add selected code to chat (Ctrl+L / Cmd+L)",
                    "priority": "high",
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Submit with Codebase",
                    "category": "shortcut",
                    "description": "Submit chat with codebase context (Ctrl+Enter / Cmd+Enter)",
                    "priority": "high",
                    "notes": ["From Cursor Docs"]
                },

                # Inline Editing (from Cursor Docs)
                {
                    "name": "Cmd+K Menu",
                    "category": "shortcut",
                    "description": "Open inline edit menu (Ctrl+K / Cmd+K)",
                    "priority": "high",
                    "notes": ["From Cursor Docs - inline editing with AI"]
                },
                {
                    "name": "Apply Inline Changes",
                    "category": "shortcut",
                    "description": "Apply inline AI changes (Ctrl+Enter / Cmd+Enter)",
                    "priority": "high",
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Cancel Inline Changes",
                    "category": "shortcut",
                    "description": "Cancel/delete inline changes (Ctrl+Backspace / Cmd+Backspace)",
                    "priority": "high",
                    "notes": ["From Cursor Docs"]
                },

                # Documentation Features (from Cursor Docs)
                {
                    "name": "@Docs Feature",
                    "category": "feature",
                    "description": "Access official documentation without leaving IDE",
                    "priority": "high",
                    "notes": ["From Cursor Docs - documentation integration"]
                },
                {
                    "name": "@Web Feature",
                    "category": "feature",
                    "description": "Web searches without leaving IDE",
                    "priority": "high",
                    "notes": ["From Cursor Docs - web search integration"]
                },

                # Codebase Features (from Cursor Docs)
                {
                    "name": "Codebase Indexing",
                    "category": "feature",
                    "description": "Automatic indexing of new files and version control integration",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs - understands code relationships"]
                },
                {
                    "name": "Codebase Understanding",
                    "category": "feature",
                    "description": "Deep understanding and recall through embedding models",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs"]
                },

                # MCP Features (from Cursor Docs)
                {
                    "name": "MCP Support",
                    "category": "integration",
                    "description": "Model Context Protocol - Vercel, GitHub, Figma, Stripe, Sentry",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs - we use MCP"]
                },
                {
                    "name": "Custom MCP Servers",
                    "category": "api",
                    "description": "Connect to proprietary databases, internal docs, custom tools",
                    "priority": "high",
                    "notes": ["From Cursor Docs - extend functionality"]
                },
                {
                    "name": "Database Integration",
                    "category": "integration",
                    "description": "PostgreSQL, MongoDB, MySQL, Redis via MCP",
                    "priority": "medium",
                    "notes": ["From Cursor Docs - direct query execution"]
                },

                # Version Control (from Cursor Docs)
                {
                    "name": "Version Control Integration",
                    "category": "integration",
                    "description": "GitHub, GitLab, Bitbucket - repository management, CI/CD",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs - we use Git/GitLens"]
                },

                # Advanced Features (from Cursor Docs)
                {
                    "name": "Scoped Changes",
                    "category": "feature",
                    "description": "Targeted edits or terminal commands using natural language",
                    "priority": "high",
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Multi-Line Edits",
                    "category": "feature",
                    "description": "Suggested edits across multiple lines",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Smart Rewrites",
                    "category": "feature",
                    "description": "Cursor predicts and completes your thoughts",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Custom Commands",
                    "category": "feature",
                    "description": "Use and manage reusable prompts within team",
                    "priority": "medium",
                    "notes": ["From Cursor Docs"]
                },

                # Navigation Shortcuts (from Cursor Docs)
                {
                    "name": "Quick Open File",
                    "category": "shortcut",
                    "description": "Quick file open (Ctrl+P / Cmd+P)",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Go to Line",
                    "category": "shortcut",
                    "description": "Go to specific line (Ctrl+G / Cmd+G)",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Go to Symbol in Workspace",
                    "category": "shortcut",
                    "description": "Jump to symbol (Ctrl+T / Cmd+T)",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Jump to Symbol in File",
                    "category": "shortcut",
                    "description": "Symbol navigation in file (Ctrl+Shift+O / Cmd+Shift+O)",
                    "priority": "high",
                    "utilized": True,
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Peek Definition",
                    "category": "shortcut",
                    "description": "Peek at definition (Alt+F12 / Option+F12)",
                    "priority": "medium",
                    "notes": ["From Cursor Docs"]
                },
                {
                    "name": "Zen Mode",
                    "category": "shortcut",
                    "description": "Toggle Zen mode (Ctrl+K Z / Cmd+K Z)",
                    "priority": "low",
                    "notes": ["From Cursor Docs"]
                },

                # Workflow Features
                {
                    "name": "Git Integration",
                    "category": "integration",
                    "description": "Git/GitLens integration",
                    "priority": "high",
                    "utilized": True
                },
                {
                    "name": "Terminal Integration",
                    "category": "integration",
                    "description": "Integrated terminal",
                    "priority": "high",
                    "utilized": True
                },
                {
                    "name": "File Explorer",
                    "category": "feature",
                    "description": "File explorer sidebar",
                    "priority": "high",
                    "utilized": True
                },
                {
                    "name": "Search",
                    "category": "feature",
                    "description": "Global search functionality",
                    "priority": "high",
                    "utilized": True
                }
            ]

            for feature_data in known_features:
                feature = CursorFeature(**feature_data)
                self.features[feature.name] = feature

        except Exception as e:
            self.logger.error(f"Error in _initialize_known_features: {e}", exc_info=True)
            raise
    def _load_features(self):
        """Load feature tracking data"""
        if self.features_file.exists():
            try:
                with open(self.features_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, feature_data in data.get("features", {}).items():
                        if name in self.features:
                            # Update existing feature with saved data
                            saved_feature = CursorFeature(**feature_data)
                            self.features[name].utilized = saved_feature.utilized
                            self.features[name].utilization_count = saved_feature.utilization_count
                            self.features[name].last_used = saved_feature.last_used
                            if saved_feature.notes:
                                self.features[name].notes = saved_feature.notes
                    logger.info(f"   ✅ Loaded feature tracking data")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load features: {e}")

    def _save_features(self):
        """Save feature tracking data"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "features": {name: feature.to_dict() for name, feature in self.features.items()}
            }
            with open(self.features_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving features: {e}")

    def record_feature_use(self, feature_name: str, notes: Optional[str] = None):
        """Record feature usage"""
        if feature_name not in self.features:
            logger.warning(f"   ⚠️  Unknown feature: {feature_name}")
            return

        feature = self.features[feature_name]
        feature.utilized = True
        feature.utilization_count += 1
        feature.last_used = datetime.now().isoformat()

        if notes:
            feature.notes.append(f"{datetime.now().isoformat()}: {notes}")

        self._save_features()
        logger.info(f"   ✅ Recorded usage: {feature_name} ({feature.utilization_count} times)")

    def get_utilization_percentage(self) -> float:
        """Get overall utilization percentage"""
        if not self.features:
            return 0.0

        utilized = sum(1 for f in self.features.values() if f.utilized)
        total = len(self.features)

        return (utilized / total) * 100.0 if total > 0 else 0.0

    def get_unutilized_features(self, priority: Optional[str] = None) -> List[CursorFeature]:
        """Get unutilized features"""
        unutilized = [f for f in self.features.values() if not f.utilized]

        if priority:
            unutilized = [f for f in unutilized if f.priority == priority]

        # Sort by priority (high first)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        unutilized.sort(key=lambda f: priority_order.get(f.priority, 3))

        return unutilized

    def get_utilization_report(self) -> Dict[str, Any]:
        """Get comprehensive utilization report"""
        total = len(self.features)
        utilized = sum(1 for f in self.features.values() if f.utilized)
        unutilized = total - utilized
        percentage = self.get_utilization_percentage()

        # By category
        by_category = {}
        for feature in self.features.values():
            if feature.category not in by_category:
                by_category[feature.category] = {"total": 0, "utilized": 0}
            by_category[feature.category]["total"] += 1
            if feature.utilized:
                by_category[feature.category]["utilized"] += 1

        # By priority
        by_priority = {}
        for feature in self.features.values():
            if feature.priority not in by_priority:
                by_priority[feature.priority] = {"total": 0, "utilized": 0}
            by_priority[feature.priority]["total"] += 1
            if feature.utilized:
                by_priority[feature.priority]["utilized"] += 1

        # High priority unutilized
        high_priority_unutilized = self.get_unutilized_features(priority="high")

        return {
            "timestamp": datetime.now().isoformat(),
            "overall": {
                "total_features": total,
                "utilized": utilized,
                "unutilized": unutilized,
                "percentage": percentage
            },
            "by_category": by_category,
            "by_priority": by_priority,
            "high_priority_unutilized": [
                {
                    "name": f.name,
                    "category": f.category,
                    "description": f.description,
                    "notes": f.notes
                }
                for f in high_priority_unutilized
            ],
            "next_steps": [
                f"Utilize '{f.name}' ({f.category})" for f in high_priority_unutilized[:5]
            ]
        }

    def print_report(self):
        """Print utilization report"""
        report = self.get_utilization_report()

        print("=" * 80)
        print("📊 CURSOR IDE FEATURE UTILIZATION REPORT")
        print("=" * 80)
        print()
        print(f"Overall Utilization: {report['overall']['percentage']:.1f}%")
        print(f"  Total Features: {report['overall']['total_features']}")
        print(f"  Utilized: {report['overall']['utilized']}")
        print(f"  Unutilized: {report['overall']['unutilized']}")
        print()

        print("By Category:")
        for category, stats in report['by_category'].items():
            cat_percentage = (stats['utilized'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {category}: {stats['utilized']}/{stats['total']} ({cat_percentage:.1f}%)")
        print()

        print("By Priority:")
        for priority, stats in report['by_priority'].items():
            pri_percentage = (stats['utilized'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {priority}: {stats['utilized']}/{stats['total']} ({pri_percentage:.1f}%)")
        print()

        if report['high_priority_unutilized']:
            print("🚨 High Priority Unutilized Features:")
            for feature in report['high_priority_unutilized']:
                print(f"  • {feature['name']} ({feature['category']})")
                print(f"    {feature['description']}")
                if feature['notes']:
                    for note in feature['notes'][-2:]:  # Last 2 notes
                        print(f"    📝 {note}")
            print()

        if report['next_steps']:
            print("📋 Next Steps:")
            for step in report['next_steps']:
                print(f"  • {step}")
        print()


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Feature Utilization Tracker")
        parser.add_argument("--report", action="store_true", help="Show utilization report")
        parser.add_argument("--record", nargs=2, metavar=("FEATURE", "NOTES"),
                           help="Record feature usage")
        parser.add_argument("--unutilized", choices=["high", "medium", "low"],
                           help="Show unutilized features by priority")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        tracker = CursorIDEFeatureUtilizationTracker()

        if args.record:
            feature_name, notes = args.record
            tracker.record_feature_use(feature_name, notes)
            if args.json:
                print(json.dumps({"recorded": True, "feature": feature_name}, indent=2))
            else:
                print(f"✅ Recorded usage: {feature_name}")
                print(f"   Utilization: {tracker.get_utilization_percentage():.1f}%")

        elif args.unutilized:
            features = tracker.get_unutilized_features(priority=args.unutilized)
            if args.json:
                print(json.dumps([f.to_dict() for f in features], indent=2))
            else:
                print(f"\n🚨 Unutilized {args.unutilized} priority features:")
                for feature in features:
                    print(f"  • {feature.name} ({feature.category})")
                    print(f"    {feature.description}")

        elif args.report or not any([args.record, args.unutilized]):
            report = tracker.get_utilization_report()
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                tracker.print_report()

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()