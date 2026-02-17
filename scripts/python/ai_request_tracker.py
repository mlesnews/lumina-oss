from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("ai_request_tracker")




# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AIRequestTracker:
    """Unified tracker for AI agent requests with lookback and budget checks."""

    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path).resolve()
        self.config = self._load_config()
        self.lookback_windows = self.config["lookback_configuration"][
            "lookback_windows"
        ]
        self.retention_days = int(
            self.config["request_tracking"].get("retention_days", 90)
        )
        self.storage_path = self._resolve_storage_path()
        self.request_log: List[Dict[str, Any]] = []
        self._ensure_storage_dir()
        self._hydrate_from_disk()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def _resolve_storage_path(self) -> Path:
        try:
            raw_path = self.config["request_tracking"]["storage_location"]
            storage = Path(raw_path)
            if not storage.is_absolute():
                project_root = self.config_path.parents[2]
                storage = project_root / storage
            return storage

        except Exception as e:
            self.logger.error(f"Error in _resolve_storage_path: {e}", exc_info=True)
            raise
    def _ensure_storage_dir(self) -> None:
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _hydrate_from_disk(self) -> None:
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        if not self.storage_path.exists():
            return
        for path in sorted(self.storage_path.glob("*.jsonl")):
            try:
                date_part = path.stem
                file_date = datetime.strptime(date_part, "%Y%m%d")
            except ValueError:
                continue
            if file_date < cutoff:
                continue
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        self.request_log.append(record)
                    except json.JSONDecodeError:
                        continue

    def _persist_request(self, record: Dict[str, Any]) -> None:
        try:
            day = datetime.utcfromtimestamp(record["timestamp"]).strftime("%Y%m%d")
            file_path = self.storage_path / f"{day}.jsonl"
            with file_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")

        except Exception as e:
            self.logger.error(f"Error in _persist_request: {e}", exc_info=True)
            raise
    def _update_metrics(self, record: Dict[str, Any]) -> None:
        metrics = self.config.get("metrics", {})
        metrics["total_requests"] = metrics.get("total_requests", 0) + 1
        if record["status"] == "success":
            metrics["successful_requests"] = metrics.get("successful_requests", 0) + 1
        if record["status"] == "failed":
            metrics["failed_requests"] = metrics.get("failed_requests", 0) + 1
        metrics["total_tokens_used"] = (
            metrics.get("total_tokens_used", 0) + record["total_tokens"]
        )
        total_requests = metrics.get("total_requests", 1)
        metrics["avg_tokens_per_request"] = (
            metrics["total_tokens_used"] / total_requests
        )
        successful = metrics.get("successful_requests", 0)
        metrics["success_rate"] = successful / total_requests if total_requests else 0
        metrics["last_request_timestamp"] = record["timestamp"]
        self.config["metrics"] = metrics

    def _update_budgets(self, provider: Optional[str], total_tokens: int) -> None:
        if not provider:
            return
        budgets = self.config.get("token_budgets", {})
        if provider not in budgets:
            return
        budget = budgets[provider]
        budget["current_used_today"] = (
            budget.get("current_used_today", 0) + total_tokens
        )
        budget["current_used_month"] = (
            budget.get("current_used_month", 0) + total_tokens
        )
        budgets[provider] = budget
        self.config["token_budgets"] = budgets

    def log_request(
        self,
        request_id: str,
        agent: str,
        prompt_tokens: int,
        completion_tokens: int,
        status: str,
        provider: Optional[str] = None,
        result: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        timestamp = time.time()
        record = {
            "request_id": request_id,
            "timestamp": timestamp,
            "agent": agent,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "status": status,
            "provider": provider,
            "result": result,
            "error": error,
        }
        self.request_log.append(record)
        self._persist_request(record)
        self._update_metrics(record)
        self._update_budgets(provider, record["total_tokens"])
        return record

    def get_recent_requests(self, window: str = "session") -> List[Dict[str, Any]]:
        if window not in self.lookback_windows:
            raise ValueError(f"Unknown lookback window: {window}")
        window_seconds = self.lookback_windows[window]["seconds"]
        cutoff = time.time() - window_seconds
        return [req for req in self.request_log if req["timestamp"] >= cutoff]

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        for req in reversed(self.request_log):
            if req.get("request_id") == request_id:
                return req
        return None

    def analyze_token_usage(
        self, window: str = "session", agent: Optional[str] = None
    ) -> Dict[str, Any]:
        recent = self.get_recent_requests(window)
        if agent:
            recent = [r for r in recent if r.get("agent") == agent]
        total_tokens = sum(r.get("total_tokens", 0) for r in recent)
        request_count = len(recent)
        successes = len([r for r in recent if r.get("status") == "success"])
        failures = len([r for r in recent if r.get("status") == "failed"])
        return {
            "window": window,
            "request_count": request_count,
            "successful": successes,
            "failed": failures,
            "total_tokens": total_tokens,
            "avg_tokens_per_request": total_tokens / request_count
            if request_count
            else 0,
            "peak_tokens": max((r.get("total_tokens", 0) for r in recent), default=0),
            "agents": list({r.get("agent") for r in recent}),
        }

    def check_budget_health(self, provider: str) -> Dict[str, Any]:
        budgets = self.config.get("token_budgets", {})
        if provider not in budgets:
            raise ValueError(f"Unknown provider: {provider}")
        budget = budgets[provider]
        daily_limit = budget.get("daily_limit", 0)
        used_today = budget.get("current_used_today", 0)
        warning_threshold = budget.get("warning_threshold", 0.8)
        used_percent = used_today / daily_limit if daily_limit else 0
        if used_percent >= 1.0:
            warning = "limit_exceeded"
        elif used_percent >= warning_threshold:
            warning = "warning"
        else:
            warning = "normal"
        return {
            "provider": provider,
            "used_today": used_today,
            "daily_limit": daily_limit,
            "used_percent": used_percent,
            "remaining": max(0, daily_limit - used_today),
            "warning_level": warning,
        }

    def get_failed_requests(self, window: str = "session") -> List[Dict[str, Any]]:
        recent = self.get_recent_requests(window)
        return [r for r in recent if r.get("status") == "failed"]

    def get_request_timeline(self, window: str = "session") -> List[Dict[str, Any]]:
        recent = self.get_recent_requests(window)
        return sorted(recent, key=lambda x: x.get("timestamp", 0))

    def estimate_remaining_budget(self, provider: str) -> Dict[str, Any]:
        budgets = self.config.get("token_budgets", {})
        if provider not in budgets:
            raise ValueError(f"Unknown provider: {provider}")
        budget = budgets[provider]
        remaining_tokens = max(
            0, budget.get("daily_limit", 0) - budget.get("current_used_today", 0)
        )
        recent_usage = self.analyze_token_usage(window="session")
        avg_tokens = recent_usage.get("avg_tokens_per_request", 0)
        if avg_tokens > 0:
            estimated_requests = int(remaining_tokens / avg_tokens)
        else:
            estimated_requests = 0
        return {
            "provider": provider,
            "remaining_tokens": remaining_tokens,
            "estimated_requests": estimated_requests,
            "avg_tokens_per_request": avg_tokens,
        }

    # ===== MASTER/PADAWAN LEARNING INTEGRATION =====

    def log_learning_interaction(
        self,
        request_id: str,
        agent: str,
        learner_role: str,
        teaching_topic: str,
        prompt_tokens: int,
        completion_tokens: int,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log Master/Padawan learning interaction with role-based token multipliers.

        Args:
            learner_role: 'master' (teaching) or 'padawan' (learning)
            teaching_topic: e.g., 'pattern_registry', 'error_handling', 'optimization'
        """
        master_padawan_config = self.config.get("master_padawan_learning", {})
        role_config = master_padawan_config.get(
            "master_mode" if learner_role == "master" else "padawan_mode", {}
        )
        token_multiplier = role_config.get("token_multiplier", 1.0)
        effective_tokens = int((prompt_tokens + completion_tokens) * token_multiplier)

        record = self.log_request(
            request_id=request_id,
            agent=agent,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            status="success",
            provider=provider,
            result=f"{learner_role}_teaching_topic_{teaching_topic}",
        )
        record.update(
            {
                "learner_role": learner_role,
                "teaching_topic": teaching_topic,
                "token_class": role_config.get(
                    "token_class",
                    "teaching" if learner_role == "master" else "learning",
                ),
                "effective_tokens": effective_tokens,
                "token_multiplier": token_multiplier,
            }
        )
        return record

    def get_learning_progress(
        self, agent: str, window: str = "weekly"
    ) -> Dict[str, Any]:
        """Get learning progress for an agent across Master/Padawan sessions."""
        recent = self.get_recent_requests(window)
        padawan_sessions = [
            r
            for r in recent
            if r.get("agent") == agent and r.get("learner_role") == "padawan"
        ]
        master_sessions = [
            r
            for r in recent
            if r.get("agent") == agent and r.get("learner_role") == "master"
        ]
        learning_tokens = sum(r.get("total_tokens", 0) for r in padawan_sessions)
        teaching_tokens = sum(r.get("total_tokens", 0) for r in master_sessions)
        total = learning_tokens + teaching_tokens
        return {
            "agent": agent,
            "window": window,
            "learning_sessions": len(padawan_sessions),
            "teaching_sessions": len(master_sessions),
            "learning_tokens": learning_tokens,
            "teaching_tokens": teaching_tokens,
            "learning_rate": learning_tokens / total if total > 0 else 0,
            "topics_covered": list(
                {
                    r.get("teaching_topic")
                    for r in (padawan_sessions + master_sessions)
                    if r.get("teaching_topic")
                }
            ),
        }

    def classify_session_type(self, chat_history: List[Dict[str, str]]) -> str:
        """
        Classify chat session as teaching, learning, practice, or validation.
        Uses keywords and interaction patterns from chat history.
        """
        teaching_keywords = [
            "explain",
            "show you",
            "teach",
            "demonstrate",
            "pattern",
            "best practice",
        ]
        learning_keywords = [
            "learn",
            "understand",
            "how do i",
            "why",
            "clarify",
            "example",
        ]
        practice_keywords = ["try", "apply", "implement", "practice", "code", "execute"]
        validation_keywords = [
            "mastery",
            "ready",
            "promote",
            "level up",
            "graduation",
            "validation",
        ]

        text = " ".join([m.get("content", "").lower() for m in chat_history])
        if any(kw in text for kw in validation_keywords):
            return "mastery_validation"
        if any(kw in text for kw in practice_keywords):
            return "practice_session"
        if any(kw in text for kw in learning_keywords):
            return "learning_session"
        if any(kw in text for kw in teaching_keywords):
            return "teaching_session"
        return "generic_session"


def load_tracker() -> AIRequestTracker:
    try:
        config_path = (
            Path(__file__).resolve().parents[2]
            / ".lumina"
            / "config"
            / "ai_token_request_tracker.json"
        )
        return AIRequestTracker(config_path)


    except Exception as e:
        logger.error(f"Error in load_tracker: {e}", exc_info=True)
        raise
__all__ = ["AIRequestTracker", "load_tracker"]
