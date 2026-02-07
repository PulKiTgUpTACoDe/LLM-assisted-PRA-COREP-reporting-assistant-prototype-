"""LangChain orchestrator for COREP query processing."""

import logging
import json
import os
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.config import get_settings
from app.models.schemas import TemplateField

logger = logging.getLogger(__name__)
settings = get_settings()


class LangChainOrchestrator:
    """LangChain-based orchestrator for COREP query processing."""
    
    def __init__(self):
        os.environ["LANGCHAIN_TRACING_V2"] = settings.langsmith_tracing
        os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langsmith_endpoint
        
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature,
            max_output_tokens=settings.max_output_tokens,
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key
        )
        
        self.vectorstore = Chroma(
            collection_name=settings.collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir
        )
        
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": settings.top_k_results}
        )
        
        logger.info("LangChain orchestrator initialized successfully")
    
    async def process_scenario(
        self,
        question: str,
        retrieved_context: List[Dict[str, Any]],
        template_structure: List[TemplateField]
    ) -> Dict[str, Any]:
        """Process scenario using LangChain chain."""
        
        # Build prompt template
        prompt_template = self._create_prompt_template()
        
        # Format context from retrieved documents
        context_text = self._format_context(retrieved_context)
        
        # Create the chain
        chain = (
            {
                "question": RunnablePassthrough(),
                "context": lambda x: context_text,
                "template_fields": lambda x: self._format_template_fields(template_structure)
            }
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        try:
            # Run the chain
            result = await chain.ainvoke(question)
            
            # Parse the response
            parsed_response = self._parse_llm_response(result)
            return parsed_response
            
        except Exception as e:
            logger.error(f"LangChain processing failed: {e}")
            raise
    
    def process_query(self, question: str, template_structure: List[TemplateField]) -> Dict[str, Any]:
        try:
            logger.info(f"Processing query: {question[:100]}...")
            
            retrieved_docs = self.retriever.invoke(question)
            retrieved_context = [
                {
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", 0)
                }
                for doc in retrieved_docs
            ]
            
            logger.info(f"Retrieved {len(retrieved_context)} documents")
            
            context_text = self._format_context(retrieved_context)
            template_fields_text = self._format_template_fields(template_structure)
            prompt_template = self._create_prompt_template()
            
            chain = (
                {
                    "question": RunnablePassthrough(), 
                    "context": lambda _: context_text, 
                    "template_fields": lambda _: template_fields_text
                }
                | prompt_template
                | self.llm
                | StrOutputParser()
            )
            
            result = chain.invoke(question)
            parsed_response = self._parse_llm_response(result)
            return parsed_response
            
        except Exception as e:
            logger.error(f"LangChain processing failed: {e}")
            raise
    
    def retrieve_documents(self, question: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using LangChain retriever."""
        
        try:
            # Use LangChain retriever
            docs = self.retriever.invoke(question)
            
            # Convert to our format
            retrieved_context = []
            for doc in docs:
                retrieved_context.append({
                    "text": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown"),
                    "metadata": doc.metadata,
                    "relevance_score": doc.metadata.get("score", 0.0)
                })
            
            logger.info(f"Retrieved {len(retrieved_context)} documents via LangChain")
            return retrieved_context
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return []
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create LangChain prompt template."""
        
        template = """You are an expert regulatory reporting analyst specializing in UK PRA COREP reporting.
Your task is to analyze a bank reporting scenario and populate COREP CA1 (Own Funds) template fields based on the PRA Rulebook and CRR regulations.

## REPORTING SCENARIO
{question}

## REGULATORY CONTEXT
{context}

## TARGET TEMPLATE FIELDS
{template_fields}

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
    "Assumed all £500M CET1 capital is in the form of ordinary share capital and related share premium"
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

**CRITICAL**: Respond ONLY with the JSON object. Do not include any other text or markdown formatting.
"""
        
        return ChatPromptTemplate.from_template(template)
    
    def _format_context(self, retrieved_context: List[Dict[str, Any]]) -> str:
        """Format retrieved context for prompt."""
        
        context_text = "\n\n".join([
            f"### {ctx.get('source', 'Unknown Source')}\n{ctx['text']}"
            for ctx in retrieved_context
        ])
        
        return context_text if context_text else "No regulatory context retrieved."
    
    def _format_template_fields(self, template_structure: List[TemplateField]) -> str:
        """Format template fields for prompt."""
        
        # Limit to key fields to avoid huge prompts
        key_fields = template_structure[:20]
        
        fields_text = "Key fields to populate:\n"
        for field in key_fields:
            fields_text += f"- {field.field_code}: {field.label}\n"
        
        return fields_text
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate LLM JSON response."""
        
        try:
            # Clean response if needed
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # Find json block
                start_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("```json") or line.strip() == "```":
                        start_idx = i + 1
                        break
                response_text = "\n".join(lines[start_idx:])
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Try to parse JSON
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # If JSON is incomplete, try to extract what we can
                logger.warning(f"JSON parsing failed, attempting to extract partial data: {e}")
                
                # Try to find the last complete populated_fields entry
                import re
                fields_match = re.search(r'"populated_fields"\s*:\s*\[(.*)\]', response_text, re.DOTALL)
                
                if fields_match:
                    # Try to parse just the fields array
                    try:
                        # Add closing braces to make valid JSON
                        partial_json = f'{{"populated_fields": [{fields_match.group(1)}]}}'
                        data = json.loads(partial_json)
                        data.setdefault("missing_data", ["Response was truncated"])
                        data.setdefault("assumptions", [])
                    except:
                        # If that fails too, return empty structure
                        return {
                            "populated_fields": [],
                            "missing_data": [f"Failed to parse LLM response: {str(e)}"],
                            "assumptions": [],
                            "error": response_text[:500]
                        }
                else:
                    return {
                        "populated_fields": [],
                        "missing_data": [f"Failed to parse LLM response: {str(e)}"],
                        "assumptions": [],
                        "error": response_text[:500]
                    }
            
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
                
                # Set defaults
                field.setdefault("justification", "No justification provided")
                field.setdefault("source_rules", [])
                field.setdefault("confidence", "unknown")
            
            return data
            
        except Exception as e:
            logger.error(f"Unexpected error parsing LLM response: {e}")
            
            return {
                "populated_fields": [],
                "missing_data": [f"Failed to parse LLM response: {str(e)}"],
                "assumptions": [],
                "error": str(e)
            }
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "collection_name": settings.collection_name,
                "document_count": count,
                "status": "ready" if count > 0 else "empty"
            }
        except Exception as e:
            logger.error(f"Failed to get vectorstore stats: {e}")
            return {"status": "error", "message": str(e)}


# Create singleton instance
_langchain_orchestrator = None

def get_langchain_orchestrator() -> LangChainOrchestrator:
    """Get or create LangChain orchestrator instance."""
    global _langchain_orchestrator
    
    if _langchain_orchestrator is None:
        _langchain_orchestrator = LangChainOrchestrator()
    
    return _langchain_orchestrator
