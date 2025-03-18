import os
import openai
from django.conf import settings
from ..models import Document, DocumentChunk
from quiz.models import Topic, Question, Answer

def generate_rag_quiz(document, topic_name, question_count=20):
    """Generate a quiz using RAG approach"""
    # Process document if needed
    try:
        from .document_loader import process_document
        if not document.is_processed:
            num_chunks = process_document(document)
            if num_chunks == 0:
                raise ValueError(f"No chunks were created for document {document.id}")
            document.refresh_from_db()
        
        # Get chunks and verify they exist
        chunks = DocumentChunk.objects.filter(document=document)
    if not chunks.exists():
        # Try processing document again
        process_document(document)
        document.refresh_from_db()
        chunks = DocumentChunk.objects.filter(document=document)
        if not chunks.exists():
            raise ValueError(f"No chunks found for document {document.id}. Document may not be properly processed.")
    
    # Create or get the topic
    topic, created = Topic.objects.get_or_create(
        name=topic_name,
        defaults={'description': f"Questions about {topic_name}"}
    )
    
    # Generate questions using OpenAI with document chunks
    api_key = settings.OPENAI_API_KEY
    openai.api_key = api_key
    
    questions_created = 0
    
    # Use a subset of chunks for RAG (to avoid token limits)
    sample_size = min(10, chunks.count())
    sample_chunks = chunks.order_by('?')[:sample_size]
    
    # Create context from chunks
    context = "\n\n".join([chunk.content for chunk in sample_chunks])
    
    # Generate questions with OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are an expert quiz creator."},
            {"role": "user", "content": f"""
            Create {question_count} multiple-choice questions based on this document content. 
            For each question, provide 4 possible answers, with one correct answer.
            Format your response as JSON like this:
            [
                {{
                    "question": "Question text here?",
                    "answers": [
                        {{"text": "First answer", "correct": true}},
                        {{"text": "Second answer", "correct": false}},
                        {{"text": "Third answer", "correct": false}},
                        {{"text": "Fourth answer", "correct": false}}
                    ],
                    "explanation": "Explanation of the correct answer"
                }}
            ]
            
            Here's the document content to base questions on:
            {context}
            """
            }
        ],
        temperature=0.7
    )
    
    # Parse the response
    import json
    generated_questions = json.loads(response['choices'][0]['message']['content'])
    
    # Save questions to database
    for q_data in generated_questions:
        # Create question
        question = Question.objects.create(
            text=q_data["question"],
            topic=topic,
            explanation=q_data.get("explanation", "")
        )
        
        # Create answers
        for a_data in q_data["answers"]:
            Answer.objects.create(
                question=question,
                text=a_data["text"],
                is_correct=a_data["correct"]
            )
        
        questions_created += 1
    
    return questions_created, topic