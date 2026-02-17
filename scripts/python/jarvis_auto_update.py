#!/usr/bin/env python3
"""
JARVIS Auto-Update Script (#automation)

Syncs agents and IDE config from upstream sources (GitHub, NPM) per config/auto_update.yaml,
preserving author credits. Run from repo root or scripts/python/.

Usage:
  python scripts/python/jarvis_auto_update.py
  python scripts/python/jarvis_auto_update.py --check-only
  python scripts/python/jarvis_auto_update.py --dry-run

Reference: docs/JARVIS_CA_IDE_CONSOLIDATION_PLAN.md §6, docs/system/JARVIS_PHASE_3_4_NEXT_STEPS.md
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

# Author-preserved filenames (do not overwrite when author_preserve is true)
AUTHOR_PRESERVE_FILES = {"README.md", "AUTHORS.txt", "CHANGELOG.md", "LICENSE"}

LOG = logging.getLogger("jarvis_auto_update")


def _find_repo_root(start: Path | None = None) -> Path:
    """Walk up to find repo root (directory containing config/auto_update.yaml or .git)."""
    start = start or Path.cwd()
    for p in [start, *start.parents]:
        if (p / "config" / "auto_update.yaml").exists():
            return p
        if (p / ".git").exists():
            return p
    return start


def _load_config(root: Path) -> dict:
    """Load config/auto_update.yaml."""
    path = root / "config" / "auto_update.yaml"
    if not path.exists():
        return {}
    if yaml is None:
        LOG.warning("PyYAML not installed; pip install pyyaml")
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _find_npm() -> str | None:
    """Return path to npm executable, or None if not found. Tries PATH then Windows locations."""
    npm = shutil.which("npm")
    if npm:
        return npm
    if sys.platform == "win32":
        for candidate in (
            os.environ.get("ProgramFiles", "C:\\Program Files") + "\\nodejs\\npm.cmd",
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)") + "\\nodejs\\npm.cmd",
            os.environ.get("APPDATA", "") + "\\npm\\npm.cmd",
        ):
            if candidate and os.path.isfile(candidate):
                return candidate
    return None


def _check_source(source: dict, root: Path) -> dict | None:
    """Check one source for available updates. Returns update info or None."""
    name = source.get("name", "?")
    kind = source.get("type", "")
    url = source.get("url", "")
    pkg = source.get("package", "")

    # Skip placeholder URLs (no real fetch); log is done once in main()
    if "your-org" in url or "your-org" in pkg:
        return None

    if kind == "github":
        try:
            r = subprocess.run(
                ["git", "ls-remote", "--exit-code", url, "HEAD"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=root,
            )
            if r.returncode == 0 and r.stdout:
                head = r.stdout.split()[0]
                return {"name": name, "type": "github", "url": url, "path": source.get("path"), "head": head, "author_preserve": source.get("author_preserve", False)}
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            LOG.warning("Check failed for %s: %s", name, e)
        return None

    if kind == "npm":
        npm_cmd = _find_npm()
        if not npm_cmd:
            return None  # npm not found; main() logs once
        # npm view does not support wildcard package names; skip check (apply can still run npm install)
        if "*" in pkg:
            return None
        try:
            r = subprocess.run(
                [npm_cmd, "view", pkg, "version", "--no-workspaces"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=root,
            )
            if r.returncode == 0 and r.stdout:
                version = r.stdout.strip()
                return {"name": name, "type": "npm", "package": pkg, "path": source.get("path"), "version": version, "author_preserve": source.get("author_preserve", False)}
        except subprocess.TimeoutExpired:
            LOG.info("npm view timed out for %s; skipping.", name)
        except OSError as e:
            LOG.warning("Check failed for %s: %s", name, e)
        return None

    return None


def _apply_update(update: dict, root: Path, dry_run: bool) -> bool:
    """Apply one update. Returns True on success."""
    name = update.get("name", "?")
    path_rel = update.get("path")
    if not path_rel:
        LOG.warning("No path for %s", name)
        return False

    dest = root / path_rel
    dest.mkdir(parents=True, exist_ok=True)
    author_preserve = update.get("author_preserve", False)

    if update.get("type") == "github":
        url = update.get("url", "")
        if dry_run:
            LOG.info("[dry-run] Would fetch %s into %s", name, path_rel)
            return True
        try:
            with tempfile.TemporaryDirectory(prefix="jarvis_au_") as tmp:
                clone_dir = Path(tmp) / "repo"
                subprocess.run(
                    ["git", "clone", "--depth", "1", url, str(clone_dir)],
                    check=True,
                    capture_output=True,
                    timeout=60,
                    cwd=root,
                )
                for f in clone_dir.rglob("*"):
                    if f.is_file():
                        rel = f.relative_to(clone_dir)
                        out = dest / rel
                        if author_preserve and rel.name in AUTHOR_PRESERVE_FILES and out.exists():
                            continue
                        out.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, out)
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            LOG.error("Apply failed for %s: %s", name, e)
            return False

    if update.get("type") == "npm":
        pkg = update.get("package", "")
        npm_cmd = _find_npm()
        if not npm_cmd:
            LOG.info("npm not on PATH; skipping apply for %s. Add Node.js to PATH to enable.", name)
            return False
        if dry_run:
            LOG.info("[dry-run] Would npm install %s for %s", pkg, name)
            return True
        try:
            # Install from repo root so package lands in node_modules; path in config is for reference
            subprocess.run(
                [npm_cmd, "install", pkg, "--no-workspaces", "--legacy-peer-deps"],
                check=True,
                capture_output=True,
                timeout=120,
                cwd=root,
            )
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            LOG.error("Apply failed for %s: %s", name, e)
            return False

    return False


def _notify(results: list[dict], log_path: Path, config: dict) -> None:
    """Write results to internal log and optional Slack/Discord webhook."""
    notif = config.get("notifications", {})
    channels = notif.get("channels", [])

    if "internal_log" in channels:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now(timezone.utc).isoformat()}] jarvis_auto_update\n")
            for r in results:
                f.write(f"  {r.get('source', '?')}: {r.get('status', '?')}")
                if r.get("error"):
                    f.write(f" ({r['error']})")
                f.write("\n")

    webhook_url = (notif.get("webhook_url") or "").strip()
    if webhook_url:
        _notify_webhook(results, webhook_url)


def _notify_webhook(results: list[dict], webhook_url: str) -> None:
    """POST summary to Slack/Discord webhook (URL not logged)."""
    ok = sum(1 for r in results if r.get("status") == "success")
    failed = sum(1 for r in results if r.get("status") == "failed")
    text = f"JARVIS Auto-Update: {ok} ok, {failed} failed"
    if failed:
        text += " — check data/jarvis_auto_update.log"
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                LOG.warning("Webhook returned status %s", resp.status)
    except Exception as e:
        LOG.warning("Webhook notification failed: %s", e)


def main() -> int:
    parser = argparse.ArgumentParser(description="JARVIS Auto-Update: sync from upstream, preserve author credits.")
    parser.add_argument("--check-only", action="store_true", help="Only check for updates, do not apply.")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be applied, do not change files.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    root = _find_repo_root()
    if not (root / "config" / "auto_update.yaml").exists():
        LOG.error("config/auto_update.yaml not found; run from repo root or scripts/python/")
        return 1

    config = _load_config(root)
    sources = config.get("sources", [])
    if not sources:
        LOG.info("No sources in config.")
        return 0

    placeholder_count = sum(
        1 for s in sources
        if "your-org" in s.get("url", "") or "your-org" in s.get("package", "")
    )
    npm_sources = [s for s in sources if s.get("type") == "npm"]
    npm_available = _find_npm() is not None

    updates = []
    for src in sources:
        u = _check_source(src, root)
        if u:
            updates.append(u)

    if placeholder_count:
        LOG.info("Skipping %s source(s) (placeholder URL/package). Replace your-org in config to enable.", placeholder_count)
    if npm_sources and not npm_available:
        LOG.info("npm not on PATH; %s NPM source(s) skipped. Add Node.js to PATH to enable.", len(npm_sources))

    if not updates:
        LOG.info("No updates available.")
        return 0

    if args.check_only:
        for u in updates:
            LOG.info("Would update: %s", u.get("name"))
        return 0

    results = []
    for u in updates:
        ok = _apply_update(u, root, args.dry_run)
        results.append({
            "source": u.get("name", "?"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "success" if ok else "failed",
            "error": None if ok else "apply failed",
        })

    log_path = root / "data" / "jarvis_auto_update.log"
    _notify(results, log_path, config)

    failed = sum(1 for r in results if r.get("status") == "failed")
    LOG.info("Updates applied: %d ok, %d failed", len(results) - failed, failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
