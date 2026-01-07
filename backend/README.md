# LawAI Backend

FastAPI backend with RAG capabilities for Indian legal documents.

## 📁 Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   ├── core/             # Configuration
│   ├── models/           # Pydantic schemas
│   └── services/         # Business logic
├── data/
│   ├── ipc/              # IPC sections & vector store
│   ├── crpc/             # CrPC sections & vector store
│   └── combined/         # Merged vector store
├── scripts/              # Extraction & setup scripts
└── requirements.txt      # Python dependencies
```

## 🚀 Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:

```bash
OPENAI_API_KEY=your_key_here
```

### 3. Run Server

```bash
# From backend directory
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or from project root:
```bash
cd backend && PYTHONPATH=/path/to/backend python -m uvicorn app.main:app --reload
```

## 📊 Data Pipeline

### Extract Legal Documents

```bash
# Extract IPC
python scripts/advanced_extract_ipc.py

# Build vector store (combines IPC & CrPC)
# Vector stores are already built in data/combined/
```

## 🔌 API Endpoints

### Health Check
```
GET http://localhost:8000/
```

### Query (Non-streaming)
```
POST http://localhost:8000/api/query
{
  "question": "What is Section 420?",
  "chat_history": []
}
```

### Query (Streaming)
```
POST http://localhost:8000/api/query-stream
{
  "question": "Tell me about bail",
  "chat_history": []
}
```

## 📚 Vector Store

- **Location**: `data/combined/vector_store/`
- **Sections**: 1,490 (708 IPC + 782 CrPC)
- **Embeddings**: OpenAI text-embedding-3-small
- **Index**: FAISS

## 🧪 Testing

API docs available at: `http://localhost:8000/docs`

## 🔧 Configuration

See `app/core/config.py` for all settings:
- LLM model (default: gpt-4-turbo-preview)
- Embedding model
- Vector store path
- Chunk sizes

## 📝 Notes

- Data files (PDFs, vector stores) are gitignored
- Set up your own data using scripts in `scripts/`
- See parent README for complete setup guide
