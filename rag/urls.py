from django.urls import path
from . import views

app_name = 'rag'  # This namespace is important!

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('upload/', views.upload_document, name='upload_document'),
    path('generate/', views.generate_quiz, name='generate_quiz'),
    # Add any other paths you need
]
