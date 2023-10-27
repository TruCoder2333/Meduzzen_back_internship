from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel


class CustomUser(AbstractUser, TimeStampedModel):
   avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
   additional_info = models.TextField(blank=True, null=True)
   companies = models.ManyToManyField(
      'companies.Company', 
      related_name='companies_member', 
      related_query_name='company_member', 
      blank=True
      )
   administered_companies = models.ManyToManyField(
      'companies.Company', 
      related_name='company_administrators', 
      related_query_name='company_administrator', 
      blank=True
      )

