"""Query orchestrator using LangChain."""

from typing import Dict, Any
from app.models.schemas import TemplateResponse, TemplateField, AuditLogEntry, ConfidenceLevel
from app.services.langchain_orchestrator import get_langchain_orchestrator
from app.services.ca1_template import CA1Template
from app.services.validator import Validator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LangChainQueryOrchestrator:
    def __init__(self):
        self.llm_orchestrator = get_langchain_orchestrator()
        self.validator = Validator()
    
    async def process_query(
        self,
        query_id: str,
        question: str,
        template_id: str = "CA1",
        context: Dict[str, Any] = None
    ) -> TemplateResponse:
        try:
            logger.info(f"Processing query {query_id}: {question[:100]}")
            
            retrieved_context = self.llm_orchestrator.retrieve_documents(question)
            logger.info(f"Retrieved {len(retrieved_context)} documents")
            
            if not retrieved_context:
                logger.warning("No documents found")
                retrieved_context = [{
                    "text": "No regulatory context found.",
                    "source": "System",
                    "relevance_score": 0.0
                }]
            
            template_fields = CA1Template.get_empty_template()
            
            llm_response = await self.llm_orchestrator.process_scenario(
                question=question,
                retrieved_context=retrieved_context,
                template_structure=template_fields
            )
            
            populated_fields = self._map_llm_output(template_fields, llm_response)
            validation_issues = self.validator.validate_fields(populated_fields)
            audit_log = self._generate_audit_log(llm_response, retrieved_context)
            
            return TemplateResponse(
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
                    "orchestration_method": "langchain"
                }
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}", exc_info=True)
            raise
    
    def _map_llm_output(
        self,
        template_fields: list[TemplateField],
        llm_response: Dict[str, Any]
    ) -> list[TemplateField]:
        field_map = {f.field_code: f for f in template_fields}
        
        for llm_field in llm_response.get("populated_fields", []):
            field_code = llm_field.get("field_code")
            
            if field_code in field_map:
                field_map[field_code].value = llm_field.get("value")
                field_map[field_code].justification = llm_field.get("justification")
                field_map[field_code].source_rules = llm_field.get("source_rules", [])
                
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
        audit_entries = []
        
        for field_data in llm_response.get("populated_fields", []):
            source_rules = []
            for rule_id in field_data.get("source_rules", []):
                rule_text = "Rule text not found"
                for ctx in retrieved_context:
                    if rule_id.lower() in ctx['text'].lower():
                        rule_text = ctx['text'][:200] + "..."
                        break
                
                source_rules.append({
                    "rule_id": rule_id,
                    "rule_text": rule_text,
                    "relevance_score": "N/A"
                })
            
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
