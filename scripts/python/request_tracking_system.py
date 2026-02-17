#!/usr/bin/env python3
"""
Request Tracking & Implementation System

Tracks all user requests/asks and ensures they are analyzed, developed, and implemented.
Prevents lost requests by maintaining a comprehensive audit trail.

Author: <COMPANY_NAME> LLC
Date: 2025-01-28
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
logger = get_logger("request_tracking_system")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class RequestStatus(Enum):
    """Request status enumeration"""
    PENDING = "pending"  # Request received, not yet analyzed
    ANALYZED = "analyzed"  # Request analyzed, awaiting development
    IN_DEVELOPMENT = "in_development"  # Currently being developed
    IN_REVIEW = "in_review"  # Development complete, awaiting review
    IMPLEMENTED = "implemented"  # Implemented and verified
    BLOCKED = "blocked"  # Blocked by dependencies
    REJECTED = "rejected"  # Request rejected (with reason)
    STALE = "stale"  # No activity for extended period


class RequestPriority(Enum):
    """Request priority enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Request:
    """User request/ask tracking"""
    request_id: str
    timestamp: str
    user_message: str
    extracted_intent: str
    status: RequestStatus
    priority: RequestPriority
    category: str
    tags: List[str] = field(default_factory=list)

    # Analysis phase
    analysis_completed: bool = False
    analysis_notes: str = ""
    analysis_timestamp: Optional[str] = None

    # Development phase
    development_started: bool = False
    development_notes: str = ""
    development_timestamp: Optional[str] = None
    implementation_plan: Dict[str, Any] = field(default_factory=dict)

    # Review phase
    review_completed: bool = False
    review_notes: str = ""
    review_timestamp: Optional[str] = None

    # Implementation phase
    implementation_completed: bool = False
    implementation_notes: str = ""
    implementation_timestamp: Optional[str] = None
    verification_results: Dict[str, Any] = field(default_factory=dict)

    # Tracking
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    updates: List[Dict[str, Any]] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    related_requests: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Request:
        """Create from dictionary"""
        data["status"] = RequestStatus(data["status"])
        data["priority"] = RequestPriority(data["priority"])
        return cls(**data)


class RequestTrackingSystem:
    """Comprehensive request tracking and implementation system"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "request_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.requests_file = self.data_dir / "requests.json"
        self.audit_log_file = self.data_dir / "audit_log.jsonl"
        self.logger = get_logger("RequestTracking")

        self.requests: Dict[str, Request] = {}
        self._load_requests()

    def _load_requests(self):
        """Load requests from disk"""
        if self.requests_file.exists():
            try:
                with open(self.requests_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for req_id, req_data in data.items():
                        self.requests[req_id] = Request.from_dict(req_data)
                self.logger.info(f"Loaded {len(self.requests)} requests")
            except Exception as e:
                self.logger.error(f"Failed to load requests: {e}")

    def _save_requests(self):
        """Save requests to disk"""
        try:
            data = {req_id: req.to_dict() for req_id, req in self.requests.items()}
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save requests: {e}")

    def _log_audit(self, action: str, request_id: str, details: Dict[str, Any]):
        """Log audit trail"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "request_id": request_id,
            "details": details
        }
        try:
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to log audit: {e}")

    def _add_update(self, request: Request, update_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Add update to request"""
        update = {
            "timestamp": datetime.now().isoformat(),
            "type": update_type,
            "message": message,
            "details": details or {}
        }
        request.updates.append(update)
        request.last_updated = datetime.now().isoformat()

    def create_request(
        self,
        user_message: str,
        extracted_intent: str,
        priority: RequestPriority = RequestPriority.MEDIUM,
        category: str = "general",
        tags: Optional[List[str]] = None
    ) -> Request:
        """Create a new request"""
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        request = Request(
            request_id=request_id,
            timestamp=datetime.now().isoformat(),
            user_message=user_message,
            extracted_intent=extracted_intent,
            status=RequestStatus.PENDING,
            priority=priority,
            category=category,
            tags=tags or []
        )

        self.requests[request_id] = request
        self._save_requests()
        self._log_audit("create", request_id, {"intent": extracted_intent, "priority": priority.value})
        self._add_update(request, "created", f"Request created: {extracted_intent}")

        self.logger.info(f"Created request {request_id}: {extracted_intent}")
        return request

    def analyze_request(self, request_id: str, analysis_notes: str, implementation_plan: Optional[Dict[str, Any]] = None) -> bool:
        """Mark request as analyzed"""
        if request_id not in self.requests:
            self.logger.error(f"Request {request_id} not found")
            return False

        request = self.requests[request_id]
        request.analysis_completed = True
        request.analysis_notes = analysis_notes
        request.analysis_timestamp = datetime.now().isoformat()
        request.status = RequestStatus.ANALYZED

        if implementation_plan:
            request.implementation_plan = implementation_plan

        self._add_update(request, "analyzed", f"Request analyzed: {analysis_notes[:100]}")
        self._save_requests()
        self._log_audit("analyze", request_id, {"notes": analysis_notes})

        self.logger.info(f"Request {request_id} analyzed")
        return True

    def start_development(self, request_id: str, development_notes: str) -> bool:
        """Mark request as in development"""
        if request_id not in self.requests:
            self.logger.error(f"Request {request_id} not found")
            return False

        request = self.requests[request_id]
        request.development_started = True
        request.development_notes = development_notes
        request.development_timestamp = datetime.now().isoformat()
        request.status = RequestStatus.IN_DEVELOPMENT

        self._add_update(request, "development_started", f"Development started: {development_notes[:100]}")
        self._save_requests()
        self._log_audit("start_development", request_id, {"notes": development_notes})

        self.logger.info(f"Request {request_id} development started")
        return True

    def complete_development(self, request_id: str, review_notes: str) -> bool:
        """Mark development as complete, move to review"""
        if request_id not in self.requests:
            self.logger.error(f"Request {request_id} not found")
            return False

        request = self.requests[request_id]
        request.review_completed = False  # Reset for review phase
        request.review_notes = review_notes
        request.review_timestamp = datetime.now().isoformat()
        request.status = RequestStatus.IN_REVIEW

        self._add_update(request, "development_complete", f"Development complete, awaiting review: {review_notes[:100]}")
        self._save_requests()
        self._log_audit("complete_development", request_id, {"notes": review_notes})

        self.logger.info(f"Request {request_id} development complete, in review")
        return True

    def complete_review(self, request_id: str, review_notes: str) -> bool:
        """Mark review as complete"""
        if request_id not in self.requests:
            self.logger.error(f"Request {request_id} not found")
            return False

        request = self.requests[request_id]
        request.review_completed = True
        request.review_notes = review_notes
        request.review_timestamp = datetime.now().isoformat()

        self._add_update(request, "review_complete", f"Review complete: {review_notes[:100]}")
        self._save_requests()
        self._log_audit("complete_review", request_id, {"notes": review_notes})

        self.logger.info(f"Request {request_id} review complete")
        return True

    def implement_request(
        self,
        request_id: str,
        implementation_notes: str,
        verification_results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark request as implemented"""
        if request_id not in self.requests:
            self.logger.error(f"Request {request_id} not found")
            return False

        request = self.requests[request_id]
        request.implementation_completed = True
        request.implementation_notes = implementation_notes
        request.implementation_timestamp = datetime.now().isoformat()
        request.status = RequestStatus.IMPLEMENTED

        if verification_results:
            request.verification_results = verification_results

        self._add_update(request, "implemented", f"Request implemented: {implementation_notes[:100]}")
        self._save_requests()
        self._log_audit("implement", request_id, {
            "notes": implementation_notes,
            "verification": verification_results
        })

        self.logger.info(f"Request {request_id} implemented")
        return True

    def block_request(self, request_id: str, blocker_reason: str) -> bool:
        """Block a request"""
        if request_id not in self.requests:
            self.logger.error(f"Request {request_id} not found")
            return False

        request = self.requests[request_id]
        request.status = RequestStatus.BLOCKED
        request.blockers.append(blocker_reason)

        self._add_update(request, "blocked", f"Request blocked: {blocker_reason}")
        self._save_requests()
        self._log_audit("block", request_id, {"reason": blocker_reason})

        self.logger.warning(f"Request {request_id} blocked: {blocker_reason}")
        return True

    def get_pending_requests(self) -> List[Request]:
        try:
            """Get all pending requests"""
            return [req for req in self.requests.values() if req.status == RequestStatus.PENDING]

        except Exception as e:
            self.logger.error(f"Error in get_pending_requests: {e}", exc_info=True)
            raise
    def get_stale_requests(self, days: int = 7) -> List[Request]:
        try:
            """Get requests with no activity for specified days"""
            cutoff = datetime.now() - timedelta(days=days)
            stale = []
            for req in self.requests.values():
                last_update = datetime.fromisoformat(req.last_updated)
                if last_update < cutoff and req.status != RequestStatus.IMPLEMENTED:
                    stale.append(req)
            return stale

        except Exception as e:
            self.logger.error(f"Error in get_stale_requests: {e}", exc_info=True)
            raise
    def get_requests_by_status(self, status: RequestStatus) -> List[Request]:
        try:
            """Get requests by status"""
            return [req for req in self.requests.values() if req.status == status]

        except Exception as e:
            self.logger.error(f"Error in get_request: {e}", exc_info=True)
            raise
    def get_requests_by_priority(self, priority: RequestPriority) -> List[Request]:
        try:
            """Get requests by priority"""
            return [req for req in self.requests.values() if req.priority == priority]

        except Exception as e:
            self.logger.error(f"Error in get_requests_by_priority: {e}", exc_info=True)
            raise
    def get_request(self, request_id: str) -> Optional[Request]:
        try:
            """Get a specific request"""
            return self.requests.get(request_id)

        except Exception as e:
            self.logger.error(f"Error in get_request: {e}", exc_info=True)
            raise
    def generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        total = len(self.requests)
        by_status = {}
        by_priority = {}

        for status in RequestStatus:
            by_status[status.value] = len(self.get_requests_by_status(status))

        for priority in RequestPriority:
            by_priority[priority.value] = len(self.get_requests_by_priority(priority))

        pending = self.get_pending_requests()
        stale = self.get_stale_requests()
        in_development = self.get_requests_by_status(RequestStatus.IN_DEVELOPMENT)
        implemented = self.get_requests_by_status(RequestStatus.IMPLEMENTED)

        return {
            "report_date": datetime.now().isoformat(),
            "total_requests": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "pending_count": len(pending),
            "stale_count": len(stale),
            "in_development_count": len(in_development),
            "implemented_count": len(implemented),
            "implementation_rate": (len(implemented) / total * 100) if total > 0 else 0,
            "pending_requests": [req.request_id for req in pending],
            "stale_requests": [req.request_id for req in stale],
            "critical_pending": [
                req.request_id for req in pending
                if req.priority == RequestPriority.CRITICAL
            ]
        }


def main():
    try:
        """Test the request tracking system"""
        import sys
        project_root = Path(__file__).parent.parent.parent

        tracker = RequestTrackingSystem(project_root)

        # Generate audit report
        report = tracker.generate_audit_report()
        print("\n" + "=" * 60)
        print("REQUEST TRACKING AUDIT REPORT")
        print("=" * 60)
        print(json.dumps(report, indent=2))

        # Show pending requests
        pending = tracker.get_pending_requests()
        if pending:
            print(f"\n⚠️  {len(pending)} PENDING REQUESTS:")
            for req in pending[:10]:  # Show first 10
                print(f"  - {req.request_id}: {req.extracted_intent} (Priority: {req.priority.value})")

        # Show stale requests
        stale = tracker.get_stale_requests()
        if stale:
            print(f"\n⚠️  {len(stale)} STALE REQUESTS (no activity >7 days):")
            for req in stale[:10]:  # Show first 10
                print(f"  - {req.request_id}: {req.extracted_intent} (Last updated: {req.last_updated})")

        # Show critical pending
        critical = [req for req in pending if req.priority == RequestPriority.CRITICAL]
        if critical:
            print(f"\n🔴 {len(critical)} CRITICAL PENDING REQUESTS:")
            for req in critical:
                print(f"  - {req.request_id}: {req.extracted_intent}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()