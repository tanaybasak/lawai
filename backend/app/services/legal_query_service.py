"""Legal query service - handles legal questions and research"""

from typing import Dict, List
from app.services.vector_store import VectorStoreService
from app.services.legal_graph import LegalGraphService
import logging

logger = logging.getLogger(__name__)


class LegalQueryService:
    """Service for handling legal queries and research"""
    
    def __init__(self):
        self.vector_store: VectorStoreService = None
        self.legal_graph: LegalGraphService = None
        self._initialized = False
    
    async def initialize(self, force_reload: bool = False) -> None:
        """Initialize legal query service"""
        if self._initialized and not force_reload:
            logger.info("Legal query service already initialized")
            return
        
        logger.info("Initializing legal query service...")
        
        # Initialize criminal law vector store
        self.vector_store = VectorStoreService(domain="criminal")
        await self.vector_store.initialize(force_reload=force_reload)
        
        # Initialize legal graph
        self.legal_graph = LegalGraphService(self.vector_store)
        
        self._initialized = True
        logger.info("Legal query service initialized successfully")
    
    async def query(self, question: str, chat_history: List[dict] = None) -> Dict:
        """Process a legal query"""
        if not self._initialized:
            raise RuntimeError("Legal query service not initialized")
        
        return self.legal_graph.query(question, chat_history)
    
    async def query_stream(self, question: str, chat_history: List[dict] = None):
        """Process a legal query with streaming response"""
        if not self._initialized:
            raise RuntimeError("Legal query service not initialized")
        
        async for chunk in self.legal_graph.query_stream(question, chat_history):
            yield chunk
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self._initialized and self.vector_store is not None
