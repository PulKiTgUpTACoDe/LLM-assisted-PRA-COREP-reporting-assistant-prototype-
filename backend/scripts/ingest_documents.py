"""Python 3.14 compatible document ingestion using ChromaDB native API."""

import sys
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import google.genai as genai
from app.config import get_settings

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.google_api_key)


def extract_text_from_pdf(pdf_path: Path) -> list[tuple[str, dict]]:
    """Extract text from PDF using pypdf."""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(pdf_path)
        pages = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                metadata = {
                    "source": str(pdf_path),
                    "filename": pdf_path.name,
                    "page": i + 1,
                    "document_type": "pra_rulebook" if "own" in pdf_path.name.lower() or "crr" in pdf_path.name.lower() else "corep_instructions",
                    "template_id": "CA1"
                }
                pages.append((text, metadata))
        
        return pages
    except Exception as e:
        print(f"   ❌ Error reading PDF: {e}")
        return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Simple text chunking with overlap."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks


def generate_embedding(text: str) -> list[float]:
    """Generate embedding using Gemini."""
    result = genai.embed_content(
        model=f"models/{settings.embedding_model}",
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']


def main():
    """Ingest documents using native ChromaDB client."""
    
    print("🚀 Document Ingestion\n")
    print("=" * 60)
    
    # Initialize ChromaDB client
    print("\n1️⃣ Initializing ChromaDB...")
    persist_path = Path(settings.chroma_persist_dir)
    persist_path.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=str(persist_path),
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    try:
        collection = client.get_collection(name=settings.collection_name)
        print(f"   ✅ Using existing collection: {settings.collection_name}")
        print(f"   📊 Current documents: {collection.count()}")
        
        # Delete and recreate for fresh ingestion
        client.delete_collection(name=settings.collection_name)
        print(f"   🗑️  Cleared existing collection")
    except:
        pass
    
    collection = client.create_collection(name=settings.collection_name)
    print(f"   ✅ Created collection: {settings.collection_name}")
    
    # Get data directories
    data_dir = Path(__file__).parent.parent.parent / "data"
    pra_dir = data_dir / "pra_rulebook"
    corep_dir = data_dir / "corep_templates"
    
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    # Process PRA PDFs
    if pra_dir.exists():
        print(f"\n2️⃣ Processing PRA Rulebook PDFs...")
        pdf_files = list(pra_dir.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file.name}")
            pages = extract_text_from_pdf(pdf_file)
            print(f"      📖 Extracted {len(pages)} pages")
            
            file_chunk_count = 0
            for page_text, metadata in pages[:57]:
                chunks = chunk_text(page_text, settings.chunk_size, settings.chunk_overlap)
                file_chunk_count += len(chunks)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{pdf_file.stem}_page{metadata['page']}_chunk{i}"
                    all_chunks.append(chunk)
                    all_metadatas.append({
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    })
                    all_ids.append(chunk_id)
            
            print(f"      ✂️  Created {file_chunk_count} chunks")
    
    # Process COREP PDFs
    if corep_dir.exists():
        print(f"\n3️⃣ Processing COREP Template PDFs...")
        pdf_files = list(corep_dir.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file.name}")
            pages = extract_text_from_pdf(pdf_file)
            print(f"      📖 Extracted {len(pages)} pages")
            
            file_chunk_count = 0
            for page_text, metadata in pages:
                chunks = chunk_text(page_text, settings.chunk_size, settings.chunk_overlap)
                file_chunk_count += len(chunks)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{pdf_file.stem}_page{metadata['page']}_chunk{i}"
                    all_chunks.append(chunk)
                    all_metadatas.append({
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    })
                    all_ids.append(chunk_id)
            
            print(f"      ✂️  Created {file_chunk_count} chunks")
    
    if not all_chunks:
        print("\n❌ No documents found. Place PDF files in:")
        print(f"   - {pra_dir}")
        print(f"   - {corep_dir}")
        return
    
    print(f"\n4️⃣ Generating embeddings for {len(all_chunks)} chunks...")
    print("   ⏳ This may take a few minutes...")
    
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        if (i + 1) % 10 == 0:
            print(f"   📊 Progress: {i + 1}/{len(all_chunks)}")
        
        embedding = generate_embedding(chunk)
        embeddings.append(embedding)
    
    print(f"   ✅ Generated {len(embeddings)} embeddings")
    
    # Add to ChromaDB
    print(f"\n5️⃣ Ingesting into ChromaDB...")
    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas,
        ids=all_ids
    )
    
    print(f"   ✅ Ingested {len(all_chunks)} chunks")
    
    # Verify
    print(f"\n6️⃣ Verifying...")
    count = collection.count()
    print(f"   ✅ Vector store contains {count} documents")
    print(f"   💾 Persisted to: {persist_path}")
    
    print("\n" + "=" * 60)
    print("✅ Ingestion complete!\n")
    print("Next steps:")
    print("  1. Start backend: uvicorn app.main:app --reload")
    print("  2. Test: http://localhost:8000/api/health")


if __name__ == "__main__":
    main()
