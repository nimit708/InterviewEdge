"""
Audit router — Full activity trail for transparency.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime

from ..auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/events")
async def get_audit_events(
    user: CurrentUser = Depends(get_current_user),
    event_type: Optional[str] = None,
    actor: Optional[str] = None,
    since: Optional[datetime] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    """Get audit trail with optional filters."""
    # TODO: Query from CockroachDB audit_events table
    return {
        "events": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


@router.get("/events/{entity_id}/trail")
async def get_entity_audit_trail(
    entity_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Get full audit trail for a specific entity (decision, task, campaign)."""
    # TODO: Query by related_entity_id
    return {
        "entity_id": entity_id,
        "trail": [],
    }
