"""
Campaign router — Automated campaigning endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel

from ..auth import CurrentUser, get_current_user

router = APIRouter()


class CampaignRequest(BaseModel):
    campaign_type: str  # recovery, win_back, upsell, retention
    context: Optional[dict] = None


@router.get("/opportunities")
async def get_campaign_opportunities(
    user: CurrentUser = Depends(get_current_user),
):
    """Get current campaign opportunities identified by the agent."""
    # TODO: Call CampaignEngine.identify_opportunities()
    return {
        "opportunities": [],
        "total": 0,
    }


@router.post("/generate")
async def generate_campaign(
    request: CampaignRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Generate a campaign plan for SME approval."""
    # TODO: Call CampaignEngine.generate_campaign()
    return {
        "campaign_id": "placeholder",
        "status": "pending_approval",
        "message": f"Campaign plan for '{request.campaign_type}' generated. Pending your approval.",
    }


@router.post("/{campaign_id}/approve")
async def approve_campaign(
    campaign_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Approve a campaign for execution."""
    # TODO: Update status, trigger execution
    return {
        "campaign_id": campaign_id,
        "status": "approved",
        "message": "Campaign approved. Agent will begin execution.",
    }


@router.post("/{campaign_id}/reject")
async def reject_campaign(
    campaign_id: str,
    reason: Optional[str] = None,
    user: CurrentUser = Depends(get_current_user),
):
    """Reject a campaign plan."""
    return {
        "campaign_id": campaign_id,
        "status": "rejected",
        "message": "Campaign rejected. Agent will learn from this feedback.",
    }


@router.get("/history")
async def get_campaign_history(
    user: CurrentUser = Depends(get_current_user),
    limit: int = 20,
):
    """Get history of campaigns and their outcomes."""
    return {
        "campaigns": [],
        "total": 0,
    }
