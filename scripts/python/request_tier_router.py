#!/usr/bin/env python3
"""
Request → Character → Tier + Compute Multiplier + Rate Tier Router

Reads config/character_cluster_request_tiers.json. Given (character, difficulty, request_type),
resolves request_type to boon_match | bane_match | neutral_match via character_boons_banes,
then returns tier, compute_multiplier, rate_tier (and escalate_to when present).

One-shot delegation: use --delegate (or --one-shot). When escalate_to is set, re-routes as the
first delegated character and returns run_as + tier/compute/rate in one call.

Phase 1 – First path. @DOIT @JARVIS #ACTION
Doc: docs/system/CONNECT_THE_DOTS_IMPLEMENTATION_ACTION.md
Config: config/character_cluster_request_tiers.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Repo root: same directory as config/
def _repo_root() -> Path:
    cur = Path(__file__).resolve().parent
    for _ in range(10):
        if (cur / "config").is_dir() and (cur / "config" / "character_cluster_request_tiers.json").exists():
            return cur
        cur = cur.parent
    return Path.cwd()


def load_config(root: Path | None = None) -> dict[str, Any]:
    root = root or _repo_root()
    path = root / "config" / "character_cluster_request_tiers.json"
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def resolve_match_type(
    config: dict[str, Any],
    character: str,
    request_type: str,
) -> str:
    """Map request_type to boon_match | bane_match | neutral_match using character_boons_banes."""
    boons_banes = config.get("character_boons_banes") or {}
    char_bb = boons_banes.get(character)
    if not char_bb:
        return "neutral_match"
    boons = set((char_bb.get("boons") or []))
    banes = set((char_bb.get("banes") or []))
    if request_type in boons:
        return "boon_match"
    if request_type in banes:
        return "bane_match"
    return "neutral_match"


def route(
    character: str,
    difficulty: str,
    request_type: str,
    config: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """
    Request → character → tier + compute_multiplier + rate_tier.

    Input:
        character: Tony | Mace | Gandalf | Marvin | JARVIS
        difficulty: easy | moderate | specialized | critical
        request_type: e.g. code_generation, review, long_form_compliance_docs (maps to boons/banes)

    Output:
        tier (int), compute_multiplier (float), rate_tier (str), escalate_to (list | None), match_type (str)
    """
    if config is None:
        config = load_config(repo_root)

    rates = config.get("request_character_rates") or {}
    char_rates = rates.get(character)
    if not char_rates:
        return {
            "tier": 2,
            "compute_multiplier": 1.0,
            "rate_tier": "standard",
            "escalate_to": None,
            "match_type": "neutral_match",
            "error": f"Unknown character: {character}",
        }

    diff_rates = char_rates.get(difficulty)
    if not diff_rates:
        return {
            "tier": 2,
            "compute_multiplier": 1.0,
            "rate_tier": "standard",
            "escalate_to": None,
            "match_type": "neutral_match",
            "error": f"Unknown difficulty: {difficulty}",
        }

    match_type = resolve_match_type(config, character, request_type)
    row = diff_rates.get(match_type)
    if not row:
        return {
            "tier": 2,
            "compute_multiplier": 1.0,
            "rate_tier": "standard",
            "escalate_to": None,
            "match_type": match_type,
            "error": f"Missing rate row: {match_type}",
        }

    return {
        "tier": row.get("tier", 2),
        "compute_multiplier": row.get("compute_multiplier", 1.0),
        "rate_tier": row.get("rate_tier", "standard"),
        "escalate_to": row.get("escalate_to"),
        "match_type": match_type,
    }


def route_one_shot(
    character: str,
    difficulty: str,
    request_type: str,
    *,
    delegate: bool = True,
    config: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """
    One-shot: route, then if escalate_to is set and delegate=True, re-route as the
    first delegated character. Returns the single "run as X" result so the caller
    doesn't have to decide—delegation is done in one shot.
    """
    result = route(character, difficulty, request_type, config=config, repo_root=repo_root)
    if not delegate or not result.get("escalate_to"):
        result["run_as"] = character
        result["delegate_to"] = None
        return result
    delegated = result["escalate_to"][0]
    delegated_result = route(delegated, difficulty, request_type, config=config, repo_root=repo_root)
    delegated_result["run_as"] = delegated
    delegated_result["delegate_to"] = delegated
    delegated_result["delegated_from"] = character
    return delegated_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Request → character → tier + compute_multiplier + rate_tier (Phase 1 router)"
    )
    parser.add_argument("character", help="Tony | Mace | Gandalf | Marvin | JARVIS")
    parser.add_argument("difficulty", help="easy | moderate | specialized | critical")
    parser.add_argument("request_type", help="e.g. code_generation, review, long_form_compliance_docs")
    parser.add_argument("--json", action="store_true", help="Output full result as JSON")
    parser.add_argument(
        "--delegate",
        "--one-shot",
        dest="one_shot",
        action="store_true",
        help="One-shot: if escalate_to is set, re-route as delegated character; output is run_as + tier/compute/rate",
    )
    args = parser.parse_args()

    try:
        if args.one_shot:
            result = route_one_shot(args.character, args.difficulty, args.request_type, delegate=True)
        else:
            result = route(args.character, args.difficulty, args.request_type)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    # One-line summary
    run_as = result.get("run_as", args.character)
    esc = ""
    if result.get("escalate_to") and not args.one_shot:
        esc = f" escalate_to={result['escalate_to']}"
    if result.get("delegate_to"):
        esc = f" delegated_from={result.get('delegated_from')}"
    err = ""
    if result.get("error"):
        err = f" error={result['error']}"
    print(
        f"run_as={run_as} tier={result['tier']} compute_multiplier={result['compute_multiplier']} "
        f"rate_tier={result['rate_tier']} match_type={result['match_type']}{esc}{err}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
