"""Pydantic models for API requests and responses"""

from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """Request model for legal queries"""
    question: str = Field(..., description="The legal question to ask")
    chat_history: Optional[List[dict]] = Field(
        default=None,
        description="Previous chat history for context"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the penalties for hacking under the IT Act?",
                "chat_history": []
            }
        }


class QueryResponse(BaseModel):
    """Response model for legal queries"""
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="The generated answer")
    sources: List[str] = Field(..., description="Source documents used")
    success: bool = Field(default=True, description="Success status")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Application status")
    vector_store_loaded: bool = Field(..., description="Vector store status")


class ReloadResponse(BaseModel):
    """Document reload response"""
    message: str
    success: bool


class LegalSourcesResponse(BaseModel):
    """Legal sources list response"""
    sources: List[dict]
    success: bool
