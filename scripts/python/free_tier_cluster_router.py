#!/usr/bin/env python3
"""
Free-tier virtual cluster router: promotes the model whose traits best match the
AI token request, considers token pool remaining, and round-robins among similar
models to preserve pool reserves.

#automation: run with --request-type <edit|chat|generate|refactor|debug|explain|test|document|security|optimize>
Output: JSON with model_id, endpoint, api_base, cursor_model_name.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLUSTER_CONFIG = REPO_ROOT / "config" / "free_tier_virtual_cluster.json"
PROVIDERS_CONFIG = REPO_ROOT / "config" / "ca_free_models_providers.json"
POOL_STATE_PATH = REPO_ROOT / "data" / "free_tier_token_pools.json"


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_state_path(config: dict) -> Path:
    rel = config["token_pools"]["state_file"]
    return (REPO_ROOT / rel) if not Path(rel).is_absolute() else Path(rel)


def ensure_pool_state(config: dict) -> dict:
    state_path = get_state_path(config)
    if not state_path.exists():
        state = {
            "period_start": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "reset_period": config["token_pools"].get("reset_period", "daily"),
            "per_slot": {},
            "round_robin": {},
        }
        save_json(state_path, state)
        return state
    state = load_json(state_path)
    # Optional: reset if period rolled over (daily = by date)
    period = config["token_pools"].get("reset_period", "daily")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if period == "daily" and state.get("period_start") != today:
        state["period_start"] = today
        state["per_slot"] = {}
        save_json(state_path, state)
    return state


def slot_key(model_id: str, endpoint_key: str) -> str:
    return f"{model_id}|{endpoint_key}"


def get_pool_remaining(state: dict, config: dict, model_id: str, endpoint_key: str) -> int | None:
    """Return remaining tokens for this slot; None = unlimited."""
    pools = config.get("token_pools", {})
    per_endpoint = pools.get("per_endpoint", {}).get(endpoint_key, {})
    max_tokens = per_endpoint.get("max_tokens_per_period") or pools.get("default_max_tokens_per_period")
    if max_tokens is None or max_tokens == 0:
        return None
    key = slot_key(model_id, endpoint_key)
    used = state.get("per_slot", {}).get(key, {}).get("tokens_used", 0)
    return max(0, max_tokens - used)


def role_to_similarity_group(model_id: str, cluster: dict) -> str | None:
    for group, model_ids in cluster.get("similarity_groups", {}).items():
        if not isinstance(model_ids, list):
            continue
        if model_id in model_ids:
            return group
    return None


def select_model(
    request_type: str,
    cluster: dict,
    providers: dict,
    state: dict,
) -> tuple[str, str, str, str]:
    """
    Returns (model_id, endpoint_key, api_base, cursor_model_name).
    """
    mapping = cluster.get("request_trait_mapping", {}).get(request_type) or cluster["request_trait_mapping"].get("default", {})
    primary_roles = mapping.get("primary_roles", ["general_purpose"])
    fallback_roles = mapping.get("fallback_roles", [])
    tier_preference = mapping.get("tier_preference", [2, 1, 3])

    # Build model_id -> role, tier, context_length from providers
    model_info = {}
    for m in providers.get("ollama_models", []):
        model_info[m["model_id"]] = {
            "role": m["role"],
            "tier": m["tier"],
            "context_length": m.get("context_length", 32768),
        }

    # Candidates: (model_id, role_priority, tier) for primary then fallback
    candidates = []
    for model_id, info in model_info.items():
        role = info["role"]
        if role in primary_roles:
            candidates.append((model_id, 0, info["tier"]))
        elif role in fallback_roles:
            candidates.append((model_id, 1, info["tier"]))

    # Sort by role_priority then tier preference (lower index in tier_preference = better)
    def tier_rank(tier: int) -> int:
        try:
            return tier_preference.index(tier)
        except ValueError:
            return 999

    candidates.sort(key=lambda x: (x[1], tier_rank(x[2]), x[2]))

    endpoints = cluster.get("endpoints", {})
    policy = cluster.get("routing_policy", {})
    consider_pool = policy.get("consider_pool_remaining", True)
    pool_low_ratio = policy.get("pool_low_threshold_ratio", 0.2)
    round_robin = policy.get("round_robin_within_similar", True)
    prefer_endpoints = policy.get("prefer_endpoint_order", ["ollama_local", "iron_legion"])

    # Build (model_id, endpoint_key) slots with pool remaining and similarity group
    slots = []
    for model_id, _rp, _tier in candidates:
        for ep_key in prefer_endpoints:
            if ep_key not in endpoints:
                continue
            remaining = get_pool_remaining(state, cluster, model_id, ep_key) if consider_pool else None
            if remaining is not None and remaining <= 0:
                continue
            group = role_to_similarity_group(model_id, cluster)
            slots.append({
                "model_id": model_id,
                "endpoint_key": ep_key,
                "api_base": endpoints[ep_key]["url"],
                "pool_remaining": remaining,
                "similarity_group": group,
                "role_priority": _rp,
                "tier_rank": tier_rank(_tier),
            })

    if not slots:
        # Fallback: first candidate, first endpoint
        model_id = candidates[0][0] if candidates else list(model_info)[0]
        ep_key = prefer_endpoints[0]
        api_base = endpoints.get(ep_key, {}).get("url", "http://localhost:11434/v1")
        cursor_name = f"{model_id.replace(':', '-')}-{ep_key.replace('_', '-')}"
        return (model_id, ep_key, api_base, cursor_name)

    # Round-robin within similarity group: pick group that was used least recently
    rr = state.get("round_robin", {})
    if round_robin and slots:
        # Group slots by similarity_group; within each group pick by round_robin index
        from collections import defaultdict
        by_group = defaultdict(list)
        for s in slots:
            g = s["similarity_group"] or "default"
            by_group[g].append(s)
        # Prefer primary role, then higher pool remaining, then rotate
        best_slot = None
        best_group = None
        for g, group_slots in by_group.items():
            group_slots.sort(key=lambda s: (s["role_priority"], -(s["pool_remaining"] or 999999), s["tier_rank"]))
            idx = rr.get(g, 0) % len(group_slots)
            slot = group_slots[idx]
            if best_slot is None or (slot["role_priority"], slot["tier_rank"]) < (best_slot["role_priority"], best_slot["tier_rank"]):
                best_slot = slot
                best_group = g
        if best_slot is not None:
            slot = best_slot
            # Advance round-robin for next time
            rr[best_group] = rr.get(best_group, 0) + 1
            state["round_robin"] = rr
            save_json(get_state_path(cluster), state)
    else:
        # No round-robin: pick best by role_priority, tier, pool_remaining
        slots.sort(key=lambda s: (s["role_priority"], s["tier_rank"], -(s["pool_remaining"] or 999999)))
        slot = slots[0]

    model_id = slot["model_id"]
    ep_key = slot["endpoint_key"]
    api_base = slot["api_base"]
    cursor_name = f"{model_id.replace(':', '-')}-{ep_key.replace('_', '-')}"
    return (model_id, ep_key, api_base, cursor_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Free-tier virtual cluster router")
    parser.add_argument("--request-type", default="default", help="edit|chat|generate|refactor|debug|explain|test|document|security|optimize|default")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    cluster = load_json(CLUSTER_CONFIG)
    providers = load_json(PROVIDERS_CONFIG)
    state = ensure_pool_state(cluster)

    model_id, endpoint_key, api_base, cursor_model_name = select_model(
        args.request_type, cluster, providers, state
    )

    out = {
        "model_id": model_id,
        "endpoint": endpoint_key,
        "api_base": api_base,
        "cursor_model_name": cursor_model_name,
        "request_type": args.request_type,
    }

    if args.json:
        print(json.dumps(out))
    else:
        print(f"model_id={model_id} endpoint={endpoint_key} api_base={api_base} cursor_model_name={cursor_model_name}")
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
