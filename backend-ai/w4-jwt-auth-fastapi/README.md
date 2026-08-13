# W4: Auth - Login & protect

A secure REST API built with **FastAPI** and **Supabase Auth** — sign up, log in, log out, and access protected routes using **JWT bearer tokens**.

Interactive docs with a live **Authorize 🔒 padlock**: <http://localhost:8000/docs>

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env template and fill in your Supabase values
cp .env.example .env      # Windows: copy .env.example .env

# 3. Start the server
uvicorn main:app --reload --port 8000
```

> The server logs **"Connected to Supabase"** and serves the API at `http://localhost:8000`.

---

## Environment variables

| Variable | Example | Description |
|---|---|---|
| `SUPABASE_URL` | `https://xxxx.supabase.co` | Your Supabase project URL |
| `SUPABASE_KEY` | `eyJhbGci...` | Your Supabase **anon** (public) key |

> **Never commit `.env`** — it's git-ignored. `.env.example` is the safe committed placeholder.  
> Never use the `service_role` key here — it bypasses all security.

---

## API reference

| Method | Route | Auth required | Status codes | Description |
|---|---|---|---|---|
| `GET` | `/` | ❌ | 200 | API info |
| `POST` | `/auth/signup` | ❌ | 201, 400 | Register a new user |
| `POST` | `/auth/login` | ❌ | 200, 400, 401 | Log in — returns JWT |
| `POST` | `/auth/logout` | ✅ Bearer | 204, 401 | End the session |
| `GET` | `/public/info` | ❌ | 200 | Open public endpoint |
| `GET` | `/protected/profile` | ✅ Bearer | 200, 401 | View your profile |
| `GET` | `/protected/dashboard` | ✅ Bearer | 200, 401 | View your dashboard |

### Status code reference

| Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created (signup success) |
| 204 | No Content (logout success) |
| 400 | Bad Request — missing or invalid fields |
| 401 | Unauthorized — missing, malformed, or expired token |

---

## The trust triangle

```
Client ──POST /auth/login──▶ Your Server ──sign_in_with_password()──▶ Supabase
                                                                         │
                                                             access_token ◀─┘
Client ◀── {access_token} ──────────────────────────────────────────────┘

Client ──GET /protected/profile──▶ Your Server ──get_user(token)──▶ Supabase
   Authorization: Bearer <token>       │                               │
                                       └── 200 user data ◀── verified ─┘
```

---

## Example curl flow

```bash
# 1. Sign up
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# HTTP/1.1 201 Created

# 2. Log in — copy the access_token from the response
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# HTTP/1.1 200 OK
# {"access_token":"eyJ...","refresh_token":"...","token_type":"bearer"}

# 3. Call protected route with valid token
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer eyJ..."
# HTTP/1.1 200 OK
# {"id":"...","email":"test@example.com","created_at":"..."}

# 4. Call protected route WITHOUT token → 401
curl -i http://localhost:8000/protected/profile
# HTTP/1.1 401 Unauthorized
# {"detail":"Access token required"}

# 5. Tamper the token → 401
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer eyJ...TAMPERED"
# HTTP/1.1 401 Unauthorized
# {"detail":"Invalid or expired token"}

# 6. Public route — no token needed
curl -i http://localhost:8000/public/info
# HTTP/1.1 200 OK
# {"message":"Welcome stranger! This info is public."}

# 7. Log out
curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer eyJ..."
# HTTP/1.1 204 No Content
```

---

## Swagger UI — Authorize flow

1. Open <http://localhost:8000/docs>
2. Call `POST /auth/login` → copy the `access_token`
3. Click the **Authorize 🔒** button (top right)
4. Paste the token and click **Authorize**
5. Try `GET /protected/profile` → **200** ✅

Protected routes show a **lock icon** (🔒) in the docs automatically.

---

## Project structure

```
.
├── main.py          # All FastAPI routes
├── auth.py          # Supabase client + get_current_user dependency
├── requirements.txt
├── .env.example     # Committed key-name placeholder
├── .env             # Real secrets — git-ignored ⚠️
└── .gitignore
```

### Why a separate `auth.py`?

The `get_current_user` dependency is defined once in `auth.py` and reused across every protected route via `Depends(get_current_user)`. Adding a new protected route requires zero new auth code — just add the dependency. This is the **middleware pattern**: one guard, standing at every locked door.

---

## How authentication works here

1. **You never store passwords** — Supabase hashes and stores them.
2. **You never write cryptography** — Supabase signs the JWT; you only verify it.
3. **Token verification** calls `supabase.auth.get_user(token)` — a real network call to Supabase, making the verification trustworthy.
4. **The anon key is safe** — it's the public key. The `service_role` key is never used here.
