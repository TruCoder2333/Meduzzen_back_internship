from django.db import models

from accounts.models import CustomUser
from companies.models import Company
from core.models import TimeStampedModel


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
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.FloatField()

class UserAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "User Answer"
        verbose_name_plural = "User Answers"

    def __str__(self):
        return f"User Answer for Question '{self.question}' in Quiz Attempt '{self.quiz_attempt}'"