from django.contrib import admin
from .models import Document, DocumentChunk, GeneratedQuestion

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'uploaded_at', 'is_processed']
    search_fields = ['title', 'topic', 'description']
    list_filter = ['uploaded_at', 'topic', 'is_processed']

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_number']
    list_filter = ['document']

@admin.register(GeneratedQuestion)
class GeneratedQuestionAdmin(admin.ModelAdmin):
    list_display = ['document', 'text', 'created_at']
    list_filter = ['document', 'created_at']
    search_fields = ['text', 'answer']
