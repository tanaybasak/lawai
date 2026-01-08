"""Base graph service for reusable graph workflow logic"""

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.services.vector_store import VectorStoreService
import logging

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """Base state for graph workflows"""
    question: str
    retrieved_documents: List[dict]
    context: str
    answer: str
    chat_history: List[dict]


class BaseGraphService:
    """Base class for graph-based services with common functionality"""
    
    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def _reformulate_question(self, state: GraphState) -> str:
        """Reformulate question using chat history for better retrieval"""
        question = state['question']
        chat_history = state.get('chat_history', [])
        
        # If no chat history, return original question
        if not chat_history or len(chat_history) == 0:
            return question
        
        # Build conversation context from recent history
        recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
        conversation_context = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in recent_history
        ])
        
        # Use LLM to reformulate question with context
        reformulation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that reformulates follow-up questions to be standalone questions.
            
Given a conversation history and a follow-up question, reformulate the question to include necessary context from the conversation.
The reformulated question should be a complete, standalone question that can be understood without the conversation history.

If the question is already standalone, return it as-is."""),
            ("human", """Conversation History:
{conversation_history}

Follow-up Question: {question}

Reformulated Question:""")
        ])
        
        try:
            messages = reformulation_prompt.format_messages(
                conversation_history=conversation_context,
                question=question
            )
            response = self.llm.invoke(messages)
            reformulated = response.content.strip()
            logger.info(f"Reformulated question: '{question}' -> '{reformulated}'")
            return reformulated
        except Exception as e:
            logger.warning(f"Question reformulation failed: {e}. Using original question.")
            return question
    
    def _retrieve(self, state: GraphState, k: int = None) -> GraphState:
        """Retrieve relevant documents - common retrieval logic"""
        search_query = self._reformulate_question(state)
        logger.info(f"Retrieving documents for: {search_query}")
        
        k = k or settings.TOP_K_RESULTS
        results = self.vector_store_service.similarity_search(search_query, k=k)
        
        # Store as structured data
        state['retrieved_documents'] = [
            {
                "section": doc.metadata.get('section', 'N/A'),
                "title": doc.metadata.get('title', ''),
                "content": doc.page_content
            }
            for doc in results
        ]
        
        # Build context string
        state['context'] = "\n\n---\n\n".join([
            f"Source: {doc.metadata.get('law', 'IPC')} Section {doc.metadata.get('section', 'N/A')}: {doc.metadata.get('title', '')}\n{doc.page_content}"
            for doc in results
        ])
        
        logger.info(f"Retrieved {len(results)} documents")
        return state
    
    def _build_conversation_context(self, chat_history: List[dict]) -> str:
        """Build conversation context string from chat history"""
        if not chat_history or len(chat_history) == 0:
            return ""
        
        recent_history = chat_history[-8:] if len(chat_history) > 8 else chat_history
        return "\n".join([
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in recent_history
        ])
    
    def _format_sources_as_strings(self, documents: List[dict]) -> List[str]:
        """Format retrieved documents as string list for API response"""
        return [
            f"{doc['section']} - {doc['title']}"
            for doc in documents
        ]
