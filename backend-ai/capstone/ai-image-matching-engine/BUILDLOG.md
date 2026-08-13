# 📝 BUILDLOG.md — AI Co-Pilot & Architectural Build Log

**Capstone Project:** AI Image Understanding & Content Matching Engine  
**Track:** Backend AI Engineering Capstone  
**Author:** Nivedh  

---

## 📌 Build Journey & AI Collaboration Notes

### 1. Where AI Assisted
* **Vision Schema Construction:** AI generated Pydantic models with field constraints for structured JSON output (`VisionAnalysis`).
* **Semantic Embedding Projection:** AI helped design the 16-dimensional dense vector mapping to cluster species concepts ("fox", "wolf", "dog", "bear", "deer").
* **Pytest Acceptance Probes:** AI assisted in writing unit tests verifying low-confidence flagging and cost metering.

### 2. Where AI Was Incorrect / Required Human Refinement
* **Plural Form Vector Projection:** AI's initial keyword matching missed plural forms like `"wolves"` vs `"wolf"`, causing embedding vectors to drop similarity scores. I refactored `embedding_engine.py` to handle stemming and plural forms (`foxes`, `wolves`).
* **Candidate Pool Low-Confidence Noise:** The initial candidate ranking loop evaluated low-confidence images alongside high-confidence ones, occasionally polluting threshold checks. I added explicit candidate filtering before top-rank selection.

### 3. Key Architectural Refactorings
* **Decoupled Safety Layer (`mismatch_guard.py`):** Separated the Mismatch Guard into a pure functional pipeline enforcing similarity thresholds (`0.75`), confidence cutoffs (`0.70`), and subject/category mismatch rules.
