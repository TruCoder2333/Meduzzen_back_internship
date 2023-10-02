from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class Logger(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    actions = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.action} by {self.user}" if self.user else self.action