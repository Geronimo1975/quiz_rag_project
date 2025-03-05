# teacher_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.management import call_command
from django.conf import settings
from django.db import models
import os

from .forms import DocumentUploadForm, QuizGenerationForm
from rag.models import Document
from quiz.models import Topic, Question, Answer, QuizSession, QuizResponse
from django.contrib.auth.models import User
from quiz_project.utils import is_teacher
from rag.services.quiz_generator import generate_rag_quiz

@login_required
@user_passes_test(is_teacher)
def dashboard(request):
    """Teacher dashboard home page"""
    # Get statistics
    documents = Document.objects.all().order_by('-uploaded_at')
    topics = Topic.objects.all()
    
    # Count questions per topic
    topic_stats = []
    for topic in topics:
        questions_count = Question.objects.filter(topic=topic).count()
        # Get quiz sessions for this topic
        sessions_count = QuizSession.objects.filter(topic=topic).count()
        avg_score = QuizSession.objects.filter(topic=topic, score__isnull=False).values_list('score', flat=True).aggregate(avg=models.Avg('score'))
        
        topic_stats.append({
            'topic': topic,
            'questions': questions_count,
            'sessions': sessions_count,
            'avg_score': avg_score['avg'] if avg_score['avg'] is not None else 0,
        })
    
    # Calculate overall stats
    total_questions = Question.objects.count()
    total_answers = Answer.objects.count()
    
    # Recent quiz activity
    recent_sessions = QuizSession.objects.all().order_by('-start_time')[:5]
    
    return render(request, 'teacher_dashboard/dashboard.html', {
        'documents': documents,
        'topic_stats': topic_stats,
        'total_documents': documents.count(),
        'total_questions': total_questions,
        'total_answers': total_answers,
        'recent_sessions': recent_sessions,
        'active_topics': topics.count(),
    })

@login_required
@user_passes_test(is_teacher)
def upload_document(request):
    """Upload a new document"""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, f"Document '{document.title}' uploaded successfully.")
            return redirect('teacher_dashboard:dashboard')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'teacher_dashboard/upload_document.html', {
        'form': form,
    })

@login_required
@user_passes_test(is_teacher)
def generate_quiz(request):
    if request.method == 'POST':
        form = QuizGenerationForm(request.POST)
        if form.is_valid():
            document = form.cleaned_data['document']
            topic_name = form.cleaned_data['topic_name']
            question_count = form.cleaned_data['question_count']
            
            try:
                # Generate quiz using RAG
                question_count, topic = generate_rag_quiz(
                    document=document,
                    topic_name=topic_name,
                    question_count=question_count
                )
                
                messages.success(
                    request, 
                    f"Successfully generated {question_count} questions for topic '{topic.name}'"
                )
                return redirect('quiz:topic_detail', topic_id=topic.id)
            except Exception as e:
                messages.error(request, f"Error generating questions: {str(e)}")
    else:
        form = QuizGenerationForm()
    
    return render(request, 'teacher_dashboard/generate_quiz.html', {'form': form})

@login_required
@user_passes_test(is_teacher)
def view_document(request, document_id):
    """View a document's details and related questions"""
    document = get_object_or_404(Document, id=document_id)
    
    # Get questions from topics that match this document
    topic, created = Topic.objects.get_or_create(name=document.topic)
    questions = Question.objects.filter(topic=topic)
    
    # Get quiz sessions that used this topic
    sessions = QuizSession.objects.filter(topic=topic).order_by('-start_time')
    
    # Get distribution of difficulty (assuming questions have a difficulty field)
    difficulty_stats = {}
    for question in questions:
        difficulty = getattr(question, 'difficulty', 'medium')  # Default to medium if not present
        difficulty_stats[difficulty] = difficulty_stats.get(difficulty, 0) + 1
    
    # Sample questions for preview
    sample_questions = questions.order_by('?')[:5]  # Random 5 questions
    
    return render(request, 'teacher_dashboard/view_document.html', {
        'document': document,
        'topic': topic,
        'questions': questions,
        'questions_count': questions.count(),
        'sessions': sessions,
        'sessions_count': sessions.count(),
        'difficulty_stats': difficulty_stats,
        'sample_questions': sample_questions,
    })

@login_required
@user_passes_test(is_teacher)
def edit_question(request, question_id):
    """Edit an existing question"""
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        # Get form data
        text = request.POST.get('question_text')
        explanation = request.POST.get('explanation')
        
        # Update question
        question.text = text
        question.explanation = explanation
        question.save()
        
        # Process answers
        for answer in question.answers.all():
            answer_id = str(answer.id)
            answer_text = request.POST.get(f'answer_text_{answer_id}')
            is_correct = request.POST.get(f'is_correct') == answer_id
            
            if answer_text:
                answer.text = answer_text
                answer.is_correct = is_correct
                answer.save()
        
        messages.success(request, "Question updated successfully!")
        return redirect('teacher_dashboard:view_document', document_id=question.topic.document_set.first().id)
    
    # Get all answers for this question
    answers = question.answers.all()
    
    return render(request, 'teacher_dashboard/edit_question.html', {
        'question': question,
        'answers': answers,
    })

@login_required
@user_passes_test(is_teacher)
def manage_topics(request):
    """Manage quiz topics"""
    # Handle topic creation
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            topic, created = Topic.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            
            if created:
                messages.success(request, f"Topic '{name}' created successfully!")
            else:
                messages.warning(request, f"Topic '{name}' already exists.")
        
        # Check for delete action
        delete_id = request.POST.get('delete_topic')
        if delete_id:
            try:
                topic = Topic.objects.get(id=delete_id)
                name = topic.name
                topic.delete()
                messages.success(request, f"Topic '{name}' deleted successfully!")
            except Topic.DoesNotExist:
                messages.error(request, "Topic not found!")
    
    # Get all topics with stats
    topics = Topic.objects.all().order_by('name')
    topic_stats = []
    
    for topic in topics:
        questions_count = Question.objects.filter(topic=topic).count()
        sessions_count = QuizSession.objects.filter(topic=topic).count()
        
        topic_stats.append({
            'topic': topic,
            'questions': questions_count,
            'sessions': sessions_count,
        })
    
    return render(request, 'teacher_dashboard/manage_topics.html', {
        'topic_stats': topic_stats,
    })

@login_required
@user_passes_test(is_teacher)
def manage_quizzes(request):
    """View and manage student quiz sessions"""
    # Get filtering parameters
    topic_id = request.GET.get('topic')
    user_id = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset
    sessions = QuizSession.objects.all().order_by('-start_time')
    
    # Apply filters
    if topic_id:
        sessions = sessions.filter(topic_id=topic_id)
    if user_id:
        sessions = sessions.filter(user_id=user_id)
    if date_from:
        sessions = sessions.filter(start_time__gte=date_from)
    if date_to:
        sessions = sessions.filter(start_time__lte=date_to)
    
    # Get unique users and topics for filters
    users = User.objects.filter(quiz_sessions__isnull=False).distinct()
    topics = Topic.objects.filter(quizsession__isnull=False).distinct()
    
    # Calculate overall stats
    total_sessions = sessions.count()
    completed_sessions = sessions.filter(end_time__isnull=False).count()
    avg_score = sessions.filter(score__isnull=False).aggregate(avg=models.Avg('score'))
    
    return render(request, 'teacher_dashboard/manage_quizzes.html', {
        'sessions': sessions[:50],  # Limit to 50 latest sessions
        'users': users,
        'topics': topics,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'avg_score': avg_score['avg'] if avg_score['avg'] is not None else 0,
        'selected_topic': topic_id,
        'selected_user': user_id,
    })

@login_required
@user_passes_test(is_teacher)
def quiz_analysis(request, session_id):
    """Detailed analysis of a quiz session"""
    session = get_object_or_404(QuizSession, id=session_id)
    responses = QuizResponse.objects.filter(session=session).order_by('question__id')
    
    # Calculate stats
    total = responses.count()
    correct = responses.filter(is_correct=True).count()
    incorrect = total - correct
    score = session.score if session.score is not None else 0
    
    # Time spent
    time_spent = None
    if session.end_time and session.start_time:
        time_spent = (session.end_time - session.start_time).total_seconds()
        
    return render(request, 'teacher_dashboard/quiz_analysis.html', {
        'session': session,
        'responses': responses,
        'total': total,
        'correct': correct,
        'incorrect': incorrect,
        'score': score,
        'time_spent': time_spent,
    })
