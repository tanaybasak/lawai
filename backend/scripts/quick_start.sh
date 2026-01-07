#!/bin/bash

# Quick Start Script for IPC RAG Pipeline
# This script runs the complete pipeline from PDF extraction to RAG testing

set -e  # Exit on error

echo "=================================="
echo "🚀 IPC RAG Pipeline - Quick Start"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -d "data/ipc" ]; then
    echo "❌ Error: Please run this script from the backend/ directory"
    exit 1
fi

# Check if PDF exists
if [ ! -f "data/ipc/ipc_bare_act.pdf" ]; then
    echo "❌ Error: IPC PDF not found at data/ipc/ipc_bare_act.pdf"
    echo "   Please upload your IPC PDF to this location first"
    exit 1
fi

echo "✅ Found IPC PDF"
echo ""

# Step 1: Extract IPC sections
echo "=================================="
echo "Step 1: Extracting IPC Sections"
echo "=================================="
echo ""

if [ -f "data/ipc/ipc_sections.json" ]; then
    echo "⚠️  ipc_sections.json already exists"
    read -p "   Overwrite? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "   Skipping extraction..."
    else
        python scripts/advanced_extract_ipc.py
    fi
else
    python scripts/advanced_extract_ipc.py
fi

echo ""

# Step 2: Build vector store
echo "=================================="
echo "Step 2: Building Vector Store"
echo "=================================="
echo ""

if [ -d "data/ipc/vector_store" ]; then
    echo "⚠️  Vector store already exists"
    read -p "   Rebuild? (y/n): " rebuild
    if [ "$rebuild" != "y" ]; then
        echo "   Skipping vector store build..."
    else
        python scripts/build_ipc_vectorstore.py
    fi
else
    python scripts/build_ipc_vectorstore.py
fi

echo ""

# Step 3: Test the system
echo "=================================="
echo "Step 3: Testing RAG System"
echo "=================================="
echo ""

read -p "Run interactive tests? (y/n): " run_tests

if [ "$run_tests" = "y" ]; then
    python scripts/test_ipc_rag.py --interactive
else
    echo "Skipping tests. You can run them later with:"
    echo "  python scripts/test_ipc_rag.py --interactive"
fi

echo ""
echo "=================================="
echo "✨ Setup Complete!"
echo "=================================="
echo ""
echo "📁 Generated files:"
echo "   - data/ipc/ipc_sections.json"
echo "   - data/ipc/vector_store/"
echo ""
echo "🎯 Next steps:"
echo "   1. Test the system: python scripts/test_ipc_rag.py --interactive"
echo "   2. Integrate with your app (see scripts/README.md)"
echo "   3. Add more legal documents"
echo ""
