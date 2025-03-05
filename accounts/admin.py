from django.contrib import admin
from .models import UserProfile, LearningProgress

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'preferred_topics')
    search_fields = ('user__username', 'preferred_topics')

@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'proficiency_level', 'last_updated')
    list_filter = ('topic', 'last_updated')
    search_fields = ('user__username', 'topic')
