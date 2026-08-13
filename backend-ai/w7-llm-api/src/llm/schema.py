from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Category(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non-fiction"
    CHILDREN = "children"
    ACADEMIC = "academic"
    UNKNOWN = "unknown"

class EnrichRequest(BaseModel):
    title: str = Field(..., max_length=500, description="The title of the book")
    description: Optional[str] = Field(None, max_length=5000, description="The description of the book")
    price_gbp: float = Field(..., description="The price in GBP")

class EnrichResponse(BaseModel):
    category: Category = Field(..., description="The category of the book")
    summary: str = Field(..., description="A one-sentence summary of the book")
    quality_flags: List[str] = Field(..., description="A list of data quality issues, or empty if none")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

def get_stub_response() -> EnrichResponse:
    """Returns a valid stub response for testing when LLM_STUB=1"""
    return EnrichResponse(
        category=Category.FICTION,
        summary="A fascinating story about stubbed data.",
        quality_flags=["stub_mode_active"],
        confidence=0.95
    )
