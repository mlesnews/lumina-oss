#!/usr/bin/env python3
"""PERSONAPLEX Versioning System - @V3"""
import json, logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VersionPhase(Enum):
    DEVELOPMENT = "dev"
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"

class VersionType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    phase: VersionPhase = VersionPhase.DEVELOPMENT
    phase_version: int = 0

    def __str__(self) -> str:
        phase_str = ""
        if self.phase != VersionPhase.STABLE:
            phase_str = f"-{self.phase.value}"
            if self.phase_version > 0:
                phase_str += f".{self.phase_version}"
        return f"{self.major}.{self.minor}.{self.patch}{phase_str}"

    def bump(self, version_type: VersionType) -> "Version":
        if version_type == VersionType.MAJOR:
            return Version(major=self.major+1, minor=0, patch=0, phase=VersionPhase.DEVELOPMENT)
        elif version_type == VersionType.MINOR:
            return Version(major=self.major, minor=self.minor+1, patch=0, phase=VersionPhase.DEVELOPMENT)
        return Version(major=self.major, minor=self.minor, patch=self.patch+1, phase=self.phase)

class VersionManager:
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.versions_file = self.workspace_root / "data" / "personaplex_versions.json"
        self._artifacts: Dict[str, dict] = {}
        self._load_versions()
        logger.info("VersionManager initialized")

    def _load_versions(self) -> None:
        if self.versions_file.exists():
            try:
                with open(self.versions_file, "r") as f:
                    data = json.load(f)
                    self._artifacts = data.get("artifacts", {})
            except:
                pass

    def _save_versions(self) -> None:
        self.versions_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.versions_file, "w") as f:
            json.dump({"updated_at": datetime.utcnow().isoformat(), "artifacts": self._artifacts}, f, indent=2)

    def register(self, artifact_id: str, name: str, version: Version, description: str = "") -> None:
        self._artifacts[artifact_id] = {"name": name, "version": str(version), "description": description}
        self._save_versions()
        logger.info(f"Registered: {artifact_id} v{version}")

    def get_statistics(self) -> dict:
        phases = {}
        for art in self._artifacts.values():
            v_str = art["version"]
            for phase in VersionPhase:
                if phase.value in v_str:
                    phases[phase.value] = phases.get(phase.value, 0) + 1
                    break
        return {"total": len(self._artifacts), "by_phase": phases}

def create_version_manager(workspace_root: Optional[str] = None) -> VersionManager:
    return VersionManager(workspace_root=workspace_root)

if __name__ == "__main__":
    m = create_version_manager()
    v = Version(major=1, minor=2, patch=3, phase=VersionPhase.BETA)
    print(f"Version: {v}")
    print("PERSONAPLEX Versioning initialized!")
