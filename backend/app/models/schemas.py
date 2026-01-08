"""Pydantic models for API requests and responses"""

# Import all models for backward compatibility
from app.models.base import BaseRequest, BaseResponse, SourcedResponse
from app.models.requests import QueryRequest, AgreementRequest
from app.models.responses import (
    HealthResponse,
    ReloadResponse,
    QueryResponse,
    AgreementResponse,
    LegalSourcesResponse
)

__all__ = [
    # Base models
    "BaseRequest",
    "BaseResponse", 
    "SourcedResponse",
    # Request models
    "QueryRequest",
    "AgreementRequest",
    # Response models
    "HealthResponse",
    "ReloadResponse",
    "QueryResponse",
    "AgreementResponse",
    "LegalSourcesResponse",
]

