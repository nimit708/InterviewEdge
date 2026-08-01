"""
Dashboard router — overview data for the SME dashboard.
"""

from fastapi import APIRouter, Depends

from ..auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    user: CurrentUser = Depends(get_current_user),
):
    """
    Get the main dashboard overview including:
    - Key payment metrics
    - Active agent tasks
    - Pending approvals
    - Recent anomalies
    - Agent recommendations
    """
    # TODO: Aggregate from multiple sources
    return {
        "metrics": {
            "revenue_today": 0.0,
            "transactions_today": 0,
            "failure_rate": 0.0,
            "active_customers": 0,
        },
        "agent": {
            "active_tasks": 0,
            "pending_approvals": 0,
            "recent_recommendations": [],
            "monitoring": [],
        },
        "anomalies": [],
        "health_score": 100,
    }


@router.get("/activity-feed")
async def get_activity_feed(
    user: CurrentUser = Depends(get_current_user),
    limit: int = 20,
):
    """
    Get the real-time activity feed showing:
    - Agent observations
    - Payment events
    - Approval requests
    - Completed actions and outcomes
    """
    # TODO: Query activity from CockroachDB
    return {
        "activities": [],
        "total": 0,
    }
