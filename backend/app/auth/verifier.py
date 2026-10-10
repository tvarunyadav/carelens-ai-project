import time
from typing import Optional, Dict, Tuple
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt
from jwt import PyJWKClient
from app.core.config import settings
from app.core.http_client import get_http_client
from app.schemas.models import StaffProfile

security = HTTPBearer(auto_error=False)

_jwks_client: Optional[PyJWKClient] = None

# Short-lived in-memory TTL cache for cryptographically verified staff profiles (token -> (expiry_timestamp, StaffProfile))
# TTL is set to 30 seconds to optimize rapid back-to-back request chains (e.g. /me followed by /patients)
# while preserving cryptographic token verification and database staff profile enforcement.
_profile_cache: Dict[str, Tuple[float, StaffProfile]] = {}
CACHE_TTL_SECONDS = 30.0

def get_jwks_client() -> Optional[PyJWKClient]:
    global _jwks_client
    if _jwks_client is None and settings.SUPABASE_URL and "placeholder" not in settings.SUPABASE_URL and "your-supabase" not in settings.SUPABASE_URL:
        jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client

def clear_profile_cache() -> None:
    """Utility function to clear cached profiles."""
    global _profile_cache
    _profile_cache.clear()

async def fetch_staff_profile_from_db(user_id: str, token: str) -> StaffProfile:
    """
    Loads staff profile directly from public.staff_profiles table in Supabase PostgREST.
    Strictly verifies identity against persisted database row.
    Never infers roles from email or user_metadata.
    Raises 403 Forbidden if profile row is missing.
    Raises 503 Service Unavailable on database/network failures.
    """
    supabase_url = settings.SUPABASE_URL.rstrip('/')
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": settings.SUPABASE_ANON_KEY
    }
    
    url = f"{supabase_url}/rest/v1/staff_profiles?id=eq.{user_id}&select=id,email,full_name,role"
    client = get_http_client()
    
    try:
        response = await client.get(url, headers=headers)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database access failure: Unable to verify staff profile ({str(exc)})"
        )

    if response.status_code == 200:
        rows = response.json()
        if not rows or len(rows) == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Staff profile record not found in system"
            )
        row = rows[0]
        return StaffProfile(
            id=row["id"],
            email=row["email"],
            full_name=row["full_name"],
            role=row["role"]
        )
    elif response.status_code in (401, 403):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient database permissions to load staff profile"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database query failure (status {response.status_code}): Unable to verify staff profile"
        )

async def verify_supabase_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> StaffProfile:
    """
    Cryptographically verifies Supabase Bearer JWT access token against Supabase Auth API,
    configured JWT secret, or public JWKS key set.
    Derives trusted identity ONLY after successful verification.
    Then loads and enforces the persisted StaffProfile from public.staff_profiles in Supabase.
    Rejects tampered, expired, wrong-project, or unverified tokens.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header or Bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials.strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty authentication token provided"
        )

    now = time.time()
    if token in _profile_cache:
        exp_time, cached_profile = _profile_cache[token]
        if now < exp_time:
            return cached_profile

    supabase_url = settings.SUPABASE_URL.rstrip('/')
    is_live_supabase_configured = (
        supabase_url
        and "your-supabase-project" not in supabase_url
        and "placeholder" not in supabase_url
    )

    verified_user_id: Optional[str] = None

    # 1. Primary Method: Supabase Auth API /user endpoint verification
    if is_live_supabase_configured:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_ANON_KEY
            }
            client = get_http_client()
            response = await client.get(f"{supabase_url}/auth/v1/user", headers=headers)
                
            if response.status_code == 200:
                user_data = response.json()
                verified_user_id = user_data.get("id")
            elif response.status_code in (400, 401, 403):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication token rejected by Supabase Auth service"
                )
        except httpx.RequestError:
            pass

    # 2. Secondary Method: Cryptographic symmetric verification via SUPABASE_JWT_SECRET
    if not verified_user_id and settings.SUPABASE_JWT_SECRET and "your-supabase" not in settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
            verified_user_id = payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid authentication token: {str(e)}")

    # 3. Tertiary Method: Cryptographic asymmetric JWKS signature verification
    if not verified_user_id:
        jwks_client = get_jwks_client()
        if jwks_client:
            try:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256", "ES256"],
                    audience="authenticated"
                )
                verified_user_id = payload.get("sub")
            except Exception:
                pass

    if not verified_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, tampered, or unverified authentication token."
        )

    # 4. Load persisted staff profile row for the cryptographically verified user ID
    profile = await fetch_staff_profile_from_db(verified_user_id, token)

    # Cache verified profile for short duration
    _profile_cache[token] = (now + CACHE_TTL_SECONDS, profile)

    return profile
