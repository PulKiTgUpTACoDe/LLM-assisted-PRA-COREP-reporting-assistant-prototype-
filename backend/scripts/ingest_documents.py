"""Enhanced document ingestion script supporting PDF and Excel files."""

import os
import sys
from pathlib import Path
import hashlib
from typing import List, Dict, Any
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.vector_store import VectorStore
from app.config import get_settings

settings = get_settings()


class EnhancedDocumentIngester:
    """Ingests regulatory documents including PDFs and Excel files."""
    
    def __init__(self):
        """Initialize ingester and vector store."""
        self.vector_store = VectorStore()
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def ingest_pdf(self, pdf_path: str, document_type: str = "pra_rulebook"):
        """
        Ingest a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            document_type: Type of document (pra_rulebook, corep_instructions, etc.)
        """
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"❌ PDF not found: {pdf_path}")
            return
        
        print(f"📄 Processing PDF: {pdf_file.name}")
        
        try:
            import pdfplumber
            
            all_text = []
            
            # Extract text from PDF
            with pdfplumber.open(pdf_file) as pdf:
                print(f"   📖 Total pages: {len(pdf.pages)}")
                
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
                    
                    if (i + 1) % 10 == 0:
                        print(f"   ⏳ Processed {i + 1}/{len(pdf.pages)} pages...")
            
            # Combine all text
            full_text = "\n\n".join(all_text)
            print(f"   ✅ Extracted {len(full_text)} characters")
            
            # Extract metadata
            metadata = {
                "source": str(pdf_file),
                "filename": pdf_file.name,
                "document_type": document_type,
                "template_id": "CA1",
                "file_type": "pdf"
            }
            
            # Chunk the document
            chunks = self._chunk_document(full_text)
            print(f"   ✂️  Split into {len(chunks)} chunks")
            
            # Prepare for ingestion
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = self._generate_chunk_id(pdf_file, i)
                documents.append(chunk)
                metadatas.append({
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                ids.append(chunk_id)
            
            # Ingest
            print(f"   💾 Ingesting {len(documents)} chunks into vector store...")
            self.vector_store.add_documents(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"   ✅ Successfully ingested PDF")
            
        except ImportError:
            print(f"   ❌ pdfplumber not installed. Run: pip install pdfplumber")
        except Exception as e:
            print(f"   ❌ Error processing PDF: {e}")
    
    def ingest_excel_template(self, excel_path: str):
        """
        Parse Excel file to extract CA1 template structure.
        This doesn't go into vector DB, but helps validate our template definition.
        
        Args:
            excel_path: Path to Excel file with CA1 template
        """
        
        excel_file = Path(excel_path)
        if not excel_file.exists():
            print(f"❌ Excel file not found: {excel_path}")
            return
        
        print(f"📊 Parsing Excel template: {excel_file.name}")
        
        try:
            import pandas as pd
            import openpyxl
            
            # Try to find the CA1 sheet
            xls = pd.ExcelFile(excel_file)
            print(f"   📋 Sheets found: {xls.sheet_names}")
            
            # Look for CA1 or C_01 sheet
            ca1_sheet = None
            for sheet in xls.sheet_names:
                if 'CA1' in sheet.upper() or 'C_01' in sheet.upper() or 'C 01' in sheet.upper():
                    ca1_sheet = sheet
                    break
            
            if ca1_sheet:
                print(f"   ✅ Found CA1 template sheet: {ca1_sheet}")
                df = pd.read_excel(excel_file, sheet_name=ca1_sheet)
                print(f"   📐 Template dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"   💡 Save this for template validation")
            else:
                print(f"   ⚠️  CA1 sheet not found. Available sheets: {xls.sheet_names}")
            
        except ImportError:
            print(f"   ❌ pandas/openpyxl not installed. Run: pip install pandas openpyxl")
        except Exception as e:
            print(f"   ❌ Error parsing Excel: {e}")
    
    def ingest_directory(self, directory_path: str, document_type: str = "pra_rulebook"):
        """
        Ingest all documents from a directory (PDFs, TXT, HTML).
        
        Args:
            directory_path: Path to directory
            document_type: Type of documents
        """
        
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return
        
        # Find all supported files
        pdf_files = list(directory.glob("**/*.pdf"))
        txt_files = list(directory.glob("**/*.txt"))
        html_files = list(directory.glob("**/*.html"))
        
        all_files = pdf_files + txt_files + html_files
        
        if not all_files:
            print(f"⚠️  No supported files found in {directory_path}")
            return
        
        print(f"📚 Found {len(all_files)} documents:")
        print(f"   - {len(pdf_files)} PDFs")
        print(f"   - {len(txt_files)} TXT files")
        print(f"   - {len(html_files)} HTML files")
        
        # Process each file
        for file_path in all_files:
            if file_path.suffix.lower() == '.pdf':
                self.ingest_pdf(str(file_path), document_type)
            else:
                # Use original text ingestion
                self._ingest_text_file(file_path, document_type)
    
    def _ingest_text_file(self, file_path: Path, document_type: str):
        """Ingest a text or HTML file."""
        
        print(f"📄 Processing: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            return
        
        # Extract metadata
        metadata = {
            "source": str(file_path),
            "filename": file_path.name,
            "document_type": document_type,
            "template_id": "CA1",
            "file_type": file_path.suffix[1:]
        }
        
        # Extract article number if present
        article_match = re.search(r'Article[_\s](\d+)', file_path.stem, re.IGNORECASE)
        if article_match:
            metadata["article_number"] = article_match.group(1)
        
        # Chunk
        chunks = self._chunk_document(content)
        print(f"   ✂️  Split into {len(chunks)} chunks")
        
        # Prepare for ingestion
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_chunk_id(file_path, i)
            documents.append(chunk)
            metadatas.append({
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
            ids.append(chunk_id)
        
        # Ingest
        self.vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"   ✅ Ingested {len(chunks)} chunks")
    
    def _chunk_document(self, content: str) -> List[str]:
        """Split document into overlapping chunks."""
        
        # Clean content
        content = self._clean_text(content)
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                
                # Overlap
                overlap_sentences = current_chunk[-(self.chunk_overlap // 20):] if len(current_chunk) > 1 else []
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks if chunks else [content]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        
        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    def _generate_chunk_id(self, file_path: Path, chunk_index: int) -> str:
        """Generate unique ID for a chunk."""
        content = f"{file_path}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()


def main():
    """Main ingestion entry point."""
    
    print("🚀 Enhanced PRA COREP Document Ingestion Tool\n")
    
    ingester = EnhancedDocumentIngester()
    
    # Get data directory
    data_dir = Path(__file__).parent.parent.parent / "data"
    
    print("📂 Looking for documents in data directory...\n")
    
    # Check for PDFs in data directory
    pra_dir = data_dir / "pra_rulebook"
    corep_dir = data_dir / "corep_templates"
    
    # Ingest all PDFs and text files
    if pra_dir.exists():
        print(f"📖 Ingesting PRA Rulebook documents...\n")
        ingester.ingest_directory(str(pra_dir), "pra_rulebook")
    
    if corep_dir.exists():
        print(f"\n📊 Processing COREP templates...\n")
        
        # Look for Excel files
        excel_files = list(corep_dir.glob("**/*.xlsx")) + list(corep_dir.glob("**/*.xls"))
        for excel_file in excel_files:
            ingester.ingest_excel_template(str(excel_file))
        
        # Ingest PDF instructions
        ingester.ingest_directory(str(corep_dir), "corep_instructions")
    
    # Show final stats
    stats = ingester.vector_store.get_collection_stats()
    print(f"\n📊 Final Vector Store Stats:")
    print(f"   Collection: {stats['collection_name']}")
    print(f"   Total documents: {stats['document_count']}")
    print(f"   Status: {stats['status']}")
    
    print("\n✨ Ingestion complete!")


if __name__ == "__main__":
    main()
