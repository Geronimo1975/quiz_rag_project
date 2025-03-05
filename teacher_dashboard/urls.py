# teacher_dashboard/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'teacher_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_document, name='upload_document'),
    path('generate/', views.generate_quiz, name='generate_quiz'),
    path('document/<int:document_id>/', views.view_document, name='view_document'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('topics/', views.manage_topics, name='manage_topics'),
    path('quizzes/', views.manage_quizzes, name='manage_quizzes'),
    path('quiz/<int:session_id>/analysis/', views.quiz_analysis, name='quiz_analysis'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)