from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    preferred_topics = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of topics")
    
    def __str__(self):
        return f"Profile for {self.user.username}"

class LearningProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_progress')
    topic = models.CharField(max_length=100)
    proficiency_level = models.FloatField(default=0)  # 0-100%
    weak_areas = models.TextField(blank=True)  # Comma-separated list of weak concepts
    strong_areas = models.TextField(blank=True)  # Comma-separated list of strong concepts
    last_updated = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'topic')
    
    def __str__(self):
        return f"{self.user.username}'s progress in {self.topic}: {self.proficiency_level}%"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for new users"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
