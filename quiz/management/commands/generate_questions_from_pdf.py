import os
import random
import tempfile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from quiz.models import Topic, Question, Answer
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
import openai
import json
import time

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class Command(BaseCommand):
    help = 'Generate quiz questions from a PDF document using RAG'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to the PDF document')
        parser.add_argument('--topic', type=str, default='Python Programming', help='Topic name for the questions')
        parser.add_argument('--count', type=int, default=200, help='Number of questions to generate')
        parser.add_argument('--api-key', type=str, help='OpenAI API key')
        parser.add_argument('--batch-size', type=int, default=10, help='Number of questions to generate in each batch')

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file"""
        self.stdout.write(f"Extracting text from {pdf_path}")
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            self.stderr.write(f"Error extracting text from PDF: {e}")
        return text

    def chunk_text(self, text, chunk_size=5000, overlap=500):
        """Split text into overlapping chunks"""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk) > 100:  # Avoid very small chunks
                chunks.append(chunk)
        return chunks

    def generate_question_from_text(self, text_chunk, topic_name, api_key):
        """Generate a quiz question from a text chunk using OpenAI"""
        if not api_key:
            # Mock question generation if no API key provided
            return self.mock_generate_question(topic_name)
        
        openai.api_key = api_key
        
        prompt = f"""
        Based on the following Python documentation text, create a challenging quiz question about Python programming:
        
        {text_chunk[:1500]}
        
        Generate:
        1. A specific quiz question about Python
        2. One correct answer to the question
        3. Three incorrect but plausible answers
        4. A brief explanation of why the correct answer is correct
        5. A difficulty level (easy, medium, or hard)
        
        Format your response as JSON:
        {{
            "question": "The question text",
            "correct_answer": "The correct answer",
            "incorrect_answers": ["Wrong answer 1", "Wrong answer 2", "Wrong answer 3"],
            "explanation": "Why the correct answer is correct",
            "difficulty": "medium"
        }}
        """
        
        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            # Process the response to extract JSON
            response_text = response.choices[0].text.strip()
            question_data = json.loads(response_text)
            return question_data
        except Exception as e:
            self.stderr.write(f"Error generating question with API: {e}")
            return self.mock_generate_question(topic_name)

    def mock_generate_question(self, topic_name):
        """Generate a mock question when API is not available"""
        # Extended list of mock questions for variety
        questions = [
            {
                "question": "What is the output of print(type(1/2)) in Python 3?",
                "correct_answer": "<class 'float'>",
                "incorrect_answers": ["<class 'int'>", "<class 'fraction'>", "<class 'double'>"],
                "explanation": "In Python 3, division of integers results in a float.",
                "difficulty": "medium"
            },
            {
                "question": "Which method is used to add an element to the end of a list?",
                "correct_answer": "append()",
                "incorrect_answers": ["push()", "add()", "insert()"],
                "explanation": "The append() method adds an element to the end of a list.",
                "difficulty": "easy"
            },
            {
                "question": "What does the 'self' parameter in a class method represent?",
                "correct_answer": "The instance of the class",
                "incorrect_answers": ["The class itself", "The parent class", "The method itself"],
                "explanation": "In class methods, 'self' refers to the instance of the class that called the method.",
                "difficulty": "medium"
            },
            {
                "question": "How do you create a virtual environment in Python?",
                "correct_answer": "python -m venv myenv",
                "incorrect_answers": ["pip install virtualenv", "python create venv", "virtualenv --create"],
                "explanation": "The command 'python -m venv myenv' creates a virtual environment named 'myenv'.",
                "difficulty": "medium"
            },
            {
                "question": "What is the purpose of the __init__ method in Python classes?",
                "correct_answer": "To initialize object attributes",
                "incorrect_answers": ["To create a new class", "To delete an object", "To import modules"],
                "explanation": "The __init__ method is called when an object is created and is used to initialize attributes.",
                "difficulty": "easy"
            },
            {
                "question": "Which of the following is not a built-in data type in Python?",
                "correct_answer": "Array",
                "incorrect_answers": ["List", "Dictionary", "Tuple"],
                "explanation": "Arrays are not built-in data types in Python. They're available through the NumPy library.",
                "difficulty": "medium"
            },
            {
                "question": "What does the 'yield' keyword do in Python?",
                "correct_answer": "It returns a generator",
                "incorrect_answers": ["It stops the function execution", "It imports a module", "It defines a class"],
                "explanation": "The yield keyword turns a function into a generator that returns values one at a time.",
                "difficulty": "hard"
            }
        ]
        return random.choice(questions)

    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        topic_name = options['topic']
        question_count = options['count']
        api_key = options.get('api_key')
        batch_size = options['batch_size']
        
        # Check if file exists
        if not os.path.isfile(pdf_path):
            self.stderr.write(f"File not found: {pdf_path}")
            return
            
        # Get or create topic
        topic, created = Topic.objects.get_or_create(
            name=topic_name,
            defaults={
                'description': f"Questions about {topic_name}",
                'slug': slugify(topic_name)
            }
        )
        
        if created:
            self.stdout.write(f"Created new topic: {topic_name}")
        else:
            self.stdout.write(f"Using existing topic: {topic_name}")
        
        # Check existing questions for this topic
        existing_count = Question.objects.filter(topic=topic).count()
        if existing_count > 0:
            self.stdout.write(f"Topic already has {existing_count} questions.")
            if existing_count >= question_count:
                self.stdout.write(f"Already have {existing_count} questions, which meets or exceeds target of {question_count}.")
                return
            else:
                question_count = question_count - existing_count
                self.stdout.write(f"Will generate {question_count} additional questions.")
            
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            self.stderr.write("Failed to extract text from PDF")
            return
            
        self.stdout.write(f"Extracted {len(text)} characters from PDF")
        
        # Chunk the text
        chunks = self.chunk_text(text)
        self.stdout.write(f"Divided text into {len(chunks)} chunks")
        
        # Generate questions
        questions_generated = 0
        chunk_index = 0
        
        # Warn about time
        estimated_time = question_count * 3  # Assuming ~3 seconds per question
        self.stdout.write(f"Generating {question_count} questions. This may take approximately {estimated_time} seconds.")
        
        while questions_generated < question_count:
            batch_questions = min(batch_size, question_count - questions_generated)
            self.stdout.write(f"Generating batch of {batch_questions} questions...")
            
            for i in range(batch_questions):
                if chunk_index >= len(chunks):
                    chunk_index = 0
                    
                chunk = chunks[chunk_index]
                
                # Generate a question from this chunk
                try:
                    question_data = self.generate_question_from_text(chunk, topic_name, api_key)
                    
                    # Create question in database
                    question = Question.objects.create(
                        topic=topic,
                        text=question_data["question"],
                        explanation=question_data["explanation"],
                        difficulty=question_data.get("difficulty", "medium")
                    )
                    
                    # Create correct answer
                    Answer.objects.create(
                        question=question,
                        text=question_data["correct_answer"],
                        is_correct=True
                    )
                    
                    # Create incorrect answers
                    for wrong_answer in question_data["incorrect_answers"]:
                        Answer.objects.create(
                            question=question,
                            text=wrong_answer,
                            is_correct=False
                        )
                    
                    questions_generated += 1
                    
                except Exception as e:
                    self.stderr.write(f"Error processing chunk {chunk_index}: {e}")
                
                chunk_index += 1
            
            self.stdout.write(f"Generated {questions_generated}/{question_count} questions")
            # Add a small delay between batches if using API to avoid rate limits
            if api_key and questions_generated < question_count:
                time.sleep(1)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {questions_generated} questions for topic '{topic_name}'"))
        self.stdout.write(self.style.SUCCESS(f"Total questions for topic: {existing_count + questions_generated}"))
