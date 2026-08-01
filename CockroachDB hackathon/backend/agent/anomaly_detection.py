"""
Anomaly Detection — Detects unusual patterns in payment data.

Uses learned baselines from CockroachDB to identify:
- Payment failure spikes
- Revenue drops
- Unusual transaction volumes
- Customer churn acceleration
- Suspicious transaction patterns

Detection methods:
- Statistical (z-score against historical baselines)
- Rate-of-change (rapid shifts in metrics)
- Pattern matching (known failure patterns from memory)
"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from enum import Enum

from .memory import AgenticMemoryStore, BaselineMemory


class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(str, Enum):
    FAILURE_SPIKE = "failure_spike"
    REVENUE_DROP = "revenue_drop"
    VOLUME_ANOMALY = "volume_anomaly"
    CHURN_ACCELERATION = "churn_acceleration"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    UNUSUAL_TIMING = "unusual_timing"


class DetectedAnomaly(BaseModel):
    """A detected anomaly in payment data."""
    id: str
    sme_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    metric_name: str
    current_value: float
    baseline_value: float
    deviation_score: float  # How many std devs from normal
    description: str
    detected_at: datetime
    window_start: datetime
    window_end: datetime
    affected_count: Optional[int] = None  # Number of affected transactions/customers
    metadata: Optional[dict] = None


class AnomalyDetector:
    """
    Detects anomalies by comparing current metrics to learned baselines.
    Uses CockroachDB data and agent memory for context.
    """

    def __init__(self, memory_store: AgenticMemoryStore):
        self.memory = memory_store

    async def run_detection(self, sme_id: str) -> list[DetectedAnomaly]:
        """Run all anomaly detection checks for an SME."""
        anomalies = []

        anomalies.extend(await self._check_failure_rate(sme_id))
        anomalies.extend(await self._check_revenue(sme_id))
        anomalies.extend(await self._check_volume(sme_id))
        anomalies.extend(await self._check_churn(sme_id))

        return anomalies

    async def _check_failure_rate(self, sme_id: str) -> list[DetectedAnomaly]:
        """Check if current failure rate exceeds baseline."""
        anomalies = []
        baselines = await self.memory.get_baselines(sme_id)
        failure_baseline = next(
            (b for b in baselines if b.metric_name == "failure_rate"), None
        )

        if not failure_baseline:
            return anomalies

        # TODO: Query current failure rate from CockroachDB
        # SELECT COUNT(*) FILTER (WHERE status = 'failed')::float / COUNT(*)
        # FROM transactions
        # WHERE sme_id = $1 AND created_at >= NOW() - INTERVAL '1 hour'
        current_failure_rate = 0.0

        deviation = self._calculate_z_score(
            current_failure_rate,
            failure_baseline.mean_value,
            failure_baseline.std_deviation,
        )

        if deviation > 2.0:  # More than 2 standard deviations
            severity = self._severity_from_deviation(deviation)
            anomalies.append(DetectedAnomaly(
                id=f"anomaly_{sme_id}_{datetime.utcnow().strftime('%Y%m%d%H%M')}",
                sme_id=sme_id,
                anomaly_type=AnomalyType.FAILURE_SPIKE,
                severity=severity,
                metric_name="failure_rate",
                current_value=current_failure_rate,
                baseline_value=failure_baseline.mean_value,
                deviation_score=deviation,
                description=f"Payment failure rate ({current_failure_rate:.1%}) is {deviation:.1f}x above normal ({failure_baseline.mean_value:.1%})",
                detected_at=datetime.utcnow(),
                window_start=datetime.utcnow() - timedelta(hours=1),
                window_end=datetime.utcnow(),
            ))

        return anomalies

    async def _check_revenue(self, sme_id: str) -> list[DetectedAnomaly]:
        """Check for unexpected revenue drops."""
        # TODO: Compare current hourly/daily revenue against baseline
        return []

    async def _check_volume(self, sme_id: str) -> list[DetectedAnomaly]:
        """Check for unusual transaction volumes."""
        # TODO: Compare current volume against baseline
        return []

    async def _check_churn(self, sme_id: str) -> list[DetectedAnomaly]:
        """Check if customer churn rate is accelerating."""
        # TODO: Compare recent inactive customer rate against baseline
        return []

    def _calculate_z_score(self, current: float, mean: float, std_dev: float) -> float:
        """Calculate z-score (number of standard deviations from mean)."""
        if std_dev == 0:
            return 0.0
        return abs(current - mean) / std_dev

    def _severity_from_deviation(self, deviation: float) -> AnomalySeverity:
        """Map deviation score to severity level."""
        if deviation > 4.0:
            return AnomalySeverity.CRITICAL
        elif deviation > 3.0:
            return AnomalySeverity.HIGH
        elif deviation > 2.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW
