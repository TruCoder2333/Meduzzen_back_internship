from django.db import models
from core.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser, TimeStampedModel):
   pass
