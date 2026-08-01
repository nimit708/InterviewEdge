"""
Forecast router — Revenue, volume, and failure rate predictions.
"""

from fastapi import APIRouter, Depends, Query

from ..auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/revenue")
async def get_revenue_forecast(
    user: CurrentUser = Depends(get_current_user),
    days: int = Query(30, description="Days to forecast"),
):
    """Get revenue forecast for the next N days."""
    # TODO: Call Forecaster.forecast_revenue()
    return {
        "metric": "revenue",
        "period_days": days,
        "data_points": [],
        "trend": "stable",
        "summary": "Forecast not yet available — generate demo data first.",
    }


@router.get("/transactions")
async def get_transaction_forecast(
    user: CurrentUser = Depends(get_current_user),
    days: int = Query(30, description="Days to forecast"),
):
    """Get transaction volume forecast."""
    # TODO: Call Forecaster.forecast_transactions()
    return {
        "metric": "transactions",
        "period_days": days,
        "data_points": [],
        "trend": "stable",
        "summary": "Forecast not yet available.",
    }


@router.get("/failure-rate")
async def get_failure_rate_forecast(
    user: CurrentUser = Depends(get_current_user),
    days: int = Query(14, description="Days to forecast"),
):
    """Get failure rate forecast."""
    # TODO: Call Forecaster.forecast_failure_rate()
    return {
        "metric": "failure_rate",
        "period_days": days,
        "data_points": [],
        "trend": "stable",
        "summary": "Forecast not yet available.",
    }


@router.get("/daily-brief")
async def get_daily_brief(
    user: CurrentUser = Depends(get_current_user),
):
    """Get today's AI-generated daily business brief."""
    # TODO: Call DailyBriefGenerator.generate()
    return {
        "headline": "Welcome to LedgerMind",
        "health_score": 100,
        "sections": [],
        "action_items": [],
        "forecast_summary": "Generate demo data to see your first daily brief.",
        "generated_at": None,
    }
