"""
Audit Activity Logger — Tracks all agent and user actions.

Every action in the system is logged for:
- Compliance and transparency
- SME can review what the agent did and why
- Debugging agent behavior
- Building trust through explainability

Audit events include:
- Agent observations and analyses
- Agent recommendations
- SME approval/rejection decisions
- Executed actions and their parameters
- Outcome measurements
- Campaign executions
- Login events
- Data imports
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum
import uuid


class AuditEventType(str, Enum):
    # Agent events
    AGENT_OBSERVATION = "agent.observation"
    AGENT_ANALYSIS = "agent.analysis"
    AGENT_RECOMMENDATION = "agent.recommendation"
    AGENT_EXECUTION = "agent.execution"
    AGENT_OUTCOME_CHECK = "agent.outcome_check"
    AGENT_LEARNING = "agent.learning"
    # User events
    USER_APPROVAL = "user.approval"
    USER_REJECTION = "user.rejection"
    USER_LOGIN = "user.login"
    USER_DATA_IMPORT = "user.data_import"
    USER_TASK_CREATED = "user.task_created"
    # Campaign events
    CAMPAIGN_CREATED = "campaign.created"
    CAMPAIGN_APPROVED = "campaign.approved"
    CAMPAIGN_EXECUTED = "campaign.executed"
    CAMPAIGN_OUTCOME = "campaign.outcome"
    # System events
    ANOMALY_DETECTED = "system.anomaly_detected"
    BASELINE_UPDATED = "system.baseline_updated"
    DAILY_BRIEF_GENERATED = "system.daily_brief"
    FORECAST_GENERATED = "system.forecast"


class AuditEvent(BaseModel):
    """A single audit event."""
    id: str = None
    sme_id: str
    event_type: AuditEventType
    actor: str  # "agent", "user:<email>", "system"
    description: str
    details: Optional[dict] = None
    related_entity_id: Optional[str] = None  # ID of related decision/task/campaign
    created_at: datetime = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class AuditLogger:
    """
    Writes audit events to CockroachDB.
    Provides query interface for the audit trail UI.
    """

    def __init__(self, db_session):
        self.db = db_session

    async def log(
        self,
        sme_id: str,
        event_type: AuditEventType,
        actor: str,
        description: str,
        details: Optional[dict] = None,
        related_entity_id: Optional[str] = None,
    ) -> str:
        """Log an audit event. Returns the event ID."""
        event = AuditEvent(
            sme_id=sme_id,
            event_type=event_type,
            actor=actor,
            description=description,
            details=details,
            related_entity_id=related_entity_id,
        )
        # TODO: Insert into CockroachDB audit_events table
        return event.id

    async def get_events(
        self,
        sme_id: str,
        event_types: Optional[list[AuditEventType]] = None,
        actor: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditEvent]:
        """Query audit events with filters."""
        # TODO: Query from CockroachDB
        return []

    async def get_entity_trail(
        self, entity_id: str
    ) -> list[AuditEvent]:
        """Get the full audit trail for a specific entity (decision, task, etc.)."""
        # TODO: Query by related_entity_id
        return []
