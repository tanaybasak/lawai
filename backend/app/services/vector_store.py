"""Vector store service"""

import os
from typing import List, Optional, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing FAISS vector stores (supports multiple domains)"""
    
    def __init__(self, domain: str = "criminal"):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.vector_store: Optional[FAISS] = None
        self.domain = domain
        # Get store path from domain mapping, fallback to default
        self.store_path = settings.VECTOR_STORES.get(domain, settings.VECTOR_STORE_PATH)
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create vector store from documents"""
        logger.info(f"Creating vector store from {len(documents)} documents...")
        
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        logger.info("Vector store created successfully")
        return self.vector_store
    
    def save_vector_store(self) -> None:
        """Save vector store to disk"""
        if self.vector_store is None:
            raise ValueError("No vector store to save")
        
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        self.vector_store.save_local(self.store_path)
        logger.info(f"Vector store saved to {self.store_path}")
    
    def load_vector_store(self, store_path: str = None) -> Optional[FAISS]:
        """Load vector store from disk (optionally specify path)"""
        path = store_path or self.store_path
        
        if not os.path.exists(path):
            logger.warning(f"Vector store not found at {path}")
            return None
        
        try:
            loaded_store = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Only update instance store if using default path
            if store_path is None:
                self.vector_store = loaded_store
            
            logger.info(f"Vector store loaded successfully from {path}")
            return loaded_store
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return None
    
    def switch_domain(self, domain: str) -> bool:
        """Switch to a different domain's vector store"""
        if domain not in settings.VECTOR_STORES:
            logger.error(f"Unknown domain: {domain}")
            return False
        
        self.domain = domain
        self.store_path = settings.VECTOR_STORES[domain]
        return self.load_vector_store() is not None
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents"""
        if self.vector_store is None:
            logger.info("No vector store available - returning empty results")
            return []
        
        k = k or settings.TOP_K_RESULTS
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def search_multiple_stores(self, query: str, domains: List[str], k: int = None) -> Dict[str, List[Document]]:
        """Search across multiple domain stores"""
        k = k or settings.TOP_K_RESULTS
        results = {}
        
        for domain in domains:
            if domain in settings.VECTOR_STORES:
                store = self.load_vector_store(settings.VECTOR_STORES[domain])
                if store:
                    results[domain] = store.similarity_search(query, k=k)
                    logger.info(f"Found {len(results[domain])} results in {domain} domain")
        
        return results
    
    @staticmethod
    def detect_domain(query: str) -> str:
        """Detect the appropriate domain from query keywords"""
        query_lower = query.lower()
        
        # Unilateral NDA keywords
        if any(word in query_lower for word in [
            "unilateral", "one-way", "recipient", "disclosing party only",
            "company discloses", "recipient obligations"
        ]):
            return "nda_unilateral"
        
        # Mutual NDA keywords
        if any(word in query_lower for word in [
            "mutual", "bilateral", "both parties", "two-way"
        ]):
            return "nda_mutual"
        
        # General Contract/NDA keywords (default to mutual)
        if any(word in query_lower for word in [
            "nda", "confidential", "non-disclosure", "contract", "agreement",
            "clause", "confidentiality", "disclosure"
        ]):
            return "nda"
        
        # Criminal law keywords (default)
        if any(word in query_lower for word in [
            "ipc", "crpc", "criminal", "penal", "section", "offence", 
            "punishment", "bail", "arrest", "charge", "trial"
        ]):
            return "criminal"
        
        # Default to criminal (most common use case)
        return "criminal"
    
    async def initialize(self, force_reload: bool = False) -> None:
        """Initialize vector store - optional loading"""
        
        # Try to load vector store if it exists, but don't fail if it doesn't
        if os.path.exists(self.store_path):
            if self.load_vector_store():
                logger.info("Vector store initialized (loaded from disk)")
            else:
                logger.warning("Vector store exists but failed to load")
        else:
            logger.info("No vector store found - will use OpenAI knowledge only")
            # Don't raise error, just continue without vector store
