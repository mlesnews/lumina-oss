#!/usr/bin/env python3
"""
Premium-tier virtual cluster router: promotes the paid model whose traits best
match the AI token request, considers token pool remaining, and round-robins
among similar models to preserve pool reserves.

#automation: run with --request-type <edit|chat|generate|refactor|...>
Output: JSON with model_id, provider, api_base, cursor_model_name, key_source.
API keys: never in config; use key_source (env var name) to resolve at runtime.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLUSTER_CONFIG = REPO_ROOT / "config" / "premium_tier_virtual_cluster.json"
PROVIDERS_CONFIG = REPO_ROOT / "config" / "ca_premium_models_providers.json"


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
        now = datetime.now(timezone.utc)
        state = {
            "period_start": now.strftime("%Y-%m-01"),
            "reset_period": config["token_pools"].get("reset_period", "monthly"),
            "per_slot": {},
            "round_robin": {},
        }
        save_json(state_path, state)
        return state
    state = load_json(state_path)
    period = config["token_pools"].get("reset_period", "monthly")
    now = datetime.now(timezone.utc)
    this_month = now.strftime("%Y-%m-01")
    if period == "monthly" and state.get("period_start") != this_month:
        state["period_start"] = this_month
        state["per_slot"] = {}
        save_json(state_path, state)
    return state


def slot_key(model_id: str, provider: str) -> str:
    return f"{model_id}|{provider}"


def get_pool_remaining(state: dict, config: dict, model_id: str, provider: str) -> int | None:
    """Return remaining requests (or tokens) for this slot; None = unlimited."""
    pools = config.get("token_pools", {})
    per_provider = pools.get("per_provider", {}).get(provider, {})
    max_req = per_provider.get("max_requests_per_period") or pools.get("default_max_requests_per_period")
    max_tok = per_provider.get("max_tokens_per_period") or pools.get("default_max_tokens_per_period")
    cap = max_req if max_req and max_req > 0 else (max_tok if max_tok and max_tok > 0 else None)
    if cap is None or cap == 0:
        return None
    key = slot_key(model_id, provider)
    used = state.get("per_slot", {}).get(key, {})
    used_req = used.get("requests_used", 0)
    used_tok = used.get("tokens_used", 0)
    remaining = max(0, (max_req or cap) - used_req) if max_req else max(0, (max_tok or cap) - used_tok)
    return remaining


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
    providers_doc: dict,
    state: dict,
) -> tuple[str, str, str, str, str]:
    """
    Returns (model_id, provider, api_base, cursor_model_name, key_source).
    """
    mapping = cluster.get("request_trait_mapping", {}).get(request_type) or cluster["request_trait_mapping"].get("default", {})
    primary_roles = mapping.get("primary_roles", ["general_purpose"])
    fallback_roles = mapping.get("fallback_roles", [])
    tier_preference = mapping.get("tier_preference", [2, 1, 3])

    # Build model_id -> provider, role, tier from premium_models
    model_info = {}
    provider_urls = providers_doc.get("providers", {})
    for m in providers_doc.get("premium_models", []):
        model_id = m["model_id"]
        prov = m["provider"]
        if provider_urls.get(prov) and provider_urls[prov].get("api_base"):
            model_info[model_id] = {
                "provider": prov,
                "role": m["role"],
                "tier": m["tier"],
                "context_length": m.get("context_length", 128000),
            }

    def tier_rank(tier: int) -> int:
        try:
            return tier_preference.index(tier)
        except ValueError:
            return 999

    candidates = []
    for model_id, info in model_info.items():
        role = info["role"]
        if role in primary_roles:
            candidates.append((model_id, 0, info["tier"]))
        elif role in fallback_roles:
            candidates.append((model_id, 1, info["tier"]))

    candidates.sort(key=lambda x: (x[1], tier_rank(x[2]), x[2]))

    endpoints = cluster.get("endpoints", {})
    policy = cluster.get("routing_policy", {})
    consider_pool = policy.get("consider_pool_remaining", True)
    round_robin = policy.get("round_robin_within_similar", True)
    prefer_order = policy.get("prefer_endpoint_order", ["openai", "anthropic", "openrouter", "azure_openai", "cursor_builtin"])

    slots = []
    for model_id, _rp, _tier in candidates:
        info = model_info[model_id]
        prov = info["provider"]
        if prov not in endpoints or not endpoints[prov].get("url"):
            continue
        remaining = get_pool_remaining(state, cluster, model_id, prov) if consider_pool else None
        if remaining is not None and remaining <= 0:
            continue
        group = role_to_similarity_group(model_id, cluster)
        slots.append({
            "model_id": model_id,
            "provider": prov,
            "api_base": endpoints[prov]["url"],
            "pool_remaining": remaining,
            "similarity_group": group,
            "role_priority": _rp,
            "tier_rank": tier_rank(_tier),
        })

    if not slots:
        model_id = candidates[0][0] if candidates else next(iter(model_info))
        prov = model_info[model_id]["provider"]
        api_base = provider_urls.get(prov, {}).get("api_base") or ""
        key_src = provider_urls.get(prov, {}).get("key_source", "")
        cursor_name = f"{model_id.replace('/', '-')}-{prov}"
        return (model_id, prov, api_base, cursor_name, key_src)

    rr = state.get("round_robin", {})
    if round_robin and slots:
        by_group = defaultdict(list)
        for s in slots:
            g = s["similarity_group"] or "default"
            by_group[g].append(s)
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
            rr[best_group] = rr.get(best_group, 0) + 1
            state["round_robin"] = rr
            save_json(get_state_path(cluster), state)
    else:
        slots.sort(key=lambda s: (s["role_priority"], s["tier_rank"], -(s["pool_remaining"] or 999999)))
        slot = slots[0]

    model_id = slot["model_id"]
    prov = slot["provider"]
    api_base = slot["api_base"]
    key_src = provider_urls.get(prov, {}).get("key_source", "")
    cursor_name = f"{model_id.replace('/', '-')}-{prov}"
    return (model_id, prov, api_base, cursor_name, key_src)


def main() -> None:
    parser = argparse.ArgumentParser(description="Premium-tier virtual cluster router")
    parser.add_argument("--request-type", default="default", help="edit|chat|generate|refactor|debug|explain|test|document|security|optimize|default")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    args = parser.parse_args()

    cluster = load_json(CLUSTER_CONFIG)
    providers_doc = load_json(PROVIDERS_CONFIG)
    state = ensure_pool_state(cluster)

    model_id, provider, api_base, cursor_model_name, key_source = select_model(
        args.request_type, cluster, providers_doc, state
    )

    out = {
        "model_id": model_id,
        "provider": provider,
        "api_base": api_base,
        "cursor_model_name": cursor_model_name,
        "key_source": key_source,
        "request_type": args.request_type,
    }

    if args.json:
        print(json.dumps(out))
    else:
        print(f"model_id={model_id} provider={provider} api_base={api_base} key_source={key_source}")
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
