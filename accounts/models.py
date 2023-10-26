from django.contrib.auth.models import AbstractUser
from core.models import TimeStampedModel
from django.db import models



class CustomUser(AbstractUser, TimeStampedModel):
   companies = models.ManyToManyField(
      'companies.Company', 
      related_name='companies_member', 
      related_query_name='company_member', 
      blank=True
      )

