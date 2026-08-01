"""
LedgerMind FastAPI Application
Main entry point for the API service.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .auth import get_current_user, check_sme_membership
from .routers import agent_router, payments_router, dashboard_router, approvals_router
from .routers import campaign_router, audit_router, forecast_router, demo_router
from .database import init_db, close_db
from ..ingestion.csv_import import router as csv_router
from ..ingestion.stripe_webhook import router as stripe_webhook_router
from ..ingestion.synthetic_data import router as synthetic_data_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="LedgerMind API",
    description="AI-Powered Payment Operations Agent for SMEs",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for Amplify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    dashboard_router.router,
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_user)],
)

app.include_router(
    agent_router.router,
    prefix="/api/v1/agent",
    tags=["agent"],
    dependencies=[Depends(get_current_user), Depends(check_sme_membership)],
)

app.include_router(
    payments_router.router,
    prefix="/api/v1/payments",
    tags=["payments"],
    dependencies=[Depends(get_current_user)],
)

app.include_router(
    approvals_router.router,
    prefix="/api/v1/approvals",
    tags=["approvals"],
    dependencies=[Depends(get_current_user), Depends(check_sme_membership)],
)

app.include_router(
    campaign_router.router,
    prefix="/api/v1/campaigns",
    tags=["campaigns"],
    dependencies=[Depends(get_current_user), Depends(check_sme_membership)],
)

app.include_router(
    audit_router.router,
    prefix="/api/v1/audit",
    tags=["audit"],
    dependencies=[Depends(get_current_user)],
)

app.include_router(
    forecast_router.router,
    prefix="/api/v1/forecast",
    tags=["forecast"],
    dependencies=[Depends(get_current_user), Depends(check_sme_membership)],
)


# Ingestion routes
app.include_router(
    csv_router,
    prefix="/api/v1/import",
    tags=["import"],
    dependencies=[Depends(get_current_user), Depends(check_sme_membership)],
)

app.include_router(
    stripe_webhook_router,
    prefix="/api/v1/webhook",
    tags=["webhook"],
)

app.include_router(
    synthetic_data_router,
    prefix="/api/v1/demo-data",
    tags=["demo-data"],
    dependencies=[Depends(get_current_user), Depends(check_sme_membership)],
)

# Public demo (no auth)
app.include_router(
    demo_router.router,
    prefix="/api/v1/demo",
    tags=["demo"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ledgermind-api"}
