import os
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import PyPDF2
import json

from django.conf import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI

from ..repositories.document_repository import DocumentRepository
from rag.models import Document

class RAGService:
    def __init__(self):
        self.document_repository = DocumentRepository()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def process_document(self, document_id: UUID) -> List[Dict[str, Any]]:
        """Process a document: extract text, split into chunks, generate embeddings"""
        document = self.document_repository.get_document_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Extract text from PDF
        text = self._extract_text_from_pdf(document.file.path)
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Save chunks
        saved_chunks = []
        for i, chunk_content in enumerate(chunks):
            chunk = self.document_repository.save_document_chunk(
                document_id=document_id,
                content=chunk_content,
                chunk_index=i
            )
            
            # Generate embedding for chunk
            embedding = self._generate_embedding(chunk_content)
            self.document_repository.save_embedding(chunk.id, embedding)
            
            saved_chunks.append({
                'id': chunk.id,
                'content': chunk_content[:100] + "..." if len(chunk_content) > 100 else chunk_content,
                'chunk_index': i
            })
        
        return saved_chunks
    
    def generate_questions(self, document_id: UUID, num_questions: int = 20) -> List[Dict[str, Any]]:
        """Generate quiz questions from document chunks"""
        # Get document
        document = self.document_repository.get_document_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Get chunks with embeddings
        chunks = self.document_repository.get_document_chunks(document_id)
        if not chunks:
            raise ValueError(f"No chunks found for document {document_id}")
        
        generated_questions = []
        # Generate questions from each chunk until we have enough
        for chunk in chunks:
            if len(generated_questions) >= num_questions:
                break
                
            # Generate question from chunk
            question_data = self._generate_question_from_chunk(chunk.content)
            if question_data:
                # Save question to database
                question = self.document_repository.save_generated_question(
                    document_id=document_id,
                    chunk_id=chunk.id,
                    question_text=question_data['question'],
                    correct_answer=question_data['correct_answer'],
                    incorrect_answers=question_data['incorrect_answers'],
                    difficulty=question_data.get('difficulty', 0.5)
                )
                
                generated_questions.append({
                    'id': question.id,
                    'question': question_data['question'],
                    'correct_answer': question_data['correct_answer'],
                    'incorrect_answers': question_data['incorrect_answers']
                })
        
        return generated_questions
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _generate_question_from_chunk(self, content: str) -> Optional[Dict[str, Any]]:
        """Generate a question from chunk content"""
        try:
            prompt = f"""
            Based on the following text, create a multiple-choice question with six possible answers.
            Only one answer should be correct. The question should test understanding of key concepts.
            
            Text: {content}
            
            Return the result as a JSON object with the following format:
            {{
                "question": "The question text",
                "correct_answer": "The correct answer",
                "incorrect_answers": ["Wrong answer 1", "Wrong answer 2", "Wrong answer 3", "Wrong answer 4", "Wrong answer 5"],
                "difficulty": 0.6  # A value between 0 and 1, where 1 is most difficult
            }}
            
            Only return valid JSON, no other text.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational quiz generator assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            return None
