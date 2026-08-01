"""
Agent router — endpoints for interacting with the LedgerMind AI agent.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from enum import Enum

from ..auth import CurrentUser, get_current_user

router = APIRouter()


class AgentTaskType(str, Enum):
    INVESTIGATE_FAILURE_SPIKE = "investigate_failure_spike"
    CREATE_RECOVERY_LIST = "create_recovery_list"
    FOLLOW_UP_INACTIVE = "follow_up_inactive"
    MONITOR_ANOMALY = "monitor_anomaly"
    PREPARE_CAMPAIGN = "prepare_campaign"
    SCHEDULE_PERFORMANCE_CHECK = "schedule_performance_check"


class AgentTaskRequest(BaseModel):
    task_type: AgentTaskType
    context: Optional[dict] = None
    parameters: Optional[dict] = None


class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


@router.post("/tasks")
async def create_agent_task(
    request: AgentTaskRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Create a new agent task. The agent will:
    1. Observe current payment activity
    2. Retrieve relevant structured and semantic memory
    3. Compare current behaviour with learned baselines
    4. Explain the likely cause
    5. Recommend an action (pending SME approval)
    """
    # TODO: Dispatch task to agent service via SQS or direct invocation
    return {
        "task_id": "task_placeholder",
        "task_type": request.task_type,
        "status": "queued",
        "message": f"Agent task '{request.task_type.value}' has been queued for processing",
    }


@router.post("/chat")
async def agent_chat(
    request: AgentChatRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Chat with the LedgerMind agent. The agent can explain observations,
    provide recommendations, and answer questions about payment operations.
    """
    # TODO: Route to agent service
    return {
        "conversation_id": request.conversation_id or "new_conv",
        "response": "Agent response placeholder",
        "requires_approval": False,
    }


@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Get the current status and results of an agent task."""
    # TODO: Fetch from CockroachDB
    return {
        "task_id": task_id,
        "status": "in_progress",
        "observations": [],
        "recommendations": [],
    }


@router.get("/memory/{sme_id}")
async def get_agent_memory(
    sme_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Retrieve the agent's memory for this SME — past decisions,
    outcomes, learned baselines, and stored patterns.
    """
    # TODO: Query CockroachDB agentic memory tables
    return {
        "sme_id": sme_id,
        "decisions": [],
        "baselines": [],
        "learned_patterns": [],
    }
