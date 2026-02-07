"""Pydantic models for request/response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence level for field values."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class ValidationSeverity(str, Enum):
    """Severity level for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class QueryRequest(BaseModel):
    """Request model for COREP query."""
    question: str = Field(..., description="Natural language question or scenario", min_length=10)
    template_id: str = Field(default="CA1", description="Target COREP template ID")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "question": "Our bank has CET1 capital of £500M, AT1 instruments of £100M. What should we report in CA1?",
                "template_id": "CA1"
            }]
        }
    }


class TemplateField(BaseModel):
    """Single field in a COREP template."""
    field_code: str = Field(..., description="COREP field code (e.g., C0010_R0010)")
    row_code: str = Field(..., description="Row code")
    col_code: str = Field(..., description="Column code")
    label: str = Field(..., description="Field label/description")
    value: Optional[Any] = Field(default=None, description="Populated value")
    data_type: str = Field(default="numeric", description="Data type (numeric, text, date)")
    justification: Optional[str] = Field(default=None, description="Reason for the value")
    source_rules: List[str] = Field(default_factory=list, description="Rule IDs used")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.UNKNOWN)


class ValidationIssue(BaseModel):
    """Validation error or warning."""
    field_code: str
    severity: ValidationSeverity
    message: str
    suggestion: Optional[str] = None


class AuditLogEntry(BaseModel):
    """Audit log entry for a field."""
    field_code: str
    value: Any
    reasoning: str
    source_rules: List[Dict[str, str]]  # [{rule_id, rule_text, relevance_score}]
    confidence: ConfidenceLevel
    retrieved_at: str


class TemplateResponse(BaseModel):
    """Response model for populated COREP template."""
    query_id: str = Field(..., description="Unique query identifier")
    template_id: str
    template_name: str
    fields: List[TemplateField]
    validation_issues: List[ValidationIssue]
    audit_log: List[AuditLogEntry]
    missing_data: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TemplateInfo(BaseModel):
    """Information about available COREP templates."""
    template_id: str
    name: str
    description: str
    row_count: int
    col_count: int
    field_count: int
    status: str = "available"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: Dict[str, str]
