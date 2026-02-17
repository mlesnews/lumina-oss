#!/usr/bin/env python3
"""
LUMINA B-Side Sandbox Daemon
============================
Runs outside Cursor's sandbox with full network access. Watches the request
directory for job files written by the A-Side (Agent / Cursor sandbox), executes
only allowlisted scripts, and writes responses back. Enables the "double sandbox"
workaround: A-Side = Cursor (file I/O only), B-Side = LUMINA (our sandbox, network allowed).

#automation #workaround #cursor-sandbox
"""

import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_shutdown_requested = False


def _handle_sigint(_signum, _frame):
    global _shutdown_requested
    _shutdown_requested = True

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CONFIG_PATH = PROJECT_ROOT / "config" / "lumina_sandbox.json"
REQUEST_DIR_DEFAULT = PROJECT_ROOT / "data" / "lumina_sandbox" / "requests"
RESPONSE_DIR_DEFAULT = PROJECT_ROOT / "data" / "lumina_sandbox" / "responses"
PROCESSED_DIR_NAME = "processed"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("lumina_sandbox_daemon")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_allowed_map(config: dict) -> dict:
    return {a["id"]: a for a in config.get("allowed_actions", [])}


def ensure_dirs(config: dict) -> tuple[Path, Path]:
    req = PROJECT_ROOT / config.get("request_dir", REQUEST_DIR_DEFAULT.name)
    rsp = PROJECT_ROOT / config.get("response_dir", RESPONSE_DIR_DEFAULT.name)
    req.mkdir(parents=True, exist_ok=True)
    rsp.mkdir(parents=True, exist_ok=True)
    (req / PROCESSED_DIR_NAME).mkdir(exist_ok=True)
    return req, rsp


def run_script(action: dict, cwd: Path, timeout_seconds: int) -> tuple[int, str, str]:
    runner = action.get("runner", "python")
    script_rel = action.get("script", "")
    args_list = action.get("args") or []
    script_path = (cwd / script_rel).resolve()
    if not script_path.exists():
        return -1, "", f"Script not found: {script_path}"

    if runner == "powershell":
        cmd = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-NoProfile",
            "-File", str(script_path),
        ] + [str(a) for a in args_list]
    elif runner == "python":
        cmd = [sys.executable, str(script_path)] + [str(a) for a in args_list]
    else:
        return -1, "", f"Unknown runner: {runner}"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=False,  # Read as bytes to avoid UnicodeDecodeError in thread
            timeout=timeout_seconds,
            env=os.environ.copy(),
            check=False,
        )

        # Decode manually with replacement for invalid characters
        def decode_safe(b):
            if not b:
                return ""
            try:
                return b.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    return b.decode("cp1252", errors="replace")
                except Exception:
                    return b.decode("utf-8", errors="replace")

        stdout = decode_safe(result.stdout)
        stderr = decode_safe(result.stderr)

        return result.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout_seconds}s"
    except Exception as e:
        return -1, "", str(e)


def process_request(
    request_path: Path,
    request_data: dict,
    allowed: dict,
    _response_dir: Path,
    timeout: int,
) -> dict:
    action_id = request_data.get("action_id") or request_data.get("id")
    if not action_id:
        return {"ok": False, "error": "Missing action_id or id in request"}
    action = allowed.get(action_id)
    if not action:
        return {"ok": False, "error": f"Action not allowlisted: {action_id}"}

    exit_code, stdout, stderr = run_script(action, PROJECT_ROOT, timeout)
    req_id = request_data.get("request_id") or request_path.stem
    return {
        "ok": exit_code == 0,
        "request_id": req_id,
        "action_id": action_id,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }


def main_loop(config: dict):
    global _shutdown_requested
    allowed = get_allowed_map(config)
    request_dir, response_dir = ensure_dirs(config)
    poll_interval = config.get("poll_interval_seconds", 2)
    timeout = config.get("default_timeout_seconds", 300)

    logger.info("LUMINA B-Side Sandbox Daemon started (full network). Watching: %s", request_dir)
    logger.info("Allowed actions: %s", list(allowed.keys()))

    while not _shutdown_requested:
        try:
            for f in request_dir.glob("*.json"):
                if f.name.startswith(".") or f.parent.name == PROCESSED_DIR_NAME:
                    continue
                try:
                    with open(f, encoding="utf-8") as fp:
                        data = json.load(fp)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("Invalid request file %s: %s", f.name, e)
                    continue

                req_id = data.get("request_id") or f.stem
                action_id_val = data.get("action_id") or data.get("id")
                logger.info("Processing request: %s (action_id=%s)", req_id, action_id_val)

                response = process_request(f, data, allowed, response_dir, timeout)
                response_path = response_dir / f"{req_id}.json"
                with open(response_path, "w", encoding="utf-8") as fp:
                    json.dump(response, fp, indent=2)
                logger.info("Response written: %s (ok=%s)", response_path.name, response.get("ok"))

                processed = request_dir / PROCESSED_DIR_NAME / f.name
                shutil.move(str(f), str(processed))
        except KeyboardInterrupt:
            _shutdown_requested = True
            break
        except Exception as e:
            logger.exception("Loop error: %s", e)

        for _ in range(poll_interval):
            if _shutdown_requested:
                break
            time.sleep(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LUMINA B-Side Sandbox Daemon (run outside Cursor for network)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process one batch and exit (for testing)",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install as Task Scheduler task (run at logon)",
    )
    args = parser.parse_args()

    config = load_config()
    allowed = get_allowed_map(config)
    request_dir, response_dir = ensure_dirs(config)
    timeout = config.get("default_timeout_seconds", 300)

    if args.install:
        script_path = Path(__file__).resolve()
        ps_lines = [
            '$TaskName = "LUMINA-B-Side-Sandbox-Daemon"',
            f'$Action = New-ScheduledTaskAction -Execute "pythonw.exe" '
            f'-Argument \'"{script_path}"\' -WorkingDirectory "{PROJECT_ROOT}"',
            "$Trigger = New-ScheduledTaskTrigger -AtLogOn",
            '$Trigger.Delay = "PT1M"',
            r'$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" '
            "-LogonType Interactive -RunLevel Highest",
            "$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries "
            "-DontStopIfGoingOnBatteries -StartWhenAvailable",
            'Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger '
            '-Principal $Principal -Settings $Settings '
            '-Description "LUMINA B-Side: runs network-requiring scripts (file handoff)" -Force',
            'Write-Output "Installed: $TaskName"',
        ]
        ps = "\n".join(ps_lines)
        r = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            check=False,
        )
        print(r.stdout or "")
        if r.returncode != 0:
            print(r.stderr or "", file=sys.stderr)
        return r.returncode

    if args.once:
        processed = 0
        for f in request_dir.glob("*.json"):
            if f.parent.name == PROCESSED_DIR_NAME:
                continue
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            response = process_request(f, data, allowed, response_dir, timeout)
            response_path = response_dir / f"{response['request_id']}.json"
            with open(response_path, "w", encoding="utf-8") as fp:
                json.dump(response, fp, indent=2)
            shutil.move(str(f), str(request_dir / PROCESSED_DIR_NAME / f.name))
            processed += 1
        logger.info("Processed %s request(s). Exiting.", processed)
        return 0

    signal.signal(signal.SIGINT, _handle_sigint)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_sigint)
    try:
        main_loop(config)
    except KeyboardInterrupt:
        pass
    if _shutdown_requested:
        logger.info("Shutdown requested. Exiting.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested. Exiting.")
        sys.exit(0)
