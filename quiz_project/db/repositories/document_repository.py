from typing import List, Optional
from uuid import UUID

from rag.models import Document, DocumentChunk, GeneratedQuestion

class DocumentRepository:
    @staticmethod
    def get_all_documents() -> List[Document]:
        """Get all documents"""
        return Document.objects.all().order_by('-uploaded_at')
    
    @staticmethod
    def get_document_by_id(document_id: UUID) -> Optional[Document]:
        """Get document by ID"""
        try:
            return Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return None
    
    @staticmethod
    def get_document_chunks(document_id: UUID) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        return DocumentChunk.objects.filter(document_id=document_id)
    
    @staticmethod
    def save_document_chunk(document_id: UUID, content: str, chunk_index: int) -> DocumentChunk:
        """Save a document chunk"""
        document = Document.objects.get(id=document_id)
        chunk = DocumentChunk(
            document=document,
            content=content,
            chunk_index=chunk_index
        )
        chunk.save()
        return chunk
    
    @staticmethod
    def save_embedding(chunk_id: UUID, embedding: List[float]) -> None:
        """Save embedding for a document chunk"""
        chunk = DocumentChunk.objects.get(id=chunk_id)
        chunk.embedding = embedding
        chunk.save()
    
    @staticmethod
    def save_generated_question(
        document_id: UUID, 
        chunk_id: Optional[UUID], 
        question_text: str, 
        correct_answer: str, 
        incorrect_answers: List[str],
        difficulty: float = 0.5
    ) -> GeneratedQuestion:
        """Save a generated question"""
        document = Document.objects.get(id=document_id)
        chunk = None if chunk_id is None else DocumentChunk.objects.get(id=chunk_id)
        
        question = GeneratedQuestion(
            document=document,
            chunk=chunk,
            question_text=question_text,
            correct_answer=correct_answer,
            incorrect_answers=incorrect_answers,
            difficulty=difficulty
        )
        question.save()
        return question
