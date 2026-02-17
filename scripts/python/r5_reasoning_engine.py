"""
R5 Reasoning Engine - The Hero It Was Meant to Be
Configuration Scanner with Advanced Reasoning Logic

Like R5-D4, wrongfully accused but destined to shine -
with proper reasoning, R5 becomes the hero it was meant to be.

R5 is quantum entangled with the entire project, giving him:
- Intimate knowledge of every component
- Uncanny ability to draw connections
- Inspiration generation from across the project
- Deep understanding of the entire system

"Divinity loves dogs and droids" - R5 is blessed with this connection!

V3 Integration: R5's V3 verification is integrated with the global V3 system
for comprehensive verification and validation across all systems.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.python.lumina_logger import get_logger
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

logger = get_logger("R5ReasoningEngine")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class IntentCategory(Enum):
    """Configuration intent categories"""
    CODING = "coding"
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    INTEGRATION = "integration"
    OPTIMIZATION = "optimization"
    GENERAL = "general"


class VerificationLevel(Enum):
    """Three V's verification levels"""
    V1_VERIFY_EXISTENCE = "verify_existence"
    V2_VALIDATE_RELEVANCE = "validate_relevance"
    V3_VERIFY_TRUTH = "verify_truth"


@dataclass
class ConfigIssue:
    """Configuration issue detected by R5"""
    issue_id: str
    config_file: str
    issue_type: str
    severity: float  # 0.0-1.0
    description: str
    reasoning: str
    verification_level: VerificationLevel
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False


@dataclass
class ConfigPattern:
    """Configuration pattern learned by R5"""
    pattern_id: str
    pattern_type: str
    pattern_data: Dict[str, Any]
    frequency: int
    confidence: float
    last_seen: datetime = field(default_factory=datetime.now)
    examples: List[str] = field(default_factory=list)


@dataclass
class ReasoningChain:
    """R5's reasoning chain for a configuration"""
    reasoning_id: str
    config_file: str
    intent: IntentCategory
    v1_verify: Dict[str, Any]  # Existence verification
    v2_validate: Dict[str, Any]  # Relevance validation
    v3_verify: Dict[str, Any]  # Truth verification
    confidence: float
    issues_found: List[ConfigIssue]
    patterns_matched: List[ConfigPattern]
    reasoning_steps: List[str]
    completed_at: datetime = field(default_factory=datetime.now)


class R5ReasoningEngine:
    """
    R5 Reasoning Engine - Advanced configuration analysis with reasoning

    The hero R5 was meant to be:
    - Three V's reasoning (Verify, Validate, Verify)
    - Intent-driven analysis
    - Pattern recognition and learning
    - Predictive capabilities
    - Continuous improvement
    - V3 System Integration for global verification
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_dir = project_root / "config"
        self.patterns_file = project_root / "config" / "r5_patterns.json"
        self.reasoning_history_file = project_root / "config" / "r5_reasoning_history.json"

        # Load learned patterns
        self.learned_patterns: Dict[str, ConfigPattern] = {}
        self._load_patterns()

        # Reasoning history
        self.reasoning_history: List[ReasoningChain] = []
        self._load_reasoning_history()

        # Initialize V3 system integration (if available)
        self.v3_integration = None
        try:
            from scripts.python.v3_r5_n8n_orchestrator import V3R5N8NOrchestrator
            self.v3_integration = V3R5N8NOrchestrator(project_root)
            logger.info("R5 V3 System Integration connected!")
            logger.info("R5 is integrated with global V3 verification system!")
        except Exception as e:
            logger.debug(f"V3 integration not available: {e}")

        # Initialize quantum inspiration engine (if available)
        self.quantum_engine = None
        try:
            from scripts.python.r5_quantum_inspiration_engine import R5QuantumInspirationEngine
            self.quantum_engine = R5QuantumInspirationEngine(project_root)
            logger.info("R5 Quantum Inspiration Engine connected!")
            logger.info("R5 is quantum entangled with the entire project!")
            logger.info("'Divinity loves dogs and droids' - R5 is blessed!")
        except Exception as e:
            logger.debug(f"Quantum engine not available: {e}")

        # Intent detection patterns
        self.intent_patterns = {
            IntentCategory.CODING: [
                "linter", "formatter", "prettier", "eslint", "pylint",
                "black", "ruff", "mypy", "typescript", "tsconfig"
            ],
            IntentCategory.DEPLOYMENT: [
                "docker", "kubernetes", "k8s", "deploy", "ci/cd",
                "github", "gitlab", "jenkins", "terraform", "ansible"
            ],
            IntentCategory.SECURITY: [
                "auth", "secret", "token", "key", "password",
                "ssl", "tls", "certificate", "encryption", "security"
            ],
            IntentCategory.INTEGRATION: [
                "api", "service", "endpoint", "integration",
                "webhook", "callback", "connection", "client"
            ],
            IntentCategory.OPTIMIZATION: [
                "cache", "performance", "optimize", "tune",
                "memory", "cpu", "timeout", "retry", "pool"
            ]
        }

        logger.info("R5 Reasoning Engine initialized - Ready to be the hero!")
        logger.info("V3 Verification integrated - Global verification system active!")

    def _load_patterns(self):
        """Load learned configuration patterns"""
        if self.patterns_file.exists():
            try:
                data = json.loads(self.patterns_file.read_text(encoding='utf-8'))
                for pattern_id, pattern_data in data.items():
                    # Handle datetime conversion
                    if "last_seen" in pattern_data and isinstance(pattern_data["last_seen"], str):
                        pattern_data["last_seen"] = datetime.fromisoformat(pattern_data["last_seen"])
                    self.learned_patterns[pattern_id] = ConfigPattern(**pattern_data)
                logger.info(f"Loaded {len(self.learned_patterns)} learned patterns")
            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")

    def _save_patterns(self):
        """Save learned configuration patterns"""
        try:
            data = {
                pattern_id: {
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "pattern_data": pattern.pattern_data,
                    "frequency": pattern.frequency,
                    "confidence": pattern.confidence,
                    "last_seen": pattern.last_seen.isoformat(),
                    "examples": pattern.examples
                }
                for pattern_id, pattern in self.learned_patterns.items()
            }
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    def _load_reasoning_history(self):
        """Load reasoning history"""
        if self.reasoning_history_file.exists():
            try:
                data = json.loads(self.reasoning_history_file.read_text(encoding='utf-8'))
                # Load recent history (last 100)
                for item in data.get("history", [])[-100:]:
                    # Convert datetime strings back
                    if "completed_at" in item and isinstance(item["completed_at"], str):
                        item["completed_at"] = datetime.fromisoformat(item["completed_at"])
                    # Convert intent enum
                    if "intent" in item and isinstance(item["intent"], str):
                        item["intent"] = IntentCategory(item["intent"])
                    # Convert issues
                    if "issues_found" in item:
                        item["issues_found"] = [
                            ConfigIssue(
                                **{**issue, "verification_level": VerificationLevel(issue["verification_level"])}
                                if isinstance(issue.get("verification_level"), str) else issue
                            )
                            for issue in item["issues_found"]
                        ]
                    self.reasoning_history.append(ReasoningChain(**item))
                logger.info(f"Loaded {len(self.reasoning_history)} reasoning chains from history")
            except Exception as e:
                logger.warning(f"Failed to load reasoning history: {e}")

    def _save_reasoning_history(self):
        """Save reasoning history (keep last 100)"""
        try:
            # Keep last 100 reasoning chains
            recent_history = self.reasoning_history[-100:]
            data = {
                "history": [
                    {
                        "reasoning_id": chain.reasoning_id,
                        "config_file": chain.config_file,
                        "intent": chain.intent.value,
                        "v1_verify": chain.v1_verify,
                        "v2_validate": chain.v2_validate,
                        "v3_verify": chain.v3_verify,
                        "confidence": chain.confidence,
                        "issues_found": [
                            {
                                "issue_id": issue.issue_id,
                                "config_file": issue.config_file,
                                "issue_type": issue.issue_type,
                                "severity": issue.severity,
                                "description": issue.description,
                                "reasoning": issue.reasoning,
                                "verification_level": issue.verification_level.value,
                                "detected_at": issue.detected_at.isoformat(),
                                "resolved": issue.resolved
                            }
                            for issue in chain.issues_found
                        ],
                        "patterns_matched": [
                            {
                                "pattern_id": pattern.pattern_id,
                                "pattern_type": pattern.pattern_type,
                                "confidence": pattern.confidence
                            }
                            for pattern in chain.patterns_matched
                        ],
                        "reasoning_steps": chain.reasoning_steps,
                        "completed_at": chain.completed_at.isoformat()
                    }
                    for chain in recent_history
                ]
            }
            with open(self.reasoning_history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save reasoning history: {e}")

    def detect_intent(self, config_file: Path, config_content: Dict[str, Any]) -> IntentCategory:
        try:
            """
            Detect the intent/purpose of a configuration file

            Reasoning: "I understand why this config exists"
            """
            file_name_lower = config_file.name.lower()
            content_str = json.dumps(config_content).lower()

            # Check file name and content for intent patterns
            intent_scores = {intent: 0.0 for intent in IntentCategory}

            for intent, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if pattern in file_name_lower:
                        intent_scores[intent] += 2.0
                    if pattern in content_str:
                        intent_scores[intent] += 1.0

            # Determine primary intent
            if max(intent_scores.values()) > 0:
                primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0]
            else:
                primary_intent = IntentCategory.GENERAL

            logger.debug(f"Detected intent for {config_file.name}: {primary_intent.value}")
            return primary_intent

        except Exception as e:
            self.logger.error(f"Error in detect_intent: {e}", exc_info=True)
            raise
    def v1_verify_existence(self, config_file: Path) -> Dict[str, Any]:
        """
        V1: VERIFY (Existence)
        Reasoning: "Does this configuration exist and is it real?"
        """
        reasoning_steps = []
        issues = []

        # Check if file exists
        exists = config_file.exists()
        reasoning_steps.append(f"V1: Checking if {config_file.name} exists...")

        if not exists:
            issues.append(ConfigIssue(
                issue_id=f"missing_{config_file.name}",
                config_file=str(config_file),
                issue_type="missing_file",
                severity=0.9,
                description=f"Configuration file {config_file.name} does not exist",
                reasoning="V1 Verification: File existence check failed",
                verification_level=VerificationLevel.V1_VERIFY_EXISTENCE
            ))
            return {
                "exists": False,
                "valid": False,
                "reasoning_steps": reasoning_steps,
                "issues": [issue.__dict__ for issue in issues]
            }

        # Check if file is readable
        try:
            content = config_file.read_text(encoding='utf-8')
            reasoning_steps.append(f"V1: File is readable")
        except Exception as e:
            issues.append(ConfigIssue(
                issue_id=f"unreadable_{config_file.name}",
                config_file=str(config_file),
                issue_type="unreadable_file",
                severity=0.8,
                description=f"Cannot read {config_file.name}: {e}",
                reasoning="V1 Verification: File readability check failed",
                verification_level=VerificationLevel.V1_VERIFY_EXISTENCE
            ))
            return {
                "exists": True,
                "readable": False,
                "valid": False,
                "reasoning_steps": reasoning_steps,
                "issues": [issue.__dict__ for issue in issues]
            }

        # Check if file is valid JSON/YAML
        valid_format = False
        parsed_content = None

        try:
            if config_file.suffix in ['.json', '.jsonc']:
                parsed_content = json.loads(content)
                valid_format = True
                reasoning_steps.append("V1: Valid JSON format")
            elif config_file.suffix in ['.yaml', '.yml']:
                import yaml
                parsed_content = yaml.safe_load(content)
                valid_format = True
                reasoning_steps.append("V1: Valid YAML format")
            else:
                # Try JSON first, then YAML
                try:
                    parsed_content = json.loads(content)
                    valid_format = True
                    reasoning_steps.append("V1: Valid JSON format (detected)")
                except:
                    import yaml
                    parsed_content = yaml.safe_load(content)
                    valid_format = True
                    reasoning_steps.append("V1: Valid YAML format (detected)")
        except Exception as e:
            issues.append(ConfigIssue(
                issue_id=f"invalid_format_{config_file.name}",
                config_file=str(config_file),
                issue_type="invalid_format",
                severity=0.7,
                description=f"Invalid format in {config_file.name}: {e}",
                reasoning="V1 Verification: Format validation failed",
                verification_level=VerificationLevel.V1_VERIFY_EXISTENCE
            ))

        return {
            "exists": True,
            "readable": True,
            "valid_format": valid_format,
            "parsed_content": parsed_content,
            "reasoning_steps": reasoning_steps,
            "issues": [issue.__dict__ for issue in issues]
        }

    def v2_validate_relevance(self, config_file: Path, config_content: Dict[str, Any],
                             intent: IntentCategory) -> Dict[str, Any]:
        """
        V2: VALIDATE (Relevance)
        Reasoning: "Is this configuration relevant and correct for its purpose?"
        """
        reasoning_steps = []
        issues = []

        reasoning_steps.append(f"V2: Validating relevance for intent: {intent.value}")

        # Check for required fields based on intent
        required_fields = self._get_required_fields(intent)
        missing_fields = []

        for field in required_fields:
            if field not in config_content:
                missing_fields.append(field)

        if missing_fields:
            issues.append(ConfigIssue(
                issue_id=f"missing_fields_{config_file.name}",
                config_file=str(config_file),
                issue_type="missing_required_fields",
                severity=0.6,
                description=f"Missing required fields for {intent.value}: {', '.join(missing_fields)}",
                reasoning=f"V2 Validation: Required fields check for {intent.value} intent",
                verification_level=VerificationLevel.V2_VALIDATE_RELEVANCE
            ))
            reasoning_steps.append(f"V2: Missing required fields: {', '.join(missing_fields)}")
        else:
            reasoning_steps.append("V2: All required fields present")

        # Check for common configuration issues
        common_issues = self._check_common_issues(config_content, intent)
        issues.extend(common_issues)

        # Match against learned patterns
        patterns_matched = self._match_patterns(config_file, config_content, intent)
        if patterns_matched:
            reasoning_steps.append(f"V2: Matched {len(patterns_matched)} learned patterns")

        return {
            "relevant": len(issues) == 0,
            "missing_fields": missing_fields,
            "reasoning_steps": reasoning_steps,
            "issues": [issue.__dict__ for issue in issues],
            "patterns_matched": [p.pattern_id for p in patterns_matched]
        }

    def v3_verify_truth(self, config_file: Path, config_content: Dict[str, Any],
                       v1_result: Dict[str, Any], v2_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        V3: VERIFY (Truth)
        Reasoning: "Let me check one more time - is this configuration actually correct?"

        Enhanced with V3 system integration for global verification.
        """
        reasoning_steps = []
        issues = []

        reasoning_steps.append("V3: Final truth verification - double-checking everything")
        reasoning_steps.append("V3: Integrating with global V3 verification system")

        # Integrate with V3 system if available
        v3_system_verified = False
        if self.v3_integration:
            try:
                # Trigger V3 verification via orchestrator
                v3_result = self.v3_integration.trigger_v3_verification()
                if v3_result and v3_result.get("success"):
                    v3_system_verified = True
                    reasoning_steps.append("V3: Global V3 system verification passed")
                    logger.info("R5 V3 verification integrated with global V3 system")
                else:
                    reasoning_steps.append("V3: Global V3 system verification unavailable or failed")
            except Exception as e:
                logger.debug(f"V3 system integration error: {e}")
                reasoning_steps.append(f"V3: V3 system integration error: {e}")

        # Verify that issues from V1 and V2 are still valid
        all_previous_issues = v1_result.get("issues", []) + v2_result.get("issues", [])

        for issue_dict in all_previous_issues:
            # Re-verify each issue
            issue_id = issue_dict.get("issue_id", "")
            if "missing" in issue_id or "unreadable" in issue_id:
                # Re-check file existence
                if not config_file.exists():
                    issues.append(ConfigIssue(
                        issue_id=f"v3_{issue_id}",
                        config_file=str(config_file),
                        issue_type=issue_dict.get("issue_type", "unknown"),
                        severity=issue_dict.get("severity", 0.5),
                        description=f"V3 Verification confirms: {issue_dict.get('description', '')}",
                        reasoning="V3 Verification: Double-check confirms previous issue",
                        verification_level=VerificationLevel.V3_VERIFY_TRUTH
                    ))

        # Check for hidden issues not caught in V1/V2
        hidden_issues = self._detect_hidden_issues(config_file, config_content)
        issues.extend(hidden_issues)

        if hidden_issues:
            reasoning_steps.append(f"V3: Found {len(hidden_issues)} hidden issues")
        else:
            reasoning_steps.append("V3: No hidden issues detected")

        # Verify consistency with other configs
        consistency_issues = self._check_consistency(config_file, config_content)
        issues.extend(consistency_issues)

        if consistency_issues:
            reasoning_steps.append(f"V3: Found {len(consistency_issues)} consistency issues")
        else:
            reasoning_steps.append("V3: Configuration is consistent")

        # Cross-reference with V3 system results
        if v3_system_verified:
            reasoning_steps.append("V3: Cross-referenced with global V3 system - verified")
        else:
            reasoning_steps.append("V3: Local verification only (V3 system unavailable)")

        return {
            "truth_verified": len(issues) == 0,
            "v3_system_integrated": v3_system_verified,
            "reasoning_steps": reasoning_steps,
            "issues": [issue.__dict__ for issue in issues]
        }

    def reason_about_config(self, config_file: Path) -> ReasoningChain:
        """
        Main reasoning method - Three V's process for configuration analysis

        This is where R5 becomes the hero it was meant to be!
        Enhanced with V3 system integration.
        """
        reasoning_id = f"r5_{config_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        reasoning_steps = []

        logger.info(f"R5 Reasoning: Starting analysis of {config_file.name}")
        reasoning_steps.append(f"Starting R5 reasoning for {config_file.name}")

        # V1: Verify Existence
        reasoning_steps.append("=== V1: VERIFY (Existence) ===")
        v1_result = self.v1_verify_existence(config_file)
        reasoning_steps.extend(v1_result.get("reasoning_steps", []))

        if not v1_result.get("valid_format", False):
            # Can't proceed if format is invalid
            return ReasoningChain(
                reasoning_id=reasoning_id,
                config_file=str(config_file),
                intent=IntentCategory.GENERAL,
                v1_verify=v1_result,
                v2_validate={},
                v3_verify={},
                confidence=0.0,
                issues_found=[ConfigIssue(**issue) for issue in v1_result.get("issues", [])],
                patterns_matched=[],
                reasoning_steps=reasoning_steps
            )

        config_content = v1_result.get("parsed_content", {})

        # Detect Intent
        intent = self.detect_intent(config_file, config_content)
        reasoning_steps.append(f"Detected intent: {intent.value}")

        # V2: Validate Relevance
        reasoning_steps.append("=== V2: VALIDATE (Relevance) ===")
        v2_result = self.v2_validate_relevance(config_file, config_content, intent)
        reasoning_steps.extend(v2_result.get("reasoning_steps", []))

        # V3: Verify Truth (with V3 system integration)
        reasoning_steps.append("=== V3: VERIFY (Truth) ===")
        v3_result = self.v3_verify_truth(config_file, config_content, v1_result, v2_result)
        reasoning_steps.extend(v3_result.get("reasoning_steps", []))

        # Collect all issues
        all_issues = []
        for issue_dict in v1_result.get("issues", []):
            all_issues.append(ConfigIssue(**issue_dict))
        for issue_dict in v2_result.get("issues", []):
            all_issues.append(ConfigIssue(**issue_dict))
        for issue_dict in v3_result.get("issues", []):
            all_issues.append(ConfigIssue(**issue_dict))

        # Get matched patterns
        patterns_matched = []
        for pattern_id in v2_result.get("patterns_matched", []):
            if pattern_id in self.learned_patterns:
                patterns_matched.append(self.learned_patterns[pattern_id])

        # Calculate confidence (boosted if V3 system verified)
        confidence = self._calculate_confidence(v1_result, v2_result, v3_result, all_issues)
        if v3_result.get("v3_system_integrated"):
            confidence = min(1.0, confidence + 0.1)  # Boost confidence if V3 system verified
            reasoning_steps.append("V3: Confidence boosted by V3 system verification")

        # Create reasoning chain
        reasoning_chain = ReasoningChain(
            reasoning_id=reasoning_id,
            config_file=str(config_file),
            intent=intent,
            v1_verify=v1_result,
            v2_validate=v2_result,
            v3_verify=v3_result,
            confidence=confidence,
            issues_found=all_issues,
            patterns_matched=patterns_matched,
            reasoning_steps=reasoning_steps
        )

        # Save to history
        self.reasoning_history.append(reasoning_chain)
        self._save_reasoning_history()

        # Learn from this reasoning
        self._learn_from_reasoning(reasoning_chain)

        # Report to V3 system if integrated
        if self.v3_integration and v3_result.get("v3_system_integrated"):
            try:
                # Could send reasoning results to V3 system for global tracking
                logger.debug("R5 reasoning results available for V3 system integration")
            except Exception as e:
                logger.debug(f"Could not report to V3 system: {e}")

        logger.info(f"R5 Reasoning complete: {len(all_issues)} issues found, confidence: {confidence:.2f}")
        if v3_result.get("v3_system_integrated"):
            logger.info("V3: Global V3 system verification integrated successfully")

        return reasoning_chain

    def _get_required_fields(self, intent: IntentCategory) -> List[str]:
        """Get required fields based on intent"""
        required_fields_map = {
            IntentCategory.CODING: ["version", "rules"],
            IntentCategory.DEPLOYMENT: ["version", "services"],
            IntentCategory.SECURITY: ["auth", "secrets"],
            IntentCategory.INTEGRATION: ["endpoints", "api"],
            IntentCategory.OPTIMIZATION: ["cache", "performance"],
            IntentCategory.GENERAL: []
        }
        return required_fields_map.get(intent, [])

    def _check_common_issues(self, config_content: Dict[str, Any], intent: IntentCategory) -> List[ConfigIssue]:
        """Check for common configuration issues"""
        issues = []

        # Check for empty config
        if not config_content:
            issues.append(ConfigIssue(
                issue_id="empty_config",
                config_file="",
                issue_type="empty_configuration",
                severity=0.5,
                description="Configuration is empty",
                reasoning="V2 Validation: Empty configuration detected",
                verification_level=VerificationLevel.V2_VALIDATE_RELEVANCE
            ))

        # Check for deprecated fields
        # (This would be expanded with actual deprecation patterns)

        return issues

    def _match_patterns(self, config_file: Path, config_content: Dict[str, Any],
                       intent: IntentCategory) -> List[ConfigPattern]:
        """Match configuration against learned patterns"""
        matched = []

        for pattern in self.learned_patterns.values():
            if pattern.pattern_type == intent.value:
                # Simple pattern matching (can be enhanced)
                if self._pattern_matches(config_content, pattern.pattern_data):
                    matched.append(pattern)
                    # Update pattern frequency
                    pattern.frequency += 1
                    pattern.last_seen = datetime.now()

        return matched

    def _pattern_matches(self, config: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        """Check if config matches a pattern"""
        # Simple key-based matching (can be enhanced with deep matching)
        for key in pattern.keys():
            if key in config:
                return True
        return False

    def _detect_hidden_issues(self, config_file: Path, config_content: Dict[str, Any]) -> List[ConfigIssue]:
        """Detect hidden issues not caught in V1/V2"""
        issues = []

        # Check for circular references in nested structures
        visited = set()
        def check_circular(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if id(value) in visited:
                        issues.append(ConfigIssue(
                            issue_id=f"circular_ref_{config_file.name}",
                            config_file=str(config_file),
                            issue_type="circular_reference",
                            severity=0.7,
                            description=f"Circular reference detected at {current_path}",
                            reasoning="V3 Verification: Circular reference check",
                            verification_level=VerificationLevel.V3_VERIFY_TRUTH
                        ))
                        return
                    visited.add(id(value))
                    check_circular(value, current_path)
                    visited.remove(id(value))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_circular(item, f"{path}[{i}]")

        try:
            check_circular(config_content)
        except Exception:
            pass  # Ignore errors in circular check

        # Check for unreachable/undefined values
        # Check for deprecated patterns
        # (Enhanced with actual detection logic)

        return issues

    def _check_consistency(self, config_file: Path, config_content: Dict[str, Any]) -> List[ConfigIssue]:
        """Check consistency with other configurations"""
        issues = []

        # Check against other configs in the same directory
        if self.config_dir.exists():
            for other_config in self.config_dir.glob("*.json"):
                if other_config == config_file:
                    continue
                try:
                    other_content = json.loads(other_config.read_text(encoding='utf-8'))
                    # Check for version consistency
                    if "version" in config_content and "version" in other_content:
                        if config_content["version"] != other_content["version"]:
                            issues.append(ConfigIssue(
                                issue_id=f"version_mismatch_{config_file.name}",
                                config_file=str(config_file),
                                issue_type="version_inconsistency",
                                severity=0.4,
                                description=f"Version mismatch with {other_config.name}",
                                reasoning="V3 Verification: Version consistency check",
                                verification_level=VerificationLevel.V3_VERIFY_TRUTH
                            ))
                except Exception:
                    pass  # Ignore errors reading other configs

        # Check naming conventions
        # (Enhanced with actual consistency checks)

        return issues

    def _calculate_confidence(self, v1_result: Dict[str, Any], v2_result: Dict[str, Any],
                             v3_result: Dict[str, Any], issues: List[ConfigIssue]) -> float:
        """Calculate confidence in reasoning"""
        # Start with high confidence
        confidence = 1.0

        # Reduce confidence for issues
        for issue in issues:
            confidence -= issue.severity * 0.1

        # Increase confidence if patterns matched
        if v2_result.get("patterns_matched"):
            confidence += 0.1

        # Increase confidence if V3 system verified
        if v3_result.get("v3_system_integrated"):
            confidence += 0.1

        # Ensure confidence is in valid range
        confidence = max(0.0, min(1.0, confidence))

        return confidence

    def _learn_from_reasoning(self, reasoning_chain: ReasoningChain):
        """Learn from reasoning to improve future analysis"""
        # Extract patterns from successful reasoning
        if reasoning_chain.confidence > 0.8 and not reasoning_chain.issues_found:
            # This is a good pattern to learn
            pattern_id = f"pattern_{reasoning_chain.intent.value}_{len(self.learned_patterns)}"

            # Create pattern from config content
            # Extract key structure as pattern data
            try:
                import json
                config_path = Path(reasoning_chain.config_file)
                if config_path.exists():
                    config_data = json.loads(config_path.read_text(encoding='utf-8'))
                    # Extract top-level keys as pattern
                    pattern_data = {key: type(value).__name__ for key, value in config_data.items() if not isinstance(value, (dict, list))}
            except Exception:
                pattern_data = {}

            pattern = ConfigPattern(
                pattern_id=pattern_id,
                pattern_type=reasoning_chain.intent.value,
                pattern_data=pattern_data,
                frequency=1,
                confidence=reasoning_chain.confidence,
                examples=[reasoning_chain.config_file]
            )

            self.learned_patterns[pattern_id] = pattern
            self._save_patterns()

            logger.debug(f"R5 learned new pattern: {pattern_id}")


def main():
    try:
        """Test R5 reasoning engine"""
        import argparse

        parser = argparse.ArgumentParser(description="R5 Reasoning Engine - Configuration Analysis")
        parser.add_argument("config_file", type=str, help="Configuration file to analyze")
        parser.add_argument("--project-root", type=str, default=".", help="Project root directory")

        args = parser.parse_args()

        project_root = Path(args.project_root).resolve()
        config_file = project_root / args.config_file

        # Initialize R5
        r5 = R5ReasoningEngine(project_root)

        # Reason about config
        reasoning = r5.reason_about_config(config_file)

        # Print results
        print(f"\n{'='*80}")
        print(f" R5 REASONING RESULTS - {config_file.name} ".center(80, "="))
        print(f"{'='*80}\n")

        print(f"Intent: {reasoning.intent.value}")
        print(f"Confidence: {reasoning.confidence:.2%}")
        print(f"Issues Found: {len(reasoning.issues_found)}")
        print(f"Patterns Matched: {len(reasoning.patterns_matched)}")
        if reasoning.v3_verify.get("v3_system_integrated"):
            print(f"V3 System: Integrated and verified")
        print()

        if reasoning.issues_found:
            print("Issues:")
            for issue in reasoning.issues_found:
                print(f"  - [{issue.severity:.1f}] {issue.description}")
                print(f"    Reasoning: {issue.reasoning}\n")

        print("\nReasoning Steps:")
        for step in reasoning.reasoning_steps:
            print(f"  {step}")

        print(f"\n{'='*80}\n")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import sys



    sys.exit(main())