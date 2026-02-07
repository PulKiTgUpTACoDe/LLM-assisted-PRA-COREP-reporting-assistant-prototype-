"""LLM Orchestrator using Google Gemini for regulatory analysis."""

import google.generativeai as genai
from app.config import get_settings
from app.models.schemas import TemplateField, ConfidenceLevel
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMOrchestrator:
    """Orchestrates LLM calls to Gemini for COREP template population."""
    
    def __init__(self):
        """Initialize Gemini client."""
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
    
    async def process_scenario(
        self,
        question: str,
        retrieved_context: List[Dict[str, Any]],
        template_structure: List[TemplateField]
    ) -> Dict[str, Any]:
        """
        Process a regulatory scenario and generate structured output.
        
        Args:
            question: User's natural language question/scenario
            retrieved_context: Retrieved regulatory text chunks
            template_structure: Target template structure
        
        Returns:
            Dictionary with populated fields and justifications
        """
        
        prompt = self._build_prompt(question, retrieved_context, template_structure)
        
        try:
            response = await self._call_gemini(prompt)
            parsed_response = self._parse_llm_response(response)
            return parsed_response
            
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            raise
    
    def _build_prompt(
        self,
        question: str,
        retrieved_context: List[Dict[str, Any]],
        template_structure: List[TemplateField]
    ) -> str:
        """Build comprehensive prompt for Gemini."""
        
        # Format retrieved context
        context_text = "\n\n".join([
            f"### {ctx.get('source', 'Unknown Source')}\n{ctx['text']}"
            for ctx in retrieved_context
        ])
        
        # Build template schema for output
        template_schema = {
            field.field_code: {
                "label": field.label,
                "data_type": field.data_type,
                "row_code": field.row_code,
                "col_code": field.col_code
            }
            for field in template_structure[:20]  # Limit for now to avoid huge prompts
        }
        
        prompt = f"""You are an expert regulatory reporting analyst specializing in UK PRA COREP reporting. 
Your task is to analyze a bank reporting scenario and populate COREP CA1 (Own Funds) template fields based on the PRA Rulebook and CRR regulations.

## REPORTING SCENARIO
{question}

## REGULATORY CONTEXT
Below are relevant excerpts from the PRA Rulebook and Capital Requirements Regulation (CRR):

{context_text}

## TARGET TEMPLATE: CA1 - Own Funds
You must populate the following fields in the COREP CA1 template:

**Key Fields to Populate:**
- R0010_C0010: Capital instruments and share premium
- R0030_C0010: Retained earnings
- R0040_C0010: Accumulated other comprehensive income
- R0050_C0010: Other reserves
- R0090_C0010: Intangible assets (deduction from CET1)
- R0100_C0010: Deferred tax assets (deduction from CET1)
- R0210_C0010: AT1 capital instruments
- R0300_C0010: Tier 2 capital instruments

## INSTRUCTIONS
1. Carefully analyze the scenario against the regulatory context
2. Determine appropriate values for each applicable field
3. For each field you populate:
   - Provide the numeric value (in the currency units specified in the scenario)
   - Explain the justification citing specific regulatory articles
   - List the source rule paragraphs used (e.g., "CRR Article 26(1)")
   - Assign a confidence level: "high", "medium", "low", or "unknown"
4. Identify any missing information needed to complete the template
5. Document any assumptions you made

## OUTPUT FORMAT (JSON)
Return ONLY valid JSON in this exact structure:

{{
  "populated_fields": [
    {{
      "field_code": "R0010_C0010",
      "value": 500000000,
      "justification": "The scenario states CET1 capital of £500M. Per CRR Article 26, this includes capital instruments and share premium accounts.",
      "source_rules": ["CRR Article 26(1)", "CRR Article 28"],
      "confidence": "high"
    }}
  ],
  "missing_data": [
    "Breakdown of CET1 capital components (share capital vs. share premium not specified)"
  ],
  "assumptions": [
    "Assumed all £500M CET1 capital is in the form of ordinary share capital and related share premium",
    "Assumed intangible assets and DTA values are provided explicitly"
  ],
  "calculated_fields": [
    {{
      "field_code": "R0200_C0010",
      "value": 420000000,
      "calculation": "CET1 capital = R0070 (CET1 before adjustments) - R0180 (total deductions)",
      "formula": "500000000 - 80000000"
    }}
  ]
}}

**CRITICAL**: Respond ONLY with the JSON object. Do not include any other text, explanations, or markdown formatting."""
        
        return prompt
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API with the constructed prompt."""
        
        generation_config = {
            "temperature": settings.temperature,
            "max_output_tokens": settings.max_output_tokens,
            "response_mime_type": "application/json"  # Force JSON output
        }
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM JSON response."""
        
        try:
            # Parse JSON
            data = json.loads(response_text)
            
            # Validate required keys
            required_keys = ["populated_fields", "missing_data", "assumptions"]
            for key in required_keys:
                if key not in data:
                    logger.warning(f"Missing key in LLM response: {key}")
                    data[key] = []
            
            # Validate populated fields structure
            for field in data.get("populated_fields", []):
                if "field_code" not in field or "value" not in field:
                    logger.warning(f"Invalid field structure: {field}")
                    continue
                
                # Set defaults for missing attributes
                field.setdefault("justification", "No justification provided")
                field.setdefault("source_rules", [])
                field.setdefault("confidence", "unknown")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            
            # Return empty structure if parsing fails
            return {
                "populated_fields": [],
                "missing_data": ["Failed to parse LLM response"],
                "assumptions": [],
                "error": str(e)
            }
