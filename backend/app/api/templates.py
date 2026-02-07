"""Templates endpoint."""

from fastapi import APIRouter
from app.models.schemas import TemplateInfo
from typing import List

router = APIRouter()


@router.get("/", response_model=List[TemplateInfo])
async def list_templates():
    """List available COREP templates."""
    
    # For now, return CA1 template info
    # This will be expanded as we add more templates
    return [
        TemplateInfo(
            template_id="CA1",
            name="Own Funds",
            description="COREP CA1 - Own Funds template for reporting capital composition",
            row_count=47,  # Standard CA1 has ~47 rows
            col_count=2,   # Typically Amount and Of which: classified as equity
            field_count=94,
            status="available"
        )
    ]


@router.get("/{template_id}", response_model=TemplateInfo)
async def get_template(template_id: str):
    """Get specific template information."""
    
    templates = await list_templates()
    for template in templates:
        if template.template_id == template_id:
            return template
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
