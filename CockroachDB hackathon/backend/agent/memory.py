"""
LedgerMind Agentic Memory — CockroachDB-backed structured + semantic memory.

The agent uses CockroachDB as its memory system:
- Structured memory: decisions, baselines, outcomes, approvals
- Semantic memory: vector embeddings for similarity-based retrieval
- Episodic memory: past incidents and their resolutions

This allows the agent to learn from past decisions and improve over time.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum
import uuid


class MemoryType(str, Enum):
    OBSERVATION = "observation"
    DECISION = "decision"
    OUTCOME = "outcome"
    BASELINE = "baseline"
    INCIDENT = "incident"
    PATTERN = "pattern"


class AgentMemoryEntry(BaseModel):
    """A single memory entry stored in CockroachDB."""
    id: str = None
    sme_id: str
    memory_type: MemoryType
    content: dict
    embedding: Optional[list[float]] = None  # For vector search
    created_at: datetime = None
    metadata: Optional[dict] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class DecisionMemory(BaseModel):
    """Records an agent decision and the SME's response."""
    task_type: str
    observation: str
    analysis: str
    recommendation: str
    approval_status: str  # pending, approved, rejected
    sme_feedback: Optional[str] = None
    outcome: Optional[dict] = None  # Filled after execution
    outcome_score: Optional[float] = None  # How well did the action work?


class BaselineMemory(BaseModel):
    """Learned baseline for comparison."""
    metric_name: str
    normal_range_low: float
    normal_range_high: float
    sample_size: int
    last_updated: datetime
    confidence: float  # 0.0 to 1.0


class AgenticMemoryStore:
    """
    CockroachDB-backed memory store for the LedgerMind agent.
    
    Uses:
    - Regular tables for structured data (decisions, baselines, outcomes)
    - pgvector extension for semantic similarity search
    - Changefeeds for real-time observation triggers
    """

    def __init__(self, db_session):
        self.db = db_session

    async def store_observation(self, sme_id: str, observation: dict) -> str:
        """Store a new observation from payment activity monitoring."""
        entry = AgentMemoryEntry(
            sme_id=sme_id,
            memory_type=MemoryType.OBSERVATION,
            content=observation,
        )
        # TODO: Insert into CockroachDB with embedding
        return entry.id

    async def store_decision(self, sme_id: str, decision: DecisionMemory) -> str:
        """Store an agent decision (recommendation + approval state)."""
        entry = AgentMemoryEntry(
            sme_id=sme_id,
            memory_type=MemoryType.DECISION,
            content=decision.model_dump(),
        )
        # TODO: Insert into CockroachDB
        return entry.id

    async def store_outcome(self, decision_id: str, outcome: dict, score: float):
        """
        Store the outcome of an approved action.
        This is how the agent learns — by connecting decisions to their results.
        """
        # TODO: Update decision record with outcome, store for future retrieval
        pass

    async def retrieve_relevant_memories(
        self,
        sme_id: str,
        query_text: str,
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
    ) -> list[AgentMemoryEntry]:
        """
        Retrieve memories relevant to the current situation.
        Uses vector similarity search on CockroachDB pgvector.
        """
        # TODO: Generate embedding for query_text, do similarity search
        return []

    async def get_baselines(self, sme_id: str) -> list[BaselineMemory]:
        """Get learned baselines for this SME."""
        # TODO: Query baselines table
        return []

    async def get_similar_past_incidents(
        self, sme_id: str, current_incident: dict, limit: int = 5
    ) -> list[dict]:
        """
        Find past incidents similar to the current one.
        The agent uses these to inform its recommendations.
        """
        # TODO: Vector similarity search on past incidents
        return []

    async def update_baseline(self, sme_id: str, baseline: BaselineMemory):
        """Update a learned baseline based on new data."""
        # TODO: Upsert baseline in CockroachDB
        pass

    async def get_decision_history(
        self, sme_id: str, task_type: Optional[str] = None, limit: int = 20
    ) -> list[DecisionMemory]:
        """
        Get history of past decisions and their outcomes.
        Used by the agent to learn which recommendations work best.
        """
        # TODO: Query from CockroachDB
        return []
