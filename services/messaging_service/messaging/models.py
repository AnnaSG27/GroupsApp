from django.db import models


class Message(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )

    sender_id = models.IntegerField()

    group_id = models.IntegerField()

    content = models.TextField(blank=True)
    file = models.FileField(upload_to='messages/files/', blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} from user {self.sender_id} in group {self.group_id}"
