from django.db import models

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
