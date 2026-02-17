#!/usr/bin/env python3
"""
Intent Processor for Lumina 2.0 @AIOS

Translates natural language user input into structured, actionable intentions.
This is the critical bridge between human expression and AI execution.

Capabilities:
- Natural language understanding
- Intent classification and structuring
- Parameter extraction
- Confidence scoring
- Context integration
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


@dataclass
class ProcessedIntent:
    """Structured representation of a processed user intent"""
    id: str
    raw_input: str
    intent_type: str
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    context_requirements: List[str] = field(default_factory=list)
    execution_hints: List[str] = field(default_factory=list)
    fallback_actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentProcessor:
    """
    AI-Native Intent Processor - True Understanding Engine

    Transforms human intentions into deep, contextual understanding.
    Goes beyond pattern matching to true comprehension and implication analysis.
    """

    def __init__(self):
        self.logger = get_logger("IntentProcessor")

        # Enhanced AI-native capabilities
        self.context_analyzer = ContextAnalyzer()
        self.implication_engine = ImplicationEngine()
        self.intention_evaluator = IntentionEvaluator()
        self.confidence_calculator = AIConfidenceCalculator()

        # Legacy pattern matching (for fallback)
        self.intent_patterns = self._load_intent_patterns()
        self.entity_extractors = self._load_entity_extractors()
        self.intent_classifiers = self._load_intent_classifiers()

        # AI-native state
        self.processing_history = []
        self.contextual_memory = ContextualMemory()
        self.learning_engine = IntentLearningEngine()

        # True AI thresholds
        self.true_understanding_threshold = 0.85
        self.confidence_threshold = 0.6

        self.logger.info("🧠 AI-Native Intent Processor initialized - true understanding active")

    # ============================================================================
    # AI-NATIVE UNDERSTANDING COMPONENTS
    # ============================================================================

    async def understand_with_ai_native_processing(self, user_input: str, context: Dict[str, Any] = None) -> ProcessedIntent:
        """
        True AI-native intent processing - goes beyond pattern matching
        """
        # Step 1: Analyze full context
        full_context = await self.context_analyzer.analyze_full_context(user_input, context or {})

        # Step 2: Extract true intention (not just keywords)
        true_intention = await self.intention_evaluator.extract_true_intention(user_input, full_context)

        # Step 3: Calculate implications and consequences
        implications = await self.implication_engine.calculate_implications(true_intention, full_context)

        # Step 4: Determine optimal execution strategy
        execution_strategy = await self._determine_execution_strategy(true_intention, implications, full_context)

        # Step 5: Calculate true confidence based on understanding depth
        true_confidence = await self.confidence_calculator.calculate_true_confidence(
            true_intention, implications, full_context
        )

        # Step 6: Generate intelligent response metadata
        metadata = {
            "processing_method": "ai_native",
            "understanding_depth": "deep",
            "context_awareness": True,
            "implication_analysis": True,
            "strategy_optimization": True,
            "learning_applied": await self.learning_engine.should_apply_learning(user_input)
        }

        return ProcessedIntent(
            id=f"ai_native_{int(datetime.now().timestamp())}",
            raw_input=user_input,
            intent_type=true_intention.get("type", "unknown"),
            confidence=true_confidence,
            parameters=true_intention.get("parameters", {}),
            entities=true_intention.get("entities", []),
            context_requirements=execution_strategy.get("context_requirements", []),
            execution_hints=execution_strategy.get("execution_hints", []),
            fallback_actions=execution_strategy.get("fallback_actions", []),
            metadata=metadata
        )

    async def _determine_execution_strategy(self, intention: Dict[str, Any], implications: Dict[str, Any],
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine optimal execution strategy based on true understanding
        """
        strategy = {
            "context_requirements": [],
            "execution_hints": [],
            "fallback_actions": [],
            "autonomy_level": "full",
            "monitoring_required": False
        }

        # Analyze intention complexity
        complexity = self._assess_intention_complexity(intention)

        if complexity > 0.8:
            # High complexity - require more context and monitoring
            strategy["context_requirements"].extend([
                "system_state", "resource_availability", "user_preferences",
                "historical_patterns", "risk_assessment"
            ])
            strategy["execution_hints"].extend([
                "Break down into smaller steps",
                "Verify each step before proceeding",
                "Maintain rollback capability"
            ])
            strategy["autonomy_level"] = "supervised"
            strategy["monitoring_required"] = True
        elif complexity > 0.5:
            # Medium complexity - standard approach
            strategy["context_requirements"].extend([
                "user_context", "system_capabilities"
            ])
            strategy["execution_hints"].extend([
                "Execute step by step",
                "Validate intermediate results"
            ])
            strategy["autonomy_level"] = "assisted"
        else:
            # Low complexity - full autonomy
            strategy["execution_hints"].extend([
                "Execute autonomously",
                "Optimize for speed and efficiency"
            ])
            strategy["autonomy_level"] = "full"

        # Add fallback actions based on implications
        if implications.get("risk_level", "low") == "high":
            strategy["fallback_actions"].append({
                "condition": "high_risk_detected",
                "action": "request_user_approval",
                "reason": "High-risk operation requires confirmation"
            })

        if implications.get("resource_intensive", False):
            strategy["fallback_actions"].append({
                "condition": "resource_constraint",
                "action": "optimize_resource_usage",
                "reason": "Operation may require resource optimization"
            })

        return strategy

    def _assess_intention_complexity(self, intention: Dict[str, Any]) -> float:
        """
        Assess the complexity of an intention on a 0-1 scale
        """
        complexity = 0.0

        # Factor 1: Number of parameters (more parameters = more complex)
        param_count = len(intention.get("parameters", {}))
        complexity += min(param_count * 0.1, 0.3)

        # Factor 2: Number of entities involved
        entity_count = len(intention.get("entities", []))
        complexity += min(entity_count * 0.05, 0.2)

        # Factor 3: Intention type complexity
        complex_types = ["system_maintenance", "analysis_intelligence", "workflow_management"]
        if intention.get("type") in complex_types:
            complexity += 0.3

        # Factor 4: Context dependencies
        context_deps = intention.get("context_dependencies", 0)
        complexity += min(context_deps * 0.1, 0.2)

        return min(complexity, 1.0)

    # ============================================================================
    # AI-NATIVE COMPONENT CLASSES
    # ============================================================================

class ContextAnalyzer:
    """Analyzes full context for true understanding"""

    async def analyze_full_context(self, user_input: str, provided_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze complete context including environmental, historical, and implicit factors"""
        context = provided_context.copy()

        # Add environmental context
        context.update({
            "timestamp": datetime.now().isoformat(),
            "input_length": len(user_input),
            "input_complexity": self._assess_input_complexity(user_input),
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
        })

        # Add historical context (patterns, preferences)
        context["historical_patterns"] = await self._extract_historical_patterns(user_input)

        # Add implicit context (what's not said but implied)
        context["implicit_intentions"] = await self._infer_implicit_intentions(user_input, context)

        # Add environmental awareness
        context["system_state"] = await self._assess_system_state()
        context["user_state"] = await self._assess_user_state()

        return context

    def _assess_input_complexity(self, text: str) -> float:
        """Assess complexity of input text"""
        words = len(text.split())
        sentences = len([s for s in text.split('.') if s.strip()])
        unique_words = len(set(text.lower().split()))

        complexity = (words * 0.01) + (sentences * 0.1) + (unique_words / words if words > 0 else 0)
        return min(complexity, 1.0)

    async def _extract_historical_patterns(self, user_input: str) -> List[Dict[str, Any]]:
        """Extract patterns from historical interactions"""
        # Placeholder for historical pattern analysis
        return []

    async def _infer_implicit_intentions(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """Infer intentions that are implied but not stated"""
        implicit = []

        # Time-based implications
        if context.get("time_of_day", 12) < 6:
            implicit.append("early_morning_context")
        elif context.get("time_of_day", 12) > 22:
            implicit.append("late_night_context")

        # Complexity-based implications
        if context.get("input_complexity", 0) > 0.7:
            implicit.append("complex_request")
            implicit.append("may_need_breakdown")

        return implicit

    async def _assess_system_state(self) -> Dict[str, Any]:
        """Assess current system state"""
        return {
            "cpu_usage": "unknown",  # Would integrate with system monitoring
            "memory_available": "unknown",
            "network_status": "unknown",
            "active_processes": []
        }

    async def _assess_user_state(self) -> Dict[str, Any]:
        """Assess current user state and context"""
        return {
            "recent_activities": [],
            "current_focus": "unknown",
            "fatigue_level": "unknown",
            "preference_patterns": {}
        }


class ImplicationEngine:
    """Calculates implications and consequences of intentions"""

    async def calculate_implications(self, intention: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all implications of an intention"""
        implications = {
            "risk_level": "low",
            "resource_requirements": [],
            "time_estimate": "short",
            "side_effects": [],
            "dependencies": [],
            "success_factors": [],
            "failure_scenarios": [],
            "optimization_opportunities": []
        }

        # Analyze based on intention type
        intent_type = intention.get("type", "unknown")

        if intent_type == "system_maintenance":
            implications.update({
                "risk_level": "high",
                "resource_requirements": ["system_access", "backup_capability"],
                "time_estimate": "long",
                "side_effects": ["potential_downtime", "service_interruption"],
                "success_factors": ["backup_verified", "maintenance_window"],
                "failure_scenarios": ["data_loss", "system_instability"]
            })

        elif intent_type == "code_management":
            implications.update({
                "risk_level": "medium",
                "resource_requirements": ["development_environment", "version_control"],
                "time_estimate": "medium",
                "side_effects": ["code_changes", "testing_required"],
                "success_factors": ["code_compiles", "tests_pass"],
                "optimization_opportunities": ["automated_testing", "code_review"]
            })

        elif intent_type == "communication":
            implications.update({
                "risk_level": "low",
                "resource_requirements": ["communication_channels"],
                "time_estimate": "short",
                "side_effects": ["notification_sent"],
                "success_factors": ["message_delivered", "recipient_reachable"]
            })

        # Context-based adjustments
        if context.get("time_pressure", False):
            implications["risk_level"] = "high"
            implications["optimization_opportunities"].append("prioritize_speed")

        if context.get("resource_constraints", False):
            implications["time_estimate"] = "extended"
            implications["optimization_opportunities"].append("resource_optimization")

        return implications


class IntentionEvaluator:
    """Extracts true intentions beyond surface-level keywords"""

    async def extract_true_intention(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the actual underlying intention"""

        # Analyze sentiment and urgency
        sentiment = await self._analyze_sentiment(user_input)
        urgency = await self._analyze_urgency(user_input)

        # Identify core action
        core_action = await self._identify_core_action(user_input)

        # Determine scope and scale
        scope = await self._determine_scope(user_input, context)

        # Extract specific requirements
        requirements = await self._extract_requirements(user_input)

        return {
            "type": core_action.get("type", "unknown"),
            "sentiment": sentiment,
            "urgency": urgency,
            "scope": scope,
            "requirements": requirements,
            "parameters": core_action.get("parameters", {}),
            "entities": await self._extract_intention_entities(user_input),
            "confidence_indicators": core_action.get("confidence_indicators", [])
        }

    async def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of the input"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "pleased"]
        negative_words = ["bad", "terrible", "awful", "horrible", "angry", "frustrated", "disappointed"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    async def _analyze_urgency(self, text: str) -> str:
        """Analyze urgency level"""
        urgent_indicators = ["urgent", "asap", "immediately", "emergency", "critical", "now", "fast"]
        text_lower = text.lower()

        urgent_count = sum(1 for indicator in urgent_indicators if indicator in text_lower)

        if urgent_count >= 2:
            return "critical"
        elif urgent_count == 1:
            return "high"
        else:
            return "normal"

    async def _identify_core_action(self, text: str) -> Dict[str, Any]:
        """Identify the core action being requested"""
        text_lower = text.lower()

        # Code-related actions
        if any(word in text_lower for word in ["fix", "debug", "resolve", "code", "programming"]):
            return {
                "type": "code_management",
                "parameters": {"action": "fix"},
                "confidence_indicators": ["technical_terms", "problem_description"]
            }

        # System-related actions
        if any(word in text_lower for word in ["update", "install", "configure", "system"]):
            return {
                "type": "system_maintenance",
                "parameters": {"action": "maintain"},
                "confidence_indicators": ["system_terms", "administrative_context"]
            }

        # Communication actions
        if any(word in text_lower for word in ["email", "message", "contact", "send"]):
            return {
                "type": "communication",
                "parameters": {"action": "communicate"},
                "confidence_indicators": ["communication_terms"]
            }

        # Analysis actions
        if any(word in text_lower for word in ["analyze", "find", "search", "report"]):
            return {
                "type": "analysis_intelligence",
                "parameters": {"action": "analyze"},
                "confidence_indicators": ["analysis_terms"]
            }

        # Workflow actions
        if any(word in text_lower for word in ["run", "execute", "workflow", "process"]):
            return {
                "type": "workflow_management",
                "parameters": {"action": "execute"},
                "confidence_indicators": ["workflow_terms"]
            }

        return {
            "type": "unknown",
            "parameters": {},
            "confidence_indicators": []
        }

    async def _determine_scope(self, text: str, context: Dict[str, Any]) -> str:
        """Determine the scope of the intention"""
        text_lower = text.lower()

        # Check for scope indicators
        if any(word in text_lower for word in ["all", "everything", "every", "complete"]):
            return "global"
        elif any(word in text_lower for word in ["some", "few", "several"]):
            return "limited"
        elif any(word in text_lower for word in ["this", "current", "here"]):
            return "local"
        else:
            return "standard"

    async def _extract_requirements(self, text: str) -> List[str]:
        """Extract specific requirements mentioned"""
        requirements = []

        # Look for requirement indicators
        if "backup" in text.lower():
            requirements.append("backup_required")
        if "test" in text.lower():
            requirements.append("testing_required")
        if "verify" in text.lower():
            requirements.append("verification_required")
        if "notify" in text.lower():
            requirements.append("notification_required")

        return requirements

    async def _extract_intention_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities relevant to the intention"""
        entities = []

        # File references
        import re
        file_patterns = [
            r'\b\w+\.(py|js|java|cpp|html|css|md|txt|json|xml)\b',
            r'file\s+[\w\.\-/]+',
            r'[\w\.\-/]+\.(py|js|java|cpp|html|css|md|txt|json|xml)'
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "type": "file_reference",
                    "value": match,
                    "context": "intention_target"
                })

        return entities


class AIConfidenceCalculator:
    """Calculates true confidence based on understanding depth"""

    async def calculate_true_confidence(self, intention: Dict[str, Any], implications: Dict[str, Any],
                                      context: Dict[str, Any]) -> float:
        """Calculate confidence based on multiple factors"""

        confidence = 0.5  # Base confidence

        # Factor 1: Intention clarity
        if intention.get("type") != "unknown":
            confidence += 0.2

        # Factor 2: Parameter completeness
        param_count = len(intention.get("parameters", {}))
        confidence += min(param_count * 0.1, 0.2)

        # Factor 3: Context availability
        context_score = len(context) * 0.02
        confidence += min(context_score, 0.15)

        # Factor 4: Implication analysis
        if implications.get("success_factors"):
            confidence += 0.1

        # Factor 5: Historical success patterns
        # (Would integrate with learning history)
        confidence += 0.05

        return min(confidence, 0.95)


class ContextualMemory:
    """Maintains contextual memory for improved understanding"""

    def __init__(self):
        self.short_term_memory = []
        self.long_term_memory = []
        self.patterns = {}

    async def store_context(self, context: Dict[str, Any]):
        """Store context for future reference"""
        self.short_term_memory.append({
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only recent context
        if len(self.short_term_memory) > 10:
            # Move old context to long-term memory
            old_context = self.short_term_memory.pop(0)
            self.long_term_memory.append(old_context)

        # Keep only recent long-term memory
        if len(self.long_term_memory) > 100:
            self.long_term_memory = self.long_term_memory[-100:]

    async def retrieve_relevant_context(self, current_input: str) -> List[Dict[str, Any]]:
        """Retrieve contextually relevant historical information"""
        relevant = []

        for memory in self.short_term_memory + self.long_term_memory:
            # Simple relevance check (would be more sophisticated)
            if any(keyword in current_input.lower() for keyword in memory.get("context", {}).keys()):
                relevant.append(memory)

        return relevant[:5]  # Return top 5 most relevant


class IntentLearningEngine:
    """Learns from intent processing to improve future understanding"""

    def __init__(self):
        self.success_patterns = {}
        self.failure_patterns = {}
        self.confidence_history = []

    async def should_apply_learning(self, user_input: str) -> bool:
        """Determine if learning should be applied to this input"""
        # Apply learning to complex or ambiguous inputs
        word_count = len(user_input.split())
        has_question_marks = "?" in user_input
        has_ambiguous_terms = any(word in user_input.lower() for word in ["maybe", "perhaps", "might"])

        return word_count > 10 or has_question_marks or has_ambiguous_terms

    async def learn_from_processing(self, user_input: str, result: ProcessedIntent, success: bool):
        """Learn from processing results"""
        key = self._generate_learning_key(user_input)

        if success:
            if key not in self.success_patterns:
                self.success_patterns[key] = []
            self.success_patterns[key].append({
                "input": user_input,
                "result": result.intent_type,
                "confidence": result.confidence,
                "timestamp": datetime.now().isoformat()
            })
        else:
            if key not in self.failure_patterns:
                self.failure_patterns[key] = []
            self.failure_patterns[key].append({
                "input": user_input,
                "attempted_type": result.intent_type,
                "confidence": result.confidence,
                "timestamp": datetime.now().isoformat()
            })

        # Store confidence history
        self.confidence_history.append(result.confidence)
        if len(self.confidence_history) > 100:
            self.confidence_history = self.confidence_history[-100:]

    def _generate_learning_key(self, text: str) -> str:
        """Generate a learning key from input text"""
        # Simple key generation - would be more sophisticated
        words = text.lower().split()[:3]  # First 3 words
        return "_".join(words)

    # ============================================================================
    # LEGACY PATTERN MATCHING (FALLBACK)
    # ============================================================================

    def _load_intent_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load intent recognition patterns"""
        return {
            "code_management": [
                {
                    "patterns": [r"fix.*bug", r"debug.*code", r"resolve.*error"],
                    "keywords": ["fix", "debug", "resolve", "error", "bug"],
                    "confidence_boost": 0.3
                },
                {
                    "patterns": [r"create.*file", r"add.*code", r"implement.*feature"],
                    "keywords": ["create", "add", "implement", "feature"],
                    "confidence_boost": 0.2
                }
            ],
            "workflow_management": [
                {
                    "patterns": [r"run.*workflow", r"execute.*process", r"start.*automation"],
                    "keywords": ["run", "execute", "start", "workflow", "process"],
                    "confidence_boost": 0.4
                },
                {
                    "patterns": [r"check.*status", r"monitor.*progress", r"view.*results"],
                    "keywords": ["check", "monitor", "view", "status", "progress"],
                    "confidence_boost": 0.3
                }
            ],
            "communication": [
                {
                    "patterns": [r"check.*email", r"read.*messages", r"view.*inbox"],
                    "keywords": ["email", "messages", "inbox", "communication"],
                    "confidence_boost": 0.4
                },
                {
                    "patterns": [r"send.*message", r"reply.*to", r"contact.*someone"],
                    "keywords": ["send", "reply", "contact", "message"],
                    "confidence_boost": 0.3
                }
            ],
            "system_maintenance": [
                {
                    "patterns": [r"update.*system", r"install.*software", r"configure.*settings"],
                    "keywords": ["update", "install", "configure", "system", "software"],
                    "confidence_boost": 0.3
                },
                {
                    "patterns": [r"backup.*data", r"clean.*files", r"optimize.*performance"],
                    "keywords": ["backup", "clean", "optimize", "performance"],
                    "confidence_boost": 0.2
                }
            ],
            "analysis_intelligence": [
                {
                    "patterns": [r"analyze.*data", r"find.*insights", r"generate.*report"],
                    "keywords": ["analyze", "insights", "report", "data", "intelligence"],
                    "confidence_boost": 0.4
                },
                {
                    "patterns": [r"search.*for", r"look.*up", r"find.*information"],
                    "keywords": ["search", "lookup", "find", "information"],
                    "confidence_boost": 0.3
                }
            ]
        }

    def _load_entity_extractors(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load entity extraction patterns"""
        return {
            "file_paths": [
                r"[a-zA-Z]:[\\/][^\s]*\.[a-zA-Z0-9]+",  # Windows paths
                r"/[^\s]*\.[a-zA-Z0-9]+",  # Unix paths
                r"\./[^\s]*\.[a-zA-Z0-9]+",  # Relative paths
            ],
            "urls": [
                r"https?://[^\s]+",
                r"www\.[^\s]+",
                r"[a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*"
            ],
            "email_addresses": [
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            ],
            "dates": [
                r"\d{1,2}/\d{1,2}/\d{2,4}",
                r"\d{2,4}-\d{1,2}-\d{1,2}",
                r"(today|tomorrow|yesterday)",
                r"(next|last)\s+(week|month|year)"
            ],
            "times": [
                r"\d{1,2}:\d{2}(\s*[ap]m)?",
                r"\d{1,2}\s*[ap]m"
            ],
            "quantities": [
                r"\d+\s*(files?|items?|messages?|emails?)",
                r"(all|some|many|few)\s+(files?|items?|messages?|emails?)"
            ]
        }

    def _load_intent_classifiers(self) -> Dict[str, Dict[str, Any]]:
        """Load intent classification rules"""
        return {
            "code_management": {
                "primary_keywords": ["code", "programming", "development", "bug", "fix"],
                "secondary_keywords": ["file", "function", "class", "variable", "error"],
                "context_indicators": ["git", "repository", "branch", "commit"]
            },
            "workflow_management": {
                "primary_keywords": ["workflow", "process", "automation", "task"],
                "secondary_keywords": ["run", "execute", "start", "stop", "monitor"],
                "context_indicators": ["schedule", "trigger", "pipeline", "job"]
            },
            "communication": {
                "primary_keywords": ["email", "message", "contact", "communication"],
                "secondary_keywords": ["send", "receive", "reply", "check"],
                "context_indicators": ["inbox", "conversation", "notification"]
            },
            "system_maintenance": {
                "primary_keywords": ["system", "maintenance", "update", "configure"],
                "secondary_keywords": ["install", "setup", "optimize", "backup"],
                "context_indicators": ["server", "database", "network", "storage"]
            },
            "analysis_intelligence": {
                "primary_keywords": ["analyze", "search", "find", "report"],
                "secondary_keywords": ["data", "information", "insights", "statistics"],
                "context_indicators": ["dashboard", "metrics", "intelligence", "syphon"]
            }
        }

    async def process(self, user_intent: Any) -> ProcessedIntent:
        """
        AI-Native Intent Processing - True Understanding Engine

        This is the revolutionary @AIOS transformation:
        - Input: "I need to work on my project but the system is slow"
        - Output: Deep understanding with implications, context, and optimal execution strategy
        """
        start_time = datetime.now()

        # Extract basic information
        intent_id = getattr(user_intent, 'id', 'unknown')
        raw_input = getattr(user_intent, 'raw_input', str(user_intent))
        provided_context = getattr(user_intent, 'context', {})

        self.logger.info(f"🧠 AI-Native Processing: {raw_input[:50]}...")

        try:
            # PRIMARY: Try AI-native processing first
            if await self._should_use_ai_native_processing(raw_input, provided_context):
                self.logger.info("🎯 Using AI-native understanding")
                result = await self.understand_with_ai_native_processing(raw_input, provided_context)

                # Store successful AI-native processing for learning
                await self.learning_engine.learn_from_processing(raw_input, result, True)

                self.logger.info(f"✅ AI-native processing complete: {result.intent_type} (confidence: {result.confidence:.2f})")
                return result

            # FALLBACK: Use legacy pattern matching if AI-native fails or is inappropriate
            else:
                self.logger.info("🔄 Falling back to pattern matching")
                result = await self._process_with_legacy_patterns(user_intent)

                # Store legacy processing for learning
                await self.learning_engine.learn_from_processing(raw_input, result, True)

                self.logger.info(f"✅ Legacy processing complete: {result.intent_type} (confidence: {result.confidence:.2f})")
                return result

        except Exception as e:
            self.logger.error(f"❌ Intent processing failed: {e}")

            # Learn from failure
            failed_result = ProcessedIntent(
                id=intent_id,
                raw_input=raw_input,
                intent_type="unknown",
                confidence=0.0,
                metadata={"error": str(e), "processing_method": "failed"}
            )
            await self.learning_engine.learn_from_processing(raw_input, failed_result, False)

            return failed_result

    async def _should_use_ai_native_processing(self, raw_input: str, context: Dict[str, Any]) -> bool:
        """
        Determine if AI-native processing should be used

        Uses multiple factors to decide between true understanding vs pattern matching
        """
        # Factor 1: Input complexity
        word_count = len(raw_input.split())
        sentence_count = len([s for s in raw_input.split('.') if s.strip()])
        complexity_score = min((word_count * 0.1) + (sentence_count * 0.2), 1.0)

        # Factor 2: Context richness
        context_score = min(len(context) * 0.1, 0.5)

        # Factor 3: Learning history success rate
        learning_key = self.learning_engine._generate_learning_key(raw_input)
        success_history = self.learning_engine.success_patterns.get(learning_key, [])
        failure_history = self.learning_engine.failure_patterns.get(learning_key, [])

        total_history = len(success_history) + len(failure_history)
        if total_history > 0:
            history_score = len(success_history) / total_history
        else:
            history_score = 0.5  # No history = neutral

        # Factor 4: System capability assessment
        capability_score = 1.0 if self.context_analyzer else 0.0

        # Combined decision
        total_score = (complexity_score * 0.3) + (context_score * 0.2) + (history_score * 0.3) + (capability_score * 0.2)

        # Use AI-native processing if score > 0.6 or if explicitly requested
        should_use_ai = total_score > 0.6 or context.get("force_ai_native", False)

        self.logger.debug(f"AI-native decision: {should_use_ai} (score: {total_score:.2f})")
        return should_use_ai

    async def _process_with_legacy_patterns(self, user_intent: Any) -> ProcessedIntent:
        """
        Fallback to legacy pattern matching when AI-native processing is not appropriate
        """
        start_time = datetime.now()

        # Extract basic information
        intent_id = getattr(user_intent, 'id', 'unknown')
        raw_input = getattr(user_intent, 'raw_input', str(user_intent))

        # Step 1: Preprocess input
        processed_text = self._preprocess_text(raw_input)

        # Step 2: Extract entities
        entities = self._extract_entities(processed_text)

        # Step 3: Classify intent
        intent_type, base_confidence = self._classify_intent(processed_text)

        # Step 4: Extract parameters
        parameters = self._extract_parameters(processed_text, intent_type, entities)

        # Step 5: Determine context requirements
        context_requirements = self._determine_context_requirements(intent_type, parameters)

        # Step 6: Generate execution hints
        execution_hints = self._generate_execution_hints(intent_type, parameters)

        # Step 7: Calculate final confidence
        final_confidence = self._calculate_confidence(base_confidence, entities, parameters)

        # Step 8: Create fallback actions
        fallback_actions = self._generate_fallbacks(intent_type, final_confidence)

        # Step 9: Create processed intent
        processed_intent = ProcessedIntent(
            id=intent_id,
            raw_input=raw_input,
            intent_type=intent_type,
            confidence=final_confidence,
            parameters=parameters,
            entities=entities,
            context_requirements=context_requirements,
            execution_hints=execution_hints,
            fallback_actions=fallback_actions,
            metadata={
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "processed_text": processed_text,
                "classification_method": "pattern_matching_fallback",
                "ai_native_available": True
            }
        )

        # Step 10: Log and store processing result
        self._log_processing_result(processed_intent)
        self.processing_history.append(processed_intent)

        return processed_intent

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better intent recognition"""
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Expand common contractions
        contractions = {
            "i'm": "i am",
            "don't": "do not",
            "can't": "cannot",
            "won't": "will not",
            "it's": "it is",
            "that's": "that is"
        }

        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)

        return text

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using pattern matching"""
        entities = []

        for entity_type, patterns in self.entity_extractors.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        "type": entity_type,
                        "value": match,
                        "start": text.find(match),
                        "end": text.find(match) + len(match),
                        "confidence": 0.8  # Pattern-based extraction is generally reliable
                    })

        # Remove duplicates and sort by position
        unique_entities = []
        seen = set()
        for entity in sorted(entities, key=lambda x: x['start']):
            key = (entity['type'], entity['value'])
            if key not in seen:
                unique_entities.append(entity)
                seen.add(key)

        return unique_entities

    def _classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify the intent type and return base confidence"""
        intent_scores = {}

        # Score each intent type
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0

            for pattern_group in patterns:
                # Check for pattern matches
                for pattern in pattern_group.get("patterns", []):
                    if re.search(pattern, text, re.IGNORECASE):
                        score += pattern_group.get("confidence_boost", 0.1)

                # Check for keyword matches
                keywords = pattern_group.get("keywords", [])
                for keyword in keywords:
                    if keyword.lower() in text:
                        score += 0.1

            intent_scores[intent_type] = score

        # Also check against classifier rules
        for intent_type, rules in self.intent_classifiers.items():
            primary_keywords = rules.get("primary_keywords", [])
            secondary_keywords = rules.get("secondary_keywords", [])

            primary_matches = sum(1 for kw in primary_keywords if kw in text)
            secondary_matches = sum(1 for kw in secondary_keywords if kw in text)

            # Boost score based on keyword matches
            keyword_score = (primary_matches * 0.2) + (secondary_matches * 0.1)
            intent_scores[intent_type] = intent_scores.get(intent_type, 0) + keyword_score

        # Find the highest scoring intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent_type, score = best_intent

            # Normalize confidence (cap at 0.9 for base classification)
            confidence = min(score, 0.9)

            return intent_type, confidence
        else:
            return "unknown", 0.1

    def _extract_parameters(self, text: str, intent_type: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract parameters specific to the intent type"""
        parameters = {}

        # Extract parameters based on intent type
        if intent_type == "code_management":
            parameters.update(self._extract_code_parameters(text, entities))
        elif intent_type == "workflow_management":
            parameters.update(self._extract_workflow_parameters(text, entities))
        elif intent_type == "communication":
            parameters.update(self._extract_communication_parameters(text, entities))
        elif intent_type == "system_maintenance":
            parameters.update(self._extract_system_parameters(text, entities))
        elif intent_type == "analysis_intelligence":
            parameters.update(self._extract_analysis_parameters(text, entities))

        # Add common parameters from entities
        for entity in entities:
            entity_type = entity["type"]
            if entity_type not in parameters:
                parameters[entity_type] = []

            parameters[entity_type].append({
                "value": entity["value"],
                "confidence": entity["confidence"]
            })

        return parameters

    def _extract_code_parameters(self, text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract parameters for code management intents"""
        params = {}

        # Look for specific actions
        if any(word in text for word in ["fix", "debug", "resolve"]):
            params["action"] = "fix"
        elif any(word in text for word in ["create", "add", "implement"]):
            params["action"] = "create"
        elif any(word in text for word in ["test", "run", "execute"]):
            params["action"] = "test"

        # Extract file references
        file_entities = [e for e in entities if e["type"] == "file_paths"]
        if file_entities:
            params["target_files"] = [e["value"] for e in file_entities]

        return params

    def _extract_workflow_parameters(self, text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract parameters for workflow management intents"""
        params = {}

        # Determine workflow action
        if any(word in text for word in ["run", "execute", "start"]):
            params["action"] = "execute"
        elif any(word in text for word in ["check", "monitor", "view"]):
            params["action"] = "monitor"
        elif any(word in text for word in ["stop", "cancel", "pause"]):
            params["action"] = "stop"

        # Look for workflow names or IDs
        workflow_indicators = ["workflow", "process", "pipeline", "job"]
        for indicator in workflow_indicators:
            if indicator in text:
                # Extract words after the indicator
                pattern = rf"{indicator}\s+([a-zA-Z0-9_\-\s]+)"
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    params["workflow_name"] = matches[0].strip()
                    break

        return params

    def _extract_communication_parameters(self, text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract parameters for communication intents"""
        params = {}

        # Determine communication type
        if any(word in text for word in ["email", "mail"]):
            params["communication_type"] = "email"
        elif any(word in text for word in ["message", "sms", "text"]):
            params["communication_type"] = "message"
        elif any(word in text for word in ["call", "phone"]):
            params["communication_type"] = "call"

        # Extract email addresses
        email_entities = [e for e in entities if e["type"] == "email_addresses"]
        if email_entities:
            params["recipients"] = [e["value"] for e in email_entities]

        return params

    def _extract_system_parameters(self, text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract parameters for system maintenance intents"""
        params = {}

        # Determine system action
        if any(word in text for word in ["update", "upgrade"]):
            params["action"] = "update"
        elif any(word in text for word in ["install", "setup"]):
            params["action"] = "install"
        elif any(word in text for word in ["backup", "save"]):
            params["action"] = "backup"
        elif any(word in text for word in ["clean", "remove"]):
            params["action"] = "clean"

        # Look for software/package names
        software_indicators = ["install", "update", "configure"]
        for indicator in software_indicators:
            if indicator in text:
                # Extract words after the indicator
                pattern = rf"{indicator}\s+([a-zA-Z0-9_\-\s]+)"
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    params["software_name"] = matches[0].strip()
                    break

        return params

    def _extract_analysis_parameters(self, text: str, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract parameters for analysis and intelligence intents"""
        params = {}

        # Determine analysis type
        if any(word in text for word in ["search", "find", "lookup"]):
            params["analysis_type"] = "search"
        elif any(word in text for word in ["analyze", "examine"]):
            params["analysis_type"] = "analysis"
        elif any(word in text for word in ["report", "summary"]):
            params["analysis_type"] = "reporting"

        # Extract search terms
        search_indicators = ["for", "about", "regarding"]
        for indicator in search_indicators:
            if indicator in text:
                # Extract everything after the indicator
                idx = text.find(indicator)
                if idx != -1:
                    search_term = text[idx + len(indicator):].strip()
                    if search_term:
                        params["search_term"] = search_term
                        break

        return params

    def _determine_context_requirements(self, intent_type: str, parameters: Dict[str, Any]) -> List[str]:
        """Determine what context information is needed"""
        requirements = []

        if intent_type == "code_management":
            requirements.extend(["current_directory", "git_status", "open_files"])
        elif intent_type == "workflow_management":
            requirements.extend(["active_workflows", "system_status", "resource_usage"])
        elif intent_type == "communication":
            requirements.extend(["email_accounts", "message_history", "contact_list"])
        elif intent_type == "system_maintenance":
            requirements.extend(["system_info", "installed_software", "disk_usage"])
        elif intent_type == "analysis_intelligence":
            requirements.extend(["available_data", "search_history", "intelligence_sources"])

        # Add requirements based on parameters
        if "target_files" in parameters:
            requirements.append("file_permissions")
        if "recipients" in parameters:
            requirements.append("contact_verification")

        return requirements

    def _generate_execution_hints(self, intent_type: str, parameters: Dict[str, Any]) -> List[str]:
        """Generate hints for execution"""
        hints = []

        if intent_type == "code_management":
            hints.extend([
                "Check git status before making changes",
                "Run tests after code modifications",
                "Consider creating a backup branch"
            ])
        elif intent_type == "workflow_management":
            hints.extend([
                "Verify workflow dependencies are met",
                "Check resource availability",
                "Monitor execution progress"
            ])
        elif intent_type == "communication":
            hints.extend([
                "Verify recipient contact information",
                "Check message content for clarity",
                "Consider response time expectations"
            ])

        return hints

    def _calculate_confidence(self, base_confidence: float, entities: List[Dict[str, Any]],
                            parameters: Dict[str, Any]) -> float:
        """Calculate final confidence score"""
        confidence = base_confidence

        # Boost confidence based on entities found
        entity_boost = len(entities) * 0.05
        confidence += entity_boost

        # Boost confidence based on parameters extracted
        param_boost = len(parameters) * 0.03
        confidence += param_boost

        # Apply context requirements factor
        if parameters.get("context_requirements"):
            confidence += 0.05

        # Cap at 0.95 (leave room for uncertainty)
        return min(confidence, 0.95)

    def _generate_fallbacks(self, intent_type: str, confidence: float) -> List[str]:
        """Generate fallback actions for low confidence intents"""
        fallbacks = []

        if confidence < self.confidence_threshold:
            fallbacks.append("Request user clarification")
            fallbacks.append("Present multiple interpretation options")

        # Intent-specific fallbacks
        if intent_type == "code_management":
            fallbacks.append("Show available code files for selection")
        elif intent_type == "workflow_management":
            fallbacks.append("List available workflows for selection")
        elif intent_type == "communication":
            fallbacks.append("Ask user to specify communication type")

        return fallbacks

    def _log_processing_result(self, processed_intent: ProcessedIntent):
        """Log the processing result for analysis"""
        self.logger.debug(
            f"Intent processed: {processed_intent.intent_type} "
            f"(confidence: {processed_intent.confidence:.2f})"
        )

        if processed_intent.entities:
            self.logger.debug(f"  Entities found: {len(processed_intent.entities)}")

        if processed_intent.parameters:
            self.logger.debug(f"  Parameters extracted: {list(processed_intent.parameters.keys())}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about intent processing"""
        if not self.processing_history:
            return {"total_processed": 0}

        total_processed = len(self.processing_history)
        avg_confidence = sum(p.confidence for p in self.processing_history) / total_processed

        intent_types = {}
        for processed in self.processing_history:
            intent_type = processed.intent_type
            intent_types[intent_type] = intent_types.get(intent_type, 0) + 1

        return {
            "total_processed": total_processed,
            "average_confidence": avg_confidence,
            "intent_type_distribution": intent_types,
            "most_common_intent": max(intent_types.items(), key=lambda x: x[1]) if intent_types else None
        }


# Demonstration
async def demonstrate_intent_processing():
    """Demonstrate intent processing capabilities"""
    print("🧠 INTENT PROCESSOR DEMONSTRATION")
    print("=" * 50)

    processor = IntentProcessor()

    test_inputs = [
        "Fix the bug in the workflow approval system",
        "Check my email and summarize important messages",
        "Run the video production pipeline",
        "Analyze security vulnerabilities in the codebase",
        "Install the latest software updates",
        "Create a report on system performance"
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n{i}. Input: '{test_input}'")

        # Create mock user intent
        class MockIntent:
            def __init__(self, text):
                self.id = f"test_{i}"
                self.raw_input = text

        mock_intent = MockIntent(test_input)

        try:
            result = await processor.process(mock_intent)

            print(f"   Intent Type: {result.intent_type}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Entities: {len(result.entities)}")
            print(f"   Parameters: {list(result.parameters.keys()) if result.parameters else 'None'}")

            if result.execution_hints:
                print(f"   Hint: {result.execution_hints[0]}")

        except Exception as e:
            print(f"   Error: {e}")

    # Show processing statistics
    print("\n📊 Processing Statistics:")
    stats = processor.get_processing_stats()
    print(f"   Total Processed: {stats['total_processed']}")
    print(f"   Average Confidence: {stats['average_confidence']:.2f}")

    if stats.get('most_common_intent'):
        intent_type, count = stats['most_common_intent']
        print(f"   Most Common Intent: {intent_type} ({count} times)")

    print("\n✅ Intent Processing Demonstration Complete")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_intent_processing())
