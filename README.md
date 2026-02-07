# LLM-Assisted PRA COREP Reporting Assistant

A prototype LLM-powered assistant for UK Banks to prepare PRA COREP regulatory returns, focusing on the CA1 (Own Funds) template.

## 🎯 Project Overview

This system helps analysts prepare COREP regulatory returns by:

- Accepting natural language questions about reporting scenarios
- Retrieving relevant PRA Rulebook sections using RAG
- Generating structured output aligned to COREP templates
- Providing audit trails showing which rules justify each field

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│  ChromaDB   │
│  Frontend   │      │   Backend    │      │  (Vector)   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ Gemini 3.0   │
                     │    Flash     │
                     └──────────────┘
```

## 📁 Project Structure

```
.
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Pydantic schemas
│   │   └── config.py       # Configuration
│   ├── scripts/            # Data ingestion scripts
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # Next.js application
│   ├── app/                # App router pages
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── public/             # Static assets
├── data/                   # Regulatory documents
│   ├── pra_rulebook/
│   ├── corep_templates/
│   └── chroma_db/          # Vector database storage
└── docs/                   # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Google AI Studio API Key (Gemini)

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
cp .env.example .env  # Add your Gemini API key
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to access the application.

## 📊 Tech Stack

- **Backend**: FastAPI, Python 3.12
- **Frontend**: Next.js 15, React 19, TailwindCSS
- **LLM**: Google Gemini 2.0 Flash
- **Embeddings**: Gemini text-embedding-004
- **Vector DB**: ChromaDB
- **Data Grid**: AG Grid Community

## 📝 Development Status

This is a prototype demonstrating LLM-assisted regulatory reporting. Currently supports:

- ✅ CA1 (Own Funds) template
- ✅ Natural language query processing
- ✅ Regulatory text retrieval
- ✅ Structured output generation
- ✅ Basic validation rules
- ✅ Audit trail generation

## 📚 Documentation

See [`data_collection_guide.md`](./docs/data_collection_guide.md) for instructions on collecting PRA Rulebook documents.

## 🔒 License

MIT License - See LICENSE file for details.

## 🙋 Support

For questions or issues, please open a GitHub issue.
