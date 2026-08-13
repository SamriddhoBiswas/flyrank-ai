import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

# Single shared Supabase client — initialised once at import time
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# HTTPBearer with auto_error=False so we can return 401 (not 403) ourselves
# when the Authorization header is absent or malformed.
# FastAPI still renders the padlock in Swagger docs.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
):
    """
    Reusable FastAPI dependency — the auth guard.

    1. Rejects missing / malformed Authorization header → 401 "Access token required"
    2. Asks Supabase to verify the token                → 401 "Invalid or expired token"
    3. Returns the verified User object to the route handler.
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required",
        )

    token = credentials.credentials
    try:
        response = supabase.auth.get_user(token)
        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )
        return response.user
    except HTTPException:
        raise  # re-raise our own 401s unchanged
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
