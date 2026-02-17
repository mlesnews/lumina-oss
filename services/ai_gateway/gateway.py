#!/usr/bin/env python3
"""
Lumina AI Gateway - Unified access to local cluster and cloud AI models.

Provides a single OpenAI-compatible API that routes to:
- Local Ollama cluster (Kaiju, NAS, Ultron)
- Free tier cloud providers (Groq, Together, OpenRouter)
- Premium tier cloud providers (OpenAI, Anthropic, Google)
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lumina-gateway")

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "ai_gateway_config.json"


@dataclass
class ModelEndpoint:
    """Represents a model endpoint (local or cloud)."""

    provider_id: str
    provider_name: str
    model_id: str
    base_url: str
    api_key: Optional[str] = None
    is_local: bool = False
    priority: int = 100
    capabilities: List[str] = field(default_factory=list)
    healthy: bool = True
    last_check: Optional[datetime] = None


class ChatMessage(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class LuminaGateway:
    """Main gateway class that handles routing and load balancing."""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config = self._load_config(config_path)
        self.endpoints: Dict[str, ModelEndpoint] = {}
        self.model_registry: Dict[str, List[ModelEndpoint]] = {}
        self.aliases: Dict[str, Dict] = {}
        self._build_registry()

    def _load_config(self, path: Path) -> Dict:
        """Load gateway configuration."""
        if path.exists():
            with open(path) as f:
                return json.load(f)
        logger.warning(f"Config not found at {path}, using defaults")
        return {}

    def _build_registry(self):
        """Build the model registry from config."""
        # Local cluster endpoints
        local_cluster = self.config.get("local_cluster", {})
        for endpoint in local_cluster.get("discovery", {}).get("endpoints", []):
            ep = ModelEndpoint(
                provider_id=endpoint["id"],
                provider_name=endpoint["name"],
                model_id="*",  # Local endpoints serve multiple models
                base_url=f"http://{endpoint['host']}:{endpoint['port']}/v1",
                is_local=True,
                priority=endpoint.get("priority", 100),
                capabilities=endpoint.get("capabilities", []),
            )
            self.endpoints[endpoint["id"]] = ep

        # Cloud providers
        for tier in ["free_tier", "premium_tier"]:
            providers = self.config.get("cloud_providers", {}).get(tier, {}).get("providers", [])
            for provider in providers:
                api_key = os.environ.get(provider.get("api_key_env", ""))
                for model in provider.get("models", []):
                    model_id = model["id"]
                    ep = ModelEndpoint(
                        provider_id=provider["id"],
                        provider_name=provider["name"],
                        model_id=model_id,
                        base_url=provider["base_url"],
                        api_key=api_key,
                        is_local=False,
                        priority=50 if tier == "free_tier" else 10,
                        capabilities=["chat"] + (["vision"] if model.get("vision") else []),
                    )
                    key = f"{provider['id']}:{model_id}"
                    self.endpoints[key] = ep

                    # Register model -> endpoints mapping
                    if model_id not in self.model_registry:
                        self.model_registry[model_id] = []
                    self.model_registry[model_id].append(ep)

        # Aliases
        self.aliases = self.config.get("model_aliases", {}).get("aliases", {})
        logger.info(f"Registered {len(self.endpoints)} endpoints, {len(self.aliases)} aliases")

    def resolve_model(self, model: str) -> tuple[str, ModelEndpoint]:
        """Resolve a model name/alias to actual model and endpoint."""
        # Check if it's an alias
        if model in self.aliases:
            alias = self.aliases[model]
            provider = alias["provider"]
            actual_model = alias["model"]

            if provider == "local":
                # Route to best available local endpoint
                for ep_id, ep in self.endpoints.items():
                    if ep.is_local and ep.healthy:
                        return actual_model, ep
                raise HTTPException(503, "No healthy local endpoints available")
            else:
                key = f"{provider}:{actual_model}"
                if key in self.endpoints:
                    return actual_model, self.endpoints[key]

        # Check if it's a direct model reference
        if model in self.model_registry:
            # Return highest priority healthy endpoint
            endpoints = sorted(self.model_registry[model], key=lambda e: e.priority)
            for ep in endpoints:
                if ep.healthy:
                    return model, ep

        # Check if it's a local model (route to local cluster)
        for ep_id, ep in self.endpoints.items():
            if ep.is_local and ep.healthy:
                return model, ep

        raise HTTPException(400, f"Model '{model}' not found in registry")

    async def health_check(self, endpoint: ModelEndpoint) -> bool:
        """Check if an endpoint is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                if endpoint.is_local:
                    resp = await client.get(f"{endpoint.base_url.replace('/v1', '')}/api/tags")
                else:
                    # For cloud providers, just check if we have an API key
                    return endpoint.api_key is not None
                endpoint.healthy = resp.status_code == 200
                endpoint.last_check = datetime.now()
                return endpoint.healthy
        except Exception as e:
            logger.warning(f"Health check failed for {endpoint.provider_name}: {e}")
            endpoint.healthy = False
            return False

    async def forward_chat_request(self, request: ChatRequest) -> Any:
        """Forward a chat request to the appropriate endpoint."""
        model, endpoint = self.resolve_model(request.model)

        logger.info(f"Routing {request.model} -> {endpoint.provider_name} ({model})")

        headers = {"Content-Type": "application/json"}
        if endpoint.api_key:
            headers["Authorization"] = f"Bearer {endpoint.api_key}"

        payload = {
            "model": model,
            "messages": [m.model_dump(exclude_none=True) for m in request.messages],
            "stream": request.stream,
        }
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        async with httpx.AsyncClient(timeout=120.0) as client:
            if request.stream:

                async def stream_response():
                    async with client.stream(
                        "POST",
                        f"{endpoint.base_url}/chat/completions",
                        json=payload,
                        headers=headers,
                    ) as resp:
                        async for chunk in resp.aiter_bytes():
                            yield chunk

                return StreamingResponse(stream_response(), media_type="text/event-stream")
            else:
                resp = await client.post(
                    f"{endpoint.base_url}/chat/completions", json=payload, headers=headers
                )
                if resp.status_code != 200:
                    raise HTTPException(resp.status_code, resp.text)
                return resp.json()

    def list_models(self) -> Dict:
        """List all available models."""
        models = []

        # Local models (would need to query each endpoint)
        for ep_id, ep in self.endpoints.items():
            if ep.is_local:
                models.append(
                    {
                        "id": f"local:{ep.provider_id}/*",
                        "provider": ep.provider_name,
                        "type": "local",
                        "healthy": ep.healthy,
                    }
                )

        # Cloud models
        for key, ep in self.endpoints.items():
            if not ep.is_local:
                models.append(
                    {
                        "id": ep.model_id,
                        "provider": ep.provider_name,
                        "type": "cloud",
                        "has_key": ep.api_key is not None,
                    }
                )

        # Aliases
        aliases = [{"alias": k, **v} for k, v in self.aliases.items()]

        return {
            "models": models,
            "aliases": aliases,
            "local_endpoints": [
                {"id": ep.provider_id, "name": ep.provider_name, "healthy": ep.healthy}
                for ep in self.endpoints.values()
                if ep.is_local
            ],
        }


# FastAPI app
app = FastAPI(
    title="Lumina AI Gateway",
    description="Unified access to local cluster and cloud AI models",
    version="1.0.0",
)

gateway = LuminaGateway()


@app.get("/")
async def root():
    return {"service": "Lumina AI Gateway", "status": "running"}


@app.get("/v1/models")
@app.get("/api/v1/models")
async def list_models():
    return gateway.list_models()


@app.post("/v1/chat/completions")
@app.post("/api/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    return await gateway.forward_chat_request(request)


@app.get("/health")
async def health():
    """Health check endpoint."""
    healthy_local = sum(1 for ep in gateway.endpoints.values() if ep.is_local and ep.healthy)
    total_local = sum(1 for ep in gateway.endpoints.values() if ep.is_local)
    return {
        "status": "healthy" if healthy_local > 0 else "degraded",
        "local_endpoints": f"{healthy_local}/{total_local}",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/admin/refresh")
async def refresh_endpoints():
    """Refresh all endpoint health status."""
    results = {}
    for ep_id, ep in gateway.endpoints.items():
        if ep.is_local:
            results[ep_id] = await gateway.health_check(ep)
    return {"refreshed": results}


if __name__ == "__main__":
    uvicorn.run("gateway:app", host="127.0.0.1", port=11435, reload=True, log_level="info")
