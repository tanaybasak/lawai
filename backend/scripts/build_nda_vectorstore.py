"""
Script to build a FAISS vector store from NDA clause library
This creates a production-ready RAG system for NDA clause retrieval
"""
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.vector_store import VectorStoreService


def build_nda_vector_store():
    """Build vector store from NDA clauses"""
    print("=" * 80)
    print("Building NDA Clause Library Vector Store")
    print("=" * 80)
    
    # Initialize vector store service
    vector_service = VectorStoreService()
    
    # Load NDA clauses
    nda_path = backend_dir / "data" / "nda" / "mutual_nda_clauses.json"
    print(f"\nLoading NDA clauses from: {nda_path}")
    
    with open(nda_path, 'r', encoding='utf-8') as f:
        nda_clauses = json.load(f)
    
    print(f"Loaded {len(nda_clauses)} NDA clauses")
    
    # Create documents with enhanced metadata
    print("\nCreating documents with metadata...")
    documents = []
    
    for clause in nda_clauses:
        # Create rich text content for embedding
        content_parts = [
            f"Clause ID: {clause['clause_id']}",
            f"Category: {clause['category']}",
            f"Title: {clause['title']}",
            f"Clause Text: {clause['clause_text']}",
        ]
        
        # Add alternatives if present
        if clause.get('alternatives'):
            content_parts.append(f"Alternative Versions: {len(clause['alternatives'])}")
            for i, alt in enumerate(clause['alternatives'], 1):
                content_parts.append(f"Alternative {i}: {alt}")
        
        # Add metadata fields
        if clause.get('negotiation_notes'):
            content_parts.append(f"Negotiation Notes: {clause['negotiation_notes']}")
        
        if clause.get('tags'):
            content_parts.append(f"Tags: {', '.join(clause['tags'])}")
        
        content = "\n\n".join(content_parts)
        
        # Create metadata
        metadata = {
            "clause_id": clause['clause_id'],
            "category": clause['category'],
            "title": clause['title'],
            "jurisdiction": clause['jurisdiction'],
            "practice_area": clause['practice_area'],
            "risk_level": clause['risk_level'],
            "tags": ", ".join(clause['tags']),
            "law": "NDA",
            "type": "clause"
        }
        
        # Add optional metadata
        if clause.get('related_clauses'):
            metadata['related_clauses'] = ", ".join(clause['related_clauses'])
        
        documents.append({
            "page_content": content,
            "metadata": metadata
        })
    
    print(f"Created {len(documents)} documents")
    
    # Convert to Document objects
    from langchain_core.documents import Document
    doc_objects = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in documents]
    
    # Create vector store
    output_dir = backend_dir / "data" / "nda" / "vector_store"
    print(f"\nCreating vector store at: {output_dir}")
    
    vectorstore = vector_service.create_vector_store(doc_objects)
    
    # Save vector store
    output_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(output_dir))
    
    print(f"\n✅ Vector store saved successfully!")
    print(f"   - Location: {output_dir}")
    print(f"   - Documents: {len(documents)}")
    print(f"   - Categories: {len(set(c['category'] for c in nda_clauses))}")
    print("=" * 80)
    
    # Test the vector store
    print("\n🧪 Testing vector store with sample queries...")
    print("-" * 80)
    
    test_queries = [
        "confidential information definition",
        "how long do confidentiality obligations last",
        "what are the remedies for breach",
        "can I assign this agreement",
        "export control requirements"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = vectorstore.similarity_search(query, k=2)
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('clause_id', 'N/A')} - {doc.metadata.get('title', 'N/A')}")
            print(f"     Category: {doc.metadata.get('category', 'N/A')} | Risk: {doc.metadata.get('risk_level', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("✅ NDA Vector Store Build Complete!")
    print("=" * 80)


if __name__ == "__main__":
    build_nda_vector_store()
