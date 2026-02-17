#!/usr/bin/env python3
"""Test the cluster router."""

import json
import time

import requests

ROUTER_URL = "http://localhost:8080"

print("=== Testing Cluster Router ===\n")

# 1. Health check
print("1. Health check:")
try:
    r = requests.get(f"{ROUTER_URL}/health", timeout=10)
    print(f"   Status: {r.status_code}")
    health = r.json()
    for name, info in health.get("nodes", {}).items():
        healthy = info["healthy"]
        rt = info["response_time_ms"]
        models = len(info.get("models", []))
        print(f"   {name}: healthy={healthy}, response_time={rt:.0f}ms, models={models}")
except Exception as e:
    print(f"   FAILED: {e}")

# 2. Test OpenAI endpoint (non-streaming)
print("\n2. OpenAI endpoint (non-streaming):")
payload = {
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Say OK"}],
    "stream": False,
}
start = time.time()
try:
    r = requests.post(f"{ROUTER_URL}/v1/chat/completions", json=payload, timeout=120)
    elapsed = time.time() - start
    print(f"   Status: {r.status_code}")
    print(f"   Time: {elapsed:.1f}s")
    if r.status_code == 200:
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        print(f"   Response: {content[:100]}")
    else:
        print(f"   Error: {r.text[:200]}")
except requests.exceptions.Timeout:
    print(f"   TIMEOUT after {time.time() - start:.1f}s")
except Exception as e:
    print(f"   FAILED: {e}")

# 3. Test native Ollama endpoint (non-streaming)
print("\n3. Native Ollama endpoint (non-streaming):")
payload = {
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Say OK"}],
    "stream": False,
}
start = time.time()
try:
    r = requests.post(f"{ROUTER_URL}/api/chat", json=payload, timeout=120)
    elapsed = time.time() - start
    print(f"   Status: {r.status_code}")
    print(f"   Time: {elapsed:.1f}s")
    if r.status_code == 200:
        data = r.json()
        content = data.get("message", {}).get("content", "")
        print(f"   Response: {content[:100]}")
    else:
        print(f"   Error: {r.text[:200]}")
except requests.exceptions.Timeout:
    print(f"   TIMEOUT after {time.time() - start:.1f}s")
except Exception as e:
    print(f"   FAILED: {e}")

# 4. Test streaming
print("\n4. OpenAI endpoint (streaming):")
payload = {
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Say OK"}],
    "stream": True,
}
start = time.time()
try:
    r = requests.post(f"{ROUTER_URL}/v1/chat/completions", json=payload, timeout=60, stream=True)
    print(f"   Status: {r.status_code}")
    chunks = 0
    content = ""
    for line in r.iter_lines():
        if line:
            chunks += 1
            if chunks <= 3:
                print(f"   Chunk {chunks}: {line[:80]}")
            try:
                if line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    content += delta
            except:
                pass
    print(f"   Total chunks: {chunks}")
    print(f"   Time: {time.time() - start:.1f}s")
    print(f"   Content: {content[:100]}")
except requests.exceptions.Timeout:
    print(f"   TIMEOUT after {time.time() - start:.1f}s")
except Exception as e:
    print(f"   FAILED: {e}")

print("\n=== Done ===")
