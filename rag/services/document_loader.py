
from typing import List, Tuple
from uuid import UUID
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from ..models import Document, DocumentChunk

def process_document(document) -> int:
    """Process a document and create chunks. Returns number of chunks created."""
    try:
        if isinstance(document, (str, UUID)):
            document = Document.objects.get(id=document)
        
        # Delete existing chunks
        DocumentChunk.objects.filter(document=document).delete()
        
        # Read PDF content
        pdf_reader = PdfReader(document.file.path)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(text_content)
        
        # Save chunks
        for i, chunk_content in enumerate(chunks):
            DocumentChunk.objects.create(
                document=document,
                chunk_number=i,
                content=chunk_content
            )
        
        # Mark document as processed
        document.is_processed = True
        document.save()
        
        return len(chunks)
        
    except Document.DoesNotExist:
        raise ValueError(f"Document {document} not found")
    except Exception as e:
        raise ValueError(f"Error processing document: {str(e)}")
