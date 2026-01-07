"""Main assistant service orchestrating all components"""

from app.services.vector_store import VectorStoreService
from app.services.legal_graph import LegalGraphService
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class AssistantService:
    """Main service for legal assistant functionality"""
    
    def __init__(self):
        self.vector_store_service: VectorStoreService = None
        self.legal_graph_service: LegalGraphService = None
        self._initialized = False
    
    async def initialize(self, force_reload: bool = False) -> None:
        """Initialize all services"""
        if self._initialized and not force_reload:
            logger.info("Assistant service already initialized")
            return
        
        logger.info("Initializing assistant service...")
        
        # Initialize vector store
        self.vector_store_service = VectorStoreService()
        await self.vector_store_service.initialize(force_reload=force_reload)
        
        # Initialize legal graph
        self.legal_graph_service = LegalGraphService(self.vector_store_service)
        
        self._initialized = True
        logger.info("Assistant service initialized successfully")
    
    async def query(self, question: str, chat_history: List[dict] = None) -> Dict:
        """Process a legal query"""
        if not self._initialized:
            raise RuntimeError("Assistant service not initialized")
        
        return self.legal_graph_service.query(question, chat_history)
    
    async def query_stream(self, question: str, chat_history: List[dict] = None):
        """Process a legal query with streaming response"""
        if not self._initialized:
            raise RuntimeError("Assistant service not initialized")
        
        async for chunk in self.legal_graph_service.query_stream(question, chat_history):
            yield chunk
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self._initialized and self.vector_store_service is not None
