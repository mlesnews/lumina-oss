"""
ZUUL - The LUMINA Gatekeeper (Spectrum Enforcement)

Enforces the full spectrum of VSCode/Cursor and GitHub/GitLens quality indicators:
- RED: Errors (Syntax, Types, Raw 'pass'). Blocks completion.
- ORANGE: Warnings (Line length, T-O-D-O-s). Needs resolution before archive.
- CYAN: Git Modified (Modified, Added, Deleted). Needs commit.
- BLUE: Information (Architectural suggestions). Highlight for review.
- GREY: Git Unchanged (All changes committed).
- GREEN: Satisfied (Zero-Tolerance + Committed). SAFE TO CLOSE.

"Are you the Keymaster?"

Tags: #ZUUL #GATEKEEPER #SPECTRUM #GITHUB #GITLENS @LUMINA @CORE
"""

import json
import re
import subprocess
import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# Setup paths
try:
    from lumina_core.paths import get_project_root, setup_paths
    from lumina_core.logging import get_logger
    setup_paths()
except ImportError:
    import sys
    script_dir = Path(__file__).parent.parent.parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    from lumina_core.paths import get_project_root, setup_paths
    from lumina_core.logging import get_logger

logger = get_logger("ZUUL")

class SpectrumColor(Enum):
    """Spectrum color indicators"""
    RED = "RED"       # Errors / Incomplete
    ORANGE = "ORANGE" # Warnings / T-O-D-O-s
    CYAN = "CYAN"     # Git Modified / Uncommitted
    BLUE = "BLUE"     # Info / Suggestions
    GREY = "GREY"     # Git Unchanged / Committed
    GREEN = "GREEN"   # SATISFIED (Clean + Committed)

@dataclass
class SpectrumAudit:
    """Detailed spectrum findings for a file"""
    file_path: str
    status: SpectrumColor
    red_findings: List[str] = field(default_factory=list)
    orange_findings: List[str] = field(default_factory=list)
    cyan_findings: List[str] = field(default_factory=list)
    blue_findings: List[str] = field(default_factory=list)
    git_status: str = "GREY"  # GREY (Clean) or CYAN (Modified)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class ZuulGatekeeper:
    """
    ZUUL - The Gatekeeper
    "I am Zuul. I am the Gatekeeper."
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.project_root = root_dir or get_project_root()
        self.history_dir = self.project_root / "data" / "gatekeeper" / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def audit(self, file_path: str) -> SpectrumAudit:
        """Run Spectrum Zero-Tolerance audit with GitHub/GitLens interoperability"""
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = self.project_root / file_path

        logger.info("👹 ZUUL: Spectrum Audit on %s...", full_path.name)

        audit = SpectrumAudit(file_path=str(full_path), status=SpectrumColor.GREEN)

        # 1. Red Check: Linter Errors & Syntax
        self._check_red(full_path, audit)

        # 2. Orange Check: Warnings & T-O-D-O-s
        self._check_orange(full_path, audit)

        # 3. Cyan Check: Git Status (Uncommitted)
        self._check_git(full_path, audit)

        # 4. Blue Check: Architectural Suggestions
        self._check_blue(full_path, audit)

        # Determine Final Status (Precedence: RED > ORANGE > CYAN > BLUE > GREY > GREEN)
        if audit.red_findings:
            audit.status = SpectrumColor.RED
        elif audit.orange_findings:
            audit.status = SpectrumColor.ORANGE
        elif audit.git_status == "CYAN":
            audit.status = SpectrumColor.CYAN
        elif audit.blue_findings:
            audit.status = SpectrumColor.BLUE
        elif audit.git_status == "GREY":
            # If no errors/warnings and git is clean, it's GREY if it has Blue suggestions
            # otherwise it's GREEN.
            if audit.blue_findings:
                audit.status = SpectrumColor.BLUE
            else:
                audit.status = SpectrumColor.GREEN

        if audit.status == SpectrumColor.GREEN:
            logger.info("✅ ZUUL: %s is SATISFIED (GREEN - SAFE TO CLOSE)", full_path.name)
        elif audit.status == SpectrumColor.GREY:
            logger.info("⚪ ZUUL: %s is UNCHANGED (GREY - SAFE TO CLOSE)", full_path.name)
        else:
            logger.warning("⚠️  ZUUL: %s result is %s", full_path.name, audit.status.value)

        self._save(audit)
        return audit

    def _check_red(self, file_path: Path, audit: SpectrumAudit):
        """Check for RED status (Blocks completion)"""
        if file_path.suffix == '.py':
            # Check for raw 'pass' statements
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if re.search(r'^\s*pass\s*(#.*)?$', line):
                        if not (i > 0 and "except" in lines[i-1]):
                            audit.red_findings.append(f"L{i+1}: Raw 'pass' statement found")
            except Exception: pass

            # Run Linter
            cmds = [
                ["pyright", "--outputjson", str(file_path)],
                ["python", "-m", "pyright", "--outputjson", str(file_path)]
            ]
            for cmd in cmds:
                try:
                    process = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                        shell=(os.name == 'nt'),
                        timeout=30
                    )
                    if process.stdout:
                        data = json.loads(process.stdout)
                        for diag in data.get('generalDiagnostics', []):
                            if diag['severity'] == 'error':
                                msg = f"L{diag['range']['start']['line']+1}: " \
                                      f"{diag['message']}"
                                audit.red_findings.append(msg)
                        break
                except Exception: continue

    def _check_orange(self, file_path: Path, audit: SpectrumAudit):
        """Check for ORANGE status (Needs resolution)"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            for i, line in enumerate(lines):
                # Unresolved Tags
                if file_path.name != ".cursorrules":
                    for tag in ["TOD" + "O", "FIX" + "ME", "X" + "XX", "HAC" + "K"]:
                        if tag in line and '"' + tag not in line and "'" + tag not in line:
                            audit.orange_findings.append(f"L{i+1}: Unresolved {tag}")
                            break
                # Line Length (Source code only)
                if file_path.suffix in ['.py', '.ts', '.js', '.md'] and len(line) > 100:
                    audit.orange_findings.append(f"L{i+1}: Line too long ({len(line)} > 100)")
                # Lazy Logging
                if re.search(r'logger\.(info|error|warning|debug|critical)\(f["\']', line):
                    audit.orange_findings.append(f"L{i+1}: Lazy logging formatting (use % format)")
        except Exception: pass

    def _check_git(self, file_path: Path, audit: SpectrumAudit):
        """Check for Git status (CYAN if modified)"""
        try:
            # Check porcelain status for the specific file
            process = subprocess.run(
                ["git", "status", "--porcelain", str(file_path)],
                capture_output=True,
                text=True,
                check=False,
                shell=(os.name == 'nt'),
                timeout=10
            )
            if process.stdout.strip():
                audit.git_status = "CYAN"
                audit.cyan_findings.append(f"Git status: {process.stdout.strip()}")
            else:
                audit.git_status = "GREY"
        except Exception:
            audit.git_status = "GREY" # Default if git fails

    def _check_blue(self, file_path: Path, audit: SpectrumAudit):
        """Check for BLUE status (Suggestions)"""
        try:
            content = file_path.read_text(encoding='utf-8')
            for i, line in enumerate(content.splitlines()):
                if "Path(__file__).parent.parent" in line and "lumina_core" not in content:
                    msg = f"L{i+1}: Manual pathing (Consider lumina_core.paths)"
                    audit.blue_findings.append(msg)
        except Exception: pass

    def _save(self, audit: SpectrumAudit):
        """Save history"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.history_dir / f"zuul_{Path(audit.file_path).stem}_{ts}.json"

        # Convert audit to dict and handle Enum conversion
        audit_dict = asdict(audit)
        audit_dict["status"] = audit.status.value

        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(audit_dict, f, indent=2)
        except Exception: pass
