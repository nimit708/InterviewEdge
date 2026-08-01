"""
Daily Business Brief — AI-generated daily summary for SMEs.

Every day (configurable), the agent generates a brief covering:
- Payment performance summary
- Key metric changes vs baseline
- Detected anomalies
- Agent recommendations
- Forecast outlook
- Pending approvals
- Campaign opportunities
"""

from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional


class DailyBriefSection(BaseModel):
    title: str
    content: str
    severity: str = "info"  # info, warning, alert
    metrics: Optional[dict] = None


class DailyBrief(BaseModel):
    """Complete daily business brief."""
    sme_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    headline: str
    health_score: int  # 0-100
    sections: list[DailyBriefSection]
    action_items: list[str]
    forecast_summary: str


class DailyBriefGenerator:
    """Generates daily business briefs using Bedrock and CockroachDB data."""

    def __init__(self, mcp_server, memory_store, bedrock_client):
        self.mcp = mcp_server
        self.memory = memory_store
        self.bedrock = bedrock_client

    async def generate(self, sme_id: str) -> DailyBrief:
        """Generate the daily business brief."""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        # Gather all data
        revenue = await self.mcp.get_revenue_metrics(
            sme_id=sme_id, period="24h"
        )
        failures = await self.mcp.get_failure_analysis(
            sme_id=sme_id, hours_back=24
        )
        customer_health = await self.mcp.get_customer_health(sme_id=sme_id)

        # Get baselines for comparison
        baselines = await self.memory.get_baselines(sme_id)

        # Build sections
        sections = []

        # Revenue section
        rev_data = revenue.data or {}
        sections.append(DailyBriefSection(
            title="Revenue Performance",
            content=self._format_revenue(rev_data, baselines),
            severity="info",
            metrics=rev_data,
        ))

        # Failure section
        fail_data = failures.data or {}
        failure_severity = "alert" if fail_data.get("failure_rate", 0) > 0.05 else "info"
        sections.append(DailyBriefSection(
            title="Payment Health",
            content=self._format_failures(fail_data, baselines),
            severity=failure_severity,
            metrics=fail_data,
        ))

        # Customer section
        health_data = customer_health.data or {}
        sections.append(DailyBriefSection(
            title="Customer Health",
            content=self._format_customer_health(health_data),
            severity="warning" if health_data.get("at_risk", 0) > 3 else "info",
            metrics=health_data,
        ))

        # Generate LLM summary
        llm_brief = await self._generate_llm_brief(sections)

        return DailyBrief(
            sme_id=sme_id,
            generated_at=now,
            period_start=yesterday,
            period_end=now,
            headline=llm_brief.get("headline", "Daily Business Brief"),
            health_score=self._calculate_health_score(rev_data, fail_data, health_data),
            sections=sections,
            action_items=llm_brief.get("action_items", []),
            forecast_summary=llm_brief.get("forecast", "No forecast available"),
        )

    def _format_revenue(self, data: dict, baselines: list) -> str:
        revenue = data.get("total_revenue", 0)
        txn_count = data.get("transaction_count", 0)
        return (
            f"Revenue: ${revenue:,.2f} across {txn_count} transactions. "
            f"Growth rate: {data.get('growth_rate', 0):.1%}"
        )

    def _format_failures(self, data: dict, baselines: list) -> str:
        rate = data.get("failure_rate", 0)
        total = data.get("total_failures", 0)
        return f"Failure rate: {rate:.1%} ({total} failures in 24h)"

    def _format_customer_health(self, data: dict) -> str:
        return (
            f"Active: {data.get('active', 0)}, "
            f"At-risk: {data.get('at_risk', 0)}, "
            f"Churned: {data.get('churned', 0)}"
        )

    def _calculate_health_score(
        self, revenue: dict, failures: dict, customers: dict
    ) -> int:
        """Calculate overall business health score (0-100)."""
        score = 100
        # Penalize high failure rate
        failure_rate = failures.get("failure_rate", 0)
        if failure_rate > 0.1:
            score -= 30
        elif failure_rate > 0.05:
            score -= 15
        elif failure_rate > 0.03:
            score -= 5

        # Penalize negative growth
        growth = revenue.get("growth_rate", 0)
        if growth < -0.1:
            score -= 20
        elif growth < 0:
            score -= 10

        # Penalize high churn
        at_risk = customers.get("at_risk", 0)
        total = customers.get("total_customers", 1)
        if total > 0 and at_risk / total > 0.2:
            score -= 15

        return max(0, min(100, score))

    async def _generate_llm_brief(self, sections: list) -> dict:
        """Use Bedrock to generate a natural language brief."""
        # TODO: Call Bedrock with section data
        return {
            "headline": "Business performance is on track",
            "action_items": [],
            "forecast": "Stable outlook for the next 7 days",
        }
