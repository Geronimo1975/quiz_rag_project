from django.contrib import admin
from .models import Topic, Question, Answer, QuizSession, QuizResponse

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'difficulty')
    list_filter = ('topic', 'difficulty')
    search_fields = ('text',)
    inlines = [AnswerInline]

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'start_time', 'end_time', 'score')
    list_filter = ('topic', 'start_time')
    search_fields = ('user__username',)

@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)
