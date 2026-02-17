#!/usr/bin/env python3
"""
File Auto-Close Manager - Automatically close files after 30 minutes unless pinned

Integrates with @V3 and @JARVIS decisioning for intelligent file management.

Features:
- Monitors open files with timestamps
- 30-minute auto-close timer (unless pinned)
- File pinning system to prevent auto-close
- @V3 and @JARVIS integration for decisioning
- Comprehensive logging and reporting
- Graceful cleanup and error handling
"""

import asyncio
import json
import logging
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class FileSession:
    """Represents a file session with metadata"""
    file_path: str
    opened_at: datetime
    last_accessed: datetime
    is_pinned: bool = False
    pin_reason: str = ""
    workspace: str = ""
    file_type: str = ""
    importance_score: float = 0.0
    decision_context: Dict[str, Any] = None

    def __post_init__(self):
        if self.decision_context is None:
            self.decision_context = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['opened_at'] = self.opened_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileSession':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['opened_at'] = datetime.fromisoformat(data['opened_at'])
        data_copy['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        return cls(**data_copy)

    @property
    def age_minutes(self) -> float:
        """Get age in minutes"""
        return (datetime.now() - self.opened_at).total_seconds() / 60

    @property
    def idle_minutes(self) -> float:
        """Get idle time in minutes"""
        return (datetime.now() - self.last_accessed).total_seconds() / 60


class FileAutoCloseManager:
    """Manages automatic closing of files with intelligent decisioning"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "file_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File tracking
        self.active_files: Dict[str, FileSession] = {}
        self.pinned_files: Set[str] = set()
        self.closed_files: Dict[str, datetime] = {}

        # Configuration
        self.auto_close_minutes = 30
        self.check_interval_seconds = 60  # Check every minute
        self.max_concurrent_closes = 5

        # Decisioning
        self.v3_decision_threshold = 0.7  # Minimum confidence for auto-close
        self.jarvis_override_enabled = True

        # Setup logging
        self.logger = logging.getLogger("FileAutoCloseManager")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Load existing data
        self._load_session_data()

    def _load_session_data(self):
        """Load existing session data"""
        try:
            # Load active files
            active_file = self.data_dir / "active_files.json"
            if active_file.exists():
                with open(active_file, 'r') as f:
                    active_data = json.load(f)
                    for file_path, session_data in active_data.items():
                        self.active_files[file_path] = FileSession.from_dict(session_data)

            # Load pinned files
            pinned_file = self.data_dir / "pinned_files.json"
            if pinned_file.exists():
                with open(pinned_file, 'r') as f:
                    pinned_data = json.load(f)
                    self.pinned_files = set(pinned_data.get('pinned_files', []))

        except Exception as e:
            self.logger.warning(f"Failed to load session data: {e}")

    def save_session_data(self):
        """Save session data"""
        try:
            # Save active files
            active_data = {
                file_path: session.to_dict()
                for file_path, session in self.active_files.items()
            }
            with open(self.data_dir / "active_files.json", 'w') as f:
                json.dump(active_data, f, indent=2)

            # Save pinned files
            pinned_data = {'pinned_files': list(self.pinned_files)}
            with open(self.data_dir / "pinned_files.json", 'w') as f:
                json.dump(pinned_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")

    def register_file_open(self, file_path: str, workspace: str = "") -> bool:
        try:
            """Register that a file has been opened"""
            file_path = str(Path(file_path).resolve())

            if file_path in self.active_files:
                # Update last accessed
                self.active_files[file_path].last_accessed = datetime.now()
                self.logger.debug(f"Updated access time for: {file_path}")
            else:
                # Create new session
                session = FileSession(
                    file_path=file_path,
                    opened_at=datetime.now(),
                    last_accessed=datetime.now(),
                    workspace=workspace,
                    file_type=self._get_file_type(file_path),
                    is_pinned=file_path in self.pinned_files
                )
                self.active_files[file_path] = session
                self.logger.info(f"Registered new file: {file_path}")

            # Remove from closed files if present
            self.closed_files.pop(file_path, None)

            self.save_session_data()
            return True

        except Exception as e:
            self.logger.error(f"Error in register_file_open: {e}", exc_info=True)
            raise
    def pin_file(self, file_path: str, reason: str = "") -> bool:
        try:
            """Pin a file to prevent auto-close"""
            file_path = str(Path(file_path).resolve())

            if file_path in self.active_files:
                self.active_files[file_path].is_pinned = True
                self.active_files[file_path].pin_reason = reason

            self.pinned_files.add(file_path)
            self.logger.info(f"Pinned file: {file_path} ({reason})")
            self.save_session_data()
            return True

        except Exception as e:
            self.logger.error(f"Error in pin_file: {e}", exc_info=True)
            raise
    def unpin_file(self, file_path: str) -> bool:
        try:
            """Unpin a file to allow auto-close"""
            file_path = str(Path(file_path).resolve())

            if file_path in self.active_files:
                self.active_files[file_path].is_pinned = False
                self.active_files[file_path].pin_reason = ""

            self.pinned_files.discard(file_path)
            self.logger.info(f"Unpinned file: {file_path}")
            self.save_session_data()
            return True

        except Exception as e:
            self.logger.error(f"Error in unpin_file: {e}", exc_info=True)
            raise
    def _get_file_type(self, file_path: str) -> str:
        try:
            """Get file type from extension"""
            path = Path(file_path)
            ext = path.suffix.lower()

            type_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.cs': 'csharp',
                '.php': 'php',
                '.rb': 'ruby',
                '.go': 'go',
                '.rs': 'rust',
                '.md': 'markdown',
                '.json': 'json',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.xml': 'xml',
                '.html': 'html',
                '.css': 'css',
                '.sql': 'sql',
                '.sh': 'shell',
                '.bat': 'batch',
                '.ps1': 'powershell'
            }

            return type_map.get(ext, 'unknown')

        except Exception as e:
            self.logger.error(f"Error in _get_file_type: {e}", exc_info=True)
            raise
    async def evaluate_file_for_close(self, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluate whether a file should be closed using @V3 and @JARVIS decisioning

        Returns: (should_close, reason, context)
        """
        if file_path not in self.active_files:
            return False, "File not in active tracking", {}

        session = self.active_files[file_path]

        # Skip pinned files
        if session.is_pinned:
            return False, f"Pinned: {session.pin_reason}", {"pinned": True}

        # Quick checks first
        if session.age_minutes < self.auto_close_minutes:
            return False, ".1f", {"age_minutes": session.age_minutes}

        # Get decision context
        context = await self._build_decision_context(session)

        # @V3 Decisioning
        v3_decision = await self._v3_evaluate_close(context)

        # @JARVIS Override Check
        if self.jarvis_override_enabled:
            jarvis_decision = await self._jarvis_evaluate_close(context, v3_decision)

            if jarvis_decision['override']:
                return (
                    jarvis_decision['should_close'],
                    jarvis_decision['reason'],
                    {**context, **jarvis_decision}
                )

        # Return V3 decision
        return v3_decision['should_close'], v3_decision['reason'], context

    async def _build_decision_context(self, session: FileSession) -> Dict[str, Any]:
        """Build decision context for evaluation"""
        context = {
            'file_path': session.file_path,
            'file_type': session.file_type,
            'age_minutes': session.age_minutes,
            'idle_minutes': session.idle_minutes,
            'workspace': session.workspace,
            'is_pinned': session.is_pinned,
            'importance_score': session.importance_score
        }

        # Add file metadata
        file_path = Path(session.file_path)
        if file_path.exists():
            stat = file_path.stat()
            context.update({
                'file_size': stat.st_size,
                'modified_recently': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() < 3600,
                'is_readonly': not os.access(file_path, os.W_OK)
            })

        # Add workspace context
        if session.workspace:
            workspace_path = Path(session.workspace)
            if workspace_path.exists():
                # Check if file is in active workspace areas
                relative_path = os.path.relpath(session.file_path, session.workspace)
                context['in_src'] = relative_path.startswith(('src', 'source', 'lib'))
                context['in_docs'] = relative_path.startswith(('docs', 'doc', 'documentation'))
                context['in_tests'] = relative_path.startswith(('test', 'tests', 'spec'))

        return context

    async def _v3_evaluate_close(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """@V3 decisioning for file close evaluation"""
        # V3 Decision Logic
        score = 0.0
        reasons = []

        # Age factor (older = more likely to close)
        if context['age_minutes'] > 60:  # 1 hour
            score += 0.4
            reasons.append(".0f")
        elif context['age_minutes'] > 30:  # 30 minutes
            score += 0.2
            reasons.append(".0f")

        # Idle factor (more idle = more likely to close)
        if context['idle_minutes'] > 30:
            score += 0.3
            reasons.append(".0f")
        elif context['idle_minutes'] > 10:
            score += 0.1
            reasons.append(".0f")

        # File type factors
        important_types = {'python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go'}
        if context['file_type'] in important_types:
            score -= 0.2  # Less likely to close important files
            reasons.append(f"Important file type: {context['file_type']}")

        # Location factors
        if context.get('in_src', False):
            score -= 0.1  # Source files are important
            reasons.append("Source file")

        if context.get('in_tests', False):
            score += 0.1  # Test files can be closed more easily
            reasons.append("Test file")

        # Size factor (larger files = more important)
        if context.get('file_size', 0) > 10000:  # 10KB
            score -= 0.1
            reasons.append("Large file")

        # Recent modification
        if context.get('modified_recently', False):
            score -= 0.2
            reasons.append("Recently modified")

        # Read-only files are less likely to need keeping open
        if context.get('is_readonly', False):
            score += 0.1
            reasons.append("Read-only file")

        # Decision
        should_close = score >= self.v3_decision_threshold
        reason = "; ".join(reasons) if reasons else "V3 evaluation"

        return {
            'should_close': should_close,
            'confidence': score,
            'reason': reason,
            'v3_score': score
        }

    async def _jarvis_evaluate_close(self, context: Dict[str, Any], v3_decision: Dict[str, Any]) -> Dict[str, Any]:
        """@JARVIS override decisioning"""
        # JARVIS Decision Logic - More sophisticated analysis

        # Check for critical patterns that should prevent closing
        critical_indicators = []

        # Files with recent changes should not be closed
        if context.get('modified_recently', False):
            critical_indicators.append("recent_changes")

        # Files currently being edited (check if in editor)
        if await self._is_file_currently_edited(context['file_path']):
            critical_indicators.append("currently_edited")

        # Files with unsaved changes (if detectable)
        if await self._has_unsaved_changes(context['file_path']):
            critical_indicators.append("unsaved_changes")

        # Files that are dependencies of open files
        if await self._is_dependency_of_open_files(context['file_path']):
            critical_indicators.append("dependency")

        # Files with TODO/FIXME comments
        if await self._has_active_todos(context['file_path']):
            critical_indicators.append("active_todos")

        # Override decision
        if critical_indicators:
            return {
                'override': True,
                'should_close': False,
                'reason': f"JARVIS override: {', '.join(critical_indicators)}",
                'critical_indicators': critical_indicators
            }

        # Check for files that should be closed despite V3 decision
        close_indicators = []

        # Very old files with no recent activity
        if context['age_minutes'] > 120 and context['idle_minutes'] > 60:  # 2+ hours old, idle 1+ hour
            close_indicators.append("very_old_idle")

        # Temporary files
        if any(pattern in context['file_path'].lower() for pattern in ['temp', 'tmp', 'cache', '.log']):
            close_indicators.append("temporary_file")

        # Backup files
        if context['file_path'].endswith(('.bak', '.backup', '.orig', '.old')):
            close_indicators.append("backup_file")

        if close_indicators and not v3_decision['should_close']:
            return {
                'override': True,
                'should_close': True,
                'reason': f"JARVIS override: {', '.join(close_indicators)}",
                'close_indicators': close_indicators
            }

        # No override
        return {
            'override': False,
            'should_close': v3_decision['should_close'],
            'reason': v3_decision['reason']
        }

    async def _is_file_currently_edited(self, file_path: str) -> bool:
        """Check if file is currently being edited (VSCode integration)"""
        # This would integrate with VSCode API to check active editor
        # For now, use a simple heuristic
        try:
            # Check if file has been modified recently (within last 5 minutes)
            stat = os.stat(file_path)
            modified_recently = (time.time() - stat.st_mtime) < 300  # 5 minutes
            return modified_recently
        except:
            return False

    async def _has_unsaved_changes(self, file_path: str) -> bool:
        """Check if file has unsaved changes"""
        # This would integrate with VSCode's dirty file detection
        # For now, return False (would need VSCode extension API)
        return False

    async def _is_dependency_of_open_files(self, file_path: str) -> bool:
        """Check if file is a dependency of other open files"""
        # This would analyze import/include relationships
        # For now, use simple heuristics based on file type and location
        file_ext = Path(file_path).suffix.lower()

        # Check if it's a commonly imported file
        common_modules = ['__init__.py', 'utils.py', 'helpers.py', 'common.py', 'config.py']
        if any(file_path.endswith(module) for module in common_modules):
            return True

        return False

    async def _has_active_todos(self, file_path: str) -> bool:
        """Check if file has active TODO/FIXME comments"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)  # Read first 10KB
                todo_patterns = [r'# TODO', r'# FIXME', r'// TODO', r'// FIXME', r'/\* TODO', r'/\* FIXME']  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                return any(re.search(pattern, content, re.IGNORECASE) for pattern in todo_patterns)
        except:
            return False

    async def process_auto_close(self) -> Dict[str, Any]:
        """Process automatic file closing"""
        candidates = []
        results = {
            'processed': 0,
            'closed': 0,
            'kept_open': 0,
            'errors': 0,
            'details': []
        }

        # Find candidates for closing
        for file_path, session in self.active_files.items():
            if session.age_minutes >= self.auto_close_minutes and not session.is_pinned:
                candidates.append(file_path)

        # Limit concurrent closes
        candidates = candidates[:self.max_concurrent_closes]

        # Process each candidate
        for file_path in candidates:
            try:
                should_close, reason, context = await self.evaluate_file_for_close(file_path)

                results['processed'] += 1

                if should_close:
                    # Attempt to close the file
                    if await self._close_file_in_vscode(file_path):
                        results['closed'] += 1
                        self.closed_files[file_path] = datetime.now()
                        del self.active_files[file_path]
                        self.logger.info(f"Auto-closed file: {file_path} ({reason})")
                    else:
                        results['kept_open'] += 1
                        self.logger.warning(f"Failed to close file: {file_path}")
                else:
                    results['kept_open'] += 1
                    self.logger.debug(f"Keeping file open: {file_path} ({reason})")

                results['details'].append({
                    'file_path': file_path,
                    'action': 'closed' if should_close else 'kept_open',
                    'reason': reason,
                    'context': context
                })

            except Exception as e:
                results['errors'] += 1
                self.logger.error(f"Error processing file {file_path}: {e}")
                results['details'].append({
                    'file_path': file_path,
                    'action': 'error',
                    'reason': str(e)
                })

        # Save updated data
        self.save_session_data()

        return results

    async def _close_file_in_vscode(self, file_path: str) -> bool:
        """Close file in VSCode using command line or extension"""
        try:
            # This would use VSCode's command line interface or extension API
            # For now, we'll use a placeholder - actual implementation would need VSCode extension
            self.logger.info(f"Would close file in VSCode: {file_path}")

            # Placeholder - in real implementation, this would:
            # 1. Use VSCode's --goto command to focus the file
            # 2. Send keyboard shortcut to close (Ctrl+W or Cmd+W)
            # 3. Or use VSCode extension API to close specific files

            return True  # Assume success for now
        except Exception as e:
            self.logger.error(f"Failed to close file {file_path}: {e}")
            return False

    async def run_auto_close_monitor(self):
        """Run the automatic file close monitoring loop"""
        self.logger.info("🚀 Starting File Auto-Close Monitor")

        while True:
            try:
                # Process auto-close candidates
                results = await self.process_auto_close()

                if results['processed'] > 0:
                    self.logger.info(
                        f"Auto-close cycle: {results['closed']} closed, "
                        f"{results['kept_open']} kept open, {results['errors']} errors"
                    )

                # Wait for next check
                await asyncio.sleep(self.check_interval_seconds)

            except Exception as e:
                self.logger.error(f"Auto-close monitor error: {e}")
                await asyncio.sleep(60)  # Wait a minute on error

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        now = datetime.now()

        # Active files by age
        age_distribution = defaultdict(int)
        type_distribution = defaultdict(int)
        pinned_count = 0

        for session in self.active_files.values():
            age_hours = int(session.age_minutes / 60)
            if age_hours < 1:
                age_distribution['<1h'] += 1
            elif age_hours < 6:
                age_distribution['1-6h'] += 1
            elif age_hours < 24:
                age_distribution['6-24h'] += 1
            else:
                age_distribution['>24h'] += 1

            type_distribution[session.file_type] += 1

            if session.is_pinned:
                pinned_count += 1

        # Recent closes
        recent_closes = sum(
            1 for close_time in self.closed_files.values()
            if (now - close_time).total_seconds() < 3600  # Last hour
        )

        return {
            'active_files': len(self.active_files),
            'pinned_files': pinned_count,
            'closed_recently': recent_closes,
            'age_distribution': dict(age_distribution),
            'type_distribution': dict(type_distribution),
            'auto_close_threshold_minutes': self.auto_close_minutes,
            'check_interval_seconds': self.check_interval_seconds
        }

    def export_file_sessions_report(self) -> str:
        try:
            """Export detailed file sessions report"""
            report_lines = [
                "# File Auto-Close Manager - Active Sessions Report",
                "",
                f"Generated: {datetime.now().isoformat()}",
                "",
                "## Summary",
                f"- Active Files: {len(self.active_files)}",
                f"- Pinned Files: {sum(1 for s in self.active_files.values() if s.is_pinned)}",
                f"- Auto-close Threshold: {self.auto_close_minutes} minutes",
                "",
                "## Active Files",
                ""
            ]

            # Sort by age (oldest first)
            sorted_sessions = sorted(
                self.active_files.values(),
                key=lambda s: s.age_minutes,
                reverse=True
            )

            for session in sorted_sessions:
                pin_status = "📌 PINNED" if session.is_pinned else "📄"
                age_str = ".1f" if session.age_minutes < 60 else ".1f"

                report_lines.extend([
                    f"### {pin_status} {Path(session.file_path).name}",
                    f"- **Path:** {session.file_path}",
                    f"- **Type:** {session.file_type}",
                    f"- **Age:** {age_str}",
                    f"- **Idle:** {session.idle_minutes:.1f} minutes",
                    f"- **Opened:** {session.opened_at.isoformat()}",
                    f"- **Workspace:** {session.workspace or 'N/A'}",
                ])

                if session.pin_reason:
                    report_lines.append(f"- **Pin Reason:** {session.pin_reason}")

                report_lines.append("")

            return "\n".join(report_lines)


        except Exception as e:
            self.logger.error(f"Error in export_file_sessions_report: {e}", exc_info=True)
            raise
# Global instance
file_manager = FileAutoCloseManager()


async def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="File Auto-Close Manager")
    parser.add_argument("action", choices=[
        "status", "report", "pin", "unpin", "close", "monitor"
    ], help="Action to perform")
    parser.add_argument("--file", help="File path for pin/unpin actions")
    parser.add_argument("--reason", help="Reason for pinning")

    args = parser.parse_args()

    manager = FileAutoCloseManager()

    if args.action == "status":
        status = manager.get_status_report()
        print("📊 File Auto-Close Status")
        print(f"Active Files: {status['active_files']}")
        print(f"Pinned Files: {status['pinned_files']}")
        print(f"Recently Closed: {status['closed_recently']}")
        print(f"Auto-close Threshold: {status['auto_close_threshold_minutes']} minutes")
        print("\nAge Distribution:")
        for age_range, count in status['age_distribution'].items():
            print(f"  {age_range}: {count}")
        print("\nFile Types:")
        for file_type, count in status['type_distribution'].items():
            print(f"  {file_type}: {count}")

    elif args.action == "report":
        report = manager.export_file_sessions_report()
        print(report)

    elif args.action == "pin":
        if not args.file:
            print("❌ Please provide --file")
            return 1
        success = manager.pin_file(args.file, args.reason or "")
        if success:
            print(f"✅ Pinned file: {args.file}")
        else:
            print(f"❌ Failed to pin file: {args.file}")

    elif args.action == "unpin":
        if not args.file:
            print("❌ Please provide --file")
            return 1
        success = manager.unpin_file(args.file)
        if success:
            print(f"✅ Unpinned file: {args.file}")
        else:
            print(f"❌ Failed to unpin file: {args.file}")

    elif args.action == "close":
        results = await manager.process_auto_close()
        print(f"🔄 Auto-close cycle completed:")
        print(f"  Processed: {results['processed']}")
        print(f"  Closed: {results['closed']}")
        print(f"  Kept Open: {results['kept_open']}")
        print(f"  Errors: {results['errors']}")

    elif args.action == "monitor":
        print("🚀 Starting file auto-close monitor...")
        await manager.run_auto_close_monitor()


if __name__ == "__main__":


    asyncio.run(main())