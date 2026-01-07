# LawAI - Indian Legal Assistant

A RAG-based legal assistant for Indian laws (IPC & CrPC) with conversational AI capabilities.

## 🏗️ Project Structure

```
lawai/
├── backend/          # FastAPI backend with RAG
├── src/             # React frontend
├── public/          # Static assets
└── README.md        # This file
```

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Run backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# From project root
npm install
npm start
```

## 📚 Features

- ✅ **708 IPC Sections** - Complete Indian Penal Code
- ✅ **782 CrPC Sections** - Criminal Procedure Code
- ✅ **RAG-Powered** - Answers from actual legal documents
- ✅ **Conversational Memory** - Context-aware responses
- ✅ **Source Attribution** - Cites specific sections
- ✅ **Multi-language Support** - English & Hindi

## 🔧 Technology Stack

### Backend
- FastAPI
- LangChain & LangGraph
- OpenAI GPT-4
- FAISS Vector Store
- Python 3.13

### Frontend
- React 18
- i18next (internationalization)
- Modern CSS Modules

## 📖 Documentation

- [Backend Integration Guide](BACKEND_INTEGRATION.md)
- [Setup Guide](SETUP_GUIDE.md)
- [Backend Scripts README](backend/scripts/README.md)

## 🎯 How It Works

1. **PDF Extraction**: Extracts sections from IPC & CrPC PDFs
2. **Vector Embeddings**: Creates semantic embeddings using OpenAI
3. **FAISS Index**: Builds searchable vector store
4. **RAG Pipeline**: Retrieves relevant sections for user queries
5. **LLM Response**: GPT-4 generates answers using only retrieved sections

## 🔑 Environment Variables

```bash
# Backend (.env in backend/)
OPENAI_API_KEY=your_openai_api_key_here
```

## 📦 Data Files

Large data files (PDFs, vector stores) are not included in the repo. To set up:

1. Add your legal PDFs to `backend/data/`
2. Run extraction scripts (see SETUP_GUIDE.md)
3. Build vector stores

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is for educational purposes.

## 🔒 Security Note

- Never commit `.env` files
- Keep API keys secure
- Review `.gitignore` before commits

## 📞 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for Indian Legal Tech**
