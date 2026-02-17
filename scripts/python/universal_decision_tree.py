#!/usr/bin/env python3
"""
Universal Decision Tree System
<COMPANY_NAME> LLC

Reusable decision tree logic for:
- Local AI → GROK escalation
- Cost control decisions
- Resource allocation
- Any decision-making scenario

Integrated with @SYPHON for logic reuse across the entire system.

@JARVIS @MARVIN @TONY @MACE @GANDALF @SYPHON
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("UniversalDecisionTree")
except:
    logger = None



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DecisionOutcome(Enum):
    """Decision outcomes"""
    # AI/Model decisions
    USE_LOCAL = "use_local"
    RETRY_LOCAL = "retry_local"
    USE_GROK = "use_grok"
    USE_CLOUD = "use_cloud"
    # Cache tier decisions
    USE_L1_CACHE = "use_l1_cache"  # Memory cache
    USE_L2_CACHE = "use_l2_cache"  # SSD cache
    USE_L3_CACHE = "use_l3_cache"  # NAS cache
    FALLBACK_LOCAL_CACHE = "fallback_local_cache"  # Fallback to local only
    # NAS connection decisions
    RETRY_NAS_CONNECTION = "retry_nas_connection"
    USE_NAS_API = "use_nas_api"  # Use API instead of SSH
    SKIP_NAS = "skip_nas"  # Skip NAS, use local only
    # General outcomes
    FAIL = "fail"
    ESCALATE = "escalate"
    SKIP = "skip"  # Skip operation gracefully


@dataclass
class DecisionNode:
    """Decision tree node"""
    node_id: str
    condition: str  # Python expression or function name
    true_outcome: Optional[str] = None  # Next node ID or outcome
    false_outcome: Optional[str] = None  # Next node ID or outcome
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionContext:
    """Context for decision making"""
    # AI/Model context
    complexity: str = "medium"  # low, medium, high
    urgency: str = "medium"  # low, medium, high
    cost_sensitive: bool = True
    local_ai_available: bool = True
    local_ai_quality: float = 0.8  # 0.0 to 1.0
    retry_count: int = 0
    max_retries: int = 3
    # Cache context
    cache_data_size: int = 0  # Size in bytes
    memory_cache_available: bool = True
    memory_cache_usage_percent: float = 0.0  # 0.0 to 100.0
    ssd_cache_available: bool = True
    ssd_cache_usage_percent: float = 0.0
    nas_cache_available: bool = False
    nas_api_available: bool = False
    nas_ssh_available: bool = False
    cache_domain: str = "generic"  # e.g., "jarvis_cron", "physics"
    # Connection context
    connection_retry_count: int = 0
    last_error: Optional[str] = None
    error_count: int = 0
    # General
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionResult:
    """Decision result"""
    outcome: DecisionOutcome
    reasoning: str
    confidence: float  # 0.0 to 1.0
    next_action: str
    cost_estimate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class UniversalDecisionTree:
    """
    Universal Decision Tree System

    Reusable decision tree logic that can be applied anywhere.
    Integrated with @SYPHON for logic extraction and reuse.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize decision tree system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger or self._get_logger()

        # Load decision tree config
        self.config_file = self.project_root / "config" / "ai_decision_tree.json"
        self.trees: Dict[str, Dict[str, Any]] = {}

        # Ensure default trees are created first
        self._create_default_trees()

        # Then try to load from config (will merge or replace)
        self._load_trees()

        self.logger.info("✅ Universal Decision Tree System initialized")

    def decide(self, 
               tree_name: str,
               context: DecisionContext) -> DecisionResult:
        """
        Make decision using specified tree

        Args:
            tree_name: Name of decision tree to use
            context: Decision context

        Returns:
            Decision result
        """
        if tree_name not in self.trees:
            self.logger.error(f"Decision tree '{tree_name}' not found")
            return DecisionResult(
                outcome=DecisionOutcome.FAIL,
                reasoning=f"Tree '{tree_name}' not found",
                confidence=0.0,
                next_action="fail"
            )

        tree = self.trees[tree_name]
        root_node_id = tree.get("root_node", "start")

        # Traverse tree
        result = self._traverse_tree(tree, root_node_id, context)

        return result

    def _traverse_tree(self,
                      tree: Dict[str, Any],
                      node_id: str,
                      context: DecisionContext) -> DecisionResult:
        """Traverse decision tree"""
        nodes = tree.get("nodes", {})

        if node_id not in nodes:
            return DecisionResult(
                outcome=DecisionOutcome.FAIL,
                reasoning=f"Node '{node_id}' not found",
                confidence=0.0,
                next_action="fail"
            )

        node = nodes[node_id]
        condition = node.get("condition", "")

        # Evaluate condition
        condition_result = self._evaluate_condition(condition, context)

        # Get next node or outcome
        if condition_result:
            next_step = node.get("true_outcome")
        else:
            next_step = node.get("false_outcome")

        # Check if it's an outcome or another node
        if next_step in [e.value for e in DecisionOutcome]:
            # It's a final outcome
            outcome = DecisionOutcome(next_step)
            reasoning = node.get("reasoning", f"Condition '{condition}' evaluated to {condition_result}")
            confidence = node.get("confidence", 0.8)

            # Calculate cost estimate
            cost = self._estimate_cost(outcome, context)

            return DecisionResult(
                outcome=outcome,
                reasoning=reasoning,
                confidence=confidence,
                next_action=outcome.value,
                cost_estimate=cost,
                metadata=node.get("metadata", {})
            )
        else:
            # Continue traversing
            return self._traverse_tree(tree, next_step, context)

    def _evaluate_condition(self, condition: str, context: DecisionContext) -> bool:
        """Evaluate condition against context"""
        # Convert context to dict for evaluation
        ctx_dict = {
            # AI/Model context
            "complexity": context.complexity,
            "urgency": context.urgency,
            "cost_sensitive": context.cost_sensitive,
            "local_ai_available": context.local_ai_available,
            "local_ai_quality": context.local_ai_quality,
            "retry_count": context.retry_count,
            "max_retries": context.max_retries,
            # Cache context
            "cache_data_size": context.cache_data_size,
            "memory_cache_available": context.memory_cache_available,
            "memory_cache_usage_percent": context.memory_cache_usage_percent,
            "ssd_cache_available": context.ssd_cache_available,
            "ssd_cache_usage_percent": context.ssd_cache_usage_percent,
            "nas_cache_available": context.nas_cache_available,
            "nas_api_available": context.nas_api_available,
            "nas_ssh_available": context.nas_ssh_available,
            "cache_domain": context.cache_domain,
            # Connection context
            "connection_retry_count": context.connection_retry_count,
            "last_error": context.last_error or "",
            "error_count": context.error_count,
            **context.custom_data
        }

        # Map string values to numbers for comparison
        complexity_map = {"low": 1, "medium": 2, "high": 3}
        urgency_map = {"low": 1, "medium": 2, "high": 3}

        ctx_dict["complexity_num"] = complexity_map.get(ctx_dict["complexity"], 2)
        ctx_dict["urgency_num"] = urgency_map.get(ctx_dict["urgency"], 2)

        # Parse condition safely using AST (replaces dangerous eval)
        try:
            import ast
            tree = ast.parse(condition, mode='eval')
            result = self._safe_ast_check(tree.body, ctx_dict)
            return bool(result)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking condition '{condition}': {e}")
            return False

    def _safe_ast_check(self, node, ctx: dict):
        """Check an AST node safely — only comparisons, booleans, literals, variable lookups."""
        import ast
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in ctx:
                return ctx[node.id]
            raise ValueError(f"Unknown variable: {node.id}")
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._safe_ast_check(v, ctx) for v in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._safe_ast_check(v, ctx) for v in node.values)
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return not self._safe_ast_check(node.operand, ctx)
            elif isinstance(node.op, ast.USub):
                return -self._safe_ast_check(node.operand, ctx)
        elif isinstance(node, ast.Compare):
            left = self._safe_ast_check(node.left, ctx)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._safe_ast_check(comparator, ctx)
                if isinstance(op, ast.Eq): check = left == right
                elif isinstance(op, ast.NotEq): check = left != right
                elif isinstance(op, ast.Lt): check = left < right
                elif isinstance(op, ast.LtE): check = left <= right
                elif isinstance(op, ast.Gt): check = left > right
                elif isinstance(op, ast.GtE): check = left >= right
                elif isinstance(op, ast.In): check = left in right
                else: raise ValueError(f"Unsupported operator: {type(op).__name__}")
                if not check:
                    return False
                left = right
            return True
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                obj = self._safe_ast_check(node.func.value, ctx)
                method = node.func.attr
                if method == 'lower' and isinstance(obj, str):
                    return obj.lower()
            raise ValueError("Function calls not allowed in conditions")
        elif isinstance(node, ast.Attribute):
            obj = self._safe_ast_check(node.value, ctx)
            attr = node.attr
            if attr in ('lower',) and isinstance(obj, str):
                return getattr(obj, attr)
            raise ValueError(f"Attribute access not allowed: {attr}")
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    def _estimate_cost(self, outcome: DecisionOutcome, context: DecisionContext) -> float:
        """Estimate cost for outcome"""
        # Cost per 1M tokens (for AI outcomes)
        costs = {
            DecisionOutcome.USE_LOCAL: 0.001,  # $0.001 per 1M tokens
            DecisionOutcome.RETRY_LOCAL: 0.001,
            DecisionOutcome.USE_GROK: 5.00,  # $5 per 1M tokens
            DecisionOutcome.USE_CLOUD: 47.00,  # $47 per 1M tokens
            # Cache operations (essentially free, just storage)
            DecisionOutcome.USE_L1_CACHE: 0.0,
            DecisionOutcome.USE_L2_CACHE: 0.0,
            DecisionOutcome.USE_L3_CACHE: 0.0,
            DecisionOutcome.FALLBACK_LOCAL_CACHE: 0.0,
            # NAS operations (network cost negligible)
            DecisionOutcome.RETRY_NAS_CONNECTION: 0.0,
            DecisionOutcome.USE_NAS_API: 0.0,
            DecisionOutcome.SKIP_NAS: 0.0,
            # General outcomes
            DecisionOutcome.FAIL: 0.0,
            DecisionOutcome.ESCALATE: 0.0,
            DecisionOutcome.SKIP: 0.0
        }

        # Estimate tokens (simplified - would need actual estimation)
        estimated_tokens = 1000  # Default estimate for AI operations

        return (estimated_tokens / 1_000_000) * costs.get(outcome, 0.0)

    def _load_trees(self):
        """Load decision trees from config (merge with defaults)"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    loaded_trees = data.get("trees", {})
                    # Merge loaded trees with defaults (loaded trees take precedence)
                    self.trees.update(loaded_trees)
                    if len(loaded_trees) > 0:
                        self.logger.info(f"✅ Loaded {len(loaded_trees)} decision trees from config")
                    # Ensure defaults exist (in case config is missing some)
                    self._create_default_trees()
                    # Save to ensure all trees are persisted
                    self._save_trees()
            except Exception as e:
                self.logger.error(f"Failed to load decision trees: {e}")
                # Ensure defaults exist even if loading fails
                self._create_default_trees()
                self._save_trees()
        else:
            # Config file doesn't exist, just ensure defaults are created and save them
            self._create_default_trees()
            self._save_trees()

    def _create_default_trees(self):
        """Create default decision trees"""
        # AI Fallback Tree (Local → GROK → Cloud)
        if "ai_fallback" not in self.trees:
            self.trees["ai_fallback"] = {
            "name": "AI Fallback Decision Tree",
            "description": "Decides when to use local AI, GROK, or cloud",
            "root_node": "start",
            "nodes": {
                "start": {
                    "condition": "local_ai_available == True",
                    "true_outcome": "check_quality",
                    "false_outcome": "use_grok",
                    "reasoning": "Check if local AI is available"
                },
                "check_quality": {
                    "condition": "local_ai_quality >= 0.7",
                    "true_outcome": "use_local",
                    "false_outcome": "check_retries",
                    "reasoning": "Local AI quality is acceptable"
                },
                "check_retries": {
                    "condition": "retry_count < max_retries",
                    "true_outcome": "retry_local",
                    "false_outcome": "check_complexity",
                    "reasoning": "Retry local AI if under retry limit"
                },
                "check_complexity": {
                    "condition": "complexity_num >= 3 or urgency_num >= 3",
                    "true_outcome": "use_grok",
                    "false_outcome": "check_cost",
                    "reasoning": "High complexity/urgency needs GROK"
                },
                "check_cost": {
                    "condition": "cost_sensitive == False",
                    "true_outcome": "use_grok",
                    "false_outcome": "use_local",
                    "reasoning": "If not cost-sensitive, use GROK"
                },
                "use_local": {
                    "condition": "True",
                    "true_outcome": DecisionOutcome.USE_LOCAL.value,
                    "reasoning": "Use local AI",
                    "confidence": 0.9
                },
                "retry_local": {
                    "condition": "True",
                    "true_outcome": DecisionOutcome.RETRY_LOCAL.value,
                    "reasoning": "Retry local AI",
                    "confidence": 0.8
                },
                "use_grok": {
                    "condition": "True",
                    "true_outcome": DecisionOutcome.USE_GROK.value,
                    "reasoning": "Use GROK (not gate-gated, decision tree controlled)",
                    "confidence": 0.85
                }
            }
        }

        # Cache Tier Selection Tree (L1 → L2 → L3)
        if "cache_tier_selection" not in self.trees:
            self.trees["cache_tier_selection"] = {
                "name": "Cache Tier Selection Decision Tree",
                "description": "Decides which cache tier to use (L1 memory, L2 SSD, L3 NAS)",
                "root_node": "start",
                "nodes": {
                    "start": {
                        "condition": "cache_data_size > 0",
                        "true_outcome": "check_memory",
                        "false_outcome": "use_l1_cache",
                        "reasoning": "Check data size to determine cache tier"
                    },
                    "check_memory": {
                        "condition": "memory_cache_available == True and (cache_data_size < 10485760 or memory_cache_usage_percent < 80.0)",
                        "true_outcome": "use_l1_cache",
                        "false_outcome": "check_ssd",
                        "reasoning": "Use L1 if memory available and data fits or memory not full"
                    },
                    "check_ssd": {
                        "condition": "ssd_cache_available == True and (cache_data_size < 1073741824 or ssd_cache_usage_percent < 80.0)",
                        "true_outcome": "use_l2_cache",
                        "false_outcome": "check_nas",
                        "reasoning": "Use L2 SSD if available and data fits or SSD not full"
                    },
                    "check_nas": {
                        "condition": "nas_cache_available == True",
                        "true_outcome": "use_l3_cache",
                        "false_outcome": "check_domain",
                        "reasoning": "Use L3 NAS if available"
                    },
                    "check_domain": {
                        "condition": "cache_domain == 'jarvis_cron'",
                        "true_outcome": "use_l2_cache",
                        "false_outcome": "fallback_local_cache",
                        "reasoning": "jarvis_cron domain requires persistence, prefer L2"
                    },
                    "use_l1_cache": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.USE_L1_CACHE.value,
                        "reasoning": "Use L1 memory cache (fastest)",
                        "confidence": 0.95
                    },
                    "use_l2_cache": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.USE_L2_CACHE.value,
                        "reasoning": "Use L2 SSD cache (persistent)",
                        "confidence": 0.90
                    },
                    "use_l3_cache": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.USE_L3_CACHE.value,
                        "reasoning": "Use L3 NAS cache (most persistent)",
                        "confidence": 0.85
                    },
                    "fallback_local_cache": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.FALLBACK_LOCAL_CACHE.value,
                        "reasoning": "Fallback to local cache only",
                        "confidence": 0.80
                    }
                }
            }

        # NAS Connection Decision Tree
        if "nas_connection" not in self.trees:
            self.trees["nas_connection"] = {
                "name": "NAS Connection Decision Tree",
                "description": "Decides NAS connection strategy (SSH, API, retry, skip)",
                "root_node": "start",
                "nodes": {
                    "start": {
                        "condition": "nas_ssh_available == True",
                        "true_outcome": "use_ssh",
                        "false_outcome": "check_api",
                        "reasoning": "Check SSH availability first"
                    },
                    "check_api": {
                        "condition": "nas_api_available == True",
                        "true_outcome": "use_nas_api",
                        "false_outcome": "check_retries",
                        "reasoning": "SSH unavailable, check API"
                    },
                    "check_retries": {
                        "condition": "connection_retry_count < 3",
                        "true_outcome": "retry_nas_connection",
                        "false_outcome": "skip_nas",
                        "reasoning": "Retry if under limit"
                    },
                    "use_ssh": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.USE_LOCAL.value,  # SSH is local connection method
                        "reasoning": "Use SSH connection",
                        "confidence": 0.90
                    },
                    "use_nas_api": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.USE_NAS_API.value,
                        "reasoning": "Use NAS API connection",
                        "confidence": 0.85
                    },
                    "retry_nas_connection": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.RETRY_NAS_CONNECTION.value,
                        "reasoning": "Retry NAS connection",
                        "confidence": 0.75
                    },
                    "skip_nas": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.SKIP_NAS.value,
                        "reasoning": "Skip NAS, use local cache only",
                        "confidence": 0.95
                    }
                }
            }

        # Error Handling Decision Tree
        if "error_handling" not in self.trees:
            self.trees["error_handling"] = {
                "name": "Error Handling Decision Tree",
                "description": "Decides how to handle errors (retry, skip, fail, escalate)",
                "root_node": "start",
                "nodes": {
                    "start": {
                        "condition": "error_count > 0",
                        "true_outcome": "check_retries",
                        "false_outcome": "skip",
                        "reasoning": "Check if errors occurred"
                    },
                    "check_retries": {
                        "condition": "retry_count < max_retries",
                        "true_outcome": "check_error_type",
                        "false_outcome": "check_urgency",
                        "reasoning": "Check retry availability"
                    },
                    "check_error_type": {
                        "condition": "'timeout' in (last_error or '').lower() or 'connection' in (last_error or '').lower()",
                        "true_outcome": "retry_local",
                        "false_outcome": "check_severity",
                        "reasoning": "Connection/timeout errors are retriable"
                    },
                    "check_severity": {
                        "condition": "error_count < 3",
                        "true_outcome": "retry_local",
                        "false_outcome": "check_urgency",
                        "reasoning": "Low error count, safe to retry"
                    },
                    "check_urgency": {
                        "condition": "urgency_num >= 3",
                        "true_outcome": "escalate",
                        "false_outcome": "skip",
                        "reasoning": "High urgency requires escalation"
                    },
                    "retry_local": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.RETRY_LOCAL.value,
                        "reasoning": "Retry operation",
                        "confidence": 0.80
                    },
                    "skip": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.SKIP.value,
                        "reasoning": "Skip operation gracefully",
                        "confidence": 0.90
                    },
                    "escalate": {
                        "condition": "True",
                        "true_outcome": DecisionOutcome.ESCALATE.value,
                        "reasoning": "Escalate to higher level",
                        "confidence": 0.85
                    }
                }
            }

    def _save_trees(self):
        try:
            """Save decision trees to config"""
            data = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "trees": self.trees
            }

            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"💾 Saved decision trees to {self.config_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_trees: {e}", exc_info=True)
            raise
    def _get_logger(self):
        """Get logger"""
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("UniversalDecisionTree")


# Singleton instance
_decision_tree_instance: Optional[UniversalDecisionTree] = None


def get_decision_tree() -> UniversalDecisionTree:
    """Get singleton decision tree instance"""
    global _decision_tree_instance
    if _decision_tree_instance is None:
        _decision_tree_instance = UniversalDecisionTree()
    return _decision_tree_instance


def decide(tree_name: str, context: DecisionContext) -> DecisionResult:
    """Convenience function for decision making"""
    tree = get_decision_tree()
    return tree.decide(tree_name, context)


if __name__ == "__main__":
    # Test decision tree
    tree = get_decision_tree()

    # Test case 1: Local AI available, good quality
    context1 = DecisionContext(
        complexity="medium",
        urgency="low",
        cost_sensitive=True,
        local_ai_available=True,
        local_ai_quality=0.9
    )
    result1 = tree.decide("ai_fallback", context1)
    print(f"\nTest 1: {result1.outcome.value}")
    print(f"   Reasoning: {result1.reasoning}")
    print(f"   Cost: ${result1.cost_estimate:.4f}")

    # Test case 2: Local AI low quality, high complexity
    context2 = DecisionContext(
        complexity="high",
        urgency="high",
        cost_sensitive=False,
        local_ai_available=True,
        local_ai_quality=0.5,
        retry_count=3
    )
    result2 = tree.decide("ai_fallback", context2)
    print(f"\nTest 2: {result2.outcome.value}")
    print(f"   Reasoning: {result2.reasoning}")
    print(f"   Cost: ${result2.cost_estimate:.4f}")

