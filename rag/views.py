from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from uuid import UUID

from quiz_project.db.services.rag_service import RAGService
from quiz_project.db.repositories.document_repository import DocumentRepository
from teacher_dashboard.forms import DocumentUploadForm
from .models import Document

# Initialize services
rag_service = RAGService()
document_repository = DocumentRepository()

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if 'file' not in request.FILES:
                    messages.error(request, "No file was uploaded.")
                    return render(request, 'rag/upload_document.html', {'form': form})
                
                uploaded_file = request.FILES['file']
                if not uploaded_file.name.endswith('.pdf'):
                    messages.error(request, "Only PDF files are allowed.")
                    return render(request, 'rag/upload_document.html', {'form': form})
                
                document = form.save()
                rag_service.process_document(document.id)
                messages.success(request, f"Document '{document.title}' uploaded and processed successfully.")
                return redirect('rag:document_list')
            except Exception as e:
                messages.error(request, f"Error during upload: {str(e)}")
                return render(request, 'rag/upload_document.html', {'form': form})
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DocumentUploadForm()
    
    return render(request, 'rag/upload_document.html', {'form': form})

@login_required
def document_list(request):
    """View to list all uploaded documents"""
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'rag/document_list.html', {'documents': documents})

@login_required
def generate_quiz(request):
    document_id = request.GET.get('document')
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        num_questions = int(request.POST.get('num_questions', 20))
        
        try:
            # Generate questions
            questions = rag_service.generate_questions(document.id, num_questions)
            
            messages.success(request, f"Generated {len(questions)} questions for quiz.")
            return redirect('quiz:topic_list')
        except Exception as e:
            messages.error(request, f"Error generating questions: {str(e)}")
    
    return render(request, 'rag/generate_quiz.html', {'document': document})

