from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from accounts.models import CustomUser
from notifications.utils import send_notification_to_user

from .models import Quiz, QuizResult


@shared_task
def check_last_test_dates():
    users = CustomUser.objects.all()

    for user in users:
        quizzes = Quiz.objects.filter(company=user.company)
        for quiz in quizzes:
            last_test = QuizResult.objects.filter(user=user, quiz=quiz).order_by('-timestamp').first()
            if last_test:
                time_since_last_test = timezone.now() - last_test.timestamp
                if time_since_last_test > timedelta(days=1):  
                    send_notification_to_user(user, quiz)



