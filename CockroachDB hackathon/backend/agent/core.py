"""
LedgerMind Agent Core — The main agent loop.

The agent follows this cycle:
1. Observe — Monitor current payment activity
2. Retrieve — Fetch relevant structured and semantic memory
3. Compare — Measure current behaviour against learned baselines
4. Explain — Identify likely cause of anomalies
5. Recommend — Suggest actions to the SME
6. Store — Record decisions and approval state
7. Check — Verify outcomes of approved actions
8. Learn — Use outcomes to improve future incident handling
"""

import os
from typing import Optional
from enum import Enum
from pydantic import BaseModel

from .memory import AgenticMemoryStore, DecisionMemory, MemoryType
from .tools import AgentToolkit


class AgentState(str, Enum):
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    RECOMMENDING = "recommending"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    CHECKING_OUTCOME = "checking_outcome"
    IDLE = "idle"


class AgentRecommendation(BaseModel):
    """A recommendation from the agent to the SME."""
    task_id: str
    summary: str
    explanation: str
    proposed_action: str
    confidence: float
    supporting_evidence: list[str]
    risk_level: str  # low, medium, high
    requires_approval: bool = True


class LedgerMindAgent:
    """
    The LedgerMind AI Agent.
    
    Uses Amazon Bedrock for reasoning and CockroachDB for agentic memory.
    All consequential actions require SME approval before execution.
    """

    def __init__(self, sme_id: str, memory_store: AgenticMemoryStore):
        self.sme_id = sme_id
        self.memory = memory_store
        self.toolkit = AgentToolkit(sme_id, memory_store)
        self.state = AgentState.IDLE
        self.bedrock_model_id = os.getenv(
            "BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0"
        )

    async def observe(self) -> dict:
        """
        Step 1: Observe current payment activity.
        Pulls latest transaction data, failure rates, customer activity.
        """
        self.state = AgentState.OBSERVING
        observations = await self.toolkit.get_current_activity()
        await self.memory.store_observation(self.sme_id, observations)
        return observations

    async def analyze(self, observations: dict) -> dict:
        """
        Steps 2-4: Retrieve memory, compare baselines, explain anomalies.
        """
        self.state = AgentState.ANALYZING

        # Retrieve relevant memories
        relevant_memories = await self.memory.retrieve_relevant_memories(
            sme_id=self.sme_id,
            query_text=str(observations),
            memory_types=[MemoryType.INCIDENT, MemoryType.DECISION, MemoryType.OUTCOME],
        )

        # Get baselines for comparison
        baselines = await self.memory.get_baselines(self.sme_id)

        # Find similar past incidents
        similar_incidents = await self.memory.get_similar_past_incidents(
            self.sme_id, observations
        )

        # Use Bedrock to analyze and explain
        analysis = await self._reason_with_bedrock(
            observations=observations,
            memories=relevant_memories,
            baselines=baselines,
            similar_incidents=similar_incidents,
        )

        return analysis

    async def recommend(self, analysis: dict) -> AgentRecommendation:
        """
        Step 5: Recommend an action based on analysis.
        The recommendation goes to the SME for approval.
        """
        self.state = AgentState.RECOMMENDING

        # Generate recommendation using Bedrock
        recommendation = await self._generate_recommendation(analysis)

        # Store the decision (pending approval)
        decision = DecisionMemory(
            task_type=analysis.get("task_type", "general"),
            observation=str(analysis.get("observations", "")),
            analysis=str(analysis.get("explanation", "")),
            recommendation=recommendation.proposed_action,
            approval_status="pending",
        )
        await self.memory.store_decision(self.sme_id, decision)

        self.state = AgentState.AWAITING_APPROVAL
        return recommendation

    async def execute_approved_action(self, approval_id: str, action: dict):
        """
        Step 6: Execute an approved action and store the decision.
        Only runs after SME approval.
        """
        self.state = AgentState.EXECUTING
        # TODO: Execute the action via toolkit
        # TODO: Store execution state
        pass

    async def check_outcome(self, decision_id: str) -> dict:
        """
        Step 7: Check the outcome of an executed action.
        Runs after a configurable delay to measure impact.
        """
        self.state = AgentState.CHECKING_OUTCOME
        # TODO: Compare metrics before/after action
        # TODO: Score the outcome
        outcome = {
            "decision_id": decision_id,
            "metrics_before": {},
            "metrics_after": {},
            "improvement": 0.0,
            "score": 0.0,
        }
        return outcome

    async def learn_from_outcome(self, decision_id: str, outcome: dict):
        """
        Step 8: Use the outcome to improve future incident handling.
        Updates baselines and stores outcome for future retrieval.
        """
        await self.memory.store_outcome(
            decision_id=decision_id,
            outcome=outcome,
            score=outcome.get("score", 0.0),
        )
        self.state = AgentState.IDLE

    # --- Task-Specific Methods ---

    async def investigate_failure_spike(self, context: Optional[dict] = None):
        """Investigate a sudden spike in payment failures."""
        observations = await self.observe()
        analysis = await self.analyze({**observations, "task_type": "investigate_failure_spike"})
        recommendation = await self.recommend(analysis)
        return recommendation

    async def create_recovery_list(self, context: Optional[dict] = None):
        """Create a list of customers to recover after payment issues."""
        observations = await self.observe()
        analysis = await self.analyze({**observations, "task_type": "create_recovery_list"})
        recommendation = await self.recommend(analysis)
        return recommendation

    async def follow_up_inactive_customers(self, days_threshold: int = 30):
        """Identify and plan follow-up for inactive customers."""
        observations = await self.observe()
        analysis = await self.analyze({
            **observations,
            "task_type": "follow_up_inactive",
            "days_threshold": days_threshold,
        })
        recommendation = await self.recommend(analysis)
        return recommendation

    async def monitor_anomaly(self, anomaly_id: str, duration_hours: int = 24):
        """Monitor a detected anomaly for a specified duration."""
        # TODO: Set up scheduled monitoring task
        pass

    async def prepare_campaign_suggestion(self, context: Optional[dict] = None):
        """Prepare a campaign suggestion based on customer patterns."""
        observations = await self.observe()
        analysis = await self.analyze({**observations, "task_type": "prepare_campaign"})
        recommendation = await self.recommend(analysis)
        return recommendation

    async def schedule_performance_check(self, check_after_hours: int = 24):
        """Schedule a performance check after an action is taken."""
        # TODO: Create scheduled task for outcome checking
        pass

    # --- Private Methods ---

    async def _reason_with_bedrock(self, **kwargs) -> dict:
        """Use Amazon Bedrock to reason about observations and memory."""
        # TODO: Call Bedrock with structured prompt
        # Include observations, baselines, similar incidents, past decisions
        return {
            "explanation": "Placeholder analysis",
            "anomalies_detected": [],
            "confidence": 0.0,
        }

    async def _generate_recommendation(self, analysis: dict) -> AgentRecommendation:
        """Use Bedrock to generate a recommendation."""
        # TODO: Call Bedrock to generate actionable recommendation
        return AgentRecommendation(
            task_id="placeholder",
            summary="Placeholder recommendation",
            explanation="Based on analysis...",
            proposed_action="No action yet",
            confidence=0.0,
            supporting_evidence=[],
            risk_level="low",
            requires_approval=True,
        )
