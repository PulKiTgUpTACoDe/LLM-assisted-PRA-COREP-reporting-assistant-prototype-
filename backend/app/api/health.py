"""Health check endpoint."""

from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config import get_settings
import google.generativeai as genai

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and service status."""
    
    # Check Gemini API
    gemini_status = "unknown"
    try:
        genai.configure(api_key=settings.google_api_key)
        models = genai.list_models()
        gemini_status = "connected"
    except Exception as e:
        gemini_status = f"error: {str(e)[:50]}"
    
    # Check ChromaDB via LangChain
    chroma_status = "unknown"
    try:
        from app.services.langchain_orchestrator import get_langchain_orchestrator
        langchain_orch = get_langchain_orchestrator()
        stats = langchain_orch.get_vectorstore_stats()
        chroma_status = f"{stats['status']} ({stats.get('document_count', 0)} docs)"
    except Exception as e:
        chroma_status = f"error: {str(e)[:50]}"
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "gemini_api": gemini_status,
            "vector_db": chroma_status,
            "model": settings.gemini_model,
            "orchestration": "langchain"
        }
    )
