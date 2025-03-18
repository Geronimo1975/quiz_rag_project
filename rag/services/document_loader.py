from typing import List, Tuple
from uuid import UUID
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import os
from ..models import Document, DocumentChunk

def process_document(document) -> int:
    """Process a document and create chunks. Returns number of chunks created."""
    try:
        # Get document instance
        if isinstance(document, (str, UUID, int)):
            document = Document.objects.get(id=document)
        elif not isinstance(document, Document):
            raise ValueError(f"Invalid document type: {type(document)}")

        if not document.file:
            raise ValueError("No file associated with document")

        if not os.path.exists(document.file.path):
            raise ValueError(f"File not found at {document.file.path}")

        # Delete existing chunks
        DocumentChunk.objects.filter(document=document).delete()

        # Read PDF content
        pdf_reader = PdfReader(document.file.path)
        text = ""
        for page in pdf_reader:
            text += page.extract_text()

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)

        # Save chunks
        for i, chunk_text in enumerate(chunks):
            DocumentChunk.objects.create(
                document=document,
                chunk_number=i + 1,
                content=chunk_text
            )

        # Mark document as processed
        document.is_processed = True
        document.save()

        return len(chunks)

    except Document.DoesNotExist:
        raise ValueError(f"Document {document} not found")
    except Exception as e:
        raise ValueError(f"Error processing document: {str(e)}")