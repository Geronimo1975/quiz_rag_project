import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..models import Document, DocumentChunk

def process_document(document):
    """Process a document into searchable chunks for RAG"""
    # Get the file path
    file_path = document.file.path
    
    # Extract text from PDF
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Save chunks to database
    for i, chunk_text in enumerate(chunks):
        DocumentChunk.objects.create(
            document=document,
            chunk_number=i,
            content=chunk_text
        )
    
    document.is_processed = True
    document.save()
    return len(chunks)