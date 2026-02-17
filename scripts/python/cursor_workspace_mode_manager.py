#!/usr/bin/env python3
"""
Cursor Workspace Mode Manager
@MARVIN @JARVIS

Manages workspace vs non-workspace mode operations in Cursor IDE:
- Workspace mode: For debugging (full project context)
- Non-workspace mode: For normal programming operations

Implements proper workflow, precedence, and operations like real-life programming.
Automatically syncs configurations between modes when required.
"""

import sys
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [WorkspaceMode] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class WorkspaceMode(Enum):
    """Workspace operation modes"""
    WORKSPACE = "workspace"  # Folder/project opened - for debugging
    NON_WORKSPACE = "non_workspace"  # Single file(s) opened - for normal programming
    UNKNOWN = "unknown"


@dataclass
class WorkspaceState:
    """Current workspace state"""
    mode: WorkspaceMode
    workspace_path: Optional[Path] = None
    open_files: List[Path] = field(default_factory=list)
    has_workspace_folder: bool = False
    is_debug_mode: bool = False
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkspaceConfig:
    """Configuration for workspace vs non-workspace modes"""
    workspace_mode: Dict[str, Any] = field(default_factory=dict)
    non_workspace_mode: Dict[str, Any] = field(default_factory=dict)
    sync_settings: List[str] = field(default_factory=list)
    auto_sync: bool = True
    sync_interval_minutes: int = 60


class CursorWorkspaceModeManager:
    """
    Manages Cursor IDE workspace mode operations with proper workflows.

    Key Principles:
    1. Workspace mode (folder opened) = Debugging (full context)
    2. Non-workspace mode (files only) = Normal programming
    3. Settings sync automatically between modes when required
    4. Proper precedence: Workspace > User > Default
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.cursor_config_dir = Path.home() / ".cursor"
        self.workspace_settings_path = self.project_root / ".cursor" / "settings.json"
        self.user_settings_path = self.cursor_config_dir / "User" / "settings.json"

        # Configuration
        self.config_path = self.project_root / "config" / "cursor_workspace_config.json"
        self.config = self._load_config()

        # State tracking
        self.current_state = WorkspaceState(mode=WorkspaceMode.UNKNOWN)

        logger.info("✅ Cursor Workspace Mode Manager initialized")

    def _load_config(self) -> WorkspaceConfig:
        """Load workspace configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Filter only fields that WorkspaceConfig expects
                    config_data = {
                        "workspace_mode": data.get("workspace_mode", {}),
                        "non_workspace_mode": data.get("non_workspace_mode", {}),
                        "sync_settings": data.get("sync_settings", []),
                        "auto_sync": data.get("auto_sync", True),
                        "sync_interval_minutes": data.get("sync_interval_minutes", 60)
                    }
                    return WorkspaceConfig(**config_data)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        # Default configuration
        return WorkspaceConfig(
            workspace_mode={
                "debug.enabled": True,
                "debug.allowBreakpointsEverywhere": True,
                "debug.showBreakpointsInOverviewRuler": True,
                "debug.inlineValues": True,
                "debug.toolBarLocation": "floating",
                "files.watcherExclude": {
                    "**/.git/objects/**": True,
                    "**/.git/subtree-cache/**": True,
                    "**/node_modules/*/**": True
                },
                "search.exclude": {
                    "**/node_modules": True,
                    "**/bower_components": True,
                    "**/*.code-search": True
                },
                "editor.codeLens": True,
                "editor.formatOnSave": True,
                "editor.formatOnPaste": False,
                "editor.rulers": [80, 120],
                "editor.suggestSelection": "first",
                "editor.wordBasedSuggestions": "off"
            },
            non_workspace_mode={
                "debug.enabled": False,
                "editor.formatOnSave": True,
                "editor.formatOnPaste": False,
                "editor.codeLens": False,
                "files.watcherExclude": {},
                "search.exclude": {}
            },
            sync_settings=[
                "editor.formatOnSave",
                "editor.formatOnPaste",
                "editor.rulers",
                "editor.suggestSelection",
                "editor.wordBasedSuggestions"
            ],
            auto_sync=True,
            sync_interval_minutes=60
        )

    def detect_workspace_mode(self) -> WorkspaceState:
        try:
            """
            Detect current workspace mode based on Cursor IDE state.

            Returns:
                WorkspaceState with detected mode
            """
            # Check if we're in a workspace (folder opened)
            has_workspace_folder = (
                self.workspace_settings_path.exists() or
                (self.project_root / ".vscode").exists() or
                (self.project_root / ".git").exists()
            )

            # Determine mode
            if has_workspace_folder:
                mode = WorkspaceMode.WORKSPACE
                workspace_path = self.project_root
                is_debug_mode = True  # Workspace mode is for debugging
            else:
                mode = WorkspaceMode.NON_WORKSPACE
                workspace_path = None
                is_debug_mode = False

            state = WorkspaceState(
                mode=mode,
                workspace_path=workspace_path,
                has_workspace_folder=has_workspace_folder,
                is_debug_mode=is_debug_mode
            )

            self.current_state = state
            logger.info(f"Detected mode: {mode.value}, Debug: {is_debug_mode}")

            return state

        except Exception as e:
            self.logger.error(f"Error in detect_workspace_mode: {e}", exc_info=True)
            raise
    def verify_workflow(self) -> Dict[str, Any]:
        try:
            """
            Verify that workflows, precedence, and operations are correct.

            Returns:
                Verification results with recommendations
            """
            state = self.detect_workspace_mode()

            results = {
                "current_mode": state.mode.value,
                "is_debug_mode": state.is_debug_mode,
                "has_workspace_folder": state.has_workspace_folder,
                "workflow_correct": False,
                "issues": [],
                "recommendations": []
            }

            # Verify workflow correctness
            if state.mode == WorkspaceMode.WORKSPACE:
                # In workspace mode, should have workspace settings
                if not self.workspace_settings_path.exists():
                    results["issues"].append(
                        "Workspace mode detected but no .cursor/settings.json found"
                    )
                    results["recommendations"].append(
                        "Create workspace settings for debugging configuration"
                    )
                else:
                    results["workflow_correct"] = True

            elif state.mode == WorkspaceMode.NON_WORKSPACE:
                # In non-workspace mode, should use user settings
                if not self.user_settings_path.exists():
                    results["issues"].append(
                        "Non-workspace mode but no user settings found"
                    )
                else:
                    results["workflow_correct"] = True

            # Check precedence: Workspace > User > Default
            if state.mode == WorkspaceMode.WORKSPACE:
                workspace_settings = self._load_settings(self.workspace_settings_path)
                user_settings = self._load_settings(self.user_settings_path)

                # Workspace settings should take precedence
                if workspace_settings and user_settings:
                    # Check for conflicting settings
                    conflicts = self._find_setting_conflicts(
                        workspace_settings, user_settings, self.config.sync_settings
                    )
                    if conflicts:
                        results["issues"].append(
                            f"Setting conflicts detected: {', '.join(conflicts)}"
                        )
                        results["recommendations"].append(
                            "Sync settings to resolve conflicts"
                        )

            return results

        except Exception as e:
            self.logger.error(f"Error in verify_workflow: {e}", exc_info=True)
            raise
    def _load_settings(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load settings from JSON file"""
        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load settings from {path}: {e}")
            return None

    def _find_setting_conflicts(
        self,
        workspace_settings: Dict[str, Any],
        user_settings: Dict[str, Any],
        sync_settings: List[str]
    ) -> List[str]:
        """Find conflicts in settings that should be synced"""
        conflicts = []

        for setting in sync_settings:
            workspace_val = self._get_nested_value(workspace_settings, setting)
            user_val = self._get_nested_value(user_settings, setting)

            if workspace_val is not None and user_val is not None:
                if workspace_val != user_val:
                    conflicts.append(setting)

        return conflicts

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = key.split('.')
        value = data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None

        return value

    def _set_nested_value(self, data: Dict[str, Any], key: str, value: Any):
        """Set nested value in dictionary using dot notation"""
        keys = key.split('.')
        current = data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def sync_settings(
        self,
        source_mode: WorkspaceMode,
        target_mode: WorkspaceMode,
        settings: Optional[List[str]] = None
    ) -> bool:
        """
        Sync settings between workspace and non-workspace modes.

        Args:
            source_mode: Source mode to sync from
            target_mode: Target mode to sync to
            settings: List of settings to sync (defaults to config.sync_settings)

        Returns:
            True if sync successful
        """
        if settings is None:
            settings = self.config.sync_settings

        try:
            if source_mode == WorkspaceMode.WORKSPACE:
                source_settings = self._load_settings(self.workspace_settings_path)
                source_config = self.config.workspace_mode
            else:
                source_settings = self._load_settings(self.user_settings_path)
                source_config = self.config.non_workspace_mode

            if target_mode == WorkspaceMode.WORKSPACE:
                target_path = self.workspace_settings_path
                target_settings = self._load_settings(target_path) or {}
            else:
                target_path = self.user_settings_path
                target_settings = self._load_settings(target_path) or {}

            # Sync settings
            synced_count = 0
            for setting in settings:
                # Get value from source config or source settings
                value = None
                if source_config and setting in source_config:
                    value = source_config[setting]
                elif source_settings:
                    value = self._get_nested_value(source_settings, setting)

                if value is not None:
                    self._set_nested_value(target_settings, setting, value)
                    synced_count += 1

            # Save target settings
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(target_settings, f, indent=2)

            logger.info(f"Synced {synced_count} settings from {source_mode.value} to {target_mode.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to sync settings: {e}")
            return False

    def auto_sync_if_needed(self) -> bool:
        try:
            """
            Automatically sync settings if needed based on current mode and config.

            Returns:
                True if sync was performed
            """
            if not self.config.auto_sync:
                return False

            state = self.detect_workspace_mode()

            # Sync workspace -> non-workspace for shared settings
            if state.mode == WorkspaceMode.WORKSPACE:
                # Sync shared settings to user settings
                return self.sync_settings(
                    WorkspaceMode.WORKSPACE,
                    WorkspaceMode.NON_WORKSPACE,
                    self.config.sync_settings
                )
            elif state.mode == WorkspaceMode.NON_WORKSPACE:
                # Optionally sync user -> workspace for when workspace is opened
                # This is less common but can be useful
                if self.workspace_settings_path.exists():
                    return self.sync_settings(
                        WorkspaceMode.NON_WORKSPACE,
                        WorkspaceMode.WORKSPACE,
                        self.config.sync_settings
                    )

            return False

        except Exception as e:
            self.logger.error(f"Error in auto_sync_if_needed: {e}", exc_info=True)
            raise
    def apply_mode_settings(self, mode: WorkspaceMode) -> bool:
        """
        Apply mode-specific settings to current workspace.

        Args:
            mode: Mode to apply settings for

        Returns:
            True if settings applied successfully
        """
        try:
            if mode == WorkspaceMode.WORKSPACE:
                settings_path = self.workspace_settings_path
                mode_config = self.config.workspace_mode
            else:
                settings_path = self.user_settings_path
                mode_config = self.config.non_workspace_mode

            # Load existing settings
            settings = self._load_settings(settings_path) or {}

            # Apply mode-specific settings
            for key, value in mode_config.items():
                self._set_nested_value(settings, key, value)

            # Save settings
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)

            logger.info(f"Applied {mode.value} mode settings")
            return True

        except Exception as e:
            logger.error(f"Failed to apply mode settings: {e}")
            return False

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        state = self.detect_workspace_mode()
        verification = self.verify_workflow()

        return {
            "current_mode": state.mode.value,
            "workspace_path": str(state.workspace_path) if state.workspace_path else None,
            "is_debug_mode": state.is_debug_mode,
            "workflow_correct": verification["workflow_correct"],
            "issues": verification["issues"],
            "recommendations": verification["recommendations"],
            "config": {
                "auto_sync": self.config.auto_sync,
                "sync_interval_minutes": self.config.sync_interval_minutes,
                "sync_settings_count": len(self.config.sync_settings)
            }
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor Workspace Mode Manager")
        parser.add_argument("--detect", action="store_true", help="Detect current workspace mode")
        parser.add_argument("--verify", action="store_true", help="Verify workflow correctness")
        parser.add_argument("--sync", action="store_true", help="Sync settings between modes")
        parser.add_argument("--auto-sync", action="store_true", help="Auto-sync if needed")
        parser.add_argument("--apply-mode", choices=["workspace", "non_workspace"], help="Apply mode-specific settings")
        parser.add_argument("--summary", action="store_true", help="Get workflow summary")

        args = parser.parse_args()

        manager = CursorWorkspaceModeManager()

        if args.detect:
            state = manager.detect_workspace_mode()
            print(f"Mode: {state.mode.value}")
            print(f"Workspace: {state.has_workspace_folder}")
            print(f"Debug Mode: {state.is_debug_mode}")

        if args.verify:
            verification = manager.verify_workflow()
            print(f"Workflow Correct: {verification['workflow_correct']}")
            if verification['issues']:
                print(f"Issues: {verification['issues']}")
            if verification['recommendations']:
                print(f"Recommendations: {verification['recommendations']}")

        if args.sync:
            state = manager.detect_workspace_mode()
            if state.mode == WorkspaceMode.WORKSPACE:
                manager.sync_settings(WorkspaceMode.WORKSPACE, WorkspaceMode.NON_WORKSPACE)
            else:
                manager.sync_settings(WorkspaceMode.NON_WORKSPACE, WorkspaceMode.WORKSPACE)
            print("Settings synced")

        if args.auto_sync:
            synced = manager.auto_sync_if_needed()
            print(f"Auto-sync performed: {synced}")

        if args.apply_mode:
            mode = WorkspaceMode(args.apply_mode.replace("-", "_"))
            manager.apply_mode_settings(mode)
            print(f"Applied {mode.value} mode settings")

        if args.summary:
            summary = manager.get_workflow_summary()
            print(json.dumps(summary, indent=2))

        if not any([args.detect, args.verify, args.sync, args.auto_sync, args.apply_mode, args.summary]):
            # Default: show summary
            summary = manager.get_workflow_summary()
            print(json.dumps(summary, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()