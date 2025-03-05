from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    topic = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_number = models.IntegerField()
    content = models.TextField()
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_number}"

class GeneratedQuestion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(default="Generated question")  # Add default
    answer = models.TextField(default="Generated answer")  # Add default
    alternatives = models.JSONField(default=list)  # Store incorrect answers
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Question from {self.document.title}"
