from .models import QuizAttempt


def get_current_quiz_attempt(user, quiz):
        try:
            current_attempt = QuizAttempt.objects.get(user=user, quiz=quiz)
            return current_attempt
        except QuizAttempt.DoesNotExist:
            new_attempt = QuizAttempt(user=user, quiz=quiz)
            new_attempt.save()
            return new_attempt