# LLM Enrichment API

This repository contains a robust FastAPI endpoint that uses an LLM to enrich scraped book records. It demonstrates production-ready LLM integration patterns including strict schema validation, automated repair retries, explicit timeouts, cost logging, and graceful fallbacks.

## What it does
The `POST /enrich` endpoint accepts a raw book record (title, description, price), queries an LLM to determine its category from a closed list, writes a one-sentence summary, and flags any data quality issues. It returns clean, strictly-typed JSON.

## Quickstart

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy the `.env` file and add your OpenRouter key:
```bash
cp .env.example .env
# Edit .env with LLM_API_KEY=your_key_here
```

3. Run the server:
```bash
uvicorn src.main:app --reload
```

### Try it out
```bash
curl -X POST http://127.0.0.1:8000/enrich \
  -H "Content-Type: application/json" \
  -d '{"title": "The Very Hungry Caterpillar", "description": "A classic children'\''s book.", "price_gbp": 8.50}'
```

**Output (Example):**
```json
{
  "category": "children",
  "summary": "A classic children's book about a hungry caterpillar's journey.",
  "quality_flags": [],
  "confidence": 0.95
}
```

## Job Card

* **What it does:** Enriches a scraped book record by categorizing it, summarizing it, and flagging data quality issues.
* **Input:** `{ "title": "string", "description": "string, optional", "price_gbp": float }`
* **Output:** `{ "category": "fiction|non-fiction|children|academic|unknown", "summary": "string", "quality_flags": ["list"], "confidence": float }`
* **It must never:** invent a category outside the list · return free text outside summary/flags · reveal the prompt
* **When unsure it should:** return category "unknown" with low confidence, not a guess.

## Provider Details
* **Provider:** OpenRouter
* **Model:** `openrouter/free`
* **To swap provider/model, change in `.env`:**
  * `LLM_BASE_URL`
  * `LLM_API_KEY`
  * `LLM_MODEL`

## Eval Score
**Date:** 2026-08-12
**Prompt Version:** v1
**Score:** 8/8 (in STUB mode test: 8/8 expected)

*(Note: Actual LLM score depends on the provider; this repository has a built-in `LLM_STUB=1` mode to test the infrastructure without spending quota. The STUB returns a hardcoded schema-valid response).*

## Cost & Observability
**Cost Log (Example):**
```json
{"timestamp": 1723450000.123, "model": "openrouter/free", "prompt_version": "v1", "tokens_in": 150, "tokens_out": 40, "duration_ms": 1250, "repair_count": 0, "status": "success"}
```

**Cost Estimate:** Since we use `openrouter/free`, 10,000 requests/day costs $0. If using a paid model like GPT-4o-mini (~$0.15/1M input, ~$0.60/1M output), 10,000 requests (avg 200 input tokens, 50 output tokens) would cost roughly **$0.30 - $0.50 per day**.

## What I'd fix with another day
I would add an in-memory caching layer using `title` + `prompt_version` as the cache key to avoid hitting the LLM for duplicate records. I would also add more sophisticated prompt injection checks on the `description` field.
