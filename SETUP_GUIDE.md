# IPC RAG Pipeline - Complete Setup Guide

## 🎉 What I've Created

I've built a complete pipeline to extract IPC sections from your PDF and create a RAG (Retrieval-Augmented Generation) application. Here's what's been set up:

### 📦 Created Files

```
backend/scripts/
├── extract_ipc.py              # Basic PDF extraction
├── advanced_extract_ipc.py     # Advanced extraction with LLM support
├── build_ipc_vectorstore.py    # Create FAISS vector store for RAG
├── test_ipc_rag.py            # Interactive testing interface
├── quick_start.sh             # One-command setup script
└── README.md                  # Detailed documentation

backend/data/ipc/
└── ipc_bare_act.pdf           # Your uploaded PDF (already there)
```

### 🎯 Output Structure

The pipeline creates normalized JSON like this:

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

---

## 🚀 Quick Start (3 Simple Steps)

### Step 1: Install Dependencies

```bash
cd backend
pip install PyPDF2
```

### Step 2: Run the Pipeline

**Option A: Automated (Recommended)**

```bash
./scripts/quick_start.sh
```

**Option B: Manual Step-by-Step**

```bash
# Extract sections from PDF
python scripts/advanced_extract_ipc.py

# Build vector store for RAG
python scripts/build_ipc_vectorstore.py

# Test the system
python scripts/test_ipc_rag.py --interactive
```

### Step 3: Test Your RAG System

```bash
python scripts/test_ipc_rag.py --interactive
```

Try queries like:
- "What is the punishment for cheating?"
- "Sections related to theft"
- "Murder under IPC"

---

## 📚 Features

### 1. **PDF Extraction** (`extract_ipc.py`)
- Extracts text from PDF
- Parses sections using regex
- Fast and simple

### 2. **Advanced Extraction** (`advanced_extract_ipc.py`)
- Multiple parsing strategies
- Optional LLM-based parsing for complex formats
- Better accuracy with `--use-llm` flag

### 3. **Vector Store** (`build_ipc_vectorstore.py`)
- Creates OpenAI embeddings
- Builds FAISS vector store
- Enables semantic search
- Supports chunking with `--split`

### 4. **Testing Interface** (`test_ipc_rag.py`)
- Interactive query testing
- Shows similarity scores
- Full RAG responses with citations
- Statistics and quality metrics

---

## 💡 Usage Examples

### Basic Extraction
```bash
python scripts/advanced_extract_ipc.py
# Output: data/ipc/ipc_sections.json
```

### Extract with LLM (Better Accuracy)
```bash
python scripts/advanced_extract_ipc.py --use-llm
# Uses GPT-4o-mini for intelligent parsing
```

### Build Vector Store with Chunking
```bash
python scripts/build_ipc_vectorstore.py --split --chunk-size 1000
# Output: data/ipc/vector_store/
```

### Test with a Specific Query
```bash
python scripts/test_ipc_rag.py --query "What is section 302?" --rag
```

### Interactive Testing
```bash
python scripts/test_ipc_rag.py --interactive
```

---

## 🔗 Integration with Your App

### Update Vector Store Service

Edit `backend/app/services/vector_store.py`:

```python
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class VectorStoreService:
    def __init__(self):
        # Load IPC vector store
        vector_store_path = Path(__file__).parent.parent.parent / "data" / "ipc" / "vector_store"
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = FAISS.load_local(
            str(vector_store_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def search_ipc(self, query: str, k: int = 5):
        """Search IPC sections"""
        return self.vector_store.similarity_search(query, k=k)
    
    def search_with_scores(self, query: str, k: int = 5):
        """Search with relevance scores"""
        return self.vector_store.similarity_search_with_score(query, k=k)
```

### Use in Legal Graph

Edit `backend/app/services/legal_graph.py`:

```python
def retrieve_context(self, state):
    """Retrieve relevant IPC sections"""
    question = state['question']
    
    # Search IPC vector store
    results = self.vector_store.search_ipc(question, k=5)
    
    # Format context
    context = "\n\n".join([
        f"Section {doc.metadata['section']}: {doc.metadata['title']}\n{doc.page_content}"
        for doc in results
    ])
    
    state['context'] = context
    return state
```

---

## 📊 Expected Results

- **PDF Pages**: ~500+ pages
- **Sections Extracted**: ~500+ sections
- **Extraction Time**: 1-5 minutes
- **Vector Store Build**: 5-10 minutes
- **Query Time**: < 1 second

---

## 🔧 Troubleshooting

### "No sections extracted"
```bash
# Try advanced extractor with LLM
python scripts/advanced_extract_ipc.py --use-llm
```

### "Vector store not found"
```bash
# Build vector store
python scripts/build_ipc_vectorstore.py
```

### "OpenAI API error"
```bash
# Check your .env file has OPENAI_API_KEY
cat backend/.env | grep OPENAI_API_KEY
```

---

## 🎯 Next Steps

### 1. **Test the Pipeline**
```bash
./scripts/quick_start.sh
```

### 2. **Add More Laws**
- Upload CrPC PDF to `data/crpc/`
- Upload Evidence Act PDF to `data/evidence_act/`
- Run extraction scripts for each

### 3. **Enhance Search**
- Implement hybrid search (vector + BM25)
- Add metadata filtering
- Cross-reference sections

### 4. **Improve Extraction**
- Fine-tune regex patterns
- Add chapter extraction
- Extract cross-references

### 5. **Integrate with UI**
- Show source sections in responses
- Add section highlighting
- Enable direct section lookup

---

## 📖 Documentation

For detailed documentation, see:
- `scripts/README.md` - Complete guide
- Code comments in each script
- Inline help: `python script.py --help`

---

## ✨ Summary

You now have a complete RAG pipeline that:

1. ✅ Extracts IPC sections from PDF
2. ✅ Normalizes them into structured JSON
3. ✅ Creates embeddings and vector store
4. ✅ Enables semantic search
5. ✅ Generates contextual answers with citations
6. ✅ Ready to integrate with your FastAPI app

**Start with:**
```bash
cd backend
pip install PyPDF2
./scripts/quick_start.sh
```

Happy coding! 🚀
