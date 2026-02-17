#!/usr/bin/env python3
"""
Cloud AI Provider Tracker System

Tracks cloud AI providers (OpenAI, Anthropic, Google, etc.) to identify:
- Traits (capabilities, characteristics)
- Specialties (what they excel at)
- Uniqueness (what makes them unique)
- @Sparks (insights and learnings)
- Best tool for the job (learning system)

Integrates with:
- #decisioning engine
- @sparks system
- Auto mode decision tree

Tags: #CLOUD_AI #PROVIDER_TRACKING #DECISIONING #SPARKS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import insights/sparks system
try:
    from insights_sparks_system import InsightsSparksSystem, capture_spark
    SPARKS_AVAILABLE = True
except ImportError:
    SPARKS_AVAILABLE = False
    logger = get_logger("CloudAIProviderTracker")
    logger.warning("⚠️  Insights/Sparks system not available")

logger = get_logger("CloudAIProviderTracker")


class ProviderType(Enum):
    """AI provider types (local and cloud)"""
    # Local AI Providers
    ULTRON = "ultron"  # ULTRON Hybrid Cluster (local + KAIJU)
    IRON_LEGION = "iron_legion"  # KAIJU Iron Legion Cluster
    KAIJU_IRON_LEGION = "kaiju_iron_legion"  # KAIJU NAS Iron Legion
    ULTRON_LOCAL = "ultron_local"  # Local ULTRON (localhost)
    IRON_LEGION_ROUTER = "iron_legion_router"  # Iron Legion Router
    LOCAL_CLUSTER = "local_cluster"  # Generic local cluster
    DOCKER_OLLAMA = "docker_ollama"  # Docker Ollama

    # Cloud AI Providers
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"
    COHERE = "cohere"
    MISTRAL = "mistral"
    PERPLEXITY = "perplexity"
    GROQ = "groq"
    TOGETHER = "together"
    OTHER = "other"


class TaskCategory(Enum):
    """Task categories for learning best provider"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    REASONING = "reasoning"
    CREATIVE = "creative"
    MULTI_MODAL = "multi_modal"
    CONVERSATION = "conversation"
    RESEARCH = "research"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"


@dataclass
class ProviderTrait:
    """A trait of a cloud AI provider"""
    name: str
    description: str
    category: str  # e.g., "capability", "performance", "cost", "safety"
    strength: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)  # Evidence for this trait


@dataclass
class ProviderSpecialty:
    """A specialty area where a provider excels"""
    area: str
    description: str
    confidence: float  # 0.0 to 1.0
    success_rate: float  # 0.0 to 1.0
    examples: List[str] = field(default_factory=list)


@dataclass
class ProviderUniqueness:
    """What makes a provider unique"""
    feature: str
    description: str
    uniqueness_score: float  # 0.0 to 1.0
    comparison: Dict[str, str] = field(default_factory=dict)  # vs other providers


@dataclass
class ProviderSpark:
    """A @spark (insight) about a provider"""
    spark_id: str
    content: str
    timestamp: datetime
    source: str
    context: Dict[str, Any] = field(default_factory=dict)
    impact_score: float = 0.0


@dataclass
class JobPerformance:
    """Performance record for a provider on a specific job type"""
    task_category: TaskCategory
    provider: ProviderType
    success_count: int = 0
    failure_count: int = 0
    total_time: float = 0.0  # seconds
    quality_score: float = 0.0  # 0.0 to 1.0
    cost_per_job: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    @property
    def average_time(self) -> float:
        """Calculate average time per job"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.total_time / total

    @property
    def overall_score(self) -> float:
        """Calculate overall performance score"""
        # Weighted combination: success_rate (40%), quality (30%), speed (20%), cost (10%)
        speed_score = 1.0 / (1.0 + self.average_time / 60.0)  # Normalize to 0-1
        cost_score = 1.0 / (1.0 + self.cost_per_job / 0.10)  # Normalize to 0-1

        return (
            self.success_rate * 0.4 +
            self.quality_score * 0.3 +
            speed_score * 0.2 +
            cost_score * 0.1
        )


@dataclass
class ProviderPowerLevel:
    """Power/performance level of a provider"""
    level: int  # 1-10, where 1 is least powerful, 10 is most powerful
    description: str
    suitable_for: List[str]  # Task types this power level can handle


@dataclass
class ProviderCost:
    """Cost information for a provider"""
    cost_per_1k_tokens_input: float = 0.0  # Cost per 1K input tokens
    cost_per_1k_tokens_output: float = 0.0  # Cost per 1K output tokens
    cost_per_request: float = 0.0  # Fixed cost per request
    is_free: bool = False  # True for local providers
    cost_category: str = "unknown"  # "free", "low", "medium", "high"


@dataclass
class CloudAIProvider:
    """Complete cloud AI provider profile"""
    provider_type: ProviderType
    name: str
    description: str
    models: List[str] = field(default_factory=list)
    traits: List[ProviderTrait] = field(default_factory=list)
    specialties: List[ProviderSpecialty] = field(default_factory=list)
    uniqueness: List[ProviderUniqueness] = field(default_factory=list)
    sparks: List[ProviderSpark] = field(default_factory=list)
    job_performance: Dict[TaskCategory, JobPerformance] = field(default_factory=dict)
    power_level: Optional[ProviderPowerLevel] = None  # Power/performance level
    cost: Optional[ProviderCost] = None  # Cost information
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "provider_type": self.provider_type.value,
            "name": self.name,
            "description": self.description,
            "models": self.models,
            "traits": [asdict(t) for t in self.traits],
            "specialties": [asdict(s) for s in self.specialties],
            "uniqueness": [asdict(u) for u in self.uniqueness],
            "sparks": [
                {
                    "spark_id": s.spark_id,
                    "content": s.content,
                    "timestamp": s.timestamp.isoformat(),
                    "source": s.source,
                    "context": s.context,
                    "impact_score": s.impact_score
                }
                for s in self.sparks
            ],
            "job_performance": {
                cat.value: asdict(perf) if perf else None
                for cat, perf in self.job_performance.items()
            },
            "power_level": asdict(self.power_level) if self.power_level else None,
            "cost": asdict(self.cost) if self.cost else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CloudAIProvider':
        """Create from dictionary"""
        provider = cls(
            provider_type=ProviderType(data["provider_type"]),
            name=data["name"],
            description=data["description"],
            models=data.get("models", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

        # Load traits
        for t_data in data.get("traits", []):
            provider.traits.append(ProviderTrait(**t_data))

        # Load specialties
        for s_data in data.get("specialties", []):
            provider.specialties.append(ProviderSpecialty(**s_data))

        # Load uniqueness
        for u_data in data.get("uniqueness", []):
            provider.uniqueness.append(ProviderUniqueness(**u_data))

        # Load sparks
        for spark_data in data.get("sparks", []):
            provider.sparks.append(ProviderSpark(
                spark_id=spark_data["spark_id"],
                content=spark_data["content"],
                timestamp=datetime.fromisoformat(spark_data["timestamp"]),
                source=spark_data["source"],
                context=spark_data.get("context", {}),
                impact_score=spark_data.get("impact_score", 0.0)
            ))

        # Load job performance
        for cat_str, perf_data in data.get("job_performance", {}).items():
            if perf_data:
                cat = TaskCategory(cat_str)
                perf_data["task_category"] = cat
                perf_data["provider"] = provider.provider_type
                perf_data["last_updated"] = datetime.fromisoformat(perf_data.get("last_updated", datetime.now().isoformat()))
                provider.job_performance[cat] = JobPerformance(**perf_data)

        # Load power level
        if data.get("power_level"):
            provider.power_level = ProviderPowerLevel(**data["power_level"])

        # Load cost
        if data.get("cost"):
            provider.cost = ProviderCost(**data["cost"])

        return provider


class CloudAIProviderTracker:
    """
    Cloud AI Provider Tracker System

    Tracks cloud AI providers to identify:
    - Traits (capabilities, characteristics)
    - Specialties (what they excel at)
    - Uniqueness (what makes them unique)
    - @Sparks (insights and learnings)
    - Best tool for the job (learning system)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Cloud AI Provider Tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cloud_ai_providers"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize insights/sparks system
        self.sparks_system = None
        if SPARKS_AVAILABLE:
            try:
                from insights_sparks_system import InsightsSparksSystem
                self.sparks_system = InsightsSparksSystem(project_root=self.project_root)
                logger.info("✅ Insights/Sparks system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Sparks system init error: {e}")

        # Load providers
        self.providers: Dict[ProviderType, CloudAIProvider] = {}
        self._load_providers()

        # Initialize default providers if none exist
        if not self.providers:
            self._initialize_default_providers()

        logger.info("=" * 80)
        logger.info("☁️  CLOUD AI PROVIDER TRACKER")
        logger.info(f"   Tracking {len(self.providers)} providers")
        logger.info("=" * 80)

    def _load_providers(self):
        """Load providers from disk"""
        providers_file = self.data_dir / "providers.json"

        if not providers_file.exists():
            return

        try:
            with open(providers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for provider_data in data.get("providers", []):
                provider = CloudAIProvider.from_dict(provider_data)
                self.providers[provider.provider_type] = provider

            logger.info(f"✅ Loaded {len(self.providers)} providers from disk")
        except Exception as e:
            logger.warning(f"⚠️  Error loading providers: {e}")

    def _save_providers(self):
        """Save providers to disk"""
        providers_file = self.data_dir / "providers.json"

        try:
            data = {
                "version": "1.0.0",
                "updated_at": datetime.now().isoformat(),
                "providers": [p.to_dict() for p in self.providers.values()]
            }

            with open(providers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.debug(f"💾 Saved {len(self.providers)} providers to disk")
        except Exception as e:
            logger.error(f"❌ Error saving providers: {e}")

    def _initialize_default_providers(self):
        """Initialize default provider profiles"""
        logger.info("🔧 Initializing default provider profiles...")

        # ULTRON - Hybrid Cluster (Local + KAIJU)
        ultron = CloudAIProvider(
            provider_type=ProviderType.ULTRON,
            name="ULTRON",
            description="ULTRON Hybrid Cluster - combines local ULTRON and KAIJU Iron Legion for intelligent routing and failover",
            models=["qwen2.5:72b", "llama3.2:11b", "codellama:13b", "llama3", "codellama:13b"]
        )
        ultron.power_level = ProviderPowerLevel(
            level=7,  # High power for complex reasoning
            description="High-performance hybrid cluster suitable for complex tasks",
            suitable_for=["code_generation", "reasoning", "analysis", "debugging", "refactoring"]
        )
        ultron.cost = ProviderCost(
            cost_per_1k_tokens_input=0.0,
            cost_per_1k_tokens_output=0.0,
            cost_per_request=0.0,
            is_free=True,
            cost_category="free"
        )
        ultron.traits.append(ProviderTrait(
            name="Hybrid Routing",
            description="Intelligent routing between local and NAS nodes with automatic failover",
            category="capability",
            strength=0.95
        ))
        ultron.traits.append(ProviderTrait(
            name="Local-First",
            description="Privacy-first, no data leaves local network",
            category="privacy",
            strength=1.0
        ))
        ultron.traits.append(ProviderTrait(
            name="Zero Cost",
            description="No API costs, runs on local infrastructure",
            category="cost",
            strength=1.0
        ))
        ultron.specialties.append(ProviderSpecialty(
            area="Advanced Reasoning",
            description="Excellent for complex reasoning and multi-step tasks",
            confidence=0.9,
            success_rate=0.85
        ))
        ultron.specialties.append(ProviderSpecialty(
            area="Code Generation",
            description="Strong code generation with local models",
            confidence=0.85,
            success_rate=0.80
        ))
        ultron.uniqueness.append(ProviderUniqueness(
            feature="Hybrid Cluster Architecture",
            description="Combines laptop ULTRON and KAIJU NAS into single virtual cluster with intelligent routing",
            uniqueness_score=0.95,
            comparison={
                "Cloud Providers": "No network latency, complete privacy",
                "Pure Local": "Can leverage NAS resources for larger models"
            }
        ))
        ultron.uniqueness.append(ProviderUniqueness(
            feature="Default Model Protection",
            description="Protected as default model in Cursor IDE - always available",
            uniqueness_score=0.9,
            comparison={"Other Providers": "Always prioritized for local-first workflows"}
        ))
        self.providers[ProviderType.ULTRON] = ultron

        # Iron Legion - KAIJU Cluster
        iron_legion = CloudAIProvider(
            provider_type=ProviderType.IRON_LEGION,
            name="Iron Legion",
            description="KAIJU Iron Legion Cluster - expert model cluster on NAS for specialized tasks",
            models=["llama3", "codellama:13b", "qwen2.5:72b"]
        )
        iron_legion.power_level = ProviderPowerLevel(
            level=6,  # Medium-high power for specialized tasks
            description="Medium-high performance cluster suitable for specialized and batch tasks",
            suitable_for=["batch_processing", "code_generation", "analysis", "documentation"]
        )
        iron_legion.cost = ProviderCost(
            cost_per_1k_tokens_input=0.0,
            cost_per_1k_tokens_output=0.0,
            cost_per_request=0.0,
            is_free=True,
            cost_category="free"
        )
        iron_legion.traits.append(ProviderTrait(
            name="Expert Models",
            description="Specialized models for different task types",
            category="capability",
            strength=0.9
        ))
        iron_legion.traits.append(ProviderTrait(
            name="NAS-Based",
            description="Runs on KAIJU NAS for centralized resource management",
            category="infrastructure",
            strength=0.9
        ))
        iron_legion.traits.append(ProviderTrait(
            name="Load Balancing",
            description="Intelligent load balancing across multiple models",
            category="performance",
            strength=0.85
        ))
        iron_legion.specialties.append(ProviderSpecialty(
            area="Batch Processing",
            description="Excellent for parallel batch processing tasks",
            confidence=0.9,
            success_rate=0.85
        ))
        iron_legion.specialties.append(ProviderSpecialty(
            area="Multi-Model Routing",
            description="Routes to best model for each task type",
            confidence=0.85,
            success_rate=0.80
        ))
        iron_legion.uniqueness.append(ProviderUniqueness(
            feature="KAIJU NAS Integration",
            description="Deeply integrated with KAIJU NAS infrastructure for centralized management",
            uniqueness_score=0.9,
            comparison={
                "Cloud Providers": "No data leaves NAS, complete control",
                "Local Only": "Can leverage NAS resources and storage"
            }
        ))
        iron_legion.uniqueness.append(ProviderUniqueness(
            feature="Self-Healing Cluster",
            description="Automatic monitoring and self-healing capabilities",
            uniqueness_score=0.85,
            comparison={"Other Providers": "Built-in resilience and recovery"}
        ))
        self.providers[ProviderType.IRON_LEGION] = iron_legion

        # OpenAI
        openai = CloudAIProvider(
            provider_type=ProviderType.OPENAI,
            name="OpenAI",
            description="OpenAI's GPT models - versatile, widely used",
            models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"]
        )
        openai.power_level = ProviderPowerLevel(
            level=9,  # Very high power
            description="Very high-performance models suitable for complex tasks",
            suitable_for=["code_generation", "reasoning", "analysis", "creative", "multi_modal"]
        )
        openai.cost = ProviderCost(
            cost_per_1k_tokens_input=0.03,  # Approximate GPT-4 pricing
            cost_per_1k_tokens_output=0.06,
            cost_per_request=0.0,
            is_free=False,
            cost_category="high"
        )
        openai.traits.append(ProviderTrait(
            name="Versatility",
            description="Strong across many task types",
            category="capability",
            strength=0.9
        ))
        openai.specialties.append(ProviderSpecialty(
            area="Code Generation",
            description="Excellent at generating code in multiple languages",
            confidence=0.9,
            success_rate=0.85
        ))
        self.providers[ProviderType.OPENAI] = openai

        # Anthropic
        anthropic = CloudAIProvider(
            provider_type=ProviderType.ANTHROPIC,
            name="Anthropic",
            description="Claude models - strong reasoning and safety",
            models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"]
        )
        anthropic.power_level = ProviderPowerLevel(
            level=10,  # Maximum power for complex reasoning
            description="Maximum performance models suitable for the most complex reasoning tasks",
            suitable_for=["reasoning", "code_review", "analysis", "complex_problem_solving"]
        )
        anthropic.cost = ProviderCost(
            cost_per_1k_tokens_input=0.015,  # Approximate Claude 3.5 Sonnet pricing
            cost_per_1k_tokens_output=0.075,
            cost_per_request=0.0,
            is_free=False,
            cost_category="high"
        )
        anthropic.traits.append(ProviderTrait(
            name="Reasoning",
            description="Strong analytical and reasoning capabilities",
            category="capability",
            strength=0.95
        ))
        anthropic.specialties.append(ProviderSpecialty(
            area="Code Review",
            description="Excellent at reviewing and analyzing code",
            confidence=0.95,
            success_rate=0.90
        ))
        anthropic.uniqueness.append(ProviderUniqueness(
            feature="Constitutional AI",
            description="Built with safety and helpfulness principles",
            uniqueness_score=0.9,
            comparison={"OpenAI": "More explicit safety training"}
        ))
        self.providers[ProviderType.ANTHROPIC] = anthropic

        # Azure OpenAI
        azure_openai = CloudAIProvider(
            provider_type=ProviderType.AZURE_OPENAI,
            name="Azure OpenAI",
            description="OpenAI models via Azure - enterprise integration",
            models=["gpt-4", "gpt-4-turbo", "gpt-35-turbo"]
        )
        azure_openai.power_level = ProviderPowerLevel(
            level=9,  # Very high power (same as OpenAI)
            description="Very high-performance models with enterprise integration",
            suitable_for=["code_generation", "reasoning", "analysis", "enterprise_workloads"]
        )
        azure_openai.cost = ProviderCost(
            cost_per_1k_tokens_input=0.03,  # Similar to OpenAI
            cost_per_1k_tokens_output=0.06,
            cost_per_request=0.0,
            is_free=False,
            cost_category="high"
        )
        azure_openai.traits.append(ProviderTrait(
            name="Enterprise Integration",
            description="Deep Azure ecosystem integration",
            category="capability",
            strength=0.95
        ))
        azure_openai.specialties.append(ProviderSpecialty(
            area="Enterprise Workloads",
            description="Optimized for enterprise-scale deployments",
            confidence=0.9,
            success_rate=0.88
        ))
        self.providers[ProviderType.AZURE_OPENAI] = azure_openai

        # Google
        google = CloudAIProvider(
            provider_type=ProviderType.GOOGLE,
            name="Google",
            description="Google's Gemini models - multi-modal strength",
            models=["gemini-pro", "gemini-ultra", "gemini-1.5-pro"]
        )
        google.power_level = ProviderPowerLevel(
            level=8,  # High power for multi-modal
            description="High-performance models with strong multi-modal capabilities",
            suitable_for=["multi_modal", "code_generation", "analysis", "creative"]
        )
        google.cost = ProviderCost(
            cost_per_1k_tokens_input=0.0005,  # Approximate Gemini pricing (very low)
            cost_per_1k_tokens_output=0.0015,
            cost_per_request=0.0,
            is_free=False,
            cost_category="low"
        )
        google.traits.append(ProviderTrait(
            name="Multi-modal",
            description="Strong multi-modal capabilities (text, image, video)",
            category="capability",
            strength=0.9
        ))
        google.specialties.append(ProviderSpecialty(
            area="Multi-modal Tasks",
            description="Excellent at tasks requiring multiple modalities",
            confidence=0.9,
            success_rate=0.85
        ))
        self.providers[ProviderType.GOOGLE] = google

        self._save_providers()
        logger.info(f"✅ Initialized {len(self.providers)} default providers")

    def add_trait(
        self,
        provider_type: ProviderType,
        trait: ProviderTrait
    ) -> bool:
        """Add a trait to a provider"""
        if provider_type not in self.providers:
            logger.warning(f"⚠️  Provider {provider_type.value} not found")
            return False

        provider = self.providers[provider_type]

        # Check if trait already exists
        existing = next((t for t in provider.traits if t.name == trait.name), None)
        if existing:
            # Update existing trait
            existing.description = trait.description
            existing.category = trait.category
            existing.strength = trait.strength
            existing.evidence.extend(trait.evidence)
            logger.info(f"   📝 Updated trait: {trait.name}")
        else:
            provider.traits.append(trait)
            logger.info(f"   ➕ Added trait: {trait.name}")

        provider.updated_at = datetime.now()
        self._save_providers()
        return True

    def add_specialty(
        self,
        provider_type: ProviderType,
        specialty: ProviderSpecialty
    ) -> bool:
        """Add a specialty to a provider"""
        if provider_type not in self.providers:
            logger.warning(f"⚠️  Provider {provider_type.value} not found")
            return False

        provider = self.providers[provider_type]

        # Check if specialty already exists
        existing = next((s for s in provider.specialties if s.area == specialty.area), None)
        if existing:
            # Update existing specialty
            existing.description = specialty.description
            existing.confidence = specialty.confidence
            existing.success_rate = specialty.success_rate
            existing.examples.extend(specialty.examples)
            logger.info(f"   📝 Updated specialty: {specialty.area}")
        else:
            provider.specialties.append(specialty)
            logger.info(f"   ➕ Added specialty: {specialty.area}")

        provider.updated_at = datetime.now()
        self._save_providers()
        return True

    def add_uniqueness(
        self,
        provider_type: ProviderType,
        uniqueness: ProviderUniqueness
    ) -> bool:
        """Add a uniqueness feature to a provider"""
        if provider_type not in self.providers:
            logger.warning(f"⚠️  Provider {provider_type.value} not found")
            return False

        provider = self.providers[provider_type]

        # Check if uniqueness already exists
        existing = next((u for u in provider.uniqueness if u.feature == uniqueness.feature), None)
        if existing:
            # Update existing uniqueness
            existing.description = uniqueness.description
            existing.uniqueness_score = uniqueness.uniqueness_score
            existing.comparison.update(uniqueness.comparison)
            logger.info(f"   📝 Updated uniqueness: {uniqueness.feature}")
        else:
            provider.uniqueness.append(uniqueness)
            logger.info(f"   ➕ Added uniqueness: {uniqueness.feature}")

        provider.updated_at = datetime.now()
        self._save_providers()
        return True

    def capture_provider_spark(
        self,
        provider_type: ProviderType,
        content: str,
        source: str = "unknown",
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[ProviderSpark]:
        """Capture a @spark (insight) about a provider"""
        if provider_type not in self.providers:
            logger.warning(f"⚠️  Provider {provider_type.value} not found")
            return None

        provider = self.providers[provider_type]

        # Create spark
        spark = ProviderSpark(
            spark_id=f"spark_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            content=content,
            timestamp=datetime.now(),
            source=source,
            context=context or {}
        )

        provider.sparks.append(spark)
        provider.updated_at = datetime.now()

        logger.info(f"💡 Captured @spark for {provider.name}: {content[:80]}...")

        # Also capture in insights/sparks system
        if self.sparks_system:
            try:
                self.sparks_system.capture_spark(
                    content=f"[{provider.name}] {content}",
                    source=source,
                    context={
                        "provider": provider_type.value,
                        "provider_name": provider.name,
                        **(context or {})
                    },
                    tags=["cloud_ai", "provider", provider_type.value]
                )
                spark.impact_score = 1.0  # Will be calculated by sparks system
            except Exception as e:
                logger.warning(f"⚠️  Error capturing spark in insights system: {e}")

        self._save_providers()
        return spark

    def record_job_performance(
        self,
        provider_type: ProviderType,
        task_category: TaskCategory,
        success: bool,
        quality_score: float = 0.0,
        time_taken: float = 0.0,
        cost: float = 0.0
    ) -> bool:
        """Record job performance for learning"""
        if provider_type not in self.providers:
            logger.warning(f"⚠️  Provider {provider_type.value} not found")
            return False

        provider = self.providers[provider_type]

        # Get or create job performance record
        if task_category not in provider.job_performance:
            provider.job_performance[task_category] = JobPerformance(
                task_category=task_category,
                provider=provider_type
            )

        perf = provider.job_performance[task_category]

        # Update performance
        if success:
            perf.success_count += 1
        else:
            perf.failure_count += 1

        perf.total_time += time_taken
        perf.quality_score = (perf.quality_score * (perf.success_count + perf.failure_count - 1) + quality_score) / (perf.success_count + perf.failure_count)
        perf.cost_per_job = (perf.cost_per_job * (perf.success_count + perf.failure_count - 1) + cost) / (perf.success_count + perf.failure_count)
        perf.last_updated = datetime.now()

        provider.updated_at = datetime.now()
        self._save_providers()

        logger.debug(f"   📊 Recorded performance: {provider.name} - {task_category.value} - {'✅' if success else '❌'}")
        return True

    def get_best_provider_for_job(
        self,
        task_category: TaskCategory,
        min_confidence: float = 0.7,
        use_least_powerful: bool = True,
        prioritize_cost: bool = True
    ) -> Optional[ProviderType]:
        """
        Get the best provider for a specific job type

        MEASURE TWICE, CUT ONCE:
        - Analyzes all providers that can handle the task
        - Selects LEAST POWERFUL sufficient provider
        - Prioritizes LOWEST COST
        - Uses learned performance to ensure quality

        Args:
            task_category: Task category
            min_confidence: Minimum confidence threshold
            use_least_powerful: If True, prefer least powerful sufficient provider
            prioritize_cost: If True, prioritize lowest cost

        Returns:
            Best provider based on intelligent selection
        """
        # Step 1: MEASURE TWICE - Analyze all providers that can handle this task
        suitable_providers = []

        for provider_type, provider in self.providers.items():
            # Check if provider has performance data for this task
            has_performance = task_category in provider.job_performance
            perf = provider.job_performance.get(task_category)

            # Check if provider's power level is suitable for this task
            is_suitable = False
            if provider.power_level:
                task_str = task_category.value
                is_suitable = (
                    task_str in provider.power_level.suitable_for or
                    has_performance  # If we have performance data, assume suitable
                )
            else:
                # If no power level defined, assume suitable if we have performance data
                is_suitable = has_performance

            if not is_suitable:
                continue

            # Calculate score
            if perf:
                score = perf.overall_score
            else:
                # No performance data - use specialty confidence if available
                specialty = next(
                    (s for s in provider.specialties if s.area.lower() == task_category.value.lower()),
                    None
                )
                score = specialty.confidence if specialty else 0.5

            if score < min_confidence:
                continue

            # Calculate cost score (lower is better)
            cost_score = 0.0
            if provider.cost:
                if provider.cost.is_free:
                    cost_score = 0.0  # Free is best
                else:
                    # Normalize cost (lower cost = higher score)
                    total_cost = provider.cost.cost_per_1k_tokens_input + provider.cost.cost_per_1k_tokens_output
                    cost_score = 1.0 / (1.0 + total_cost * 100)  # Normalize to 0-1

            suitable_providers.append({
                "provider_type": provider_type,
                "provider": provider,
                "performance_score": score,
                "power_level": provider.power_level.level if provider.power_level else 10,
                "cost_score": cost_score,
                "is_free": provider.cost.is_free if provider.cost else False,
                "cost": provider.cost
            })

        if not suitable_providers:
            logger.warning(f"   ⚠️  No suitable providers found for {task_category.value}")
            return None

        # Step 2: CUT ONCE - Select best provider using intelligent logic

        # Sort by: 1) Free providers first, 2) Least powerful sufficient, 3) Lowest cost, 4) Best performance
        suitable_providers.sort(key=lambda x: (
            not x["is_free"],  # Free first (False sorts before True)
            x["power_level"] if use_least_powerful else 0,  # Least powerful first
            -x["cost_score"] if prioritize_cost else 0,  # Highest cost score (lowest cost) first
            -x["performance_score"]  # Best performance first
        ))

        best = suitable_providers[0]
        best_provider_type = best["provider_type"]
        best_provider = best["provider"]

        logger.info("=" * 80)
        logger.info(f"   🎯 BEST TOOL FOR THE JOB: {task_category.value}")
        logger.info(f"   📊 Selected: {best_provider.name}")
        logger.info(f"   ⚡ Power Level: {best['power_level']}/10 (least powerful sufficient)")
        logger.info(f"   💰 Cost: {'FREE' if best['is_free'] else f'${best_provider.cost.cost_per_1k_tokens_input + best_provider.cost.cost_per_1k_tokens_output:.4f}/1K tokens'}")
        logger.info(f"   📈 Performance Score: {best['performance_score']:.2f}")
        logger.info("=" * 80)

        return best_provider_type

    def get_provider_recommendations(
        self,
        task_category: TaskCategory,
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """Get top N provider recommendations for a task category"""
        recommendations = []

        for provider_type, provider in self.providers.items():
            if task_category not in provider.job_performance:
                continue

            perf = provider.job_performance[task_category]
            score = perf.overall_score

            recommendations.append({
                "provider": provider_type,
                "provider_name": provider.name,
                "score": score,
                "success_rate": perf.success_rate,
                "quality_score": perf.quality_score,
                "average_time": perf.average_time,
                "cost_per_job": perf.cost_per_job
            })

        # Sort by score descending
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        return recommendations[:top_n]

    def get_provider(self, provider_type: ProviderType) -> Optional[CloudAIProvider]:
        """Get a provider by type"""
        return self.providers.get(provider_type)

    def list_providers(self) -> List[ProviderType]:
        """List all tracked providers"""
        return list(self.providers.keys())


# Global instance
_global_tracker = None

def get_provider_tracker() -> CloudAIProviderTracker:
    """Get global Cloud AI Provider Tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CloudAIProviderTracker()
    return _global_tracker


if __name__ == "__main__":
    # Demo
    tracker = CloudAIProviderTracker()

    # Capture a spark
    tracker.capture_provider_spark(
        ProviderType.ANTHROPIC,
        "Claude excels at code review tasks with detailed explanations",
        source="user_observation",
        context={"task": "code_review", "quality": "high"}
    )

    # Record job performance
    tracker.record_job_performance(
        ProviderType.ANTHROPIC,
        TaskCategory.CODE_REVIEW,
        success=True,
        quality_score=0.95,
        time_taken=45.0,
        cost=0.05
    )

    # Get best provider for a job
    best = tracker.get_best_provider_for_job(TaskCategory.CODE_REVIEW)
    if best:
        print(f"\n✅ Best provider for code review: {best.value}")

    # Get recommendations
    recs = tracker.get_provider_recommendations(TaskCategory.CODE_GENERATION, top_n=3)
    print(f"\n📊 Top recommendations for code generation:")
    for rec in recs:
        print(f"   {rec['provider_name']}: {rec['score']:.2f} (success: {rec['success_rate']:.2f})")
