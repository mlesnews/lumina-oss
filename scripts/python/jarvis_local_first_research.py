#!/usr/bin/env python3
"""
JARVIS Local-First Research System

Implements a comprehensive research methodology that ALWAYS prioritizes local resources:
- Local documentation and codebase
- Deep-dive cached searches
- Local knowledge bases and indexes
- Exhaustive local exploration before external sources

This system ensures JARVIS leverages all available local intelligence before
consulting external @SOURCES, providing faster, more accurate, and cost-effective research.

@JARVIS @MANUS @LUMINA - Local-First Research Workflow
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
# import aiofiles  # Using standard file operations instead
import psutil
from concurrent.futures import ThreadPoolExecutor

# Import SYPHON components
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from syphon.models import DataSourceType, SyphonData
from syphon.extractors import BaseExtractor, ExtractionResult
from r5_living_context_matrix import R5LivingContextMatrix
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class LocalKnowledgeBase:
    """Comprehensive local knowledge base for JARVIS research"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.kb_dir = self.project_root / "data" / "jarvis_knowledge_base"
        self.cache_dir = self.kb_dir / "cache"
        self.index_dir = self.kb_dir / "indexes"
        self.docs_dir = self.kb_dir / "documents"

        # Create directories
        for dir_path in [self.kb_dir, self.cache_dir, self.index_dir, self.docs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Knowledge base components
        self.document_index = {}  # filename -> metadata
        self.code_index = {}      # file -> code entities
        self.cache = {}          # query -> results cache
        self.last_updated = None

        # Load existing knowledge
        self._load_indexes()

    def _load_indexes(self):
        """Load existing knowledge base indexes"""
        try:
            # Load document index
            doc_index_file = self.index_dir / "document_index.json"
            if doc_index_file.exists():
                with open(doc_index_file, 'r') as f:
                    self.document_index = json.load(f)

            # Load code index
            code_index_file = self.index_dir / "code_index.json"
            if code_index_file.exists():
                with open(code_index_file, 'r') as f:
                    self.code_index = json.load(f)

            # Load cache
            cache_file = self.cache_dir / "query_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    self.cache = json.load(f)

        except Exception as e:
            logging.warning(f"Failed to load knowledge base indexes: {e}")

    def save_indexes(self):
        """Save knowledge base indexes"""
        try:
            # Save document index
            with open(self.index_dir / "document_index.json", 'w') as f:
                json.dump(self.document_index, f, indent=2)

            # Save code index
            with open(self.index_dir / "code_index.json", 'w') as f:
                json.dump(self.code_index, f, indent=2)

            # Save cache
            with open(self.cache_dir / "query_cache.json", 'w') as f:
                json.dump(self.cache, f, indent=2)

        except Exception as e:
            logging.error(f"Failed to save knowledge base indexes: {e}")

    async def index_project_files(self):
        """Index all project files for local search"""
        logging.info("Indexing project files for local knowledge base...")

        # Index documentation files
        await self._index_documentation()

        # Index code files
        await self._index_codebase()

        # Update timestamp
        self.last_updated = datetime.now()
        self.save_indexes()

        logging.info(f"Indexed {len(self.document_index)} documents and {len(self.code_index)} code files")

    async def _index_documentation(self):
        """Index all documentation files"""
        doc_patterns = [
            "**/*.md", "**/*.txt", "**/*.rst", "**/*.adoc",
            "**/README*", "**/CHANGELOG*", "**/docs/**/*.md"
        ]

        for pattern in doc_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() and not self._is_excluded_file(file_path):
                    await self._index_document_file(file_path)

    async def _index_codebase(self):
        """Index all code files"""
        code_extensions = [
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs',
            '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala'
        ]

        for ext in code_extensions:
            for file_path in self.project_root.glob(f"**/*{ext}"):
                if file_path.is_file() and not self._is_excluded_file(file_path):
                    await self._index_code_file(file_path)

    def _is_excluded_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from indexing"""
        excluded_patterns = [
            '__pycache__', 'node_modules', '.git', 'build', 'dist',
            '*.pyc', '*.pyo', '*.class', '*.jar', '*.min.js'
        ]

        str_path = str(file_path)
        return any(pattern in str_path for pattern in excluded_patterns)

    async def _index_document_file(self, file_path: Path):
        """Index a documentation file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract metadata
            metadata = {
                "filename": file_path.name,
                "path": str(file_path.relative_to(self.project_root)),
                "size": len(content),
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "word_count": len(content.split()),
                "sections": self._extract_document_sections(content),
                "keywords": self._extract_keywords(content),
                "indexed_at": datetime.now().isoformat()
            }

            self.document_index[str(file_path.relative_to(self.project_root))] = {
                "metadata": metadata,
                "content": content[:10000]  # Store first 10k chars for search
            }

        except Exception as e:
            logging.warning(f"Failed to index document {file_path}: {e}")

    async def _index_code_file(self, file_path: Path):
        """Index a code file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract code entities
            entities = self._extract_code_entities(content, file_path.suffix)

            metadata = {
                "filename": file_path.name,
                "path": str(file_path.relative_to(self.project_root)),
                "language": file_path.suffix[1:],  # Remove leading dot
                "size": len(content),
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "line_count": content.count('\n') + 1,
                "entities": entities,
                "indexed_at": datetime.now().isoformat()
            }

            self.code_index[str(file_path.relative_to(self.project_root))] = {
                "metadata": metadata,
                "content": content[:5000]  # Store first 5k chars for search
            }

        except Exception as e:
            logging.warning(f"Failed to index code file {file_path}: {e}")

    def _extract_document_sections(self, content: str) -> List[str]:
        """Extract document sections/headings"""
        sections = []

        # Markdown headers
        header_pattern = r'^#{1,6}\s+(.+)$'
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            sections.append(match.group(1).strip())

        # RST headers
        rst_pattern = r'^(.+)\n[=~-]+\n'
        for match in re.finditer(rst_pattern, content, re.MULTILINE):
            sections.append(match.group(1).strip())

        return sections[:20]  # Limit to first 20 sections

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r'\b\w{4,}\b', content.lower())
        word_freq = {}

        # Remove common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'an', 'a', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}

        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top 20 keywords
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]

    def _extract_code_entities(self, content: str, extension: str) -> Dict[str, List[str]]:
        """Extract code entities (functions, classes, etc.)"""
        entities = {
            "functions": [],
            "classes": [],
            "imports": [],
            "constants": []
        }

        if extension == '.py':
            # Python patterns
            entities["functions"] = re.findall(r'def\s+(\w+)\s*\(', content)
            entities["classes"] = re.findall(r'class\s+(\w+)[\s(:]', content)
            entities["imports"] = re.findall(r'(?:from\s+[\w.]+\s+import|import)\s+(.+)', content)

        elif extension in ['.js', '.ts']:
            # JavaScript/TypeScript patterns
            entities["functions"] = re.findall(r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>|(\w+)\s*\([^)]*\)\s*{)', content)
            entities["classes"] = re.findall(r'class\s+(\w+)', content)
            entities["imports"] = re.findall(r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]', content)

        elif extension == '.java':
            # Java patterns
            entities["classes"] = re.findall(r'(?:class|interface|enum)\s+(\w+)', content)
            entities["functions"] = re.findall(r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\([^)]*\)', content)

        # Clean up nested lists from regex groups
        for key in entities:
            entities[key] = [item for sublist in entities[key] for item in (sublist if isinstance(sublist, list) else [sublist]) if item]

        return entities

    async def deep_search_local(self, query: str, max_results: int = 50) -> Dict[str, Any]:
        """Perform deep-dive cached search on local resources"""

        # Check cache first
        cache_key = f"{query}_{max_results}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if datetime.now() - datetime.fromisoformat(cached_result["timestamp"]) < timedelta(hours=1):
                return cached_result["results"]

        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "document_results": [],
            "code_results": [],
            "total_matches": 0,
            "search_time": 0
        }

        start_time = time.time()

        # Search documentation
        doc_results = await self._search_documents(query, max_results // 2)
        results["document_results"] = doc_results

        # Search codebase
        code_results = await self._search_codebase(query, max_results // 2)
        results["code_results"] = code_results

        results["total_matches"] = len(doc_results) + len(code_results)
        results["search_time"] = time.time() - start_time

        # Cache results
        self.cache[cache_key] = {
            "timestamp": results["timestamp"],
            "results": results
        }
        self.save_indexes()

        return results

    async def _search_documents(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search documentation files"""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for file_path, doc_data in self.document_index.items():
            score = 0
            matches = []

            # Search in metadata
            metadata = doc_data["metadata"]
            filename = metadata["filename"].lower()
            sections = [s.lower() for s in metadata.get("sections", [])]

            # Filename match
            if query_lower in filename:
                score += 10
                matches.append(f"Filename: {metadata['filename']}")

            # Section matches
            for section in sections:
                if query_lower in section:
                    score += 5
                    matches.append(f"Section: {section}")

            # Keyword matches
            keywords = [kw[0] if isinstance(kw, tuple) else kw for kw in metadata.get("keywords", [])]
            keyword_matches = sum(1 for kw in keywords if query_lower in kw.lower())
            if keyword_matches > 0:
                score += keyword_matches * 2
                matches.append(f"Keywords: {keyword_matches} matches")

            # Content search
            content = doc_data.get("content", "").lower()
            if query_lower in content:
                score += 3
                # Find context around match
                context_start = max(0, content.find(query_lower) - 100)
                context_end = min(len(content), content.find(query_lower) + len(query_lower) + 100)
                context = content[context_start:context_end]
                matches.append(f"Content: ...{context}...")

            if score > 0:
                results.append({
                    "file": file_path,
                    "score": score,
                    "matches": matches,
                    "metadata": metadata
                })

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    async def _search_codebase(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search codebase files"""
        results = []
        query_lower = query.lower()

        for file_path, code_data in self.code_index.items():
            score = 0
            matches = []

            metadata = code_data["metadata"]

            # Search in entities
            entities = metadata.get("entities", {})
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    if query_lower in entity.lower():
                        score += 4
                        matches.append(f"{entity_type}: {entity}")

            # Search in content
            content = code_data.get("content", "").lower()
            if query_lower in content:
                score += 2
                # Find context around match
                context_start = max(0, content.find(query_lower) - 50)
                context_end = min(len(content), content.find(query_lower) + len(query_lower) + 50)
                context = content[context_start:context_end]
                matches.append(f"Code: ...{context}...")

            if score > 0:
                results.append({
                    "file": file_path,
                    "score": score,
                    "matches": matches,
                    "metadata": metadata
                })

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]


class JARVISLocalFirstResearch:
    """JARVIS Local-First Research Workflow"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.knowledge_base = LocalKnowledgeBase()
        self.r5_matrix = R5LivingContextMatrix(self.project_root)

        # Setup logging
        self.logger = logging.getLogger("JARVIS_LocalFirst")
        self.logger.setLevel(logging.INFO)

        # Research workflow state
        self.research_history = []
        self.local_exhaustion_threshold = 0.8  # Consider local search exhausted if coverage > 80%

    async def initialize_knowledge_base(self):
        """Initialize and update the local knowledge base"""
        self.logger.info("Initializing JARVIS local knowledge base...")

        # Check if we need to update the index
        if (not self.knowledge_base.last_updated or
            datetime.now() - self.knowledge_base.last_updated > timedelta(hours=24)):
            await self.knowledge_base.index_project_files()

        self.logger.info("Local knowledge base ready")

    async def research_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform local-first research on a query"""

        research_session = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "local_search_performed": False,
            "local_results": {},
            "external_search_needed": False,
            "external_sources": [],
            "final_answer": None,
            "confidence_score": 0.0,
            "research_path": []
        }

        self.logger.info(f"Starting local-first research for: {query}")

        # Phase 1: Exhaustive Local Search
        local_results = await self._perform_exhaustive_local_search(query)
        research_session["local_search_performed"] = True
        research_session["local_results"] = local_results
        research_session["research_path"].append("local_search")

        # Analyze local search coverage
        coverage_score = self._calculate_search_coverage(local_results)

        if coverage_score >= self.local_exhaustion_threshold:
            # Local search is sufficient
            research_session["final_answer"] = self._synthesize_local_answer(query, local_results)
            research_session["confidence_score"] = coverage_score
            research_session["research_path"].append("local_synthesis")
        else:
            # Need external sources
            research_session["external_search_needed"] = True
            external_sources = self._identify_needed_external_sources(query, local_results)
            research_session["external_sources"] = external_sources
            research_session["research_path"].append("external_source_identification")

            # For now, note that external search is needed
            # In full implementation, this would trigger SYPHON external search
            research_session["final_answer"] = self._create_external_search_plan(query, local_results, external_sources)
            research_session["confidence_score"] = coverage_score * 0.7  # Reduced confidence due to gaps

        # Record research session
        self.research_history.append(research_session)

        return research_session

    async def _perform_exhaustive_local_search(self, query: str) -> Dict[str, Any]:
        """Perform exhaustive search of all local resources"""

        # Deep search knowledge base
        kb_results = await self.knowledge_base.deep_search_local(query)

        # Search SYPHON data
        syphon_results = await self._search_syphon_data(query)

        # Search R5 Living Context Matrix
        r5_results = await self._search_r5_matrix(query)

        # Search project documentation specifically
        doc_results = await self._search_project_documentation(query)

        return {
            "knowledge_base": kb_results,
            "syphon_data": syphon_results,
            "r5_matrix": r5_results,
            "project_docs": doc_results,
            "total_sources_searched": 4,
            "search_timestamp": datetime.now().isoformat()
        }

    async def _search_syphon_data(self, query: str) -> Dict[str, Any]:
        """Search SYPHON extracted data"""
        syphon_dir = self.project_root / "data" / "syphon"

        results = {
            "total_entries": 0,
            "relevant_entries": 0,
            "matches": []
        }

        if not syphon_dir.exists():
            return results

        # Search extracted_data.json
        data_file = syphon_dir / "extracted_data.json"
        if data_file.exists():
            try:
                with open(data_file, 'r') as f:
                    syphon_data = json.load(f)

                query_lower = query.lower()
                for entry in syphon_data:
                    content = entry.get("content", "").lower()
                    if query_lower in content:
                        results["matches"].append({
                            "source_type": entry.get("metadata", {}).get("extraction_type"),
                            "content_snippet": content[:200] + "..." if len(content) > 200 else content,
                            "relevance_score": 1.0 if query_lower in content else 0.5
                        })

                results["total_entries"] = len(syphon_data)
                results["relevant_entries"] = len(results["matches"])

            except Exception as e:
                self.logger.warning(f"Failed to search SYPHON data: {e}")

        return results

    async def _search_r5_matrix(self, query: str) -> Dict[str, Any]:
        """Search R5 Living Context Matrix"""
        results = {
            "total_sessions": 0,
            "relevant_sessions": 0,
            "matches": []
        }

        # This would integrate with R5 matrix search
        # For now, return placeholder
        return results

    async def _search_project_documentation(self, query: str) -> Dict[str, Any]:
        """Search project-specific documentation"""
        results = {
            "readme_files": [],
            "config_files": [],
            "api_docs": [],
            "total_matches": 0
        }

        # Search README files
        for readme_path in self.project_root.glob("**/README*"):
            if readme_path.is_file():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if query.lower() in content:
                            results["readme_files"].append(str(readme_path.relative_to(self.project_root)))
                except Exception:
                    pass

        # Search config files
        config_patterns = ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.toml", "**/*.ini"]
        for pattern in config_patterns:
            for config_file in self.project_root.glob(pattern):
                if config_file.is_file():
                    try:
                        with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            if query.lower() in content:
                                results["config_files"].append(str(config_file.relative_to(self.project_root)))
                    except Exception:
                        pass

        results["total_matches"] = len(results["readme_files"]) + len(results["config_files"])

        return results

    def _calculate_search_coverage(self, local_results: Dict[str, Any]) -> float:
        """Calculate how comprehensively the local search covered the query"""

        total_sources = local_results.get("total_sources_searched", 0)
        sources_with_results = 0
        total_matches = 0

        # Check knowledge base results
        kb_results = local_results.get("knowledge_base", {})
        if kb_results.get("total_matches", 0) > 0:
            sources_with_results += 1
            total_matches += kb_results["total_matches"]

        # Check SYPHON results
        syphon_results = local_results.get("syphon_data", {})
        if syphon_results.get("relevant_entries", 0) > 0:
            sources_with_results += 1
            total_matches += syphon_results["relevant_entries"]

        # Check documentation results
        doc_results = local_results.get("project_docs", {})
        if doc_results.get("total_matches", 0) > 0:
            sources_with_results += 1
            total_matches += doc_results["total_matches"]

        # Calculate coverage score
        source_coverage = sources_with_results / total_sources if total_sources > 0 else 0
        match_density = min(1.0, total_matches / 10)  # Normalize match count

        return (source_coverage * 0.6) + (match_density * 0.4)

    def _synthesize_local_answer(self, query: str, local_results: Dict[str, Any]) -> str:
        """Synthesize an answer from local search results"""

        answer_parts = [f"Based on comprehensive local research for: {query}\n"]

        # Summarize knowledge base results
        kb_results = local_results.get("knowledge_base", {})
        if kb_results.get("total_matches", 0) > 0:
            answer_parts.append(f"📚 Found {kb_results['total_matches']} relevant matches in local documentation and code:")
            for result in kb_results.get("document_results", [])[:3]:
                answer_parts.append(f"  • {result['file']}: {', '.join(result['matches'][:2])}")

        # Summarize SYPHON results
        syphon_results = local_results.get("syphon_data", {})
        if syphon_results.get("relevant_entries", 0) > 0:
            answer_parts.append(f"🔍 Found {syphon_results['relevant_entries']} relevant entries in SYPHON data:")

        # Summarize documentation results
        doc_results = local_results.get("project_docs", {})
        if doc_results.get("total_matches", 0) > 0:
            answer_parts.append(f"📖 Found documentation references in {doc_results['total_matches']} files")

        answer_parts.append("\n💡 Local research completed. No external sources needed for this query.")

        return "\n".join(answer_parts)

    def _identify_needed_external_sources(self, query: str, local_results: Dict[str, Any]) -> List[str]:
        """Identify what external sources are needed to complete the research"""

        needed_sources = []

        # Analyze gaps in local results
        coverage = self._calculate_search_coverage(local_results)

        if coverage < 0.5:
            needed_sources.extend([
                "@SOURCES web_search",
                "@SOURCES documentation_search",
                "@SOURCES api_references"
            ])

        # Query-specific external sources
        query_lower = query.lower()

        if any(term in query_lower for term in ["api", "endpoint", "integration"]):
            needed_sources.append("@SOURCES api_documentation")

        if any(term in query_lower for term in ["tutorial", "guide", "how to"]):
            needed_sources.append("@SOURCES learning_resources")

        if any(term in query_lower for term in ["latest", "recent", "update", "news"]):
            needed_sources.append("@SOURCES recent_updates")

        return list(set(needed_sources))  # Remove duplicates

    def _create_external_search_plan(self, query: str, local_results: Dict[str, Any], external_sources: List[str]) -> str:
        """Create a plan for external search to complete the research"""

        plan_parts = [f"Local research completed for: {query}\n"]

        # Summarize what was found locally
        total_local_matches = (
            local_results.get("knowledge_base", {}).get("total_matches", 0) +
            local_results.get("syphon_data", {}).get("relevant_entries", 0) +
            local_results.get("project_docs", {}).get("total_matches", 0)
        )

        plan_parts.append(f"📊 Local search found {total_local_matches} relevant matches")

        # Specify what external sources are needed
        plan_parts.append("🔍 External sources needed:")
        for source in external_sources:
            plan_parts.append(f"  • {source}")

        plan_parts.append("\n📋 External search plan:")
        plan_parts.append("  1. Query external APIs and documentation")
        plan_parts.append("  2. Cross-reference with local findings")
        plan_parts.append("  3. Synthesize comprehensive answer")
        plan_parts.append("  4. Cache results for future local searches")

        return "\n".join(plan_parts)

    def get_research_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent research history"""
        return self.research_history[-limit:] if self.research_history else []

    def get_research_statistics(self) -> Dict[str, Any]:
        """Get research performance statistics"""
        if not self.research_history:
            return {"total_researches": 0}

        total_researches = len(self.research_history)
        local_only_researches = sum(1 for r in self.research_history if not r.get("external_search_needed", False))
        avg_confidence = sum(r.get("confidence_score", 0) for r in self.research_history) / total_researches

        return {
            "total_researches": total_researches,
            "local_only_percentage": (local_only_researches / total_researches) * 100,
            "external_search_percentage": ((total_researches - local_only_researches) / total_researches) * 100,
            "average_confidence_score": avg_confidence,
            "most_recent_research": self.research_history[-1]["query"] if self.research_history else None
        }


async def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Local-First Research System")
    parser.add_argument("action", choices=["research", "index", "stats", "history"], help="Action to perform")
    parser.add_argument("--query", help="Research query")
    parser.add_argument("--limit", type=int, default=10, help="Result limit")

    args = parser.parse_args()

    research_system = JARVISLocalFirstResearch()

    try:
        if args.action == "index":
            await research_system.initialize_knowledge_base()
            print("✅ Local knowledge base indexed successfully")

        elif args.action == "research":
            if not args.query:
                print("❌ Please provide a query with --query")
                return 1

            await research_system.initialize_knowledge_base()
            result = await research_system.research_query(args.query)

            print("🔍 JARVIS Local-First Research Results")
            print("=" * 50)
            print(f"Query: {result['query']}")
            print(f"Local Search: {'✅ Performed' if result['local_search_performed'] else '❌ Not performed'}")
            print(f"External Search Needed: {'✅ Yes' if result['external_search_needed'] else '❌ No'}")
            print(f"Confidence Score: {result['confidence_score']:.1%}")
            print(f"Research Path: {' → '.join(result['research_path'])}")
            print()

            if result['final_answer']:
                print("📋 Answer:")
                print(result['final_answer'])
            else:
                print("❌ No answer generated")

        elif args.action == "stats":
            stats = research_system.get_research_statistics()
            print("📊 JARVIS Research Statistics")
            print("=" * 30)
            print(f"Total Researches: {stats['total_researches']}")
            if stats['total_researches'] > 0:
                print(".1f")
                print(".1f")
                print(".2f")
                if stats['most_recent_research']:
                    print(f"Most Recent: {stats['most_recent_research']}")

        elif args.action == "history":
            history = research_system.get_research_history(args.limit)
            print("📚 JARVIS Research History")
            print("=" * 30)
            for i, entry in enumerate(history, 1):
                print(f"{i}. {entry['query']} ({entry['confidence_score']:.1%}) - {entry['timestamp'][:19]}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    asyncio.run(main())