#!/usr/bin/env python3
"""
Embeddings MCP Server for Kilo Code

Provides Continue-style embeddings and semantic search for codebase awareness.
This enables @Codebase and @Repository Map context providers.

Features:
- Index codebase files into embeddings
- Semantic search across codebase
- Repository structure mapping
- Similarity-based code finding

Requirements:
    pip install sentence-transformers numpy faiss-cpu

Usage:
    python embeddings_mcp_server.py              # Start MCP server
    python embeddings_mcp_server.py --index      # Index codebase
    python embeddings_mcp_server.py --search "query"

Tags: @PEAK @KILO_CODE @EMBEDDINGS @CONTINUE #automation
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "embeddings"
INDEX_FILE = DATA_DIR / "codebase_index.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.npy"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# EMBEDDINGS ENGINE
# =============================================================================

class EmbeddingsEngine:
    """Handles codebase embeddings and semantic search"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.file_map: Dict[int, str] = {}
        self.chunk_map: Dict[int, Dict[str, Any]] = {}
        
    def _load_model(self):
        """Lazy load the embedding model"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"Loading embedding model: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                print("Model loaded!")
            except ImportError:
                print("ERROR: sentence-transformers not installed")
                print("Run: pip install sentence-transformers")
                return False
        return True
    
    def _get_code_files(self, root: Path, extensions: List[str] = None) -> List[Path]:
        """Get all code files in the project"""
        if extensions is None:
            extensions = [
                ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
                ".md", ".txt", ".sh", ".ps1", ".bat", ".sql", ".html", ".css",
                ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp"
            ]
        
        files = []
        ignore_dirs = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            ".cursor", "dist", "build", ".next", "coverage"
        }
        
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in extensions:
                # Check if in ignored directory
                if not any(ignored in path.parts for ignored in ignore_dirs):
                    files.append(path)
        
        return files
    
    def _chunk_file(self, file_path: Path, chunk_size: int = 500) -> List[Dict[str, Any]]:
        """Split file into chunks for embedding"""
        chunks = []
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  Error reading {file_path}: {e}")
            return []
        
        lines = content.split("\n")
        current_chunk = []
        current_size = 0
        start_line = 0
        
        for i, line in enumerate(lines):
            line_size = len(line)
            
            if current_size + line_size > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "file": str(file_path.relative_to(PROJECT_ROOT)),
                    "start_line": start_line,
                    "end_line": i,
                    "content": "\n".join(current_chunk)
                })
                current_chunk = []
                current_size = 0
                start_line = i
            
            current_chunk.append(line)
            current_size += line_size
        
        # Save final chunk
        if current_chunk:
            chunks.append({
                "file": str(file_path.relative_to(PROJECT_ROOT)),
                "start_line": start_line,
                "end_line": len(lines),
                "content": "\n".join(current_chunk)
            })
        
        return chunks
    
    def index_codebase(self, root: Path = None) -> Dict[str, Any]:
        """Index the codebase into embeddings"""
        if not self._load_model():
            return {"success": False, "error": "Model not available"}
        
        if root is None:
            root = PROJECT_ROOT
        
        print(f"Indexing codebase at: {root}")
        
        # Get all code files
        files = self._get_code_files(root)
        print(f"Found {len(files)} files to index")
        
        # Chunk all files
        all_chunks = []
        for file_path in files:
            chunks = self._chunk_file(file_path)
            all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} chunks")
        
        if not all_chunks:
            return {"success": False, "error": "No chunks created"}
        
        # Generate embeddings
        print("Generating embeddings...")
        texts = [chunk["content"] for chunk in all_chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        try:
            import faiss
            import numpy as np
            
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
            # Save index
            faiss.write_index(self.index, str(DATA_DIR / "faiss.index"))
            
        except ImportError:
            print("WARNING: FAISS not available, using numpy fallback")
            import numpy as np
            np.save(EMBEDDINGS_FILE, embeddings)
        
        # Build chunk map
        self.chunk_map = {i: chunk for i, chunk in enumerate(all_chunks)}
        
        # Save metadata
        index_data = {
            "indexed_at": datetime.now().isoformat(),
            "num_files": len(files),
            "num_chunks": len(all_chunks),
            "model": self.model_name,
            "chunks": all_chunks
        }
        
        with open(INDEX_FILE, "w") as f:
            json.dump(index_data, f, indent=2)
        
        print(f"Index saved to {INDEX_FILE}")
        
        return {
            "success": True,
            "files_indexed": len(files),
            "chunks_created": len(all_chunks)
        }
    
    def load_index(self) -> bool:
        """Load existing index"""
        if not INDEX_FILE.exists():
            return False
        
        try:
            with open(INDEX_FILE) as f:
                index_data = json.load(f)
            
            self.chunk_map = {i: chunk for i, chunk in enumerate(index_data["chunks"])}
            
            # Load FAISS index
            try:
                import faiss
                index_path = DATA_DIR / "faiss.index"
                if index_path.exists():
                    self.index = faiss.read_index(str(index_path))
                    return True
            except ImportError:
                pass
            
            # Fallback to numpy
            if EMBEDDINGS_FILE.exists():
                import numpy as np
                self.embeddings = np.load(EMBEDDINGS_FILE)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error loading index: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Semantic search across codebase"""
        if not self._load_model():
            return []
        
        # Load index if not loaded
        if self.index is None and not self.load_index():
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search
        try:
            import faiss
            import numpy as np
            
            faiss.normalize_L2(query_embedding)
            distances, indices = self.index.search(query_embedding, top_k)
            
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx in self.chunk_map:
                    chunk = self.chunk_map[idx].copy()
                    chunk["score"] = float(dist)
                    chunk["rank"] = i + 1
                    results.append(chunk)
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_repository_map(self) -> Dict[str, Any]:
        """Get repository structure map"""
        structure = {}
        
        files = self._get_code_files(PROJECT_ROOT)
        
        for file_path in files:
            rel_path = file_path.relative_to(PROJECT_ROOT)
            parts = rel_path.parts
            
            current = structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file with basic info
            current[parts[-1]] = {
                "type": "file",
                "extension": file_path.suffix,
                "size": file_path.stat().st_size
            }
        
        return structure


# =============================================================================
# MCP SERVER
# =============================================================================

class EmbeddingsMCPServer:
    """MCP Server for embeddings functionality"""
    
    def __init__(self):
        self.engine = EmbeddingsEngine()
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "tools/list":
            return self._list_tools()
        elif method == "tools/call":
            return self._call_tool(params)
        else:
            return {"error": f"Unknown method: {method}"}
    
    def _list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return {
            "tools": [
                {
                    "name": "index_codebase",
                    "description": "Index the codebase into embeddings for semantic search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "semantic_search",
                    "description": "Search the codebase semantically",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "repository_map",
                    "description": "Get repository structure map",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if tool_name == "index_codebase":
            result = self.engine.index_codebase()
            return {"content": [{"type": "text", "text": json.dumps(result)}]}
        
        elif tool_name == "semantic_search":
            query = arguments.get("query", "")
            top_k = arguments.get("top_k", 10)
            results = self.engine.search(query, top_k)
            return {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}
        
        elif tool_name == "repository_map":
            repo_map = self.engine.get_repository_map()
            return {"content": [{"type": "text", "text": json.dumps(repo_map, indent=2)}]}
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def run_stdio(self):
        """Run as STDIO MCP server"""
        print("Embeddings MCP Server started", file=sys.stderr)
        
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError:
                pass
            except Exception as e:
                print(json.dumps({"error": str(e)}))
                sys.stdout.flush()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Embeddings MCP Server")
    parser.add_argument("--index", action="store_true", help="Index the codebase")
    parser.add_argument("--search", type=str, help="Search the codebase")
    parser.add_argument("--top-k", type=int, default=10, help="Number of search results")
    parser.add_argument("--map", action="store_true", help="Show repository map")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP server")
    
    args = parser.parse_args()
    
    engine = EmbeddingsEngine()
    
    if args.index:
        result = engine.index_codebase()
        print(json.dumps(result, indent=2))
    
    elif args.search:
        results = engine.search(args.search, args.top_k)
        print(f"\nSearch results for: {args.search}\n")
        for r in results:
            print(f"[{r['rank']}] {r['file']}:{r['start_line']}-{r['end_line']} (score: {r['score']:.3f})")
            print(f"    {r['content'][:100]}...")
            print()
    
    elif args.map:
        repo_map = engine.get_repository_map()
        print(json.dumps(repo_map, indent=2))
    
    elif args.mcp:
        server = EmbeddingsMCPServer()
        server.run_stdio()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
