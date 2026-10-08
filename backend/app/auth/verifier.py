from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt
from jwt import PyJWKClient
from app.core.config import settings
from app.schemas.models import StaffProfile

security = HTTPBearer(auto_error=False)

# Optional PyJWKClient cache for asymmetric key validation
_jwks_client: Optional[PyJWKClient] = None

def get_jwks_client() -> Optional[PyJWKClient]:
    global _jwks_client
    if _jwks_client is None and settings.SUPABASE_URL and "placeholder" not in settings.SUPABASE_URL and "your-supabase" not in settings.SUPABASE_URL:
        jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client

async def verify_supabase_token(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> StaffProfile:
    """
    Verifies Supabase Bearer JWT access token against Supabase Auth API or public JWKS / JWT secret.
    Rejects missing, invalid, expired, or unverified tokens.
    Does NOT contain hardcoded authentication bypasses.
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

    supabase_url = settings.SUPABASE_URL.rstrip('/')
    is_live_supabase_configured = (
        supabase_url
        and "your-supabase-project" not in supabase_url
        and "placeholder" not in supabase_url
    )

    # 1. Primary Verified Token Method: Supabase Auth API /user endpoint
    if is_live_supabase_configured:
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_ANON_KEY
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{supabase_url}/auth/v1/user", headers=headers)
                
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get("id")
                email = user_data.get("email", "")
                user_metadata = user_data.get("user_metadata", {})
                role = user_metadata.get("role", "doctor")
                full_name = user_metadata.get("full_name", email.split("@")[0].capitalize() if email else "Staff User")

                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid Supabase user payload")

                return StaffProfile(
                    id=user_id,
                    email=email,
                    full_name=full_name,
                    role=role
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication token rejected by Supabase Auth service"
                )
        except httpx.RequestError as e:
            # Fall back to local secret or JWKS decoding if network request fails
            pass

    # 2. Secondary Verified Method: Symmetric secret verification if SUPABASE_JWT_SECRET is configured
    if settings.SUPABASE_JWT_SECRET and "your-supabase" not in settings.SUPABASE_JWT_SECRET:
        try:
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
            full_name = user_metadata.get("full_name", email.split("@")[0].capitalize() if email else "Staff User")

            if not sub:
                raise HTTPException(status_code=401, detail="Invalid token subject payload")

            return StaffProfile(id=sub, email=email, full_name=full_name, role=role)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Authentication token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid authentication token: {str(e)}")

    # 3. Tertiary Method: Asymmetric JWKS key validation
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
            sub = payload.get("sub")
            email = payload.get("email", "")
            user_metadata = payload.get("user_metadata", {})
            role = user_metadata.get("role", "doctor")
            full_name = user_metadata.get("full_name", email.split("@")[0].capitalize() if email else "Staff User")

            if not sub:
                raise HTTPException(status_code=401, detail="Invalid token subject payload")

            return StaffProfile(id=sub, email=email, full_name=full_name, role=role)
        except Exception:
            pass

    # Unconfigured or invalid token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid, expired, or unverified authentication token. Please configure valid Supabase credentials."
    )
