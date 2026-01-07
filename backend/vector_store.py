"""Vector store management for legal documents"""

import os
from typing import List
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from config import VECTOR_STORE_PATH, EMBEDDING_MODEL, OPENAI_API_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages vector store operations for legal documents"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
        self.vector_store = None
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create a new vector store from documents"""
        logger.info(f"Creating vector store with {len(documents)} documents...")
        
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        logger.info("Vector store created successfully")
        return self.vector_store
    
    def save_vector_store(self, path: str = VECTOR_STORE_PATH):
        """Save vector store to disk"""
        if self.vector_store is None:
            raise ValueError("No vector store to save. Create one first.")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.vector_store.save_local(path)
        logger.info(f"Vector store saved to {path}")
    
    def load_vector_store(self, path: str = VECTOR_STORE_PATH) -> FAISS:
        """Load vector store from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Vector store not found at {path}")
        
        self.vector_store = FAISS.load_local(
            path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"Vector store loaded from {path}")
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        """Add more documents to existing vector store"""
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        self.vector_store.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 5):
        """Search with relevance scores"""
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        return self.vector_store.similarity_search_with_score(query, k=k)


def initialize_vector_store(force_reload: bool = False):
    """Initialize or load the vector store"""
    manager = VectorStoreManager()
    
    if force_reload or not os.path.exists(VECTOR_STORE_PATH):
        logger.info("Initializing vector store from scratch...")
        from document_loader import LegalDocumentLoader
        
        loader = LegalDocumentLoader()
        documents = loader.load_legal_documents()
        
        if not documents:
            raise ValueError("No documents loaded!")
        
        manager.create_vector_store(documents)
        manager.save_vector_store()
    else:
        logger.info("Loading existing vector store...")
        manager.load_vector_store()
    
    return manager


if __name__ == "__main__":
    # Test vector store
    manager = initialize_vector_store(force_reload=False)
    
    # Test search
    query = "What are the provisions for cyber crimes?"
    results = manager.similarity_search(query, k=3)
    
    print(f"\nSearch results for: '{query}'")
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Source: {doc.metadata.get('act_name')}")
        print(f"Content: {doc.page_content[:200]}...")
