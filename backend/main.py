"""
FastAPI server for LawAI Legal Assistant

⚠️  LEGACY VERSION - Consider using the modular version instead!
    New entry point: main_modular.py
    See README_MODULAR.md for details
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from legal_graph import LegalAssistantGraph
from vector_store import initialize_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Migration notice
print("\n" + "=" * 80)
print("⚠️  You're using the LEGACY main.py")
print("Consider migrating to the modular version: main_modular.py")
print("See README_MODULAR.md for the new architecture details")
print("=" * 80 + "\n")

app = FastAPI(
    title="LawAI Legal Assistant API",
    description="RAG-based legal assistant for Indian laws",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
vector_store_manager = None
legal_assistant = None


class QueryRequest(BaseModel):
    """Request model for legal queries"""
    question: str
    chat_history: Optional[List[dict]] = None


class QueryResponse(BaseModel):
    """Response model for legal queries"""
    question: str
    answer: str
    sources: List[str]
    success: bool = True


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_store_loaded: bool


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global vector_store_manager, legal_assistant
    
    try:
        logger.info("Initializing LawAI Legal Assistant...")
        
        # Initialize vector store
        vector_store_manager = initialize_vector_store(force_reload=False)
        
        # Initialize legal assistant graph
        legal_assistant = LegalAssistantGraph(vector_store_manager)
        
        logger.info("LawAI Legal Assistant initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        raise


@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        vector_store_loaded=vector_store_manager is not None
    )


@app.post("/query", response_model=QueryResponse)
async def query_legal_assistant(request: QueryRequest):
    """Query the legal assistant"""
    try:
        if legal_assistant is None:
            raise HTTPException(
                status_code=500,
                detail="Legal assistant not initialized"
            )
        
        logger.info(f"Processing query: {request.question}")
        
        result = legal_assistant.query(
            question=request.question,
            chat_history=request.chat_history
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


@app.post("/reload-documents")
async def reload_documents():
    """Reload legal documents and rebuild vector store"""
    global vector_store_manager, legal_assistant
    
    try:
        logger.info("Reloading documents...")
        
        vector_store_manager = initialize_vector_store(force_reload=True)
        legal_assistant = LegalAssistantGraph(vector_store_manager)
        
        return {"message": "Documents reloaded successfully", "success": True}
        
    except Exception as e:
        logger.error(f"Error reloading documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reloading documents: {str(e)}"
        )


@app.get("/legal-sources")
async def get_legal_sources():
    """Get list of configured legal sources"""
    from config import LEGAL_SOURCES
    return {"sources": LEGAL_SOURCES, "success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
