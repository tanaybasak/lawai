"""LangGraph workflow for legal assistant RAG"""

from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from vector_store import VectorStoreManager
from config import LLM_MODEL, OPENAI_API_KEY, TOP_K_RESULTS, TEMPERATURE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the state
class GraphState(TypedDict):
    """State for the legal assistant graph"""
    question: str
    retrieved_documents: List[str]
    context: str
    answer: str
    chat_history: List[dict]


class LegalAssistantGraph:
    """LangGraph workflow for legal question answering"""
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        self.vector_store = vector_store_manager
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        self.graph = self._build_graph()
    
    def _retrieve(self, state: GraphState) -> GraphState:
        """Retrieve relevant documents"""
        logger.info(f"Retrieving documents for: {state['question']}")
        
        results = self.vector_store.similarity_search(
            state['question'],
            k=TOP_K_RESULTS
        )
        
        state['retrieved_documents'] = [doc.page_content for doc in results]
        state['context'] = "\n\n---\n\n".join([
            f"Source: {doc.metadata.get('act_name', 'Unknown')}\n{doc.page_content}"
            for doc in results
        ])
        
        logger.info(f"Retrieved {len(results)} documents")
        return state
    
    def _generate(self, state: GraphState) -> GraphState:
        """Generate answer based on retrieved context"""
        logger.info("Generating answer...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Indian legal assistant with deep knowledge of Indian laws including the Information Technology Act and Indian Penal Code.

Your role is to:
- Provide accurate legal information based on the context provided
- Cite specific sections and provisions when relevant
- Explain legal concepts in clear, understandable language
- Indicate when you're uncertain or when consultation with a lawyer is recommended
- Always be professional and precise

Important: Base your answers on the provided context from Indian legal documents. If the context doesn't contain relevant information, clearly state that."""),
            ("human", """Context from legal documents:
{context}

Question: {question}

Please provide a comprehensive answer based on the legal context above. Include relevant section numbers and provisions where applicable.""")
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


if __name__ == "__main__":
    # Test the graph
    from vector_store import initialize_vector_store
    
    vector_store = initialize_vector_store()
    assistant = LegalAssistantGraph(vector_store)
    
    test_questions = [
        "What are the penalties for hacking under the IT Act?",
        "What is the punishment for theft under IPC?",
        "Explain data protection laws in India"
    ]
    
    for question in test_questions:
        print(f"\n{'='*80}")
        print(f"Question: {question}")
        print('='*80)
        
        result = assistant.query(question)
        
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources used: {len(result['sources'])} documents")
