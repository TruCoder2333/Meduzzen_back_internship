from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel


class CustomUser(AbstractUser, TimeStampedModel):
   pass
