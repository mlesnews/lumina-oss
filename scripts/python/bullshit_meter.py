#!/usr/bin/env python3
"""
Bullshit Meter - Reliability & Credibility Tracking System

Tracks claim accuracy and credibility over time. Based on "The Boy Who Cried Wolf" 
principle: credibility decreases with false claims, and repeated false alarms are 
filtered/hidden like spam in log files.

Purpose:
- Track claim accuracy (true/false)
- Build credibility scores
- Filter unreliable sources (hide like spam)
- Prevent "crying wolf" fatigue
"""

from __future__ import annotations

import json
import time
from collections import deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ClaimStatus(Enum):
    """Claim verification status"""
    PENDING = "pending"
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    UNVERIFIED = "unverified"
    IGNORED = "ignored"  # Like spam - too many false claims


class ClaimType(Enum):
    """Type of claim being made"""
    STATEMENT = "statement"
    PREDICTION = "prediction"
    STATUS = "status"
    ASSERTION = "assertion"
    PROMISE = "promise"


@dataclass
class Claim:
    """A claim that can be verified"""
    claim_id: str
    source: str  # Who/what made the claim
    claim_text: str
    claim_type: ClaimType
    timestamp: datetime
    status: ClaimStatus = ClaimStatus.PENDING
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    verification_notes: Optional[str] = None
    confidence: float = 0.5  # Initial confidence (0.0-1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['claim_type'] = self.claim_type.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.verified_at:
            data['verified_at'] = self.verified_at.isoformat()
        return data


@dataclass
class SourceCredibility:
    """Credibility tracking for a source"""
    source: str
    total_claims: int = 0
    true_claims: int = 0
    false_claims: int = 0
    unverified_claims: int = 0
    credibility_score: float = 0.5  # 0.0-1.0, starts at neutral
    last_false_claim: Optional[datetime] = None
    consecutive_false_claims: int = 0
    is_ignored: bool = False  # Like spam - hide if too unreliable
    ignore_threshold: int = 5  # Ignore after N consecutive false claims
    ignore_until: Optional[datetime] = None

    def update_credibility(self, was_true: bool) -> None:
        """Update credibility score based on claim verification"""
        self.total_claims += 1

        if was_true:
            self.true_claims += 1
            self.consecutive_false_claims = 0
            # Increase credibility (weighted by total claims)
            adjustment = 0.1 / max(1, self.total_claims / 10)
            self.credibility_score = min(1.0, self.credibility_score + adjustment)
        else:
            self.false_claims += 1
            self.consecutive_false_claims += 1
            self.last_false_claim = datetime.now()
            # Decrease credibility (more penalty for recent false claims)
            penalty = 0.2 * (1.0 + self.consecutive_false_claims * 0.1)
            self.credibility_score = max(0.0, self.credibility_score - penalty)

            # Ignore source if too many consecutive false claims (like spam)
            if self.consecutive_false_claims >= self.ignore_threshold:
                self.is_ignored = True
                # Ignore for increasing duration (exponential backoff)
                hours = 2 ** min(self.consecutive_false_claims - self.ignore_threshold, 6)
                self.ignore_until = datetime.now() + timedelta(hours=hours)

    def should_ignore(self) -> bool:
        """Check if source should be ignored (like spam)"""
        if not self.is_ignored:
            return False

        # Check if ignore period has expired
        if self.ignore_until and datetime.now() > self.ignore_until:
            self.is_ignored = False
            self.ignore_until = None
            return False

        return True

    def get_accuracy_rate(self) -> float:
        """Get accuracy rate (0.0-1.0)"""
        verified = self.true_claims + self.false_claims
        if verified == 0:
            return 0.5  # Neutral if no verification
        return self.true_claims / verified

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.last_false_claim:
            data['last_false_claim'] = self.last_false_claim.isoformat()
        if self.ignore_until:
            data['ignore_until'] = self.ignore_until.isoformat()
        return data


class BullshitMeter:
    """
    Bullshit Meter - Tracks claim accuracy and credibility

    Based on "The Boy Who Cried Wolf" principle:
    - Credibility decreases with false claims
    - Repeated false alarms are filtered/hidden (like spam)
    - Unreliable sources are ignored after threshold
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize bullshit meter"""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "bullshit_meter"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("BullshitMeter")

        # State files
        self.claims_file = self.data_dir / "claims.jsonl"
        self.credibility_file = self.data_dir / "credibility.json"

        # In-memory state
        self.claims: Dict[str, Claim] = {}
        self.source_credibility: Dict[str, SourceCredibility] = {}
        self.recent_claims: deque = deque(maxlen=1000)  # Recent claims for quick lookup

        self._lock = threading.RLock()

        # Load persisted state
        self._load_persisted_state()

        self.logger.info("Bullshit Meter initialized")

    def record_claim(
        self,
        source: str,
        claim_text: str,
        claim_type: ClaimType = ClaimType.STATEMENT,
        initial_confidence: Optional[float] = None
    ) -> str:
        """
        Record a new claim

        Args:
            source: Who/what made the claim
            claim_text: The claim text
            claim_type: Type of claim
            initial_confidence: Initial confidence (defaults to source credibility)

        Returns:
            claim_id: Unique identifier for the claim
        """
        claim_id = f"{source}_{int(time.time() * 1000)}"

        # Get source credibility for initial confidence
        if source not in self.source_credibility:
            self.source_credibility[source] = SourceCredibility(source=source)

        source_cred = self.source_credibility[source]
        confidence = initial_confidence if initial_confidence is not None else source_cred.credibility_score

        claim = Claim(
            claim_id=claim_id,
            source=source,
            claim_text=claim_text,
            claim_type=claim_type,
            timestamp=datetime.now(),
            confidence=confidence
        )

        with self._lock:
            self.claims[claim_id] = claim
            self.recent_claims.append(claim)
            source_cred.total_claims += 1
            source_cred.unverified_claims += 1

        # Persist claim
        self._persist_claim(claim)

        self.logger.debug(f"Recorded claim from {source}: {claim_text[:50]}...")

        return claim_id

    def verify_claim(
        self,
        claim_id: str,
        is_true: bool,
        verified_by: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Verify a claim (true or false)

        Args:
            claim_id: Claim identifier
            is_true: Whether the claim was true
            verified_by: Who verified it
            notes: Verification notes

        Returns:
            True if verification was successful
        """
        with self._lock:
            if claim_id not in self.claims:
                self.logger.warning(f"Claim not found: {claim_id}")
                return False

            claim = self.claims[claim_id]
            claim.status = ClaimStatus.VERIFIED_TRUE if is_true else ClaimStatus.VERIFIED_FALSE
            claim.verified_at = datetime.now()
            claim.verified_by = verified_by
            claim.verification_notes = notes

            # Update source credibility (The Boy Who Cried Wolf principle)
            if claim.source in self.source_credibility:
                source_cred = self.source_credibility[claim.source]
                source_cred.unverified_claims -= 1
                source_cred.update_credibility(is_true)

                # Log if source is being ignored (like spam)
                if source_cred.is_ignored and source_cred.should_ignore():
                    self.logger.warning(
                        f"⚠️ Source '{claim.source}' ignored (like spam) - "
                        f"{source_cred.consecutive_false_claims} consecutive false claims. "
                        f"Ignore until: {source_cred.ignore_until}"
                    )

            # Update persisted claim
            self._persist_claim(claim)

            # Save credibility state
            self._save_credibility_state()

        return True

    def should_trust_source(self, source: str) -> Tuple[bool, float]:
        """
        Check if a source should be trusted

        Returns:
            (should_trust, credibility_score)
        """
        with self._lock:
            if source not in self.source_credibility:
                return True, 0.5  # Neutral if unknown

            source_cred = self.source_credibility[source]

            # Check if source is ignored (like spam)
            if source_cred.should_ignore():
                return False, source_cred.credibility_score

            # Trust threshold (can be adjusted)
            trust_threshold = 0.3
            return source_cred.credibility_score >= trust_threshold, source_cred.credibility_score

    def filter_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Filter claims based on source credibility (hide unreliable like spam)

        Args:
            claims: List of claims to filter

        Returns:
            Filtered list (unreliable sources hidden)
        """
        filtered = []

        for claim in claims:
            should_trust, _ = self.should_trust_source(claim.source)
            if should_trust or claim.status == ClaimStatus.VERIFIED_TRUE:
                filtered.append(claim)
            else:
                # Mark as ignored (like spam in log files)
                claim.status = ClaimStatus.IGNORED

        return filtered

    def get_source_credibility(self, source: str) -> Optional[SourceCredibility]:
        """Get credibility for a source"""
        with self._lock:
            return self.source_credibility.get(source)

    def get_all_credibility(self) -> Dict[str, SourceCredibility]:
        """Get all source credibility scores"""
        with self._lock:
            return self.source_credibility.copy()

    def _persist_claim(self, claim: Claim) -> None:
        """Persist claim to JSON Lines file"""
        try:
            with open(self.claims_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(claim.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to persist claim: {e}")

    def _save_credibility_state(self) -> None:
        """Save credibility state to disk"""
        try:
            with self._lock:
                state = {
                    'timestamp': datetime.now().isoformat(),
                    'sources': {
                        source: cred.to_dict()
                        for source, cred in self.source_credibility.items()
                    }
                }

            with open(self.credibility_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save credibility state: {e}")

    def _load_persisted_state(self) -> None:
        """Load persisted credibility state"""
        if not self.credibility_file.exists():
            return

        try:
            with open(self.credibility_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            with self._lock:
                for source, cred_data in state.get('sources', {}).items():
                    cred = SourceCredibility(source=source)
                    cred.total_claims = cred_data.get('total_claims', 0)
                    cred.true_claims = cred_data.get('true_claims', 0)
                    cred.false_claims = cred_data.get('false_claims', 0)
                    cred.unverified_claims = cred_data.get('unverified_claims', 0)
                    cred.credibility_score = cred_data.get('credibility_score', 0.5)
                    cred.consecutive_false_claims = cred_data.get('consecutive_false_claims', 0)
                    cred.is_ignored = cred_data.get('is_ignored', False)
                    cred.ignore_threshold = cred_data.get('ignore_threshold', 5)

                    if cred_data.get('last_false_claim'):
                        cred.last_false_claim = datetime.fromisoformat(cred_data['last_false_claim'])
                    if cred_data.get('ignore_until'):
                        cred.ignore_until = datetime.fromisoformat(cred_data['ignore_until'])

                    self.source_credibility[source] = cred

            self.logger.info(f"Loaded credibility state for {len(self.source_credibility)} sources")
        except Exception as e:
            self.logger.error(f"Failed to load credibility state: {e}")


if __name__ == "__main__":
    # Example usage
    meter = BullshitMeter()

    # Record a claim
    claim_id = meter.record_claim(
        source="test_ai",
        claim_text="The system is healthy",
        claim_type=ClaimType.STATEMENT
    )

    # Verify claim (false)
    meter.verify_claim(claim_id, is_true=False, verified_by="user")

    # Check if source should be trusted
    should_trust, credibility = meter.should_trust_source("test_ai")
    print(f"Should trust test_ai: {should_trust}, credibility: {credibility:.2f}")

