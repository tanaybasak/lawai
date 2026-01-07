"""
LawAI Legal Assistant - Main Entry Point

A modular RAG-based legal assistant for Indian laws using LangChain and LangGraph.
"""

import uvicorn
from app import create_application
from app.core.config import settings

# Create application instance
app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "main_modular:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
