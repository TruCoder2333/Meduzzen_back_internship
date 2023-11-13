from enum import Enum

from django.db import models

from accounts.models import CustomUser


class NotificationStatus(Enum):
    UNREAD = 'unread'
    READ = 'read'

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[(status.value, status.name) for status in NotificationStatus])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_as_read(self):
        self.status = NotificationStatus.READ.value
        self.save()

    class Meta:
        ordering = ['-created_at']

