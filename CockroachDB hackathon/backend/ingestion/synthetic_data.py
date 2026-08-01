"""
Synthetic Demo-Data Generator — Creates realistic payment data for demos.

Generates:
- Customers with realistic profiles
- Transaction history with seasonal patterns
- Realistic failure spikes and anomalies
- Subscription lifecycle events
- Inactive customer segments

Designed to showcase all agent capabilities without needing real Stripe data.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends

from ..api.auth import CurrentUser, check_sme_membership

router = APIRouter()

# Realistic business patterns
FAILURE_REASONS = [
    "card_declined",
    "insufficient_funds",
    "expired_card",
    "processing_error",
    "authentication_required",
    "do_not_honor",
    "invalid_card_number",
    "fraudulent",
    "lost_card",
    "stolen_card",
]

CUSTOMER_NAMES = [
    "Acme Corp", "TechStart Ltd", "Green Valley Farms", "Urban Fitness",
    "CloudNine Solutions", "Bright Ideas Inc", "Swift Logistics",
    "Peak Performance", "Harbor Consulting", "Sunrise Bakery",
    "MetroClean Services", "Digital Nomad Co", "FreshBite Catering",
    "SafeGuard Security", "EcoHome Supplies", "BlueWave Marketing",
    "PrimeTime Events", "DataFlow Analytics", "HealthFirst Clinic",
    "SkyBridge Architects",
]


class DemoDataConfig(BaseModel):
    """Configuration for synthetic data generation."""
    num_customers: int = 50
    days_of_history: int = 90
    avg_daily_transactions: int = 25
    base_failure_rate: float = 0.03  # 3% normal failure rate
    include_anomaly_spike: bool = True  # Add a failure spike for agent to detect
    include_inactive_customers: bool = True  # Some customers stop transacting
    include_seasonal_patterns: bool = True
    avg_transaction_amount: float = 85.0
    currency: str = "USD"


@router.post("/generate")
async def generate_demo_data(
    config: DemoDataConfig = DemoDataConfig(),
    user: CurrentUser = Depends(check_sme_membership),
):
    """
    Generate synthetic demo data for the SME.
    Creates customers, transactions, and realistic patterns.
    """
    sme_id = user.sme_id
    customers = _generate_customers(config.num_customers, sme_id)
    transactions = _generate_transactions(customers, config)
    anomalies = _inject_anomalies(transactions, config) if config.include_anomaly_spike else []

    # TODO: Bulk insert into CockroachDB
    # INSERT INTO customers ... ON CONFLICT DO NOTHING
    # INSERT INTO transactions ...

    return {
        "generated": {
            "customers": len(customers),
            "transactions": len(transactions),
            "anomaly_events": len(anomalies),
            "date_range": {
                "from": (datetime.utcnow() - timedelta(days=config.days_of_history)).isoformat(),
                "to": datetime.utcnow().isoformat(),
            },
        },
        "features_demonstrated": [
            "Normal transaction flow",
            "Payment failure spike (for agent investigation)",
            "Inactive customers (for follow-up task)",
            "Seasonal patterns (for baseline learning)",
            "Recovery candidates (for campaign suggestions)",
        ],
    }


@router.post("/generate-quick")
async def generate_quick_demo(
    user: CurrentUser = Depends(check_sme_membership),
):
    """Generate a quick demo dataset with sensible defaults."""
    config = DemoDataConfig(
        num_customers=30,
        days_of_history=60,
        avg_daily_transactions=20,
        include_anomaly_spike=True,
        include_inactive_customers=True,
    )
    return await generate_demo_data(config, user)


def _generate_customers(count: int, sme_id: str) -> list[dict]:
    """Generate realistic customer profiles."""
    customers = []
    for i in range(count):
        name = CUSTOMER_NAMES[i % len(CUSTOMER_NAMES)] if i < len(CUSTOMER_NAMES) else f"Customer {i+1}"
        customer = {
            "id": str(uuid.uuid4()),
            "sme_id": sme_id,
            "email": f"{name.lower().replace(' ', '.')}@example.com",
            "name": name,
            "stripe_customer_id": f"cus_demo_{uuid.uuid4().hex[:12]}",
            "status": "active",
            "created_at": datetime.utcnow() - timedelta(days=random.randint(30, 365)),
        }
        customers.append(customer)

    # Mark some as inactive
    inactive_count = int(count * 0.15)
    for c in customers[-inactive_count:]:
        c["status"] = "inactive"

    return customers


def _generate_transactions(customers: list[dict], config: DemoDataConfig) -> list[dict]:
    """Generate transaction history with realistic patterns."""
    transactions = []
    active_customers = [c for c in customers if c["status"] == "active"]
    inactive_customers = [c for c in customers if c["status"] == "inactive"]

    for day_offset in range(config.days_of_history, 0, -1):
        date = datetime.utcnow() - timedelta(days=day_offset)

        # Seasonal pattern: more transactions on weekdays
        day_of_week = date.weekday()
        daily_multiplier = 1.0
        if config.include_seasonal_patterns:
            if day_of_week >= 5:  # Weekend
                daily_multiplier = 0.6
            elif day_of_week == 0:  # Monday boost
                daily_multiplier = 1.3

        num_transactions = int(config.avg_daily_transactions * daily_multiplier * random.uniform(0.7, 1.3))

        for _ in range(num_transactions):
            customer = random.choice(active_customers)
            amount = max(5.0, random.gauss(config.avg_transaction_amount, config.avg_transaction_amount * 0.4))

            # Normal failure rate
            is_failed = random.random() < config.base_failure_rate
            status = "failed" if is_failed else "succeeded"
            failure_reason = random.choice(FAILURE_REASONS) if is_failed else None

            transaction = {
                "id": str(uuid.uuid4()),
                "sme_id": customer["sme_id"],
                "customer_id": customer["id"],
                "amount": round(amount, 2),
                "currency": config.currency,
                "status": status,
                "failure_reason": failure_reason,
                "created_at": date + timedelta(
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59),
                ),
                "stripe_payment_intent_id": f"pi_demo_{uuid.uuid4().hex[:16]}",
            }
            transactions.append(transaction)

        # Inactive customers: generate transactions only early in history
        if day_offset > config.days_of_history * 0.5:
            for customer in inactive_customers:
                if random.random() < 0.3:
                    transaction = {
                        "id": str(uuid.uuid4()),
                        "sme_id": customer["sme_id"],
                        "customer_id": customer["id"],
                        "amount": round(random.gauss(config.avg_transaction_amount, 20), 2),
                        "currency": config.currency,
                        "status": "succeeded",
                        "failure_reason": None,
                        "created_at": date + timedelta(hours=random.randint(8, 22)),
                        "stripe_payment_intent_id": f"pi_demo_{uuid.uuid4().hex[:16]}",
                    }
                    transactions.append(transaction)

    return transactions


def _inject_anomalies(transactions: list[dict], config: DemoDataConfig) -> list[dict]:
    """
    Inject a realistic failure spike into the last 2 days.
    This gives the agent something to investigate.
    """
    anomaly_transactions = []
    spike_start = datetime.utcnow() - timedelta(hours=36)
    spike_end = datetime.utcnow() - timedelta(hours=12)

    # Generate a spike of failures (20% failure rate vs normal 3%)
    for _ in range(40):
        t = spike_start + timedelta(
            hours=random.uniform(0, (spike_end - spike_start).total_seconds() / 3600)
        )
        transaction = {
            "id": str(uuid.uuid4()),
            "sme_id": transactions[0]["sme_id"] if transactions else "demo",
            "customer_id": random.choice(transactions)["customer_id"] if transactions else "demo",
            "amount": round(random.gauss(config.avg_transaction_amount, 20), 2),
            "currency": config.currency,
            "status": "failed",
            "failure_reason": random.choice(["card_declined", "processing_error", "authentication_required"]),
            "created_at": t,
            "stripe_payment_intent_id": f"pi_demo_{uuid.uuid4().hex[:16]}",
            "metadata": {"anomaly_injected": True},
        }
        anomaly_transactions.append(transaction)

    return anomaly_transactions
