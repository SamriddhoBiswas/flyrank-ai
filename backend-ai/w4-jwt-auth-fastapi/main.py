from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth import bearer_scheme, get_current_user, supabase

# ── App setup ─────────────────────────────────────────────────────────────────
# Setting openapi_tags + security on app-level means FastAPI renders the
# Authorize padlock automatically on protected routes in /docs.
app = FastAPI(
    title="Auth API",
    version="1.0",
    description=(
        "Secure FastAPI API with **Supabase Auth** — sign up, log in, log out, "
        "and access protected routes using JWT bearer tokens.\n\n"
        "Click **Authorize** (🔒) and paste your access_token from `POST /auth/login`."
    ),
)


# ── 422 → 400 ─────────────────────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Bad request — missing or invalid fields"},
    )


# ── Pydantic model ────────────────────────────────────────────────────────────
class AuthRequest(BaseModel):
    email: str
    password: str


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Info"], summary="API info")
def root():
    """Returns basic metadata about this API."""
    return {
        "name": "Auth API",
        "version": "1.0",
        "docs": "/docs",
        "endpoints": [
            "POST /auth/signup",
            "POST /auth/login",
            "POST /auth/logout",
            "GET  /public/info",
            "GET  /protected/profile",
            "GET  /protected/dashboard",
        ],
    }


# ── Stage 1: Sign Up ──────────────────────────────────────────────────────────
@app.post(
    "/auth/signup",
    status_code=201,
    tags=["Auth"],
    summary="Register a new user account",
)
def signup(body: AuthRequest):
    """
    Creates a new Supabase user.
    - Missing email or password → **400**
    - Success → **201** with the user object
    """
    if not body.email.strip() or not body.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        response = supabase.auth.sign_up(
            {"email": body.email, "password": body.password}
        )
        if response.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        return {
            "user": {
                "id": str(response.user.id),
                "email": response.user.email,
                "created_at": str(response.user.created_at),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Stage 1: Log In ───────────────────────────────────────────────────────────
@app.post("/auth/login", tags=["Auth"], summary="Log in and receive a JWT")
def login(body: AuthRequest):
    """
    Authenticates with Supabase and returns the JWT access token.
    - Missing fields → **400**
    - Wrong credentials → **401**
    - Success → **200** with `access_token` + `refresh_token`
    """
    if not body.email.strip() or not body.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
        if response.session is None:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        err = str(e).lower()
        if "invalid" in err or "credentials" in err:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        raise HTTPException(status_code=400, detail=str(e))


# ── Stage 4: Log Out (protected) ──────────────────────────────────────────────
@app.post(
    "/auth/logout",
    status_code=204,
    tags=["Auth"],
    summary="End the current session",
    dependencies=[Depends(get_current_user)],
)
def logout():
    """
    Signs the user out via Supabase. Requires a valid Bearer token.
    - Missing / invalid token → **401**
    - Success → **204** No Content
    """
    try:
        supabase.auth.sign_out()
    except Exception:
        pass  # best-effort; token already verified by the dependency
    return None


# ── Stage 2: Public endpoint ──────────────────────────────────────────────────
@app.get("/public/info", tags=["Public"], summary="Open endpoint — no auth needed")
def public_info():
    """Anyone can call this — no token required."""
    return {"message": "Welcome stranger! This info is public."}


# ── Stage 3 + 4: Protected — profile ─────────────────────────────────────────
@app.get(
    "/protected/profile",
    tags=["Protected"],
    summary="Read your private profile",
)
def profile(current_user=Depends(get_current_user)):
    """
    Returns the verified user's id, email, and creation date.
    - Missing token → **401** "Access token required"
    - Invalid / expired token → **401** "Invalid or expired token"
    - Valid token → **200** with user metadata
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "created_at": str(current_user.created_at),
    }


# ── Stage 4: Protected — dashboard (second protected route, zero new auth code)
@app.get(
    "/protected/dashboard",
    tags=["Protected"],
    summary="Read your private dashboard",
)
def dashboard(current_user=Depends(get_current_user)):
    """
    A second protected route — the same `get_current_user` dependency guards it.
    No new auth code was written. That reuse is the whole point of middleware/deps.
    """
    return {
        "message": f"Welcome to your dashboard, {current_user.email}!",
        "user_id": str(current_user.id),
    }
