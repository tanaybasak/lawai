"""API routes"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    ReloadResponse,
    LegalSourcesResponse,
    AgreementRequest,
    AgreementResponse
)
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint"""
    assistant_service = request.app.state.assistant_service
    
    return HealthResponse(
        status="healthy",
        vector_store_loaded=assistant_service.is_ready()
    )


@router.post("/query", response_model=QueryResponse)
async def query_legal_assistant(query_request: QueryRequest, request: Request):
    """Query the legal assistant"""
    try:
        assistant_service = request.app.state.assistant_service
        
        if not assistant_service.is_ready():
            raise HTTPException(
                status_code=500,
                detail="Legal assistant not initialized"
            )
        
        logger.info(f"Processing query: {query_request.question}")
        
        result = await assistant_service.query(
            question=query_request.question,
            chat_history=query_request.chat_history
        )
        
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/query-stream")
async def query_legal_assistant_stream(query_request: QueryRequest, request: Request):
    """Query the legal assistant with streaming response"""
    try:
        assistant_service = request.app.state.assistant_service
        
        if not assistant_service.is_ready():
            raise HTTPException(
                status_code=500,
                detail="Legal assistant not initialized"
            )
        
        logger.info(f"Processing streaming query: {query_request.question}")
        
        async def generate():
            """Generate streaming response"""
            try:
                # Stream the response
                async for chunk in assistant_service.query_stream(
                    question=query_request.question,
                    chat_history=query_request.chat_history
                ):
                    # Send each chunk as JSON
                    yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send completion signal
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}")
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing streaming query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.post("/reload-documents", response_model=ReloadResponse)
async def reload_documents(request: Request):
    """Reload legal documents and rebuild vector store"""
    try:
        logger.info("Reloading documents...")
        
        assistant_service = request.app.state.assistant_service
        await assistant_service.initialize(force_reload=True)
        
        return ReloadResponse(
            message="Documents reloaded successfully",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error reloading documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reloading documents: {str(e)}"
        )


@router.get("/legal-sources", response_model=LegalSourcesResponse)
async def get_legal_sources():
    """Get list of configured legal sources"""
    return LegalSourcesResponse(
        sources=settings.LEGAL_SOURCES,
        success=True
    )


@router.post("/generate-agreement", response_model=AgreementResponse)
async def generate_agreement(agreement_request: AgreementRequest, request: Request):
    """Generate a legal agreement (NDA, MSA, etc.)"""
    try:
        assistant_service = request.app.state.assistant_service
        
        if not assistant_service.is_ready():
            raise HTTPException(
                status_code=500,
                detail="Assistant service not initialized"
            )
        
        logger.info(f"Generating {agreement_request.agreement_type} agreement (mutual: {agreement_request.is_mutual})")
        
        result = await assistant_service.generate_agreement(
            agreement_type=agreement_request.agreement_type,
            requirements=agreement_request.requirements,
            is_mutual=agreement_request.is_mutual
        )
        
        return AgreementResponse(
            agreement_type=result["agreement_type"],
            document=result["document"],
            clauses_used=result["clauses_used"],
            sources=result.get("sources", result["clauses_used"]),  # Use sources or fallback to clauses_used
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error generating agreement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating agreement: {str(e)}"
        )

