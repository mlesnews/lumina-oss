#!/usr/bin/env python3
"""
#automation Check JARVIS chat backends (ULTRON / Iron Legion) for post-reboot readiness.

Calls localhost:11434 (Ollama/ULTRON) and <NAS_IP>:11437 (Iron Legion/Kaiju).
Prints which backend(s) are up. Exit 0 if at least one is up, else 1.

Usage:
  python scripts/python/check_jarvis_chat_backends.py

Ref: docs/system/JARVIS_CHAT_AFTER_REBOOT_5W1H_AND_GAPS.md
     docs/system/CURSOR_IDE_QOL_INDEX.md (After reboot)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

DEFAULT_ULTRON_URL = "http://localhost:11434"
DEFAULT_IRON_LEGION_URL = "http://<NAS_IP>:11437"
TIMEOUT_SEC = 3


def _check_endpoint(base_url: str, path: str = "/api/tags") -> bool:
    try:
        req = Request(f"{base_url.rstrip('/')}{path}", method="GET")
        with urlopen(req, timeout=TIMEOUT_SEC) as _:
            return True
    except (URLError, HTTPError, OSError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Check JARVIS chat backends (ULTRON / Iron Legion).")
    ap.add_argument("--config", default=None, help="Optional JSON with ultron_url and iron_legion_url.")
    ap.add_argument("-q", "--quiet", action="store_true", help="Only exit code; no stdout.")
    args = ap.parse_args()

    ultron_url = DEFAULT_ULTRON_URL
    iron_legion_url = DEFAULT_IRON_LEGION_URL
    if args.config and os.path.isfile(args.config):
        try:
            with open(args.config, encoding="utf-8") as f:
                cfg = json.load(f)
            ultron_url = cfg.get("ultron_url", ultron_url)
            iron_legion_url = cfg.get("iron_legion_url", iron_legion_url)
        except (json.JSONDecodeError, OSError):
            pass

    ultron_up = _check_endpoint(ultron_url)
    iron_legion_up = _check_endpoint(iron_legion_url)

    if not args.quiet:
        if ultron_up:
            print("ULTRON up")
        else:
            print("ULTRON down")
        if iron_legion_up:
            print("Iron Legion up")
        else:
            print("Iron Legion down")
        if not ultron_up and not iron_legion_up:
            print("None — start Ollama and/or ensure Kaiju (<NAS_IP>) is on.")

    return 0 if (ultron_up or iron_legion_up) else 1


if __name__ == "__main__":
    sys.exit(main())
