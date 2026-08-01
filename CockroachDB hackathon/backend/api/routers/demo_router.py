"""
Public Demo router — Endpoints for the public demo experience.

Provides a self-contained demo flow:
1. Auto-login with demo credentials
2. Pre-populated synthetic data
3. Guided walkthrough of features
4. No real payment processing
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DemoSession(BaseModel):
    """A demo session for public access."""
    session_id: str
    demo_sme_id: str
    demo_user_email: str
    token: str  # Demo JWT
    features: list[str]


@router.post("/start")
async def start_demo():
    """
    Start a public demo session.
    Creates a temporary SME account with synthetic data.
    """
    # TODO: Create temp demo account, generate demo data, return demo JWT
    return {
        "session_id": "demo_session",
        "message": "Demo started! Synthetic data has been generated.",
        "demo_user": {
            "email": "demo@ledgermind.ai",
            "sme_name": "Demo Coffee Shop",
        },
        "features_available": [
            "Dashboard with live metrics",
            "AI Agent chat and task execution",
            "Anomaly detection (pre-injected failure spike)",
            "Approval workflow",
            "Revenue forecasting",
            "Campaign suggestions",
            "Audit trail",
            "Daily brief",
        ],
        "walkthrough": [
            "1. View the Dashboard — notice the anomaly alert",
            "2. Open Agent — ask 'Investigate the failure spike'",
            "3. Review the agent's recommendation in Approvals",
            "4. Approve the action and watch the outcome",
            "5. Check Forecast for revenue predictions",
            "6. View Audit trail for full transparency",
        ],
    }


@router.get("/status/{session_id}")
async def get_demo_status(session_id: str):
    """Get current demo session status."""
    return {
        "session_id": session_id,
        "active": True,
        "data_generated": True,
        "expires_in_minutes": 30,
    }


@router.post("/reset/{session_id}")
async def reset_demo(session_id: str):
    """Reset demo data to fresh state."""
    return {
        "session_id": session_id,
        "message": "Demo reset. Fresh synthetic data generated.",
    }
