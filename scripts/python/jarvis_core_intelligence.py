#!/usr/bin/env python3
"""
JARVIS Core Intelligence

The brain of JARVIS - Natural language understanding, context awareness, memory,
and intelligent conversation capabilities.

MCU JARVIS Capability: Natural conversation, context understanding, memory, and
intelligent assistance.

@JARVIS @CORE_INTELLIGENCE @MCU_FEATURE
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import re
from collections import deque
import time
import tempfile
import shutil

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCoreIntelligence")


class IntentType(Enum):
    """User intent types"""
    QUESTION = "question"
    COMMAND = "command"
    REQUEST = "request"
    CONVERSATION = "conversation"
    INFORMATION = "information"
    CONTROL = "control"
    QUERY = "query"
    UNKNOWN = "unknown"


class ContextType(Enum):
    """Context types"""
    CONVERSATION = "conversation"
    TASK = "task"
    PROJECT = "project"
    SYSTEM = "system"
    USER_PREFERENCE = "user_preference"
    MEMORY = "memory"


@dataclass
class Context:
    """Context information"""
    context_id: str
    context_type: ContextType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['context_type'] = self.context_type.value
        data['created_at'] = self.created_at.isoformat()
        data['accessed_at'] = self.accessed_at.isoformat()
        return data


@dataclass
class Memory:
    """Memory entry"""
    memory_id: str
    content: str
    category: str
    importance: float = 0.5  # 0.0 to 1.0
    associated_entities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['accessed_at'] = self.accessed_at.isoformat()
        return data


@dataclass
class Intent:
    """Detected user intent"""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    original_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['intent_type'] = self.intent_type.value
        return data


@dataclass
class ConversationTurn:
    """Conversation turn"""
    turn_id: str
    user_input: str
    intent: Intent
    jarvis_response: str
    context_used: List[str] = field(default_factory=list)
    memories_created: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['intent'] = self.intent.to_dict()
        data['timestamp'] = self.timestamp.isoformat()
        return data


class JARVISCoreIntelligence:
    """
    JARVIS Core Intelligence

    MCU JARVIS Capability: Natural conversation, context understanding, memory.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize core intelligence"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISCoreIntelligence")

        # Memory storage
        self.memories: Dict[str, Memory] = {}

        # Context storage
        self.contexts: Dict[str, Context] = {}

        # Conversation history (sliding window)
        self.conversation_history: deque = deque(maxlen=50)

        # Current conversation context
        self.current_context_id: Optional[str] = None

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis" / "intelligence"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.memories_file = self.data_dir / "memories.json"
        self.contexts_file = self.data_dir / "contexts.json"
        self.conversations_file = self.data_dir / "conversations.json"

        # Load state
        self._load_state()

        # Intent patterns
        self.intent_patterns = self._load_intent_patterns()

        # Memory optimization settings
        self.max_memories = 10000  # Maximum memories before pruning
        self.memory_prune_threshold = 0.1  # Prune memories below this importance

        # Context optimization settings
        self.max_contexts = 5000  # Maximum contexts before pruning
        self.context_expiry_days = 90  # Contexts older than this are candidates for pruning

        # Auto-prune old/low-importance data
        self._optimize_memory()
        self._optimize_contexts()

        self.logger.info("🧠 JARVIS Core Intelligence initialized")
        self.logger.info(f"   Memories: {len(self.memories)}")
        self.logger.info(f"   Contexts: {len(self.contexts)}")
        self.logger.info(f"   Conversation history: {len(self.conversation_history)} turns")

    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Load intent recognition patterns"""
        return {
            IntentType.QUESTION: [
                r'\b(what|when|where|who|why|how|which|can you|could you|would you|tell me|explain|describe)\b',
                r'\?',
            ],
            IntentType.COMMAND: [
                r'\b(do|execute|run|start|stop|open|close|create|delete|update|set|change|enable|disable)\b',
                r'\b(turn on|turn off|switch|activate|deactivate)\b',
            ],
            IntentType.REQUEST: [
                r'\b(please|can you|could you|would you|I need|I want|help me)\b',
            ],
            IntentType.INFORMATION: [
                r'\b(status|check|show|display|list|get|fetch|retrieve)\b',
            ],
            IntentType.CONTROL: [
                r'\b(control|manage|handle|operate|configure)\b',
            ],
        }

    def _load_state(self):
        """Load memories and contexts"""
        # Load memories
        if self.memories_file.exists():
            try:
                with open(self.memories_file, 'r') as f:
                    data = json.load(f)
                    for mem_data in data:
                        memory = Memory(
                            memory_id=mem_data['memory_id'],
                            content=mem_data['content'],
                            category=mem_data['category'],
                            importance=mem_data.get('importance', 0.5),
                            associated_entities=mem_data.get('associated_entities', []),
                            created_at=datetime.fromisoformat(mem_data['created_at']),
                            accessed_at=datetime.fromisoformat(mem_data.get('accessed_at', datetime.now().isoformat())),
                            access_count=mem_data.get('access_count', 0)
                        )
                        self.memories[memory.memory_id] = memory
                self.logger.info(f"   Loaded {len(self.memories)} memories")
            except Exception as e:
                self.logger.error(f"Error loading memories: {e}")

        # Load contexts
        if self.contexts_file.exists():
            try:
                with open(self.contexts_file, 'r') as f:
                    data = json.load(f)
                    for ctx_data in data:
                        context = Context(
                            context_id=ctx_data['context_id'],
                            context_type=ContextType(ctx_data['context_type']),
                            content=ctx_data['content'],
                            metadata=ctx_data.get('metadata', {}),
                            created_at=datetime.fromisoformat(ctx_data['created_at']),
                            accessed_at=datetime.fromisoformat(ctx_data.get('accessed_at', datetime.now().isoformat())),
                            relevance_score=ctx_data.get('relevance_score', 1.0)
                        )
                        self.contexts[context.context_id] = context
                self.logger.info(f"   Loaded {len(self.contexts)} contexts")
            except Exception as e:
                self.logger.error(f"Error loading contexts: {e}")

    def _save_state(self):
        """Save memories and contexts using atomic writes"""
        max_retries = 3
        retry_delay = 0.5

        # Save memories with atomic write
        self._atomic_write_file(
            self.memories_file,
            [m.to_dict() for m in self.memories.values()],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        # Save contexts with atomic write
        self._atomic_write_file(
            self.contexts_file,
            [c.to_dict() for c in self.contexts.values()],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        # Save recent conversations with atomic write
        self._atomic_write_file(
            self.conversations_file,
            [c.to_dict() for c in self.conversation_history],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

    def _atomic_write_file(self, file_path: Path, data: Any, max_retries: int = 3, retry_delay: float = 0.5):
        """
        Atomically write data to a file with retry logic.

        Uses a temporary file and rename to ensure atomic writes and avoid
        permission issues on Windows (especially with Dropbox).

        Args:
            file_path: Target file path
            data: Data to write (will be JSON serialized)
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
        """
        # Ensure directory exists and is writable
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # Test write permissions
            test_file = file_path.parent / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Directory not writable: {file_path.parent} - {e}")
                return
        except Exception as e:
            self.logger.error(f"Error creating directory {file_path.parent}: {e}")
            return

        for attempt in range(max_retries):
            try:
                # Create temporary file in the same directory (ensures same filesystem)
                temp_file = file_path.parent / f".{file_path.name}.tmp"

                # Write to temporary file
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

                # Atomic rename (works on Windows if files are on same filesystem)
                # On Windows, replace existing file if it exists
                if file_path.exists():
                    # Try to remove existing file first (might be locked)
                    try:
                        file_path.unlink()
                    except PermissionError:
                        # File might be locked by Dropbox or another process
                        # Wait a bit and try again
                        time.sleep(retry_delay * (attempt + 1))
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise

                # Atomic rename
                temp_file.replace(file_path)
                return  # Success

            except PermissionError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.debug(f"Permission denied, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: Permission denied after {max_retries} attempts - {e}")
                    # Clean up temp file if it exists
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except OSError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    self.logger.debug(f"OS error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: {e}")
                    # Clean up temp file if it exists
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except Exception as e:
                self.logger.error(f"Unexpected error saving state to {file_path}: {e}", exc_info=True)
                # Clean up temp file if it exists
                if 'temp_file' in locals() and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
                return  # Don't retry on unexpected errors

    def understand_intent(self, user_input: str) -> Intent:
        """
        Understand user intent from natural language with enhanced ML-like scoring

        MCU JARVIS Capability: Natural language understanding with advanced pattern matching
        """
        user_input_lower = user_input.lower()
        input_length = len(user_input.split())

        # Score each intent type with weighted patterns
        intent_scores = {}
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            pattern_weights = [1.0] * len(patterns)  # Can be customized per pattern

            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, user_input_lower, re.IGNORECASE)
                if matches:
                    # Weight by pattern match count and position
                    match_count = len(matches)
                    weight = pattern_weights[i] if i < len(pattern_weights) else 1.0

                    # Boost if pattern appears early in the sentence
                    first_match_pos = user_input_lower.find(matches[0])
                    position_boost = 1.0 + (1.0 - (first_match_pos / len(user_input))) * 0.3

                    score += (match_count * weight * position_boost) / len(patterns)

            # Normalize by input length (longer inputs might have more matches)
            if input_length > 0:
                score = score / (1.0 + input_length * 0.1)

            intent_scores[intent_type] = score

        # Use conversation history to boost context-aware intents
        if self.conversation_history:
            last_turn = self.conversation_history[-1]
            if last_turn.intent.intent_type == IntentType.CONVERSATION:
                intent_scores[IntentType.CONVERSATION] *= 1.3
            elif last_turn.intent.intent_type == IntentType.QUESTION:
                intent_scores[IntentType.QUESTION] *= 1.2

        # Find best intent
        if not intent_scores or max(intent_scores.values()) == 0:
            best_intent_type = IntentType.UNKNOWN
            confidence = 0.0
        else:
            best_intent_type = max(intent_scores.items(), key=lambda x: x[1])[0]
            confidence = min(intent_scores[best_intent_type], 1.0)  # Cap at 1.0

        # Extract entities and parameters
        entities = self._extract_entities(user_input)
        parameters = self._extract_parameters(user_input, best_intent_type)

        intent = Intent(
            intent_type=best_intent_type if confidence > 0.1 else IntentType.UNKNOWN,
            confidence=confidence,
            entities=entities,
            parameters=parameters,
            original_text=user_input
        )

        self.logger.debug(f"Intent detected: {intent.intent_type.value} (confidence: {confidence:.2f})")
        return intent

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        entities = {}

        # Extract device names
        device_patterns = [
            r'\b(light|lights|lighting)\b',
            r'\b(thermostat|temperature|temp)\b',
            r'\b(camera|cameras|security)\b',
            r'\b(door|doors)\b',
            r'\b(window|windows)\b',
        ]
        devices = []
        for pattern in device_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                devices.append(re.search(pattern, text, re.IGNORECASE).group(1))
        if devices:
            entities['devices'] = devices

        # Extract locations
        location_patterns = [
            r'\b(room|lab|workshop|office|home|house|living room|bedroom|kitchen)\b',
        ]
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            locations.extend(matches)
        if locations:
            entities['locations'] = locations

        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if numbers:
            entities['numbers'] = [float(n) for n in numbers]

        return entities

    def _extract_parameters(self, text: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract parameters based on intent type"""
        parameters = {}

        if intent_type == IntentType.COMMAND:
            # Extract action
            action_patterns = [
                (r'\b(turn on|enable|activate|open|start)\b', 'action', 'on'),
                (r'\b(turn off|disable|deactivate|close|stop)\b', 'action', 'off'),
                (r'\b(set|change|adjust|configure)\b', 'action', 'set'),
            ]
            for pattern, key, value in action_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    parameters[key] = value
                    break

        # Extract values
        value_match = re.search(r'\b(to|at|as)\s+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if value_match:
            parameters['value'] = float(value_match.group(2))

        return parameters

    def get_relevant_context(self, intent: Intent, max_contexts: int = 5) -> List[Context]:
        """Get relevant contexts for the intent"""
        relevant_contexts = []

        for context in self.contexts.values():
            # Calculate relevance score
            score = context.relevance_score

            # Boost if context type matches intent
            if intent.intent_type == IntentType.CONVERSATION and context.context_type == ContextType.CONVERSATION:
                score *= 1.5
            elif intent.intent_type == IntentType.TASK and context.context_type == ContextType.TASK:
                score *= 1.5

            # Boost if entities match
            if intent.entities:
                content_lower = context.content.lower()
                for entity_list in intent.entities.values():
                    for entity in entity_list:
                        if str(entity).lower() in content_lower:
                            score *= 1.2

            # Boost recent contexts
            age_hours = (datetime.now() - context.accessed_at).total_seconds() / 3600
            if age_hours < 24:
                score *= 1.3
            elif age_hours < 168:  # 1 week
                score *= 1.1

            context.relevance_score = score
            relevant_contexts.append((score, context))

        # Sort by relevance and return top N
        relevant_contexts.sort(key=lambda x: x[0], reverse=True)
        return [ctx for _, ctx in relevant_contexts[:max_contexts]]

    def get_relevant_memories(self, intent: Intent, max_memories: int = 5) -> List[Memory]:
        """Get relevant memories for the intent"""
        relevant_memories = []

        for memory in self.memories.values():
            score = memory.importance

            # Boost if entities match
            if intent.entities:
                content_lower = memory.content.lower()
                for entity_list in intent.entities.values():
                    for entity in entity_list:
                        if str(entity).lower() in content_lower:
                            score *= 1.3

            # Boost frequently accessed
            score *= (1.0 + memory.access_count * 0.1)

            # Boost recent memories
            age_hours = (datetime.now() - memory.accessed_at).total_seconds() / 3600
            if age_hours < 24:
                score *= 1.2

            relevant_memories.append((score, memory))

        # Sort by relevance and return top N
        relevant_memories.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in relevant_memories[:max_memories]]

    def create_memory(self, content: str, category: str, importance: float = None,
                     associated_entities: List[str] = None) -> Memory:
        """
        Create a new memory with auto-calculated importance if not provided

        Args:
            content: Memory content
            category: Memory category
            importance: Importance score (0.0-1.0). If None, auto-calculated.
            associated_entities: Associated entity names
        """
        memory_id = f"mem_{int(datetime.now().timestamp())}_{len(self.memories)}"

        # Auto-calculate importance if not provided
        if importance is None:
            importance = self._calculate_memory_importance(content, category, associated_entities)

        memory = Memory(
            memory_id=memory_id,
            content=content,
            category=category,
            importance=importance,
            associated_entities=associated_entities or []
        )

        self.memories[memory_id] = memory

        # Prune if needed
        if len(self.memories) > self.max_memories:
            self._optimize_memory()

        self._save_state()

        self.logger.info(f"💾 Created memory: {category} - {content[:50]}... (importance: {importance:.2f})")
        return memory

    def _calculate_memory_importance(self, content: str, category: str, 
                                      associated_entities: List[str] = None) -> float:
        """
        Auto-calculate memory importance based on content analysis

        Returns:
            Importance score between 0.0 and 1.0
        """
        importance = 0.5  # Base importance

        # Boost for longer content (more information)
        content_length = len(content)
        if content_length > 500:
            importance += 0.2
        elif content_length > 200:
            importance += 0.1

        # Boost for important categories
        important_categories = ['user_preference', 'system_config', 'security', 'critical']
        if category.lower() in important_categories:
            importance += 0.2

        # Boost for entities (more connections = more important)
        if associated_entities and len(associated_entities) > 0:
            importance += min(len(associated_entities) * 0.05, 0.2)

        # Boost for keywords indicating importance
        important_keywords = ['critical', 'important', 'remember', 'always', 'never', 'must', 'should']
        content_lower = content.lower()
        keyword_count = sum(1 for kw in important_keywords if kw in content_lower)
        importance += min(keyword_count * 0.05, 0.15)

        # Cap at 1.0
        return min(importance, 1.0)

    def create_context(self, context_type: ContextType, content: str,
                      metadata: Dict[str, Any] = None) -> Context:
        """Create a new context"""
        context_id = f"ctx_{int(datetime.now().timestamp())}_{len(self.contexts)}"

        context = Context(
            context_id=context_id,
            context_type=context_type,
            content=content,
            metadata=metadata or {}
        )

        self.contexts[context_id] = context
        self.current_context_id = context_id
        self._save_state()

        self.logger.info(f"📋 Created context: {context_type.value}")
        return context

    def process_conversation(self, user_input: str, jarvis_response: str,
                           context_used: List[str] = None,
                           memories_created: List[str] = None) -> ConversationTurn:
        """Process a conversation turn"""
        # Understand intent
        intent = self.understand_intent(user_input)

        # Get relevant context and memories
        relevant_contexts = self.get_relevant_context(intent)
        relevant_memories = self.get_relevant_memories(intent)

        # Update context access
        for context in relevant_contexts:
            context.accessed_at = datetime.now()

        # Update memory access
        for memory in relevant_memories:
            memory.accessed_at = datetime.now()
            memory.access_count += 1

        # Create conversation turn
        turn_id = f"turn_{int(datetime.now().timestamp())}_{len(self.conversation_history)}"
        turn = ConversationTurn(
            turn_id=turn_id,
            user_input=user_input,
            intent=intent,
            jarvis_response=jarvis_response,
            context_used=[c.context_id for c in relevant_contexts],
            memories_created=memories_created or []
        )

        self.conversation_history.append(turn)
        self._save_state()

        return turn

    def generate_response_context(self, intent: Intent, relevant_contexts: List[Context],
                                 relevant_memories: List[Memory]) -> str:
        """
        Generate context-aware response hints

        Returns a string that summarizes relevant context for response generation
        """
        context_parts = []

        # Add relevant memories
        if relevant_memories:
            memory_summary = "Relevant memories: " + "; ".join([
                mem.content[:100] for mem in relevant_memories[:3]
            ])
            context_parts.append(memory_summary)

        # Add relevant contexts
        if relevant_contexts:
            context_summary = "Current context: " + "; ".join([
                ctx.content[:100] for ctx in relevant_contexts[:2]
            ])
            context_parts.append(context_summary)

        # Add conversation history (last few turns)
        if self.conversation_history:
            recent_turns = list(self.conversation_history)[-3:]
            history_summary = "Recent conversation: " + " | ".join([
                f"User: {turn.user_input[:50]}" for turn in recent_turns
            ])
            context_parts.append(history_summary)

        return " | ".join(context_parts) if context_parts else ""

    def get_conversation_summary(self, last_n_turns: int = 10, use_formatter: bool = True) -> str:
        """Get summary of recent conversation with clear speaker labels"""
        if not self.conversation_history:
            return "No conversation history"

        recent_turns = list(self.conversation_history)[-last_n_turns:]

        # Use formatter if available and requested
        if use_formatter:
            try:
                from jarvis_conversation_formatter import ConversationFormatter, Speaker
                formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)

                formatted_messages = []
                for turn in recent_turns:
                    # Add human message
                    formatted_messages.append(formatter.format_message(
                        Speaker.HUMAN,
                        turn.user_input[:200],  # Limit length for summary
                        turn.timestamp
                    ))
                    # Add JARVIS response
                    formatted_messages.append(formatter.format_message(
                        Speaker.JARVIS,
                        turn.jarvis_response[:200],  # Limit length for summary
                        turn.timestamp
                    ))

                return formatter.format_for_display(formatted_messages)
            except ImportError:
                # Fallback to basic format
                pass

        # Basic format with clear labels
        summary_parts = []
        for turn in recent_turns:
            time_str = turn.timestamp.strftime('%H:%M')
            summary_parts.append(
                f"[{time_str}] 👤 HUMAN: {turn.user_input[:100]}"
            )
            summary_parts.append(
                f"[{time_str}] 🤖 JARVIS: {turn.jarvis_response[:100]}"
            )

        return "\n".join(summary_parts)

    def _optimize_memory(self):
        """Optimize memory storage by pruning low-importance or old memories"""
        if len(self.memories) <= self.max_memories:
            return

        # Sort by importance and access patterns
        memory_scores = []
        for memory in self.memories.values():
            # Calculate composite score
            age_days = (datetime.now() - memory.accessed_at).days
            age_factor = max(0.0, 1.0 - (age_days / 365.0))  # Decay over 1 year
            access_factor = min(1.0, memory.access_count / 10.0)  # Normalize access count

            score = (memory.importance * 0.5 + 
                    age_factor * 0.3 + 
                    access_factor * 0.2)

            memory_scores.append((score, memory.memory_id))

        # Sort by score (lowest first)
        memory_scores.sort(key=lambda x: x[0])

        # Remove lowest scoring memories
        to_remove = len(self.memories) - self.max_memories
        removed = 0
        for score, memory_id in memory_scores:
            if removed >= to_remove:
                break
            if score < self.memory_prune_threshold:
                del self.memories[memory_id]
                removed += 1

        if removed > 0:
            self.logger.info(f"🧹 Pruned {removed} low-importance memories")
            self._save_state()

    def _optimize_contexts(self):
        """Optimize context storage by pruning old or low-relevance contexts"""
        if len(self.contexts) <= self.max_contexts:
            return

        # Remove contexts older than expiry
        now = datetime.now()
        to_remove = []
        for context_id, context in self.contexts.items():
            age_days = (now - context.accessed_at).days
            if age_days > self.context_expiry_days and context.relevance_score < 0.3:
                to_remove.append(context_id)

        for context_id in to_remove:
            del self.contexts[context_id]

        # If still over limit, remove lowest relevance
        if len(self.contexts) > self.max_contexts:
            contexts_by_relevance = sorted(
                self.contexts.items(),
                key=lambda x: x[1].relevance_score
            )
            to_remove = len(self.contexts) - self.max_contexts
            for context_id, _ in contexts_by_relevance[:to_remove]:
                del self.contexts[context_id]

        if to_remove:
            self.logger.info(f"🧹 Pruned {len(to_remove)} old/low-relevance contexts")
            self._save_state()

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive intelligence status report"""
        # Calculate memory statistics
        memory_importance_dist = {
            "high": len([m for m in self.memories.values() if m.importance >= 0.7]),
            "medium": len([m for m in self.memories.values() if 0.3 <= m.importance < 0.7]),
            "low": len([m for m in self.memories.values() if m.importance < 0.3])
        }

        # Calculate context age distribution
        now = datetime.now()
        context_age_dist = {
            "recent": len([c for c in self.contexts.values() 
                          if (now - c.accessed_at).days < 7]),
            "week_old": len([c for c in self.contexts.values() 
                            if 7 <= (now - c.accessed_at).days < 30]),
            "month_old": len([c for c in self.contexts.values() 
                             if 30 <= (now - c.accessed_at).days < 90]),
            "old": len([c for c in self.contexts.values() 
                       if (now - c.accessed_at).days >= 90])
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "memories_count": len(self.memories),
            "contexts_count": len(self.contexts),
            "conversation_turns": len(self.conversation_history),
            "current_context": self.current_context_id,
            "memory_categories": {
                cat: len([m for m in self.memories.values() if m.category == cat])
                for cat in set(m.category for m in self.memories.values())
            },
            "memory_importance_distribution": memory_importance_dist,
            "context_types": {
                ctx_type.value: len([c for c in self.contexts.values() if c.context_type == ctx_type])
                for ctx_type in ContextType
            },
            "context_age_distribution": context_age_dist,
            "optimization": {
                "max_memories": self.max_memories,
                "max_contexts": self.max_contexts,
                "memory_prune_threshold": self.memory_prune_threshold,
                "context_expiry_days": self.context_expiry_days
            }
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Core Intelligence")
        parser.add_argument("--status", action="store_true", help="Get status report")
        parser.add_argument("--understand", type=str, help="Understand intent from text")
        parser.add_argument("--memory", nargs=3, metavar=("CONTENT", "CATEGORY", "IMPORTANCE"), help="Create memory")
        parser.add_argument("--context", nargs=3, metavar=("TYPE", "CONTENT", "METADATA"), help="Create context")
        parser.add_argument("--summary", action="store_true", help="Get conversation summary")

        args = parser.parse_args()

        intelligence = JARVISCoreIntelligence()

        if args.status:
            report = intelligence.get_status_report()
            print(json.dumps(report, indent=2, default=str))

        elif args.understand:
            intent = intelligence.understand_intent(args.understand)
            print(json.dumps(intent.to_dict(), indent=2, default=str))

        elif args.memory:
            content, category, importance = args.memory
            memory = intelligence.create_memory(content, category, float(importance))
            print(f"✅ Created memory: {memory.memory_id}")

        elif args.context:
            ctx_type, content, metadata_json = args.context
            metadata = json.loads(metadata_json) if metadata_json else {}
            context = intelligence.create_context(ContextType(ctx_type), content, metadata)
            print(f"✅ Created context: {context.context_id}")

        elif args.summary:
            summary = intelligence.get_conversation_summary()
            print(summary)

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()