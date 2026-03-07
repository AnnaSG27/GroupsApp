from django.db import models
from django.conf import settings
from groups.models import Group


class Message(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    content = models.TextField(blank=True)
    file = models.FileField(upload_to='messages/files/', blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.group.name}"
