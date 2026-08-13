import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Vision Analysis & Structured Metadata Schema
# ---------------------------------------------------------
class VisionAnalysis(BaseModel):
    subject: str = Field(..., description="Primary subject in the image (e.g. red fox, wolf, dog)")
    category: str = Field(..., description="Broader biological or object category (e.g. animal, landscape)")
    attributes: List[str] = Field(default_factory=list, description="Visual descriptors (e.g. orange fur, forest)")
    caption: str = Field(..., description="Detailed natural language description of image content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score 0.0 to 1.0")
    is_low_confidence: bool = Field(False, description="Flagged if confidence is below threshold (< 0.70)")

class ImageRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    url: str
    metadata: VisionAnalysis
    embedding: List[float] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ---------------------------------------------------------
# Article Post Schema
# ---------------------------------------------------------
class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    topic_category: str
    target_subject: str
    embedding: List[float] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ---------------------------------------------------------
# Ranking & Mismatch Guard Schemas
# ---------------------------------------------------------
class CandidateMatch(BaseModel):
    image_id: str
    filename: str
    subject: str
    caption: str
    similarity_score: float
    confidence_score: float

class MatchDecision(BaseModel):
    post_id: str
    post_title: str
    suggested_image: Optional[CandidateMatch] = None
    status: str # "ACCEPTED", "REJECTED", "NO_CONFIDENT_MATCH"
    reason: str
    ranked_candidates: List[CandidateMatch] = Field(default_factory=list)

# ---------------------------------------------------------
# Review & Audit Schemas
# ---------------------------------------------------------
class ReviewAction(BaseModel):
    post_id: str
    image_id: str
    action: str # "APPROVED", "REJECTED"
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CostEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str # "VISION_ANALYSIS", "EMBEDDING_GENERATION"
    item_id: str
    tokens_or_calls: int
    cost_usd: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
