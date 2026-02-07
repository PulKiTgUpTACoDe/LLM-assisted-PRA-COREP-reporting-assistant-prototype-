# LLM-Assisted PRA COREP Reporting Assistant (Prototype)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)

An intelligent assistant that helps UK banks prepare COREP regulatory returns by retrieving relevant PRA Rulebook sections and generating structured template data using LLM-powered analysis.

## 🎯 Overview

This prototype demonstrates:

- **Natural language queries** → Retrieve PRA Rulebook sections → Generate structured COREP data
- **End-to-end pipeline**: Question → RAG retrieval → LLM processing → Template population → Validation → Audit trail
- **Focus**: CA1 (Own Funds) template as proof-of-concept

## ✨ Features

- 🤖 **LLM-Powered Analysis**: Uses Google Gemini 2.5 Flash for regulatory interpretation
- 📚 **RAG Pipeline**: ChromaDB + LangChain for semantic document retrieval
- ✅ **Validation**: Business rule checks and cross-field validation
- 📋 **Audit Trail**: Full traceability to regulatory sources
- 🎨 **Modern UI**: Next.js frontend with real-time query processing
- 🔍 **LangSmith Tracing**: Optional observability for debugging

## 🏗️ Architecture

```
Frontend (Next.js) → Backend API (FastAPI) → LangChain Orchestrator
                                                ↓
                              ChromaDB ← Gemini Embeddings
                                                ↓
                              Gemini LLM → Structured Output
                                                ↓
                              Validator → Audit Log → Response
```

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Google AI API Key** (for Gemini)
- **LangSmith API Key** (optional, for tracing)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd LLM-assisted-PRA-COREP-reporting-assistant-prototype-
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

Create `.env` file:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
LANGSMITH_TRACING=true  # Optional
LANGSMITH_API_KEY=your_langsmith_key  # Optional
LANGSMITH_PROJECT=corep-assistant
```

### 3. Ingest Documents

Place PRA Rulebook PDFs in `data/pra_rulebook/` and run:

```bash
python scripts/ingest_documents.py
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### 5. Frontend Setup

```bash
cd ../frontend
npm install
```

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 6. Start Frontend

```bash
npm run dev
```

Frontend runs at: `http://localhost:3000`

## 🎮 Usage

1. **Navigate** to `http://localhost:3000`
2. **Enter** a regulatory scenario (e.g., "Our bank has CET1 capital of £500M...")
3. **Select** template (CA1 - Own Funds)
4. **Submit** and view:
   - Populated COREP fields
   - Validation warnings
   - Audit trail with regulatory sources

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── models/           # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── langchain_orchestrator.py
│   │   ├── langchain_query_orchestrator.py
│   │   ├── ca1_template.py
│   │   └── validator.py
│   ├── config.py
│   └── main.py
├── scripts/
│   └── ingest_documents.py
├── tests/
└── requirements.txt

frontend/
├── app/
│   ├── page.tsx          # Landing page
│   ├── query/page.tsx    # Query interface
│   └── results/page.tsx  # Results display
├── lib/
│   └── api.ts            # API client
└── package.json

data/
├── pra_rulebook/         # Place PDFs here
└── chroma_db/            # Vector database (auto-generated)
```

## 🔧 Configuration

### Backend (`backend/.env`)

| Variable            | Description     | Required                           |
| ------------------- | --------------- | ---------------------------------- |
| `GOOGLE_API_KEY`    | Gemini API key  | ✅ Yes                             |
| `GEMINI_MODEL`      | Model name      | No (default: gemini-2.5-flash)     |
| `EMBEDDING_MODEL`   | Embedding model | No (default: gemini-embedding-001) |
| `LANGSMITH_TRACING` | Enable tracing  | No (default: false)                |
| `LANGSMITH_API_KEY` | LangSmith key   | No                                 |

### Frontend (`frontend/.env.local`)

| Variable              | Description | Required |
| --------------------- | ----------- | -------- |
| `NEXT_PUBLIC_API_URL` | Backend URL | ✅ Yes   |

## 🧪 Testing

### Test LangChain Integration

```bash
cd backend
python tests/test_langchain_integration.py
```

### API Health Check

```bash
curl http://localhost:8000/api/health
```

### Sample Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Bank has CET1: £500M, AT1: £100M, Tier 2: £50M",
    "template_id": "CA1"
  }'
```

## 📊 Sample Scenarios

Try these in the query interface:

1. **Basic Capital Reporting**:

   ```
   Our bank has CET1 capital of £500M, AT1 instruments of £100M, and Tier 2 capital of £50M. What should we report in CA1?
   ```

2. **Deductions Scenario**:

   ```
   Bank has ordinary shares of £450M, retained earnings £100M, intangible assets £30M, and deferred tax assets £20M. Calculate CA1 fields.
   ```

3. **Complex Calculation**:
   ```
   CET1 before deductions: £600M, IRB shortfall: £15M, negative amounts from securitization: £10M. What is the final CET1 capital?
   ```

## 🐛 Troubleshooting

### Backend Won't Start

- **Check Python version**: `python --version` (must be 3.9+)
- **Verify dependencies**: `pip install -r requirements.txt --upgrade`
- **Check `.env`**: Ensure `GOOGLE_API_KEY` is set

### No Documents Retrieved

- **Run ingestion**: `python scripts/ingest_documents.py`
- **Check `data/chroma_db/`**: Should contain database files
- **Verify PDFs**: Place in `data/pra_rulebook/`

### Frontend Connection Error

- **Check backend**: `curl http://localhost:8000/api/health`
- **Verify `.env.local`**: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Restart both servers**

### LangSmith Not Working

- **Set environment variables** in `backend/.env`:
  ```
  LANGSMITH_TRACING=true
  LANGSMITH_API_KEY=your_key_here
  LANGSMITH_PROJECT=corep-assistant
  ```
- **Check** [LangSmith dashboard](https://smith.langchain.com/)

## 📝 API Documentation

Once the backend is running, view interactive API docs:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🎯 Limitations (Prototype Scope)

- ✅ **Implemented**: CA1 (Own Funds) template only
- ❌ **Not Implemented**: Other templates (CA3, CA4, etc.)
- ✅ **Basic Validation**: Required fields, type checks, cross-field rules
- ❌ **Advanced Features**: Multi-template workflows, user authentication, database persistence

## 🗺️ Roadmap

- [ ] Add CA3 (Capital Requirements) template
- [ ] Implement calculated field auto-population
- [ ] Add Excel/XML export for regulatory submission
- [ ] User authentication and saved sessions
- [ ] Advanced prompt engineering for complex scenarios
- [ ] Integration with bank's data systems

## 📄 License

This is a prototype for demonstration purposes.

## 🤝 Contributing

This is a proof-of-concept prototype. For production use, consider:

- Enhanced error handling
- Comprehensive testing
- Security hardening
- Scalability improvements
- Regulatory compliance review

## 📞 Support

For questions or issues, please refer to:

- `docs/langchain_integration.md` - LangChain setup details
- `docs/langsmith_setup.md` - LangSmith tracing guide
- API documentation at `http://localhost:8000/docs`

---

**Built with**: LangChain • Gemini 2.5 Flash • ChromaDB • FastAPI • Next.js
