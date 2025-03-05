<<<<<<< HEAD
Setting Up Python Quiz with Django, RAG, OpenAI, and PostgreSQL
Let's build this step-by-step. I'll provide terminal commands and explanations for each stage.

Step 1: Create project directory and virtual environment

´´´

bash -
### Create project directory
mkdir quiz_rag_project
cd quiz_rag_project

´´´
### Create and activate virtual environment


bash


´´´

python -m venv venv
source venv/bin/activate

´´´
### Install Django and initial dependencies
pip install django psycopg2-binary python-dotenv


´´´





quiz_project/
├── manage.py
├── quiz_project/                 # Project settings
│   ├── __init__.py
│   ├── settings.py               # Database and app configuration
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py
│   └── wsgi.py
├── accounts/                     # User authentication app
│   ├── __init__.py
│   ├── models.py                 # Extended User model
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── quiz/                         # Quiz functionality app
│   ├── __init__.py
│   ├── models.py                 # Question/Answer/Result models
│   ├── views.py                  # Quiz presentation logic
│   ├── urls.py
│   ├── templates/
│   └── utils/                    # Quiz scoring, analysis
├── rag/                          # RAG system app
│   ├── __init__.py
│   ├── models.py                 # Document storage models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_loader.py    # PDF processing
│   │   ├── embeddings.py         # Vector embeddings
│   │   └── question_generator.py # Question generation
├── static/
├── media/                        # For PDF storage
├── templates/                    # Base templates
└── requirements.txt




Step 2: Set up Django project

# Start Django project
django-admin startproject quiz_project .

# Create apps for different components
python manage.py startapp accounts
python manage.py startapp quiz
python manage.py startapp rag

# Install RAG and OpenAI dependencies
pip install openai langchain langchain_openai pypdf tiktoken


Step 3: Configure PostgreSQL
First, ensure PostgreSQL is installed and running:


# Install PostgreSQL if needed (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE quiz_db;"
sudo -u postgres psql -c "CREATE USER quizuser WITH PASSWORD 'quizpassword';"
sudo -u postgres psql -c "ALTER ROLE quizuser SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE quizuser SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE quizuser SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE quiz_db TO quizuser;"



Step 4: Configure Django settings
Let's update the Django settings file:

Step 5: Create .env file for environment variables


SECRET_KEY=your_django_secret_key_here
DEBUG=True
DB_NAME=quiz_db
DB_USER=quizuser
DB_PASSWORD=quizpassword
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your_openai_api_key_here

Step 6: Create requirements.txt

pip freeze > requirements.txt


Now create a superuser and start the development server:

```bash
python manage.py createsuperuser
python manage.py runserver
```

 Progress tracking:
   - Add progress bar on quiz questions
   - Store quiz results in user profiles
   - Create learning progress visualization

 Timer for each question:
   - Add JavaScript countdown timer
   - Auto-submit when time runs out

 Interactive answer selection:
   - Make answers clickable without needing radio buttons
   - Highlight selected answers

 Detailed results at the end:
   - Show score with visual feedback
   - Display personalized feedback based on score
   - List correct/incorrect answers

 Question review:
   - Show explanation for each question
   - Highlight correct and incorrect answers
   - Provide additional learning resources

