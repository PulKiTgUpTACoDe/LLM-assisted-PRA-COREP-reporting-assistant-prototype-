# LangSmith Tracing Setup

## What is LangSmith?

LangSmith is LangChain's observability platform that helps you:

- 🔍 **Debug** LLM chains and prompts
- 📊 **Monitor** performance and costs
- 🧪 **Test** and evaluate outputs
- 🎯 **Optimize** prompts and chains

## Setup Instructions

### 1. Get API Key

1. Go to https://smith.langchain.com
2. Sign up or log in
3. Create a new API key
4. Copy your API key

### 2. Configure Environment

Add to your `backend/.env`:

```bash
# Enable LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_actual_api_key_here
LANGCHAIN_PROJECT=corep-assistant
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 3. Restart Backend

```bash
# Backend will auto-reload if using uvicorn --reload
# Otherwise, restart manually
uvicorn app.main:app --reload
```

### 4. View Traces

1. Visit https://smith.langchain.com
2. Select your project: **corep-assistant**
3. Submit a query through the frontend
4. See the full trace with:
   - Document retrieval steps
   - Prompt template
   - LLM calls
   - Response parsing
   - Execution times

## What Gets Traced

With LangSmith enabled, you'll see:

- **Retrieval Chain**: Documents fetched from ChromaDB
- **Prompt Construction**: Complete prompt sent to Gemini
- **LLM Invocation**: Model responses and timing
- **Output Parsing**: JSON extraction and validation
- **Errors**: Stack traces and debugging info

## Example Trace View

```
└─ LangChain Query Processing (2.3s)
   ├─ Retriever (0.5s)
   │  └─ Retrieved 10 docs from ChromaDB
   ├─ Prompt Template (0.1s)
   │  └─ Filled template with context
   ├─ ChatGoogleGenerativeAI (1.5s)
   │  └─ gemini-2.5-flash response
   └─ Parse Output (0.2s)
      └─ Extracted 3 populated fields
```

## Disable Tracing

To turn off (e.g., in production):

```bash
LANGCHAIN_TRACING_V2=false
```

## Tips

- **Project Names**: Use different projects for dev/staging/prod
- **Feedback**: Add thumbs up/down in LangSmith UI to track quality
- **Datasets**: Save good examples to create evaluation sets
- **Sharing**: Share trace links with team members for debugging
