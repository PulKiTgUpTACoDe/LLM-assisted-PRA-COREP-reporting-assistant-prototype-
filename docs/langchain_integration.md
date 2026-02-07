# LangChain Integration Guide

## What Changed

The system now uses **LangChain** for improved orchestration of the RAG pipeline:

### New Components

1. **`langchain_orchestrator.py`**
   - Uses `ChatGoogleGenerativeAI` for LLM interactions
   - Uses `GoogleGenerativeAIEmbeddings` for document embeddings
   - Integrates `Chroma` vector store natively
   - Implements LangChain chains for better prompt flow

2. **`langchain_query_orchestrator.py`**
   - Replaces the original `orchestrator.py`
   - Uses LangChain retriever for document search
   - Chains prompt → LLM → parsing in a single pipeline

### Benefits

✅ **Better Chaining**: Cleaner pipeline composition  
✅ **Native Integration**: LangChain's Gemini & Chroma connectors  
✅ **Easier Debugging**: LangChain's built-in tracing  
✅ **Future Extensibility**: Easy to add more chains (e.g., re-ranking, agents)

---

## Setup Instructions

### 1. Update Dependencies

```bash
cd backend
.\venv\Scripts\Activate
pip install -r requirements.txt
```

New packages installed:

- `langchain==0.3.7`
- `langchain-google-genai==2.0.5`
- `langchain-community==0.3.7`
- `langchain-chroma==0.1.4`

### 2. Verify Integration

Run the test script:

```bash
cd backend
.\venv\Scripts\Activate
python tests\test_langchain_integration.py
```

Expected output:

```
✅ LangChain orchestrator initialized
✅ Retrieved X documents
✅ LLM processing successful
✅ Query processing complete
✅ ALL TESTS PASSED!
```

### 3. Check Health Endpoint

Start the server:

```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/api/health

Expected response:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "services": {
    "gemini_api": "connected",
    "vector_db": "ready (X docs)",
    "model": "gemini-2.0-flash-exp",
    "orchestration": "langchain"
  }
}
```

---

## Architecture Changes

### Before (Original)

```
Custom Orchestrator → Custom Vector Store → Direct Gemini SDK
```

### After (LangChain)

```
LangChain Chain → LangChain Retriever → LangChain ChatGoogleGenerativeAI
```

### Data Flow

```
1. User Query
   ↓
2. LangChain Retriever (Chroma + Gemini Embeddings)
   ↓
3. Retrieved Context
   ↓
4. LangChain Prompt Template
   ↓
5. ChatGoogleGenerativeAI (Gemini 2.0 Flash)
   ↓
6. Structured JSON Response
   ↓
7. Validation + Audit Log
   ↓
8. Results to Frontend
```

---

## Backward Compatibility

The original services are **still available**:

- `app/services/vector_store.py`
- `app/services/llm_orchestrator.py`
- `app/services/orchestrator.py`

You can switch back by changing the import in `app/api/query.py`:

```python
# LangChain (current)
from app.services.langchain_query_orchestrator import LangChainQueryOrchestrator

# Original (fallback)
from app.services.orchestrator import QueryOrchestrator
```

---

## Testing Checklist

- [ ] Install new dependencies
- [ ] Run test script successfully
- [ ] Backend health check shows LangChain status
- [ ] Process a test query via API
- [ ] Verify results on frontend
- [ ] Check audit log shows source rules

---

## Next Steps

With LangChain integrated, you can now easily add:

- **Re-ranking**: Improve retrieval quality
- **Agents**: Multi-step reasoning for complex scenarios
- **Custom chains**: Specialized workflows per template
- **Callbacks**: Enhanced logging and monitoring

---

## Troubleshooting

**Import errors**: Ensure all langchain packages installed  
**Vector store empty**: Run document ingestion first  
**Gemini quota**: Check API key and rate limits  
**Chain failures**: Check test script for detailed errors
