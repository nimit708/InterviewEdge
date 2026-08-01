"""
Approvals router — human-in-the-loop approval system.
SME approves consequential actions before they are executed.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from enum import Enum

from ..auth import CurrentUser, get_current_user

router = APIRouter()


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalDecision(BaseModel):
    status: ApprovalStatus
    reason: Optional[str] = None
    modified_parameters: Optional[dict] = None


@router.get("/pending")
async def get_pending_approvals(
    user: CurrentUser = Depends(get_current_user),
):
    """
    Get all actions pending SME approval.
    These are consequential actions the agent wants to take.
    """
    # TODO: Query pending approvals from CockroachDB
    return {
        "approvals": [],
        "total": 0,
    }


@router.post("/{approval_id}/decide")
async def decide_approval(
    approval_id: str,
    decision: ApprovalDecision,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Approve or reject an agent-proposed action.
    If approved, the agent will execute the action and monitor outcomes.
    If rejected, the agent stores the decision for future learning.
    """
    # TODO: Update approval status, trigger agent execution if approved
    return {
        "approval_id": approval_id,
        "status": decision.status,
        "message": f"Action {decision.status.value}. Agent will {'execute and monitor outcome' if decision.status == ApprovalStatus.APPROVED else 'record this for future learning'}.",
    }


@router.get("/history")
async def get_approval_history(
    user: CurrentUser = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    """
    Get history of past approval decisions and their outcomes.
    The agent uses these outcomes to improve future recommendations.
    """
    # TODO: Query approval history with outcomes from CockroachDB
    return {
        "approvals": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }
