from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from quiz.models import Topic, Question, Answer
import random

class Command(BaseCommand):
    help = 'Creates sample quiz topics and questions'

    def handle(self, *args, **options):
        # Sample quiz topics
        topics = [
            {
                'name': 'Python Basics',
                'description': 'Fundamental concepts of Python programming language.'
            },
            {
                'name': 'Web Development',
                'description': 'HTML, CSS, JavaScript, and web frameworks.'
            },
            {
                'name': 'Data Science',
                'description': 'Data analysis, visualization, and machine learning.'
            },
            {
                'name': 'DevOps',
                'description': 'Continuous integration, deployment, and infrastructure.'
            },
        ]
        
        # Create topics
        created_topics = []
        for topic_data in topics:
            # Add a slug field based on the name
            topic_slug = slugify(topic_data['name'])
            
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults={
                    'description': topic_data['description'],
                    'slug': topic_slug
                }
            )
            created_topics.append(topic)
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f"{status}: {topic.name}")
        
        # Sample questions for each topic
        for topic in created_topics:
            if topic.name == 'Python Basics':
                questions = [
                    {
                        'text': 'What is the purpose of the "if __name__ == \'__main__\'" statement in Python?',
                        'explanation': 'This statement is used to check whether a Python script is being run directly or imported as a module.',
                        'difficulty': 'medium',
                        'answers': [
                            {'text': 'To check if the script is being run directly', 'is_correct': True},
                            {'text': 'To check if the script has a main function', 'is_correct': False},
                            {'text': 'To define the main function in Python', 'is_correct': False},
                            {'text': 'To import the main module', 'is_correct': False},
                        ]
                    },
                    {
                        'text': 'What is the difference between a list and a tuple in Python?',
                        'explanation': 'Lists are mutable (can be changed), while tuples are immutable (cannot be changed after creation).',
                        'difficulty': 'easy',
                        'answers': [
                            {'text': 'Lists are mutable, tuples are immutable', 'is_correct': True},
                            {'text': 'Lists can contain strings, tuples can only contain numbers', 'is_correct': False},
                            {'text': 'Lists use square brackets, tuples use parentheses', 'is_correct': False},
                            {'text': 'Lists are faster than tuples', 'is_correct': False},
                        ]
                    },
                    {
                        'text': 'What is a decorator in Python?',
                        'explanation': 'A decorator is a function that takes another function as input and extends its behavior without explicitly modifying it.',
                        'difficulty': 'hard',
                        'answers': [
                            {'text': 'A function that adds functionality to another function', 'is_correct': True},
                            {'text': 'A type of comment used to document code', 'is_correct': False},
                            {'text': 'A design pattern for creating classes', 'is_correct': False},
                            {'text': 'A special import statement', 'is_correct': False},
                        ]
                    },
                ]
            elif topic.name == 'Web Development':
                questions = [
                    {
                        'text': 'What is the purpose of CSS in web development?',
                        'explanation': 'CSS (Cascading Style Sheets) is used to style and layout web pages.',
                        'difficulty': 'easy',
                        'answers': [
                            {'text': 'To style and layout web pages', 'is_correct': True},
                            {'text': 'To create interactive web pages', 'is_correct': False},
                            {'text': 'To define the structure of web pages', 'is_correct': False},
                            {'text': 'To create server-side logic', 'is_correct': False},
                        ]
                    },
                    {
                        'text': 'What is a RESTful API?',
                        'explanation': 'REST (Representational State Transfer) is an architectural style for designing networked applications. RESTful APIs use HTTP methods explicitly and are stateless.',
                        'difficulty': 'medium',
                        'answers': [
                            {'text': 'An architectural style for designing networked applications', 'is_correct': True},
                            {'text': 'A programming language for web development', 'is_correct': False},
                            {'text': 'A database management system', 'is_correct': False},
                            {'text': 'A JavaScript framework', 'is_correct': False},
                        ]
                    },
                ]
            else:
                # Generate some generic questions for other topics
                questions = [
                    {
                        'text': f'What is the most important concept in {topic.name}?',
                        'explanation': 'This is a sample explanation for this question.',
                        'difficulty': 'medium',
                        'answers': [
                            {'text': f'Understanding the fundamentals of {topic.name}', 'is_correct': True},
                            {'text': f'Advanced techniques in {topic.name}', 'is_correct': False},
                            {'text': f'Theoretical knowledge of {topic.name}', 'is_correct': False},
                            {'text': f'Historical development of {topic.name}', 'is_correct': False},
                        ]
                    },
                    {
                        'text': f'Which tool is most commonly used in {topic.name}?',
                        'explanation': 'Different tools are used for different purposes in this field.',
                        'difficulty': 'easy',
                        'answers': [
                            {'text': f'The most popular framework for {topic.name}', 'is_correct': True},
                            {'text': f'A legacy system that is outdated', 'is_correct': False},
                            {'text': f'An experimental tool not widely adopted', 'is_correct': False},
                            {'text': f'A proprietary solution that is expensive', 'is_correct': False},
                        ]
                    },
                ]
            
            # Create questions and answers
            for q_data in questions:
                question, created = Question.objects.get_or_create(
                    topic=topic,
                    text=q_data['text'],
                    defaults={
                        'explanation': q_data['explanation'],
                        'difficulty': q_data['difficulty'],
                    }
                )
                
                if created:
                    # Create answers - NEW RANDOMIZED APPROACH
                    all_answers = []
                    # Add correct answer
                    all_answers.append({
                        'text': q_data['answers'][0]['text'],
                        'is_correct': True
                    })
                    
                    # Add incorrect answers
                    for a_data in q_data['answers'][1:]:
                        all_answers.append({
                            'text': a_data['text'],
                            'is_correct': False
                        })
                    
                    # Shuffle the answers before creating them
                    random.shuffle(all_answers)
                    
                    # Create the answers in random order
                    for answer_data in all_answers:
                        Answer.objects.create(
                            question=question,
                            text=answer_data['text'],
                            is_correct=answer_data['is_correct']
                        )
                    
                    self.stdout.write(f"Created question: {question.text[:30]}...")
                else:
                    self.stdout.write(f"Question already exists: {question.text[:30]}...")
        
        self.stdout.write(self.style.SUCCESS("Successfully created sample quiz data"))
