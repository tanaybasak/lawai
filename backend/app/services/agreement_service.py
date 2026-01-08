"""Agreement generation service - handles contract/agreement creation"""

from typing import Dict, List
from app.services.vector_store import VectorStoreService
from app.services.legal_graph import LegalGraphService
import logging

logger = logging.getLogger(__name__)


class AgreementService:
    """Service for generating legal agreements"""
    
    def __init__(self):
        self.vector_stores: Dict[str, VectorStoreService] = {}
        self._initialized = False
    
    async def initialize(self, force_reload: bool = False) -> None:
        """Initialize agreement vector stores"""
        if self._initialized and not force_reload:
            logger.info("Agreement service already initialized")
            return
        
        logger.info("Initializing agreement service...")
        
        # Initialize NDA vector stores
        self.vector_stores["nda_mutual"] = VectorStoreService(domain="nda_mutual")
        await self.vector_stores["nda_mutual"].initialize(force_reload=force_reload)
        
        self.vector_stores["nda_unilateral"] = VectorStoreService(domain="nda_unilateral")
        await self.vector_stores["nda_unilateral"].initialize(force_reload=force_reload)
        
        self._initialized = True
        logger.info("Agreement service initialized successfully")
    
    def _get_vector_store(self, agreement_type: str, is_mutual: bool) -> VectorStoreService:
        """Get the appropriate vector store for the agreement type"""
        if agreement_type.lower() == "nda":
            store_key = "nda_mutual" if is_mutual else "nda_unilateral"
            return self.vector_stores.get(store_key)
        
        # Default to mutual NDA for other agreement types
        return self.vector_stores.get("nda_mutual")
    
    def _build_query(self, agreement_type: str, is_mutual: bool, requirements: str) -> str:
        """Build the generation query from parameters"""
        agreement_mode = "mutual" if is_mutual else "unilateral"
        
        if requirements:
            return f"Generate a comprehensive {agreement_mode} {agreement_type.upper()} with the following requirements: {requirements}"
        
        return f"Generate a comprehensive {agreement_mode} {agreement_type.upper()} with all standard clauses including definitions, obligations, exclusions, term, remedies, and general provisions."
    
    async def generate(
        self, 
        agreement_type: str, 
        requirements: str = "", 
        is_mutual: bool = True
    ) -> Dict:
        """Generate an agreement document"""
        if not self._initialized:
            raise RuntimeError("Agreement service not initialized")
        
        # Get appropriate vector store
        vector_store = self._get_vector_store(agreement_type, is_mutual)
        
        if not vector_store or vector_store.vector_store is None:
            raise RuntimeError(f"Vector store not available for {agreement_type}")
        
        # Create specialized legal graph for agreements
        agreement_graph = LegalGraphService(vector_store)
        
        # Build and execute query
        query = self._build_query(agreement_type, is_mutual, requirements)
        result = agreement_graph.query(query, chat_history=None)
        
        sources = result.get("sources", [])
        
        return {
            "agreement_type": agreement_type,
            "document": result["answer"],
            "clauses_used": sources,
            "sources": sources,  # Include sources for API response
            "success": True
        }
    
    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self._initialized and len(self.vector_stores) > 0
