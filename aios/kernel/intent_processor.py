"""Intent Processor Module

This module provides the core intent processing logic used by the @AIOS kernel.
Uses local LLM models via LiteLLM gateway for real intent classification.
Falls back to keyword pattern matching when LLM is unavailable.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("IntentProcessor")

# Intent categories the system recognizes
KNOWN_INTENTS = [
    "execute_trade",
    "analyze_market",
    "check_portfolio",
    "run_strategy",
    "system_health",
    "configure_settings",
    "search_knowledge",
    "generate_report",
    "schedule_task",
    "general_query",
]

# Keyword patterns for fast fallback classification
KEYWORD_PATTERNS: Dict[str, List[str]] = {
    "execute_trade": ["buy", "sell", "trade", "order", "execute", "position", "long", "short"],
    "analyze_market": ["analyze", "analysis", "market", "price", "chart", "trend", "signal"],
    "check_portfolio": ["portfolio", "balance", "holdings", "net worth", "allocation", "assets"],
    "run_strategy": ["strategy", "backtest", "simulate", "collider", "molecule", "particle", "spice"],
    "system_health": ["health", "status", "monitor", "uptime", "cluster", "node", "container"],
    "configure_settings": ["configure", "config", "settings", "set", "update", "change", "toggle"],
    "search_knowledge": ["search", "find", "lookup", "query", "knowledge", "rag", "archives"],
    "generate_report": ["report", "summary", "overview", "digest", "snapshot"],
    "schedule_task": ["schedule", "cron", "automate", "recurring", "timer", "interval"],
}


class IntentProcessor:
    """Handles natural language intent extraction.

    Primary: LLM-based classification via LiteLLM gateway.
    Fallback: Keyword pattern matching for speed and offline operation.
    """

    def __init__(self, llm_base_url: str = "http://localhost:8080"):
        self._llm_base_url = llm_base_url
        self._llm_model = "ollama/qwen2.5:7b"  # Fast local model for classification

    async def understand_with_ai_native_processing(
        self, raw_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process input using AI-native capabilities.

        Sends the raw input to a local LLM for intent classification.
        Falls back to keyword matching if the LLM is unavailable.

        Parameters
        ----------
        raw_input : str
            The raw user input.
        context : Dict[str, Any]
            Current system context.

        Returns
        -------
        Dict[str, Any]
            A dictionary with intent, confidence, entities, and metadata.
        """
        # Try LLM-based classification first
        try:
            return await self._classify_with_llm(raw_input, context)
        except Exception as e:
            logger.debug(f"LLM classification unavailable ({e}), using pattern fallback")
            return await self._process_with_legacy_patterns(raw_input)

    async def _classify_with_llm(
        self, raw_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classify intent using local LLM via LiteLLM gateway."""
        import httpx

        prompt = (
            "Classify the following user request into exactly one intent category.\n"
            f"Categories: {', '.join(KNOWN_INTENTS)}\n\n"
            f"User request: {raw_input}\n\n"
            "Respond with ONLY a JSON object:\n"
            '{"intent": "<category>", "confidence": <0.0-1.0>, '
            '"entities": {"key": "value"}, "reasoning": "<brief>"}'
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._llm_base_url}/v1/chat/completions",
                json={
                    "model": self._llm_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an intent classifier for a trading and automation system. "
                                "Return ONLY valid JSON with intent, confidence, entities, reasoning."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200,
                },
            )
            resp.raise_for_status()

        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Parse JSON from response
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(0))
            # Validate intent is known
            if result.get("intent") not in KNOWN_INTENTS:
                result["intent"] = "general_query"
                result["confidence"] = max(0.3, result.get("confidence", 0.5) - 0.2)
            result["metadata"] = {"source": "ai_native", "model": self._llm_model}
            return result

        # If LLM didn't return valid JSON, fall through to patterns
        raise ValueError("LLM response was not valid JSON")

    async def _process_with_legacy_patterns(
        self, raw_input: str
    ) -> Dict[str, Any]:
        """Fallback processing using keyword pattern matching.

        Parameters
        ----------
        raw_input : str
            The raw user input to classify.

        Returns
        -------
        Dict[str, Any]
            Classified intent with confidence score.
        """
        text_lower = raw_input.lower()
        best_intent = "general_query"
        best_score = 0.0

        for intent, keywords in KEYWORD_PATTERNS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                score = min(0.9, matches * 0.25)
                if score > best_score:
                    best_score = score
                    best_intent = intent

        # Base confidence for pattern matching is lower than LLM
        confidence = max(0.3, best_score) if best_intent != "general_query" else 0.3

        return {
            "intent": best_intent,
            "confidence": confidence,
            "entities": {},
            "metadata": {"source": "keyword_patterns"},
        }
