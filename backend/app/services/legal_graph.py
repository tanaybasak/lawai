"""Legal graph service using LangGraph"""

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.services.vector_store import VectorStoreService
import logging

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """State for the legal assistant graph"""
    question: str
    retrieved_documents: List[str]
    context: str
    answer: str
    chat_history: List[dict]


class LegalGraphService:
    """LangGraph workflow for legal question answering"""
    
    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.graph = self._build_graph()
    
    def _reformulate_question(self, state: GraphState) -> str:
        """Reformulate question using chat history for better retrieval"""
        question = state['question']
        chat_history = state.get('chat_history', [])
        
        # If no chat history, return original question
        if not chat_history or len(chat_history) == 0:
            return question
        
        # Build conversation context from recent history (last 3 exchanges)
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
            
Examples:
Conversation: "What are grounds for divorce?" -> "Under Hindu Marriage Act..."
Follow-up: "What about punishment?" -> Reformulated: "What is the punishment for filing false divorce claims under Hindu Marriage Act?"
            
Conversation: "What is Section 66 of IT Act?" -> "Section 66 deals with..."
Follow-up: "What are the penalties?" -> Reformulated: "What are the penalties under Section 66 of the IT Act?"
            
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
    
    def _retrieve(self, state: GraphState) -> GraphState:
        """Retrieve relevant documents using reformulated question"""
        # Reformulate question with chat history context
        search_query = self._reformulate_question(state)
        
        logger.info(f"Retrieving documents for: {search_query}")
        
        results = self.vector_store_service.similarity_search(
            search_query,
            k=settings.TOP_K_RESULTS
        )
        
        # Store as structured data for better source tracking
        state['retrieved_documents'] = [
            {
                "section": doc.metadata.get('section', 'N/A'),
                "title": doc.metadata.get('title', ''),
                "content": doc.page_content
            }
            for doc in results
        ]
        
        state['context'] = "\n\n---\n\n".join([
            f"Source: {doc.metadata.get('law', 'IPC')} Section {doc.metadata.get('section', 'N/A')}: {doc.metadata.get('title', '')}\n{doc.page_content}"
            for doc in results
        ])
        
        logger.info(f"Retrieved {len(results)} documents")
        return state
    
    def _generate(self, state: GraphState) -> GraphState:
        """Generate answer based on retrieved context and chat history"""
        logger.info("Generating answer...")
        
        # Build conversation history string if available
        chat_history = state.get('chat_history', [])
        conversation_context = ""
        if chat_history and len(chat_history) > 0:
            # Include recent conversation for context (last 4 exchanges)
            recent_history = chat_history[-8:] if len(chat_history) > 8 else chat_history
            conversation_context = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in recent_history
            ])
        
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
    
    def query(self, question: str, chat_history: List[dict] = None) -> dict:
        """Query the legal assistant"""
        initial_state = {
            "question": question,
            "retrieved_documents": [],
            "context": "",
            "answer": "",
            "chat_history": chat_history or []
        }
        
        result = self.graph.invoke(initial_state)
        
        return {
            "question": result["question"],
            "answer": result["answer"],
            "sources": result["retrieved_documents"]
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
