from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""
    
    class Meta:
        model = Document
        fields = ['title', 'file', 'topic', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
        }