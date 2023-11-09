import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUser
from companies.models import Company
from core.models import TimeStampedModel
from notifications.models import Notification, NotificationStatus


class Quiz(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    frequency_in_days = models.PositiveIntegerField()  
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  


    def __str__(self):
        return self.title

    
class Question(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text

class Answer(TimeStampedModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)

class QuizResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default=None)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.FloatField()
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.company_id and self.quiz:
            self.company = self.quiz.company

        super(QuizResult, self).save(*args, **kwargs)

class UserAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "User Answer"
        verbose_name_plural = "User Answers"

    def __str__(self):
        return f"User Answer for Question '{self.question}' in Quiz Attempt '{self.quiz_attempt}'"


@receiver(post_save, sender=Quiz)
def create_quiz_notifications(sender, instance, **kwargs):
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()

    # Get all users in the company
    company_users = instance.company.members.all()

    # Create notifications for each user
    for user in company_users:
        Notification.objects.create(
            user=user,
            status=NotificationStatus.UNREAD.value,
            text=f'New quiz "{instance.title}" is available. Take it now!',
        )

        message = json.dumps({'type': 'notification', 'message': 'New quiz available!'})
        async_to_sync(channel_layer.group_add)(f'user_{user.id}', f'notification_group_{user.id}')
        async_to_sync(channel_layer.group_send)(f'user_{user.id}', {'type': 'send_notification', 'message': message})