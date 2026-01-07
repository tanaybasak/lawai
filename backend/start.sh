#!/bin/bash

# Startup script for Render deployment
echo "🚀 Starting LawAI Backend..."

# Build vector stores
echo "📦 Building vector stores..."
python scripts/build_ipc_vectorstore.py

# Start the application
echo "🌟 Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
