#!/usr/bin/env python3
"""
SYPHON Data Models

Standardized data models for SYPHON system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DataSourceType(Enum):
    """Types of data sources for syphon extraction"""
    EMAIL = "email"
    SMS = "sms"
    BANKING = "banking"
    SOCIAL = "social"
    CODE = "code"
    DOCUMENT = "document"
    IDE = "ide"  # IDE diagnostics, problems, notifications
    WEB = "web"  # Web scraping and content extraction
    MATRIX = "matrix"  # Matrix simulation pipe (universal)
    WORKFLOW = "workflow"  # JARVIS workflows, agent coordination, collaboration
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
    financial_data: Optional[Dict[str, Any]] = None  # For banking extraction

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
            "intelligence": self.intelligence,
            "financial_data": self.financial_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SyphonData:
        """Create from dictionary"""
        return cls(
            data_id=data["data_id"],
            source_type=DataSourceType(data["source_type"]),
            source_id=data["source_id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            extracted_at=datetime.fromisoformat(data.get("extracted_at", datetime.now().isoformat())),
            actionable_items=data.get("actionable_items", []),
            tasks=data.get("tasks", []),
            decisions=data.get("decisions", []),
            intelligence=data.get("intelligence", []),
            financial_data=data.get("financial_data")
        )


@dataclass
class ExtractionResult:
    """Result of extraction operation"""
    success: bool
    data: Optional[SyphonData] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data.to_dict() if self.data else None,
            "error": self.error,
            "metadata": self.metadata
        }


class HealthStatus(Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class HealthMetrics:
    """Health metrics for monitoring"""
    status: HealthStatus
    uptime: float
    success_rate: float
    error_count: int
    last_error: Optional[str] = None
    last_success: Optional[datetime] = None
    component_status: Dict[str, HealthStatus] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "uptime": self.uptime,
            "success_rate": self.success_rate,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "component_status": {k: v.value for k, v in self.component_status.items()}
        }

