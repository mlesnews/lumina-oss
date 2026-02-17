#!/usr/bin/env python3
"""
SYPHON System - Extract Actionable Intelligence from Communications

"I drink your milkshake!" - Extract all valuable intelligence before it's lost.

SYPHON extracts actionable items, tasks, decisions, and intelligence from:
- Email messages
- SMS/Text messages
- Social media posts
- Extension updates
- Any communication channel

Author: <COMPANY_NAME> LLC
Date: 2025-01-24
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add project root to path for unified engine
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.pattern_unified_engine import PatternUnifiedEngine
    UNIFIED_ENGINE_AVAILABLE = True
except ImportError:
    UNIFIED_ENGINE_AVAILABLE = False
    PatternUnifiedEngine = None

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DataSourceType(Enum):
    """Types of data sources for syphon extraction"""
    EMAIL = "email"
    SMS = "sms"
    SOCIAL = "social"
    CODE = "code"
    DOCUMENT = "document"
    OTHER = "other"


@dataclass
class SyphonData:
    """Represents extracted syphon data"""
    data_id: str
    source_type: DataSourceType
    source_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.now)
    actionable_items: List[str] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    intelligence: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "data_id": self.data_id,
            "source_type": self.source_type.value,
            "source_id": self.source_id,
            "content": self.content,
            "metadata": self.metadata,
            "extracted_at": self.extracted_at.isoformat(),
            "actionable_items": self.actionable_items,
            "tasks": self.tasks,
            "decisions": self.decisions,
            "intelligence": self.intelligence
        }


class SYPHONSystem:
    """SYPHON System - Extract actionable intelligence from communications"""

    def __init__(self, project_root: Path) -> None:
        """
        Initialize SYPHON system.

        Args:
            project_root: Root path of the project
        """
        self.project_root = Path(project_root)
        
        # Load storage policy
        self.storage_policy = self._load_storage_policy()
        
        if self.storage_policy.get("zero_local_storage_enforced"):
            self.data_dir = Path(self.storage_policy["nas_paths"]["syphon_raw"])
            self.logger.info(f"🛡️  Enforcing Zero-Local-Storage Policy. Using NAS: {self.data_dir}")
        else:
            self.data_dir = self.project_root / "data" / "syphon"
            
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_data_file = self.data_dir / "extracted_data.json"
        self.extracted_data: List[SyphonData] = []
        self.logger = get_logger("SYPHONSystem")

    def _load_storage_policy(self) -> Dict[str, Any]:
        """Load storage policy from config"""
        policy_file = self.project_root / "config" / "storage_policy.json"
        if policy_file.exists():
            try:
                with open(policy_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading storage policy: {e}")
        return {"zero_local_storage_enforced": False}

        # Initialize unified pattern engine if available
        if UNIFIED_ENGINE_AVAILABLE:
            self.unified_engine = PatternUnifiedEngine(self.project_root)
            self.logger.info("   ✅ Using Pattern Unified Engine (EXTRAPOLATION <=> REGEX <=> PATTERN MATCHING)")
        else:
            self.unified_engine = None
            self.logger.warning("   ⚠️  Pattern Unified Engine not available, using fallback")

        # Load existing extracted data
        self._load_extracted_data()

    def _load_extracted_data(self) -> None:
        """Load previously extracted data"""
        if self.extracted_data_file.exists():
            try:
                with open(self.extracted_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.extracted_data = [
                        self._dict_to_syphon_data(item) for item in data
                    ]
                self.logger.info(f"Loaded {len(self.extracted_data)} syphon items")
            except Exception as e:
                self.logger.error(f"Error loading syphon data: {e}")
                self.extracted_data = []

    def _dict_to_syphon_data(self, data: Dict[str, Any]) -> SyphonData:
        """Convert dictionary to SyphonData"""
        return SyphonData(
            data_id=data.get("data_id", ""),
            source_type=DataSourceType(data.get("source_type", "other")),
            source_id=data.get("source_id", ""),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            extracted_at=datetime.fromisoformat(data.get("extracted_at", datetime.now().isoformat())),
            actionable_items=data.get("actionable_items", []),
            tasks=data.get("tasks", []),
            decisions=data.get("decisions", []),
            intelligence=data.get("intelligence", [])
        )

    def _save_extracted_data(self) -> None:
        """Save extracted data to file"""
        try:
            data = [item.to_dict() for item in self.extracted_data]
            with open(self.extracted_data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            self.logger.info(f"Saved {len(self.extracted_data)} syphon items")
        except Exception as e:
            self.logger.error(f"Error saving syphon data: {e}")

    def syphon_email(
        self,
        email_id: str,
        subject: str,
        body: str,
        from_address: str,
        to_address: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SyphonData:
        """
        Syphon actionable intelligence from email.

        Args:
            email_id: Unique email identifier
            subject: Email subject
            body: Email body content
            from_address: Sender email address
            to_address: Recipient email address
            metadata: Additional metadata

        Returns:
            SyphonData with extracted intelligence
        """
        content = f"Subject: {subject}\n\n{body}"
        full_metadata = {
            "email_id": email_id,
            "from": from_address,
            "to": to_address,
            "subject": subject,
            **(metadata or {})
        }

        # Extract actionable items
        actionable_items = self._extract_actionable_items(content)

        # Extract tasks
        tasks = self._extract_tasks(content, subject)

        # Extract decisions
        decisions = self._extract_decisions(content)

        # Extract intelligence
        intelligence = self._extract_intelligence(content, subject)

        syphon_data = SyphonData(
            data_id=f"email_{email_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.EMAIL,
            source_id=email_id,
            content=content,
            metadata=full_metadata,
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks,
            decisions=decisions,
            intelligence=intelligence
        )

        self.extracted_data.append(syphon_data)
        self._save_extracted_data()

        self.logger.info(f"Syphoned email {email_id}: {len(actionable_items)} items, {len(tasks)} tasks")
        return syphon_data

    def syphon_sms(
        self,
        sms_id: str,
        message: str,
        from_number: str,
        to_number: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SyphonData:
        """
        Syphon actionable intelligence from SMS/text message.

        Args:
            sms_id: Unique SMS identifier
            message: SMS message content
            from_number: Sender phone number
            to_number: Recipient phone number
            metadata: Additional metadata

        Returns:
            SyphonData with extracted intelligence
        """
        full_metadata = {
            "sms_id": sms_id,
            "from": from_number,
            "to": to_number,
            **(metadata or {})
        }

        # Extract actionable items
        actionable_items = self._extract_actionable_items(message)

        # Extract tasks
        tasks = self._extract_tasks(message, "")

        # Extract decisions
        decisions = self._extract_decisions(message)

        # Extract intelligence
        intelligence = self._extract_intelligence(message, "")

        syphon_data = SyphonData(
            data_id=f"sms_{sms_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.SMS,
            source_id=sms_id,
            content=message,
            metadata=full_metadata,
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks,
            decisions=decisions,
            intelligence=intelligence
        )

        self.extracted_data.append(syphon_data)
        self._save_extracted_data()

        self.logger.info(f"Syphoned SMS {sms_id}: {len(actionable_items)} items, {len(tasks)} tasks")
        return syphon_data

    def _extract_actionable_items(self, content: str) -> List[str]:
        """Extract actionable items from content using unified engine"""
        actionable_items = []

        # Use unified engine if available
        if self.unified_engine:
            try:
                # Combine all action patterns into one regex
                action_pattern = r'(?:action required|action needed|please|need to|must|should|required to|todo|task|do|complete|finish|implement|follow up|follow-up|f/u|urgent|asap|immediately|soon|deadline|due date|by|before|review|check|verify|confirm|update|change|modify|fix|schedule|meeting|call|call back)'

                # Use unified engine to extract patterns
                result = self.unified_engine.unified_operation("extract", content, action_pattern, flags=re.IGNORECASE)

                if result.extracted:
                    # Extract sentences containing these patterns
                    sentences = re.split(r'[.!?]\s+', content)
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence or len(sentence) < 10:
                            continue

                        # Check if sentence contains any extracted pattern
                        sentence_lower = sentence.lower()
                        for extracted in result.extracted:
                            if extracted.lower() in sentence_lower:
                                if sentence not in actionable_items and len(sentence) > 15:
                                    actionable_items.append(sentence)
                                    break
            except Exception as e:
                self.logger.warning(f"   Unified engine error, falling back: {e}")

        # Fallback to original implementation
        if not actionable_items:
            content_lower = content.lower()

            # Action keywords
            action_patterns = [
                r'(?:action required|action needed|please|need to|must|should|required to)',
                r'(?:todo|task|do|complete|finish|implement)',
                r'(?:follow up|follow-up|f/u)',
                r'(?:urgent|asap|immediately|soon)',
                r'(?:deadline|due date|by|before)',
                r'(?:review|check|verify|confirm)',
                r'(?:update|change|modify|fix)',
                r'(?:schedule|meeting|call|call back)'
            ]

            # Extract sentences with action keywords
            sentences = re.split(r'[.!?]\s+', content)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 10:
                    continue

                # Check for action keywords
                for pattern in action_patterns:
                    if re.search(pattern, sentence.lower()):
                        if sentence not in actionable_items and len(sentence) > 15:
                            actionable_items.append(sentence)
                        break

        # Extract bullet points and numbered lists
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Bullet points
            if re.match(r'^[-*•→▶]\s+', line):
                item = re.sub(r'^[-*•→▶]\s+', '', line)
                if item and len(item) > 10 and item not in actionable_items:
                    actionable_items.append(item)

            # Numbered lists
            if re.match(r'^\d+[.)]\s+', line):
                item = re.sub(r'^\d+[.)]\s+', '', line)
                if item and len(item) > 10 and item not in actionable_items:
                    actionable_items.append(item)

        return actionable_items[:20]  # Limit to top 20

    def _extract_tasks(self, content: str, subject: str) -> List[Dict[str, Any]]:
        """Extract tasks from content"""
        tasks = []
        content_lower = content.lower()

        # Task patterns
        task_patterns = [
            (r'(?:todo|task|action):\s*(.+)', 'explicit'),
            (r'(?:need to|must|should|required to)\s+(.+)', 'required'),
            (r'(?:please|can you|could you)\s+(.+)', 'request'),
            (r'(?:follow up|follow-up)\s+(?:on|with|about)\s+(.+)', 'followup'),
            (r'(?:deadline|due|by)\s+(.+?)(?:\.|$)', 'deadline'),
        ]

        for pattern, task_type in task_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                task_text = match.group(1).strip()
                if task_text and len(task_text) > 10:
                    tasks.append({
                        "text": task_text,
                        "type": task_type,
                        "priority": self._determine_priority(content_lower, task_text)
                    })

        return tasks[:10]  # Limit to top 10

    def _extract_decisions(self, content: str) -> List[Dict[str, Any]]:
        """Extract decisions from content"""
        decisions = []
        content_lower = content.lower()

        # Decision patterns
        decision_patterns = [
            (r'(?:decided|decision|chose|selected|going with)\s+(.+)', 'made'),
            (r'(?:we will|we\'ll|we are going to)\s+(.+)', 'commitment'),
            (r'(?:approved|approval|approved for)\s+(.+)', 'approval'),
            (r'(?:rejected|reject|declined|decline)\s+(.+)', 'rejection'),
        ]

        for pattern, decision_type in decision_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                decision_text = match.group(1).strip()
                if decision_text and len(decision_text) > 10:
                    decisions.append({
                        "text": decision_text,
                        "type": decision_type
                    })

        return decisions[:10]  # Limit to top 10

    def _extract_intelligence(self, content: str, subject: str) -> List[Dict[str, Any]]:
        """Extract intelligence/insights from content"""
        intelligence = []
        content_lower = content.lower()

        # Intelligence patterns
        intel_patterns = [
            (r'(?:important|critical|urgent|priority)\s+(.+)', 'priority'),
            (r'(?:status|update|progress)\s+(?:on|for)\s+(.+)', 'status'),
            (r'(?:issue|problem|error|bug)\s+(.+)', 'issue'),
            (r'(?:opportunity|chance|possibility)\s+(.+)', 'opportunity'),
            (r'(?:risk|concern|warning)\s+(.+)', 'risk'),
        ]

        for pattern, intel_type in intel_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                intel_text = match.group(1).strip()
                if intel_text and len(intel_text) > 10:
                    intelligence.append({
                        "text": intel_text,
                        "type": intel_type
                    })

        return intelligence[:10]  # Limit to top 10

    def _determine_priority(self, content: str, task_text: str) -> str:
        """Determine task priority"""
        content_lower = content.lower()
        task_lower = task_text.lower()

        if any(word in content_lower or word in task_lower for word in ['urgent', 'asap', 'immediately', 'critical']):
            return 'high'
        elif any(word in content_lower or word in task_lower for word in ['important', 'soon', 'priority']):
            return 'medium'
        else:
            return 'normal'

    def syphon_generic(
        self,
        content: str,
        source_type: DataSourceType,
        source_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SyphonData:
        """
        Syphon actionable intelligence from generic content.

        Args:
            content: Content to extract intelligence from
            source_type: Type of data source
            source_id: Unique identifier for the source
            metadata: Additional metadata

        Returns:
            SyphonData with extracted intelligence
        """
        full_metadata = {
            "source_id": source_id,
            "source_type": source_type.value,
            **(metadata or {})
        }

        # Extract actionable items
        actionable_items = self._extract_actionable_items(content)

        # Extract tasks
        tasks = self._extract_tasks(content, "")

        # Extract decisions
        decisions = self._extract_decisions(content)

        # Extract intelligence
        intelligence = self._extract_intelligence(content, "")

        syphon_data = SyphonData(
            data_id=f"generic_{source_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=source_type,
            source_id=source_id,
            content=content,
            metadata=full_metadata,
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks,
            decisions=decisions,
            intelligence=intelligence
        )

        self.extracted_data.append(syphon_data)
        self._save_extracted_data()

        self.logger.info(f"Syphoned generic content {source_id}: {len(actionable_items)} items, {len(tasks)} tasks")
        return syphon_data

    def get_extracted_data(
        self,
        source_type: Optional[DataSourceType] = None,
        limit: Optional[int] = None
    ) -> List[SyphonData]:
        """
        Get extracted syphon data.

        Args:
            source_type: Filter by source type
            limit: Limit number of results

        Returns:
            List of SyphonData
        """
        data = self.extracted_data
        if source_type:
            data = [item for item in data if item.source_type == source_type]
        if limit:
            data = data[:limit]
        return data

    def detect_ai_capabilities(
        self,
        entity_name: str,
        entity_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect AI capabilities of external entity (--ai-integration strategy).

        PART OF SYPHON WORKFLOW: Always check for AI capabilities when reaching out
        to external entities (companies, organizations, systems, applications, etc.)

        Args:
            entity_name: Name of the external entity
            entity_type: Type of entity (company, organization, system, application, etc.)
            metadata: Additional metadata about the entity

        Returns:
            Dictionary with AI detection results and integration recommendations
        """
        self.logger.info(f"🤖 Detecting AI capabilities for {entity_type}: {entity_name}")

        detection_result = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "ai_detected": False,
            "ai_systems": [],
            "ai_capabilities": [],
            "integration_recommendations": [],
            "detection_methods_used": [],
            "metadata": metadata or {}
        }

        # Detection methods (following --ai-integration strategy)
        detection_methods = [
            self._check_api_documentation,
            self._check_technical_docs,
            self._check_marketing_materials,
            self._check_code_analysis,
            self._check_metadata_indicators
        ]

        for method in detection_methods:
            try:
                result = method(entity_name, entity_type, metadata)
                if result.get("ai_detected"):
                    detection_result["ai_detected"] = True
                    detection_result["ai_systems"].extend(result.get("ai_systems", []))
                    detection_result["ai_capabilities"].extend(result.get("ai_capabilities", []))
                    detection_result["detection_methods_used"].append(method.__name__)
            except Exception as e:
                self.logger.warning(f"Error in AI detection method {method.__name__}: {e}")

        # If AI detected, generate integration recommendations
        if detection_result["ai_detected"]:
            detection_result["integration_recommendations"] = self._generate_integration_recommendations(
                detection_result
            )
            self.logger.info(f"✅ AI detected for {entity_name}: {len(detection_result['ai_systems'])} system(s)")
        else:
            self.logger.info(f"ℹ️  No AI detected for {entity_name}")

        return detection_result

    def _check_api_documentation(self, entity_name: str, entity_type: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check API documentation for AI/ML endpoints"""
        result = {"ai_detected": False, "ai_systems": [], "ai_capabilities": []}

        # Check metadata for API documentation URLs
        if metadata:
            api_docs = metadata.get("api_documentation", metadata.get("api_docs", ""))
            if api_docs:
                # In real implementation, would fetch and parse API docs
                # For now, check for common AI-related keywords
                ai_keywords = ["ai", "ml", "machine learning", "model", "inference", "llm", "gpt", "claude", "anthropic", "openai"]
                # This would be enhanced with actual API doc parsing
                result["ai_detected"] = any(keyword in str(api_docs).lower() for keyword in ai_keywords)

        return result

    def _check_technical_docs(self, entity_name: str, entity_type: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check technical documentation for AI mentions"""
        result = {"ai_detected": False, "ai_systems": [], "ai_capabilities": []}

        if metadata:
            docs = metadata.get("documentation", metadata.get("docs", ""))
            if docs:
                ai_keywords = ["artificial intelligence", "ai", "machine learning", "neural network", "model", "llm"]
                if any(keyword in str(docs).lower() for keyword in ai_keywords):
                    result["ai_detected"] = True
                    result["ai_capabilities"].append("Documented AI capabilities")

        return result

    def _check_marketing_materials(self, entity_name: str, entity_type: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check marketing materials for AI-powered features"""
        result = {"ai_detected": False, "ai_systems": [], "ai_capabilities": []}

        if metadata:
            marketing = metadata.get("marketing", metadata.get("website", ""))
            if marketing:
                ai_phrases = ["ai-powered", "intelligent", "smart", "automated", "machine learning", "ai assistant"]
                if any(phrase in str(marketing).lower() for phrase in ai_phrases):
                    result["ai_detected"] = True
                    result["ai_capabilities"].append("AI-powered features")

        return result

    def _check_code_analysis(self, entity_name: str, entity_type: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check code for AI library imports or model references"""
        result = {"ai_detected": False, "ai_systems": [], "ai_capabilities": []}

        if metadata:
            code = metadata.get("code", metadata.get("repository", ""))
            if code:
                ai_libraries = ["tensorflow", "pytorch", "transformers", "openai", "anthropic", "langchain", "llama"]
                if any(lib in str(code).lower() for lib in ai_libraries):
                    result["ai_detected"] = True
                    result["ai_capabilities"].append("AI library usage detected")

        return result

    def _check_metadata_indicators(self, entity_name: str, entity_type: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check metadata for explicit AI indicators"""
        result = {"ai_detected": False, "ai_systems": [], "ai_capabilities": []}

        if metadata:
            # Check for explicit AI flags
            if metadata.get("has_ai", False) or metadata.get("ai_enabled", False):
                result["ai_detected"] = True
                result["ai_systems"].append(metadata.get("ai_system_name", "Unknown AI System"))

            # Check for AI-related tags
            tags = metadata.get("tags", [])
            if isinstance(tags, list):
                ai_tags = [tag for tag in tags if "ai" in str(tag).lower() or "ml" in str(tag).lower()]
                if ai_tags:
                    result["ai_detected"] = True
                    result["ai_capabilities"].extend(ai_tags)

        return result

    def _generate_integration_recommendations(self, detection_result: Dict[str, Any]) -> List[str]:
        """Generate integration recommendations based on AI detection"""
        recommendations = []

        if detection_result["ai_detected"]:
            recommendations.append("Establish asynchronous AI-to-AI communications (JARVIS ↔ their AI)")
            recommendations.append("Enable recommendation exchange between AI systems")
            recommendations.append("Set up direct AI-to-AI communication channel")
            recommendations.append("Configure JARVIS for external AI integration mode")
            recommendations.append("Document AI integration capabilities and protocols")

        return recommendations

    def get_actionable_summary(self) -> Dict[str, Any]:
        """Get summary of all actionable items"""
        total_items = sum(len(item.actionable_items) for item in self.extracted_data)
        total_tasks = sum(len(item.tasks) for item in self.extracted_data)
        total_decisions = sum(len(item.decisions) for item in self.extracted_data)
        total_intelligence = sum(len(item.intelligence) for item in self.extracted_data)

        return {
            "total_extracted": len(self.extracted_data),
            "total_actionable_items": total_items,
            "total_tasks": total_tasks,
            "total_decisions": total_decisions,
            "total_intelligence": total_intelligence,
            "by_source_type": {
                source_type.value: len([item for item in self.extracted_data if item.source_type == source_type])
                for source_type in DataSourceType
            }
        }


if __name__ == "__main__":
    # Test the syphon system
    project_root = Path(__file__).parent.parent.parent
    syphon = SYPHONSystem(project_root)

    # Test email syphon
    test_email = syphon.syphon_email(
        email_id="test_001",
        subject="Action Required: Complete Blueprint Implementation",
        body="""
        Hi Team,

        We need to complete the blueprint implementation specifications.

        Action items:
        - Complete API specifications (P0)
        - Define data models (P0)
        - Document Azure configurations (P0)

        Deadline: End of week
        Urgent: Yes

        Please follow up by Friday.
        """,
        from_address="team@example.com",
        to_address="dev@example.com"
    )

    print(f"Extracted {len(test_email.actionable_items)} actionable items")
    print(f"Extracted {len(test_email.tasks)} tasks")
    print(f"Extracted {len(test_email.decisions)} decisions")

    # Test SMS syphon
    test_sms = syphon.syphon_sms(
        sms_id="test_002",
        message="Urgent: Need to deploy P0 containment protocols ASAP. Call me back.",
        from_number="+1234567890",
        to_number="+0987654321"
    )

    print(f"\nSMS extracted {len(test_sms.actionable_items)} actionable items")

    # Get summary
    summary = syphon.get_actionable_summary()
    print(f"\nSummary: {json.dumps(summary, indent=2)}")

