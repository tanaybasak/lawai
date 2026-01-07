"""Configuration for LawAI RAG Application"""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Legal Sources
LEGAL_SOURCES = [
    {
        "url": "https://www.indiacode.nic.in/handle/123456789/15442",
        "act_name": "Information Technology Act",
        "description": "IT Act 2000 - India's primary legislation for cyber law and electronic commerce"
    },
    {
        "url": "https://www.indiacode.nic.in/handle/123456789/12850",
        "act_name": "Indian Penal Code",
        "description": "IPC - The main criminal code of India"
    }
]

# Vector Store Configuration
VECTOR_STORE_PATH = "./data/vector_store"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Model Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4-turbo-preview"
TEMPERATURE = 0.1

# Retrieval Configuration
TOP_K_RESULTS = 5
