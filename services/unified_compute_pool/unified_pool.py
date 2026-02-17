#!/usr/bin/env python3
"""
Unified Compute Pool - Treats all GPU + CPU as one resource pool

Architecture:
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIFIED COMPUTE POOL                             │
│                    http://localhost:8080                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    COMPUTE RESOURCES                           │  │
│  │                                                                │  │
│  │  GPU Layer:        CPU Layer:                                  │  │
│  │  ┌─────────┐       ┌─────────────┐  ┌─────────────┐           │  │
│  │  │RTX 5090 │       │ ULTRON CPU  │  │ Iron Legion │           │  │
│  │  │ 2GB*    │ ───►  │ 24 cores    │  │ ~12 cores   │           │  │
│  │  │ VRAM    │       │ 60GB RAM    │  │ ~32GB RAM   │           │  │
│  │  └─────────┘       └─────────────┘  └─────────────┘           │  │
│  │       │                   │                 │                  │  │
│  │       └───────────────────┴─────────────────┘                  │  │
│  │                        ↓                                       │  │
│  │              UNIFIED INFERENCE                                 │  │
│  │              - GPU handles first layers                        │  │
│  │              - CPU handles overflow                            │  │
│  │              - Parallel requests split across nodes            │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

*2GB usable VRAM due to Windows WDDM display reservation

Tags: @PEAK @CLUSTER @UNIFIED_POOL #automation
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aiohttp import ClientSession, ClientTimeout, web

# ═══════════════════════════════════════════════════════════════════════
# COMPUTE NODE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class ComputeResource:
    """Represents a compute resource (GPU or CPU pool)"""

    name: str
    type: str  # "gpu" or "cpu"
    host: str
    port: int
    cores: int = 0
    memory_gb: float = 0
    vram_gb: float = 0
    healthy: bool = False
    response_time_ms: float = 99999
    active_requests: int = 0
    models: List[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def compute_score(self) -> float:
        """Score based on available compute (higher = more capable)"""
        gpu_score = self.vram_gb * 10  # GPU memory is 10x valuable
        cpu_score = self.cores * 0.5 + self.memory_gb * 0.1
        return gpu_score + cpu_score


# Define all compute resources
COMPUTE_POOL = [
    ComputeResource(
        name="ULTRON-GPU",
        type="gpu",
        host="localhost",
        port=11434,
        cores=24,
        memory_gb=60,  # Available for CPU offload
        vram_gb=2,  # Usable VRAM after WDDM
    ),
    ComputeResource(
        name="ULTRON-CPU",
        type="cpu",
        host="localhost",
        port=11435,
        cores=24,
        memory_gb=60,
    ),
    ComputeResource(
        name="Iron-Legion",
        type="cpu",
        host="<NAS_IP>",
        port=11434,
        cores=12,  # Estimated
        memory_gb=32,  # Estimated
    ),
]


# ═══════════════════════════════════════════════════════════════════════
# UNIFIED COMPUTE POOL MANAGER
# ═══════════════════════════════════════════════════════════════════════


class UnifiedComputePool:
    """
    Manages all compute resources as a single unified pool.

    Strategies:
    1. Large models -> Route to highest-capacity node (ULTRON-GPU with CPU offload)
    2. Small/fast requests -> Route to fastest available node
    3. Parallel requests -> Spread across all healthy nodes
    4. Failover -> Automatic routing to backup nodes
    """

    def __init__(self):
        self.resources = COMPUTE_POOL
        self.session: Optional[ClientSession] = None
        self.total_requests = 0
        self.requests_by_node: Dict[str, int] = {}

    async def init(self):
        """Initialize the pool and start health monitoring"""
        timeout = ClientTimeout(total=30, connect=5)
        self.session = ClientSession(timeout=timeout)
        asyncio.create_task(self._health_monitor())
        print("\n=== UNIFIED COMPUTE POOL INITIALIZED ===")
        self._print_pool_status()

    async def close(self):
        if self.session:
            await self.session.close()

    def _print_pool_status(self):
        """Print current pool status"""
        total_vram = sum(r.vram_gb for r in self.resources if r.type == "gpu")
        total_ram = sum(r.memory_gb for r in self.resources)
        total_cores = sum(r.cores for r in self.resources)

        print(f"""
┌─────────────────────────────────────────────────────────┐
│              UNIFIED COMPUTE POOL                       │
├─────────────────────────────────────────────────────────┤
│  Total GPU VRAM:  {total_vram:>5.1f} GB (usable)                   │
│  Total RAM:       {total_ram:>5.1f} GB (for CPU offload)          │
│  Total CPU Cores: {total_cores:>5d}                                │
├─────────────────────────────────────────────────────────┤
│  Effective Capacity: ~{total_vram + total_ram:.0f} GB unified memory          │
│  Can run: 32B-70B models with CPU offload               │
└─────────────────────────────────────────────────────────┘
""")

    async def _health_monitor(self):
        """Continuously monitor health of all resources"""
        while True:
            for resource in self.resources:
                try:
                    start = time.time()

                    if resource.port == 11435:  # BitNet
                        url = f"{resource.url}/health"
                    else:  # Ollama
                        url = f"{resource.url}/api/tags"

                    async with self.session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            resource.healthy = True
                            resource.response_time_ms = (time.time() - start) * 1000

                            # Extract models
                            if "models" in data:
                                resource.models = [
                                    m.get("name", m.get("model", "unknown")) for m in data["models"]
                                ]
                        else:
                            resource.healthy = False
                except Exception:
                    resource.healthy = False
                    resource.response_time_ms = 99999

            await asyncio.sleep(10)  # Check every 10 seconds

    def get_pool_status(self) -> Dict[str, Any]:
        """Get current status of the unified pool"""
        healthy = [r for r in self.resources if r.healthy]

        total_vram = sum(r.vram_gb for r in healthy if r.type == "gpu")
        total_ram = sum(r.memory_gb for r in healthy)
        total_cores = sum(r.cores for r in healthy)

        all_models = set()
        for r in healthy:
            all_models.update(r.models)

        return {
            "status": "healthy" if healthy else "degraded",
            "nodes_online": len(healthy),
            "nodes_total": len(self.resources),
            "unified_capacity": {
                "gpu_vram_gb": total_vram,
                "cpu_ram_gb": total_ram,
                "total_memory_gb": total_vram + total_ram,
                "cpu_cores": total_cores,
            },
            "models_available": sorted(all_models),
            "resources": {
                r.name: {
                    "type": r.type,
                    "healthy": r.healthy,
                    "response_ms": round(r.response_time_ms, 1),
                    "active_requests": r.active_requests,
                    "models": r.models,
                }
                for r in self.resources
            },
            "total_requests": self.total_requests,
            "requests_by_node": self.requests_by_node,
        }

    def select_resource(
        self, model: Optional[str] = None, prefer_speed: bool = False
    ) -> Optional[ComputeResource]:
        """
        Select the best resource for a request.

        Strategy:
        - Large models (32B+): Route to ULTRON-GPU (has GPU + CPU offload)
        - Speed preference: Route to fastest responding healthy node
        - Default: Route to highest capacity node with lowest load
        """
        healthy = [r for r in self.resources if r.healthy]
        if not healthy:
            return None

        # Large model detection
        if model and any(size in model for size in ["32b", "70b", "72b", "14b"]):
            # Prefer GPU node for large models (can use CPU offload)
            gpu_nodes = [r for r in healthy if r.type == "gpu"]
            if gpu_nodes:
                return min(gpu_nodes, key=lambda r: r.active_requests)

        if prefer_speed:
            # Route to fastest responding node
            return min(healthy, key=lambda r: r.response_time_ms + (r.active_requests * 1000))

        # Default: Balance between capacity and load
        def score(r: ComputeResource) -> float:
            load_penalty = r.active_requests * 5000
            speed_bonus = -r.response_time_ms
            capacity_bonus = r.compute_score * 100
            return capacity_bonus + speed_bonus - load_penalty

        return max(healthy, key=score)

    async def proxy_request(self, request: web.Request, path: str) -> web.Response:
        """Proxy a request to the best available resource"""
        # Parse request
        try:
            body = await request.json() if request.body_exists else {}
        except:
            body = {}

        model = body.get("model")
        stream = body.get("stream", False)

        # Select resource
        resource = self.select_resource(model=model)
        if not resource:
            return web.json_response(
                {"error": "No healthy compute resources available"}, status=503
            )

        # Track request
        resource.active_requests += 1
        self.total_requests += 1
        self.requests_by_node[resource.name] = self.requests_by_node.get(resource.name, 0) + 1

        try:
            url = f"{resource.url}{path}"

            if stream:
                return await self._proxy_stream(url, body, resource)
            else:
                return await self._proxy_direct(url, body, resource)
        finally:
            resource.active_requests -= 1

    async def _proxy_direct(self, url: str, body: dict, resource: ComputeResource) -> web.Response:
        """Proxy a non-streaming request"""
        async with self.session.post(url, json=body) as resp:
            data = await resp.json()
            return web.json_response(data, status=resp.status)

    async def _proxy_stream(
        self, url: str, body: dict, resource: ComputeResource
    ) -> web.StreamResponse:
        """Proxy a streaming request"""
        response = web.StreamResponse(status=200, headers={"Content-Type": "application/x-ndjson"})
        await response.prepare(request)

        async with self.session.post(url, json=body) as resp:
            async for chunk in resp.content.iter_any():
                await response.write(chunk)

        await response.write_eof()
        return response


# ═══════════════════════════════════════════════════════════════════════
# HTTP SERVER
# ═══════════════════════════════════════════════════════════════════════

pool = UnifiedComputePool()


async def handle_health(request: web.Request) -> web.Response:
    """Health check endpoint"""
    status = pool.get_pool_status()
    return web.json_response(status)


async def handle_tags(request: web.Request) -> web.Response:
    """Aggregate all models from all resources"""
    status = pool.get_pool_status()

    # Build model list
    models = []
    for model_name in status["models_available"]:
        models.append(
            {
                "name": model_name,
                "model": model_name,
                "modified_at": "2026-02-03T00:00:00Z",
            }
        )

    return web.json_response({"models": models})


async def handle_chat(request: web.Request) -> web.Response:
    """Handle chat completions"""
    return await pool.proxy_request(request, "/api/chat")


async def handle_generate(request: web.Request) -> web.Response:
    """Handle text generation"""
    return await pool.proxy_request(request, "/api/generate")


async def handle_openai_chat(request: web.Request) -> web.Response:
    """Handle OpenAI-compatible chat completions"""
    return await pool.proxy_request(request, "/v1/chat/completions")


async def on_startup(app: web.Application):
    await pool.init()


async def on_cleanup(app: web.Application):
    await pool.close()


def create_app() -> web.Application:
    app = web.Application()

    app.router.add_get("/health", handle_health)
    app.router.add_get("/api/tags", handle_tags)
    app.router.add_post("/api/chat", handle_chat)
    app.router.add_post("/api/generate", handle_generate)
    app.router.add_post("/v1/chat/completions", handle_openai_chat)

    # Also handle root for compatibility
    app.router.add_get("/", lambda r: web.json_response({"status": "ok"}))

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    return app


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   ██╗   ██╗███╗   ██╗██╗███████╗██╗███████╗██████╗                    ║
║   ██║   ██║████╗  ██║██║██╔════╝██║██╔════╝██╔══██╗                   ║
║   ██║   ██║██╔██╗ ██║██║█████╗  ██║█████╗  ██║  ██║                   ║
║   ██║   ██║██║╚██╗██║██║██╔══╝  ██║██╔══╝  ██║  ██║                   ║
║   ╚██████╔╝██║ ╚████║██║██║     ██║███████╗██████╔╝                   ║
║    ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝╚═════╝                    ║
║                                                                       ║
║   ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗   ██╗████████╗███████╗       ║
║  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║   ██║╚══██╔══╝██╔════╝       ║
║  ██║     ██║   ██║██╔████╔██║██████╔╝██║   ██║   ██║   █████╗         ║
║  ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║   ██║   ██║   ██╔══╝         ║
║  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ╚██████╔╝   ██║   ███████╗       ║
║   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝      ╚═════╝    ╚═╝   ╚══════╝       ║
║                                                                       ║
║   ██████╗  ██████╗  ██████╗ ██╗                                       ║
║   ██╔══██╗██╔═══██╗██╔═══██╗██║                                       ║
║   ██████╔╝██║   ██║██║   ██║██║                                       ║
║   ██╔═══╝ ██║   ██║██║   ██║██║                                       ║
║   ██║     ╚██████╔╝╚██████╔╝███████╗                                  ║
║   ╚═╝      ╚═════╝  ╚═════╝ ╚══════╝                                  ║
║                                                                       ║
║   GPU + CPU treated as ONE unified resource pool                      ║
║   Endpoint: http://localhost:8080                                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
""")

    app = create_app()
    web.run_app(app, host="0.0.0.0", port=8080, print=None)
