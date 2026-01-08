"""Base models for shared fields and common patterns"""

from pydantic import BaseModel, Field
from typing import List, Optional


class BaseRequest(BaseModel):
    """Base request model with common fields"""
    chat_history: Optional[List[dict]] = Field(
        default=None,
        description="Previous chat history for context"
    )


class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(default=True, description="Success status")


class SourcedResponse(BaseResponse):
    """Response model that includes source documents"""
    sources: List[str] = Field(..., description="Source documents used")
