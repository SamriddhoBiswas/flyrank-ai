# 📄 EVIDENCE.md — Definition of Done Verification Log

**Capstone Project:** AI Image Understanding & Content Matching Engine  
**Track:** Backend AI Engineering Capstone  
**Author:** Nivedh  
**Repository:** [https://github.com/NivedhN160/AI-Image-Understanding-Content-Matching-Engine-Flyrank-Capstone](https://github.com/NivedhN160/AI-Image-Understanding-Content-Matching-Engine-Flyrank-Capstone)  

---

## 📌 Verification Checklist & Evidence Transcripts

### 1. Vision Understanding Pipeline & Low-Confidence Flagging
* [x] **Requirement:** Vision model generates structured JSON tags validated against schema; low-confidence classifications are flagged instead of guessed.
* [x] **Evidence (Pytest Probe 1):**
  ```text
  test_suite.py::test_probe_1_batch_processing_and_low_confidence_flag PASSED
  50 images processed, structured JSON generated.
  Low-confidence image 'blurry_shape_low_conf_01.jpg' flagged with confidence 0.55 (< 0.70 threshold).
  ```

### 2. Semantic Embedding Matching & Concept Equivalence
* [x] **Requirement:** Embedding similarity search maps equivalent concepts ("red fox", "Vulpes vulpes", "wild fox species").
* [x] **Evidence (Pytest Probe 2):**
  ```text
  test_suite.py::test_probe_2_red_fox_query_ranking PASSED
  GET /api/v1/posts/post-fox-101/images
  Status: ACCEPTED | Suggested Image: 'red_fox_01.jpg' (Similarity: 0.94, Vision Confidence: 0.94)
  Wolf & Dog candidates ranked below similarity cutoff.
  ```

### 3. The Mismatch Guard (Wolf vs Fox Refusal Scenario)
* [x] **Requirement:** Mismatch Guard rejects incorrect recommendations with human-readable explanations.
* [x] **Evidence (Pytest Probe 3):**
  ```text
  test_suite.py::test_probe_3_forced_wolf_rejection_guard PASSED
  GET /api/v1/posts/post-fox-101/images?force_candidate_id=wolf_img_01
  Status: REJECTED
  Reason: "Animal category mismatch: expected fox, detected gray wolf."
  ```

### 4. "No Confident Match" Fallback Handling
* [x] **Requirement:** When no image clears the similarity threshold, the system answers "no confident match" + detailed reasoning.
* [x] **Evidence (Pytest Probe 4):**
  ```text
  test_suite.py::test_probe_4_no_confident_match_fallback PASSED
  GET /api/v1/posts/post-sub-103/images (Deep Sea Submarine Post vs Animal Images)
  Status: NO_CONFIDENT_MATCH
  Reason: "No confident match found. Top similarity score (0.24) is below threshold (0.75); detected subjects do not match article topic."
  ```

### 5. Evaluation Dataset & Top-1 Precision Metrics
* [x] **Requirement:** Labeled evaluation dataset measures top-1 precision metric.
* [x] **Evidence (Pytest Probe 5):**
  ```text
  test_suite.py::test_probe_5_eval_top1_precision PASSED
  GET /api/v1/eval/metrics
  Response: {"top_1_precision_pct": 100.0, "total_eval_samples": 2, "correct_matches": 2}
  ```

### 6. Attributed AI Cost Tracking
* [x] **Requirement:** Every vision and embedding call attributed with cost entry.
* [x] **Evidence (Pytest Probe 6):**
  ```text
  test_suite.py::test_probe_6_attributed_cost_tracking PASSED
  GET /api/v1/costs
  Response: {"total_cost_usd": 0.00856, "total_api_calls": 103}
  ```
