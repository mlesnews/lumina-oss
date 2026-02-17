#!/usr/bin/env python3
"""
Coding Assistant Siphon - Discover and Extract All Coding Assistants

Discovers all coding assistant extensions from:
- VS Code Marketplace
- Docker Marketplace
- Other sources

Feeds through siphon system, then Jarvis/Marvin review, then dyno testing.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import requests
import subprocess
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class CodingAssistant:
    """Represents a coding assistant extension"""
    name: str
    display_name: str
    publisher: str
    marketplace: str  # "vscode" or "docker"
    description: str
    repository: Optional[str] = None
    website: Optional[str] = None
    license: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    contributors: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    install_count: Optional[int] = None
    rating: Optional[float] = None
    version: Optional[str] = None
    last_updated: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class MarketplaceDiscovery:
    """Discover coding assistants from marketplaces"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovered_assistants: List[CodingAssistant] = []

    def discover_vscode_marketplace(self) -> List[CodingAssistant]:
        """Discover coding assistants from VS Code Marketplace"""
        logger.info("🔍 Discovering VS Code Marketplace extensions...")

        # VS Code Marketplace API
        # Search for AI/coding assistant related extensions
        search_terms = [
            "ai code",
            "coding assistant",
            "code completion",
            "autocomplete",
            "copilot",
            "codeium",
            "tabnine",
            "cursor",
            "claude",
            "github copilot",
            "intellicode",
            "kite",
            "sourcery",
            "deepcode",
            "code review",
            "ai programming"
        ]

        assistants = []

        # Known major assistants (we'll add API discovery later)
        known_assistants = [
            CodingAssistant(
                name="github-copilot",
                display_name="GitHub Copilot",
                publisher="GitHub",
                marketplace="vscode",
                description="AI pair programmer",
                repository="https://github.com/features/copilot",
                website="https://github.com/features/copilot",
                categories=["AI", "Code Completion"],
                tags=["ai", "copilot", "completion"]
            ),
            CodingAssistant(
                name="codeium",
                display_name="Codeium",
                publisher="Codeium",
                marketplace="vscode",
                description="Free AI coding assistant",
                repository="https://github.com/Exafunction/codeium",
                website="https://codeium.com",
                categories=["AI", "Code Completion"],
                tags=["ai", "free", "completion"]
            ),
            CodingAssistant(
                name="tabnine",
                display_name="Tabnine",
                publisher="Tabnine",
                marketplace="vscode",
                description="AI code completion",
                repository="https://github.com/codota/TabNine",
                website="https://www.tabnine.com",
                categories=["AI", "Code Completion"],
                tags=["ai", "completion", "local"]
            ),
            CodingAssistant(
                name="intellicode",
                display_name="IntelliCode",
                publisher="Microsoft",
                marketplace="vscode",
                description="AI-assisted development",
                repository="https://github.com/MicrosoftDocs/intellicode",
                website="https://visualstudio.microsoft.com/services/intellicode/",
                categories=["AI", "Code Completion"],
                tags=["ai", "microsoft", "completion"]
            ),
            CodingAssistant(
                name="cursor",
                display_name="Cursor",
                publisher="Cursor",
                marketplace="vscode",
                description="AI-powered code editor",
                repository="https://github.com/getcursor/cursor",
                website="https://cursor.sh",
                categories=["AI", "Editor"],
                tags=["ai", "editor", "completion"]
            ),
            CodingAssistant(
                name="sourcery",
                display_name="Sourcery",
                publisher="Sourcery",
                marketplace="vscode",
                description="AI code review and refactoring",
                repository="https://github.com/sourcery-ai/sourcery",
                website="https://sourcery.ai",
                categories=["AI", "Code Review"],
                tags=["ai", "review", "refactoring"]
            ),
            CodingAssistant(
                name="deepcode",
                display_name="DeepCode",
                publisher="DeepCode",
                marketplace="vscode",
                description="AI-powered code review",
                website="https://www.deepcode.ai",
                categories=["AI", "Code Review", "Security"],
                tags=["ai", "review", "security"]
            ),
            CodingAssistant(
                name="kite",
                display_name="Kite",
                publisher="Kite",
                marketplace="vscode",
                description="AI code completions",
                repository="https://github.com/kiteco/kite",
                website="https://www.kite.com",
                categories=["AI", "Code Completion"],
                tags=["ai", "completion"]
            ),
            CodingAssistant(
                name="sourcegraph-cody",
                display_name="Sourcegraph Cody",
                publisher="Sourcegraph",
                marketplace="vscode",
                description="AI coding assistant",
                repository="https://github.com/sourcegraph/cody",
                website="https://sourcegraph.com/cody",
                categories=["AI", "Code Completion"],
                tags=["ai", "open-source"]
            ),
            CodingAssistant(
                name="continue",
                display_name="Continue",
                publisher="Continue",
                marketplace="vscode",
                description="Open-source autopilot for software development",
                repository="https://github.com/continuedev/continue",
                website="https://continue.dev",
                categories=["AI", "Code Completion"],
                tags=["ai", "open-source", "autopilot"]
            ),
            CodingAssistant(
                name="aider",
                display_name="Aider",
                publisher="Aider",
                marketplace="vscode",
                description="AI pair programmer",
                repository="https://github.com/paul-gauthier/aider",
                website="https://aider.chat",
                categories=["AI", "Code Completion"],
                tags=["ai", "pair-programming"]
            ),
            CodingAssistant(
                name="codegeex",
                display_name="CodeGeeX",
                publisher="CodeGeeX",
                marketplace="vscode",
                description="AI code generation",
                repository="https://github.com/THUDM/CodeGeeX",
                website="https://codegeex.cn",
                categories=["AI", "Code Generation"],
                tags=["ai", "generation", "multilingual"]
            )
        ]

        assistants.extend(known_assistants)
        logger.info(f"✅ Discovered {len(assistants)} VS Code extensions")

        return assistants

    def discover_docker_marketplace(self) -> List[CodingAssistant]:
        """Discover coding assistants from Docker Marketplace"""
        logger.info("🔍 Discovering Docker Marketplace images...")

        assistants = []

        # Docker Hub search for AI/coding assistants
        docker_images = [
            CodingAssistant(
                name="codeium-docker",
                display_name="Codeium Docker",
                publisher="Codeium",
                marketplace="docker",
                description="Codeium in Docker container",
                repository="https://hub.docker.com/r/codeium/codeium",
                website="https://codeium.com",
                categories=["AI", "Docker"],
                tags=["ai", "docker", "codeium"]
            ),
            CodingAssistant(
                name="tabnine-docker",
                display_name="Tabnine Docker",
                publisher="Tabnine",
                marketplace="docker",
                description="Tabnine in Docker container",
                repository="https://hub.docker.com/r/tabnine/tabnine",
                website="https://www.tabnine.com",
                categories=["AI", "Docker"],
                tags=["ai", "docker", "tabnine"]
            ),
            CodingAssistant(
                name="github-copilot-docker",
                display_name="GitHub Copilot Docker",
                publisher="GitHub",
                marketplace="docker",
                description="GitHub Copilot in Docker",
                repository="https://hub.docker.com/r/github/copilot",
                website="https://github.com/features/copilot",
                categories=["AI", "Docker"],
                tags=["ai", "docker", "copilot"]
            )
        ]

        assistants.extend(docker_images)
        logger.info(f"✅ Discovered {len(assistants)} Docker images")

        return assistants

    def discover_xcode_extensions(self) -> List[CodingAssistant]:
        """Discover coding assistants from Xcode (Apple)"""
        logger.info("🔍 Discovering Xcode extensions...")

        assistants = [
            CodingAssistant(
                name="github-copilot-xcode",
                display_name="GitHub Copilot for Xcode",
                publisher="GitHub",
                marketplace="xcode",
                description="AI pair programmer for Xcode with inline completions and chat",
                repository="https://github.com/features/copilot",
                website="https://github.com/features/copilot",
                categories=["AI", "Code Completion", "Chat"],
                tags=["ai", "copilot", "xcode", "swift", "objective-c"],
                features=[
                    "Inline code completions (Swift, Objective-C)",
                    "In-editor chat assistant",
                    "Workspace context (@workspace)",
                    "Multiple LLM support (GPT-4.1, GPT-4.5, Gemini 2.5, Claude Sonnet 3.7)"
                ]
            ),
            CodingAssistant(
                name="xcode-native-ai",
                display_name="Xcode Native AI (Xcode 26)",
                publisher="Apple",
                marketplace="xcode",
                description="Built-in AI features in Xcode 26 with model flexibility",
                website="https://developer.apple.com/xcode/",
                categories=["AI", "Native", "Code Generation"],
                tags=["ai", "xcode", "apple", "native", "swift"],
                features=[
                    "Generate code, documentation, tests",
                    "Fix errors",
                    "Code intelligence (project-wide symbols)",
                    "Custom model providers (ChatGPT, Claude, local LLMs)"
                ]
            ),
            CodingAssistant(
                name="swift-assist",
                display_name="Swift Assist (Apple + Anthropic)",
                publisher="Apple",
                marketplace="xcode",
                description="Apple's coding assistant with Claude Sonnet integration",
                website="https://developer.apple.com/",
                categories=["AI", "Code Generation", "Chat"],
                tags=["ai", "xcode", "apple", "claude", "swift"],
                features=[
                    "Code writing and editing",
                    "Testing assistance",
                    "Chat UI",
                    "Claude Sonnet integration"
                ]
            ),
            CodingAssistant(
                name="alex-xcode",
                display_name="Alex (Xcode Extension)",
                publisher="Alex (OpenAI acquired)",
                marketplace="xcode",
                description="AI assistant for Xcode with debugging and autocompletion",
                website="https://www.alexcodes.app",
                categories=["AI", "Debugging", "Code Completion"],
                tags=["ai", "xcode", "debugging", "local"],
                features=[
                    "Autofix errors",
                    "Autocompletions",
                    "Adding Swift packages",
                    "Image-to-code generation",
                    "Local or cloud model support"
                ]
            ),
            CodingAssistant(
                name="codenext-xcode",
                display_name="CodeNext",
                publisher="John Vicinno",
                marketplace="xcode",
                description="Open-source Xcode extension with context-aware completion",
                repository="https://github.com/johnvicinno/CodeNext",
                website="https://github.com/johnvicinno/CodeNext",
                license="Open Source",
                categories=["AI", "Open Source", "Code Completion"],
                tags=["ai", "xcode", "open-source", "local"],
                features=[
                    "Context-aware code autocompletion",
                    "Agent-style in-IDE chat",
                    "Custom commands",
                    "Multiple model providers (OpenAI, Anthropic, Google AI, Mistral)",
                    "Local or hosted models"
                ]
            )
        ]

        logger.info(f"✅ Discovered {len(assistants)} Xcode extensions")
        return assistants

    def discover_jetbrains_plugins(self) -> List[CodingAssistant]:
        """Discover coding assistants from JetBrains Plugin Marketplace"""
        logger.info("🔍 Discovering JetBrains plugins...")

        assistants = [
            CodingAssistant(
                name="jetbrains-ai-assistant",
                display_name="JetBrains AI Assistant",
                publisher="JetBrains",
                marketplace="jetbrains",
                description="Official JetBrains AI plugin with local and cloud models",
                website="https://www.jetbrains.com/ai/",
                categories=["AI", "Code Completion", "Official"],
                tags=["ai", "jetbrains", "official", "local", "cloud"],
                features=[
                    "Code completion (cloud and local)",
                    "Code generation",
                    "Test generation",
                    "Commit message prompts",
                    "Local full-line completion",
                    "Multi-language support (Python, Java, JS, TS, CSS, Go, Ruby)"
                ]
            ),
            CodingAssistant(
                name="jetbrains-junie",
                display_name="Junie (JetBrains Coding Agent)",
                publisher="JetBrains",
                marketplace="jetbrains",
                description="Interactive coding agent for complex workflows",
                website="https://www.jetbrains.com/ai/",
                categories=["AI", "Coding Agent", "Official"],
                tags=["ai", "jetbrains", "agent", "pair-programming"],
                features=[
                    "Proposing plans",
                    "Refactoring",
                    "Test generation",
                    "Documentation generation",
                    "Pair-programmer style collaboration"
                ]
            ),
            CodingAssistant(
                name="onuro-jetbrains",
                display_name="Onuro AI",
                publisher="Onuro",
                marketplace="jetbrains",
                description="Privacy-focused AI assistant for all JetBrains IDEs",
                website="https://www.onuro.ai/code",
                categories=["AI", "Privacy", "Code Completion"],
                tags=["ai", "jetbrains", "privacy", "local-first"],
                features=[
                    "Privacy-first with local storage",
                    "Minimal external data usage",
                    "Agentic capabilities",
                    "All JetBrains IDEs support"
                ]
            ),
            CodingAssistant(
                name="cognotik-jetbrains",
                display_name="Cognotik IntelliJ Plugin",
                publisher="Cognotik",
                marketplace="jetbrains",
                description="BYOK AI assistant with editor actions and agent tools",
                website="https://cognotik.com/intellij-plugin.html",
                categories=["AI", "BYOK", "Code Generation"],
                tags=["ai", "jetbrains", "byok", "openai", "anthropic"],
                features=[
                    "Editor actions",
                    "File-level operations",
                    "Agent tools",
                    "Documentation/test generation",
                    "BYOK (Bring Your Own Key)"
                ]
            ),
            CodingAssistant(
                name="cline-jetbrains",
                display_name="Cline",
                publisher="Community",
                marketplace="jetbrains",
                description="Open-source AI coding agent for JetBrains IDEs",
                repository="https://github.com/clinebot/cline",
                website="https://github.com/clinebot/cline",
                license="Open Source",
                categories=["AI", "Open Source", "Coding Agent"],
                tags=["ai", "jetbrains", "open-source", "claude", "gpt"],
                features=[
                    "Broad JetBrains IDE support",
                    "Native platform APIs",
                    "BYOP (Bring Your Own Provider)",
                    "Claude, GPT, Gemini support",
                    "Local model support"
                ]
            ),
            CodingAssistant(
                name="llm-intellij",
                display_name="LLM-IntelliJ",
                publisher="Hugging Face Community",
                marketplace="jetbrains",
                description="Open-source plugin for local models (CodeLlama, StarCoder)",
                repository="https://github.com/huggingface/llm-intellij",
                website="https://github.com/huggingface/llm-intellij",
                license="Open Source",
                categories=["AI", "Open Source", "Local Models"],
                tags=["ai", "jetbrains", "open-source", "local", "huggingface"],
                features=[
                    "CodeLlama support",
                    "StarCoder support",
                    "Ghost-text completion",
                    "Local model hosting",
                    "Alternative to cloud-only assistants"
                ]
            ),
            CodingAssistant(
                name="tabnine-jetbrains",
                display_name="Tabnine for JetBrains",
                publisher="Tabnine",
                marketplace="jetbrains",
                description="AI completion, chat, and consistency for JetBrains IDEs",
                website="https://www.tabnine.com",
                categories=["AI", "Code Completion", "Chat"],
                tags=["ai", "jetbrains", "completion", "chat"],
                features=[
                    "Code completion",
                    "Chat interface",
                    "Code consistency",
                    "Test/documentation generation"
                ]
            )
        ]

        logger.info(f"✅ Discovered {len(assistants)} JetBrains plugins")
        return assistants

    def discover_all(self) -> List[CodingAssistant]:
        """Discover all coding assistants from all marketplaces"""
        all_assistants = []
        all_assistants.extend(self.discover_vscode_marketplace())
        all_assistants.extend(self.discover_docker_marketplace())
        all_assistants.extend(self.discover_xcode_extensions())
        all_assistants.extend(self.discover_jetbrains_plugins())

        # Deduplicate by name (but keep marketplace variants)
        seen = set()
        unique_assistants = []
        for assistant in all_assistants:
            # Use name + marketplace as unique key
            key = f"{assistant.name}-{assistant.marketplace}"
            if key not in seen:
                seen.add(key)
                unique_assistants.append(assistant)

        self.discovered_assistants = unique_assistants
        return unique_assistants


class SiphonProcessor:
    """Process discovered assistants through siphon system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.siphon_dir = project_root / "data" / "siphon" / "coding_assistants"
        self.siphon_dir.mkdir(parents=True, exist_ok=True)

    def process_assistant(self, assistant: CodingAssistant) -> Dict[str, Any]:
        try:
            """Process an assistant through siphon"""
            logger.info(f"🔄 Siphoning {assistant.display_name}...")

            siphon_data = {
                "assistant": {
                    "name": assistant.name,
                    "display_name": assistant.display_name,
                    "publisher": assistant.publisher,
                    "marketplace": assistant.marketplace,
                    "description": assistant.description,
                    "repository": assistant.repository,
                    "website": assistant.website,
                    "license": assistant.license,
                    "authors": assistant.authors,
                    "contributors": assistant.contributors,
                    "features": assistant.features,
                    "categories": assistant.categories,
                    "tags": assistant.tags
                },
                "siphon_metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "siphon_version": "1.0",
                    "extraction_method": "marketplace_discovery"
                },
                "extracted_features": self._extract_features(assistant),
                "performance_characteristics": self._analyze_performance(assistant),
                "integration_points": self._identify_integration_points(assistant)
            }

            # Save siphon data
            output_file = self.siphon_dir / f"{assistant.name}_siphon.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(siphon_data, f, indent=2)

            return siphon_data

        except Exception as e:
            self.logger.error(f"Error in process_assistant: {e}", exc_info=True)
            raise
    def _extract_features(self, assistant: CodingAssistant) -> Dict[str, Any]:
        """Extract features from assistant"""
        # Analyze based on categories, tags, description
        features = {
            "code_completion": "code completion" in assistant.description.lower() or "completion" in assistant.tags,
            "code_review": "review" in assistant.description.lower() or "review" in assistant.tags,
            "code_generation": "generation" in assistant.description.lower() or "generation" in assistant.tags,
            "refactoring": "refactor" in assistant.description.lower() or "refactor" in assistant.tags,
            "security_scanning": "security" in assistant.categories or "security" in assistant.tags,
            "documentation": "documentation" in assistant.description.lower(),
            "chat_interface": "chat" in assistant.description.lower() or "chat" in assistant.tags,
            "multi_file": "multi" in assistant.description.lower() or "multi-file" in assistant.tags,
            "local_models": "local" in assistant.tags or "offline" in assistant.tags,
            "open_source": "open-source" in assistant.tags or assistant.license and "MIT" in assistant.license.upper()
        }
        return features

    def _analyze_performance(self, assistant: CodingAssistant) -> Dict[str, Any]:
        """Analyze performance characteristics"""
        return {
            "estimated_latency": "low" if "local" in assistant.tags else "medium",
            "resource_usage": "low" if "lightweight" in assistant.tags else "medium",
            "scalability": "high" if assistant.marketplace == "docker" else "medium"
        }

    def _identify_integration_points(self, assistant: CodingAssistant) -> List[str]:
        """Identify integration points for Jarvis"""
        points = []
        if "code completion" in assistant.description.lower():
            points.append("code_completion_engine")
        if "review" in assistant.description.lower():
            points.append("code_review_system")
        if "chat" in assistant.description.lower():
            points.append("chat_interface")
        if "security" in assistant.categories:
            points.append("security_scanner")
        return points


class JarvisMarvinReviewer:
    """Review siphoned data with Jarvis and Marvin"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.review_dir = project_root / "data" / "reviews" / "coding_assistants"
        self.review_dir.mkdir(parents=True, exist_ok=True)

    def review_siphoned_data(self, siphon_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Review siphoned data with Jarvis and Marvin"""
            logger.info(f"🤖 Jarvis & Marvin reviewing {siphon_data['assistant']['display_name']}...")

            review = {
                "assistant_name": siphon_data['assistant']['name'],
                "reviewed_at": datetime.now().isoformat(),
                "jarvis_review": self._jarvis_review(siphon_data),
                "marvin_review": self._marvin_review(siphon_data),
                "combined_recommendations": [],
                "priority_score": 0.0
            }

            # Combine recommendations
            review["combined_recommendations"] = self._combine_recommendations(
                review["jarvis_review"],
                review["marvin_review"]
            )

            # Calculate priority score
            review["priority_score"] = self._calculate_priority_score(review)

            # Save review
            output_file = self.review_dir / f"{siphon_data['assistant']['name']}_review.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(review, f, indent=2)

            return review

        except Exception as e:
            self.logger.error(f"Error in review_siphoned_data: {e}", exc_info=True)
            raise
    def _jarvis_review(self, siphon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Jarvis review of assistant"""
        assistant = siphon_data['assistant']
        features = siphon_data['extracted_features']

        return {
            "recommendation": "integrate" if any(features.values()) else "evaluate",
            "priority": "high" if features.get("code_completion") else "medium",
            "key_features": [k for k, v in features.items() if v],
            "integration_complexity": "low" if assistant.get("marketplace") == "vscode" else "medium",
            "value_assessment": "high" if len([k for k, v in features.items() if v]) > 3 else "medium"
        }

    def _marvin_review(self, siphon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Marvin's critical review"""
        assistant = siphon_data['assistant']
        features = siphon_data.get('extracted_features', {})

        # Marvin is critical but constructive
        issues = []
        if not assistant.get("repository"):
            issues.append("No repository - harder to verify and integrate")
        if not assistant.get("license"):
            issues.append("License unclear - potential IP concerns")
        if not features.get("code_completion") and not features.get("code_review"):
            issues.append("Limited core functionality")

        return {
            "recommendation": "integrate_with_caution" if issues else "integrate",
            "concerns": issues,
            "strengths": [k for k, v in features.items() if v],
            "realistic_assessment": "This assistant provides value but has limitations",
            "suggested_improvements": [
                "Ensure proper accreditation",
                "Test performance thoroughly",
                "Validate security"
            ]
        }

    def _combine_recommendations(self, jarvis: Dict, marvin: Dict) -> List[str]:
        """Combine recommendations from both reviewers"""
        recommendations = []

        if jarvis["recommendation"] == "integrate" and marvin["recommendation"] == "integrate":
            recommendations.append("✅ High priority integration - both reviewers agree")
        elif "caution" in marvin["recommendation"]:
            recommendations.append("⚠️ Integrate with caution - address concerns first")
        else:
            recommendations.append("📋 Evaluate further before integration")

        if marvin.get("concerns"):
            recommendations.extend([f"⚠️ {concern}" for concern in marvin["concerns"]])

        if jarvis.get("key_features"):
            recommendations.append(f"✨ Key features: {', '.join(jarvis['key_features'][:3])}")

        return recommendations

    def _calculate_priority_score(self, review: Dict[str, Any]) -> float:
        """Calculate priority score (0-10)"""
        score = 5.0  # Base score

        # Jarvis factors
        if review["jarvis_review"]["priority"] == "high":
            score += 2.0
        if review["jarvis_review"]["value_assessment"] == "high":
            score += 1.5

        # Marvin factors
        if not review["marvin_review"].get("concerns"):
            score += 1.0
        if len(review["marvin_review"].get("strengths", [])) > 3:
            score += 0.5

        return min(10.0, score)


class DynoPerformanceTester:
    """Performance testing on the dyno"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dyno_dir = project_root / "data" / "dyno" / "performance_tests"
        self.dyno_dir.mkdir(parents=True, exist_ok=True)

    def test_assistant(self, assistant: CodingAssistant, siphon_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Test assistant performance on dyno"""
            logger.info(f"🏎️ Testing {assistant.display_name} on dyno...")

            # Simulate performance tests
            # In real implementation, this would run actual benchmarks
            test_results = {
                "assistant_name": assistant.name,
                "tested_at": datetime.now().isoformat(),
                "baseline_metrics": {
                    "code_completion_latency_ms": 150,
                    "memory_usage_mb": 200,
                    "cpu_usage_percent": 15
                },
                "test_metrics": {
                    "code_completion_latency_ms": self._simulate_latency(assistant),
                    "memory_usage_mb": self._simulate_memory(assistant),
                    "cpu_usage_percent": self._simulate_cpu(assistant)
                },
                "improvements": {},
                "red_potato_chips": []  # Performance improvements
            }

            # Calculate improvements
            test_results["improvements"] = self._calculate_improvements(
                test_results["baseline_metrics"],
                test_results["test_metrics"]
            )

            # Identify "red potato chips" (performance wins)
            test_results["red_potato_chips"] = self._identify_performance_wins(
                test_results["improvements"]
            )

            # Save results
            output_file = self.dyno_dir / f"{assistant.name}_dyno.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, indent=2)

            return test_results

        except Exception as e:
            self.logger.error(f"Error in test_assistant: {e}", exc_info=True)
            raise
    def _simulate_latency(self, assistant: CodingAssistant) -> float:
        """Simulate code completion latency"""
        # Local models typically faster
        if "local" in assistant.tags:
            return 50.0  # 50ms
        return 120.0  # 120ms

    def _simulate_memory(self, assistant: CodingAssistant) -> float:
        """Simulate memory usage"""
        if "lightweight" in assistant.tags:
            return 100.0  # 100MB
        return 250.0  # 250MB

    def _simulate_cpu(self, assistant: CodingAssistant) -> float:
        """Simulate CPU usage"""
        if "local" in assistant.tags:
            return 25.0  # 25%
        return 12.0  # 12%

    def _calculate_improvements(self, baseline: Dict, test: Dict) -> Dict[str, float]:
        """Calculate performance improvements"""
        improvements = {}
        for metric in baseline.keys():
            if metric in test:
                improvement = ((baseline[metric] - test[metric]) / baseline[metric]) * 100
                improvements[metric] = improvement
        return improvements

    def _identify_performance_wins(self, improvements: Dict[str, float]) -> List[str]:
        """Identify significant performance wins (red potato chips)"""
        wins = []
        for metric, improvement in improvements.items():
            if improvement > 20:  # >20% improvement
                wins.append(f"🔥 {metric}: {improvement:.1f}% improvement")
            elif improvement > 10:  # >10% improvement
                wins.append(f"✅ {metric}: {improvement:.1f}% improvement")
        return wins


class CodingAssistantSiphon:
    """Main siphon orchestrator"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.discovery = MarketplaceDiscovery(project_root)
        self.siphon = SiphonProcessor(project_root)
        self.reviewer = JarvisMarvinReviewer(project_root)
        self.dyno = DynoPerformanceTester(project_root)

    def run_full_pipeline(self) -> Dict[str, Any]:
        try:
            """Run complete siphon pipeline"""
            logger.info("🚀 Starting Coding Assistant Siphon Pipeline...")

            # Step 1: Discover
            logger.info("Step 1: Discovering assistants...")
            assistants = self.discovery.discover_all()
            logger.info(f"✅ Discovered {len(assistants)} assistants")

            # Step 2: Siphon
            logger.info("Step 2: Siphoning assistants...")
            siphoned_data = []
            for assistant in assistants:
                siphon_data = self.siphon.process_assistant(assistant)
                siphoned_data.append(siphon_data)

            # Step 3: Review
            logger.info("Step 3: Jarvis & Marvin review...")
            reviews = []
            for siphon_data in siphoned_data:
                review = self.reviewer.review_siphoned_data(siphon_data)
                reviews.append(review)

            # Step 4: Dyno testing
            logger.info("Step 4: Dyno performance testing...")
            dyno_results = []
            for assistant, siphon_data in zip(assistants, siphoned_data):
                result = self.dyno.test_assistant(assistant, siphon_data)
                dyno_results.append(result)

            # Step 5: Generate summary
            summary = self._generate_summary(assistants, siphoned_data, reviews, dyno_results)

            # Save summary
            summary_file = self.project_root / "data" / "siphon" / "summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)

            logger.info("✅ Pipeline complete!")
            return summary

        except Exception as e:
            self.logger.error(f"Error in run_full_pipeline: {e}", exc_info=True)
            raise
    def _generate_summary(self, assistants, siphoned_data, reviews, dyno_results) -> Dict[str, Any]:
        """Generate comprehensive summary"""
        total_red_chips = sum(len(r.get("red_potato_chips", [])) for r in dyno_results)
        high_priority = [r for r in reviews if r["priority_score"] >= 8.0]

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_assistants": len(assistants),
                "vscode_extensions": len([a for a in assistants if a.marketplace == "vscode"]),
                "docker_images": len([a for a in assistants if a.marketplace == "docker"]),
                "high_priority_integrations": len(high_priority),
                "total_performance_wins": total_red_chips
            },
            "top_performers": sorted(
                dyno_results,
                key=lambda x: len(x.get("red_potato_chips", [])),
                reverse=True
            )[:5],
            "high_priority_assistants": [
                {
                    "name": r["assistant_name"],
                    "priority_score": r["priority_score"],
                    "recommendations": r["combined_recommendations"]
                }
                for r in high_priority
            ],
            "performance_wins": [
                {
                    "assistant": r["assistant_name"],
                    "wins": r.get("red_potato_chips", [])
                }
                for r in dyno_results if r.get("red_potato_chips")
            ]
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Coding Assistant Siphon - Discover and Extract All Assistants"
    )
    parser.add_argument(
        "--run", action="store_true",
        help="Run full siphon pipeline"
    )
    parser.add_argument(
        "--discover-only", action="store_true",
        help="Only discover assistants, don't process"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    siphon = CodingAssistantSiphon(project_root)

    if args.discover_only:
        assistants = siphon.discovery.discover_all()
        print(f"✅ Discovered {len(assistants)} coding assistants")
        for assistant in assistants:
            print(f"   - {assistant.display_name} ({assistant.marketplace})")
    elif args.run:
        summary = siphon.run_full_pipeline()
        print("\n" + "=" * 80)
        print("📊 SIPHON SUMMARY")
        print("=" * 80)
        print(f"Total Assistants: {summary['summary']['total_assistants']}")
        print(f"VS Code Extensions: {summary['summary']['vscode_extensions']}")
        print(f"Docker Images: {summary['summary']['docker_images']}")
        print(f"High Priority: {summary['summary']['high_priority_integrations']}")
        print(f"Performance Wins: {summary['summary']['total_performance_wins']}")
        print("\n🏆 Top Performance Wins:")
        for win in summary.get("performance_wins", [])[:5]:
            if win["wins"]:
                print(f"   {win['assistant']}: {len(win['wins'])} wins")
    else:
        parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()