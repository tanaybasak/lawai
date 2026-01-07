# IPC PDF Extraction and RAG Pipeline

Complete pipeline to extract IPC sections from PDF and create a RAG-enabled vector store.

## 📋 Overview

This pipeline extracts IPC sections from PDF and normalizes them into structured JSON format:

```json
{
  "jurisdiction": "India",
  "law": "IPC",
  "section": "420",
  "title": "Cheating and dishonestly inducing delivery of property",
  "text": "Whoever cheats and dishonestly induces...",
  "punishment": "imprisonment for a term which may extend to seven years..."
}
```

## 🚀 Step-by-Step Usage

### Step 1: Install Dependencies

```bash
cd backend
pip install PyPDF2
```

All other dependencies should already be in `requirements.txt`.

### Step 2: Extract IPC Sections from PDF

**Option A: Basic Extraction (Faster)**

```bash
python scripts/extract_ipc.py
```

**Option B: Advanced Extraction with LLM (More Accurate)**

```bash
python scripts/advanced_extract_ipc.py --use-llm
```

This will:
- Extract text from `backend/data/ipc/ipc_bare_act.pdf`
- Parse sections using regex patterns (or LLM if `--use-llm`)
- Save to `backend/data/ipc/ipc_sections.json`

### Step 3: Build Vector Store for RAG

```bash
python scripts/build_ipc_vectorstore.py
```

**With options:**

```bash
# Split into smaller chunks (better for long sections)
python scripts/build_ipc_vectorstore.py --split --chunk-size 1000

# Test with a query
python scripts/build_ipc_vectorstore.py --test-query "What is the punishment for cheating?"
```

This will:
- Load sections from JSON
- Create embeddings using OpenAI
- Build FAISS vector store
- Save to `backend/data/ipc/vector_store/`

### Step 4: Test the RAG System

```bash
python scripts/test_ipc_rag.py
```

## 📁 Output Files

```
backend/data/ipc/
├── ipc_bare_act.pdf          # Your uploaded PDF
├── ipc_sections.json         # Extracted & normalized sections
└── vector_store/             # FAISS vector store
    ├── index.faiss
    └── index.pkl
```

## 🔧 Scripts Overview

### 1. `extract_ipc.py`
- Basic PDF text extraction
- Regex-based section parsing
- Fast and simple

### 2. `advanced_extract_ipc.py`
- Advanced PDF extraction
- Multiple parsing strategies
- Optional LLM-based parsing for complex formats
- Better handling of edge cases

### 3. `build_ipc_vectorstore.py`
- Creates embeddings for all sections
- Builds FAISS vector store
- Supports document chunking
- Enables similarity search

### 4. `test_ipc_rag.py`
- Interactive testing interface
- Query the vector store
- See relevance scores
- Validate extraction quality

## 💡 Integration with Your App

Update `backend/app/services/vector_store.py` to use the IPC vector store:

```python
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class IPCVectorStoreService:
    def __init__(self):
        vector_store_path = Path(__file__).parent.parent.parent / "data" / "ipc" / "vector_store"
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = FAISS.load_local(
            str(vector_store_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def search(self, query: str, k: int = 5):
        return self.vector_store.similarity_search(query, k=k)
```

## 🎯 Advanced Features

### Custom Chunking Strategy

Modify chunk size based on your needs:

```bash
# Smaller chunks for precise matching
python scripts/build_ipc_vectorstore.py --split --chunk-size 500

# Larger chunks for more context
python scripts/build_ipc_vectorstore.py --split --chunk-size 2000
```

### Hybrid Search

Combine with BM25 for better retrieval:

```python
from langchain.retrievers import BM25Retriever, EnsembleRetriever

bm25 = BM25Retriever.from_documents(documents)
ensemble = EnsembleRetriever(
    retrievers=[vector_retriever, bm25],
    weights=[0.7, 0.3]
)
```

## 🐛 Troubleshooting

### "No sections extracted"
- Check PDF format and structure
- Try the advanced extractor with `--use-llm`
- Manually inspect the PDF to understand its format

### "Embedding API errors"
- Ensure OpenAI API key is set in `.env`
- Check API rate limits
- Use batching for large datasets

### "Vector store loading fails"
- Ensure vector store was created successfully
- Check file permissions
- Rebuild vector store if corrupted

## 📊 Expected Results

- **IPC PDF**: ~500+ sections
- **Extraction time**: 1-5 minutes
- **Vector store build**: 5-10 minutes
- **Query time**: < 1 second

## 🔄 Updating the Vector Store

When you get new legal documents:

1. Extract sections: `python scripts/advanced_extract_ipc.py`
2. Rebuild vector store: `python scripts/build_ipc_vectorstore.py`
3. Restart your FastAPI app to load new data

## 📚 Next Steps

1. Add more legal documents (CrPC, Evidence Act, etc.)
2. Implement hybrid search (vector + keyword)
3. Add metadata filtering (by chapter, punishment type)
4. Create a feedback loop for improving extraction
5. Add cross-referencing between sections
