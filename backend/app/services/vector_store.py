"""Vector store service"""

import os
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing FAISS vector store"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.vector_store: Optional[FAISS] = None
        self.store_path = settings.VECTOR_STORE_PATH
    
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
    
    def load_vector_store(self) -> Optional[FAISS]:
        """Load vector store from disk"""
        if not os.path.exists(self.store_path):
            logger.warning(f"Vector store not found at {self.store_path}")
            return None
        
        try:
            self.vector_store = FAISS.load_local(
                self.store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Vector store loaded successfully")
            return self.vector_store
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return None
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents"""
        if self.vector_store is None:
            logger.info("No vector store available - returning empty results")
            return []
        
        k = k or settings.TOP_K_RESULTS
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
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
