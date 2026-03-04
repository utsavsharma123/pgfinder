from django.db import models
from django.conf import settings
from inquiries.models import Inquiry


class ChatRoom(models.Model):
    inquiry = models.OneToOneField(Inquiry, on_delete=models.CASCADE, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat: {self.inquiry}'


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.full_name} in {self.room}'
