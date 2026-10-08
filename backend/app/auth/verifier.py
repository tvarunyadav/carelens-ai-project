from typing import Dict, Any, Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings
from app.schemas.models import StaffProfile

security = HTTPBearer(auto_error=False)

# In-memory mock database store for local dev / testing when live Supabase DB is disconnected
DEV_STAFF_DB: Dict[str, StaffProfile] = {
    "dev_user_alice": StaffProfile(
        id="11111111-aaaa-1111-aaaa-111111111111",
        email="dr.alice@clinic.org",
        full_name="Dr. Alice Morgan",
        role="doctor"
    ),
    "dev_user_bob": StaffProfile(
        id="22222222-bbbb-2222-bbbb-222222222222",
        email="coord.bob@clinic.org",
        full_name="Bob Vance",
        role="coordinator"
    ),
    "dev_user_admin": StaffProfile(
        id="33333333-cccc-3333-cccc-333333333333",
        email="admin.sam@clinic.org",
        full_name="Sam Admin",
        role="admin"
    )
}

async def verify_supabase_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> StaffProfile:
    """
    Verifies Supabase Bearer JWT access token from HTTP Authorization header.
    Rejects missing, malformed, or expired tokens.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header or Bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials.strip()

    # 1. Dev / Test token support for local verification & pytest
    if token.startswith("test-token-"):
        user_key = token.replace("test-token-", "")
        if user_key in DEV_STAFF_DB:
            return DEV_STAFF_DB[user_key]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid test token user identity"
        )

    # 2. Live Supabase JWT verification
    try:
        # If SUPABASE_JWT_SECRET is configured, decode and verify JWT signature
        if settings.SUPABASE_JWT_SECRET and settings.SUPABASE_JWT_SECRET != "your-supabase-jwt-secret":
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
            sub = payload.get("sub")
            email = payload.get("email", "")
            user_metadata = payload.get("user_metadata", {})
            role = user_metadata.get("role", "doctor")
            full_name = user_metadata.get("full_name", email.split("@")[0].capitalize())

            if not sub:
                raise HTTPException(status_code=401, detail="Invalid token subject payload")

            return StaffProfile(
                id=sub,
                email=email,
                full_name=full_name,
                role=role
            )
        else:
            # Unverified decode attempt for fallback or unconfigured secret check
            # Real deployment requires SUPABASE_JWT_SECRET or Supabase client verification
            payload = jwt.decode(token, options={"verify_signature": False})
            sub = payload.get("sub")
            email = payload.get("email", "")
            if not sub or not email:
                raise HTTPException(status_code=401, detail="Invalid JWT token structure")

            user_metadata = payload.get("user_metadata", {})
            role = user_metadata.get("role", "doctor")
            full_name = user_metadata.get("full_name", email.split("@")[0].capitalize())

            return StaffProfile(
                id=sub,
                email=email,
                full_name=full_name,
                role=role
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token validation failed"
        )
