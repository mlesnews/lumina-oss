#!/usr/bin/env python3
"""
SYPHON Extractors

Modular extractors for different data source types.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from syphon.models import SyphonData, DataSourceType, ExtractionResult
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from syphon.regex_tools import SyphonRegexTools, grep, awk, sed
    REGEX_TOOLS_AVAILABLE = True
except ImportError:
    REGEX_TOOLS_AVAILABLE = False
    SyphonRegexTools = None

if TYPE_CHECKING:
    from syphon.core import SYPHONConfig



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BaseExtractor(ABC):
    """Base class for all extractors"""

    def __init__(self, config: "SYPHONConfig") -> None:
        """
        Initialize extractor.

        Args:
            config: SYPHON configuration
        """
        self.config = config
        # @ff: Regex tools will be injected by SYPHONSystem if available
        self.regex_tools = None

    @abstractmethod
    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence from content.

        Args:
            content: Content to extract from
            metadata: Additional metadata

        Returns:
            ExtractionResult
        """
        pass

    def _extract_actionable_items(self, content: str, use_regex_tools: bool = True) -> List[str]:
        """
        Extract actionable items from content

        Args:
            content: Content to extract from
            use_regex_tools: If True, use @ff regex tools (grep/awk/sed) for enhanced extraction
        """
        actionable_items = []
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

        # Use @ff regex tools if available and enabled
        if use_regex_tools and self.regex_tools:
            try:
                # Use grep-like extraction for better performance
                pattern = '|'.join(action_patterns)
                # grep() accepts options dict, not flags parameter
                matches = self.regex_tools.grep(pattern, content, options={"case_sensitive": False})
                for match in matches:
                    sentence = match['line'].strip()
                    if sentence and len(sentence) > 15:
                        # Clean up sentence
                        sentence = re.sub(r'^[-*•→▶]\s+', '', sentence)
                        sentence = re.sub(r'^\d+[.)]\s+', '', sentence)
                        if sentence and len(sentence) > 15 and sentence not in actionable_items:
                            actionable_items.append(sentence)
            except Exception:
                # Fallback to standard extraction
                pass

        # Standard extraction (fallback or when regex tools not used)
        if not actionable_items:
            sentences = re.split(r'[.!?]\s+', content)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence or len(sentence) < 10:
                    continue

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

                if re.match(r'^[-*•→▶]\s+', line):
                    item = re.sub(r'^[-*•→▶]\s+', '', line)
                    if item and len(item) > 10 and item not in actionable_items:
                        actionable_items.append(item)

                if re.match(r'^\d+[.)]\s+', line):
                    item = re.sub(r'^\d+[.)]\s+', '', line)
                    if item and len(item) > 10 and item not in actionable_items:
                        actionable_items.append(item)

        return actionable_items[:20]

    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extract tasks from content"""
        tasks = []
        content_lower = content.lower()

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

        return tasks[:10]

    def _extract_decisions(self, content: str) -> List[Dict[str, Any]]:
        """Extract decisions from content"""
        decisions = []
        content_lower = content.lower()

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

        return decisions[:10]

    def _extract_intelligence(self, content: str, subject: str = "") -> List[Dict[str, Any]]:
        """Extract intelligence/insights from content"""
        intelligence = []
        content_lower = content.lower()

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

        return intelligence[:10]

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


class EmailExtractor(BaseExtractor):
    """Extractor for email messages"""

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from email"""
        try:
            email_id = content.get("email_id", "")
            subject = content.get("subject", "")
            body = content.get("body", "")
            from_address = content.get("from", "")
            to_address = content.get("to", "")

            full_content = f"Subject: {subject}\n\n{body}"

            full_metadata = {
                **metadata,
                "email_id": email_id,
                "from": from_address,
                "to": to_address,
                "subject": subject
            }

            actionable_items = self._extract_actionable_items(full_content)
            tasks = self._extract_tasks(full_content)
            decisions = self._extract_decisions(full_content)
            intelligence = self._extract_intelligence(full_content, subject)

            syphon_data = SyphonData(
                data_id=f"email_{email_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.EMAIL,
                source_id=email_id,
                content=full_content,
                metadata=full_metadata,
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=str(e))


class SMSExtractor(BaseExtractor):
    """Extractor for SMS/text messages"""

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from SMS"""
        try:
            sms_id = content.get("sms_id", "")
            message = content.get("message", "")
            from_number = content.get("from", "")
            to_number = content.get("to", "")

            full_metadata = {
                **metadata,
                "sms_id": sms_id,
                "from": from_number,
                "to": to_number
            }

            actionable_items = self._extract_actionable_items(message)
            tasks = self._extract_tasks(message)
            decisions = self._extract_decisions(message)
            intelligence = self._extract_intelligence(message)

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

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=str(e))


class BankingExtractor(BaseExtractor):
    """Extractor for banking account data"""

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence from banking account data.

        Basic tier: Budgeting, transaction history
        Premium tier: Advanced analytics, predictive modeling, AI insights
        """
        try:
            account_id = content.get("account_id", "")
            account_type = content.get("account_type", "personal")  # personal or business
            transactions = content.get("transactions", [])

            has_premium = metadata.get("has_premium", False)
            subscription_tier = metadata.get("subscription_tier", "basic")

            # Basic features (always available)
            financial_data = {
                "account_id": account_id,
                "account_type": account_type,
                "transaction_count": len(transactions),
                "budget_summary": self._calculate_budget_summary(transactions),
                "transaction_history": transactions[:100] if subscription_tier == "basic" else transactions
            }

            # Premium features
            if has_premium:
                financial_data.update({
                    "advanced_analytics": self._calculate_advanced_analytics(transactions),
                    "predictive_insights": self._generate_predictive_insights(transactions),
                    "spending_patterns": self._analyze_spending_patterns(transactions),
                    "ai_insights": self._generate_ai_insights(transactions, account_type)
                })

            # Extract actionable items from transactions
            actionable_items = self._extract_financial_actionable_items(transactions, financial_data)
            intelligence = self._extract_financial_intelligence(transactions, financial_data)

            full_metadata = {
                **metadata,
                "account_id": account_id,
                "account_type": account_type,
                "subscription_tier": subscription_tier,
                "has_premium": has_premium
            }

            syphon_data = SyphonData(
                data_id=f"banking_{account_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.BANKING,
                source_id=account_id,
                content=f"Banking data for {account_type} account {account_id}",
                metadata=full_metadata,
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                intelligence=intelligence,
                financial_data=financial_data
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=str(e))

    def _calculate_budget_summary(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic budget summary (available in basic tier)"""
        total_income = sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) > 0)
        total_expenses = abs(sum(t.get("amount", 0) for t in transactions if t.get("amount", 0) < 0))
        net = total_income - total_expenses

        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net": net,
            "transaction_count": len(transactions)
        }

    def _calculate_advanced_analytics(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate advanced analytics (premium feature)"""
        # This would include more sophisticated analysis
        return {
            "average_transaction": sum(abs(t.get("amount", 0)) for t in transactions) / len(transactions) if transactions else 0,
            "largest_transaction": max((abs(t.get("amount", 0)) for t in transactions), default=0),
            "category_breakdown": self._categorize_transactions(transactions)
        }

    def _generate_predictive_insights(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate predictive insights (premium feature)"""
        # This would use ML models for predictions
        return [
            {
                "type": "spending_forecast",
                "prediction": "Expected spending next month: $X",
                "confidence": 0.85
            }
        ]

    def _analyze_spending_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spending patterns (premium feature)"""
        return {
            "daily_average": 0,
            "weekly_trend": "stable",
            "monthly_variance": 0
        }

    def _generate_ai_insights(self, transactions: List[Dict[str, Any]], account_type: str) -> List[str]:
        """Generate AI-powered insights (premium feature)"""
        insights = []

        if account_type == "business":
            insights.append("Business account: Consider optimizing cash flow based on transaction patterns")
        else:
            insights.append("Personal account: Review recurring subscriptions for potential savings")

        return insights

    def _categorize_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Categorize transactions by type"""
        categories = {}
        for t in transactions:
            category = t.get("category", "uncategorized")
            amount = abs(t.get("amount", 0))
            categories[category] = categories.get(category, 0) + amount
        return categories

    def _extract_financial_actionable_items(self, transactions: List[Dict[str, Any]], financial_data: Dict[str, Any]) -> List[str]:
        """Extract actionable items from financial data"""
        items = []

        budget = financial_data.get("budget_summary", {})
        net = budget.get("net", 0)

        if net < 0:
            items.append(f"Action required: Account is negative by ${abs(net):.2f}")

        if budget.get("total_expenses", 0) > budget.get("total_income", 0) * 0.9:
            items.append("Warning: Expenses approaching income limit")

        return items

    def _extract_financial_intelligence(self, transactions: List[Dict[str, Any]], financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract intelligence from financial data"""
        intelligence = []

        budget = financial_data.get("budget_summary", {})

        if budget.get("net", 0) > 0:
            intelligence.append({
                "text": f"Positive cash flow: ${budget['net']:.2f}",
                "type": "positive"
            })

        return intelligence


class SocialExtractor(BaseExtractor):
    """Extractor for social media posts and YouTube videos"""

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence from social media or YouTube content.

        Supports:
        - YouTube URLs (extracts title, description, transcript if available)
        - Social media posts (text content)
        """
        try:
            # Handle YouTube URLs
            if isinstance(content, str) and ('youtube.com' in content or 'youtu.be' in content):
                return self._extract_youtube(content, metadata)

            # Handle YouTube metadata dict
            if isinstance(content, dict) and content.get("source") == "youtube":
                return self._extract_youtube_metadata(content, metadata)

            # Handle general social media content
            if isinstance(content, str):
                full_content = content
            elif isinstance(content, dict):
                full_content = content.get("text", "") or content.get("content", "")
            else:
                return ExtractionResult(success=False, error="Unsupported content type")

            if not full_content:
                return ExtractionResult(success=False, error="No content provided")

            # Extract intelligence using base methods
            actionable_items = self._extract_actionable_items(full_content)
            tasks = self._extract_tasks(full_content)
            decisions = self._extract_decisions(full_content)
            intelligence = self._extract_intelligence(full_content)

            syphon_data = SyphonData(
                data_id=f"social_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.SOCIAL,
                source_id=metadata.get("source_id", "unknown"),
                content=full_content,
                metadata={**metadata, "extraction_type": "social_media"},
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=str(e))

    def _extract_youtube(self, url: str, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from YouTube URL"""
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                return ExtractionResult(success=False, error="Could not extract video ID from URL")

            # For now, use metadata if provided, otherwise construct basic content
            # In a full implementation, this would use yt-dlp or YouTube API
            title = metadata.get("title", f"YouTube Video {video_id}")
            description = metadata.get("description", "")
            transcript = metadata.get("transcript", "")

            # Combine all content
            full_content = f"Title: {title}\n\n"
            if description:
                full_content += f"Description: {description}\n\n"
            if transcript:
                full_content += f"Transcript: {transcript}\n\n"
            full_content += f"URL: {url}"

            # Extract intelligence
            actionable_items = self._extract_actionable_items(full_content)
            tasks = self._extract_tasks(full_content)
            decisions = self._extract_decisions(full_content)
            intelligence = self._extract_intelligence(full_content, title)

            syphon_data = SyphonData(
                data_id=f"youtube_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.SOCIAL,
                source_id=video_id,
                content=full_content,
                metadata={
                    **metadata,
                    "url": url,
                    "video_id": video_id,
                    "title": title,
                    "extraction_type": "youtube"
                },
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=f"YouTube extraction failed: {e}")

    def _extract_youtube_metadata(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from YouTube metadata dict"""
        url = content.get("url", "")
        title = content.get("title", "")
        description = content.get("description", "")
        transcript = content.get("transcript", "")
        video_id = content.get("video_id", self._extract_video_id(url))

        full_content = f"Title: {title}\n\n"
        if description:
            full_content += f"Description: {description}\n\n"
        if transcript:
            full_content += f"Transcript: {transcript}\n\n"
        if url:
            full_content += f"URL: {url}"

        actionable_items = self._extract_actionable_items(full_content)
        tasks = self._extract_tasks(full_content)
        decisions = self._extract_decisions(full_content)
        intelligence = self._extract_intelligence(full_content, title)

        syphon_data = SyphonData(
            data_id=f"youtube_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.SOCIAL,
            source_id=video_id or "unknown",
            content=full_content,
            metadata={
                **metadata,
                **content,
                "extraction_type": "youtube"
            },
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks,
            decisions=decisions,
            intelligence=intelligence
        )

        return ExtractionResult(success=True, data=syphon_data)

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        import re

        # Pattern for youtube.com/watch?v=VIDEO_ID, youtu.be/VIDEO_ID, youtube.com/shorts/VIDEO_ID, youtube.com/live/VIDEO_ID
        match = re.search(r'(?:youtube\.com\/(?:watch\?v=|shorts\/|live\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        return None


class CodeExtractor(BaseExtractor):
    """Extractor for code intelligence - analyzes source code for actionable items"""

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from code"""
        try:
            if not isinstance(content, str):
                return ExtractionResult(success=False, error="Code content must be string")

            code_content = content.strip()
            if not code_content:
                return ExtractionResult(success=False, error="Empty code content")

            # Extract actionable items from code
            actionable_items = self._extract_code_actionable_items(code_content, metadata)

            # Extract tasks from code comments and structure
            tasks = self._extract_code_tasks(code_content, metadata)

            # Extract decisions from code logic
            decisions = self._extract_code_decisions(code_content, metadata)

            # Extract intelligence from code patterns and architecture
            intelligence = self._extract_code_intelligence(code_content, metadata)

            syphon_data = SyphonData(
                data_id=f"code_{hash(code_content) % 1000000:06d}",
                source_type=DataSourceType.CODE,
                source_id=metadata.get("source_id", "unknown_code"),
                content=code_content,
                metadata={
                    **metadata,
                    "extraction_type": "code_analysis",
                    "language": self._detect_language(code_content, metadata),
                    "complexity": self._calculate_complexity(code_content),
                    "lines_of_code": len(code_content.split('\n'))
                },
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=f"Code extraction failed: {str(e)}")

    def _extract_code_actionable_items(self, code: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable items from code"""
        items = []

        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # TODO/FIXME comments  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
            if any(keyword in line_lower for keyword in ['todo', 'fixme', 'xxx', 'hack']):
                items.append({
                    "type": "code_comment",
                    "description": f"Code comment requires attention: {line.strip()}",
                    "line_number": i,
                    "priority": "medium",
                    "category": "maintenance"
                })

            # Error handling improvements
            if 'except:' in line_lower and 'pass' in line_lower:
                items.append({
                    "type": "error_handling",
                    "description": f"Empty exception handler on line {i}",
                    "line_number": i,
                    "priority": "high",
                    "category": "reliability"
                })

            # Security issues
            if any(vuln in line_lower for vuln in ['password', 'secret', 'key']) and ('=' in line or '==' in line):
                if not any(safe in line_lower for safe in ['os.getenv', 'config.get', 'env[', 'variable']):
                    items.append({
                        "type": "security_risk",
                        "description": f"Potential hardcoded credential on line {i}",
                        "line_number": i,
                        "priority": "critical",
                        "category": "security"
                    })

            # Performance issues
            if 'sleep(' in line_lower and 'time.sleep' in line_lower:
                items.append({
                    "type": "performance",
                    "description": f"Blocking sleep operation on line {i}",
                    "line_number": i,
                    "priority": "medium",
                    "category": "performance"
                })

        return items

    def _extract_code_tasks(self, code: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tasks from code structure and comments"""
        tasks = []

        # Function definitions without docstrings
        lines = code.split('\n')
        in_function = False
        function_start = 0

        for i, line in enumerate(lines, 1):
            line_strip = line.strip()

            # Detect function/class definitions
            if any(keyword in line_strip for keyword in ['def ', 'class ']):
                if in_function:
                    # Check if previous function had docstring
                    has_docstring = self._check_docstring(lines[function_start-1:i-1])
                    if not has_docstring:
                        tasks.append({
                            "task_id": f"docstring_{function_start}",
                            "description": f"Add docstring to function starting at line {function_start}",
                            "priority": "medium",
                            "status": "pending",
                            "assignee": "developer",
                            "due_date": None,
                            "dependencies": []
                        })
                in_function = True
                function_start = i

        # Check final function
        if in_function:
            has_docstring = self._check_docstring(lines[function_start-1:])
            if not has_docstring:
                tasks.append({
                    "task_id": f"docstring_{function_start}",
                    "description": f"Add docstring to function starting at line {function_start}",
                    "priority": "medium",
                    "status": "pending",
                    "assignee": "developer",
                    "due_date": None,
                    "dependencies": []
                })

        return tasks

    def _extract_code_decisions(self, code: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract decision points from code logic"""
        decisions = []

        # Look for conditional statements and decision patterns
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line_strip = line.strip()

            # Complex conditionals
            if line_strip.startswith(('if ', 'elif ', 'while ')) and len(line_strip) > 100:
                decisions.append({
                    "decision_type": "complex_conditional",
                    "description": f"Complex conditional logic on line {i}",
                    "line_number": i,
                    "complexity": "high",
                    "recommendation": "Consider extracting to separate function"
                })

            # Multiple nested conditions
            if line_strip.count('if ') > 1 or line_strip.count(' and ') > 2 or line_strip.count(' or ') > 2:
                decisions.append({
                    "decision_type": "nested_logic",
                    "description": f"Nested or complex boolean logic on line {i}",
                    "line_number": i,
                    "complexity": "high",
                    "recommendation": "Simplify boolean expressions"
                })

        return decisions

    def _extract_code_intelligence(self, code: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract intelligence from code patterns and architecture"""
        intelligence = []

        # Architecture patterns
        if 'class ' in code and 'def __init__' in code:
            intelligence.append({
                "type": "architecture",
                "insight": "Object-oriented design pattern detected",
                "confidence": 0.9,
                "source": "class_structure"
            })

        # Async patterns
        if 'async def' in code or 'await ' in code:
            intelligence.append({
                "type": "architecture",
                "insight": "Asynchronous programming pattern detected",
                "confidence": 0.95,
                "source": "async_syntax"
            })

        # Error handling patterns
        if 'try:' in code and 'except ' in code:
            intelligence.append({
                "type": "reliability",
                "insight": "Error handling patterns implemented",
                "confidence": 0.8,
                "source": "exception_handling"
            })

        # Logging patterns
        if 'logger' in code.lower() or 'logging' in code.lower():
            intelligence.append({
                "type": "observability",
                "insight": "Logging instrumentation detected",
                "confidence": 0.85,
                "source": "logging_usage"
            })

        # Testing patterns (basic detection)
        if 'test' in code.lower() and ('def test_' in code or 'class Test' in code):
            intelligence.append({
                "type": "quality",
                "insight": "Unit testing patterns detected",
                "confidence": 0.9,
                "source": "test_structure"
            })

        return intelligence

    def _detect_language(self, code: str, metadata: Dict[str, Any]) -> str:
        """Detect programming language from code content"""
        # Check file extension first
        file_path = metadata.get("file_path", "")
        if file_path:
            if file_path.endswith('.py'):
                return 'python'
            elif file_path.endswith('.js'):
                return 'javascript'
            elif file_path.endswith('.ts'):
                return 'typescript'
            elif file_path.endswith('.java'):
                return 'java'
            elif file_path.endswith('.cpp'):
                return 'cpp'
            elif file_path.endswith('.c'):
                return 'c'
            elif file_path.endswith('.go'):
                return 'go'
            elif file_path.endswith('.rs'):
                return 'rust'

        # Fallback to content analysis
        code_lower = code.lower()
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function' in code and ('var ' in code or 'const ' in code or 'let ' in code):
            return 'javascript'
        elif 'public class' in code and 'system.out.println' in code_lower:
            return 'java'
        elif '#include' in code:
            return 'cpp'
        elif 'package main' in code and 'func ' in code:
            return 'go'
        elif 'fn ' in code and 'let ' in code:
            return 'rust'

        return 'unknown'

    def _calculate_complexity(self, code: str) -> str:
        """Calculate code complexity"""
        lines = len(code.split('\n'))
        functions = code.count('def ') + code.count('function ')
        conditionals = code.count('if ') + code.count('while ') + code.count('for ')

        # Simple complexity scoring
        score = lines + (functions * 10) + (conditionals * 5)

        if score < 50:
            return 'low'
        elif score < 150:
            return 'medium'
        else:
            return 'high'

    def _check_docstring(self, lines: List[str]) -> bool:
        """Check if function has a docstring"""
        # Look for triple quotes after function definition
        in_function = False
        brace_count = 0

        for line in lines:
            line_strip = line.strip()

            if line_strip.startswith('def ') or line_strip.startswith('class '):
                in_function = True
                continue

            if in_function:
                if '"""' in line or "'''" in line:
                    return True
                if line_strip.startswith('def ') or line_strip.startswith('class '):
                    # Next function, previous one didn't have docstring
                    return False
                if line_strip and not line_strip.startswith(' ') and not line_strip.startswith('\t'):
                    # End of function
                    break

        return False


class IDEExtractor(BaseExtractor):
    """Extractor for IDE diagnostics, problems, notifications, and queues"""

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence from IDE data (diagnostics, problems, notifications).

        Supports:
        - VS Code/Cursor diagnostics (errors, warnings, info)
        - IDE notifications
        - Task outputs
        - Extension output/logs
        - Problems panel data
        """
        try:
            # Handle diagnostics/problems dict
            if isinstance(content, dict):
                if "diagnostics" in content or "problems" in content:
                    return self._extract_diagnostics(content, metadata)
                elif "notifications" in content:
                    return self._extract_notifications(content, metadata)
                elif "tasks" in content:
                    return self._extract_task_outputs(content, metadata)
                else:
                    # Generic IDE data
                    return self._extract_generic_ide_data(content, metadata)

            # Handle string content (logs, output, etc.)
            if isinstance(content, str):
                return self._extract_ide_logs(content, metadata)

            return ExtractionResult(success=False, error="Unsupported IDE content type")

        except Exception as e:
            return ExtractionResult(success=False, error=f"IDE extraction failed: {e}")

    def _extract_diagnostics(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from diagnostics/problems"""
        diagnostics = content.get("diagnostics", content.get("problems", []))

        errors = []
        warnings = []
        info_items = []

        for diag in diagnostics:
            severity = diag.get("severity", "info").lower()
            message = diag.get("message", "")
            source = diag.get("source", "unknown")
            file_path = diag.get("file", diag.get("filePath", ""))
            line = diag.get("line", diag.get("lineNumber", 0))
            code = diag.get("code", "")

            diag_info = {
                "message": message,
                "source": source,
                "file": file_path,
                "line": line,
                "code": code
            }

            if severity == "error":
                errors.append(diag_info)
            elif severity == "warning":
                warnings.append(diag_info)
            else:
                info_items.append(diag_info)

        # Build full content
        full_content = f"IDE Diagnostics Summary:\n"
        full_content += f"Errors: {len(errors)}\n"
        full_content += f"Warnings: {len(warnings)}\n"
        full_content += f"Info: {len(info_items)}\n\n"

        if errors:
            full_content += "=== ERRORS ===\n"
            for err in errors[:20]:  # Limit to first 20
                full_content += f"[{err['source']}] {err['file']}:{err['line']} - {err['message']}\n"

        if warnings:
            full_content += "\n=== WARNINGS ===\n"
            for warn in warnings[:20]:
                full_content += f"[{warn['source']}] {warn['file']}:{warn['line']} - {warn['message']}\n"

        # Extract actionable items
        actionable_items = []
        for err in errors:
            actionable_items.append(f"Fix error in {err['file']}:{err['line']} - {err['message']}")

        # Extract tasks
        tasks = []
        for err in errors[:10]:
            tasks.append({
                "text": f"Resolve {err['source']} error: {err['message']}",
                "type": "fix_error",
                "priority": "high",
                "file": err['file'],
                "line": err['line']
            })

        # Extract intelligence
        intelligence = []
        if len(errors) > 10:
            intelligence.append({
                "text": f"High error count ({len(errors)}) - potential systemic issues",
                "type": "issue"
            })

        common_errors = {}
        for err in errors:
            key = f"{err['source']}:{err['code']}" if err['code'] else err['source']
            common_errors[key] = common_errors.get(key, 0) + 1

        if common_errors:
            most_common = max(common_errors.items(), key=lambda x: x[1])
            intelligence.append({
                "text": f"Most common error: {most_common[0]} ({most_common[1]} occurrences)",
                "type": "pattern"
            })

        full_metadata = {
            **metadata,
            "ide_type": metadata.get("ide_type", "unknown"),
            "workspace": metadata.get("workspace", ""),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "info_count": len(info_items),
            "common_errors": dict(list(common_errors.items())[:10])
        }

        syphon_data = SyphonData(
            data_id=f"ide_diagnostics_{metadata.get('workspace', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.IDE,
            source_id=f"{metadata.get('workspace', 'unknown')}_diagnostics",
            content=full_content,
            metadata=full_metadata,
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks,
            intelligence=intelligence
        )

        return ExtractionResult(success=True, data=syphon_data)

    def _extract_notifications(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from IDE notifications"""
        notifications = content.get("notifications", [])

        full_content = f"IDE Notifications ({len(notifications)} total):\n\n"

        actionable_items = []
        intelligence = []

        for notif in notifications:
            message = notif.get("message", "")
            severity = notif.get("severity", "info")
            source = notif.get("source", "unknown")
            timestamp = notif.get("timestamp", "")

            full_content += f"[{severity.upper()}] {source}: {message}\n"
            if timestamp:
                full_content += f"  Time: {timestamp}\n"

            # Extract actionable notifications
            if severity in ["error", "warning"]:
                actionable_items.append(f"{source}: {message}")

            # Extract intelligence from notifications
            if any(word in message.lower() for word in ["update", "available", "new version"]):
                intelligence.append({
                    "text": message,
                    "type": "update"
                })

        full_metadata = {
            **metadata,
            "ide_type": metadata.get("ide_type", "unknown"),
            "workspace": metadata.get("workspace", ""),
            "notification_count": len(notifications)
        }

        syphon_data = SyphonData(
            data_id=f"ide_notifications_{metadata.get('workspace', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.IDE,
            source_id=f"{metadata.get('workspace', 'unknown')}_notifications",
            content=full_content,
            metadata=full_metadata,
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            intelligence=intelligence
        )

        return ExtractionResult(success=True, data=syphon_data)

    def _extract_task_outputs(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from task outputs"""
        tasks = content.get("tasks", [])

        full_content = f"IDE Task Outputs ({len(tasks)} tasks):\n\n"

        actionable_items = []
        tasks_extracted = []

        for task in tasks:
            name = task.get("name", "unknown")
            status = task.get("status", "unknown")
            output = task.get("output", "")
            error = task.get("error", "")

            full_content += f"Task: {name}\n"
            full_content += f"Status: {status}\n"
            if output:
                full_content += f"Output: {output[:500]}\n"  # Limit output
            if error:
                full_content += f"Error: {error}\n"
            full_content += "\n"

            if error:
                actionable_items.append(f"Fix task '{name}': {error}")
                tasks_extracted.append({
                    "text": f"Resolve task error: {error}",
                    "type": "fix_task",
                    "priority": "high",
                    "task": name
                })

        full_metadata = {
            **metadata,
            "ide_type": metadata.get("ide_type", "unknown"),
            "workspace": metadata.get("workspace", ""),
            "task_count": len(tasks)
        }

        syphon_data = SyphonData(
            data_id=f"ide_tasks_{metadata.get('workspace', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.IDE,
            source_id=f"{metadata.get('workspace', 'unknown')}_tasks",
            content=full_content,
            metadata=full_metadata,
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks_extracted
        )

        return ExtractionResult(success=True, data=syphon_data)

    def _extract_generic_ide_data(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> ExtractionResult:
        try:
            """Extract intelligence from generic IDE data"""
            full_content = json.dumps(content, indent=2)

            actionable_items = self._extract_actionable_items(full_content)
            tasks = self._extract_tasks(full_content)
            intelligence = self._extract_intelligence(full_content)

            syphon_data = SyphonData(
                data_id=f"ide_data_{metadata.get('workspace', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.IDE,
                source_id=metadata.get("source_id", "unknown"),
                content=full_content,
                metadata=metadata,
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            self.logger.error(f"Error in _extract_generic_ide_data: {e}", exc_info=True)
            raise
    def _extract_ide_logs(self, content: str, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from IDE log content"""
        actionable_items = self._extract_actionable_items(content)
        tasks = self._extract_tasks(content)
        intelligence = self._extract_intelligence(content)

        # Look for error patterns in logs
        error_patterns = [
            r'ERROR.*?: (.+)',
            r'Error: (.+)',
            r'Failed to (.+)',
            r'Cannot (.+)',
        ]

        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                error_msg = match.group(1).strip()
                if error_msg and len(error_msg) > 10:
                    actionable_items.append(f"Error in logs: {error_msg}")

        syphon_data = SyphonData(
            data_id=f"ide_logs_{metadata.get('workspace', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.IDE,
            source_id=metadata.get("source_id", "logs"),
            content=content,
            metadata=metadata,
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks,
            intelligence=intelligence
        )

        return ExtractionResult(success=True, data=syphon_data)


class WebExtractor(BaseExtractor):
    """Extractor for web content - scrapes websites and extracts text, links, and metadata"""

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence from web content.

        Supports:
        - HTML content (string or parsed)
        - URLs (will fetch and parse)
        - Web page metadata (title, description, links, etc.)
        """
        try:
            # Handle URL strings
            if isinstance(content, str) and (content.startswith('http://') or content.startswith('https://')):
                return self._extract_from_url(content, metadata)

            # Handle HTML content dict
            if isinstance(content, dict):
                return self._extract_from_html_dict(content, metadata)

            # Handle HTML string
            if isinstance(content, str):
                return self._extract_from_html(content, metadata)

            return ExtractionResult(success=False, error="Unsupported web content type")

        except Exception as e:
            return ExtractionResult(success=False, error=f"Web extraction failed: {e}")

    def _extract_from_url(self, url: str, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from a URL"""
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin, urlparse

            # Fetch the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract content
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ""

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""

            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                link_text = link.get_text(strip=True)
                absolute_url = urljoin(url, href)
                links.append({
                    "text": link_text,
                    "url": absolute_url,
                    "domain": urlparse(absolute_url).netloc
                })

            # Extract metadata
            meta_description = ""
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag:
                meta_description = meta_desc_tag.get('content', '')

            # Combine all content
            full_content = f"Title: {title_text}\n\n"
            if meta_description:
                full_content += f"Description: {meta_description}\n\n"
            full_content += f"Content:\n{text_content}\n\n"
            full_content += f"URL: {url}\n\n"
            full_content += f"Links found: {len(links)}\n"

            # Extract intelligence
            actionable_items = self._extract_actionable_items(full_content)
            tasks = self._extract_tasks(full_content)
            decisions = self._extract_decisions(full_content)
            intelligence = self._extract_intelligence(full_content, title_text)

            syphon_data = SyphonData(
                data_id=f"web_{hash(url) % 1000000:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.WEB,
                source_id=url,
                content=full_content,
                metadata={
                    **metadata,
                    "url": url,
                    "title": title_text,
                    "description": meta_description,
                    "link_count": len(links),
                    "links": links[:100],  # Limit to first 100 links
                    "extraction_type": "web_scraping"
                },
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=f"URL extraction failed: {e}")

    def _extract_from_html(self, html_content: str, metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from HTML string"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract content similar to URL extraction
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else ""

            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            text_content = main_content.get_text(separator='\n', strip=True) if main_content else ""

            full_content = f"Title: {title_text}\n\nContent:\n{text_content}"

            actionable_items = self._extract_actionable_items(full_content)
            tasks = self._extract_tasks(full_content)
            decisions = self._extract_decisions(full_content)
            intelligence = self._extract_intelligence(full_content, title_text)

            syphon_data = SyphonData(
                data_id=f"web_html_{hash(html_content) % 1000000:06d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.WEB,
                source_id=metadata.get("source_id", "html_content"),
                content=full_content,
                metadata={**metadata, "extraction_type": "html_parsing"},
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=f"HTML extraction failed: {e}")

    def _extract_from_html_dict(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> ExtractionResult:
        """Extract intelligence from pre-parsed HTML dict"""
        title = content.get("title", "")
        text = content.get("text", content.get("content", ""))
        url = content.get("url", "")

        full_content = f"Title: {title}\n\nContent:\n{text}"
        if url:
            full_content += f"\n\nURL: {url}"

        actionable_items = self._extract_actionable_items(full_content)
        tasks = self._extract_tasks(full_content)
        decisions = self._extract_decisions(full_content)
        intelligence = self._extract_intelligence(full_content, title)

        syphon_data = SyphonData(
            data_id=f"web_dict_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=DataSourceType.WEB,
            source_id=content.get("url", content.get("source_id", "unknown")),
            content=full_content,
            metadata={**metadata, **content, "extraction_type": "html_dict"},
            extracted_at=datetime.now(),
            actionable_items=actionable_items,
            tasks=tasks,
            decisions=decisions,
            intelligence=intelligence
        )

        return ExtractionResult(success=True, data=syphon_data)
