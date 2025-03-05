# teacher_dashboard/forms.py
from django import forms
from rag.models import Document
from quiz.models import Topic

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading new documents"""
    
    class Meta:
        model = Document
        fields = ['title', 'file', 'topic', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class QuizGenerationForm(forms.Form):
    """Form for generating quiz questions from documents"""
    
    document = forms.ModelChoiceField(
        queryset=Document.objects.all().order_by('-uploaded_at'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the document to generate questions from"
    )
    
    topic_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the topic name for these questions"
    )
    
    question_count = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=20,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="How many questions to generate"
    )
    
    use_openai = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Use OpenAI for better quality questions"
    )

# teacher_dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .forms import DocumentUploadForm, QuizGenerationForm  # Import from forms, not models
from rag.models import Document
from quiz.models import Topic, Question, Answer

# Rest of your view code...