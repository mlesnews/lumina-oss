#!/usr/bin/env python3
"""
Macro Conflict Detector

Detects conflicting shortcuts across methods (PowerToys, AutoHotkey, Armoury Crate, MANUS).

Tags: #MACROS #CONFLICT_DETECTION #POWERTOYS #AUTOHOTKEY #ARMOURY_CRATE #MANUS @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
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

logger = get_logger("MacroConflictDetector")


class MacroConflictDetector:
    """
    Macro Conflict Detector

    Detects conflicts across:
    - PowerToys
    - AutoHotkey
    - Armoury Crate
    - MANUS
    - Hybrid Framework
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize conflict detector"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "macro_conflicts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.conflicts: List[Dict[str, Any]] = []

        logger.info("✅ Macro Conflict Detector initialized")

    def detect_conflicts(self) -> Dict[str, Any]:
        """
        Detect all macro conflicts

        Returns:
            Dictionary with conflicts and recommendations
        """
        logger.info("=" * 80)
        logger.info("🔍 DETECTING MACRO CONFLICTS")
        logger.info("=" * 80)
        logger.info("")

        # Load macros from all sources
        powertoys_macros = self._load_powertoys_macros()
        autohotkey_macros = self._load_autohotkey_macros()
        armoury_crate_macros = self._load_armoury_crate_macros()
        manus_macros = self._load_manus_macros()
        hybrid_macros = self._load_hybrid_macros()

        # Build shortcut registry
        shortcut_registry = self._build_shortcut_registry(
            powertoys_macros,
            autohotkey_macros,
            armoury_crate_macros,
            manus_macros,
            hybrid_macros
        )

        # Detect conflicts
        self.conflicts = self._find_conflicts(shortcut_registry)

        # Generate recommendations
        recommendations = self._generate_recommendations(self.conflicts)

        result = {
            "total_conflicts": len(self.conflicts),
            "conflicts": self.conflicts,
            "recommendations": recommendations,
            "shortcut_registry": shortcut_registry
        }

        logger.info(f"   📋 Total Conflicts: {len(self.conflicts)}")
        logger.info("")

        if self.conflicts:
            logger.info("🔍 CONFLICTS DETECTED:")
            for i, conflict in enumerate(self.conflicts, 1):
                logger.info(f"   {i}. {conflict['shortcut']}: {conflict['methods']}")
        else:
            logger.info("   ✅ No conflicts detected")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ CONFLICT DETECTION COMPLETE")
        logger.info("=" * 80)
        logger.info("")

        return result

    def _load_powertoys_macros(self) -> List[Dict[str, Any]]:
        try:
            """Load PowerToys macros"""
            config_file = self.project_root / "data" / "macros" / "powertoys_keyboard_manager.json"
            macros = []

            if config_file.exists():
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    # Extract shortcuts
                    for remap in config.get("remapKeys", []):
                        macros.append({
                            "method": "powertoys",
                            "shortcut": remap.get("originalKeys", ""),
                            "type": "key_remap"
                        })

                    for remap in config.get("remapShortcuts", []):
                        macros.append({
                            "method": "powertoys",
                            "shortcut": remap.get("originalKeys", ""),
                            "type": "shortcut_remap"
                        })

            return macros

        except Exception as e:
            self.logger.error(f"Error in _load_powertoys_macros: {e}", exc_info=True)
            raise
    def _load_autohotkey_macros(self) -> List[Dict[str, Any]]:
        try:
            """Load AutoHotkey macros"""
            script_file = self.project_root / "data" / "macros" / "lumina_macros.ahk"
            macros = []

            if script_file.exists():
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse AutoHotkey shortcuts (simplified)
                    import re
                    # Match patterns like "^!U::" (Ctrl+Alt+U)
                    patterns = re.findall(r'([^:]+)::', content)
                    for pattern in patterns:
                        if pattern.strip() and not pattern.strip().startswith(';'):
                            macros.append({
                                "method": "autohotkey",
                                "shortcut": pattern.strip(),
                                "type": "ahk_shortcut"
                            })

            return macros

        except Exception as e:
            self.logger.error(f"Error in _load_autohotkey_macros: {e}", exc_info=True)
            raise
    def _load_armoury_crate_macros(self) -> List[Dict[str, Any]]:
        try:
            """Load Armoury Crate macros"""
            config_file = self.project_root / "data" / "macros" / "armoury_crate_macros.json"
            macros = []

            if config_file.exists():
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    for macro in config.get("macros", []):
                        # Skip disabled macros (they don't conflict)
                        if macro.get("enabled", True) is False:
                            continue
                        macros.append({
                            "method": "armoury_crate",
                            "shortcut": macro.get("trigger", ""),
                            "type": "ac_macro"
                        })

            return macros

        except Exception as e:
            self.logger.error(f"Error in _load_armoury_crate_macros: {e}", exc_info=True)
            raise
    def _load_manus_macros(self) -> List[Dict[str, Any]]:
        """Load MANUS shortcuts"""
        # MANUS shortcuts are system-wide, check config
        manus_config = self.project_root / "data" / "manus_shortcuts"
        macros = []

        # Simplified - would need actual MANUS config parsing
        return macros

    def _load_hybrid_macros(self) -> List[Dict[str, Any]]:
        try:
            """Load hybrid framework macros"""
            config_file = self.project_root / "data" / "hybrid_macros" / "hybrid_macros.json"
            macros = []

            if config_file.exists():
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    for macro in config.get("macros", []):
                        macros.append({
                            "method": "hybrid",
                            "shortcut": macro.get("trigger", ""),
                            "type": "hybrid_macro",
                            "name": macro.get("name", "")
                        })

            return macros

        except Exception as e:
            self.logger.error(f"Error in _load_hybrid_macros: {e}", exc_info=True)
            raise
    def _build_shortcut_registry(self, *macro_lists) -> Dict[str, List[Dict[str, Any]]]:
        """Build registry of shortcuts by method"""
        registry = defaultdict(list)

        for macro_list in macro_lists:
            for macro in macro_list:
                shortcut = self._normalize_shortcut(macro["shortcut"])
                if shortcut:
                    registry[shortcut].append(macro)

        return dict(registry)

    def _normalize_shortcut(self, shortcut: str) -> str:
        """Normalize shortcut for comparison"""
        if not shortcut:
            return ""

        # Convert to lowercase, remove spaces
        normalized = shortcut.lower().replace(" ", "").replace("+", "+")
        return normalized

    def _find_conflicts(self, registry: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Find conflicts in shortcut registry"""
        conflicts = []

        for shortcut, macros in registry.items():
            if len(macros) > 1:
                # Multiple macros use same shortcut
                methods = [m["method"] for m in macros]
                if len(set(methods)) > 1:
                    # Different methods conflict
                    conflicts.append({
                        "shortcut": shortcut,
                        "methods": methods,
                        "macros": macros,
                        "severity": "high" if "hybrid" in methods else "medium"
                    })

        return conflicts

    def _generate_recommendations(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommendations for conflicts"""
        recommendations = []

        for conflict in conflicts:
            rec = {
                "shortcut": conflict["shortcut"],
                "issue": f"Conflict between {', '.join(conflict['methods'])}",
                "recommendation": self._suggest_resolution(conflict),
                "priority": conflict["severity"]
            }
            recommendations.append(rec)

        return recommendations

    def _suggest_resolution(self, conflict: Dict[str, Any]) -> str:
        """Suggest resolution for conflict"""
        methods = conflict["methods"]

        if "hybrid" in methods:
            return "Hybrid framework should take precedence. Disable duplicate in other methods."
        elif "powertoys" in methods and "autohotkey" in methods:
            return "Choose one method (PowerToys recommended for Windows). Disable AutoHotkey version."
        else:
            return "Review and choose primary method. Disable duplicates."

    def save_report(self, result: Dict[str, Any]) -> Path:
        """Save conflict detection report"""
        import json

        report_file = self.data_dir / "conflict_report.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Conflict report saved: {report_file.name}")
        return report_file


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Macro Conflict Detector")
    parser.add_argument("--detect", action="store_true", help="Detect conflicts")
    parser.add_argument("--save-report", action="store_true", help="Save report")

    args = parser.parse_args()

    detector = MacroConflictDetector()

    if args.detect or args.save_report:
        result = detector.detect_conflicts()
        if args.save_report:
            detector.save_report(result)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())