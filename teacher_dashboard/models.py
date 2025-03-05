from django import forms
from rag.models import Document
from quiz.models import Topic

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'topic', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class QuizGenerationForm(forms.Form):
    document = forms.ModelChoiceField(
        queryset=Document.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    topic_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    question_count = forms.IntegerField(
        min_value=20,
        max_value=100,
        initial=20,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    use_openai = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Use OpenAI for better quality questions (requires API key)"
    )
    api_key = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Your OpenAI API key (only needed if 'Use OpenAI' is selected)"
    )

# teacher_dashboard/models.py
from django.db import models

# You can add any teacher_dashboard-specific models here if needed
# For example:
# class TeacherPreference(models.Model):
#     user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
#     default_question_count = models.IntegerField(default=20)
