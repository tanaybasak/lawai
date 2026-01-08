# Backend Architecture

## Modular Service Architecture

The backend is organized with clear separation of concerns using specialized services:

### Directory Structure

```
backend/app/
├── models/
│   ├── base.py              # Base models for inheritance
│   ├── requests.py          # API request models
│   ├── responses.py         # API response models
│   └── schemas.py           # Unified exports (backward compatibility)
│
├── services/
│   ├── base_graph_service.py    # Base class for graph workflows
│   ├── legal_graph.py           # Legal Q&A graph implementation
│   ├── legal_query_service.py   # Legal queries (IPC/CrPC)
│   ├── agreement_service.py     # Agreement generation (NDA/MSA)
│   ├── assistant_service.py     # Main orchestrator service
│   └── vector_store.py          # Vector store management
│
├── api/
│   └── routes.py            # API endpoints
│
└── core/
    ├── config.py            # Configuration settings
    └── utils.py             # Utility functions
```

## Service Layer Architecture

### 1. AssistantService (Orchestrator)
**Purpose**: Main coordinator that delegates to specialized services

**Responsibilities**:
- Initialize all sub-services
- Route requests to appropriate service
- Health check aggregation

**Dependencies**:
- LegalQueryService
- AgreementService

### 2. LegalQueryService
**Purpose**: Handle legal research and Q&A (IPC/CrPC)

**Responsibilities**:
- Process legal questions
- Query criminal law vector stores
- Streaming responses for legal queries

**Vector Stores Used**:
- `criminal` (combined IPC + CrPC)

### 3. AgreementService
**Purpose**: Generate legal agreements and contracts

**Responsibilities**:
- Generate NDAs (mutual/unilateral)
- Generate other contract types (MSA, employment, etc.)
- Select appropriate vector store based on agreement type

**Vector Stores Used**:
- `nda_mutual`
- `nda_unilateral`

### 4. BaseGraphService
**Purpose**: Reusable graph workflow functionality

**Responsibilities**:
- Question reformulation with chat history
- Document retrieval logic
- Conversation context building
- Source formatting utilities

**Inherited By**:
- LegalGraphService

### 5. VectorStoreService
**Purpose**: Manage FAISS vector stores

**Responsibilities**:
- Load/save vector stores
- Domain switching
- Similarity search
- Multi-store search

## Model Layer Architecture

### Base Models (`models/base.py`)
- `BaseRequest`: Common request fields (chat_history)
- `BaseResponse`: Common response fields (success)
- `SourcedResponse`: Responses with sources

### Request Models (`models/requests.py`)
- `QueryRequest`: Legal query requests
- `AgreementRequest`: Agreement generation requests

### Response Models (`models/responses.py`)
- `QueryResponse`: Legal query responses
- `AgreementResponse`: Agreement generation responses
- `HealthResponse`: Health check responses
- `ReloadResponse`: Document reload responses
- `LegalSourcesResponse`: Legal sources list

### Unified Exports (`models/schemas.py`)
Re-exports all models for backward compatibility

## Benefits of This Architecture

### 1. Separation of Concerns
- Legal queries and agreement generation are completely isolated
- Each service has a single, well-defined responsibility
- Easy to test individual components

### 2. Reusability
- `BaseGraphService` provides common graph logic
- Base models reduce duplication
- Services can be composed in different ways

### 3. Scalability
- Easy to add new agreement types (just add vector stores)
- New services can be added without modifying existing ones
- Clear extension points for new features

### 4. Maintainability
- Changes to legal queries don't affect agreements
- Clear file organization makes code easy to find
- Type hints and documentation throughout

### 5. Testability
- Each service can be unit tested independently
- Mock vector stores for testing
- Clear interfaces between components

## API Endpoints

### Legal Queries
- `POST /query` → LegalQueryService
- `POST /query-stream` → LegalQueryService (streaming)

### Agreement Generation
- `POST /generate-agreement` → AgreementService

### System
- `GET /` → Health check
- `POST /reload-documents` → Reload all services
- `GET /legal-sources` → Get configured sources

## Data Flow

### Legal Query Flow
```
Client Request
    ↓
POST /query
    ↓
AssistantService.query()
    ↓
LegalQueryService.query()
    ↓
LegalGraphService.query()
    ↓
VectorStoreService (criminal domain)
    ↓
BaseGraphService (retrieval + generation)
    ↓
QueryResponse → Client
```

### Agreement Generation Flow
```
Client Request
    ↓
POST /generate-agreement
    ↓
AssistantService.generate_agreement()
    ↓
AgreementService.generate()
    ↓
Select vector store (nda_mutual/nda_unilateral)
    ↓
LegalGraphService.query()
    ↓
BaseGraphService (retrieval + generation)
    ↓
AgreementResponse → Client
```

## Configuration

Vector stores are configured in `core/config.py`:

```python
VECTOR_STORES = {
    "criminal": "./data/combined/vector_store",
    "ipc": "./data/ipc/vector_store",
    "crpc": "./data/crpc/vector_store",
    "nda": "./data/nda/vector_store",
    "nda_mutual": "./data/nda/vector_store",
    "nda_unilateral": "./data/nda/unilateral_vector_store",
}
```

## Future Extensions

To add a new agreement type:

1. Add vector store path to `config.py`
2. Update `AgreementService._get_vector_store()` logic
3. Add new request/response models if needed
4. No changes needed to existing services!
