#!/usr/bin/env python3
"""
BitNet Ollama-Compatible API Server

Exposes Microsoft BitNet models via an Ollama-compatible REST API.
This allows the cluster router to use BitNet as another node.

Endpoints:
    GET  /api/tags          - List available models
    GET  /api/version       - Server version
    POST /api/chat          - Chat completion (Ollama native)
    POST /api/generate      - Text generation (Ollama native)
    POST /v1/chat/completions - OpenAI-compatible chat
    GET  /health            - Health check

Usage:
    python bitnet_api_server.py [--port 11435] [--threads 16]

Tags: @PEAK @CLUSTER @BITNET #automation
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncGenerator

from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("BitNetAPI")

# =============================================================================
# CONFIGURATION
# =============================================================================

BITNET_DIR = Path(os.environ.get("BITNET_DIR", Path.home() / "bitnet"))
MODELS_DIR = BITNET_DIR / "models"
DEFAULT_PORT = 11435  # Different from Ollama's 11434
DEFAULT_THREADS = 16

# Available models
AVAILABLE_MODELS = {
    "bitnet-2b": {
        "name": "bitnet-2b",
        "model": "bitnet-2b",
        "path": MODELS_DIR / "BitNet-b1.58-2B-4T" / "ggml-model-i2_s.gguf",
        "size": 2_410_000_000,
        "parameter_size": "2.4B",
        "quantization": "I2_S (1.58-bit)",
        "family": "bitnet",
        "context_length": 4096,
    },
}


@dataclass
class ServerConfig:
    port: int = DEFAULT_PORT
    threads: int = DEFAULT_THREADS
    host: str = "0.0.0.0"


config = ServerConfig()


# =============================================================================
# BITNET INFERENCE
# =============================================================================


def get_llama_cli() -> Path:
    """Get path to llama-cli executable"""
    cli_path = BITNET_DIR / "build" / "bin" / "llama-cli.exe"
    if not cli_path.exists():
        cli_path = BITNET_DIR / "build" / "bin" / "llama-cli"
    return cli_path


async def generate_text(
    prompt: str,
    model: str = "bitnet-2b",
    max_tokens: int = 256,
    temperature: float = 0.8,
    stream: bool = False,
) -> AsyncGenerator[str, None]:
    """Generate text using BitNet"""

    model_info = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["bitnet-2b"])
    model_path = model_info["path"]

    if not model_path.exists():
        yield json.dumps({"error": f"Model not found: {model_path}"})
        return

    llama_cli = get_llama_cli()
    if not llama_cli.exists():
        yield json.dumps({"error": f"llama-cli not found: {llama_cli}"})
        return

    cmd = [
        str(llama_cli),
        "-m",
        str(model_path),
        "-p",
        prompt,
        "-n",
        str(max_tokens),
        "--threads",
        str(config.threads),
        "--temp",
        str(temperature),
        "--no-display-prompt",
    ]

    logger.info(f"Running BitNet: {model} with {config.threads} threads")
    start_time = time.time()

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        full_response = ""

        if stream:
            # Stream output character by character
            while True:
                char = await process.stdout.read(1)
                if not char:
                    break
                decoded = char.decode("utf-8", errors="replace")
                full_response += decoded
                yield decoded
        else:
            # Wait for complete response
            stdout, stderr = await process.communicate()
            full_response = stdout.decode("utf-8", errors="replace")
            yield full_response

        elapsed = time.time() - start_time
        tokens = len(full_response.split())
        logger.info(f"Generated {tokens} tokens in {elapsed:.2f}s")

    except Exception as e:
        logger.error(f"BitNet error: {e}")
        yield json.dumps({"error": str(e)})


# =============================================================================
# API HANDLERS
# =============================================================================


async def handle_tags(request: web.Request) -> web.Response:
    """GET /api/tags - List available models"""
    models = []
    for model_id, info in AVAILABLE_MODELS.items():
        if info["path"].exists():
            models.append(
                {
                    "name": info["name"],
                    "model": info["model"],
                    "modified_at": "2024-01-01T00:00:00Z",
                    "size": info["size"],
                    "digest": f"bitnet-{model_id}",
                    "details": {
                        "parent_model": "",
                        "format": "gguf",
                        "family": info["family"],
                        "parameter_size": info["parameter_size"],
                        "quantization_level": info["quantization"],
                    },
                }
            )
    return web.json_response({"models": models})


async def handle_version(request: web.Request) -> web.Response:
    """GET /api/version - Server version"""
    return web.json_response(
        {
            "version": "bitnet-1.0.0",
            "backend": "bitnet.cpp",
            "threads": config.threads,
        }
    )


async def handle_health(request: web.Request) -> web.Response:
    """GET /health - Health check"""
    llama_cli = get_llama_cli()
    healthy = llama_cli.exists()

    return web.json_response(
        {
            "status": "healthy" if healthy else "unhealthy",
            "backend": "bitnet",
            "threads": config.threads,
            "models": len([m for m in AVAILABLE_MODELS.values() if m["path"].exists()]),
        }
    )


async def handle_chat(request: web.Request) -> web.Response:
    """POST /api/chat - Ollama chat completion"""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    model = data.get("model", "bitnet-2b")
    messages = data.get("messages", [])
    stream = data.get("stream", False)
    max_tokens = data.get("options", {}).get("num_predict", 256)
    temperature = data.get("options", {}).get("temperature", 0.8)

    # Convert messages to prompt
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt += f"System: {content}\n"
        elif role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    prompt += "Assistant:"

    if stream:
        response = web.StreamResponse(
            status=200,
            headers={"Content-Type": "application/x-ndjson"},
        )
        await response.prepare(request)

        full_content = ""
        async for chunk in generate_text(prompt, model, max_tokens, temperature, stream=True):
            full_content += chunk
            chunk_data = {
                "model": model,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "message": {"role": "assistant", "content": chunk},
                "done": False,
            }
            await response.write((json.dumps(chunk_data) + "\n").encode())

        # Final message
        final_data = {
            "model": model,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message": {"role": "assistant", "content": ""},
            "done": True,
            "total_duration": 0,
            "eval_count": len(full_content.split()),
        }
        await response.write((json.dumps(final_data) + "\n").encode())
        await response.write_eof()
        return response
    else:
        full_content = ""
        async for chunk in generate_text(prompt, model, max_tokens, temperature, stream=False):
            full_content += chunk

        return web.json_response(
            {
                "model": model,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "message": {"role": "assistant", "content": full_content.strip()},
                "done": True,
            }
        )


async def handle_generate(request: web.Request) -> web.Response:
    """POST /api/generate - Ollama text generation"""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    model = data.get("model", "bitnet-2b")
    prompt = data.get("prompt", "")
    stream = data.get("stream", False)
    max_tokens = data.get("options", {}).get("num_predict", 256)
    temperature = data.get("options", {}).get("temperature", 0.8)

    if stream:
        response = web.StreamResponse(
            status=200,
            headers={"Content-Type": "application/x-ndjson"},
        )
        await response.prepare(request)

        async for chunk in generate_text(prompt, model, max_tokens, temperature, stream=True):
            chunk_data = {
                "model": model,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "response": chunk,
                "done": False,
            }
            await response.write((json.dumps(chunk_data) + "\n").encode())

        final_data = {"model": model, "done": True}
        await response.write((json.dumps(final_data) + "\n").encode())
        await response.write_eof()
        return response
    else:
        full_content = ""
        async for chunk in generate_text(prompt, model, max_tokens, temperature, stream=False):
            full_content += chunk

        return web.json_response(
            {
                "model": model,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "response": full_content.strip(),
                "done": True,
            }
        )


async def handle_openai_chat(request: web.Request) -> web.Response:
    """POST /v1/chat/completions - OpenAI-compatible chat"""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    model = data.get("model", "bitnet-2b")
    messages = data.get("messages", [])
    stream = data.get("stream", False)
    max_tokens = data.get("max_tokens", 256)
    temperature = data.get("temperature", 0.8)

    # Convert messages to prompt
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt += f"System: {content}\n"
        elif role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    prompt += "Assistant:"

    chat_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())

    if stream:
        response = web.StreamResponse(
            status=200,
            headers={"Content-Type": "text/event-stream"},
        )
        await response.prepare(request)

        async for chunk in generate_text(prompt, model, max_tokens, temperature, stream=True):
            chunk_data = {
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None,
                    }
                ],
            }
            await response.write(f"data: {json.dumps(chunk_data)}\n\n".encode())

        # Final chunk
        final_data = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        }
        await response.write(f"data: {json.dumps(final_data)}\n\n".encode())
        await response.write(b"data: [DONE]\n\n")
        await response.write_eof()
        return response
    else:
        full_content = ""
        async for chunk in generate_text(prompt, model, max_tokens, temperature, stream=False):
            full_content += chunk

        return web.json_response(
            {
                "id": chat_id,
                "object": "chat.completion",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": full_content.strip()},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(full_content.split()),
                    "total_tokens": len(prompt.split()) + len(full_content.split()),
                },
            }
        )


# =============================================================================
# APPLICATION SETUP
# =============================================================================


def create_app() -> web.Application:
    """Create the web application"""
    app = web.Application()

    # Routes
    app.router.add_get("/api/tags", handle_tags)
    app.router.add_get("/api/version", handle_version)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/", handle_health)
    app.router.add_post("/api/chat", handle_chat)
    app.router.add_post("/api/generate", handle_generate)
    # OpenAI-compatible chat endpoints (both with and without /v1 prefix for LiteLLM compatibility)
    app.router.add_post("/v1/chat/completions", handle_openai_chat)
    app.router.add_post("/chat/completions", handle_openai_chat)

    return app


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="BitNet Ollama-Compatible API Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help="CPU threads to use")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    config.port = args.port
    config.threads = args.threads
    config.host = args.host

    # Check BitNet installation
    llama_cli = get_llama_cli()
    if not llama_cli.exists():
        logger.error(f"BitNet not found at {llama_cli}")
        sys.exit(1)

    # Check for models
    available = [m for m in AVAILABLE_MODELS.values() if m["path"].exists()]
    if not available:
        logger.error("No BitNet models found!")
        sys.exit(1)

    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    BITNET API SERVER                             ║
║                                                                  ║
║  Endpoint: http://{config.host}:{config.port}                            ║
║  Threads:  {config.threads}                                              ║
║                                                                  ║
║  Models:                                                         ║""")
    for m in available:
        print(f"║    • {m['name']} ({m['parameter_size']})                             ║")
    print("""║                                                                  ║
║  Endpoints:                                                      ║
║    GET  /health              - Health check                      ║
║    GET  /api/tags            - List models                       ║
║    POST /api/chat            - Ollama chat                       ║
║    POST /api/generate        - Ollama generate                   ║
║    POST /v1/chat/completions - OpenAI chat                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

    app = create_app()
    web.run_app(app, host=config.host, port=config.port, print=None)


if __name__ == "__main__":
    main()
