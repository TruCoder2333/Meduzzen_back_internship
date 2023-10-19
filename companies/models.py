from django.db import models
from accounts.models import CustomUser
from core.models import TimeStampedModel

class Company(TimeStampedModel):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name