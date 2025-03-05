import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.utils import timezone
from .models import Topic, Question, Answer, QuizSession, QuizResponse
from django.db import models
from quiz_project.utils import is_teacher

def topic_list(request):
    """Display a list of all available quiz topics"""
    topics = Topic.objects.all()
    return render(request, 'quiz/topic_list.html', {'topics': topics})

def topic_detail(request, slug):
    """Display details about a specific topic"""
    try:
        if slug.isdigit():
            topic = get_object_or_404(Topic, id=int(slug))
        else:
            topic = get_object_or_404(Topic, slug=slug)
            
        # Check if topic is active
        if hasattr(topic, 'active') and not topic.active:
            return render(request, 'quiz/topic_inactive.html', {'topic': topic})
            
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")
        
    question_count = topic.questions.count()
    return render(request, 'quiz/topic_detail.html', {
        'topic': topic,
        'question_count': question_count
    })

@login_required
def start_quiz(request, slug):
    """Start a new quiz session with randomly selected questions"""
    try:
        if slug.isdigit():
            topic = get_object_or_404(Topic, id=int(slug))
        else:
            topic = get_object_or_404(Topic, slug=slug)
    except:
        raise Http404("Topic does not exist")
    
    # Get all questions for this topic
    all_questions = list(Question.objects.filter(topic=topic))
    
    if not all_questions:
        return render(request, 'quiz/no_questions.html', {'topic': topic})
    
    # Create a new quiz session
    session = QuizSession.objects.create(
        user=request.user,
        topic=topic
    )
    
    # Select up to 20 random questions
    questions_needed = min(20, len(all_questions))
    selected_questions = random.sample(all_questions, questions_needed)
    
    # Store the selected question IDs in the session
    request.session[f'quiz_{session.id}_questions'] = [q.id for q in selected_questions]
    
    # Redirect to the first question
    return redirect('quiz:quiz_question', session_id=session.id, question_index=0)

@login_required
def quiz_question(request, session_id, question_index):
    """Display a question and process answers"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    # Ensure the quiz isn't already completed
    if session.end_time:
        return redirect('quiz:quiz_result', session_id=session.id)
    
    # Get selected questions for this session
    question_ids = request.session.get(f'quiz_{session.id}_questions', [])
    if question_ids:
        questions = list(Question.objects.filter(id__in=question_ids))
    else:
        # Fallback to all questions
        questions = list(session.topic.questions.all())
    
    # Check if we've reached the end of the quiz
    if question_index >= len(questions):
        # Calculate score and mark as completed
        session.end_time = timezone.now()
        
        # Calculate score based on responses
        correct_answers = QuizResponse.objects.filter(
            session=session, is_correct=True
        ).count()
        
        total_questions = len(questions)
        if total_questions > 0:
            session.score = (correct_answers / total_questions) * 100
        else:
            session.score = 0
            
        session.save()
        
        return redirect('quiz:quiz_result', session_id=session.id)
    
    # Get the current question
    question = questions[question_index]
    
    # Make sure this section properly extracts the answer ID
    if request.method == 'POST':
        # Process the submitted answer
        answer_id = request.POST.get('answer')
        
        # Debug: Print the answer_id to check if we're getting it
        print(f"Received answer_id: {answer_id}")
        
        if answer_id:
            try:
                answer = get_object_or_404(Answer, id=answer_id, question=question)
                
                # Record response
                QuizResponse.objects.create(
                    session=session,
                    question=question,
                    selected_answer=answer,
                    is_correct=answer.is_correct
                )
                
                # Move to the next question
                return redirect('quiz:quiz_question', 
                              session_id=session.id, 
                              question_index=question_index + 1)
            except:
                # If there's an error with the answer, log it
                print(f"Error processing answer_id: {answer_id}")
                messages.error(request, "There was a problem with your answer. Please try again.")
        else:
            # If no answer was selected, show an error
            messages.error(request, "Please select an answer before continuing.")
    
    # Enhanced randomization of answers
    answers = list(question.answers.all())
    
    # Force randomization by creating a new list with random order
    random_order = list(range(len(answers)))
    random.shuffle(random_order)
    randomized_answers = [answers[i] for i in random_order]
    
    # Store original position for answer verification
    for i, answer in enumerate(randomized_answers):
        setattr(answer, 'original_position', random_order[i])
    
    # Calculate progress percentage
    progress_percentage = ((question_index + 1) / len(questions)) * 100
    
    # Set time limit for each question (1 minute per question)
    time_limit_per_question = 60  # seconds
    
    return render(request, 'quiz/quiz_question.html', {
        'session': session,
        'question': question,
        'answers': randomized_answers,  # Use the truly randomized list
        'question_index': question_index,
        'total_questions': len(questions),
        'progress_percentage': progress_percentage,
        'time_limit': time_limit_per_question
    })

@login_required
def quiz_result(request, session_id):
    """Display quiz results"""
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    # Get all responses for this session
    responses = session.responses.all().select_related('question', 'selected_answer')
    
    return render(request, 'quiz/quiz_result.html', {
        'session': session,
        'responses': responses,
        'score': session.score
    })

@login_required
def quiz_history(request):
    """Display user's quiz history"""
    sessions = QuizSession.objects.filter(
        user=request.user
    ).order_by('-start_time')
    
    return render(request, 'quiz/quiz_history.html', {'sessions': sessions})

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
        from quiz.models import QuizSession
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
    from quiz.models import QuizSession
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
        # Get quiz sessions for this topic
        from quiz.models import QuizSession
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
    from quiz.models import QuizSession, QuizResponse
    from django.contrib.auth.models import User
    
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
    from quiz.models import QuizSession, QuizResponse
    
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
