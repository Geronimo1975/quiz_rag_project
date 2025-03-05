from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required

from quiz_project.db.services.user_service import UserService
from .forms import RegisterForm
from quiz_project.utils import is_teacher

# Initialize services
user_service = UserService()

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('quiz:topic_list')
        else:
            messages.error(request, 'Registration failed. Please correct the errors.')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    form = AuthenticationForm()
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'quiz:topic_list')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('quiz:topic_list')

@login_required
def profile(request):
    if request.method == 'POST':
        # Update profile information
        bio = request.POST.get('bio', '')
        preferred_topics = request.POST.get('preferred_topics', '')
        
        user_service.update_user_profile(
            user_id=request.user.id, 
            bio=bio, 
            preferred_topics=preferred_topics
        )
        
        messages.success(request, 'Your profile has been updated!')
        return redirect('accounts:profile')
    
    # Get profile data
    profile_data = user_service.get_user_profile(request.user.id)
        
    return render(request, 'accounts/profile.html', {'profile': profile_data})

@login_required
def learning_progress(request):
    # Get learning progress for the current user
    progress = user_service.get_learning_progress(request.user.id)
    
    return render(request, 'accounts/progress.html', {'progress': progress})

@login_required
def progress_view(request):
    """View for displaying user's learning progress"""
    # Get user's quiz sessions
    user_sessions = request.user.quiz_sessions.all().order_by('-start_time')
    
    # Group by topic
    topics = {}
    for session in user_sessions:
        if session.topic.id not in topics:
            topics[session.topic.id] = {
                'topic': session.topic,
                'sessions': [],
                'average_score': 0,
                'best_score': 0,
                'total_questions': 0,
                'correct_answers': 0
            }
        
        topics[session.topic.id]['sessions'].append(session)
        
        # Update stats if the session has a score
        if session.score is not None:
            if session.score > topics[session.topic.id]['best_score']:
                topics[session.topic.id]['best_score'] = session.score
            
            # Get correct answers
            correct_count = session.responses.filter(is_correct=True).count()
            total_count = session.responses.count()
            
            topics[session.topic.id]['correct_answers'] += correct_count
            topics[session.topic.id]['total_questions'] += total_count
    
    # Calculate averages
    for topic_id, data in topics.items():
        if data['total_questions'] > 0:
            data['average_score'] = (data['correct_answers'] / data['total_questions']) * 100
    
    return render(request, 'accounts/progress.html', {
        'topics': list(topics.values())
    })
