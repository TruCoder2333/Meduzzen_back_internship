from django.db import models
from core.models import TimeStampedModel
from django.conf import settings

User = settings.AUTH_USER_MODEL
class Logger(TimeStampedModel):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=20, default = 'INFO')
    message = models.TextField(default = "")


    def __str__(self):
        return f'{self.timestamp} - {self.level}: {self.message}'

    