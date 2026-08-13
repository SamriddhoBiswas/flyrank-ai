import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, EmailStr

# ---------------------------------------------------------
# Tenant & Auth Schemas
# ---------------------------------------------------------
class Tenant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    api_key: str = Field(default_factory=lambda: f"key_{uuid.uuid4().hex[:12]}")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ---------------------------------------------------------
# Widget Configuration Schemas
# ---------------------------------------------------------
class WidgetCreate(BaseModel):
    title: str = Field(..., example="Get a Free Strategy Call")
    description: str = Field(..., example="Fill out the form below to speak with an AI engineer.")
    widget_type: str = Field("lead_modal", example="lead_modal") # lead_modal, signup_form, popover
    button_text: str = Field("Submit Request", example="Submit Request")
    accent_color: str = Field("#2563EB", example="#2563EB")
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

class Widget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    title: str
    description: str
    widget_type: str
    button_text: str
    accent_color: str
    allowed_origins: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# ---------------------------------------------------------
# Public Submission Schemas
# ---------------------------------------------------------
class SubmissionCreate(BaseModel):
    widget_id: str
    name: str = Field(..., min_length=2)
    email: EmailStr
    message: str = Field(..., min_length=5)
    bot_field: Optional[str] = Field(None) # Honeypot field (must be empty)

class GeoEnrichment(BaseModel):
    ip: str
    country: Optional[str] = "Unknown"
    city: Optional[str] = "Unknown"
    provider_used: Optional[str] = "None"

class Submission(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    widget_id: str
    tenant_id: str
    name: str
    email: str
    message: str
    geo: GeoEnrichment
    created_at: datetime = Field(default_factory=datetime.utcnow)
