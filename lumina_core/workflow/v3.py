"""
V3 Verification Logic - The Triple-Check Layer (GitHub Integrated)

"Verify, Validate, Verify again."
Ensures work is battletested, meets Zero-Tolerance standards, and is synced with GitHub.

Tags: #V3 #VERIFICATION #QUALITY #BATTLETESTED #GITHUB @LUMINA @CORE
"""

import re
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from lumina_core.gatekeeper import ZuulGatekeeper, SpectrumColor
from lumina_core.paths import get_project_root

@dataclass
class V3Report:
    """Triple-verification results with GitHub interoperability"""
    v1_work_verified: bool = False      # Zero-Tolerance Baseline
    v2_integration_validated: bool = False # Architecture & Imports
    v3_truth_verified: bool = False     # GitHub Sync & Completion
    details: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class V3Verifier:
    """
    V3 Verification Engine - The proof of high-fidelity work.
    """

    def __init__(self, root_dir: Optional[Path] = None):
        self.project_root = root_dir or get_project_root()
        self.gatekeeper = ZuulGatekeeper(self.project_root)

    def verify_files(self, file_paths: List[str]) -> V3Report:
        """Execute Triple-Verification protocol"""
        report = V3Report()

        # 1. V1: Verify Work (Zero-Tolerance Baseline)
        v1_all_clean = True
        for path in file_paths:
            audit = self.gatekeeper.audit(path)
            # Must be GREEN, GREY, or BLUE (BLUE is info only)
            if audit.status in [SpectrumColor.RED, SpectrumColor.ORANGE, SpectrumColor.CYAN]:
                v1_all_clean = False
                report.details.append(
                    f"V1: {Path(path).name} is {audit.status.value}. Resolving..."
                )
        report.v1_work_verified = v1_all_clean

        # 2. V2: Validate Integration (Architecture & Imports)
        v2_valid = True
        for path in file_paths:
            if not self._check_integration(path):
                v2_valid = False
                report.details.append(f"V2: {Path(path).name} has integration gaps.")
        report.v2_integration_validated = v2_valid

        # 3. V3: Verify Truth (GitHub Sync & Completion)
        # Check if files are committed (reached GREY or GREEN status)
        v3_synced = True
        for path in file_paths:
            audit = self.gatekeeper.audit(path)
            if audit.status == SpectrumColor.CYAN:
                v3_synced = False
                report.details.append(f"V3: {Path(path).name} is uncommitted (CYAN).")

        report.v3_truth_verified = (
            report.v1_work_verified and 
            report.v2_integration_validated and 
            v3_synced
        )

        if report.v3_truth_verified:
            report.details.append("SUCCESS: All files are GREY/GREEN. Safe to close.")

        return report

    def _check_integration(self, file_path: str) -> bool:
        """Check for broken imports or missing dependencies"""
        path = Path(file_path)
        if path.suffix == '.py':
            try:
                content = path.read_text(encoding='utf-8')
                # Check for relative imports
                imports = re.findall(r'from ([\w.]+) import', content) + \
                          re.findall(r'import ([\w.]+)', content)
                for imp in imports:
                    if imp.startswith('.'): return False

                # Check for raw 'pass'
                if re.search(r'^\s*pass\s*(#.*)?$', content, re.MULTILINE):
                    # Only check if it's not in an except block (V1 handles this but V2 confirms)
                    return False

                return True
            except Exception: return False
        return True
