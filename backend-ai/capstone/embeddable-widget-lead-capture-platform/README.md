# 🚀 FlyRank Backend Capstone — Embeddable Widget & Lead-Capture Platform

> A production-grade backend platform enabling customers to create embeddable lead capture widgets (`<script src="http://localhost:8000/widget.js?id=..."></script>`) installed on any external website. Incoming public browser submissions are boundary-validated, rate-limited, spam-filtered via honeypots, enriched via a 2-provider geo fallback chain, and persisted to a multi-tenant dashboard.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Framework](https://img.shields.io/badge/framework-FastAPI%20%7C%20Pydantic-orange.svg)](https://fastapi.tiangolo.com/)

---

## 🏗️ Architecture Diagram & System Flow

```text
Widget Owner (authenticated via X-API-Key)
    └─► POST /api/v1/admin/widgets ──► Widget DB (Tenant Isolated) ──► Embed Snippet

Customer Website (Second Origin: http://localhost:5500)
    └─► <script src="http://localhost:8000/widget.js?id=abc123">
            └─► GET /api/v1/widgets/:id/config (Public · Cached · CORS)
                    └─► Render Dynamic Widget Modal

Website Visitor (Public Internet)
    └─► POST /api/v1/submissions (Public · CORS · OPTIONS Preflight)
           ├─► 1. Boundary Validation ── Invalid/Oversized (>100KB)? ──► 400 / 413 Error
           ├─► 2. Abuse Protection ── Burst (>5 req/10s)? ──► 429 Too Many Requests
           ├─► 3. Honeypot Spam Check ── Bot field filled? ──► Drop silently (HTTP 200)
           ├─► 4. Geo Enrichment Fallback Chain: Provider A ─(fails)─► Provider B ─(fails)─► Store anyway
           ├─► 5. Store Enriched Submission Row
           └─► 6. Safe Side Effect (Email Notification) ── SMTP Fails? ──► Log warning & keep submission

Owner Dashboard API (authenticated)
    └─► GET /api/v1/dashboard/stats & /submissions ◄── Aggregated Analytics & Geo Breakdown
```

---

## 🛠️ Required Submission Pack Files (§ 11)

| Required File | Purpose & Contents |
| :--- | :--- |
| **`README.md`** | Architecture diagram, reproducible setup/run/test steps, API docs, and limitations note. |
| **`capstone.yaml`** | Evaluator manifest specifying `run:`, `seed:`, `test:`, `base_url:`, and probe endpoints. |
| **`EVIDENCE.md`** | Verification transcripts and Pytest probe evidence for every Definition-of-Done checkbox. |
| **`BUILDLOG.md`** | AI usage log detailing where AI assisted, where it was wrong, and what was refactored. |
| **`.env.example`** | Safe environment variable template with non-sensitive defaults. |

---

## 💻 Reproducible Setup & Run Instructions

Follow these exact steps to run and test the platform on any clean computer:

### Step 1: Clone & Navigate to Repository
```bash
git clone https://github.com/NivedhN160/Flyrank-Backend-AI-Engineering-Capstone.git
cd Flyrank-Backend-AI-Engineering-Capstone
```

### Step 2: Create & Activate Virtual Environment
```bash
# On Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Seed Demo Data
```bash
python seed_demo_data.py
```

### Step 5: Start the API Server
```bash
python main.py
```
*API Server boots on `http://localhost:8000`. Access Swagger UI docs at `http://localhost:8000/docs`.*

### Step 6: Test Customer Embed Page (Second Origin)
Open `customer_site/index.html` in your browser (or serve on `http://localhost:5500`). Watch the embeddable widget appear in the bottom-right corner and submit a live test lead!

---

## 🧪 Automated Acceptance Probe Test Suite

Run the automated acceptance suite verifying all 6 evaluator probes (§ 12):
```bash
pytest test_suite.py -v
```

*Verification Results:*
```text
test_suite.py::test_probe_1_valid_submission PASSED                     [ 16%]
test_suite.py::test_probe_2_malformed_and_oversized_payload PASSED      [ 33%]
test_suite.py::test_probe_3_rate_limiting_burst PASSED                  [ 50%]
test_suite.py::test_probe_4_geo_fallback_chain PASSED                   [ 66%]
test_suite.py::test_probe_5_email_side_effect_failure_tolerance PASSED  [ 83%]
test_suite.py::test_probe_6_honeypot_spam_filter PASSED                 [100%]

======================= 6 passed in 3.53s =======================
```

---

## ⚠️ Honest Limitations Note

1. **In-Memory Rate Limiter:** Current rate limiting uses an in-memory sliding window map. For multi-node cluster deployments, this should be backed by Redis.
2. **Synchronous Geo Enrichment:** Geo lookup is currently performed during request processing. Under massive traffic scale, geo enrichment should be offloaded to an asynchronous background Celery / Redis Queue worker.

---

## 📄 License

Built by **Samriddho** for the **FlyRank AI Internship — Backend AI Engineering Track Capstone**.  
Licensed under the [MIT License](LICENSE).
