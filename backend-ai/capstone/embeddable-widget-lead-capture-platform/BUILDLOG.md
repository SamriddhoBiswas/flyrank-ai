# 📝 BUILDLOG.md — AI Co-Pilot & Architectural Build Log

**Capstone Project:** Embeddable Widget & Lead-Capture Platform  
**Track:** Backend AI Engineering Capstone  
**Author:** Nivedh  

---

## 📌 Build Journey & AI Collaboration Notes

### 1. Where AI Assisted
* **Scaffolding Fast & Clean CORS Middlewares:** AI generated the initial FastAPI boilerplate and `CORSMiddleware` configuration.
* **Geo Provider Fallback Logic:** AI suggested using `httpx.AsyncClient` with custom timeouts to prevent upstream API latency from blocking incoming HTTP requests.
* **Pytest Acceptance Probe Suite:** AI helped draft the 6 acceptance probe test fixtures matching FlyRank evaluator specifications.

### 2. Where AI Was Incorrect / Required Human Refinement
* **Honeypot Bot Status Code Misalignment:** The AI initially returned `HTTP 201 Created` for honeypot bot submissions. I manually refactored the route handler to return `HTTP 200 OK` with JSON content to ensure bots perceive a successful post while dropping the database insertion.
* **Rate Limiter In-Memory Map Cleanup:** The AI's initial rate limiting script kept appending IP timestamps endlessly without purging old timestamps. I refactored it to filter `now - timestamp < 10` to avoid memory bloat.

### 3. Key Refactoring Decisions
* **Decoupled Repository Pattern:** Separated data access logic from HTTP routes into `repository.py`, allowing easy swapping between SQLite and PostgreSQL in Docker.
* **Non-Blocking Safe Side Effects:** Wrapped email notifications in a try/except block so SMTP server failures never roll back valid lead submissions.
