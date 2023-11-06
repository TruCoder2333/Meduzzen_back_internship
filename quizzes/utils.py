import json

from django.conf import settings

from .models import QuizAttempt


def get_current_quiz_attempt(user, quiz):
        try:
            current_attempt = QuizAttempt.objects.get(user=user, quiz=quiz)
            return current_attempt
        except QuizAttempt.DoesNotExist:
            new_attempt = QuizAttempt(user=user, quiz=quiz)
            new_attempt.save()
            return new_attempt

def save_user_answer_to_redis(user_id, quiz_id, question_id, answer, is_correct, company_id):
    key = f'user_answer:{user_id}:{quiz_id}:{question_id}'

    user_answer_data = {
        'user_id': user_id,
        'quiz_id': quiz_id,
        'question_id': question_id,
        'answer': answer,
        'is_correct': is_correct,
        'company_id': company_id
    }

    user_answer_json = json.dumps(user_answer_data)

    ttl = 48 * 3600 
    settings.REDIS_CONNECTION.setex(key, ttl, user_answer_json)

def get_user_answer_from_redis(user_id, quiz_id, question_id):
    key = f'user_answer:{user_id}:{quiz_id}:{question_id}'
    user_answer_json = settings.REDIS_CONNECTION.get(key)

    if user_answer_json:
        user_answer_data = json.loads(user_answer_json)
        return user_answer_data
    else:
        return None