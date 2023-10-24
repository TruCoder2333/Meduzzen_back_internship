from django.db import models
from accounts.models import CustomUser
from companies.models import Company

class CompanyInvitation(models.Model):
    INVITED = 'invited'
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    CANCELED = 'canceled'
    
    INVITATION_STATUS_CHOICES = (
        (INVITED, 'invited'),
        (REQUESTED, 'requested'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (CANCELED, 'Canceled')
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=INVITATION_STATUS_CHOICES)
    
    def __str__(self):
        return f"Invitation from {self.company} to {self.invited_user}"
    
    class Meta:
        verbose_name_plural = "CompanyInvites"
