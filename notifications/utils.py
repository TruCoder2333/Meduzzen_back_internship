import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification, NotificationStatus


def send_notification_to_user(user, quiz, message_type='notification'):
    channel_layer = get_channel_layer()
    Notification.objects.create(
        user=user,
        status=NotificationStatus.UNREAD.value,
        text=f'An undone quiz "{quiz.title}" is available. Take it now!',
    )
    message = json.dumps({'type': message_type, 'message': f'New quiz "{quiz.title}" is available. Take it now!'})
    async_to_sync(channel_layer.group_add)(f'user_{user.id}', f'notification_group_{user.id}')
    async_to_sync(channel_layer.group_send)(f'user_{user.id}', {'type': 'send_notification', 'message': message})
