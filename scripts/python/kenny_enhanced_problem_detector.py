#!/usr/bin/env python3
"""
Kenny Enhanced Problem Detector (Priority 4)
Enhanced problem detection with VLM-based location detection,
more problem sources (IDE, terminal, system), and better reaction system.

Tags: #KENNY #PRIORITY4 #PROBLEM_DETECTION #VLM @JARVIS @LUMINA
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KennyProblemDetector")

# VLM Integration
try:
    from vlm_integration import VLMIntegration
    VLM_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False
    VLMIntegration = None

class ProblemType(Enum):
    """Types of problems Kenny can detect"""
    IDE_ERROR = "ide_error"
    TERMINAL_ERROR = "terminal_error"
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    FILE_ERROR = "file_error"
    PERFORMANCE_ISSUE = "performance_issue"
    UNKNOWN = "unknown"

@dataclass
class Problem:
    """Represents a detected problem"""
    problem_type: ProblemType
    source: str  # IDE, Terminal, System, etc.
    message: str
    location: Optional[Tuple[int, int]] = None  # Screen coordinates (x, y)
    severity: str = "normal"  # low, normal, high, critical
    timestamp: float = 0.0
    detected_by: str = "unknown"  # vlm, file_monitor, etc.

class KennyEnhancedProblemDetector:
    """
    Priority 4: Enhanced Problem Detection
    - VLM-based location detection
    - More problem sources (IDE, terminal, system)
    - Better reaction system
    """

    def __init__(self, project_root: Path, vlm: Optional[VLMIntegration] = None):
        self.project_root = project_root
        self.vlm = vlm
        self.problems: List[Problem] = []
        self.last_check_time = time.time()
        self.check_interval = 5.0  # Check every 5 seconds

        # Problem source paths
        self.ide_log_paths = [
            project_root / "logs" / "cursor_ide.log",
            project_root / "logs" / "cursor_error.log",
        ]
        self.terminal_log_paths = [
            project_root / "logs" / "terminal.log",
            project_root / "logs" / "command.log",
        ]
        self.system_log_paths = [
            project_root / "logs" / "system.log",
            project_root / "logs" / "error.log",
        ]

        # File monitoring
        self.last_file_sizes = {}
        self.last_file_mtimes = {}

        # VLM screen analysis
        self.vlm_enabled = vlm is not None and VLM_AVAILABLE
        self.last_vlm_check = time.time()
        self.vlm_check_interval = 30.0  # VLM check every 30 seconds (more expensive)

        logger.info("✅ Enhanced Problem Detector initialized")
        if self.vlm_enabled:
            logger.info("   VLM-based location detection: ENABLED")
        else:
            logger.info("   VLM-based location detection: DISABLED (VLM not available)")

    def detect_problems(self) -> List[Problem]:
        """
        Detect problems from all sources
        Returns list of detected problems
        """
        current_time = time.time()

        # Only check periodically
        if current_time - self.last_check_time < self.check_interval:
            return []

        self.last_check_time = current_time
        new_problems = []

        # Check IDE errors
        ide_problems = self._check_ide_errors()
        new_problems.extend(ide_problems)

        # Check terminal errors
        terminal_problems = self._check_terminal_errors()
        new_problems.extend(terminal_problems)

        # Check system errors
        system_problems = self._check_system_errors()
        new_problems.extend(system_problems)

        # Check file errors
        file_problems = self._check_file_errors()
        new_problems.extend(file_problems)

        # VLM-based screen analysis (less frequent, more expensive)
        if self.vlm_enabled and (current_time - self.last_vlm_check) >= self.vlm_check_interval:
            vlm_problems = self._check_vlm_screen_analysis()
            new_problems.extend(vlm_problems)
            self.last_vlm_check = current_time

        # Add to problems list
        self.problems.extend(new_problems)

        # Keep only recent problems (last 10 minutes)
        cutoff_time = current_time - 600
        self.problems = [p for p in self.problems if p.timestamp > cutoff_time]

        return new_problems

    def _check_ide_errors(self) -> List[Problem]:
        """Check for IDE errors (Cursor, VS Code, etc.)"""
        problems = []

        for log_path in self.ide_log_paths:
            if not log_path.exists():
                continue

            try:
                # Check if file was modified recently
                mtime = log_path.stat().st_mtime
                if mtime in self.last_file_mtimes.values():
                    continue  # Already checked

                # Read recent lines
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-50:]  # Last 50 lines

                # Look for error patterns
                for line in recent_lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['error', 'exception', 'failed', 'crash', 'fatal']):
                        problem = Problem(
                            problem_type=ProblemType.IDE_ERROR,
                            source="IDE",
                            message=line.strip()[:200],  # Truncate long messages
                            severity=self._determine_severity(line),
                            timestamp=time.time(),
                            detected_by="file_monitor"
                        )
                        problems.append(problem)
                        logger.debug(f"🔍 IDE error detected: {problem.message[:50]}...")

                self.last_file_mtimes[log_path] = mtime

            except Exception as e:
                logger.debug(f"Could not check IDE log {log_path}: {e}")

        return problems

    def _check_terminal_errors(self) -> List[Problem]:
        """Check for terminal errors"""
        problems = []

        for log_path in self.terminal_log_paths:
            if not log_path.exists():
                continue

            try:
                mtime = log_path.stat().st_mtime
                if mtime in self.last_file_mtimes.values():
                    continue

                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-50:]

                for line in recent_lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['error', 'failed', 'exception', 'traceback']):
                        problem = Problem(
                            problem_type=ProblemType.TERMINAL_ERROR,
                            source="Terminal",
                            message=line.strip()[:200],
                            severity=self._determine_severity(line),
                            timestamp=time.time(),
                            detected_by="file_monitor"
                        )
                        problems.append(problem)
                        logger.debug(f"🔍 Terminal error detected: {problem.message[:50]}...")

                self.last_file_mtimes[log_path] = mtime

            except Exception as e:
                logger.debug(f"Could not check terminal log {log_path}: {e}")

        return problems

    def _check_system_errors(self) -> List[Problem]:
        """Check for system errors"""
        problems = []

        for log_path in self.system_log_paths:
            if not log_path.exists():
                continue

            try:
                mtime = log_path.stat().st_mtime
                if mtime in self.last_file_mtimes.values():
                    continue

                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-50:]

                for line in recent_lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in ['error', 'critical', 'fatal', 'panic']):
                        problem = Problem(
                            problem_type=ProblemType.SYSTEM_ERROR,
                            source="System",
                            message=line.strip()[:200],
                            severity=self._determine_severity(line),
                            timestamp=time.time(),
                            detected_by="file_monitor"
                        )
                        problems.append(problem)
                        logger.debug(f"🔍 System error detected: {problem.message[:50]}...")

                self.last_file_mtimes[log_path] = mtime

            except Exception as e:
                logger.debug(f"Could not check system log {log_path}: {e}")

        return problems

    def _check_file_errors(self) -> List[Problem]:
        """Check for file access errors"""
        problems = []

        # Check for common error files
        error_files = [
            self.project_root / "data" / "cursor_error_handling" / "error_*.json",
            self.project_root / "data" / "diagnostics" / "*.json",
        ]

        # This is a simplified check - in production, use glob patterns
        try:
            error_dir = self.project_root / "data" / "cursor_error_handling"
            if error_dir.exists():
                for error_file in error_dir.glob("error_*.json"):
                    mtime = error_file.stat().st_mtime
                    if error_file not in self.last_file_mtimes:
                        # New error file detected
                        try:
                            with open(error_file, 'r') as f:
                                error_data = json.load(f)
                                message = error_data.get("message", "Unknown error")

                                problem = Problem(
                                    problem_type=ProblemType.FILE_ERROR,
                                    source="File System",
                                    message=message[:200],
                                    severity="high",
                                    timestamp=time.time(),
                                    detected_by="file_monitor"
                                )
                                problems.append(problem)
                                logger.debug(f"🔍 File error detected: {error_file.name}")
                        except:
                            pass

                        self.last_file_mtimes[error_file] = mtime
        except Exception as e:
            logger.debug(f"Could not check file errors: {e}")

        return problems

    def _check_vlm_screen_analysis(self) -> List[Problem]:
        """
        Priority 4: VLM-based screen analysis for problem location detection
        Uses VLM to analyze screen and detect problem locations
        """
        if not self.vlm_enabled or not self.vlm:
            return []

        problems = []

        try:
            # Capture screen (simplified - in production, use proper screen capture)
            # For now, we'll use VLM to analyze if we have a screenshot

            # This is a placeholder - actual implementation would:
            # 1. Capture screen screenshot
            # 2. Send to VLM with prompt: "Find any error messages, warnings, or problems on this screen"
            # 3. Parse VLM response for problem locations and descriptions
            # 4. Return problems with screen coordinates

            # Example VLM prompt:
            # "Analyze this screenshot and identify any error messages, warnings, or problems.
            #  For each problem, provide: (1) description, (2) approximate screen coordinates (x, y),
            #  (3) severity level (low/normal/high/critical)."

            logger.debug("🔍 VLM screen analysis: (placeholder - requires screen capture)")

            # In production, this would be:
            # screenshot = capture_screen()
            # vlm_response = self.vlm.analyze_image(screenshot, prompt)
            # problems = parse_vlm_response(vlm_response)

        except Exception as e:
            logger.debug(f"VLM screen analysis failed: {e}")

        return problems

    def _determine_severity(self, message: str) -> str:
        """Determine problem severity from message"""
        message_lower = message.lower()

        if any(keyword in message_lower for keyword in ['critical', 'fatal', 'panic', 'crash']):
            return "critical"
        elif any(keyword in message_lower for keyword in ['error', 'failed', 'exception']):
            return "high"
        elif any(keyword in message_lower for keyword in ['warning', 'warn']):
            return "normal"
        else:
            return "low"

    def get_recent_problems(self, minutes: int = 5) -> List[Problem]:
        """Get problems from the last N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        return [p for p in self.problems if p.timestamp > cutoff_time]

    def get_problems_by_type(self, problem_type: ProblemType) -> List[Problem]:
        """Get problems of a specific type"""
        return [p for p in self.problems if p.problem_type == problem_type]

    def clear_old_problems(self, minutes: int = 10):
        """Clear problems older than N minutes"""
        cutoff_time = time.time() - (minutes * 60)
        self.problems = [p for p in self.problems if p.timestamp > cutoff_time]
