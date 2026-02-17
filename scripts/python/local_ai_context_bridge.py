#!/usr/bin/env python3
"""
Local AI Context Bridge - Give Ollama Models Homelab-Wide Knowledge

Problem: Local Ollama models say "I don't have access to local files"
Solution: Inject relevant project context into the system prompt automatically

Architecture:
1. Index key project documentation (docs/, config/, .cursor/rules/)
2. Build topic-based context chunks
3. Inject relevant context into Ollama API calls
4. Provide a "smart" local AI interface

Tags: #RAG #OLLAMA #CONTEXT #KNOWLEDGE-BASE @JARVIS @LUMINA @DOIT
"""

import hashlib
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LocalAIContextBridge")

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434"

# Cloud API options for faster inference (when local is too slow)
CLOUD_PROVIDERS = {
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "model": "claude-3-haiku-20240307",  # Fast and cheap
        "env_key": "ANTHROPIC_API_KEY",
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o-mini",  # Fast and cheap
        "env_key": "OPENAI_API_KEY",
    },
}

# Key documentation directories to index
DOC_PATHS = [
    "docs/system/",
    "docs/workflow/",
    "docs/",
    "config/",
    ".cursor/rules/",
    ".cursor/memories/",
    # R5 Living Context Matrix - dynamic knowledge from sessions
    "--serve/data/r5_living_matrix/",
    "data/r5_living_matrix/",
]

# File extensions to index
INDEXABLE_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".txt", ".mdc"}

# Max context size (characters) to inject
MAX_CONTEXT_SIZE = 16000  # ~4K tokens

# =============================================================================
# UNIFIED AI TIER SYSTEM
# =============================================================================
# Strategy: Local/Free by default, Cloud/Premium only when needed
# Auto-escalation: Start free, retry on cloud if local fails or is insufficient
# =============================================================================

MODEL_TIERS = {
    # -------------------------------------------------------------------------
    # FREE TIERS (Local compute - $0)
    # -------------------------------------------------------------------------
    "free-fast": {
        "model": "2b",  # BitNet model ID
        "max_context": 4000,
        "description": "FREE: BitNet CPU (2B) - 50+ tok/s, any machine",
        "type": "bitnet",
        "cost": "free",
        "speed": "2-3s",
        "quality": "basic",
    },
    "free-balanced": {
        "model": "llama3.2:3b",
        "max_context": 6000,
        "description": "FREE: GPU Ollama (3B) - project queries, 10-20s",
        "type": "gpu",
        "cost": "free",
        "speed": "10-20s",
        "quality": "good",
    },
    "free-quality": {
        "model": "qwen2.5:7b",
        "max_context": 12000,
        "description": "FREE: GPU Ollama (7B) - detailed analysis, 30-60s",
        "type": "gpu",
        "cost": "free",
        "speed": "30-60s",
        "quality": "great",
    },
    # -------------------------------------------------------------------------
    # CLOUD TIERS (Paid - costs tokens)
    # -------------------------------------------------------------------------
    "cloud-fast": {
        "model": "claude-3-haiku-20240307",
        "max_context": 16000,
        "description": "CLOUD $: Haiku - fast & cheap, 2-3s",
        "type": "cloud",
        "cost": "low",
        "speed": "2-3s",
        "quality": "good",
        "provider": "anthropic",
    },
    "cloud-premium": {
        "model": "claude-sonnet-4-20250514",
        "max_context": 32000,
        "description": "CLOUD $$$: Sonnet - best quality, complex problems",
        "type": "cloud",
        "cost": "high",
        "speed": "5-10s",
        "quality": "best",
        "provider": "anthropic",
    },
    # -------------------------------------------------------------------------
    # SMART TIERS (Auto-routing)
    # -------------------------------------------------------------------------
    "auto": {
        "model": "auto",
        "max_context": 8000,
        "description": "AUTO: Starts free, escalates to cloud if needed",
        "type": "auto",
        "cost": "variable",
        "speed": "variable",
        "quality": "adaptive",
        "escalation_chain": ["free-fast", "free-balanced", "cloud-fast"],
    },
    "cluster": {
        "model": "llama3.2:3b",
        "max_context": 8000,
        "description": "CLUSTER: Auto-routes across homelab (GPU/CPU)",
        "type": "cluster",
        "cost": "free",
        "speed": "10-30s",
        "quality": "good",
    },
    # -------------------------------------------------------------------------
    # LEGACY ALIASES (backward compatibility)
    # -------------------------------------------------------------------------
    "fast": {
        "model": "qwen2.5-coder:1.5b-base",
        "max_context": 2000,
        "description": "LEGACY → use free-fast",
        "type": "gpu",
        "cost": "free",
        "alias_for": "free-fast",
    },
    "balanced": {
        "model": "llama3.2:3b",
        "max_context": 6000,
        "description": "LEGACY → use free-balanced",
        "type": "gpu",
        "cost": "free",
        "alias_for": "free-balanced",
    },
    "quality": {
        "model": "qwen2.5:7b",
        "max_context": 12000,
        "description": "LEGACY → use free-quality",
        "type": "gpu",
        "cost": "free",
        "alias_for": "free-quality",
    },
    "cloud": {
        "model": "claude-3-haiku-20240307",
        "max_context": 16000,
        "description": "LEGACY → use cloud-fast",
        "type": "cloud",
        "cost": "low",
        "alias_for": "cloud-fast",
    },
    "bitnet-fast": {
        "model": "2b",
        "max_context": 4000,
        "description": "LEGACY → use free-fast",
        "type": "bitnet",
        "cost": "free",
        "alias_for": "free-fast",
    },
    "bitnet-quality": {
        "model": "8b",
        "max_context": 6000,
        "description": "LEGACY → use free-quality (BitNet 8B)",
        "type": "bitnet",
        "cost": "free",
    },
}

# Default tier (saves money)
DEFAULT_TIER = "free-balanced"

# Escalation chain for auto tier
ESCALATION_CHAIN = ["free-fast", "free-balanced", "free-quality", "cloud-fast", "cloud-premium"]

# Homelab cluster nodes for distributed processing
CLUSTER_NODES = {
    # GPU nodes
    "ultron": {"ip": "127.0.0.1", "port": 11434, "gpu": "RTX 5090", "type": "gpu"},
    "kaiju": {"ip": "<NAS_IP>", "port": 11434, "gpu": "RTX 3090", "type": "gpu"},
    # CPU nodes (BitNet)
    "ultron-cpu": {"ip": "127.0.0.1", "type": "cpu", "bitnet": True},
    "kaiju-cpu": {"ip": "<NAS_IP>", "type": "cpu", "bitnet": True},
    "nas-cpu": {"ip": "<NAS_PRIMARY_IP>", "type": "cpu", "bitnet": True},
}


class LocalAIContextBridge:
    """
    Bridge that gives local Ollama models access to project knowledge.

    Instead of RAG with embeddings, uses keyword-based retrieval for simplicity
    and injects relevant context into system prompts.
    """

    def __init__(self, project_path: Optional[Path] = None):
        self.project_root = Path(project_path) if project_path else project_root
        self.index_path = self.project_root / "data" / "local_ai_context"
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Document index: {doc_path: {title, summary, keywords, content_hash}}
        self.doc_index: Dict[str, Dict[str, Any]] = {}

        # Topic index: {keyword: [doc_paths]}
        self.topic_index: Dict[str, List[str]] = {}

        # Cache of document contents
        self.content_cache: Dict[str, str] = {}

        # Load existing index
        self._load_index()

        logger.info("=" * 80)
        logger.info("🌉 LOCAL AI CONTEXT BRIDGE")
        logger.info("=" * 80)
        logger.info(f"   Project: {self.project_root}")
        logger.info(f"   Documents indexed: {len(self.doc_index)}")
        logger.info(f"   Topics indexed: {len(self.topic_index)}")
        logger.info("=" * 80)

    def index_project(self, force_reindex: bool = False) -> Dict[str, Any]:
        """Index project documentation for context retrieval"""
        logger.info("📚 Indexing project documentation...")

        stats = {"indexed": 0, "skipped": 0, "errors": 0}

        for doc_dir in DOC_PATHS:
            dir_path = self.project_root / doc_dir
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob("*"):
                if file_path.suffix.lower() not in INDEXABLE_EXTENSIONS:
                    continue
                if file_path.is_dir():
                    continue

                try:
                    rel_path = str(file_path.relative_to(self.project_root))

                    # Check if already indexed and unchanged
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    content_hash = hashlib.md5(content.encode()).hexdigest()

                    if not force_reindex and rel_path in self.doc_index:
                        if self.doc_index[rel_path].get("content_hash") == content_hash:
                            stats["skipped"] += 1
                            continue

                    # Index the document
                    self._index_document(rel_path, content, content_hash)
                    stats["indexed"] += 1

                except Exception as e:
                    logger.warning(f"Error indexing {file_path}: {e}")
                    stats["errors"] += 1

        # Save index
        self._save_index()

        logger.info(
            f"✅ Indexing complete: {stats['indexed']} indexed, {stats['skipped']} skipped, {stats['errors']} errors"
        )
        return stats

    def _index_document(self, rel_path: str, content: str, content_hash: str):
        """Index a single document"""
        # Extract title (first heading or filename)
        title = Path(rel_path).stem.replace("_", " ").replace("-", " ").title()
        lines = content.split("\n")
        for line in lines[:10]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        # Extract keywords from content
        keywords = self._extract_keywords(content)

        # Create summary (first 500 chars or first paragraph)
        summary = content[:500].strip()
        if "\n\n" in content[:500]:
            summary = content[: content.find("\n\n", 0, 500)].strip()

        # Store in doc index
        self.doc_index[rel_path] = {
            "title": title,
            "summary": summary,
            "keywords": keywords,
            "content_hash": content_hash,
            "size": len(content),
            "indexed_at": datetime.now().isoformat(),
        }

        # Update topic index
        for keyword in keywords:
            if keyword not in self.topic_index:
                self.topic_index[keyword] = []
            if rel_path not in self.topic_index[keyword]:
                self.topic_index[keyword].append(rel_path)

        # Cache content
        self.content_cache[rel_path] = content

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from document content"""
        # Simple keyword extraction based on common terms
        # In production, would use NLP or embedding similarity

        # Convert to lowercase and extract words
        words = content.lower().replace("-", " ").replace("_", " ").split()

        # Count word frequencies
        word_counts: Dict[str, int] = {}
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "and",
            "or",
            "but",
            "if",
            "then",
            "else",
            "when",
            "where",
            "how",
            "what",
            "who",
            "which",
            "why",
            "for",
            "to",
            "from",
            "in",
            "on",
            "at",
            "by",
            "with",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "under",
            "over",
            "of",
            "up",
            "down",
            "out",
            "off",
            "such",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "now",
            "also",
            "any",
            "each",
            "few",
            "more",
            "most",
            "other",
            "some",
            "no",
            "not",
        }

        for word in words:
            # Clean word
            word = "".join(c for c in word if c.isalnum())
            if len(word) < 3 or word in stopwords:
                continue
            word_counts[word] = word_counts.get(word, 0) + 1

        # Get top keywords
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, count in sorted_words[:30] if count >= 2]

        return keywords

    def retrieve_context(
        self, query: str, max_docs: int = 5, max_size: int = MAX_CONTEXT_SIZE
    ) -> str:
        """Retrieve relevant context for a query with configurable size limit"""
        query_lower = query.lower()
        query_words = set(query_lower.replace("-", " ").replace("_", " ").split())

        # Score documents by keyword overlap
        doc_scores: Dict[str, float] = {}

        for rel_path, doc_info in self.doc_index.items():
            score = 0.0

            # Check keyword matches
            doc_keywords = set(doc_info.get("keywords", []))
            keyword_overlap = query_words & doc_keywords
            score += len(keyword_overlap) * 2

            # Check title match
            title_lower = doc_info.get("title", "").lower()
            for word in query_words:
                if word in title_lower:
                    score += 3

            # Check path match (e.g., "footer" in path)
            path_lower = rel_path.lower()
            for word in query_words:
                if word in path_lower:
                    score += 2

            if score > 0:
                doc_scores[rel_path] = score

        # Get top documents
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        top_docs = sorted_docs[:max_docs]

        if not top_docs:
            logger.info(f"🔍 No relevant documents found for: {query[:50]}...")
            return ""

        # Build context string
        context_parts = []
        total_size = 0

        for rel_path, score in top_docs:
            content = self._get_content(rel_path)
            if not content:
                continue

            # Truncate if needed
            available_space = max_size - total_size - 200  # Reserve for headers
            if len(content) > available_space:
                content = content[:available_space] + "\n... [truncated]"

            doc_info = self.doc_index[rel_path]
            context_parts.append(f"### {doc_info['title']} ({rel_path})\n{content}")
            total_size += len(content) + 100

            if total_size >= max_size:
                break

        context = "\n\n---\n\n".join(context_parts)
        logger.info(f"🔍 Retrieved {len(context_parts)} documents ({total_size} chars) for query")

        return context

    def _get_content(self, rel_path: str) -> Optional[str]:
        """Get document content from cache or file"""
        if rel_path in self.content_cache:
            return self.content_cache[rel_path]

        file_path = self.project_root / rel_path
        if not file_path.exists():
            return None

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            self.content_cache[rel_path] = content
            return content
        except Exception:
            return None

    def chat_with_context(
        self,
        prompt: str,
        model: str = "qwen2.5:7b",
        include_context: bool = True,
        stream: bool = False,
        use_cloud: bool = False,
        use_cluster: bool = False,
        use_bitnet: bool = False,
        bitnet_model: str = "2b",
        cloud_provider: str = "anthropic",
        max_context_size: int = None,
    ) -> Dict[str, Any]:
        """
        Chat with AI model with automatic context injection.

        Args:
            prompt: User query
            model: Local Ollama model (for GPU tiers)
            include_context: Whether to inject project context
            stream: Stream response (local only)
            use_cloud: Use cloud API for faster inference (--tier cloud)
            use_cluster: Use homelab cluster for distributed inference (--tier cluster)
            use_bitnet: Use BitNet CPU inference (--tier bitnet-fast/bitnet-quality)
            bitnet_model: BitNet model ID ("2b", "8b", etc.)
            cloud_provider: "anthropic" or "openai"
            max_context_size: Override context size limit (uses tier default if None)

        This is the "smart" interface that makes AI aware of project docs.
        """
        # Determine context size - use provided value or default
        ctx_size = max_context_size if max_context_size else MAX_CONTEXT_SIZE

        # Build system prompt with context (size-limited)
        system_prompt = self._build_system_prompt(
            prompt if include_context else "", max_context_size=ctx_size
        )

        if use_cloud:
            return self._chat_cloud(prompt, system_prompt, cloud_provider)
        elif use_cluster:
            return self._chat_cluster(prompt, system_prompt, model, stream)
        elif use_bitnet:
            return self._chat_bitnet(prompt, system_prompt, bitnet_model)
        else:
            return self._chat_local(prompt, system_prompt, model, stream)

    def _chat_cloud(
        self, prompt: str, system_prompt: str, provider: str = "anthropic"
    ) -> Dict[str, Any]:
        """Use cloud API for fast inference"""
        import time

        config = CLOUD_PROVIDERS.get(provider)
        if not config:
            return {"success": False, "error": f"Unknown provider: {provider}"}

        api_key = os.environ.get(config["env_key"])
        if not api_key:
            return {
                "success": False,
                "error": f"Missing {config['env_key']} env var. Set it or use --model for local.",
            }

        start_time = time.time()

        try:
            if provider == "anthropic":
                response = requests.post(
                    config["url"],
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": config["model"],
                        "max_tokens": 1024,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "response": data["content"][0]["text"],
                        "model": config["model"],
                        "provider": "anthropic (cloud)",
                        "context_injected": True,
                        "total_duration": time.time() - start_time,
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Anthropic API error: {response.status_code}",
                    }

            elif provider == "openai":
                response = requests.post(
                    config["url"],
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": config["model"],
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": 1024,
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "response": data["choices"][0]["message"]["content"],
                        "model": config["model"],
                        "provider": "openai (cloud)",
                        "context_injected": True,
                        "total_duration": time.time() - start_time,
                    }
                else:
                    return {"success": False, "error": f"OpenAI API error: {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _chat_local(
        self, prompt: str, system_prompt: str, model: str, stream: bool
    ) -> Dict[str, Any]:
        """Use local Ollama for inference (slower but free/private)"""
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": stream,
                    "options": {
                        "num_ctx": 8192,
                        "temperature": 0.7,
                    },
                },
                timeout=300,  # 5 min for slow local models
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data.get("response", ""),
                    "model": model,
                    "provider": "ollama (local)",
                    "context_injected": True,
                    "total_duration": data.get("total_duration", 0) / 1e9,
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama API error: {response.status_code}",
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Local model timed out (>5min). Try: --cloud for faster inference",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _chat_cluster(
        self, prompt: str, system_prompt: str, model: str, stream: bool
    ) -> Dict[str, Any]:
        """Use homelab cluster for inference - routes to best available node (GPU or CPU)"""
        import time as time_module

        # Try GPU nodes first
        best_node = None
        best_url = None

        for node_name, node_config in CLUSTER_NODES.items():
            if node_config.get("type") != "gpu":
                continue
            url = f"http://{node_config['ip']}:{node_config['port']}"
            try:
                resp = requests.get(f"{url}/api/tags", timeout=3)
                if resp.status_code == 200:
                    best_node = node_name
                    best_url = url
                    # Prefer node with model already loaded
                    ps_resp = requests.get(f"{url}/api/ps", timeout=3)
                    if ps_resp.status_code == 200:
                        running = ps_resp.json().get("models", [])
                        if any(model in m.get("name", "") for m in running):
                            break  # This node has the model loaded
            except Exception:
                continue

        # If no GPU available, try BitNet CPU
        if not best_node:
            logger.info("No GPU nodes available, trying BitNet CPU...")
            return self._chat_bitnet(prompt, system_prompt, "2b")

        logger.info(f"Routing to cluster GPU node: {best_node} ({best_url})")

        try:
            start_time = time_module.time()
            response = requests.post(
                f"{best_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": stream,
                    "options": {
                        "num_ctx": 8192,
                        "temperature": 0.7,
                    },
                },
                timeout=300,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response": data.get("response", ""),
                    "model": model,
                    "provider": f"cluster-gpu ({best_node})",
                    "node": best_node,
                    "context_injected": True,
                    "total_duration": time_module.time() - start_time,
                }
            else:
                return {
                    "success": False,
                    "error": f"Cluster API error: {response.status_code}",
                }

        except requests.exceptions.Timeout:
            # GPU timed out, try BitNet CPU as fallback
            logger.info("GPU timed out, falling back to BitNet CPU...")
            return self._chat_bitnet(prompt, system_prompt, "2b")
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _chat_bitnet(self, prompt: str, system_prompt: str, model: str) -> Dict[str, Any]:
        """Use BitNet CPU inference (Microsoft 1-bit LLMs)"""
        import time as time_module

        try:
            from bitnet_inference import BitNetInference

            bitnet = BitNetInference()
            if not bitnet.is_installed:
                return {
                    "success": False,
                    "error": "BitNet not installed. Run: scripts/powershell/setup_bitnet_homelab.ps1 -InstallDependencies",
                }

            if not bitnet.is_model_available(model):
                return {
                    "success": False,
                    "error": f"BitNet model {model} not downloaded. Run: scripts/powershell/setup_bitnet_homelab.ps1 -DownloadModels",
                }

            logger.info(f"Running BitNet CPU inference with model: {model}")

            start_time = time_module.time()

            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"

            response = bitnet.generate(
                prompt=full_prompt,
                model_id=model,
                max_tokens=512,
            )

            total_time = time_module.time() - start_time

            if response.success:
                return {
                    "success": True,
                    "response": response.text,
                    "model": f"bitnet-{model}",
                    "provider": "bitnet-cpu (local)",
                    "context_injected": True,
                    "total_duration": total_time,
                    "tokens_per_sec": response.tokens_per_second,
                }
            else:
                return {
                    "success": False,
                    "error": response.error,
                }

        except ImportError:
            return {
                "success": False,
                "error": "BitNet module not found. Ensure bitnet_inference.py is in the same directory.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_system_prompt(self, query: str, max_context_size: int = MAX_CONTEXT_SIZE) -> str:
        """Build system prompt with relevant context including R5 Living Matrix"""
        base_prompt = """You are JARVIS, an AI assistant with full access to the Lumina homelab project.

You have ADMIN ACCESS to all project documentation, configuration, and knowledge bases.
When asked about project-specific topics, you CAN and SHOULD reference the documentation provided below.

IMPORTANT: You DO have access to local files through the context injection system.
Do NOT say "I don't have access to local files" - the relevant documentation is provided below.

Project: Lumina Homelab
Location: C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina

## Knowledge Sources Available:
1. **R5 Living Context Matrix** - @PEAK patterns and learned wisdom from IDE sessions
2. **Static Documentation** - 3,110+ indexed docs, configs, and rules
3. **Cursor Rules & Memories** - Persistent guidance and context
"""

        # Always include R5 patterns if available
        r5_context = self._get_r5_context()
        if r5_context:
            base_prompt += f"""
---
## R5 LIVING CONTEXT MATRIX (Learned Patterns)

{r5_context}

---
"""

        if query:
            context = self.retrieve_context(query, max_size=max_context_size)
            if context:
                base_prompt += f"""
---
## RELEVANT PROJECT DOCUMENTATION

The following documentation is relevant to the user's query:

{context}

---
Use this documentation to provide accurate, project-specific answers.
"""

        return base_prompt

    def _get_r5_context(self) -> Optional[str]:
        """Get R5 Living Context Matrix patterns for injection"""
        r5_paths = [
            self.project_root
            / "--serve"
            / "data"
            / "r5_living_matrix"
            / "LIVING_CONTEXT_MATRIX_PROMPT.md",
            self.project_root / "data" / "r5_living_matrix" / "LIVING_CONTEXT_MATRIX_PROMPT.md",
        ]

        for r5_path in r5_paths:
            if r5_path.exists():
                try:
                    content = r5_path.read_text(encoding="utf-8", errors="ignore")
                    # Truncate if too long (keep first 4000 chars of R5 context)
                    if len(content) > 4000:
                        content = content[:4000] + "\n... [R5 context truncated]"
                    return content
                except Exception as e:
                    logger.warning(f"Could not read R5 context: {e}")

        return None

    def _load_index(self):
        """Load index from disk"""
        index_file = self.index_path / "document_index.json"
        topic_file = self.index_path / "topic_index.json"

        if index_file.exists():
            try:
                with open(index_file, encoding="utf-8") as f:
                    self.doc_index = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load document index: {e}")

        if topic_file.exists():
            try:
                with open(topic_file, encoding="utf-8") as f:
                    self.topic_index = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load topic index: {e}")

    def _save_index(self):
        """Save index to disk"""
        index_file = self.index_path / "document_index.json"
        topic_file = self.index_path / "topic_index.json"

        try:
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(self.doc_index, f, indent=2)
            with open(topic_file, "w", encoding="utf-8") as f:
                json.dump(self.topic_index, f, indent=2)
            logger.info(f"💾 Saved index to {self.index_path}")
        except Exception as e:
            logger.error(f"Could not save index: {e}")

    def get_available_topics(self) -> List[str]:
        """Get list of indexed topics"""
        return sorted(self.topic_index.keys())

    def search_docs(self, query: str) -> List[Dict[str, Any]]:
        """Search indexed documents"""
        results = []
        query_lower = query.lower()

        for rel_path, doc_info in self.doc_index.items():
            if (
                query_lower in rel_path.lower()
                or query_lower in doc_info.get("title", "").lower()
                or any(query_lower in kw for kw in doc_info.get("keywords", []))
            ):
                results.append(
                    {
                        "path": rel_path,
                        "title": doc_info.get("title"),
                        "summary": doc_info.get("summary", "")[:200],
                    }
                )

        return results[:20]


def _run_auto_escalation(
    bridge: "LocalAIContextBridge",
    query: str,
    max_context: int,
    cloud_provider: str = "anthropic",
) -> Dict[str, Any]:
    """
    Run query with auto-escalation: starts free, escalates to cloud if needed.

    Escalation chain: free-fast → free-balanced → free-quality → cloud-fast → cloud-premium
    """
    for tier_name in ESCALATION_CHAIN:
        tier_config = MODEL_TIERS.get(tier_name)
        if not tier_config:
            continue

        tier_type = tier_config.get("type", "gpu")
        model = tier_config["model"]
        ctx_size = min(max_context, tier_config.get("max_context", MAX_CONTEXT_SIZE))

        print(f"   🔄 Trying tier: {tier_name}...")

        # Determine backend
        use_cloud = tier_type == "cloud"
        use_bitnet = tier_type == "bitnet"
        use_cluster = tier_type == "cluster"

        try:
            result = bridge.chat_with_context(
                query,
                model=model,
                use_cloud=use_cloud,
                use_cluster=use_cluster,
                use_bitnet=use_bitnet,
                bitnet_model=model if use_bitnet else "2b",
                cloud_provider=cloud_provider,
                max_context_size=ctx_size,
            )

            if result.get("success"):
                result["escalated_from"] = tier_name
                result["escalation_chain"] = ESCALATION_CHAIN[
                    : ESCALATION_CHAIN.index(tier_name) + 1
                ]
                print(f"   ✅ Success with tier: {tier_name}")
                return result
            else:
                print(f"   ⚠️ {tier_name} failed: {result.get('error', 'unknown')[:50]}")

        except Exception as e:
            print(f"   ⚠️ {tier_name} error: {str(e)[:50]}")
            continue

    return {
        "success": False,
        "error": "All tiers failed. Check local AI status or cloud API keys.",
        "escalation_chain": ESCALATION_CHAIN,
    }


def _print_tier_summary():
    """Print summary of available tiers"""
    print("\n" + "=" * 70)
    print("📊 AVAILABLE AI TIERS")
    print("=" * 70)

    print("\n🆓 FREE TIERS (Local compute - $0)")
    print("-" * 40)
    for name in ["free-fast", "free-balanced", "free-quality"]:
        cfg = MODEL_TIERS.get(name, {})
        print(f"  {name:20} | {cfg.get('speed', 'N/A'):10} | {cfg.get('quality', 'N/A')}")

    print("\n💰 CLOUD TIERS (Paid - costs tokens)")
    print("-" * 40)
    for name in ["cloud-fast", "cloud-premium"]:
        cfg = MODEL_TIERS.get(name, {})
        cost = "💵" if cfg.get("cost") == "low" else "💰💰💰"
        print(
            f"  {name:20} | {cfg.get('speed', 'N/A'):10} | {cfg.get('quality', 'N/A'):6} | {cost}"
        )

    print("\n🔄 SMART TIERS")
    print("-" * 40)
    print("  auto                 | Starts free, escalates to cloud if needed")
    print("  cluster              | Distributes across homelab (GPU + CPU)")

    print("\n" + "=" * 70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Local AI Context Bridge - Chat with AI that knows your project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Tier System:
  FREE TIERS ($0):
    --tier free-fast      BitNet CPU (2B) - 2-3s, basic quality
    --tier free-balanced  GPU Ollama (3B) - 10-20s, good quality (DEFAULT)
    --tier free-quality   GPU Ollama (7B) - 30-60s, great quality

  CLOUD TIERS ($$):
    --tier cloud-fast     Claude Haiku - 2-3s, low cost
    --tier cloud-premium  Claude Sonnet - 5-10s, best quality

  SMART TIERS:
    --tier auto           Starts free, escalates to cloud if needed
    --tier cluster        Distributes across homelab (GPU + CPU)

Examples:
  # FREE: Quick question (BitNet CPU)
  python local_ai_context_bridge.py --chat "What is 2+2?" --tier free-fast

  # FREE: Project question (GPU - default)
  python local_ai_context_bridge.py --chat "What is the footer config?"

  # AUTO: Start free, escalate if needed
  python local_ai_context_bridge.py --chat "Complex analysis" --tier auto

  # CLOUD: When you need the best
  python local_ai_context_bridge.py --chat "Design architecture" --premium

  # Show available tiers
  python local_ai_context_bridge.py --tiers
        """,
    )
    parser.add_argument("--index", action="store_true", help="Index project documentation")
    parser.add_argument("--reindex", action="store_true", help="Force full reindex")
    parser.add_argument("--search", type=str, help="Search indexed documents")
    parser.add_argument("--topics", action="store_true", help="List available topics")
    parser.add_argument("--tiers", action="store_true", help="Show available AI tiers")
    parser.add_argument("--chat", type=str, help="Chat with context-aware AI")
    parser.add_argument("--model", type=str, help="Specific Ollama model (overrides --tier)")
    parser.add_argument(
        "--tier",
        type=str,
        choices=[
            # New unified tiers
            "free-fast",  # BitNet CPU - fastest free
            "free-balanced",  # GPU 3B - good free
            "free-quality",  # GPU 7B - best free
            "cloud-fast",  # Haiku - cheap cloud
            "cloud-premium",  # Sonnet - best cloud
            "auto",  # Auto-escalation
            "cluster",  # Homelab distributed
            # Legacy (backward compat)
            "fast",
            "balanced",
            "quality",
            "cloud",
            "bitnet-fast",
            "bitnet-quality",
        ],
        default="free-balanced",
        help="Tier: free-fast/balanced/quality ($0), cloud-fast/premium ($$), auto (escalates)",
    )
    parser.add_argument("--cloud", action="store_true", help="Same as --tier cloud-fast")
    parser.add_argument("--free", action="store_true", help="Force free tier (no cloud)")
    parser.add_argument("--premium", action="store_true", help="Use cloud-premium tier")
    parser.add_argument(
        "--provider",
        type=str,
        default="anthropic",
        choices=["anthropic", "openai"],
        help="Cloud provider for --tier cloud (default: anthropic)",
    )

    args = parser.parse_args()

    bridge = LocalAIContextBridge()

    if args.index or args.reindex:
        stats = bridge.index_project(force_reindex=args.reindex)
        print("\n📚 Indexing complete:")
        print(f"   Indexed: {stats['indexed']}")
        print(f"   Skipped: {stats['skipped']}")
        print(f"   Errors: {stats['errors']}")

    elif args.search:
        results = bridge.search_docs(args.search)
        print(f"\n🔍 Search results for '{args.search}':")
        for r in results:
            print(f"   • {r['title']} ({r['path']})")

    elif args.topics:
        topics = bridge.get_available_topics()
        print(f"\n📋 Available topics ({len(topics)}):")
        for topic in topics[:50]:
            print(f"   • {topic}")
        if len(topics) > 50:
            print(f"   ... and {len(topics) - 50} more")

    elif args.tiers:
        _print_tier_summary()

    elif args.chat:
        # Determine tier from flags
        if args.premium:
            tier = "cloud-premium"
        elif args.cloud:
            tier = "cloud-fast"
        elif args.free:
            tier = "free-balanced"
        else:
            tier = args.tier

        # Resolve legacy aliases
        tier_config = MODEL_TIERS.get(tier, MODEL_TIERS[DEFAULT_TIER])
        if "alias_for" in tier_config:
            tier = tier_config["alias_for"]
            tier_config = MODEL_TIERS.get(tier, MODEL_TIERS[DEFAULT_TIER])

        tier_type = tier_config.get("type", "gpu")
        model = args.model if args.model else tier_config["model"]
        max_context = tier_config.get("max_context", MAX_CONTEXT_SIZE)
        cost_indicator = tier_config.get("cost", "free")

        # Determine backend type
        use_cloud = tier_type == "cloud"
        use_cluster = tier_type == "cluster"
        use_bitnet = tier_type == "bitnet"
        use_auto = tier_type == "auto"
        bitnet_model = tier_config["model"] if use_bitnet else "2b"

        # Display tier info with appropriate icon
        if cost_indicator == "free":
            icon = "🆓"
        elif cost_indicator == "low":
            icon = "💵"
        elif cost_indicator == "high":
            icon = "💰"
        else:
            icon = "🔄" if use_auto else "🌐"

        print(f"\n{icon} Tier: {tier}")
        print(f"   {tier_config['description']}")
        print(f"   Context: {max_context} chars | Cost: {cost_indicator.upper()}")

        # Handle auto-escalation tier
        if use_auto:
            result = _run_auto_escalation(bridge, args.chat, max_context, args.provider)
        else:
            result = bridge.chat_with_context(
                args.chat,
                model=model,
                use_cloud=use_cloud,
                use_cluster=use_cluster,
                use_bitnet=use_bitnet,
                bitnet_model=bitnet_model,
                cloud_provider=args.provider,
                max_context_size=max_context,
            )

        if result["success"]:
            provider = result.get("provider", "unknown")
            print(f"\n🤖 Response ({provider}):\n{result['response']}")
            print(f"\n⏱️ Duration: {result['total_duration']:.2f}s")
        else:
            print(f"\n❌ Error: {result.get('error')}")

    else:
        # Default: show status
        print("\n🌉 LOCAL AI CONTEXT BRIDGE")
        print("=" * 60)
        print(f"   Documents indexed: {len(bridge.doc_index)}")
        print(f"   Topics indexed: {len(bridge.topic_index)}")
        print()
        print("Commands:")
        print("   --index     Index project documentation")
        print("   --reindex   Force full reindex")
        print("   --search    Search indexed documents")
        print("   --topics    List available topics")
        print("   --chat      Chat with context-aware AI")
        print("   --cloud     Use cloud API (fast, requires ANTHROPIC_API_KEY)")
        print()
        print("Examples:")
        print("   python local_ai_context_bridge.py --index")
        print('   python local_ai_context_bridge.py --chat "What is the footer?" --cloud')
        print(
            '   python local_ai_context_bridge.py --chat "What is the footer?" --model qwen2.5:7b'
        )


if __name__ == "__main__":
    main()
