from enum import Enum

from django.db import models

from accounts.models import CustomUser
from companies.models import Company


class InvitationStatus(Enum):
    INVITED = 'invited'
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELED = 'canceled'

class CompanyInvitation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(choices=[(status.value, status.name) for status in InvitationStatus])
    
    def __str__(self):
        return f"Invitation from {self.company} to {self.invited_user}"
    
    class Meta:
        verbose_name_plural = "CompanyInvites"
