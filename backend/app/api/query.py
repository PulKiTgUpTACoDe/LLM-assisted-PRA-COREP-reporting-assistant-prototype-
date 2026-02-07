"""Query endpoint for COREP reporting assistance."""

from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, TemplateResponse
from app.services.langchain_query_orchestrator import LangChainQueryOrchestrator
from app.config import get_settings
import uuid
from datetime import datetime

router = APIRouter()
settings = get_settings()


@router.post("/", response_model=TemplateResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query and generate COREP template output.
    
    This endpoint:
    1. Retrieves relevant regulatory text from the vector database
    2. Uses Gemini LLM to interpret the scenario and generate structured output
    3. Maps the output to the specified COREP template
    4. Validates the populated fields
    5. Generates an audit trail
    """
    
    try:
        # Initialize LangChain orchestrator
        orchestrator = LangChainQueryOrchestrator()
        
        # Generate unique query ID
        query_id = str(uuid.uuid4())
        
        # Process the query
        response = await orchestrator.process_query(
            query_id=query_id,
            question=request.question,
            template_id=request.template_id,
            context=request.context or {}
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{query_id}")
async def get_query_result(query_id: str):
    """Retrieve results from a previous query (future implementation)."""
    raise HTTPException(status_code=501, detail="Query history not yet implemented")
