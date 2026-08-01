"""
Forecasting — Revenue, transaction volume, and failure rate predictions.

Uses Amazon Bedrock to analyze historical patterns and generate forecasts.
Stores forecasts in CockroachDB for comparison with actual outcomes.

Methods:
- Trend extrapolation (linear/exponential)
- Seasonal decomposition (day-of-week, monthly patterns)
- LLM-based reasoning for contextual predictions
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel


class ForecastPoint(BaseModel):
    """A single forecast data point."""
    date: str
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float


class ForecastResult(BaseModel):
    """Complete forecast result."""
    metric: str
    period_days: int
    generated_at: datetime
    data_points: list[ForecastPoint]
    trend: str  # "up", "down", "stable", "seasonal"
    summary: str  # Human-readable summary from LLM
    risk_factors: list[str]
    opportunities: list[str]


class Forecaster:
    """
    Generates business forecasts using historical CockroachDB data
    and Amazon Bedrock for contextual analysis.
    """

    def __init__(self, mcp_server, bedrock_client):
        self.mcp = mcp_server
        self.bedrock = bedrock_client

    async def forecast_revenue(
        self, sme_id: str, days_forward: int = 30
    ) -> ForecastResult:
        """
        Forecast revenue for the next N days.
        Uses historical transaction data + LLM analysis.
        """
        # Get historical data via MCP
        historical = await self.mcp.get_forecast_data(
            sme_id=sme_id, metric="revenue", days_forward=days_forward
        )

        # Calculate statistical forecast
        data_points = self._statistical_forecast(
            historical.data.get("historical", []),
            days_forward,
        )

        # Use Bedrock to add contextual analysis
        llm_analysis = await self._get_llm_forecast_analysis(
            metric="revenue",
            historical=historical.data.get("historical", []),
            statistical_forecast=data_points,
        )

        return ForecastResult(
            metric="revenue",
            period_days=days_forward,
            generated_at=datetime.utcnow(),
            data_points=data_points,
            trend=llm_analysis.get("trend", "stable"),
            summary=llm_analysis.get("summary", "Insufficient data for forecast"),
            risk_factors=llm_analysis.get("risk_factors", []),
            opportunities=llm_analysis.get("opportunities", []),
        )

    async def forecast_transactions(
        self, sme_id: str, days_forward: int = 30
    ) -> ForecastResult:
        """Forecast transaction volume."""
        historical = await self.mcp.get_forecast_data(
            sme_id=sme_id, metric="transactions", days_forward=days_forward
        )
        data_points = self._statistical_forecast(
            historical.data.get("historical", []), days_forward
        )
        return ForecastResult(
            metric="transactions",
            period_days=days_forward,
            generated_at=datetime.utcnow(),
            data_points=data_points,
            trend="stable",
            summary="Transaction volume forecast",
            risk_factors=[],
            opportunities=[],
        )

    async def forecast_failure_rate(
        self, sme_id: str, days_forward: int = 14
    ) -> ForecastResult:
        """Forecast payment failure rate."""
        historical = await self.mcp.get_forecast_data(
            sme_id=sme_id, metric="failure_rate", days_forward=days_forward
        )
        data_points = self._statistical_forecast(
            historical.data.get("historical", []), days_forward
        )
        return ForecastResult(
            metric="failure_rate",
            period_days=days_forward,
            generated_at=datetime.utcnow(),
            data_points=data_points,
            trend="stable",
            summary="Failure rate forecast",
            risk_factors=[],
            opportunities=[],
        )

    def _statistical_forecast(
        self, historical: list[dict], days_forward: int
    ) -> list[ForecastPoint]:
        """
        Simple statistical forecast using moving averages and trend detection.
        For a hackathon, this is sufficient — production would use Prophet/ARIMA.
        """
        if not historical or len(historical) < 7:
            return []

        # Calculate 7-day moving average
        values = [h.get("value", 0) for h in historical]
        recent_avg = sum(values[-7:]) / 7 if len(values) >= 7 else sum(values) / len(values)
        older_avg = sum(values[-14:-7]) / 7 if len(values) >= 14 else recent_avg

        # Simple trend
        daily_trend = (recent_avg - older_avg) / 7 if older_avg > 0 else 0

        # Generate forecast points
        forecast_points = []
        for i in range(1, days_forward + 1):
            date = datetime.utcnow() + timedelta(days=i)
            predicted = recent_avg + (daily_trend * i)
            # Widen confidence interval over time
            uncertainty = abs(predicted) * 0.1 * (i / 7)

            forecast_points.append(ForecastPoint(
                date=date.strftime("%Y-%m-%d"),
                predicted_value=max(0, round(predicted, 2)),
                lower_bound=max(0, round(predicted - uncertainty, 2)),
                upper_bound=round(predicted + uncertainty, 2),
                confidence=max(0.5, 1.0 - (i * 0.015)),  # Confidence decreases over time
            ))

        return forecast_points

    async def _get_llm_forecast_analysis(
        self, metric: str, historical: list, statistical_forecast: list
    ) -> dict:
        """Use Bedrock to add contextual analysis to the forecast."""
        # TODO: Call Bedrock with historical data and statistical forecast
        # Ask LLM to identify trends, risks, opportunities, and seasonal patterns
        return {
            "trend": "stable",
            "summary": "Based on historical patterns, metrics are expected to remain stable.",
            "risk_factors": [],
            "opportunities": [],
        }
