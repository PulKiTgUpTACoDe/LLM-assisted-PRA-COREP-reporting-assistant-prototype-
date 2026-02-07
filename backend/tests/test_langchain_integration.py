"""Test script to verify LangChain integration."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.langchain_orchestrator import get_langchain_orchestrator
from app.services.langchain_query_orchestrator import LangChainQueryOrchestrator
from app.services.ca1_template import CA1Template
import uuid


async def test_langchain_integration():
    """Test the complete LangChain pipeline."""
    
    print("🧪 Testing LangChain Integration\n")
    print("=" * 60)
    
    # Test 1: Initialize LangChain orchestrator
    print("\n1️⃣ Initializing LangChain Orchestrator...")
    try:
        langchain_orch = get_langchain_orchestrator()
        print("   ✅ LangChain orchestrator initialized")
        
        # Check vector store stats
        stats = langchain_orch.get_vectorstore_stats()
        print(f"   📊 Vector Store: {stats['status']}")
        print(f"   📚 Documents: {stats.get('document_count', 0)}")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Test 2: Test document retrieval
    print("\n2️⃣ Testing Document Retrieval...")
    try:
        test_query = "What are the components of CET1 capital?"
        docs = langchain_orch.retrieve_documents(test_query)
        print(f"   ✅ Retrieved {len(docs)} documents")
        
        if docs:
            print(f"   📄 First document source: {docs[0].get('source', 'N/A')}")
            print(f"   📝 Preview: {docs[0]['text'][:150]}...")
        else:
            print(f"   ⚠️  No documents found (vector store may be empty)")
    except Exception as e:
        print(f"   ❌ Retrieval failed: {e}")
        return False
    
    # Test 3: Test LLM processing with LangChain
    print("\n3️⃣ Testing LLM Processing via LangChain Chain...")
    try:
        template_fields = CA1Template.get_empty_template()
        
        test_scenario = """
        Our bank has the following capital position:
        - Ordinary share capital: £300M
        - Retained earnings: £150M  
        - Intangible assets: £40M
        - Deferred tax assets: £25M
        
        Calculate the CET1 capital.
        """
        
        # Test with minimal context if no docs
        context = docs if docs else [{
            "text": "CET1 comprises share capital, retained earnings, minus intangible assets and deferred tax assets per CRR Article 26.",
            "source": "Test Context",
            "relevance_score": 1.0
        }]
        
        llm_response = await langchain_orch.process_scenario(
            question=test_scenario,
            retrieved_context=context,
            template_structure=template_fields[:5]  # Limit for test
        )
        
        print(f"   ✅ LLM processing successful")
        print(f"   📊 Fields populated: {len(llm_response.get('populated_fields', []))}")
        print(f"   ⚠️  Missing data points: {len(llm_response.get('missing_data', []))}")
        print(f"   💭 Assumptions made: {len(llm_response.get('assumptions', []))}")
        
        if llm_response.get('populated_fields'):
            first_field = llm_response['populated_fields'][0]
            print(f"\n   Example field:")
            print(f"      Code: {first_field.get('field_code')}")
            print(f"      Value: {first_field.get('value')}")
            print(f"      Confidence: {first_field.get('confidence')}")
    except Exception as e:
        print(f"   ❌ LLM processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test complete query orchestrator
    print("\n4️⃣ Testing Complete Query Orchestrator...")
    try:
        orchestrator = LangChainQueryOrchestrator()
        query_id = str(uuid.uuid4())
        
        result = await orchestrator.process_query(
            query_id=query_id,
            question=test_scenario,
            template_id="CA1"
        )
        
        print(f"   ✅ Query processing complete")
        print(f"   🆔 Query ID: {query_id}")
        print(f"   📊 Template: {result.template_name}")
        print(f"   ✏️  Fields populated: {len([f for f in result.fields if f.value is not None])}")
        print(f"   ⚠️  Validation issues: {len(result.validation_issues)}")
        print(f"   📝 Audit entries: {len(result.audit_log)}")
        print(f"   🔧 Orchestration: {result.metadata.get('orchestration_method')}")
        
        # Show validation results
        if result.validation_issues:
            print(f"\n   Validation Issues:")
            for issue in result.validation_issues[:3]:  # Show first 3
                print(f"      [{issue.severity.upper()}] {issue.field_code}: {issue.message}")
        
    except Exception as e:
        print(f"   ❌ Query orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! LangChain integration is working correctly.\n")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_langchain_integration())
    sys.exit(0 if success else 1)
