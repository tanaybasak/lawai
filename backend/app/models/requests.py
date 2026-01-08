"""Request models for API endpoints"""

from pydantic import Field
from typing import Optional
from app.models.base import BaseRequest


class QueryRequest(BaseRequest):
    """Request model for legal queries"""
    question: str = Field(..., description="The legal question to ask")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the penalties for hacking under the IT Act?",
                "chat_history": []
            }
        }


class AgreementRequest(BaseRequest):
    """Request model for agreement generation"""
    agreement_type: str = Field(..., description="Type of agreement (nda, msa, employment, etc.)")
    requirements: str = Field(default="", description="Specific requirements or customizations")
    is_mutual: bool = Field(default=True, description="For NDAs: mutual or unilateral")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agreement_type": "nda",
                "requirements": "Include 5-year confidentiality period and specific data protection clauses",
                "is_mutual": True,
                "chat_history": []
            }
        }
