#!/usr/bin/env python3
"""
Three-Tier AI Architecture System for LUMINA Ecosystem

Features:
- Local AI Tier (PASS-THROUGH TO LOCALHOST GPU)
- Free AI Tier (Cloud-based, limited)
- Premium AI Tier (High-performance, paid)
- Automatic tier selection based on system capabilities
- Model recommendation and routing system
- Token management and quota tracking

Tags: #AI_ARCHITECTURE #THREE_TIER #LOCAL_AI #FREE_AI #PREMIUM_AI
      @JARVIS @LUMINA @ULTRON @KAIJU
"""

import os
import sys
import json
import time
import logging
import subprocess
import platform
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum, auto

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    from github_ai_provider import GitHubAIProvider
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    GitHubAIProvider = None

logger = get_logger("ThreeTierAISystem")

# Define AI Tiers with Governance Roles
class AITier(Enum):
    """AI Service Tiers with Governance Hierarchy"""
    LOCAL = auto()    # Entry Level: Worker/Implementation tier (unlimited, fast, local)
    FREE = auto()     # Middle Management: Oversight/Coordination tier (limited, balanced)
    PREMIUM = auto()  # Senior Management: Strategic/Decision tier (expensive, authoritative)

    def governance_role(self) -> str:
        """Get the governance role for this tier"""
        roles = {
            AITier.LOCAL: "Entry Level - Implementation & Execution",
            AITier.FREE: "Middle Management - Oversight & Coordination",
            AITier.PREMIUM: "Senior Management - Strategic Decisions & Consensus"
        }
        return roles[self]

    def decision_authority(self) -> str:
        """Get decision-making authority level"""
        authorities = {
            AITier.LOCAL: "Implementation authority - Can execute approved tasks",
            AITier.FREE: "Oversight authority - Can coordinate and monitor progress",
            AITier.PREMIUM: "Executive authority - Can approve/reject major initiatives"
        }
        return authorities[self]

    def consensus_required(self) -> bool:
        """Whether this tier requires consensus for major decisions"""
        return self in [AITier.FREE, AITier.PREMIUM]

@dataclass
class AIModel:
    """AI Model Configuration"""
    name: str
    tier: AITier
    model_id: str
    description: str
    max_tokens: int
    performance_score: float
    cost_per_token: float = 0.0
    requires_gpu: bool = False
    memory_requirements_gb: float = 1.0
    local_only: bool = False
    api_endpoint: Optional[str] = None
    provider: str = "local"

@dataclass
class AIService:
    """AI Service Configuration"""
    service_name: str
    tier: AITier
    models: List[AIModel]
    quota_tokens: int = 0
    used_tokens: int = 0
    last_reset: datetime = field(default_factory=datetime.now)
    rate_limit_per_minute: int = 60
    current_requests: int = 0

@dataclass
class UserQuota:
    """User Quota Tracking"""
    user_id: str
    tier_quotas: Dict[AITier, int] = field(default_factory=dict)
    tier_usage: Dict[AITier, int] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    preferred_tier: Optional[AITier] = None

@dataclass
class AIRequest:
    """AI Request Information"""
    request_id: str
    user_id: str
    tier: AITier
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
    success: bool = False
    error_message: Optional[str] = None

@dataclass
class GovernanceDecision:
    """Governance decision requiring consensus"""
    decision_id: str
    title: str
    description: str
    required_consensus_tier: AITier
    decision_type: str  # "proceed", "halt", "modify", "escalate"
    stakeholders: List[str]
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    votes: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # tier -> {decision, reasoning, confidence}
    consensus_reached: bool = False

@dataclass
class ConsensusVote:
    """Individual vote in consensus decision"""
    voter_id: str
    voter_tier: AITier
    decision: str  # "approve", "deny", "modify", "escalate"
    reasoning: str
    confidence_score: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemCapabilities:
    """System Hardware Capabilities"""
    cpu_cores: int
    total_memory_gb: float
    available_memory_gb: float
    gpu_available: bool
    gpu_name: Optional[str] = None
    gpu_memory_gb: Optional[float] = None
    gpu_utilization: Optional[float] = None
    network_available: bool = True

class ThreeTierAISystem:
    """Three-Tier AI Architecture System"""

    def __init__(self):
        """Initialize Three-Tier AI System with Governance"""
        self.logger = logger
        self.models = self._initialize_models()
        self.services = self._initialize_services()
        self.users = self._load_user_quotas()
        self.system_caps = self._detect_system_capabilities()
        self.token_pool = self._initialize_token_pool()

        # Initialize AI providers
        self.providers = self._initialize_providers()

        # Governance system
        self.active_decisions: Dict[str, GovernanceDecision] = {}
        self.decision_history: List[GovernanceDecision] = []
        self.governance_config = self._initialize_governance_config()

        self.logger.info("Three-Tier AI Governance System initialized")
        self.logger.info(f"System capabilities: {self.system_caps}")
        self.logger.info(f"Available models: {len(self.models)}")
        self.logger.info(f"Available services: {len(self.services)}")
        self.logger.info(f"Available providers: {len(self.providers)}")
        self.logger.info("🤖 AI Governance Hierarchy Established:")
        for tier in AITier:
            self.logger.info(f"   {tier.name}: {tier.governance_role()}")
            self.logger.info(f"      Authority: {tier.decision_authority()}")
            self.logger.info(f"      Consensus Required: {tier.consensus_required()}")
        self.logger.info(f"Active governance decisions: {len(self.active_decisions)}")

    def _initialize_models(self) -> List[AIModel]:
        """Initialize AI models for all tiers"""
        models = []

        # LOCAL TIER MODELS (CPU-only)
        models.extend([
            AIModel(
                name="ULTRON Local",
                tier=AITier.LOCAL,
                model_id="qwen2.5-coder:1.5b",
                description="Local CPU-only model (1.5B parameters)",
                max_tokens=4096,
                performance_score=6.0,
                cost_per_token=0.0,
                requires_gpu=False,
                memory_requirements_gb=2.0,
                local_only=True,
                provider="ollama"
            ),
            AIModel(
                name="KAIJU Local",
                tier=AITier.LOCAL,
                model_id="llama3.2:1b",
                description="Lightweight local model (1B parameters)",
                max_tokens=2048,
                performance_score=5.5,
                cost_per_token=0.0,
                requires_gpu=False,
                memory_requirements_gb=1.5,
                local_only=True,
                provider="ollama"
            )
        ])

        # FREE TIER MODELS (Cloud-based, limited)
        models.extend([
            AIModel(
                name="ULTRON Free",
                tier=AITier.FREE,
                model_id="qwen2.5-coder:7b",
                description="Free cloud model (7B parameters, limited quota)",
                max_tokens=8192,
                performance_score=8.0,
                cost_per_token=0.000001,  # Very low cost
                requires_gpu=True,
                memory_requirements_gb=8.0,
                local_only=False,
                api_endpoint="https://api.free-ai.example.com/v1",
                provider="free-ai"
            ),
            AIModel(
                name="Mistral Free",
                tier=AITier.FREE,
                model_id="mistral:7b",
                description="Free Mistral model (7B parameters)",
                max_tokens=4096,
                performance_score=7.5,
                cost_per_token=0.0000008,
                requires_gpu=True,
                memory_requirements_gb=7.0,
                local_only=False,
                api_endpoint="https://api.free-ai.example.com/v1",
                provider="free-ai"
            )
        ])

        # FREE TIER MODELS (Cloud-based, limited) - Add GitHub Models
        models.extend([
            AIModel(
                name="GitHub GPT-4o Mini",
                tier=AITier.FREE,
                model_id="openai/gpt-4o-mini",
                description="GitHub Models: GPT-4o Mini (128K context, fast)",
                max_tokens=16384,
                performance_score=8.8,
                cost_per_token=0.00015,
                requires_gpu=False,
                memory_requirements_gb=0.1,
                local_only=False,
                api_endpoint="https://models.github.ai",
                provider="github"
            ),
            AIModel(
                name="GitHub Claude 3 Haiku",
                tier=AITier.FREE,
                model_id="anthropic/claude-3-haiku",
                description="GitHub Models: Claude 3 Haiku (fast, efficient)",
                max_tokens=4096,
                performance_score=8.5,
                cost_per_token=0.00025,
                requires_gpu=False,
                memory_requirements_gb=0.1,
                local_only=False,
                api_endpoint="https://models.github.ai",
                provider="github"
            )
        ])

        # PREMIUM TIER MODELS (High-performance)
        models.extend([
            AIModel(
                name="ULTRON Premium",
                tier=AITier.PREMIUM,
                model_id="qwen2.5-coder:72b",
                description="Premium model (72B parameters, high performance)",
                max_tokens=32768,
                performance_score=9.5,
                cost_per_token=0.000015,
                requires_gpu=True,
                memory_requirements_gb=80.0,
                local_only=False,
                api_endpoint="https://api.premium-ai.example.com/v1",
                provider="premium-ai"
            ),
            AIModel(
                name="GitHub GPT-4o",
                tier=AITier.PREMIUM,
                model_id="openai/gpt-4o",
                description="GitHub Models: GPT-4o (128K context, high performance)",
                max_tokens=16384,
                performance_score=9.7,
                cost_per_token=0.003,
                requires_gpu=False,
                memory_requirements_gb=0.1,
                local_only=False,
                api_endpoint="https://models.github.ai",
                provider="github"
            ),
            AIModel(
                name="GitHub Claude 3.5 Sonnet",
                tier=AITier.PREMIUM,
                model_id="anthropic/claude-3-5-sonnet",
                description="GitHub Models: Claude 3.5 Sonnet (state-of-the-art reasoning)",
                max_tokens=8192,
                performance_score=9.8,
                cost_per_token=0.015,
                requires_gpu=False,
                memory_requirements_gb=0.1,
                local_only=False,
                api_endpoint="https://models.github.ai",
                provider="github"
            ),
            AIModel(
                name="GPT-4 Premium",
                tier=AITier.PREMIUM,
                model_id="gpt-4-turbo",
                description="GPT-4 Turbo (128K context, state-of-the-art)",
                max_tokens=131072,
                performance_score=9.8,
                cost_per_token=0.000030,
                requires_gpu=True,
                memory_requirements_gb=100.0,
                local_only=False,
                api_endpoint="https://api.premium-ai.example.com/v1",
                provider="openai"
            ),
            AIModel(
                name="Claude Premium",
                tier=AITier.PREMIUM,
                model_id="claude-3-opus",
                description="Claude 3 Opus (200K context, enterprise-grade)",
                max_tokens=200000,
                performance_score=9.7,
                cost_per_token=0.000025,
                requires_gpu=True,
                memory_requirements_gb=90.0,
                local_only=False,
                api_endpoint="https://api.premium-ai.example.com/v1",
                provider="anthropic"
            )
        ])

        return models

    def _initialize_services(self) -> List[AIService]:
        """Initialize AI services for each tier"""
        services = []

        # Local AI Service
        local_models = [model for model in self.models if model.tier == AITier.LOCAL]
        services.append(AIService(
            service_name="LocalAI",
            tier=AITier.LOCAL,
            models=local_models,
            quota_tokens=0,  # Unlimited for local
            rate_limit_per_minute=120
        ))

        # Free AI Service
        free_models = [model for model in self.models if model.tier == AITier.FREE]
        services.append(AIService(
            service_name="FreeAI",
            tier=AITier.FREE,
            models=free_models,
            quota_tokens=100000,  # 100K tokens/month
            rate_limit_per_minute=30
        ))

        # Premium AI Service
        premium_models = [model for model in self.models if model.tier == AITier.PREMIUM]
        services.append(AIService(
            service_name="PremiumAI",
            tier=AITier.PREMIUM,
            models=premium_models,
            quota_tokens=1000000,  # 1M tokens/month
            rate_limit_per_minute=60
        ))

        return services

    def _load_user_quotas(self) -> Dict[str, UserQuota]:
        """Load user quotas from file or initialize defaults"""
        users = {}

        # Default admin user with full access
        users["admin"] = UserQuota(
            user_id="admin",
            tier_quotas={
                AITier.LOCAL: 0,      # Unlimited
                AITier.FREE: 50000,   # 50K tokens
                AITier.PREMIUM: 10000 # 10K tokens
            },
            preferred_tier=AITier.PREMIUM
        )

        # Default user with basic access
        users["default"] = UserQuota(
            user_id="default",
            tier_quotas={
                AITier.LOCAL: 0,      # Unlimited
                AITier.FREE: 10000,   # 10K tokens
                AITier.PREMIUM: 1000  # 1K tokens
            },
            preferred_tier=AITier.FREE
        )

        return users

    def _detect_system_capabilities(self) -> SystemCapabilities:
        """Detect system hardware capabilities"""
        try:
            # CPU info
            cpu_cores = psutil.cpu_count(logical=True) or 1

            # Memory info
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024 ** 3)
            available_memory_gb = memory.available / (1024 ** 3)

            # GPU info
            gpu_available = False
            gpu_name = None
            gpu_memory_gb = None
            gpu_utilization = None

            try:
                # Try to detect GPU using nvidia-smi
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,utilization.gpu',
                                        '--format=csv,noheader'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        parts = [p.strip() for p in lines[0].split(',')]
                        if len(parts) >= 3:
                            gpu_available = True
                            gpu_name = parts[0]
                            gpu_memory_gb = float(parts[1].split()[0]) / 1024
                            gpu_utilization = float(parts[2].split()[0])
            except Exception:
                pass

            # Network check
            network_available = True
            try:
                subprocess.run(['ping', '-c', '1', '8.8.8.8'],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL,
                              timeout=5)
            except Exception:
                network_available = False

            return SystemCapabilities(
                cpu_cores=cpu_cores,
                total_memory_gb=total_memory_gb,
                available_memory_gb=available_memory_gb,
                gpu_available=gpu_available,
                gpu_name=gpu_name,
                gpu_memory_gb=gpu_memory_gb,
                gpu_utilization=gpu_utilization,
                network_available=network_available
            )
        except Exception as e:
            self.logger.error(f"Failed to detect system capabilities: {e}")
            return SystemCapabilities(
                cpu_cores=1,
                total_memory_gb=8.0,
                available_memory_gb=4.0,
                gpu_available=False,
                network_available=True
            )

    def _initialize_token_pool(self) -> Dict[str, Any]:
        """Initialize token pool management"""
        return {
            'total_tokens': 1000000,
            'used_tokens': 0,
            'last_reset': datetime.now().strftime("%Y-%m-%d"),
            'emergency_mode': True,  # Due to token pool at 99% capacity
            'local_only': True       # Force local-only mode
        }

    def _initialize_providers(self) -> Dict[str, Any]:
        """Initialize AI providers"""
        providers = {}

        # GitHub AI Provider
        if GitHubAIProvider:
            try:
                providers['github'] = GitHubAIProvider(project_root=self.project_root)
                self.logger.info("✅ GitHub AI Provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize GitHub AI Provider: {e}")
                providers['github'] = None
        else:
            self.logger.warning("⚠️  GitHub AI Provider not available")
            providers['github'] = None

        # Add other providers here as needed
        # providers['openai'] = ...
        # providers['anthropic'] = ...

        return providers

    def _initialize_governance_config(self) -> Dict[str, Any]:
        """Initialize governance configuration with clear tier roles"""
        return {
            "tier_hierarchy": {
                AITier.LOCAL: {
                    "level": "Entry Level - Implementation & Execution",
                    "authority": "Can execute approved tasks and routine operations",
                    "consensus_required": False,
                    "escalation_threshold": "task_failure_3_attempts",
                    "decision_power": "Implementation authority only"
                },
                AITier.FREE: {
                    "level": "Middle Management - Oversight & Coordination",
                    "authority": "Can coordinate multiple systems and oversee progress",
                    "consensus_required": True,
                    "escalation_threshold": "complex_decision_required",
                    "decision_power": "Oversight and coordination authority"
                },
                AITier.PREMIUM: {
                    "level": "Senior Management - Strategic & Executive",
                    "authority": "Can approve/reject major initiatives and strategic decisions",
                    "consensus_required": True,
                    "escalation_threshold": "never_auto_escalate",
                    "decision_power": "Executive authority with veto power"
                }
            },
            "consensus_thresholds": {
                AITier.FREE: 0.7,      # 70% agreement required for middle management
                AITier.PREMIUM: 0.8    # 80% agreement required for senior management
            },
            "escalation_rules": {
                "max_local_attempts": 3,
                "auto_escalate_on_failure": True,
                "consensus_timeout_hours": 24,
                "emergency_bypass_threshold": 0.9  # 90% confidence bypass
            },
            "decision_categories": {
                "routine": AITier.LOCAL,      # Simple tasks, code generation
                "oversight": AITier.FREE,     # Complex coordination, multi-system tasks
                "strategic": AITier.PREMIUM, # Major decisions, architecture changes
                "emergency": AITier.PREMIUM, # Crisis situations, immediate action
                "consensus_required": AITier.PREMIUM,  # Any decision needing multiple AI agreement
                "halt_proceed_decision": AITier.PREMIUM  # Whether to proceed or halt initiatives
            },
            "governance_levels": {
                "micro": "Individual task decisions within a project",
                "macro": "Project-level or initiative-level decisions",
                "enterprise": "Organization-wide strategic decisions"
            }
        }

    def select_optimal_tier(self, user_id: str = "default") -> AITier:
        """
        Select the optimal AI tier based on:
        - User preferences and quotas
        - System capabilities
        - Current token pool status
        - Service availability
        """
        user = self.users.get(user_id, self.users["default"])

        # Check token pool status
        if self.token_pool['emergency_mode']:
            self.logger.warning("Token pool in emergency mode - forcing LOCAL tier")
            return AITier.LOCAL

        # Check system capabilities for premium tier
        premium_available = (
            self.system_caps.gpu_available and
            self.system_caps.available_memory_gb >= 16 and
            self.system_caps.network_available
        )

        # Check user preferences and quotas
        preferred_tier = user.preferred_tier

        if preferred_tier == AITier.PREMIUM and premium_available:
            # Check if user has premium quota
            if user.tier_quotas.get(AITier.PREMIUM, 0) > user.tier_usage.get(AITier.PREMIUM, 0):
                return AITier.PREMIUM

        if preferred_tier == AITier.FREE or (preferred_tier == AITier.PREMIUM and not premium_available):
            # Check if user has free quota
            if user.tier_quotas.get(AITier.FREE, 0) > user.tier_usage.get(AITier.FREE, 0):
                return AITier.FREE

        # Default to local tier
        return AITier.LOCAL

    def get_available_models(self, tier: AITier) -> List[AIModel]:
        """Get available models for a specific tier"""
        return [model for model in self.models if model.tier == tier]

    def select_best_model(self, tier: AITier, task_type: str = "general") -> AIModel:
        """
        Select the best model for a given tier and task type

        Args:
            tier: AI tier to select from
            task_type: Type of task (general, coding, analysis, etc.)
        """
        available_models = self.get_available_models(tier)

        if not available_models:
            raise ValueError(f"No models available for tier: {tier.name}")

        # Simple selection: choose model with highest performance score
        best_model = max(available_models, key=lambda x: x.performance_score)

        self.logger.info(f"Selected model: {best_model.name} ({tier.name} tier) for {task_type} task")
        return best_model

    def check_quota(self, user_id: str, tier: AITier, tokens: int) -> bool:
        """
        Check if user has sufficient quota for the requested operation

        Args:
            user_id: User identifier
            tier: AI tier
            tokens: Number of tokens required

        Returns:
            True if quota available, False otherwise
        """
        user = self.users.get(user_id, self.users["default"])

        # Local tier has unlimited quota
        if tier == AITier.LOCAL:
            return True

        current_usage = user.tier_usage.get(tier, 0)
        quota_limit = user.tier_quotas.get(tier, 0)

        if current_usage + tokens > quota_limit:
            self.logger.warning(f"Quota exceeded for user {user_id} on tier {tier.name}")
            return False

        return True

    def update_quota(self, user_id: str, tier: AITier, tokens: int):
        """
        Update user quota after token usage

        Args:
            user_id: User identifier
            tier: AI tier
            tokens: Number of tokens used
        """
        user = self.users.get(user_id, self.users["default"])

        # Update user usage
        user.tier_usage[tier] = user.tier_usage.get(tier, 0) + tokens
        user.last_activity = datetime.now()

        # Update global token pool
        if tier != AITier.LOCAL:  # Don't count local tokens
            self.token_pool['used_tokens'] += tokens

        self.logger.info(f"Updated quota for {user_id}: {tier.name} +{tokens} tokens")

    def get_model_recommendation(self, task_type: str = "general") -> Dict[str, Any]:
        """
        Get model recommendation based on current system state

        Args:
            task_type: Type of task

        Returns:
            Dictionary with recommendation details
        """
        optimal_tier = self.select_optimal_tier()
        best_model = self.select_best_model(optimal_tier, task_type)

        # Get system recommendations
        recommendations = {
            'optimal_tier': optimal_tier.name,
            'recommended_model': best_model.name,
            'model_id': best_model.model_id,
            'performance_score': best_model.performance_score,
            'max_tokens': best_model.max_tokens,
            'reason': f"Selected based on system capabilities and current token pool status",
            'system_status': {
                'emergency_mode': self.token_pool['emergency_mode'],
                'local_only': self.token_pool['local_only'],
                'gpu_available': self.system_caps.gpu_available,
                'available_memory_gb': self.system_caps.available_memory_gb
            },
            'alternatives': []
        }

        # Add alternative recommendations
        if optimal_tier != AITier.PREMIUM and self.system_caps.gpu_available:
            premium_model = self.select_best_model(AITier.PREMIUM, task_type)
            recommendations['alternatives'].append({
                'tier': AITier.PREMIUM.name,
                'model': premium_model.name,
                'reason': "Higher performance available with GPU acceleration"
            })

        if optimal_tier == AITier.LOCAL and self.system_caps.network_available:
            free_model = self.select_best_model(AITier.FREE, task_type)
            recommendations['alternatives'].append({
                'tier': AITier.FREE.name,
                'model': free_model.name,
                'reason': "Cloud-based model available when quota allows"
            })

        return recommendations

    def get_tier_statistics(self) -> Dict[str, Any]:
        """Get statistics for all tiers"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system_capabilities': asdict(self.system_caps),
            'token_pool': self.token_pool,
            'tiers': {}
        }

        for tier in [AITier.LOCAL, AITier.FREE, AITier.PREMIUM]:
            models = self.get_available_models(tier)
            service = next((s for s in self.services if s.tier == tier), None)

            stats['tiers'][tier.name] = {
                'available_models': [model.name for model in models],
                'model_count': len(models),
                'service_available': bool(service),
                'quota_available': not self.token_pool['emergency_mode'] if tier != AITier.LOCAL else True,
                'recommended_for': self._get_tier_recommendation(tier)
            }

        return stats

    def _get_tier_recommendation(self, tier: AITier) -> str:
        """Get recommendation for when to use a specific tier"""
        if tier == AITier.LOCAL:
            return "Emergency mode, offline operation, or when privacy is critical"
        elif tier == AITier.FREE:
            return "General use cases with moderate performance requirements"
        else:
            return "High-performance tasks requiring large context or complex reasoning"

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive report of AI system status"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': asdict(self.system_caps),
            'token_pool_status': self.token_pool,
            'tier_statistics': self.get_tier_statistics(),
            'model_recommendations': self.get_model_recommendation(),
            'user_quotas': {user_id: asdict(user) for user_id, user in self.users.items()}
        }

        return report

    def save_report(self, report: Dict[str, Any], filename: str = "ai_tier_report.json") -> Path:
        try:
            """Save report to JSON file"""
            reports_dir = project_root / "reports"
            reports_dir.mkdir(exist_ok=True)

            report_path = reports_dir / filename

            with report_path.open('w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"AI Tier report saved to: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main function for Three-Tier AI System"""
    # Initialize system
    ai_system = ThreeTierAISystem()

    # Get current recommendations
    recommendations = ai_system.get_model_recommendation()
    tier_stats = ai_system.get_tier_statistics()

    # Generate comprehensive report
    report = ai_system.generate_comprehensive_report()

    # Save report
    report_file = ai_system.save_report(report)

    # Print summary
    print("\n" + "="*80)
    print("THREE-TIER AI SYSTEM - COMPREHENSIVE REPORT")
    print("="*80)

    # System Info
    print(f"\n💻 SYSTEM CAPABILITIES:")
    print(f"  CPU Cores: {ai_system.system_caps.cpu_cores}")
    print(f"  Total Memory: {ai_system.system_caps.total_memory_gb:.1f} GB")
    print(f"  Available Memory: {ai_system.system_caps.available_memory_gb:.1f} GB")
    print(f"  GPU Available: {'Yes' if ai_system.system_caps.gpu_available else 'No'}")
    if ai_system.system_caps.gpu_available:
        print(f"  GPU Name: {ai_system.system_caps.gpu_name}")
        print(f"  GPU Memory: {ai_system.system_caps.gpu_memory_gb:.1f} GB")

    # Token Pool Status
    print(f"\n🎯 TOKEN POOL STATUS:")
    print(f"  Emergency Mode: {'Yes' if ai_system.token_pool['emergency_mode'] else 'No'}")
    print(f"  Local Only: {'Yes' if ai_system.token_pool['local_only'] else 'No'}")
    print(f"  Used Tokens: {ai_system.token_pool['used_tokens']:,}")
    print(f"  Total Tokens: {ai_system.token_pool['total_tokens']:,}")

    # Current Recommendation
    print(f"\n🤖 CURRENT RECOMMENDATION:")
    print(f"  Optimal Tier: {recommendations['optimal_tier']}")
    print(f"  Recommended Model: {recommendations['recommended_model']}")
    print(f"  Model ID: {recommendations['model_id']}")
    print(f"  Performance: {recommendations['performance_score']}/10")
    print(f"  Max Tokens: {recommendations['max_tokens']:,}")
    print(f"  Reason: {recommendations['reason']}")

    # Tier Statistics
    print(f"\n📊 TIER STATISTICS:")
    for tier_name, stats in recommendations['tier_statistics']['tiers'].items():
        print(f"  {tier_name} Tier:")
        print(f"    Models: {', '.join(stats['available_models'])}")
        print(f"    Available: {'Yes' if stats['service_available'] else 'No'}")
        print(f"    Quota Available: {'Yes' if stats['quota_available'] else 'No'}")
        print(f"    Recommended For: {stats['recommended_for']}")

    # Alternative Recommendations
    if recommendations['alternatives']:
        print(f"\n🔄 ALTERNATIVE OPTIONS:")
        for i, alt in enumerate(recommendations['alternatives'], 1):
            print(f"  {i}. {alt['tier']} Tier - {alt['model']}")
            print(f"     Reason: {alt['reason']}")

    print(f"\n📄 Full report saved to: {report_file}")
    print("="*80 + "\n")

    # ============================================================================
    # GOVERNANCE DECISION-MAKING SYSTEM
    # ============================================================================

    def initiate_governance_decision(self, title: str, description: str,
                                   decision_type: str = "proceed",
                                   governance_level: str = "micro",
                                   required_tier: AITier = AITier.PREMIUM,
                                   stakeholders: Optional[List[str]] = None,
                                   deadline_hours: int = 24) -> str:
        """
        Initiate a governance decision requiring consensus

        Args:
            title: Decision title
            description: Detailed description
            decision_type: Type of decision (proceed, halt, modify, escalate)
            governance_level: micro/macro/enterprise
            required_tier: Minimum tier required for consensus
            stakeholders: List of stakeholders to notify
            deadline_hours: Hours to reach consensus

        Returns:
            Decision ID for tracking
        """
        decision_id = f"gov_{int(time.time())}_{len(self.active_decisions)}"

        decision = GovernanceDecision(
            decision_id=decision_id,
            title=title,
            description=description,
            required_consensus_tier=required_tier,
            decision_type=decision_type,
            stakeholders=stakeholders or [],
            deadline=datetime.now() + timedelta(hours=deadline_hours)
        )

        self.active_decisions[decision_id] = decision

        logger.info(f"🎯 Governance Decision Initiated: {title}")
        logger.info(f"   ID: {decision_id}")
        logger.info(f"   Required Tier: {required_tier.name}")
        logger.info(f"   Governance Level: {governance_level}")
        logger.info(f"   Deadline: {decision.deadline}")

        return decision_id

    def submit_consensus_vote(self, decision_id: str, voter_id: str,
                           voter_tier: AITier, vote_decision: str,
                           reasoning: str, confidence_score: float) -> bool:
        """
        Submit a vote for a governance decision

        Args:
            decision_id: Decision to vote on
            voter_id: ID of the voting entity
            voter_tier: Tier of the voting entity
            vote_decision: approve/deny/modify/escalate
            reasoning: Explanation for the vote
            confidence_score: Confidence in the decision (0.0-1.0)

        Returns:
            Whether vote was accepted
        """
        if decision_id not in self.active_decisions:
            logger.error(f"Decision {decision_id} not found")
            return False

        decision = self.active_decisions[decision_id]

        # Check if voter has authority for this tier
        if voter_tier.value < decision.required_consensus_tier.value:
            logger.warning(f"Voter {voter_id} tier {voter_tier.name} insufficient for {decision.required_consensus_tier.name} decision")
            return False

        vote = ConsensusVote(
            voter_id=voter_id,
            voter_tier=voter_tier,
            decision=vote_decision,
            reasoning=reasoning,
            confidence_score=confidence_score
        )

        decision.votes[voter_id] = {
            "vote": vote_decision,
            "reasoning": reasoning,
            "confidence": confidence_score,
            "tier": voter_tier.name,
            "timestamp": vote.timestamp.isoformat()
        }

        logger.info(f"🗳️  Vote submitted for {decision_id}: {voter_id} ({voter_tier.name}) → {vote_decision}")

        # Check if consensus reached
        self._check_consensus(decision_id)

        return True

    def _check_consensus(self, decision_id: str) -> None:
        """Check if consensus has been reached for a decision"""
        decision = self.active_decisions[decision_id]
        threshold = self.governance_config["consensus_thresholds"].get(decision.required_consensus_tier, 0.8)

        votes = decision.votes
        if not votes:
            return

        # Count votes by decision type
        vote_counts = {}
        total_votes = len(votes)
        tier_votes = {tier.name: 0 for tier in AITier}

        for voter_data in votes.values():
            decision_type = voter_data["vote"]
            tier_name = voter_data["tier"]

            vote_counts[decision_type] = vote_counts.get(decision_type, 0) + 1
            tier_votes[tier_name] += 1

        # Find majority decision
        majority_decision = max(vote_counts.items(), key=lambda x: x[1])
        consensus_ratio = majority_decision[1] / total_votes

        if consensus_ratio >= threshold:
            decision.consensus_reached = True
            decision.resolution = majority_decision[0]
            decision.resolved_at = datetime.now()

            # Move to history
            self.decision_history.append(decision)
            del self.active_decisions[decision_id]

            logger.info(f"✅ CONSENSUS REACHED for {decision_id}")
            logger.info(f"   Decision: {majority_decision[0]}")
            logger.info(f"   Consensus Ratio: {consensus_ratio:.2f}")
            logger.info(f"   Required Threshold: {threshold}")

            self._execute_consensus_decision(decision)
        else:
            logger.info(f"⏳ Consensus not yet reached for {decision_id}: {consensus_ratio:.2f}/{threshold}")

    def _execute_consensus_decision(self, decision: GovernanceDecision) -> None:
        """Execute the consensus decision"""
        if decision.resolution == "proceed":
            logger.info(f"🚀 Proceeding with initiative: {decision.title}")
            # Implementation would trigger the approved action

        elif decision.resolution == "halt":
            logger.warning(f"🛑 Halting initiative: {decision.title}")
            # Implementation would stop the initiative

        elif decision.resolution == "modify":
            logger.info(f"🔄 Modifying initiative: {decision.title}")
            # Implementation would request modifications

        elif decision.resolution == "escalate":
            logger.warning(f"⬆️ Escalating decision: {decision.title}")
            # Implementation would escalate to higher authority

    def get_governance_status(self) -> Dict[str, Any]:
        """Get current governance system status"""
        return {
            "active_decisions": len(self.active_decisions),
            "completed_decisions": len(self.decision_history),
            "tier_hierarchy": {
                tier.name: {
                    "role": tier.governance_role(),
                    "authority": tier.decision_authority(),
                    "consensus_required": tier.consensus_required()
                }
                for tier in AITier
            },
            "active_decisions_detail": [
                {
                    "id": d.decision_id,
                    "title": d.title,
                    "tier": d.required_consensus_tier.name,
                    "type": d.decision_type,
                    "votes": len(d.votes),
                    "deadline": d.deadline.isoformat(),
                    "consensus_reached": d.consensus_reached
                }
                for d in self.active_decisions.values()
            ],
            "recent_decisions": [
                {
                    "id": d.decision_id,
                    "title": d.title,
                    "resolution": d.resolution,
                    "resolved_at": d.resolved_at.isoformat() if d.resolved_at else None
                }
                for d in self.decision_history[-5:]  # Last 5 decisions
            ]
        }

    def demonstrate_governance_hierarchy(self) -> None:
        """Demonstrate the governance hierarchy in action"""
        print("🤖 AI GOVERNANCE HIERARCHY DEMONSTRATION")
        print("="*80)

        print("\n🏗️  TIER HIERARCHY:")
        for tier in AITier:
            config = self.governance_config["tier_hierarchy"][tier]
            print(f"\n{tier.name} TIER - {config['level']}")
            print(f"   Authority: {config['authority']}")
            print(f"   Consensus Required: {config['consensus_required']}")
            print(f"   Decision Power: {config['decision_power']}")

        print("\n📋 DECISION CATEGORIES:")
        for category, tier in self.governance_config["decision_categories"].items():
            print(f"   {category.upper()}: {tier.name} Tier")

        print("\n⚖️  CONSENSUS THRESHOLDS:")
        for tier, threshold in self.governance_config["consensus_thresholds"].items():
            print(f"   {tier.name}: {threshold*100:.0f}% agreement required")

        print("\n🎯 GOVERNANCE LEVELS:")
        for level, description in self.governance_config["governance_levels"].items():
            print(f"   {level.upper()}: {description}")

        print("\n📊 CURRENT STATUS:")
        status = self.get_governance_status()
        print(f"   Active Decisions: {status['active_decisions']}")
        print(f"   Completed Decisions: {status['completed_decisions']}")

        if status['active_decisions'] > 0:
            print("\n🔄 ACTIVE DECISIONS:")
            for decision in status['active_decisions_detail']:
                print(f"   {decision['id']}: {decision['title']}")
                print(f"      Required Tier: {decision['tier']}")
                print(f"      Votes: {decision['votes']}")
                print(f"      Deadline: {decision['deadline'][:19]}")
                print(f"      Consensus: {'✅' if decision['consensus_reached'] else '⏳'}")

        print("\n" + "="*80)

def main():
    """Main CLI interface with governance demonstration"""
    import argparse

    parser = argparse.ArgumentParser(description="Three-Tier AI Governance System")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--governance", action="store_true", help="Show governance hierarchy")
    parser.add_argument("--initiate-decision", nargs=3, metavar=('TITLE', 'DESCRIPTION', 'TIER'),
                       help="Initiate governance decision (tier: local/free/premium)")
    parser.add_argument("--vote", nargs=4, metavar=('DECISION_ID', 'VOTER_ID', 'VOTE', 'CONFIDENCE'),
                       help="Submit vote for decision (vote: approve/deny/modify/escalate)")
    parser.add_argument("--governance-status", action="store_true", help="Show governance status")

    args = parser.parse_args()

    # Initialize system
    system = ThreeTierAISystem()

    if args.governance:
        system.demonstrate_governance_hierarchy()

    elif args.initiate_decision:
        title, description, tier_name = args.initiate_decision
        tier_map = {"local": AITier.LOCAL, "free": AITier.FREE, "premium": AITier.PREMIUM}
        tier = tier_map.get(tier_name.lower())

        if tier:
            decision_id = system.initiate_governance_decision(
                title=title,
                description=description,
                required_tier=tier,
                governance_level="macro"
            )
            print(f"✅ Decision initiated: {decision_id}")
        else:
            print("❌ Invalid tier. Use: local, free, or premium")

    elif args.vote:
        decision_id, voter_id, vote_decision, confidence_str = args.vote

        # Determine voter tier (simplified logic)
        if "premium" in voter_id.lower():
            voter_tier = AITier.PREMIUM
        elif "free" in voter_id.lower() or "middle" in voter_id.lower():
            voter_tier = AITier.FREE
        else:
            voter_tier = AITier.LOCAL

        try:
            confidence = float(confidence_str)
            success = system.submit_consensus_vote(
                decision_id=decision_id,
                voter_id=voter_id,
                voter_tier=voter_tier,
                vote_decision=vote_decision,
                reasoning=f"CLI vote with {confidence:.2f} confidence",
                confidence_score=confidence
            )
            if success:
                print(f"✅ Vote submitted by {voter_id}")
            else:
                print("❌ Vote submission failed")
        except ValueError:
            print("❌ Confidence must be a number between 0.0 and 1.0")

    elif args.governance_status:
        status = system.get_governance_status()
        print("🎯 GOVERNANCE STATUS")
        print("="*50)
        print(f"Active Decisions: {status['active_decisions']}")
        print(f"Completed Decisions: {status['completed_decisions']}")

        if status['active_decisions_detail']:
            print("\n🔄 ACTIVE DECISIONS:")
            for decision in status['active_decisions_detail']:
                print(f"  {decision['id']}: {decision['title']}")
                print(f"    Required Tier: {decision['tier']}")
                print(f"    Votes: {decision['votes']}")
                print(f"    Consensus: {'✅' if decision['consensus_reached'] else '⏳'}")

        if status['recent_decisions']:
            print("\n📋 RECENT DECISIONS:")
            for decision in status['recent_decisions']:
                print(f"  {decision['id']}: {decision['title']} → {decision['resolution']}")

    else:
        # Default: show status
        system.show_status()


if __name__ == "__main__":

    main()