"""FastAPI application for LLM-assisted COREP reporting."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import query, templates, health

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="LLM-Assisted COREP Reporting Assistant",
    description="AI-powered assistant for PRA COREP regulatory returns",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print(f"🚀 Starting {app.title} v{app.version}")
    print(f"📊 Using model: {settings.gemini_model}")
    print(f"🔍 Vector DB: {settings.chroma_persist_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down application")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
