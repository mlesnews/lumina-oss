"""
Lighting startup single-run guard.
Ensures lighting runs only once per boot/session even if multiple startup paths run
(unified startup + headless daemon, or duplicate tasks). Avoids duplicate console/flashing.
"""

from datetime import datetime, timezone
from pathlib import Path

GUARD_FILE_NAME = ".lighting_startup_done"
MAX_AGE_SECONDS = 600  # 10 minutes


def _guard_path(project_root: Path) -> Path:
    data = project_root / "data"
    data.mkdir(parents=True, exist_ok=True)
    return data / GUARD_FILE_NAME


def should_skip_lighting_startup(
    project_root: Path, max_age_seconds: int = MAX_AGE_SECONDS
) -> bool:
    """Return True if lighting was already run recently (skip to avoid duplicate)."""
    path = _guard_path(project_root)
    if not path.exists():
        return False
    try:
        text = path.read_text().strip()
        if not text:
            return False
        done = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if done.tzinfo is None:
            done = done.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if (now - done).total_seconds() < max_age_seconds:
            return True
    except Exception:
        pass
    return False


def mark_lighting_startup_done(project_root: Path) -> None:
    """Mark that lighting startup has run (call before or right after running lighting)."""
    path = _guard_path(project_root)
    path.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")
