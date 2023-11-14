from datetime import timedelta
from celery import shared_task
from django.utils import timezone

from accounts.models import CustomUser
from notifications.utils import send_notification_to_user

from .models import QuizResult


@shared_task
def check_and_notify_users():
    users = CustomUser.objects.prefetch_related('companies__quiz_set').all()

    for user in users:
        for company in user.companies.all():
            quizzes = company.quiz_set.all()
            for quiz in quizzes:
                last_test = QuizResult.objects.filter(user=user, quiz=quiz).order_by('-timestamp').first()
                if not last_test or timezone.now() - last_test.timestamp > timedelta(hours=24):
                    send_notification_to_user(user, quiz)



