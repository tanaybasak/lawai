"""Response models for API endpoints"""

from pydantic import Field
from typing import List
from app.models.base import BaseResponse, SourcedResponse


class HealthResponse(BaseResponse):
    """Health check response"""
    status: str = Field(..., description="Application status")
    vector_store_loaded: bool = Field(..., description="Vector store status")


class ReloadResponse(BaseResponse):
    """Document reload response"""
    message: str = Field(..., description="Status message")


class QueryResponse(SourcedResponse):
    """Response model for legal queries"""
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="The generated answer")


class AgreementResponse(BaseResponse):
    """Response model for agreement generation"""
    agreement_type: str = Field(..., description="Type of agreement generated")
    document: str = Field(..., description="The generated agreement document")
    clauses_used: List[str] = Field(..., description="List of clauses included")
    sources: List[str] = Field(..., description="Source clauses used (same as clauses_used)")


class LegalSourcesResponse(BaseResponse):
    """Legal sources list response"""
    sources: List[dict] = Field(..., description="List of legal sources")
