#!/usr/bin/env python3
"""
Federated Compute Pool Router

Supports multiple labs joining together to compound compute resources.
New labs can be added via config file or REST API.

Architecture:
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LUMINA FEDERATION                                       │
│                     http://localhost:8080                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │    HomeBase Lab     │  │    Remote Lab 1     │  │    Remote Lab 2     │  │
│  │    (Primary)        │  │   (via Tailscale)   │  │   (via Tunnel)      │  │
│  │                     │  │                     │  │                     │  │
│  │  • ULTRON-GPU       │  │  • Node-A           │  │  • Node-X           │  │
│  │  • ULTRON-CPU       │  │  • Node-B           │  │  • Node-Y           │  │
│  │  • Kaiju            │  │                     │  │                     │  │
│  │  • NAS              │  │                     │  │                     │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
│            │                       │                       │                │
│            └───────────────────────┴───────────────────────┘                │
│                                    │                                        │
│                            Unified Routing                                  │
│                    (fastest node wins, failover)                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Tags: @PEAK @FEDERATION @CLUSTER #automation
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("FederatedPool")

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "federated_compute_pool.json"
ROUTER_PORT = 8080
HEALTH_CHECK_INTERVAL = 30
REQUEST_TIMEOUT = 300


@dataclass
class ComputeNode:
    """A compute node in the federation"""

    name: str
    host: str
    port: int
    lab: str
    node_type: str = "cpu"  # gpu, cpu
    healthy: bool = False
    response_time_ms: float = 99999
    active_requests: int = 0
    total_requests: int = 0
    models: List[str] = field(default_factory=list)
    specs: Dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def is_gpu(self) -> bool:
        return self.node_type == "gpu"


@dataclass
class Lab:
    """A lab in the federation"""

    name: str
    location: str
    status: str = "active"
    nodes: List[ComputeNode] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def healthy_nodes(self) -> List[ComputeNode]:
        return [n for n in self.nodes if n.healthy]


# =============================================================================
# FEDERATED POOL MANAGER
# =============================================================================


class FederatedPool:
    """Manages the federated compute pool across all labs"""

    def __init__(self):
        self.labs: Dict[str, Lab] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._health_task: Optional[asyncio.Task] = None

    def load_config(self):
        """Load labs from config file"""
        if not CONFIG_PATH.exists():
            logger.warning(f"Config not found: {CONFIG_PATH}")
            return

        with open(CONFIG_PATH) as f:
            config = json.load(f)

        for lab_id, lab_data in config.get("labs", {}).items():
            if lab_data.get("status") != "active":
                continue

            lab = Lab(
                name=lab_data["name"],
                location=lab_data.get("location", "Unknown"),
                status=lab_data.get("status", "active"),
            )

            for node_data in lab_data.get("nodes", []):
                node = ComputeNode(
                    name=node_data["name"],
                    host=node_data["host"],
                    port=node_data["port"],
                    lab=lab_id,
                    node_type=node_data.get("type", "cpu"),
                    specs=node_data.get("specs", {}),
                )
                lab.nodes.append(node)

            self.labs[lab_id] = lab
            logger.info(f"Loaded lab: {lab.name} ({len(lab.nodes)} nodes)")

    def add_lab(self, lab_id: str, lab_data: dict) -> Lab:
        """Dynamically add a new lab"""
        lab = Lab(
            name=lab_data["name"],
            location=lab_data.get("location", "Unknown"),
            status="active",
        )

        for node_data in lab_data.get("nodes", []):
            node = ComputeNode(
                name=node_data["name"],
                host=node_data["host"],
                port=node_data["port"],
                lab=lab_id,
                node_type=node_data.get("type", "cpu"),
                specs=node_data.get("specs", {}),
            )
            lab.nodes.append(node)

        self.labs[lab_id] = lab
        logger.info(f"Added new lab: {lab.name} ({len(lab.nodes)} nodes)")

        # Save to config
        self._save_config()

        return lab

    def _save_config(self):
        """Save current state to config file"""
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f:
                config = json.load(f)
        else:
            config = {"labs": {}}

        for lab_id, lab in self.labs.items():
            config["labs"][lab_id] = {
                "name": lab.name,
                "location": lab.location,
                "status": lab.status,
                "nodes": [
                    {
                        "name": n.name,
                        "host": n.host,
                        "port": n.port,
                        "type": n.node_type,
                        "specs": n.specs,
                    }
                    for n in lab.nodes
                ],
            }

        # Update totals
        all_nodes = self.get_all_nodes()
        config["federation_totals"] = {
            "_computed": True,
            "total_labs": len(self.labs),
            "total_nodes": len(all_nodes),
            "total_gpu_vram_gb": sum(
                n.specs.get("gpu_vram_gb", 0) or 24 if n.is_gpu else 0 for n in all_nodes
            ),
            "total_cpu_cores": sum(n.specs.get("cpu_cores", 0) or 8 for n in all_nodes),
            "total_ram_gb": sum(n.specs.get("ram_gb", 0) or 32 for n in all_nodes),
        }

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)

    def get_all_nodes(self) -> List[ComputeNode]:
        """Get all nodes across all labs"""
        nodes = []
        for lab in self.labs.values():
            if lab.is_active:
                nodes.extend(lab.nodes)
        return nodes

    def get_healthy_nodes(self) -> List[ComputeNode]:
        """Get all healthy nodes"""
        return [n for n in self.get_all_nodes() if n.healthy]

    async def start(self):
        """Start the federated pool"""
        self.load_config()
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self._health_task = asyncio.create_task(self._health_loop())
        await self._check_all_nodes()
        logger.info(
            f"Federated pool started: {len(self.labs)} labs, {len(self.get_all_nodes())} nodes"
        )

    async def stop(self):
        """Stop the federated pool"""
        if self._health_task:
            self._health_task.cancel()
        if self.session:
            await self.session.close()

    async def _health_loop(self):
        """Periodic health checks"""
        while True:
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
            await self._check_all_nodes()

    async def _check_all_nodes(self):
        """Check health of all nodes"""
        tasks = [self._check_node(n) for n in self.get_all_nodes()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_node(self, node: ComputeNode):
        """Check health of a single node"""
        try:
            start = time.time()
            async with self.session.get(
                f"{node.url}/api/tags", timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    node.models = [m["name"] for m in data.get("models", [])]
                    node.healthy = True
                    node.response_time_ms = (time.time() - start) * 1000
                else:
                    node.healthy = False
        except Exception:
            node.healthy = False
            node.response_time_ms = 99999

    def select_node(
        self, model: Optional[str] = None, prefer_gpu: bool = False
    ) -> Optional[ComputeNode]:
        """Select the best node for a request"""
        available = self.get_healthy_nodes()
        if not available:
            return None

        # Filter by model if specified
        if model:
            with_model = [n for n in available if model in n.models]
            if with_model:
                available = with_model

        # Prefer GPU nodes for large models
        if prefer_gpu or (model and any(s in model for s in ["32b", "70b", "72b"])):
            gpu_nodes = [n for n in available if n.is_gpu]
            if gpu_nodes:
                available = gpu_nodes

        # Sort by response time (fastest first)
        available.sort(key=lambda n: n.response_time_ms + (n.active_requests * 1000))

        return available[0] if available else None

    def get_status(self) -> Dict[str, Any]:
        """Get federation status"""
        all_nodes = self.get_all_nodes()
        healthy = self.get_healthy_nodes()

        all_models = set()
        for n in healthy:
            all_models.update(n.models)

        return {
            "federation": "Lumina Federation",
            "status": "healthy" if healthy else "degraded",
            "labs": {
                lab_id: {
                    "name": lab.name,
                    "location": lab.location,
                    "status": lab.status,
                    "nodes_online": len(lab.healthy_nodes),
                    "nodes_total": len(lab.nodes),
                    "nodes": {
                        n.name: {
                            "healthy": n.healthy,
                            "type": n.node_type,
                            "response_ms": round(n.response_time_ms, 1),
                            "models": len(n.models),
                            "requests": n.total_requests,
                        }
                        for n in lab.nodes
                    },
                }
                for lab_id, lab in self.labs.items()
            },
            "totals": {
                "labs": len(self.labs),
                "nodes_online": len(healthy),
                "nodes_total": len(all_nodes),
                "models_available": len(all_models),
            },
            "models": sorted(all_models),
        }


# =============================================================================
# HTTP HANDLERS
# =============================================================================

pool = FederatedPool()


async def handle_health(request: web.Request) -> web.Response:
    """GET /health - Federation health"""
    return web.json_response(pool.get_status())


async def handle_tags(request: web.Request) -> web.Response:
    """GET /api/tags - All models"""
    models = {}
    for node in pool.get_healthy_nodes():
        for model_name in node.models:
            if model_name not in models:
                models[model_name] = {
                    "name": model_name,
                    "model": model_name,
                    "available_on": [f"{node.lab}/{node.name}"],
                }
            else:
                models[model_name]["available_on"].append(f"{node.lab}/{node.name}")

    return web.json_response({"models": list(models.values())})


async def handle_add_lab(request: web.Request) -> web.Response:
    """POST /federation/labs - Add a new lab"""
    try:
        data = await request.json()
        lab_id = data.get("id") or data["name"].lower().replace(" ", "_")
        lab = pool.add_lab(lab_id, data)

        # Check health of new nodes
        for node in lab.nodes:
            await pool._check_node(node)

        return web.json_response(
            {
                "status": "success",
                "lab": lab_id,
                "nodes_added": len(lab.nodes),
                "nodes_healthy": len(lab.healthy_nodes),
            }
        )
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


async def handle_proxy(request: web.Request) -> web.Response:
    """Proxy requests to best available node"""
    body = await request.read() if request.body_exists else None

    # Extract model from request
    model = None
    if body:
        try:
            data = json.loads(body)
            model = data.get("model")
        except:
            pass

    node = pool.select_node(model)
    if not node:
        return web.json_response({"error": "No healthy nodes"}, status=503)

    node.active_requests += 1
    node.total_requests += 1

    try:
        target = f"{node.url}{request.path_qs}"
        logger.info(f"-> {node.lab}/{node.name}: {request.method} {request.path}")

        async with pool.session.request(
            request.method,
            target,
            headers={
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length"]
            },
            data=body,
        ) as resp:
            # Streaming response
            if resp.headers.get("Transfer-Encoding") == "chunked":
                response = web.StreamResponse(
                    status=resp.status,
                    headers={"Content-Type": resp.content_type or "application/json"},
                )
                await response.prepare(request)
                async for chunk in resp.content.iter_any():
                    await response.write(chunk)
                await response.write_eof()
                return response

            # Regular response
            return web.Response(
                status=resp.status,
                headers={"Content-Type": resp.content_type or "application/json"},
                body=await resp.read(),
            )
    except Exception as e:
        return web.json_response({"error": str(e)}, status=502)
    finally:
        node.active_requests -= 1


async def on_startup(app: web.Application):
    await pool.start()


async def on_cleanup(app: web.Application):
    await pool.stop()


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # Federation management
    app.router.add_get("/health", handle_health)
    app.router.add_get("/federation/status", handle_health)
    app.router.add_post("/federation/labs", handle_add_lab)

    # Ollama-compatible
    app.router.add_get("/api/tags", handle_tags)
    app.router.add_get("/", handle_health)

    # Proxy everything else
    app.router.add_route("*", "/api/{path:.*}", handle_proxy)
    app.router.add_route("*", "/v1/{path:.*}", handle_proxy)

    return app


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██╗     ██╗   ██╗███╗   ███╗██╗███╗   ██╗ █████╗                            ║
║   ██║     ██║   ██║████╗ ████║██║████╗  ██║██╔══██╗                           ║
║   ██║     ██║   ██║██╔████╔██║██║██╔██╗ ██║███████║                           ║
║   ██║     ██║   ██║██║╚██╔╝██║██║██║╚██╗██║██╔══██║                           ║
║   ███████╗╚██████╔╝██║ ╚═╝ ██║██║██║ ╚████║██║  ██║                           ║
║   ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝                           ║
║                                                                               ║
║   ███████╗███████╗██████╗ ███████╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ║
║   ██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ║
║   █████╗  █████╗  ██║  ██║█████╗  ██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ║
║   ██╔══╝  ██╔══╝  ██║  ██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗║
║   ██║     ███████╗██████╔╝███████╗██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚██║
║   ╚═╝     ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   Multiple Labs → One Unified Compute Pool                                    ║
║   Endpoint: http://localhost:8080                                             ║
║                                                                               ║
║   Add a new lab via API:                                                      ║
║   POST /federation/labs                                                       ║
║   {                                                                           ║
║     "name": "Remote Lab",                                                     ║
║     "location": "Office",                                                     ║
║     "nodes": [                                                                ║
║       {"name": "GPU-Server", "host": "100.x.x.x", "port": 11434, "type": "gpu"}║
║     ]                                                                         ║
║   }                                                                           ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

    app = create_app()
    web.run_app(app, host="0.0.0.0", port=ROUTER_PORT, print=None)


if __name__ == "__main__":
    main()
