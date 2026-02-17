#!/usr/bin/env python3
"""
Post Lumina unpublish task to company Microsoft Teams channel via Incoming Webhook.

#automation: Run from repo root: python scripts/python/post_lumina_unpublish_to_teams.py

Reads webhook URL from:
  - TEAMS_WEBHOOK_URL env var, or
  - config/teams_webhook_config.json (webhook_url key)

If no URL is set, prints the message so you can paste it into Teams manually.
See docs/system/LUMINA_UNPUBLISH_VIA_TEAMS.md.
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "teams_webhook_config.json"


def get_webhook_url() -> str | None:
    url = os.environ.get("TEAMS_WEBHOOK_URL", "").strip()
    if url and not url.startswith("https://your-"):
        return url
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            url = (data.get("webhook_url") or "").strip()
            if url and "your-tenant" not in url:
                return url
        except Exception:
            pass
    return None


def build_message_card() -> dict:
    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "Lumina unpublish task",
        "themeColor": "D32F2F",
        "title": "Action required: Unpublish all Lumina extensions from marketplaces",
        "sections": [
            {
                "activityTitle": "RCA: AI (agent) published — not human",
                "activitySubtitle": "See repo: docs/system/LUMINA_EXTENSION_NEVER_PUBLISH_WHY.md",
                "markdown": True,
            },
            {
                "text": "**Extensions to remove** (publisher: lumina): Lumina Core, Lumina Premium, Lumina Unified Queue, Lumina Footer Ticker, Lumina File Auto-Close (all five).",
                "markdown": True,
            },
            {
                "text": (
                    "**1. VS Code Marketplace** — [marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage)\n"
                    "Sign in, unpublish/remove each of the five extensions.\n\n"
                    "**2. Open VSX** — [open-vsx.org](https://open-vsx.org)\n"
                    "Sign in, open publisher **lumina**, unpublish/remove each of the five.\n\n"
                    "**3. Cursor** — After 1 and 2, Cursor will stop showing them; use only VSIX install (BDA)."
                ),
                "markdown": True,
            },
            {
                "text": "**Checklist:** [ ] VS Code Marketplace done  [ ] Open VSX done  [ ] Verification search done",
                "markdown": True,
            },
        ],
    }


def post_to_teams(url: str, payload: dict) -> bool:
    try:
        import urllib.request

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except Exception as e:
        print(f"Post failed: {e}", file=sys.stderr)
        return False


def main() -> int:
    url = get_webhook_url()
    payload = build_message_card()

    if url:
        if post_to_teams(url, payload):
            print("Posted Lumina unpublish task to Teams.")
            return 0
        return 1

    print("No Teams webhook URL configured (TEAMS_WEBHOOK_URL or config/teams_webhook_config.json).")
    print("Post the following message manually in your company Teams channel:")
    print()
    print("---")
    print(payload["title"])
    print()
    for s in payload["sections"]:
        if "text" in s:
            print(s["text"])
        if "activityTitle" in s:
            print(s["activityTitle"])
            if s.get("activitySubtitle"):
                print(s["activitySubtitle"])
    print("---")
    print()
    print("See docs/system/LUMINA_UNPUBLISH_VIA_TEAMS.md and REMOVE_LUMINA_FROM_ALL_MARKETPLACES.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
