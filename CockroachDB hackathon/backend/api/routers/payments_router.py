"""
Payments router — payment data access and analytics.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime

from ..auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/summary")
async def get_payment_summary(
    user: CurrentUser = Depends(get_current_user),
    period: str = Query("7d", description="Time period: 24h, 7d, 30d, 90d"),
):
    """Get payment summary with key metrics."""
    # TODO: Aggregate from CockroachDB
    return {
        "period": period,
        "total_transactions": 0,
        "total_revenue": 0.0,
        "failure_rate": 0.0,
        "avg_transaction_value": 0.0,
        "trend": "stable",
    }


@router.get("/failures")
async def get_payment_failures(
    user: CurrentUser = Depends(get_current_user),
    since: Optional[datetime] = None,
    limit: int = 100,
):
    """Get recent payment failures for investigation."""
    # TODO: Query failures from CockroachDB
    return {
        "failures": [],
        "total": 0,
    }


@router.get("/anomalies")
async def get_detected_anomalies(
    user: CurrentUser = Depends(get_current_user),
):
    """Get anomalies detected by the agent's baseline comparison."""
    # TODO: Query anomalies detected by agent
    return {
        "anomalies": [],
        "total": 0,
    }


@router.get("/customers/inactive")
async def get_inactive_customers(
    user: CurrentUser = Depends(get_current_user),
    days_inactive: int = Query(30, description="Days since last transaction"),
):
    """Get customers who haven't transacted recently."""
    # TODO: Query from CockroachDB
    return {
        "customers": [],
        "total": 0,
        "days_inactive": days_inactive,
    }
