#!/usr/bin/env python3
"""
ULTRON Cluster Router - Unified AI Cluster Gateway

Presents ULTRON (localhost) + Iron Legion (Kaiju) as a single Ollama-compatible endpoint.
- Load balances requests between nodes
- Automatic failover if a node is down
- Health monitoring
- Sticky sessions for streaming

Endpoint: http://localhost:8080 (Ollama-compatible API)

Tags: @PEAK @CLUSTER @ULTRON @IRON_LEGION #automation
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ClusterRouter")

# =============================================================================
# CLUSTER CONFIGURATION
# =============================================================================


@dataclass
class ClusterNode:
    """A node in the AI cluster"""

    name: str
    host: str
    port: int
    priority: int = 1  # Higher = preferred
    healthy: bool = True
    last_check: float = 0
    response_time_ms: float = 0
    active_requests: int = 0
    total_requests: int = 0
    errors: int = 0
    models: List[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def load(self) -> float:
        """Load score (lower is better)"""
        return self.active_requests + (self.response_time_ms / 1000)


# Define cluster nodes - GLOBAL COMPUTE POOL (All 3 HomeBase Machines)
# Priority is equal - let response time and model availability determine routing
CLUSTER_NODES = [
    # === ULTRON (Laptop) ===
    ClusterNode(
        name="ULTRON-GPU",
        host="localhost",
        port=11434,
        priority=1,  # RTX 5090 24GB + 24 cores + 64GB RAM
    ),
    ClusterNode(
        name="ULTRON-CPU",
        host="localhost",
        port=11435,
        priority=1,  # BitNet on Intel Ultra 9 275HX (CPU-only inference)
    ),
    # === KAIJU (Desktop) ===
    ClusterNode(
        name="Kaiju",
        host="<NAS_IP>",
        port=11434,
        priority=1,  # CPU-only + ~12 cores + ~32GB RAM
    ),
    # === NAS (Synology DS1821+) ===
    ClusterNode(
        name="NAS",
        host="<NAS_PRIMARY_IP>",
        port=11434,
        priority=1,  # AMD Ryzen V1500B (4 cores) + ~32GB RAM
    ),
]

# Router configuration
ROUTER_PORT = 8080
HEALTH_CHECK_INTERVAL = 30  # seconds
REQUEST_TIMEOUT = 300  # seconds
FAILOVER_THRESHOLD = 3  # errors before marking unhealthy


# =============================================================================
# CLUSTER ROUTER
# =============================================================================


class ClusterRouter:
    """Load balancer and router for the AI cluster"""

    def __init__(self, nodes: List[ClusterNode]):
        self.nodes = {n.name: n for n in nodes}
        self.session: Optional[aiohttp.ClientSession] = None
        self._health_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the router"""
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        self._health_task = asyncio.create_task(self._health_check_loop())
        logger.info("Cluster router started")

        # Initial health check
        await self._check_all_nodes()

    async def stop(self):
        """Stop the router"""
        if self._health_task:
            self._health_task.cancel()
        if self.session:
            await self.session.close()
        logger.info("Cluster router stopped")

    async def _health_check_loop(self):
        """Periodic health check of all nodes"""
        while True:
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)
            await self._check_all_nodes()

    async def _check_all_nodes(self):
        """Check health of all nodes"""
        for node in self.nodes.values():
            await self._check_node_health(node)

    async def _check_node_health(self, node: ClusterNode):
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
                    node.last_check = time.time()
                    logger.debug(
                        f"✓ {node.name}: {len(node.models)} models, {node.response_time_ms:.0f}ms"
                    )
                else:
                    node.healthy = False
                    logger.warning(f"✗ {node.name}: HTTP {resp.status}")
        except Exception as e:
            node.healthy = False
            logger.warning(f"✗ {node.name}: {e}")

    def get_best_node(self, model: Optional[str] = None) -> Optional[ClusterNode]:
        """Get the best available node for a request"""
        # Filter healthy nodes
        available = [n for n in self.nodes.values() if n.healthy]

        if not available:
            logger.error("No healthy nodes available!")
            return None

        # If model specified, prefer nodes that have it
        if model:
            with_model = [n for n in available if model in n.models]
            if with_model:
                available = with_model

        # Sort primarily by response time (fastest first), then by load
        # A slow node (>10s response) is heavily penalized
        def score(n: ClusterNode) -> float:
            # Penalize slow nodes heavily
            if n.response_time_ms > 10000:  # >10s is considered slow
                return n.response_time_ms + (n.active_requests * 10000)
            return n.response_time_ms + (n.active_requests * 1000)

        available.sort(key=score)

        chosen = available[0]
        logger.info(f"Selected {chosen.name} (response_time={chosen.response_time_ms:.0f}ms)")

        return chosen

    def get_all_models(self) -> List[Dict[str, Any]]:
        """Get combined model list from all healthy nodes"""
        models = {}
        for node in self.nodes.values():
            if node.healthy:
                for model_name in node.models:
                    if model_name not in models:
                        # Get full model info from first node that has it
                        models[model_name] = {
                            "name": model_name,
                            "model": model_name,
                            "available_on": [node.name],
                        }
                    else:
                        models[model_name]["available_on"].append(node.name)
        return list(models.values())

    async def proxy_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[bytes] = None,
        model: Optional[str] = None,
    ) -> web.StreamResponse:
        """Proxy a request to the best available node"""

        node = self.get_best_node(model)
        if not node:
            return web.json_response({"error": "No healthy nodes available"}, status=503)

        node.active_requests += 1
        node.total_requests += 1

        target_url = f"{node.url}{path}"
        logger.info(f"→ {node.name}: {method} {path}")

        try:
            start = time.time()

            async with self.session.request(
                method,
                target_url,
                headers={
                    k: v for k, v in headers.items() if k.lower() not in ["host", "content-length"]
                },
                data=body,
            ) as resp:
                # For streaming responses
                if resp.headers.get("Transfer-Encoding") == "chunked" or "stream" in path:
                    response = web.StreamResponse(
                        status=resp.status,
                        headers={
                            "Content-Type": resp.content_type or "application/json",
                            "Transfer-Encoding": "chunked",
                        },
                    )
                    await response.prepare(request)

                    async for chunk in resp.content.iter_any():
                        await response.write(chunk)

                    await response.write_eof()
                    return response

                # For regular responses
                body = await resp.read()
                node.response_time_ms = (time.time() - start) * 1000

                return web.Response(
                    status=resp.status,
                    headers={"Content-Type": resp.content_type or "application/json"},
                    body=body,
                )

        except Exception:
            node.errors += 1
            if node.errors >= FAILOVER_THRESHOLD:
                node.healthy = False
                logger.error(f"Node {node.name} marked unhealthy after {node.errors} errors")
            raise
        finally:
            node.active_requests -= 1


# =============================================================================
# HTTP HANDLERS
# =============================================================================

router = ClusterRouter(CLUSTER_NODES)


async def handle_tags(request: web.Request) -> web.Response:
    """GET /api/tags - List all models"""
    models = router.get_all_models()
    return web.json_response({"models": models})


async def handle_version(request: web.Request) -> web.Response:
    """GET /api/version - Return cluster version"""
    return web.json_response(
        {
            "version": "cluster-1.0.0",
            "nodes": [
                {
                    "name": n.name,
                    "healthy": n.healthy,
                    "models": len(n.models),
                    "response_time_ms": round(n.response_time_ms, 1),
                }
                for n in router.nodes.values()
            ],
        }
    )


async def handle_health(request: web.Request) -> web.Response:
    """GET /health - Cluster health check"""
    healthy_nodes = [n for n in router.nodes.values() if n.healthy]
    status = "healthy" if healthy_nodes else "unhealthy"
    return web.json_response(
        {
            "status": status,
            "healthy_nodes": len(healthy_nodes),
            "total_nodes": len(router.nodes),
            "nodes": {
                n.name: {
                    "healthy": n.healthy,
                    "models": n.models,
                    "active_requests": n.active_requests,
                    "total_requests": n.total_requests,
                    "response_time_ms": round(n.response_time_ms, 1),
                }
                for n in router.nodes.values()
            },
        }
    )


async def handle_proxy(request: web.Request) -> web.Response:
    """Proxy all other requests to the cluster"""
    body = await request.read() if request.body_exists else None

    # Extract model from body if present
    model = None
    if body:
        try:
            data = json.loads(body)
            model = data.get("model")
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    node = router.get_best_node(model)
    if not node:
        return web.json_response({"error": "No healthy nodes available"}, status=503)

    node.active_requests += 1
    node.total_requests += 1

    target_url = f"{node.url}{request.path_qs}"
    logger.info(f"→ {node.name}: {request.method} {request.path}")

    try:
        start = time.time()

        async with router.session.request(
            request.method,
            target_url,
            headers={
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length", "transfer-encoding"]
            },
            data=body,
        ) as resp:
            # Check if streaming response
            is_streaming = (
                resp.headers.get("Transfer-Encoding") == "chunked"
                or "stream" in str(request.path).lower()
                or (body and b'"stream":true' in body.lower() if body else False)
            )

            if is_streaming:
                response = web.StreamResponse(
                    status=resp.status,
                    headers={
                        "Content-Type": resp.content_type or "application/x-ndjson",
                    },
                )
                await response.prepare(request)

                async for chunk in resp.content.iter_any():
                    await response.write(chunk)

                await response.write_eof()
                node.response_time_ms = (time.time() - start) * 1000
                return response

            # Regular response
            response_body = await resp.read()
            node.response_time_ms = (time.time() - start) * 1000

            return web.Response(
                status=resp.status,
                headers={"Content-Type": resp.content_type or "application/json"},
                body=response_body,
            )

    except asyncio.TimeoutError:
        node.errors += 1
        logger.error(f"Timeout on {node.name}")
        return web.json_response({"error": "Request timeout"}, status=504)
    except Exception as e:
        node.errors += 1
        logger.error(f"Error on {node.name}: {e}")
        if node.errors >= FAILOVER_THRESHOLD:
            node.healthy = False
        return web.json_response({"error": str(e)}, status=502)
    finally:
        node.active_requests -= 1


# =============================================================================
# APPLICATION SETUP
# =============================================================================


async def on_startup(app: web.Application):
    """Start the cluster router"""
    await router.start()


async def on_cleanup(app: web.Application):
    """Stop the cluster router"""
    await router.stop()


def create_app() -> web.Application:
    """Create the web application"""
    app = web.Application()

    # Lifecycle
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    # Routes
    app.router.add_get("/api/tags", handle_tags)
    app.router.add_get("/api/version", handle_version)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/", handle_health)

    # Proxy all other routes
    app.router.add_route("*", "/api/{path:.*}", handle_proxy)
    app.router.add_route("*", "/v1/{path:.*}", handle_proxy)

    return app


def main():
    """Main entry point"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    GLOBAL COMPUTE POOL                                   ║
║                    All HomeBase Machines United                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  Unified Endpoint: http://localhost:{ROUTER_PORT}                              ║
║                                                                          ║
║  ┌─────────────────────────────────────────────────────────────────────┐ ║
║  │  ULTRON (Laptop)                                                    │ ║
║  │    • ULTRON-GPU (localhost:11434) - RTX 5090 24GB + 64GB RAM        │ ║
║  │    • ULTRON-CPU (localhost:11435) - BitNet on Ultra 9 (24 cores)    │ ║
║  ├─────────────────────────────────────────────────────────────────────┤ ║
║  │  KAIJU (Desktop)                                                    │ ║
║  │    • Kaiju (<NAS_IP>:11434) - CPU ~12 cores + ~32GB RAM          │ ║
║  ├─────────────────────────────────────────────────────────────────────┤ ║
║  │  NAS (Synology DS1821+)                                             │ ║
║  │    • NAS (<NAS_PRIMARY_IP>:11434) - Ryzen 4 cores + ~32GB RAM            │ ║
║  └─────────────────────────────────────────────────────────────────────┘ ║
║                                                                          ║
║  TOTAL POOL: 24GB GPU + ~40 cores + ~128GB RAM                           ║
║                                                                          ║
║  Endpoints:                                                              ║
║    GET  /health               - Pool health status                       ║
║    GET  /api/tags             - List all models across pool              ║
║    POST /api/chat             - Chat (routes to best node)               ║
║    POST /v1/chat/completions  - OpenAI-compatible                        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

    app = create_app()
    web.run_app(app, host="0.0.0.0", port=ROUTER_PORT, print=None)


if __name__ == "__main__":
    main()
