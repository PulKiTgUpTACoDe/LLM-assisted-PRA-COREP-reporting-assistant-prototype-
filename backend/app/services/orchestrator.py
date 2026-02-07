"""Main orchestrator that coordinates all services."""

from app.services.vector_store import VectorStore
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.ca1_template import CA1Template
from app.services.validator import Validator
from app.models.schemas import (
    TemplateResponse,
    TemplateField,
    AuditLogEntry,
    ConfidenceLevel
)
from typing import Dict, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class QueryOrchestrator:
    """Coordinates the entire query processing pipeline."""
    
    def __init__(self):
        """Initialize all services."""
        self.vector_store = VectorStore()
        self.llm = LLMOrchestrator()
        self.validator = Validator()
    
    async def process_query(
        self,
        query_id: str,
        question: str,
        template_id: str = "CA1",
        context: Dict[str, Any] = None
    ) -> TemplateResponse:
        """
        Process a complete COREP query from question to populated template.
        
        Pipeline:
        1. Retrieve relevant regulatory text
        2. Generate structured output via LLM
        3. Map to template fields
        4. Validate populated fields
        5. Generate audit trail
        """
        
        logger.info(f"Processing query {query_id}: {question[:100]}")
        
        # Step 1: Retrieve relevant regulatory context
        retrieval_results = self.vector_store.search(
            query=question,
            filter_metadata={"template_id": template_id} if template_id else None
        )
        
        # Format retrieved documents for LLM
        retrieved_context = []
        if retrieval_results['documents'] and retrieval_results['documents'][0]:
            for i, doc in enumerate(retrieval_results['documents'][0]):
                metadata = retrieval_results['metadatas'][0][i] if retrieval_results['metadatas'] else {}
                distance = retrieval_results['distances'][0][i] if retrieval_results['distances'] else 0
                
                retrieved_context.append({
                    "text": doc,
                    "source": metadata.get("source", "Unknown"),
                    "relevance_score": 1.0 - distance  # Convert distance to similarity
                })
        
        logger.info(f"Retrieved {len(retrieved_context)} relevant documents")
        
        # If no documents retrieved, add a note
        if not retrieved_context:
            logger.warning("No relevant documents found in vector store")
            retrieved_context = [{
                "text": "No specific regulatory context found. Using general COREP knowledge.",
                "source": "System",
                "relevance_score": 0.0
            }]
        
        # Step 2: Get empty template structure
        template_fields = CA1Template.get_empty_template()
        
        # Step 3: Call LLM to populate fields
        llm_response = await self.llm.process_scenario(
            question=question,
            retrieved_context=retrieved_context,
            template_structure=template_fields
        )
        
        # Step 4: Map LLM output to template fields
        populated_fields = self._map_llm_output(template_fields, llm_response)
        
        # Step 5: Validate populated fields
        validation_issues = self.validator.validate_fields(populated_fields)
        
        # Step 6: Generate audit log
        audit_log = self._generate_audit_log(
            llm_response,
            retrieved_context
        )
        
        # Build response
        response = TemplateResponse(
            query_id=query_id,
            template_id=template_id,
            template_name="Own Funds (CA1)",
            fields=populated_fields,
            validation_issues=validation_issues,
            audit_log=audit_log,
            missing_data=llm_response.get("missing_data", []),
            assumptions=llm_response.get("assumptions", []),
            metadata={
                "processed_at": datetime.utcnow().isoformat(),
                "documents_retrieved": len(retrieved_context),
                "fields_populated": len([f for f in populated_fields if f.value is not None]),
                "validation_errors": len([v for v in validation_issues if v.severity == "error"]),
                "validation_warnings": len([v for v in validation_issues if v.severity == "warning"])
            }
        )
        
        logger.info(f"Query {query_id} completed successfully")
        return response
    
    def _map_llm_output(
        self,
        template_fields: list[TemplateField],
        llm_response: Dict[str, Any]
    ) -> list[TemplateField]:
        """Map LLM output to template field objects."""
        
        # Create field map for quick lookup
        field_map = {f.field_code: f for f in template_fields}
        
        # Populate fields from LLM response
        for llm_field in llm_response.get("populated_fields", []):
            field_code = llm_field.get("field_code")
            
            if field_code in field_map:
                field_map[field_code].value = llm_field.get("value")
                field_map[field_code].justification = llm_field.get("justification")
                field_map[field_code].source_rules = llm_field.get("source_rules", [])
                
                # Map confidence
                confidence_str = llm_field.get("confidence", "unknown")
                try:
                    field_map[field_code].confidence = ConfidenceLevel(confidence_str)
                except ValueError:
                    field_map[field_code].confidence = ConfidenceLevel.UNKNOWN
        
        return list(field_map.values())
    
    def _generate_audit_log(
        self,
        llm_response: Dict[str, Any],
        retrieved_context: list[Dict[str, Any]]
    ) -> list[AuditLogEntry]:
        """Generate audit trail entries."""
        
        audit_entries = []
        
        for field_data in llm_response.get("populated_fields", []):
            # Build source rules with context
            source_rules = []
            for rule_id in field_data.get("source_rules", []):
                # Try to find the rule text in retrieved context
                rule_text = "Rule text not found in retrieved context"
                for ctx in retrieved_context:
                    if rule_id.lower() in ctx['text'].lower():
                        # Extract a snippet
                        rule_text = ctx['text'][:200] + "..."
                        break
                
                source_rules.append({
                    "rule_id": rule_id,
                    "rule_text": rule_text,
                    "relevance_score": "N/A"
                })
            
            # Map confidence
            confidence_str = field_data.get("confidence", "unknown")
            try:
                confidence = ConfidenceLevel(confidence_str)
            except ValueError:
                confidence = ConfidenceLevel.UNKNOWN
            
            audit_entries.append(AuditLogEntry(
                field_code=field_data.get("field_code"),
                value=field_data.get("value"),
                reasoning=field_data.get("justification", ""),
                source_rules=source_rules,
                confidence=confidence,
                retrieved_at=datetime.utcnow().isoformat()
            ))
        
        return audit_entries
