"""
Script to build FAISS vector stores from NDA clause libraries
This creates production-ready RAG systems for both mutual and unilateral NDA clause retrieval
"""
import json
import sys
from pathlib import Path
import argparse

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.vector_store import VectorStoreService


def build_nda_vector_store(nda_type="mutual"):
    """Build vector store from NDA clauses
    
    Args:
        nda_type: Type of NDA - "mutual", "unilateral", or "both"
    """
    if nda_type == "both":
        build_nda_vector_store("mutual")
        print("\n")
        build_nda_vector_store("unilateral")
        return
    
    # Determine file paths and metadata based on NDA type
    if nda_type == "unilateral":
        nda_file = "unilateral_nda_clauses.json"
        vector_store_dir = "unilateral_vector_store"
        title = "Unilateral NDA"
        nda_metadata = "unilateral"
    else:  # mutual
        nda_file = "mutual_nda_clauses.json"
        vector_store_dir = "vector_store"
        title = "Mutual NDA"
        nda_metadata = "mutual"
    
    print("=" * 80)
    print(f"Building {title} Clause Library Vector Store")
    print("=" * 80)
    
    # Initialize vector store service
    vector_service = VectorStoreService()
    
    # Load NDA clauses
    nda_path = backend_dir / "data" / "nda" / nda_file
    print(f"\nLoading {title} clauses from: {nda_path}")
    
    with open(nda_path, 'r', encoding='utf-8') as f:
        nda_clauses = json.load(f)
    
    print(f"Loaded {len(nda_clauses)} {title} clauses")
    
    # Create documents with enhanced metadata
    print("\nCreating documents with metadata...")
    documents = []
    
    for clause in nda_clauses:
        # Create rich text content for embedding
        content_parts = [
            f"Clause ID: {clause['clause_id']}",
            f"Type: {clause.get('clause_type', 'N/A')}",
            f"Category: {clause['category']}",
            f"Title: {clause['title']}",
            f"Legal Intent: {clause.get('legal_intent', 'N/A')}",
            f"Mandatory: {clause.get('is_mandatory', False)}",
            f"Clause Text: {clause['clause_text']}",
        ]
        
        # Add variants if present (new schema)
        if clause.get('variants'):
            content_parts.append(f"Variants: {len(clause['variants'])}")
            for variant in clause['variants']:
                content_parts.append(f"- {variant['style']}: {variant['text']}")
        
        # Add alternatives if present (old schema - for backwards compatibility)
        elif clause.get('alternatives'):
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
            "clause_type": clause.get('clause_type', 'Unknown'),
            "category": clause['category'],
            "title": clause['title'],
            "legal_intent": clause.get('legal_intent', ''),
            "is_mandatory": clause.get('is_mandatory', False),
            "jurisdiction": clause['jurisdiction'],
            "practice_area": clause['practice_area'],
            "risk_level": clause['risk_level'],
            "tags": ", ".join(clause['tags']),
            "law": "NDA",
            "nda_type": nda_metadata,
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
    output_dir = backend_dir / "data" / "nda" / vector_store_dir
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
    print(f"\n🧪 Testing {title} vector store with sample queries...")
    print("-" * 80)
    
    if nda_type == "unilateral":
        test_queries = [
            "confidential information definition for one-way NDA",
            "what are recipient's obligations in unilateral NDA",
            "can recipient disclose to employees",
            "what happens when agreement terminates",
            "does recipient get any IP rights"
        ]
    else:  # mutual
        test_queries = [
            "confidential information definition",
            "how long do confidentiality obligations last",
            "what are the remedies for breach",
            "governing law and jurisdiction",
            "export control requirements"
        ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = vectorstore.similarity_search(query, k=2)
        for i, doc in enumerate(results, 1):
            print(f"  {i}. {doc.metadata.get('clause_id', 'N/A')} - {doc.metadata.get('title', 'N/A')}")
            print(f"     Category: {doc.metadata.get('category', 'N/A')} | Risk: {doc.metadata.get('risk_level', 'N/A')}")
    
    print("\n" + "=" * 80)
    print(f"✅ {title} Vector Store Build Complete!")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build NDA clause library vector stores")
    parser.add_argument(
        "--type",
        choices=["mutual", "unilateral", "both"],
        default="both",
        help="Type of NDA vector store to build (default: both)"
    )
    
    args = parser.parse_args()
    build_nda_vector_store(args.type)
