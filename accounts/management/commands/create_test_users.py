from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile, LearningProgress
import random

class Command(BaseCommand):
    help = 'Creates 5 test users with profiles and learning progress'

    def handle(self, *args, **options):
        # Test user data
        test_users = [
            {
                'username': 'student1',
                'email': 'student1@example.com',
                'password': 'testpass123',
                'first_name': 'Alex',
                'last_name': 'Schmidt',
                'bio': 'Computer Science student interested in AI and machine learning.',
                'preferred_topics': 'Python,Data Science,Machine Learning',
            },
            {
                'username': 'student2',
                'email': 'student2@example.com',
                'password': 'testpass123',
                'first_name': 'Mia',
                'last_name': 'Weber',
                'bio': 'Web developer focusing on frontend technologies.',
                'preferred_topics': 'JavaScript,HTML,CSS,React',
            },
            {
                'username': 'student3',
                'email': 'student3@example.com',
                'password': 'testpass123',
                'first_name': 'Jan',
                'last_name': 'Müller',
                'bio': 'Backend developer with experience in Django and Flask.',
                'preferred_topics': 'Python,Django,Databases',
            },
            {
                'username': 'student4',
                'email': 'student4@example.com',
                'password': 'testpass123',
                'first_name': 'Sophia',
                'last_name': 'Becker',
                'bio': 'Data analyst with focus on visualization tools.',
                'preferred_topics': 'Data Visualization,SQL,Statistics',
            },
            {
                'username': 'student5',
                'email': 'student5@example.com',
                'password': 'testpass123',
                'first_name': 'Lukas',
                'last_name': 'Hoffmann',
                'bio': 'DevOps engineer interested in containerization and CI/CD.',
                'preferred_topics': 'Docker,Kubernetes,CI/CD',
            },
        ]

        # Create topics for learning progress
        topics = [
            'Python Basics',
            'Advanced Python',
            'Web Development',
            'Data Science',
            'Machine Learning',
            'JavaScript',
            'Database Design',
            'DevOps',
        ]

        # Create users and associated data
        for user_data in test_users:
            # Check if user already exists
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(self.style.WARNING(f"User {user_data['username']} already exists. Skipping..."))
                continue

            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )

            # Update profile
            profile = UserProfile.objects.get(user=user)  # Profile is created via signal
            profile.bio = user_data['bio']
            profile.preferred_topics = user_data['preferred_topics']
            profile.save()

            # Create learning progress for 3 random topics
            selected_topics = random.sample(topics, 3)
            for topic in selected_topics:
                proficiency = random.uniform(30, 95)
                
                # Generate some meaningful weak/strong areas
                possible_areas = ['variables', 'functions', 'classes', 'algorithms', 'syntax', 
                                 'frameworks', 'memory management', 'concurrency', 'error handling', 
                                 'data types', 'testing', 'debugging']
                
                # Select random areas
                weak_count = random.randint(1, 3)
                strong_count = random.randint(1, 3)
                weak_areas = ', '.join(random.sample(possible_areas, weak_count))
                strong_areas = ', '.join(random.sample(possible_areas, strong_count))
                
                # Create progress record without topic_id field
                LearningProgress.objects.create(
                    user=user,
                    topic=topic,
                    proficiency_level=proficiency,
                    weak_areas=weak_areas,
                    strong_areas=strong_areas,
                    last_updated=timezone.now()
                )

            self.stdout.write(self.style.SUCCESS(f"Created user: {user.username} with profile and learning progress"))

        self.stdout.write(self.style.SUCCESS("Successfully created test users"))
