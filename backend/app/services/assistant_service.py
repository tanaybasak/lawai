"""Main assistant service orchestrating all components"""

from app.services.legal_query_service import LegalQueryService
from app.services.agreement_service import AgreementService
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class AssistantService:
    """Main service for legal assistant functionality - orchestrates specialized services"""
    
    def __init__(self):
        self.legal_query_service: LegalQueryService = None
        self.agreement_service: AgreementService = None
        self._initialized = False
    
    async def initialize(self, force_reload: bool = False) -> None:
        """Initialize all services"""
        if self._initialized and not force_reload:
            logger.info("Assistant service already initialized")
            return
        
        logger.info("Initializing assistant service...")
        
        # Initialize legal query service (IPC/CrPC)
        self.legal_query_service = LegalQueryService()
        await self.legal_query_service.initialize(force_reload=force_reload)
        
        # Initialize agreement service (NDAs, contracts)
        self.agreement_service = AgreementService()
        await self.agreement_service.initialize(force_reload=force_reload)
        
        self._initialized = True
        logger.info("Assistant service initialized successfully")
    
    async def query(self, question: str, chat_history: List[dict] = None) -> Dict:
        """Process a legal query - delegates to legal query service"""
        if not self._initialized:
            raise RuntimeError("Assistant service not initialized")
        
        return await self.legal_query_service.query(question, chat_history)
    
    async def query_stream(self, question: str, chat_history: List[dict] = None):
        """Process a legal query with streaming - delegates to legal query service"""
        if not self._initialized:
            raise RuntimeError("Assistant service not initialized")
        
        async for chunk in self.legal_query_service.query_stream(question, chat_history):
            yield chunk
    
    async def generate_agreement(
        self, 
        agreement_type: str, 
        requirements: str = "", 
        is_mutual: bool = True
    ) -> Dict:
        """Generate an agreement document - delegates to agreement service"""
        if not self._initialized:
            raise RuntimeError("Assistant service not initialized")
        
        return await self.agreement_service.generate(
            agreement_type=agreement_type,
            requirements=requirements,
            is_mutual=is_mutual
        )
    
    def is_ready(self) -> bool:
        """Check if all services are ready"""
        return (
            self._initialized 
            and self.legal_query_service is not None 
            and self.legal_query_service.is_ready()
            and self.agreement_service is not None
            and self.agreement_service.is_ready()
        )

