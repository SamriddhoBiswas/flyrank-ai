import os
import time
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv

from openai import OpenAI
from pydantic import ValidationError
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

import openai

from src.llm.schema import EnrichRequest, EnrichResponse, get_stub_response

load_dotenv()

app = FastAPI(title="W7 LLM Enrichment API")

# Ensure logs dir exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
QUARANTINE_LOG = LOGS_DIR / "quarantine.jsonl"

# Configuration
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "dummy")
LLM_MODEL = os.environ.get("LLM_MODEL", "openrouter/free")
LLM_STUB = os.environ.get("LLM_STUB", "0") == "1"
LLM_ENABLED = os.environ.get("LLM_ENABLED", "true").lower() == "true"
PROMPT_VERSION = "v1"

# Explicit timeout setting (Stage 4)
# Instead of default 10 minutes, we set 30.0 seconds
client = OpenAI(
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    timeout=30.0,
    max_retries=0  # We handle retries ourselves with Tenacity
)

def load_prompt() -> str:
    prompt_path = Path(f"prompts/enrich-{PROMPT_VERSION}.md")
    return prompt_path.read_text(encoding="utf-8")

# Retry only on timeouts, rate limits (429), and server errors (5xx)
# Do not retry on 400, 401, 403, 422
def is_retriable_error(exception: Exception) -> bool:
    if isinstance(exception, openai.APITimeoutError):
        return True
    if isinstance(exception, openai.RateLimitError):
        return True
    if isinstance(exception, openai.InternalServerError):
        return True
    return False

@retry(
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(Exception),
    reraise=True
)
def call_model_with_retry(messages):
    """Call model with exponential backoff and jitter."""
    try:
        return client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.1
        )
    except Exception as e:
        if is_retriable_error(e):
            print(f"Retrying on error: {e}")
            raise e
        else:
            # Fatal error, do not retry
            raise

def extract_json_from_text(text: str) -> str:
    """Strip markdown code fences if present."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

@app.post("/enrich", response_model=EnrichResponse)
def enrich_record(record: EnrichRequest):
    # Kill switch (Stage 4)
    if not LLM_ENABLED:
        raise HTTPException(status_code=503, detail="LLM feature is currently disabled via kill switch.")

    # Stub mode (Stage 1)
    if LLM_STUB:
        return get_stub_response()

    start_time = time.time()
    system_prompt = load_prompt()
    user_content = record.model_dump_json()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    repair_count = 0
    raw_output = ""
    tokens_in = 0
    tokens_out = 0

    try:
        # First attempt
        res = call_model_with_retry(messages)
        raw_output = res.choices[0].message.content
        tokens_in += res.usage.prompt_tokens if res.usage else 0
        tokens_out += res.usage.completion_tokens if res.usage else 0
        
        json_str = extract_json_from_text(raw_output)
        
        try:
            parsed_data = json.loads(json_str)
            result = EnrichResponse.model_validate(parsed_data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Repair retry (Stage 3)
            repair_count += 1
            repair_message = (
                f"Your previous answer was rejected for this reason: {str(e)}\n"
                f"Raw output: {raw_output}\n"
                f"Return only corrected JSON matching the schema."
            )
            messages.append({"role": "assistant", "content": raw_output})
            messages.append({"role": "user", "content": repair_message})
            
            res2 = call_model_with_retry(messages)
            raw_output2 = res2.choices[0].message.content
            tokens_in += res2.usage.prompt_tokens if res2.usage else 0
            tokens_out += res2.usage.completion_tokens if res2.usage else 0
            
            json_str2 = extract_json_from_text(raw_output2)
            parsed_data2 = json.loads(json_str2)
            result = EnrichResponse.model_validate(parsed_data2)
            
    except Exception as e:
        # Give up cleanly on second failure or API failure (Stage 3)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log cost even on failure
        cost_log = {
            "timestamp": time.time(),
            "model": LLM_MODEL,
            "prompt_version": PROMPT_VERSION,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "duration_ms": duration_ms,
            "repair_count": repair_count,
            "status": "failed"
        }
        print(f"COST LOG: {json.dumps(cost_log)}")
        
        # Quarantine log
        quarantine_record = {
            "input": record.model_dump(),
            "prompt_version": PROMPT_VERSION,
            "error": str(e),
            "raw_output_attempt_1": raw_output
        }
        with open(QUARANTINE_LOG, "a") as f:
            f.write(json.dumps(quarantine_record) + "\n")
            
        if isinstance(e, openai.APITimeoutError):
            raise HTTPException(status_code=504, detail="Upstream LLM timed out.")
        
        raise HTTPException(status_code=422, detail="Failed to generate valid output matching schema.")

    # Success
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Cost Logging (Stage 4)
    cost_log = {
        "timestamp": time.time(),
        "model": LLM_MODEL,
        "prompt_version": PROMPT_VERSION,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "duration_ms": duration_ms,
        "repair_count": repair_count,
        "status": "success"
    }
    print(f"COST LOG: {json.dumps(cost_log)}")

    return result

# Handle FastAPI validation errors (Stage 1)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )
