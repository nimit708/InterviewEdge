"""
SQLAlchemy models for CockroachDB.
Defines the schema for the LedgerMind application.
"""

from sqlalchemy import (
    Column, String, Float, Integer, DateTime, JSON, Boolean,
    Enum as SQLEnum, Text, Index, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
import enum

from .database import Base


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TaskStatus(str, enum.Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


# --- SME and Membership ---

class SME(Base):
    __tablename__ = "smes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    cognito_sub = Column(String(255), unique=True, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_connect_account_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), default="trial")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


# --- Payments ---

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id = Column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(50), nullable=False)  # succeeded, failed, pending
    failure_reason = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_transactions_sme_created", "sme_id", "created_at"),
        Index("idx_transactions_status", "status"),
    )


class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id = Column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    last_transaction_at = Column(DateTime, nullable=True)
    total_transactions = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_customers_sme_status", "sme_id", "status"),
        Index("idx_customers_last_txn", "last_transaction_at"),
    )


# --- Agent Memory ---

class AgentMemory(Base):
    """Structured + semantic memory for the agent."""
    __tablename__ = "agent_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id = Column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    memory_type = Column(String(50), nullable=False)  # observation, decision, outcome, baseline, incident, pattern
    content = Column(JSON, nullable=False)
    embedding = Column(Vector(1024), nullable=True)  # For pgvector semantic search
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_memory_sme_type", "sme_id", "memory_type"),
    )


class AgentDecision(Base):
    """Tracks agent decisions, approvals, and outcomes."""
    __tablename__ = "agent_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id = Column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    task_type = Column(String(100), nullable=False)
    observation = Column(Text, nullable=False)
    analysis = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    risk_level = Column(String(20), default="low")
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    sme_feedback = Column(Text, nullable=True)
    outcome = Column(JSON, nullable=True)
    outcome_score = Column(Float, nullable=True)
    embedding = Column(Vector(1024), nullable=True)  # For similar incident search
    created_at = Column(DateTime, server_default=func.now())
    approved_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    outcome_checked_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_decisions_sme_status", "sme_id", "approval_status"),
        Index("idx_decisions_task_type", "task_type"),
    )


class AgentBaseline(Base):
    """Learned baselines the agent uses for anomaly detection."""
    __tablename__ = "agent_baselines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id = Column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    normal_range_low = Column(Float, nullable=False)
    normal_range_high = Column(Float, nullable=False)
    mean_value = Column(Float, nullable=False)
    std_deviation = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    last_updated = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_baselines_sme_metric", "sme_id", "metric_name", unique=True),
    )


class AgentTask(Base):
    """Tracks agent tasks (investigations, monitoring, campaigns)."""
    __tablename__ = "agent_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id = Column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    task_type = Column(String(100), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.QUEUED)
    parameters = Column(JSON, nullable=True)
    result = Column(JSON, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)  # For scheduled checks
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_tasks_sme_status", "sme_id", "status"),
        Index("idx_tasks_scheduled", "scheduled_for"),
    )
