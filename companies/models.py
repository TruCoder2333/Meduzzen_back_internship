from django.db import models

from accounts.models import CustomUser
from core.models import TimeStampedModel


class Company(TimeStampedModel):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    members = models.ManyToManyField(
        'accounts.CustomUser', 
        related_name='members_company', 
        related_query_name='member_company', 
        blank=True
        )
    administrators = models.ManyToManyField(
        'accounts.CustomUser', 
        related_name='administrator_companies', 
        related_query_name='administrator_company',
        blank=True,
        )

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.administrators.add(self.owner)  # Add the owner as an administrator when the company is saved

    class Meta:
        verbose_name_plural = "Companies"



 