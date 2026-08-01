"""
Authentication and authorization module.
Validates Cognito JWT tokens and checks SME membership/roles.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional

from ..config import get_settings

security = HTTPBearer()

settings = get_settings()
COGNITO_REGION = settings.cognito_region
COGNITO_USER_POOL_ID = settings.cognito_user_pool_id
COGNITO_APP_CLIENT_ID = settings.cognito_app_client_id

JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"


class CurrentUser(BaseModel):
    """Represents the authenticated user extracted from JWT."""
    sub: str
    email: str
    sme_id: Optional[str] = None
    roles: list[str] = []
    permissions: list[str] = []


_jwks_cache: Optional[dict] = None


async def _get_jwks() -> dict:
    """Fetch and cache JWKS from Cognito."""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL)
            _jwks_cache = response.json()
    return _jwks_cache


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> CurrentUser:
    """
    Validate Cognito JWT and extract user information.
    """
    token = credentials.credentials

    try:
        jwks = await _get_jwks()
        # Decode without verification first to get the kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Find the matching key
        rsa_key = None
        for key in jwks.get("keys", []):
            if key["kid"] == kid:
                rsa_key = key
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key not found",
            )

        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=COGNITO_APP_CLIENT_ID,
            issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}",
        )

        return CurrentUser(
            sub=payload["sub"],
            email=payload.get("email", ""),
            sme_id=payload.get("custom:sme_id"),
            roles=payload.get("custom:roles", "").split(",") if payload.get("custom:roles") else [],
            permissions=payload.get("custom:permissions", "").split(",") if payload.get("custom:permissions") else [],
        )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def check_sme_membership(user: CurrentUser = Security(get_current_user)):
    """Verify user has an active SME membership."""
    if not user.sme_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active SME membership required",
        )
    return user
