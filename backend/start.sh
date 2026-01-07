#!/bin/bash

# Startup script for Render deployment
echo "🚀 Starting LawAI Backend..."

# Check if vector stores exist, if not build them
if [ ! -d "data/ipc/vector_store" ] || [ -z "$(ls -A data/ipc/vector_store 2>/dev/null)" ]; then
    echo "📦 Building IPC vector store..."
    python scripts/build_ipc_vectorstore.py
else
    echo "✅ Vector stores already exist"
fi

# Start the application
echo "🌟 Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
