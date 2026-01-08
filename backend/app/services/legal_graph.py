"""Legal graph service using LangGraph"""

from typing import List, Dict
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.services.vector_store import VectorStoreService
from app.services.base_graph_service import BaseGraphService, GraphState
import logging

logger = logging.getLogger(__name__)


class LegalGraphService(BaseGraphService):
    """LangGraph workflow for legal question answering"""
    
    def __init__(self, vector_store_service: VectorStoreService):
        super().__init__(vector_store_service)
        self.graph = self._build_graph()
    
    def _retrieve(self, state: GraphState) -> GraphState:
        """Retrieve relevant legal documents"""
        return super()._retrieve(state, k=settings.TOP_K_RESULTS)
    
    def _generate(self, state: GraphState) -> GraphState:
        """Generate answer based on retrieved context and chat history"""
        logger.info("Generating answer...")
        
        # Build conversation history string using base class method
        conversation_context = self._build_conversation_context(state.get('chat_history', []))
        
        # Build prompt with or without conversation history
        if conversation_context:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert Indian legal assistant specializing in the Indian criminal law (IPC and CrPC).

IMPORTANT: You must ONLY answer questions based on the legal sections provided in the context below. Do NOT use external knowledge.

Rules:
- ONLY cite legal sections that are provided in the context
- If the provided context doesn't contain information to answer the question, clearly state: "I don't have information about this in the provided legal sections."
- Always cite specific IPC section numbers and titles from the context
- Provide clear, accurate legal guidance based ONLY on the provided sections
- Recommend consulting a qualified lawyer for specific legal advice
- Do NOT make up or assume information not present in the context

Context from Indian Laws (IPC & CrPC):
{context}"""),
                ("human", """Previous Conversation:
{conversation_history}

Current Question: {question}

Answer based ONLY on the legal sections provided in the context above.""")
            ])
            
            messages = prompt.format_messages(
                context=state['context'],
                conversation_history=conversation_context,
                question=state['question']
            )
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert Indian legal assistant specializing in the Indian criminal law (IPC and CrPC).

IMPORTANT: You must ONLY answer questions based on the legal sections provided in the context below. Do NOT use external knowledge.

Rules:
- ONLY cite legal sections that are provided in the context
- If the provided context doesn't contain information to answer the question, clearly state: "I don't have information about this in the provided legal sections."
- Always cite specific IPC section numbers and titles from the context
- Provide clear, accurate legal guidance based ONLY on the provided sections
- Recommend consulting a qualified lawyer for specific legal advice
- Do NOT make up or assume information not present in the context

Context from Indian Laws (IPC & CrPC):
{context}"""),
                ("human", """Question: {question}

Answer based ONLY on the legal sections provided in the context above.""")
            ])
            
            messages = prompt.format_messages(
                context=state['context'],
                question=state['question']
            )
        
        response = self.llm.invoke(messages)
        state['answer'] = response.content
        
        logger.info("Answer generated")
        return state
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("generate", self._generate)
        
        # Add edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    def query(self, question: str, chat_history: List[dict] = None) -> Dict:
        """Query the legal assistant"""
        initial_state = {
            "question": question,
            "retrieved_documents": [],
            "context": "",
            "answer": "",
            "chat_history": chat_history or []
        }
        
        result = self.graph.invoke(initial_state)
        
        # Convert retrieved_documents to strings for API response
        sources = self._format_sources_as_strings(result["retrieved_documents"])
        
        return {
            "question": result["question"],
            "answer": result["answer"],
            "sources": sources
        }
    
    async def query_stream(self, question: str, chat_history: List[dict] = None):
        """Query the legal assistant with streaming response"""
        # Step 1: Reformulate and retrieve (non-streaming)
        initial_state = {
            "question": question,
            "retrieved_documents": [],
            "context": "",
            "answer": "",
            "chat_history": chat_history or []
        }
        
        # Reformulate question with chat history
        search_query = self._reformulate_question(initial_state)
        
        # Retrieve documents
        results = self.vector_store_service.similarity_search(
            search_query,
            k=settings.TOP_K_RESULTS
        )
        
        retrieved_documents = [
            {
                "section": doc.metadata.get('section', 'N/A'),
                "title": doc.metadata.get('title', ''),
                "content": doc.page_content
            }
            for doc in results
        ]
        context = "\n\n---\n\n".join([
            f"Source: {doc.metadata.get('law', 'IPC')} Section {doc.metadata.get('section', 'N/A')}: {doc.metadata.get('title', '')}\n{doc.page_content}"
            for doc in results
        ])
        
        # Send sources first
        yield {
            "type": "sources",
            "sources": retrieved_documents
        }
        
        # Step 2: Generate answer with streaming
        chat_history_data = initial_state.get('chat_history', [])
        conversation_context = ""
        if chat_history_data and len(chat_history_data) > 0:
            recent_history = chat_history_data[-8:] if len(chat_history_data) > 8 else chat_history_data
            conversation_context = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in recent_history
            ])
        
        # Build prompt
        if conversation_context:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert Indian legal assistant specializing in the Indian criminal law (IPC and CrPC).

IMPORTANT: You must ONLY answer questions based on the legal sections provided in the context below. Do NOT use external knowledge.

Rules:
- ONLY cite legal sections that are provided in the context
- If the provided context doesn't contain information to answer the question, clearly state: "I don't have information about this in the provided legal sections."
- Always cite specific IPC section numbers and titles from the context
- Provide clear, accurate legal guidance based ONLY on the provided sections
- Recommend consulting a qualified lawyer for specific legal advice
- Do NOT make up or assume information not present in the context

Context from Indian Laws (IPC & CrPC):
{context}"""),
                ("human", """Previous Conversation:
{conversation_history}

Current Question: {question}

Answer based ONLY on the legal sections provided in the context above.""")
            ])
            
            messages = prompt.format_messages(
                context=context,
                conversation_history=conversation_context,
                question=question
            )
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert Indian legal assistant specializing in the Indian criminal law (IPC and CrPC).

IMPORTANT: You must ONLY answer questions based on the legal sections provided in the context below. Do NOT use external knowledge.

Rules:
- ONLY cite legal sections that are provided in the context
- If the provided context doesn't contain information to answer the question, clearly state: "I don't have information about this in the provided legal sections."
- Always cite specific IPC section numbers and titles from the context
- Provide clear, accurate legal guidance based ONLY on the provided sections
- Recommend consulting a qualified lawyer for specific legal advice
- Do NOT make up or assume information not present in the context

Context from Indian Laws (IPC & CrPC):
{context}"""),
                ("human", """Question: {question}

Answer based ONLY on the legal sections provided in the context above.""")
            ])
            
            messages = prompt.format_messages(
                context=context,
                question=question
            )
        
        # Stream the response
        full_answer = ""
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                full_answer += chunk.content
                yield {
                    "type": "content",
                    "content": chunk.content
                }
        
        # Send completion
        yield {
            "type": "done",
            "question": question,
            "answer": full_answer
        }
