"""
RAG Integration for IPC Sections
Creates vector embeddings and integrates with FAISS vector store
"""

import json
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document


class IPCVectorStore:
    """Manage vector store for IPC sections"""
    
    def __init__(self, embeddings_model: str = "text-embedding-3-small"):
        self.embeddings = OpenAIEmbeddings(model=embeddings_model)
        self.vector_store = None
    
    def load_sections_from_json(self, json_path: str) -> List[Dict]:
        """Load IPC sections from JSON file"""
        print(f"📖 Loading sections from {json_path}...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            sections = json.load(f)
        
        print(f"✅ Loaded {len(sections)} sections")
        return sections
    
    def create_documents(self, sections: List[Dict]) -> List[Document]:
        """Convert IPC sections to LangChain documents"""
        print("\n📄 Creating documents...")
        
        documents = []
        
        for section in sections:
            # Create comprehensive content
            content = f"""Section {section['section']}: {section['title']}

{section['text']}"""
            
            # Add punishment if available
            if section.get('punishment'):
                content += f"\n\nPunishment: {section['punishment']}"
            
            # Create metadata
            metadata = {
                "jurisdiction": section.get("jurisdiction", "India"),
                "law": section.get("law", "IPC"),
                "section": section["section"],
                "title": section["title"],
                "source": f"IPC Section {section['section']}"
            }
            
            if section.get("chapter"):
                metadata["chapter"] = section["chapter"]
            
            doc = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(doc)
        
        print(f"✅ Created {len(documents)} documents")
        return documents
    
    def split_documents(self, documents: List[Document], chunk_size: int = 1000, 
                       chunk_overlap: int = 200) -> List[Document]:
        """Split documents into smaller chunks if needed"""
        print(f"\n✂️  Splitting documents (chunk_size={chunk_size})...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        
        print(f"✅ Created {len(split_docs)} chunks from {len(documents)} documents")
        return split_docs
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents"""
        print("\n🔢 Creating vector embeddings...")
        print("   This may take a few minutes...")
        
        # Create embeddings in batches
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"   Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}...")
            
            if i == 0:
                # Create initial vector store
                self.vector_store = FAISS.from_documents(batch, self.embeddings)
            else:
                # Add to existing vector store
                batch_store = FAISS.from_documents(batch, self.embeddings)
                self.vector_store.merge_from(batch_store)
        
        print(f"✅ Vector store created with {len(documents)} documents")
        return self.vector_store
    
    def save_vector_store(self, save_path: str):
        """Save vector store to disk"""
        print(f"\n💾 Saving vector store to {save_path}...")
        
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        self.vector_store.save_local(str(save_path))
        
        print(f"✅ Vector store saved")
    
    def load_vector_store(self, load_path: str):
        """Load vector store from disk"""
        print(f"📖 Loading vector store from {load_path}...")
        
        self.vector_store = FAISS.load_local(
            load_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        print(f"✅ Vector store loaded")
        return self.vector_store
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """Search for relevant sections"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Create or load a vector store first.")
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """Search with relevance scores"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Create or load a vector store first.")
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def build_from_json(self, json_path: str, save_path: str, 
                       split_chunks: bool = False, chunk_size: int = 1000):
        """Complete pipeline: JSON -> Vector Store"""
        print("🚀 Building IPC vector store from JSON...\n")
        
        # Load sections
        sections = self.load_sections_from_json(json_path)
        
        # Create documents
        documents = self.create_documents(sections)
        
        # Optionally split documents
        if split_chunks:
            documents = self.split_documents(documents, chunk_size=chunk_size)
        
        # Create vector store
        self.create_vector_store(documents)
        
        # Save vector store
        self.save_vector_store(save_path)
        
        print("\n✨ Vector store build complete!")
        return self.vector_store


def main():
    """Main execution - builds combined IPC + CrPC vector store"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build RAG vector store for IPC and CrPC")
    parser.add_argument("--split", action="store_true", help="Split documents into chunks")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Chunk size for splitting")
    parser.add_argument("--test-query", type=str, help="Test query to run after building")
    args = parser.parse_args()
    
    # Paths
    ipc_json_path = Path(__file__).parent.parent / "data" / "ipc" / "ipc_sections.json"
    crpc_json_path = Path(__file__).parent.parent / "data" / "crpc" / "crpc_sections.json"
    combined_vector_store_path = Path(__file__).parent.parent / "data" / "combined" / "vector_store"
    
    print("🚀 Building combined IPC + CrPC vector store...\n")
    
    # Build IPC vector store
    print("=" * 60)
    print("📚 Processing IPC (Indian Penal Code)")
    print("=" * 60)
    rag = IPCVectorStore()
    ipc_sections = rag.load_sections_from_json(str(ipc_json_path))
    ipc_documents = rag.create_documents(ipc_sections)
    
    if args.split:
        ipc_documents = rag.split_documents(ipc_documents, chunk_size=args.chunk_size)
    
    # Build CrPC vector store
    print("\n" + "=" * 60)
    print("📚 Processing CrPC (Code of Criminal Procedure)")
    print("=" * 60)
    crpc_sections = rag.load_sections_from_json(str(crpc_json_path))
    crpc_documents = rag.create_documents(crpc_sections)
    
    if args.split:
        crpc_documents = rag.split_documents(crpc_documents, chunk_size=args.chunk_size)
    
    # Combine all documents
    print("\n" + "=" * 60)
    print("🔗 Combining IPC + CrPC documents")
    print("=" * 60)
    all_documents = ipc_documents + crpc_documents
    print(f"📊 Total documents: {len(all_documents)} (IPC: {len(ipc_documents)}, CrPC: {len(crpc_documents)})")
    
    # Create combined vector store
    print("\n" + "=" * 60)
    print("🔢 Creating combined vector store")
    print("=" * 60)
    rag.create_vector_store(all_documents)
    
    # Save combined vector store
    rag.save_vector_store(str(combined_vector_store_path))
    
    # Test query
    if args.test_query:
        print(f"\n🔍 Testing with query: '{args.test_query}'")
        results = rag.search_with_score(args.test_query, k=3)
        
        print("\n📋 Top 3 Results:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n{i}. [{doc.metadata.get('law', 'N/A')}] Section {doc.metadata['section']}: {doc.metadata['title']}")
            print(f"   Score: {score:.4f}")
            print(f"   Content: {doc.page_content[:200]}...")
    
    print(f"\n✅ Done! Combined vector store saved to: {combined_vector_store_path}")


if __name__ == "__main__":
    main()
