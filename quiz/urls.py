from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('topic/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('topic/<slug:slug>/start/', views.start_quiz, name='start_quiz'),
    path('session/<int:session_id>/question/<int:question_index>/', views.quiz_question, name='quiz_question'),
    path('session/<int:session_id>/result/', views.quiz_result, name='quiz_result'),
    path('history/', views.quiz_history, name='quiz_history'),
]
