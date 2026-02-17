#!/usr/bin/env python3
"""
Apply all free CA models from config/ca_free_models_providers.json to Cursor
(cursor.agent.customModels, cursor.chat.customModels, cursor.composer.customModels).
#automation: run from repo root to sync Cursor settings with SSOT.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "ca_free_models_providers.json"
SETTINGS_PATH = REPO_ROOT / ".vscode" / "settings.json"

LOCAL_BASE = "http://localhost:11434/v1"
IRON_LEGION_BASE = "http://<NAS_IP>:11437/v1"


def model_id_to_title(model_id: str) -> str:
    """e.g. qwen2.5-coder:7b -> Qwen2.5 Coder 7B"""
    s = model_id.replace("-", " ").replace(":", " ")
    return s.title().replace(" ", " ")


def build_base_entries() -> list[dict]:
    """ULTRON (auto), Ultron alias, Iron Legion (auto)."""
    return [
        {
            "title": "ULTRON Cluster (Single Node)",
            "name": "ULTRON",
            "provider": "openai",
            "model": "auto",
            "apiBase": LOCAL_BASE,
            "contextLength": 32768,
            "timeout": 60000,
            "maxTokens": 8192,
            "description": "ULTRON Unified Cluster - Intelligent routing handled by local gateway node.",
            "localOnly": True,
            "skipProviderSelection": True,
        },
        {
            "title": "Ultron (alias)",
            "name": "Ultron",
            "provider": "openai",
            "model": "auto",
            "apiBase": LOCAL_BASE,
            "contextLength": 32768,
            "timeout": 60000,
            "maxTokens": 8192,
            "description": "Alias for ULTRON — local Ollama.",
            "localOnly": True,
            "skipProviderSelection": True,
        },
        {
            "title": "Iron Legion Cluster (Kaiju)",
            "name": "Iron Legion",
            "provider": "openai",
            "model": "auto",
            "apiBase": IRON_LEGION_BASE,
            "contextLength": 32768,
            "timeout": 60000,
            "maxTokens": 8192,
            "description": "Iron Legion - Kaiju Desktop Cluster (Single Node). Mark models handled internally.",
            "localOnly": True,
            "skipProviderSelection": True,
        },
    ]


def build_model_entry(
    model_id: str,
    context_length: int,
    api_base: str,
    suffix: str,
) -> dict:
    title = f"{model_id_to_title(model_id)} ({suffix})"
    name = f"{model_id.replace(':', '-')}-{suffix.lower().replace(' ', '-')}"
    return {
        "title": title,
        "name": name,
        "provider": "openai",
        "model": model_id,
        "apiBase": api_base,
        "contextLength": context_length,
        "timeout": 60000,
        "maxTokens": 8192,
        "description": f"Free model from CA SSOT — {suffix}.",
        "localOnly": True,
    }


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    ollama_models = config["ollama_models"]

    base = build_base_entries()
    custom_models = list(base)

    for m in ollama_models:
        model_id = m["model_id"]
        ctx = m["context_length"]
        custom_models.append(build_model_entry(model_id, ctx, LOCAL_BASE, "Local"))
        custom_models.append(build_model_entry(model_id, ctx, IRON_LEGION_BASE, "Iron Legion"))

    settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    settings["cursor.agent.customModels"] = custom_models
    settings["cursor.chat.customModels"] = custom_models
    settings["cursor.composer.customModels"] = custom_models

    SETTINGS_PATH.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(
        f"Applied {len(custom_models)} models to cursor.agent.customModels, cursor.chat.customModels, cursor.composer.customModels."
    )


if __name__ == "__main__":
    main()
