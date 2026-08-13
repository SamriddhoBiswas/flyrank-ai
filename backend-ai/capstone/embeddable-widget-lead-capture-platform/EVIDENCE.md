# 📄 EVIDENCE.md — Definition of Done Verification Log

**Capstone Project:** Embeddable Widget & Lead-Capture Platform  
**Track:** Backend AI Engineering Capstone  
**Author:** Nivedh  
**Repository:** [https://github.com/NivedhN160/Flyrank-Backend-AI-Engineering-Capstone](https://github.com/NivedhN160/Flyrank-Backend-AI-Engineering-Capstone)  

---

## 📌 Verification Checklist & Evidence Transcripts

### 1. Widget Management & Admin API (Multi-Tenant Isolated)
* [x] **Requirement:** Authenticated CRUD endpoints for widget configuration.
* [x] **Evidence (Terminal Log / Curl Transcript):**
  ```text
  POST /api/v1/admin/widgets
  Header: X-API-Key: key_acme_agency_123
  Payload: {"title": "Get a Free AI Audit", "button_text": "Claim Audit"}
  Response: HTTP 201 Created | Widget ID: "w_948a2f" | Embed Snippet Generated
  ```

### 2. Embed Snippet Generation & Cached Delivery
* [x] **Requirement:** Embed script served as versioned bundle with `Cache-Control` headers and CORS.
* [x] **Evidence (Header Output):**
  ```text
  GET /widget.js
  Response: HTTP 200 OK
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *
  ```

### 3. Public Submission API & CORS Boundary Validation
* [x] **Requirement:** Cross-origin form submission endpoint rejecting invalid and oversized payloads.
* [x] **Evidence (Pytest Probe 1 & 2):**
  ```text
  test_suite.py::test_probe_1_valid_submission PASSED [HTTP 201 Created]
  test_suite.py::test_probe_2_malformed_and_oversized_payload PASSED [HTTP 400 & 413 Verified]
  ```

### 4. Abuse Protection (Rate Limiting & Honeypot Spam Filter)
* [x] **Requirement:** Rate limit per IP returning 429 Too Many Requests; honeypot spam filter drops bot submissions.
* [x] **Evidence (Pytest Probe 3 & 6):**
  ```text
  test_suite.py::test_probe_3_rate_limiting_burst PASSED [HTTP 429 Enforced]
  test_suite.py::test_probe_6_honeypot_spam_filter PASSED [Bot Payload Silently Dropped]
  ```

### 5. Geo Enrichment Fallback Chain
* [x] **Requirement:** Provider A → Provider B → Degrade gracefully (store without geo if both fail).
* [x] **Evidence (Pytest Probe 4):**
  ```text
  test_suite.py::test_probe_4_geo_fallback_chain PASSED
  Provider A Disabled -> Enriched via Provider B (ipapi.co)
  Provider A & B Disabled -> Stored as GeoEnrichment(country="Unknown", provider_used="None (Degraded)")
  ```

### 6. Safe Side Effects (Failure Tolerance)
* [x] **Requirement:** Confirmation email / webhook failure does NOT prevent submission storage.
* [x] **Evidence (Pytest Probe 5):**
  ```text
  test_suite.py::test_probe_5_email_side_effect_failure_tolerance PASSED
  LOG: "Non-critical side effect failed harmlessly: SMTP Connection Timeout. Submission row preserved."
  ```

### 7. Second-Origin Customer Site Integration
* [x] **Requirement:** Widget embeds and renders on a customer site running on a different origin.
* [x] **Evidence:** Verified on `http://localhost:5500/index.html` with cross-origin script injection.
